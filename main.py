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
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Kids Mystery Guessing Game Automated Video Bot")
    parser.add_argument("--run-now", action="store_true", help="Select unique topic and create 1 video immediately")
    parser.add_argument("--start-scheduler", action="store_true", help="Start the 24/7 background scheduler")
    parser.add_argument("--boot-run", action="store_true", help="When starting scheduler, generate 1 video immediately on boot")
    parser.add_argument("--topic", "--object", type=str, dest="topic", help="Specify topic ID (e.g. 'baby_panda', 'baby_elephant', 'baby_trex')")
    parser.add_argument("--upload", action="store_true", help="Enable live auto-upload to YouTube Shorts, TikTok, Facebook Reels")

    args = parser.parse_args()

    if args.run_now:
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
