"""
Runs the paper bot once and saves its wallet to GitHub.

Two things start it every hour: GitHub Actions (bot.yml), and Windows Task
Scheduler on the PC, as a backup for the hours GitHub skips. The PC starts
it with pythonw.exe, so no window pops up. What it did goes in runner.log
next to this file.

The wallet lives on its own branch, "wallet", so the hourly saves don't
fill up main's history. That branch is checked out in the wallet-branch
folder next to this file.

On the PC it runs from its own copy of the repo
(C:\\Users\\jclea\\paper-bot-runner), never the folder you edit code in:
each run resets that copy to match GitHub, which would wipe unsaved work.
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
WALLET_DIR = HERE / "wallet-branch"
LOG_FILE = HERE / "runner.log"
KEEP_LOG_LINES = 1000
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)  # Windows only
SOURCE = "GitHub" if os.environ.get("GITHUB_ACTIONS") else "PC backup"


def log(message):
    """Show a message and add it to runner.log, keeping the newest lines."""
    print(message)  # does nothing under pythonw, shows in GitHub's log
    lines = []
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    lines.extend(message.splitlines())
    LOG_FILE.write_text("\n".join(lines[-KEEP_LOG_LINES:]) + "\n",
                        encoding="utf-8")


def git(*args, folder=HERE):
    """Run a git command and return its output. Stops the run if it fails."""
    result = subprocess.run(["git", *args], cwd=folder, capture_output=True,
                            text=True, creationflags=NO_WINDOW)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: "
                           f"{result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def main():
    now = datetime.now(timezone.utc)
    log(f"--- {now:%Y-%m-%d %H:%M} UTC")

    # Start from exactly what's on GitHub: the newest code and wallet
    git("fetch", "--quiet", "origin")
    git("reset", "--quiet", "--hard", "origin/main")
    if not WALLET_DIR.exists():
        git("worktree", "prune")
        git("worktree", "add", "--quiet", "--detach", WALLET_DIR.name,
            "origin/wallet")
    git("reset", "--quiet", "--hard", "origin/wallet", folder=WALLET_DIR)
    shutil.copy(WALLET_DIR / "wallet.json", HERE / "wallet.json")

    # Import after updating, so the newest version of the bot runs
    import Paper_Bot

    # Catch the bot's output so it ends up in runner.log too
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        Paper_Bot.run(now)
    log(output.getvalue().rstrip())

    shutil.copy(HERE / "wallet.json", WALLET_DIR / "wallet.json")
    git("add", "wallet.json", folder=WALLET_DIR)
    git("-c", "user.name=paper_bot",
        "-c", "user.email=paper_bot@users.noreply.github.com",
        "commit", "--quiet", "-m",
        f"bot run {now:%Y-%m-%dT%H:%MZ} ({SOURCE})", folder=WALLET_DIR)
    saved = git("rev-parse", "HEAD", folder=WALLET_DIR)
    try:
        git("push", "--quiet", "origin", f"{saved}:refs/heads/wallet")
    except RuntimeError as error:
        # Almost always: the other runner saved a moment ago. Keep its run
        # and skip this one; the next run starts fresh from GitHub anyway.
        log(f"skipped saving this run: {error}")
        return
    log("saved to GitHub")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(traceback.format_exc())
        sys.exit(1)
