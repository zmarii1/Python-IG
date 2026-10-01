"""
Paper trading bot v2: fake money, real Bitcoin prices.

Each time you run it, it:
  1. loads your fake wallet from wallet.json (or makes a new one with $1,000)
  2. grabs the live Bitcoin price (CoinGecko, or Coinbase as a backup)
  3. decides BUY, SELL, STOP_LOSS, or HOLD
  4. saves the wallet and prints how you're doing

No real money is ever involved. No API key needed.
"""
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Always next to this script, no matter which folder you run it from
STATE_FILE = Path(__file__).parent / "wallet.json"
COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin&vs_currencies=usd"
)
COINBASE_URL = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

BUY_DROP = 0.02    # buy if the price is 2% below its 24-hour high
SELL_GAIN = 0.03   # sell if the price is 3% above what we paid
STOP_LOSS = 0.05   # sell if the price is 5% below what we paid
COOLDOWN_HOURS = 6  # after a stop-loss, wait this long before buying
LOOKBACK_HOURS = 24  # how far back the bot remembers prices

# Cost of each buy or sell. Robinhood doesn't charge a fee on crypto;
# it builds about 0.95% into the price instead (its crypto order
# routing page, as of June 2026). Paper trades pay it too, so the
# fake results match what real ones would have been.
FEE = 0.01


def new_wallet():
    """A fresh wallet with $1,000 of fake cash."""
    return {
        "cash": 1000.0,
        "btc": 0.0,
        "buy_price": None,
        "last_price": None,
        "trades": [],
        "history": [],
        "last_stop_loss": None,
    }


def load_wallet():
    """Open the saved wallet, or start a fresh one if none exists yet."""
    try:
        with open(STATE_FILE, "r") as f:
            return fill_in_new_fields(json.load(f))
    except FileNotFoundError:
        return new_wallet()


def fill_in_new_fields(wallet):
    """Older wallets were saved before these fields existed."""
    wallet.setdefault("history", [])
    wallet.setdefault("last_stop_loss", None)
    return wallet


def save_wallet(wallet):
    """Write the wallet back to disk so the next run remembers it."""
    with open(STATE_FILE, "w") as f:
        json.dump(wallet, f, indent=2)


def fetch_json(url):
    """Download a URL and read the reply as JSON."""
    request = urllib.request.Request(url, headers={"User-Agent": "paper-bot"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def get_price():
    """Current Bitcoin price in USD. Tries CoinGecko, then Coinbase."""
    try:
        return fetch_json(COINGECKO_URL)["bitcoin"]["usd"]
    except Exception as error:
        print(f"CoinGecko failed ({error}), trying Coinbase instead")
        return float(fetch_json(COINBASE_URL)["data"]["amount"])


def in_cooldown(wallet, now):
    """True if a stop-loss happened less than COOLDOWN_HOURS ago."""
    if wallet["last_stop_loss"] is None:
        return False
    stopped_at = datetime.fromisoformat(wallet["last_stop_loss"])
    return now - stopped_at < timedelta(hours=COOLDOWN_HOURS)


def recent_high(wallet):
    """Highest price the bot saw in the last LOOKBACK_HOURS, or None."""
    prices = [check["price"] for check in wallet["history"]]
    return max(prices) if prices else None


def decide(wallet, price, now):
    """The strategy. This is the part you'll change the most."""
    high = recent_high(wallet)

    # Holding cash, price is well below its recent high: buy the dip,
    # unless we just took a stop-loss and are cooling off
    if wallet["btc"] == 0 and high is not None:
        if in_cooldown(wallet, now):
            return "HOLD"
        if price <= high * (1 - BUY_DROP):
            return "BUY"

    # Holding Bitcoin, price rose enough above what we paid: take profit
    if wallet["btc"] > 0:
        if price >= wallet["buy_price"] * (1 + SELL_GAIN):
            return "SELL"

        # Price fell too far below what we paid: cut the loss
        if price <= wallet["buy_price"] * (1 - STOP_LOSS):
            return "STOP_LOSS"

    return "HOLD"


def remember_price(wallet, price, now):
    """Add this check to the history and forget anything too old."""
    wallet["history"].append({"time": now.isoformat(timespec="seconds"),
                              "price": price})
    # UTC times in this format sort correctly as plain text,
    # which is much faster than converting each one back to a datetime
    cutoff = (now - timedelta(hours=LOOKBACK_HOURS)).isoformat(
        timespec="seconds")
    wallet["history"] = [
        check for check in wallet["history"] if check["time"] >= cutoff
    ]


def trade(wallet, action, price, now):
    """Carry out the action on the wallet, paying FEE on each trade."""
    if action == "BUY":
        wallet["btc"] = wallet["cash"] * (1 - FEE) / price
        wallet["cash"] = 0.0
        wallet["buy_price"] = price
    elif action in ("SELL", "STOP_LOSS"):
        wallet["cash"] = wallet["btc"] * price * (1 - FEE)
        wallet["btc"] = 0.0
        wallet["buy_price"] = None
    if action == "STOP_LOSS":
        wallet["last_stop_loss"] = now.isoformat(timespec="seconds")

    if action != "HOLD":
        wallet["trades"].append({
            "time": now.isoformat(timespec="seconds"),
            "action": action,
            "price": price,
        })

    wallet["last_price"] = price
    remember_price(wallet, price, now)


def run(now=None):
    now = now or datetime.now(timezone.utc)
    wallet = load_wallet()
    price = get_price()
    action = decide(wallet, price, now)
    trade(wallet, action, price, now)
    save_wallet(wallet)

    total = wallet["cash"] + wallet["btc"] * price
    print(f"BTC price: ${price:,.2f}")
    print(f"Action:    {action}")
    print(f"Wallet:    ${wallet['cash']:,.2f} cash + {wallet['btc']:.6f} BTC")
    print(f"Total:     ${total:,.2f}  (started at $1,000.00)")


if __name__ == "__main__":
    run()
