"""
Storage Manager & Cleaner Module
Ensures 100% clean disk & cloud storage:
1. Cleans intermediate temporary files in temp/ after every video generation.
2. Manages rolling local storage: keeps only the latest 3 finished videos in output/, auto-deleting older ones.
3. Completely prevents Git and Cloud repository bloat.
"""
import os
import shutil
from pathlib import Path
from config import BASE_DIR, TEMP_DIR, OUTPUT_DIR


class StorageManager:
    def __init__(self, max_local_videos=3):
        self.max_local_videos = max_local_videos

    def clean_temp_directory(self):
        """Cleans up all intermediate files in temp/ while preserving .gitkeep."""
        print("[*] Storage Manager: Cleaning intermediate temporary files...")
        cleaned_count = 0
        cleaned_bytes = 0
        for item in TEMP_DIR.iterdir():
            if item.name == ".gitkeep":
                continue
            try:
                if item.is_file():
                    size = item.stat().st_size
                    item.unlink()
                    cleaned_count += 1
                    cleaned_bytes += size
                elif item.is_dir():
                    shutil.rmtree(item)
                    cleaned_count += 1
            except Exception as e:
                print(f"    [!] Warning: Could not delete {item.name}: {e}")
        mb_freed = cleaned_bytes / (1024 * 1024)
        print(f"[+] Temp cleaned: Removed {cleaned_count} items ({mb_freed:.1f} MB freed).")

    def enforce_rolling_retention(self):
        """
        Keeps only the latest `max_local_videos` MP4 videos in output/.
        Auto-deletes older videos to ensure your hard drive or cloud disk NEVER fills up.
        """
        print(f"[*] Storage Manager: Enforcing rolling retention (max {self.max_local_videos} videos)...")
        mp4_files = sorted(OUTPUT_DIR.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if len(mp4_files) > self.max_local_videos:
            to_delete = mp4_files[self.max_local_videos:]
            for old_vid in to_delete:
                try:
                    size_mb = old_vid.stat().st_size / (1024 * 1024)
                    old_vid.unlink()
                    print(f"    [-] Auto-deleted old video: {old_vid.name} ({size_mb:.1f} MB freed)")
                except Exception as e:
                    print(f"    [!] Warning: Could not delete {old_vid.name}: {e}")
        else:
            print(f"[+] Output directory clean ({len(mp4_files)} videos kept).")

    def clean_after_successful_upload(self, video_path: Path):
        """Optionally deletes the video file immediately once verified uploaded to YouTube/TikTok/Reels."""
        video_path = Path(video_path)
        if video_path.exists():
            try:
                size_mb = video_path.stat().st_size / (1024 * 1024)
                video_path.unlink()
                print(f"[+] Post-upload cleanup: Deleted {video_path.name} ({size_mb:.1f} MB freed).")
            except Exception as e:
                print(f"[!] Warning: Could not delete {video_path.name}: {e}")


if __name__ == "__main__":
    sm = StorageManager()
    sm.clean_temp_directory()
    sm.enforce_rolling_retention()
