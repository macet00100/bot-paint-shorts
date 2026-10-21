"""
24/7 Autonomous Automation Scheduler - Kids Mystery Guessing Game Edition
Runs automatically 24/7 without manual intervention:
1. Selects unique, non-repeating topic from 400+ kid database (Infinite with Gemini).
2. Generates 3D Pixar character art & glowing silhouette (100% Free).
3. Generates synchronized native English child voiceover (Edge-TTS 100% Free).
4. Renders full 1080x1920 9:16 vertical shorts video with countdown, confetti, and sound effects.
5. Manages storage cleanly: auto-deletes intermediate files, keeps rolling latest 3 videos.
6. Auto-posts to YouTube Shorts, TikTok, Facebook Reels (when upload enabled).
"""
import os
import sys
import datetime
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler

from config import SCHEDULE_TIMES, OUTPUT_DIR, TEMP_DIR
from kids_catalog import KidsCurator
from kids_art_engine import KidsArtEngine
from kids_voice_engine import KidsVoiceEngine
from kids_video_engine import KidsVideoEngine
from cleaner import StorageManager
from auto_uploader import AutoUploader

# Force UTF-8 and instant line-buffering on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)


def run_pipeline(trigger_time="MANUAL", target_topic=None, enable_upload=False):
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print("\n" + "=" * 65)
    print(f"[*] RUNNING KIDS MYSTERY QUIZ PIPELINE [{trigger_time}] at {timestamp_str}")
    print(f"[*] Mode: {'LIVE AUTO-UPLOAD' if enable_upload else 'LOCAL PREVIEW ONLY (Safe Mode)'}")
    print("=" * 65)

    storage = StorageManager(max_local_videos=3)

    try:
        # Step 1: Select Unique Topic (Anti-Duplication)
        print("\n--- STEP 1: SELECT UNIQUE QUIZ TOPIC ---")
        curator = KidsCurator()
        quiz_pkg = curator.select_next_quiz(target_id=target_topic)
        topic_name = quiz_pkg["name"]
        print(f"[+] Topic Selected: '{topic_name}' ({quiz_pkg.get('category', 'general')})")
        print(f"[+] Clue 1: {quiz_pkg['clue1']}")
        print(f"[+] Clue 2: {quiz_pkg['clue2']}")

        # Step 2: 3D Pixar Character Art & Silhouette
        print("\n--- STEP 2: 3D CHARACTER ART & SILHOUETTE (100% FREE) ---")
        art_engine = KidsArtEngine()
        cutout_path, sil_path = art_engine.get_character_assets(quiz_pkg)

        # Step 3: Native English Child Voiceover
        print("\n--- STEP 3: NATIVE ENGLISH CHILD VOICEOVER ---")
        voice_engine = KidsVoiceEngine()
        voice_paths = voice_engine.generate_voiceover_segments(quiz_pkg)

        # Step 4: Video Frames & Audio Composition (1080x1920)
        print("\n--- STEP 4: RENDER FULL 1080x1920 SHORTS VIDEO ---")
        video_engine = KidsVideoEngine()
        raw_video_path = TEMP_DIR / f"raw_quiz_{timestamp_str}.mp4"
        video_engine.render_video_frames(quiz_pkg, cutout_path, sil_path, raw_video_path)

        audio_path = TEMP_DIR / f"audio_quiz_{timestamp_str}.wav"
        video_engine.mix_audio_track(voice_paths, audio_path)

        final_video_name = f"kids_quiz_{quiz_pkg['id']}_{timestamp_str}.mp4"
        final_video_path = OUTPUT_DIR / final_video_name
        video_engine.assemble_final_mp4(raw_video_path, audio_path, final_video_path)

        # Step 5: Record in History to prevent any duplicates
        curator.record_completed(quiz_pkg)

        # Step 6: Multi-Platform Auto Upload (when enabled)
        if enable_upload:
            print("\n--- STEP 6: MULTI-PLATFORM AUTO UPLOAD ---")
            uploader = AutoUploader()
            video_title = f"Can You Guess This {quiz_pkg.get('category', 'Animal').capitalize()} in 5 Seconds? 🐾 #shorts"
            short_caption = (
                f"Can you guess the mystery {quiz_pkg.get('category', 'animal')}? "
                f"Tell me in the comments! 👇 Subscribe for daily fun quizzes! #kids #quiz #shorts"
            )
            uploader.upload_all(
                final_video_path,
                video_title,
                short_caption,
                tags=["kids", "quiz", "guesstheanimal", "shorts", "animation", "family"],
                topic_pkg=quiz_pkg
            )
        else:
            print("\n--- STEP 6: PREVIEW MODE (SAFE MODE - NO UPLOAD) ---")
            print(f"[i] Video saved locally for inspection at:")
            print(f"    -> {final_video_path}")

        # Step 7: Automatic Storage Cleanup (Free up disk space)
        print("\n--- STEP 7: STORAGE CLEANUP & DISK MANAGEMENT ---")
        storage.clean_temp_directory()
        storage.enforce_rolling_retention()

        print("\n" + "=" * 65)
        print(f"[SUCCESS] Kids mystery video pipeline finished: {final_video_path.name}")
        print("=" * 65 + "\n")
        return final_video_path

    except Exception as e:
        print(f"\n[!] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        # Even on error, clean up temp files
        storage.clean_temp_directory()
        return None


def start_scheduler(enable_upload=True, run_immediately=False):
    """Runs 24/7 background scheduler posting at configured times."""
    if run_immediately:
        print("[*] Generating immediate video on scheduler boot...")
        run_pipeline(trigger_time="BOOT_INIT", enable_upload=enable_upload)

    scheduler = BlockingScheduler()
    print("\n" + "=" * 60)
    print("[*] STARTING 24/7 KIDS VIDEO BOT BACKGROUND SCHEDULER")
    print(f"[*] Posting Schedule (Local Time): {SCHEDULE_TIMES}")
    print(f"[*] Auto-Upload Mode: {'LIVE AUTO-UPLOAD' if enable_upload else 'LOCAL SAFE PREVIEW'}")
    print("=" * 60)

    for st in SCHEDULE_TIMES:
        h, m = st.split(":")
        scheduler.add_job(
            run_pipeline,
            "cron",
            hour=int(h),
            minute=int(m),
            kwargs={"trigger_time": f"CRON_{st}", "enable_upload": enable_upload},
            id=f"job_{st}"
        )
        print(f"[+] Scheduled daily run at {st}")

    # 15-Minute Continuous Community Comment Scanner & AI Replier
    try:
        from auto_community import CommunityManager
        cm = CommunityManager()
        scheduler.add_job(
            cm.run_auto_reply_cycle,
            "interval",
            minutes=15,
            id="job_auto_reply_15m"
        )
        print("[+] Scheduled 15-Minute Community Comment Scanner & Free AI Auto-Reply")
    except Exception as e:
        print(f"[!] Warning: Could not schedule community auto-reply: {e}")

    print("[*] Scheduler is actively waiting for next trigger. Press Ctrl+C to stop.\n")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[!] Scheduler stopped cleanly.")


if __name__ == "__main__":
    run_pipeline(trigger_time="TEST_CLI", enable_upload=False)
