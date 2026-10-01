"""
Paper trading bot v1: fake money, real Bitcoin prices.

Each time you run it, it:
  1. loads your fake wallet from wallet.json (or makes a new one with $1,000)
  2. grabs the live Bitcoin price
  3. decides BUY, SELL, or HOLD
  4. saves the wallet and prints how you're doing

No real money is ever involved. No API key needed.
"""
import json
import urllib.request
from datetime import datetime

STATE_FILE = "wallet.json"
PRICE_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

BUY_DROP = 0.02    # buy if the price fell 2% since the last check
SELL_GAIN = 0.03   # sell if the price is 3% above what we paid
STOP_LOSS = 0.05   # sell if the price is 5% below what we paid


def load_wallet():
    """Open the saved wallet, or start a fresh one if none exists yet."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "cash": 1000.0,
            "btc": 0.0,
            "buy_price": None,
            "last_price": None,
            "trades": [],
        }


def save_wallet(wallet):
    """Write the wallet back to disk so the next run remembers it."""
    with open(STATE_FILE, "w") as f:
        json.dump(wallet, f, indent=2)


def get_price():
    """Ask CoinGecko for the current Bitcoin price in USD."""
    with urllib.request.urlopen(PRICE_URL) as response:
        data = json.load(response)
    return data["bitcoin"]["usd"]


def decide(wallet, price):
    """The strategy. This is the part you'll change the most."""
    last = wallet["last_price"]

    # Holding cash, price dropped enough since last check: buy the dip
    if wallet["btc"] == 0 and last is not None:
        if price <= last * (1 - BUY_DROP):
            return "BUY"

    # Holding Bitcoin, price rose enough above what we paid: take profit
    if wallet["btc"] > 0:
        if price >= wallet["buy_price"] * (1 + SELL_GAIN):
            return "SELL"

        # Price fell too far below what we paid: cut the loss
        if price <= wallet["buy_price"] * (1 - STOP_LOSS):
            return "STOP_LOSS"

    return "HOLD"


def run():
    wallet = load_wallet()
    price = get_price()
    action = decide(wallet, price)

    if action == "BUY":
        wallet["btc"] = wallet["cash"] / price
        wallet["cash"] = 0.0
        wallet["buy_price"] = price
    elif action in ("SELL", "STOP_LOSS"):
        wallet["cash"] = wallet["btc"] * price
        wallet["btc"] = 0.0
        wallet["buy_price"] = None

    if action != "HOLD":
        wallet["trades"].append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "price": price,
        })

    wallet["last_price"] = price
    save_wallet(wallet)

    total = wallet["cash"] + wallet["btc"] * price
    print(f"BTC price: ${price:,.2f}")
    print(f"Action:    {action}")
    print(f"Wallet:    ${wallet['cash']:,.2f} cash + {wallet['btc']:.6f} BTC")
    print(f"Total:     ${total:,.2f}  (started at $1,000.00)")


if __name__ == "__main__":
    run()