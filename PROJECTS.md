# Projects

Everything I'm working on, in one place. Last updated 2026-10-14.

| Project | What it does | Status | Last worked on | Next step |
|---|---|---|---|---|
| [Paper trading bot](#paper-trading-bot) | Trades fake money on real Bitcoin prices every hour | Running | 2026-10-06 (code), runs hourly | Compare it to buy & hold after a month live (~Nov 6) |
| [YouTube downloader](#youtube-downloader) | Downloads a YouTube video or just its audio | Broken locally | 2026-10-07 | Put back the missing `:` on line 20 |
| [Overwatch trivia](#overwatch-trivia) | Quiz on Overwatch hero roles | Done | 2026-09-29 | None |
| [Python cheatsheet](#python-cheatsheet) | Python basics in plain English | Done | 2026-09-30 | Add each new thing as you learn it |
| [Jump Tower](#jump-tower-roblox) | Roblox jumping/clicker game | In progress | 2026-10-13 | Get the scripts into git |
| [Minecraft server](#minecraft-server) | Vanilla server in Docker | Stopped | 2026-10-11 | Automate backups |
| [Build log](#build-log) | Weekly learning plan | Out of date | 2026-09-09 | Tick off the weeks already done |

## Paper trading bot

Repo: this one (`Paper_Bot.py`, `runner.py`, `backtest.py`). See the [README](README.md) for how it works.

- **What it does:** Starts with $1,000 of fake money and trades Bitcoin by trend following: it holds BTC while the price is 2% above its 100-day average, and sits in cash when it's 2% below.
- **Status:** Running. GitHub Actions starts it every few hours (runs on 2026-10-10 to 10-14 all succeeded). A PC backup runs it hourly with Task Scheduler for the hours GitHub skips. Last run: 2026-10-14 04:11 UTC. It's holding BTC and is down about 2% from where it started.
- **Last worked on:** 2026-10-06 (moved the wallet to its own branch).
- **Next step:** Leave it alone until about 2026-11-06 (one month live), then compare the wallet against plain buy & hold over the same month.

## YouTube downloader

Repo: this one (`youtube_video_downloader.py`).

- **What it does:** Asks for a YouTube link and saves the video, or only the audio as an mp3, to `downloads/`. Uses `yt-dlp`. Bad links get a message instead of a crash.
- **Status:** The version on GitHub works. A local edit that isn't committed yet removed the `:` at the end of the `if` on line 20, so the local copy won't run.
- **Last worked on:** 2026-10-07.
- **Next step:** Put the `:` back on line 20, test one download, then commit.

## Overwatch trivia

Repo: this one (`OverwatchTrivia.py`).

- **What it does:** Asks random questions about which role each Overwatch hero plays and keeps score.
- **Status:** Done (last commit was "Overwatch Hero Role Trivia Final").
- **Last worked on:** 2026-09-29.
- **Next step:** None. It's finished.

## Python cheatsheet

Repo: this one (`python_cheatsheet.md`).

- **What it does:** Python basics explained in plain English.
- **Status:** Done for now.
- **Last worked on:** 2026-09-30.
- **Next step:** Add each new idea from the next project to it as you learn it.

## Jump Tower (Roblox)

Not on GitHub. Saved as a Roblox place file (`JumpTowernew.rbxlx`).

- **What it does:** A Roblox jumping game with several worlds. Players click to build Power, land on win pads or smash glass ceilings for Wins, and spend them on upgrades, rebirths and prestige. It also has pets that hatch from eggs, boots crafted from materials you pick up, story and daily quests, a daily streak, offline earnings, leaderboards, and a shared Chaos meter that spins a roulette of random events for the whole server.
- **Status:** In progress and big: 14 scripts, about 10,000 lines of Luau. The server owns all stats, so players can't cheat, and saves are locked so a player's progress can't be overwritten when they switch servers.
- **Last worked on:** 2026-10-13.
- **Next step:** Get the scripts into git (a private repo, for example with [Rojo](https://rojo.space)). Right now the only copies are the place files on the PC and any versions saved to Roblox, with no history of what changed.

## Minecraft server

Not on GitHub. Runs in Docker (`itzg/minecraft-server`), vanilla.

- **What it does:** A Minecraft server to play on.
- **Status:** Stopped. The container last shut down cleanly around 2026-10-11. One backup exists, made by hand on 2026-10-10.
- **Last worked on:** 2026-10-11.
- **Next step:** Set up automatic backups so the world isn't relying on one hand-made copy.

## Build log

Repo: `Hi` (private).

- **What it does:** A 7-week plan for learning: trivia game, password generator, to-do list, YouTube downloader, a Wireshark lab, then a review week. Each week has a checklist and a "where I stopped" note.
- **Status:** Out of date. Every box is still unticked, but the trivia game and the YouTube downloader (weeks 1, 3 and 4) are actually done. The password generator and the to-do list haven't been started.
- **Last worked on:** 2026-09-09.
- **Next step:** Tick off the weeks you've finished so the plan shows what's actually next (the password generator).
