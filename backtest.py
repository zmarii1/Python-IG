"""
Backtester: replays the last year of real hourly Bitcoin prices through
the paper bot's strategies to see how different settings would have done.

Run it:  python backtest.py

The first run downloads the prices (about 30 seconds) and saves them to
btc_hourly.csv, so later runs are fast. It downloads fresh prices again
once that file is more than a day old.

How to read the results:
  - Buy & hold is the baseline: buy once, never sell. A strategy that
    can't beat it isn't worth the extra trading.
  - The best settings are picked using the FIRST 6 months only, then
    tested on the LAST 6 months, which they have never seen. If a
    strategy only does well on the months it was picked from, it got
    lucky on that stretch of history; it didn't find a real edge.
"""
import csv
import itertools
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import Paper_Bot as bot

DATA_FILE = Path(__file__).parent / "btc_hourly.csv"
CANDLES_URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
DAYS = 365         # the year every strategy is tested on
WARMUP_DAYS = 100  # extra days before it, so averages are ready on day one

# Cost per trade, taken from the bot. Change it here (for example to 0)
# to see how much trading costs matter, without changing the live bot.
FEE = bot.FEE

SETTINGS_TO_TRY = {
    "trend": {
        "TREND_DAYS": [10, 20, 30, 50, 100],
        "TREND_BAND": [0.0, 0.02, 0.05, 0.08],
    },
    "dip": {
        "BUY_DROP": [0.01, 0.02, 0.03, 0.05, 0.08],
        "SELL_GAIN": [0.02, 0.03, 0.05, 0.10, 0.20],
        "STOP_LOSS": [0.03, 0.05, 0.10, 0.20],
        "COOLDOWN_HOURS": [0, 6, 24],
    },
}


def download_prices():
    """Fetch hourly closing prices from Coinbase (no key needed)."""
    prices = {}
    end = datetime.now(timezone.utc).replace(minute=0, second=0,
                                             microsecond=0)
    oldest = end - timedelta(days=DAYS + WARMUP_DAYS)
    while end > oldest:
        start = max(end - timedelta(hours=299), oldest)  # 300 per request
        url = (f"{CANDLES_URL}?granularity=3600"
               f"&start={start.isoformat()}&end={end.isoformat()}")
        request = urllib.request.Request(
            url, headers={"User-Agent": "paper-bot-backtest"})
        with urllib.request.urlopen(request, timeout=10) as response:
            candles = json.load(response)
        for candle in candles:  # [time, low, high, open, close, volume]
            prices[candle[0]] = candle[4]
        end = start - timedelta(hours=1)
        time.sleep(0.4)  # stay well under Coinbase's rate limit

    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "price"])
        for stamp in sorted(prices):
            when = datetime.fromtimestamp(stamp, timezone.utc)
            writer.writerow([when.isoformat(), prices[stamp]])


def saved_prices_ok():
    """True if the saved file exists, is fresh, and goes back far enough."""
    if not DATA_FILE.exists():
        return False
    if time.time() - DATA_FILE.stat().st_mtime > 24 * 60 * 60:
        return False
    with open(DATA_FILE, newline="") as f:
        first = datetime.fromisoformat(next(csv.DictReader(f))["time"])
    needed = datetime.now(timezone.utc) - timedelta(days=DAYS + WARMUP_DAYS)
    return first <= needed + timedelta(days=1)


def load_prices():
    """Read the saved prices, downloading them first if needed."""
    if not saved_prices_ok():
        print("Downloading hourly BTC prices...")
        download_prices()
    with open(DATA_FILE, newline="") as f:
        return [(datetime.fromisoformat(row["time"]), float(row["price"]))
                for row in csv.DictReader(f)]


def trend_averages(prices, days):
    """For each date: the average end-of-day price over the `days` days
    before it. Same numbers the live bot gets from Coinbase."""
    # The hourly candle that starts at 23:00 closes at the end of the day
    closes = {now.date(): price for now, price in prices if now.hour == 23}
    close_dates = sorted(closes)
    averages = {}
    for day in sorted({now.date() for now, _ in prices}):
        before = [d for d in close_dates if d < day][-days:]
        if len(before) == days:
            averages[day] = sum(closes[d] for d in before) / days
    return averages


