"""
24/7 Automation Scheduler - Pencil Sketch Edition
Runs automatically in the background, selecting unique non-repeating objects and posting:
- 07:00 AM (00:00 UTC)
- 07:00 PM (12:00 UTC)
- 11:00 PM (16:00 UTC)
"""
import sys
import os
import time
import datetime
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler

from config import SCHEDULE_TIMES, OUTPUT_DIR, TEMP_DIR
from object_catalog import ObjectCurator
from ai_artist import AIArtist
from voice_generator import VoiceGenerator
from ai_video_engine import AIVideoEngine
from sketch_engine import SketchEngine
from video_composer import VideoComposer
from auto_uploader import AutoUploader

# Force UTF-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def run_pipeline(trigger_time="MANUAL", target_object=None, enable_upload=False):
    """
    Executes the full automated pencil sketch workflow:
    1. Select unique, non-repeating everyday object from catalog
    2. AI generates authentic Graphite Pencil Sketch on paper
    3. AI generates synchronized native English tutorial voiceover
    4. POV Sketch Engine renders ~35s 9:16 drawing video on A4 desk paper
    5. Video Composer adds ASMR pencil scratching, lofi BGM, and muxes video
    6. Multi-platform upload only if enable_upload=True
    """
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print("\n" + "=" * 60)
    print(f"[*] RUNNING PENCIL SKETCH PIPELINE [{trigger_time}] at {timestamp_str}")
    print(f"[*] Mode: {'LIVE AUTO-UPLOAD' if enable_upload else 'LOCAL PREVIEW ONLY (Safe Mode)'}")
    print("=" * 60)

    try:
        # Step 1: Unique Object Selection
        print("\n--- STEP 1: OBJECT SELECTION (ANTI-DUPLICATION) ---")
        curator = ObjectCurator()
        pkg = curator.create_sketch_package(object_name=target_object)
        obj_name = pkg["object_name"]
        display_name = pkg["display_name"]
        print(f"[+] Selected Unique Object: '{display_name}'")
        print(f"[+] Video Title: '{pkg['video_title']}'")

        # Step 2: 2K AI Pencil Sketch on Paper
        print("\n--- STEP 2: GRAPHITE PENCIL SKETCH GENERATION ---")
        artist = AIArtist()
        image_path = TEMP_DIR / f"sketch_art_{timestamp_str}.jpg"
        artist.generate_caricature_image(pkg["image_prompt"], image_path)

        # Step 3: Native English Voiceover
        print("\n--- STEP 3: NATIVE ENGLISH VOICEOVER GENERATION ---")
        voice_gen = VoiceGenerator()
        voice_path = TEMP_DIR / f"voice_{timestamp_str}.mp3"
        voice_gen.generate_voiceover(pkg["full_script"], voice_path)

        # Step 4: True Living AI Video Generation (Hugging Face LTX-Video)
        print("\n--- STEP 4: LIVING AI VIDEO GENERATION (LTX-VIDEO DISTILLED) ---")
        final_video_name = f"sketch_{timestamp_str}.mp4"
        final_video_path = OUTPUT_DIR / final_video_name

        ai_success = False
        try:
            ai_engine = AIVideoEngine()
            if ai_engine.client is not None:
                ai_engine.render_full_tutorial(
                    object_name=obj_name,
                    display_name=display_name,
                    voiceover_path=voice_path,
                    output_video_path=final_video_path
                )
                ai_success = True
        except Exception as ai_err:
            print(f"[!] AI Video Engine encountered issue: {ai_err}. Falling back to POV sketch engine...")

        if not ai_success:
            print("\n--- STEP 4 (FALLBACK): POV SKETCH ENGINE ANIMATION (9:16) ---")
            engine = SketchEngine()
            raw_video_path = TEMP_DIR / f"sketch_raw_{timestamp_str}.mp4"
            engine.render_sketch_video(image_path, display_name, raw_video_path)

            print("\n--- STEP 5: AUDIO COMPOSITION & SYNC ---")
            composer = VideoComposer()
            composer.compose_final_video(raw_video_path, voice_path, final_video_path)

        # Step 6: Multi-Platform Auto Upload (Only when enabled)
        if enable_upload:
            print("\n--- STEP 6: MULTI-PLATFORM AUTO UPLOAD ---")
            uploader = AutoUploader()
            uploader.upload_all(
                final_video_path,
                pkg["video_title"],
                pkg["short_caption"],
                tags=["pencilsketch", "howtodraw", "art", "drawing", "shorts"]
            )
        else:
            print("\n--- STEP 6: PREVIEW MODE (AUTO-UPLOAD DISABLED) ---")
            print(f"[i] Safe Mode: Video saved locally for inspection at:")
            print(f"    -> {final_video_path}")
            print(f"[i] Upload is paused so you can review without needing to delete unwanted posts.")

        print("\n" + "=" * 60)
        print(f"[SUCCESS] Pencil sketch video created: {final_video_path}")
        print("=" * 60 + "\n")
        return final_video_path

    except Exception as e:
        print(f"\n[!] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return None


def start_scheduler():
    """Starts 24/7 background scheduler"""
    scheduler = BlockingScheduler(timezone="Asia/Ho_Chi_Minh")
    print("\n" + "=" * 60)
    print("   24/7 PENCIL SKETCH AUTOMATION SCHEDULER STARTED")
    print("=" * 60)
    print(f"Scheduled posting times: {', '.join(SCHEDULE_TIMES)} (Vietnam Time UTC+7)")
    print("Press Ctrl+C to stop.\n")

    for t in SCHEDULE_TIMES:
        hour, minute = t.split(":")
        scheduler.add_job(
            run_pipeline,
            "cron",
            hour=hour,
            minute=minute,
            args=[f"SCHEDULED_{t}"],
            name=f"Job_{t}"
        )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[!] Scheduler stopped by user.")


if __name__ == "__main__":
    run_pipeline(trigger_time="TEST_DIRECT")
