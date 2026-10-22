"""
Kids Mystery Guessing Game - Automated Video Bot (Main Entry Point)
Usage:
    python main.py --run-now            # Generate 1 video right now in safe preview mode
    python main.py --run-now --upload   # Generate 1 video and auto-upload to YouTube, TikTok, Facebook
    python main.py --topic "panda"      # Generate 1 video for specific topic
    python main.py --start-scheduler    # Run 24/7 background scheduler (07:00, 19:00, 23:00)
"""
import sys
import argparse
from scheduler import run_pipeline, start_scheduler

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)


def check_slot_already_satisfied(min_interval_minutes=90):
    """
    Checks history_kids_quiz.json to see if a video was published recently.
    Prevents duplicate videos if backup cron fires after primary cron succeeds.
    """
    from config import BASE_DIR
    import json
    import datetime
    history_file = BASE_DIR / "history_kids_quiz.json"
    if not history_file.exists():
        return False
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        if not items:
            return False
        latest = items[-1]
        completed_at_str = latest.get("completed_at")
        if not completed_at_str:
            return False
        completed_at = datetime.datetime.strptime(completed_at_str, "%Y-%m-%d %H:%M:%S")
        elapsed = (datetime.datetime.utcnow() - completed_at).total_seconds() / 60.0
        if elapsed < min_interval_minutes:
            print(f"[*] Recent video '{latest.get('name')}' published {int(elapsed)} mins ago (< {min_interval_minutes}m). Slot already satisfied. Skipping duplicate run.")
            return True
    except Exception as e:
        print(f"[!] Slot check notice: {e}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Kids Mystery Guessing Game Automated Video Bot")
    parser.add_argument("--run-now", action="store_true", help="Select unique topic and create 1 video immediately")
    parser.add_argument("--check-freshness", action="store_true", help="Skip run if a video was already published within the last 90 minutes")
    parser.add_argument("--start-scheduler", action="store_true", help="Start the 24/7 background scheduler")
    parser.add_argument("--boot-run", action="store_true", help="When starting scheduler, generate 1 video immediately on boot")
    parser.add_argument("--topic", "--object", type=str, dest="topic", help="Specify topic ID (e.g. 'baby_panda', 'baby_elephant', 'baby_trex')")
    parser.add_argument("--upload", action="store_true", help="Enable live auto-upload to YouTube Shorts, TikTok, Facebook Reels")

    args = parser.parse_args()

    if args.run_now:
        if args.check_freshness and check_slot_already_satisfied(min_interval_minutes=90):
            print("[+] Slot already satisfied by previous run. Exiting cleanly.")
            return
        print("[*] Immediate Kids Mystery Video requested...")
        run_pipeline(trigger_time="MANUAL_CLI", enable_upload=args.upload)
    elif args.start_scheduler:
        start_scheduler(enable_upload=args.upload, run_immediately=args.boot_run)
    elif args.topic:
        print(f"[*] Custom quiz topic requested: '{args.topic}'")
        run_pipeline(trigger_time="MANUAL_TOPIC", target_topic=args.topic, enable_upload=args.upload)
    else:
        print("\n=== KIDS MYSTERY GUESSING GAME - AUTOMATED VIDEO BOT ===")
        print("1. Preview 1 video locally: python main.py --run-now")
        print("2. Create & live upload:    python main.py --run-now --upload")
        print("3. Custom topic preview:   python main.py --topic 'baby_panda'")
        print("4. Start 24/7 scheduler:    python main.py --start-scheduler")
        print("========================================================\n")
        print("[*] Running immediate unique quiz in safe preview mode...")
        run_pipeline(trigger_time="DEFAULT_INIT", enable_upload=args.upload)


if __name__ == "__main__":
    main()
