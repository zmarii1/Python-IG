# Python-IG

Python projects from learning the language. The main one is a paper trading bot.

## Paper trading bot

Trades **fake money** (starting with $1,000) using **real Bitcoin prices**, every hour, on its own. No real money or exchange account is involved.

**Live wallet:** [`wallet.json` on the `wallet` branch](https://github.com/zmarii1/Python-IG/blob/wallet/wallet.json)

### How it works

| File | What it does |
|---|---|
| [`Paper_Bot.py`](Paper_Bot.py) | Gets the BTC price (CoinGecko, or Coinbase as a backup), decides BUY / SELL / HOLD, and updates the wallet. Every trade pays a 1% cost, about what Robinhood charges through its spread, so the results stay realistic. |
| [`runner.py`](runner.py) | Runs the bot once and saves the wallet to the `wallet` branch, so the hourly saves don't clutter `main`. |
| [`bot.yml`](.github/workflows/bot.yml) | GitHub Actions starts `runner.py` every hour. GitHub skips many scheduled runs, so a PC also starts it hourly with Windows Task Scheduler as a backup. |
| [`backtest.py`](backtest.py) | Replays a year of real hourly prices through the bot's own code to compare strategies and settings. |

### Strategy

**Trend following** (the default): hold Bitcoin while its price is 2% above its 100-day average, and switch to cash when it's 2% below. Dip buying is still in the code (`STRATEGY = "dip"`), but it lost money in testing.

### Backtest results

One year of hourly prices (Oct 2025 to Oct 2026), with a 1% cost per trade. The settings were picked using the first 6 months only, then tested on the last 6, which they had never seen:

| | First 6 months | Last 6 months (unseen) | Full year |
|---|---|---|---|
| Buy & hold | −44% | +26% | −29% |
| Trend, 100-day average, 2% band | −6% | +12.5% | +5.4% |
| Dip buying (the first version) | | | −80% |

The trend strategy mostly wins by staying out of crashes. In a strong rise it lags behind buy & hold. One year of one coin proves little, so these numbers are a lesson, not a promise.

### Run it yourself

Needs Python 3 (tested on 3.12 and 3.14). No packages to install.

```bash
python Paper_Bot.py     # one run, using a local test wallet
python backtest.py      # compare strategies (downloads prices the first time)
```

## Other projects

- [`OverwatchTrivia.py`](OverwatchTrivia.py): a quiz on Overwatch hero roles
- [`youtube_video_downloader.py`](youtube_video_downloader.py): downloads a YouTube video, or just its audio (needs `yt-dlp`)
- [`python_cheatsheet.md`](python_cheatsheet.md): Python basics in plain English

---

This is a learning project, not financial advice.