def simulate(period, settings, averages):
    """Run the bot's real decide() and trade() over every hour."""
    for name, value in settings.items():
        setattr(bot, name, value)
    bot.FEE = FEE
    daily_average = averages.get(bot.TREND_DAYS, {})
    wallet = bot.new_wallet()
    peak = total = wallet["cash"]
    worst_drop = 0.0
    for now, price in period:
        action = bot.decide(wallet, price, now, daily_average.get(now.date()))
        bot.trade(wallet, action, price, now)
        total = wallet["cash"] + wallet["btc"] * price
        peak = max(peak, total)
        worst_drop = max(worst_drop, (peak - total) / peak)
    return {"final": total, "trades": len(wallet["trades"]),
            "worst_drop": worst_drop}


def buy_and_hold(period):
    """Buy once at the start and never sell."""
    btc = 1000 * (1 - FEE) / period[0][1]
    peak = 1000.0
    worst_drop = 0.0
    for _, price in period:
        total = btc * price
        peak = max(peak, total)
        worst_drop = max(worst_drop, (peak - total) / peak)
    return {"final": total, "trades": 1, "worst_drop": worst_drop}


def all_combinations(strategy):
    """Every mix of the settings to try for one strategy."""
    grid = SETTINGS_TO_TRY[strategy]
    return [dict(zip(grid, values), STRATEGY=strategy)
            for values in itertools.product(*grid.values())]


def describe(settings):
    if settings["STRATEGY"] == "trend":
        return (f"trend: {settings['TREND_DAYS']}-day avg, "
                f"band {settings['TREND_BAND']:.0%}")
    return (f"dip: drop {settings['BUY_DROP']:.0%}, "
            f"gain {settings['SELL_GAIN']:.0%}, "
            f"stop {settings['STOP_LOSS']:.0%}, "
            f"cool {settings['COOLDOWN_HOURS']}h")


def show(label, result):
    change = result["final"] / 1000 - 1
    print(f"  {label:<44} ${result['final']:>9,.2f} {change:>+7.1%}"
          f" {result['trades']:>5} trades"
          f"  worst drop {result['worst_drop']:.0%}")


def top_settings(strategy, period, averages, how_many=3):
    """The best settings for one strategy on this period, skipping
    combinations that traded identically to a better one."""
    results = [(simulate(period, s, averages), s)
               for s in all_combinations(strategy)]
    results.sort(key=lambda pair: pair[0]["final"], reverse=True)
    best, seen = [], set()
    for result, settings in results:
        key = (round(result["final"], 2), result["trades"])
        if key not in seen:
            seen.add(key)
            best.append(settings)
    return best[:how_many]


def main():
    prices = load_prices()
    start = prices[0][0] + timedelta(days=WARMUP_DAYS)
    year = [(now, price) for now, price in prices if now >= start]
    half = len(year) // 2
    first, second = year[:half], year[half:]

    names = {name for grid in SETTINGS_TO_TRY.values() for name in grid}
    current = {name: getattr(bot, name) for name in names | {"STRATEGY"}}
    trend_days = set(SETTINGS_TO_TRY["trend"]["TREND_DAYS"])
    averages = {days: trend_averages(prices, days)
                for days in trend_days | {bot.TREND_DAYS}}

    print(f"\n{year[0][0]:%Y-%m-%d} to {year[-1][0]:%Y-%m-%d}: BTC went "
          f"${year[0][1]:,.0f} -> ${year[-1][1]:,.0f}. "
          f"Cost per trade: {FEE:.1%}\n")

    print("FULL YEAR")
    show("Buy & hold", buy_and_hold(year))
    show("Your current settings:", simulate(year, current, averages))
    print(f"    ({describe(current)})")

    print("\nPicking the best settings using the first 6 months only...")
    best = (top_settings("trend", first, averages)
            + top_settings("dip", first, averages))

    print("\nFIRST 6 MONTHS (where the best settings were picked)")
    show("Buy & hold", buy_and_hold(first))
    for settings in best:
        show(describe(settings), simulate(first, settings, averages))

    print("\nLAST 6 MONTHS (the real test: data they never saw)")
    show("Buy & hold", buy_and_hold(second))
    for settings in best:
        show(describe(settings), simulate(second, settings, averages))
    print()


if __name__ == "__main__":
    main()
