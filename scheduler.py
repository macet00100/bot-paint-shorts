"""
24/7 Automation Scheduler
Runs automatically in the background, researching trends and posting 3 videos daily:
- 11:00 AM (11:00)
- 08:00 PM (20:00)
- 10:00 PM (22:00)
"""
import sys
import os
import time
import datetime
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler

from config import SCHEDULE_TIMES, OUTPUT_DIR, TEMP_DIR
from trend_researcher import TrendResearcher
from ai_artist import AIArtist
from voice_generator import VoiceGenerator
from paint_engine import PaintEngine
from video_composer import VideoComposer
from auto_uploader import AutoUploader

# Force UTF-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def run_pipeline(trigger_time="MANUAL"):
    """
    Executes the full automated workflow:
    1. Research latest trending topic
    2. AI generates 2K Caricature Image
    3. AI generates synchronized voiceover
    4. Paint Engine renders 30s 9:16 drawing video
    5. Video Composer adds sound effects, BGM, and muxes final video
    6. Auto Uploader posts to YouTube Shorts, Facebook Reels, and TikTok
    """
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print("\n" + "=" * 60)
    print(f"[*] RUNNING PIPELINE [{trigger_time}] at {timestamp_str}")
    print("=" * 60)

    try:
        # Step 1: Trend Research
        print("\n--- STEP 1: TREND RESEARCH ---")
        researcher = TrendResearcher()
        pkg = researcher.generate_caricature_package()
        topic = pkg["topic"]
        print(f"[+] Selected Topic: '{topic}'")
        print(f"[+] Video Title: '{pkg['video_title']}'")

        # Step 2: 2K AI Caricature Image
        print("\n--- STEP 2: AI CARICATURE GENERATION ---")
        artist = AIArtist()
        image_path = TEMP_DIR / f"caricature_{timestamp_str}.jpg"
        artist.generate_caricature_image(pkg["image_prompt"], image_path)

        # Step 3: Vietnamese Voiceover
        print("\n--- STEP 3: VOICEOVER GENERATION ---")
        voice_gen = VoiceGenerator()
        voice_path = TEMP_DIR / f"voice_{timestamp_str}.mp3"
        voice_gen.generate_voiceover(pkg["full_script"], voice_path)

        # Step 4: Paint Animation Rendering
        print("\n--- STEP 4: MS PAINT VIDEO ANIMATION ---")
        engine = PaintEngine()
        raw_video_path = TEMP_DIR / f"paint_raw_{timestamp_str}.mp4"
        engine.render_animation(image_path, pkg["video_title"], raw_video_path)

        # Step 5: Final Video Composition
        print("\n--- STEP 5: FINAL VIDEO COMPOSITION (30S 9:16) ---")
        composer = VideoComposer()
        final_video_name = f"paint_short_{timestamp_str}.mp4"
        final_video_path = OUTPUT_DIR / final_video_name
        composer.compose_final_video(raw_video_path, voice_path, final_video_path)

        # Step 6: Multi-Platform Auto Upload
        print("\n--- STEP 6: MULTI-PLATFORM AUTO UPLOAD ---")
        uploader = AutoUploader()
        uploader.upload_all(
            final_video_path,
            pkg["video_title"],
            pkg["short_caption"],
            tags=["shorts", "mspaint", "art", "drawing", "trending"]
        )

        print("\n" + "=" * 60)
        print(f"[SUCCESS] Video successfully created and processed: {final_video_path}")
        print("=" * 60 + "\n")
        return final_video_path

    except Exception as e:
        print(f"\n[!] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return None


def start_scheduler():
    """Initializes 24/7 background scheduler for 11:00, 20:00, and 22:00"""
    scheduler = BlockingScheduler()

    print("[*] Starting 24/7 Automation Scheduler...")
    print(f"[*] Posting Schedule: {SCHEDULE_TIMES}")

    for time_str in SCHEDULE_TIMES:
        hour, minute = time_str.split(":")
        scheduler.add_job(
            run_pipeline,
            "cron",
            hour=int(hour),
            minute=int(minute),
            args=[f"SCHEDULED_{time_str}"]
        )
        print(f"    -> Scheduled daily job at {time_str}")

    print("\n[+] Scheduler is RUNNING 24/7! Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[!] Scheduler stopped by user.")


if __name__ == "__main__":
    start_scheduler()
