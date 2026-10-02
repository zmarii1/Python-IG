"""
Backup runner: does on this PC what GitHub's bot.yml does, for the hours
GitHub skips. Windows Task Scheduler starts it every hour with pythonw.exe,
so no window pops up. What it did goes in runner.log next to this file.

It runs from its own copy of the repo (C:\\Users\\jclea\\paper-bot-runner),
never the folder you edit code in. Each run it throws away anything in
that copy that isn't on GitHub, which would wipe out unsaved work.
"""
import contextlib
import io
import subprocess
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
LOG_FILE = HERE / "runner.log"
KEEP_LOG_LINES = 1000
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)  # Windows only


def log(message):
    """Add a line to runner.log, keeping only the newest lines."""
    lines = []
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    lines.extend(message.splitlines())
    LOG_FILE.write_text("\n".join(lines[-KEEP_LOG_LINES:]) + "\n",
                        encoding="utf-8")


def git(*args):
    """Run a git command in this folder. True if it worked."""
    result = subprocess.run(["git", *args], cwd=HERE, capture_output=True,
                            text=True, creationflags=NO_WINDOW)
    if result.returncode != 0:
        log(f"git {' '.join(args)} failed: "
            f"{result.stderr.strip() or result.stdout.strip()}")
    return result.returncode == 0


def main():
    now = datetime.now(timezone.utc)
    log(f"--- {now:%Y-%m-%d %H:%M} UTC")

    # Start from exactly what's on GitHub, including the newest wallet
    if not (git("fetch", "--quiet", "origin")
            and git("reset", "--quiet", "--hard", "origin/main")):
        return

    # Import after updating, so the newest version of the bot runs
    import Paper_Bot

    # pythonw has no window to print to, so catch the bot's output
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        Paper_Bot.run(now)
    log(output.getvalue().rstrip())

    git("add", "wallet.json")
    if not git("commit", "--quiet", "-m",
               f"bot run {now:%Y-%m-%dT%H:%MZ} (PC backup)"):
        return

    # If GitHub's bot saved the wallet in the last few seconds, keep its
    # run and skip this one; the next run starts fresh from GitHub anyway
    if not git("pull", "--quiet", "--rebase"):
        git("rebase", "--abort")
        log("GitHub's bot ran at the same moment; skipped this save")
        return
    if git("push", "--quiet"):
        log("saved to GitHub")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(traceback.format_exc())
