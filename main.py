"""
Pencil Sketch Automated Video Bot - Main Entry Point
Usage:
    python main.py --run-now            # Generate 1 video right now with a unique object
    python main.py --object "airplane"  # Generate 1 video for a specific object
    python main.py --start-scheduler    # Run 24/7 scheduler (07:00, 19:00, 23:00)
"""
import sys
import argparse
from scheduler import run_pipeline, start_scheduler

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Pencil Sketch Automated Video Bot for Shorts/TikTok/Reels")
    parser.add_argument("--run-now", action="store_true", help="Select unique object and create 1 video immediately")
    parser.add_argument("--start-scheduler", action="store_true", help="Start the 24/7 background scheduler")
    parser.add_argument("--object", "--topic", type=str, dest="object", help="Manually specify an object to sketch (e.g. 'car', 'grapes')")

    args = parser.parse_args()

    if args.run_now:
        print("[*] Immediate pencil sketch video requested...")
        run_pipeline(trigger_time="MANUAL_CLI")
    elif args.start_scheduler:
        start_scheduler()
    elif args.object:
        print(f"[*] Custom object requested: '{args.object}'")
        run_pipeline(trigger_time="MANUAL_OBJECT", target_object=args.object)
    else:
        # Default behavior: show options or run 1 video
        print("\n=== PENCIL SKETCH AUTOMATED VIDEO BOT ===")
        print("1. Run 1 video now:         python main.py --run-now")
        print("2. Start 24/7 scheduler:    python main.py --start-scheduler")
        print("3. Custom object:           python main.py --object 'airplane'")
        print("==========================================\n")
        print("[*] Running immediate unique object sketch...")
        run_pipeline(trigger_time="DEFAULT_INIT")


if __name__ == "__main__":
    main()
