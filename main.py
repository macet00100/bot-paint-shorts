"""
MS Paint Automated Video Bot - Main Entry Point
Usage:
    python main.py --run-now            # Generate 1 video right now from live trends
    python main.py --topic "Chủ đề"     # Generate 1 video for a specific topic
    python main.py --start-scheduler    # Run 24/7 scheduler (11:00, 20:00, 22:00)
"""
import sys
import argparse
from scheduler import run_pipeline, start_scheduler
from trend_researcher import TrendResearcher

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="MS Paint Automated Video Bot for Shorts/TikTok/Reels")
    parser.add_argument("--run-now", action="store_true", help="Research trends and create 1 video immediately")
    parser.add_argument("--start-scheduler", action="store_true", help="Start the 24/7 background scheduler")
    parser.add_argument("--topic", type=str, help="Manually specify a topic instead of researching trends")

    args = parser.parse_args()

    if args.run_now:
        print("[*] Manual run requested...")
        run_pipeline(trigger_time="MANUAL_CLI")
    elif args.start_scheduler:
        start_scheduler()
    elif args.topic:
        print(f"[*] Custom topic requested: '{args.topic}'")
        researcher = TrendResearcher()
        pkg = researcher.generate_caricature_package(trend_item={"title": args.topic, "source": "Manual Input"})
        # Run pipeline with custom package
        from ai_artist import AIArtist
        from voice_generator import VoiceGenerator
        from paint_engine import PaintEngine
        from video_composer import VideoComposer
        from auto_uploader import AutoUploader
        from config import OUTPUT_DIR, TEMP_DIR
        import datetime

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = TEMP_DIR / f"caricature_{ts}.jpg"
        AIArtist().generate_caricature_image(pkg["image_prompt"], img_path)

        voice_path = TEMP_DIR / f"voice_{ts}.mp3"
        VoiceGenerator().generate_voiceover(pkg["full_script"], voice_path)

        raw_vid = TEMP_DIR / f"paint_raw_{ts}.mp4"
        PaintEngine().render_animation(img_path, pkg["video_title"], raw_vid)

        final_vid = OUTPUT_DIR / f"paint_custom_{ts}.mp4"
        VideoComposer().compose_final_video(raw_vid, voice_path, final_vid)

        AutoUploader().upload_all(final_vid, pkg["video_title"], pkg["full_script"])
        print(f"\n[+] Finished custom video: {final_vid}")
    else:
        # Default behavior: run 1 full test video to show the user immediate results
        print("\n=== MS PAINT AUTOMATED VIDEO BOT ===")
        print("1. Run 1 video now:         python main.py --run-now")
        print("2. Start 24/7 scheduler:    python main.py --start-scheduler")
        print("3. Custom topic:            python main.py --topic 'Chủ đề của bạn'")
        print("=====================================\n")
        print("[*] Running immediate live trend test...")
        run_pipeline(trigger_time="DEFAULT_INIT")


if __name__ == "__main__":
    main()
