"""
Backtester: replays the last year of real hourly Bitcoin prices through
the paper bot's strategy to see how different settings would have done.

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
DAYS = 365

# Cost per trade, taken from the bot. Change it here (for example to 0)
# to see how much trading costs matter, without changing the live bot.
FEE = bot.FEE

SETTINGS_TO_TRY = {
    "BUY_DROP": [0.01, 0.02, 0.03, 0.05, 0.08],
    "SELL_GAIN": [0.02, 0.03, 0.05, 0.10, 0.20],
    "STOP_LOSS": [0.03, 0.05, 0.10, 0.20],
    "COOLDOWN_HOURS": [0, 6, 24],
}


def download_prices():
    """Fetch a year of hourly closing prices from Coinbase (no key)."""
    prices = {}
    end = datetime.now(timezone.utc).replace(minute=0, second=0,
                                             microsecond=0)
    oldest = end - timedelta(days=DAYS)
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


def load_prices():
    """Read the saved prices, downloading them first if needed."""
    one_day = 24 * 60 * 60
    if (not DATA_FILE.exists()
            or time.time() - DATA_FILE.stat().st_mtime > one_day):
        print("Downloading a year of hourly BTC prices...")
        download_prices()
    with open(DATA_FILE, newline="") as f:
        return [(datetime.fromisoformat(row["time"]), float(row["price"]))
                for row in csv.DictReader(f)]


def simulate(prices, settings):
    """Run the bot's real decide() and trade() over every hour."""
    for name, value in settings.items():
        setattr(bot, name, value)
    bot.FEE = FEE
    wallet = bot.new_wallet()
    peak = total = wallet["cash"]
    worst_drop = 0.0
    for now, price in prices:
        action = bot.decide(wallet, price, now)
        bot.trade(wallet, action, price, now)
        total = wallet["cash"] + wallet["btc"] * price
        peak = max(peak, total)
        worst_drop = max(worst_drop, (peak - total) / peak)
    return {"final": total, "trades": len(wallet["trades"]),
            "worst_drop": worst_drop}


def buy_and_hold(prices):
    """Buy once at the start and never sell."""
    btc = 1000 * (1 - FEE) / prices[0][1]
    peak = 1000.0
    worst_drop = 0.0
    for _, price in prices:
        total = btc * price
        peak = max(peak, total)
        worst_drop = max(worst_drop, (peak - total) / peak)
    return {"final": total, "trades": 1, "worst_drop": worst_drop}


def describe(settings):
    return (f"drop {settings['BUY_DROP']:.0%}, "
            f"gain {settings['SELL_GAIN']:.0%}, "
            f"stop {settings['STOP_LOSS']:.0%}, "
            f"cool {settings['COOLDOWN_HOURS']}h")


def show(label, result):
    change = result["final"] / 1000 - 1
    print(f"  {label:<40} ${result['final']:>9,.2f} {change:>+7.1%}"
          f" {result['trades']:>5} trades"
          f"  worst drop {result['worst_drop']:.0%}")


def main():
    prices = load_prices()
    half = len(prices) // 2
    first, second = prices[:half], prices[half:]
    current = {name: getattr(bot, name) for name in SETTINGS_TO_TRY}

    print(f"\n{len(prices):,} hours of BTC, {prices[0][0]:%Y-%m-%d} to "
          f"{prices[-1][0]:%Y-%m-%d}: ${prices[0][1]:,.0f} -> "
          f"${prices[-1][1]:,.0f}.  Fee per trade: {FEE:.1%}\n")

    print("FULL YEAR")
    show("Buy & hold", buy_and_hold(prices))
    show("Your current settings:", simulate(prices, current))
    print(f"    ({describe(current)})")

    names = list(SETTINGS_TO_TRY)
    combos = [dict(zip(names, values))
              for values in itertools.product(*SETTINGS_TO_TRY.values())]
    print(f"\nTrying {len(combos)} combinations on the first 6 months...")
    ranked = sorted(combos, key=lambda s: simulate(first, s)["final"],
                    reverse=True)

    # Many combinations trade identically (a setting that never triggers
    # makes no difference), so keep only the first of each distinct result
    best, seen = [], set()
    for settings in ranked:
        result = simulate(first, settings)
        key = (round(result["final"], 2), result["trades"])
        if key not in seen:
            seen.add(key)
            best.append(settings)
        if len(best) == 5:
            break

    print("\nFIRST 6 MONTHS (where the best settings were picked)")
    show("Buy & hold", buy_and_hold(first))
    for settings in best:
        show(describe(settings), simulate(first, settings))

    print("\nLAST 6 MONTHS (the real test: data they never saw)")
    show("Buy & hold", buy_and_hold(second))
    for settings in best:
        show(describe(settings), simulate(second, settings))
    print()


if __name__ == "__main__":
    main()
