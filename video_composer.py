"""
Video Composer Module for Pencil Sketching
Combines raw video animation with English voiceover, authentic pencil scratch ASMR,
and relaxing acoustic background music using FFmpeg.
Produces final 9:16 vertical MP4 ready for YouTube Shorts, TikTok, and Facebook Reels.
"""
import sys
import subprocess
from pathlib import Path
from config import ASSETS_DIR, TEMP_DIR, OUTPUT_DIR


class VideoComposer:
    def __init__(self):
        self.scratch_sfx = ASSETS_DIR / "scratch.wav"
        self.ding_sfx = ASSETS_DIR / "ding.wav"
        self.bgm_audio = ASSETS_DIR / "bgm.wav"

    def compose_final_video(self, raw_video_path, voiceover_path, output_path):
        """
        Merges raw video, voiceover, BGM, and pencil scratch ASMR into a finished short video (< 60s).
        """
        raw_video_path = Path(raw_video_path)
        voiceover_path = Path(voiceover_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[*] Composing final pencil sketch video -> '{output_path.name}'...")

        # Get exact duration of raw video via ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(raw_video_path)
        ]
        try:
            dur_str = subprocess.check_output(probe_cmd, text=True).strip()
            total_duration = float(dur_str)
        except Exception:
            total_duration = 38.0

        print(f"    Target video duration: {total_duration:.2f}s (< 60s)")

        # FFmpeg filter:
        # Input 0: Raw sketch video
        # Input 1: Voiceover (en-US)
        # Input 2: Background Music (looped)
        # Input 3: Pencil scratching ASMR (looped)
        # Input 4: Ding bell (at reveal)
        fade_start = max(1.0, total_duration - 3.0)
        ding_time = int(max(0, total_duration - 7.0) * 1000)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_video_path),
            "-i", str(voiceover_path),
            "-stream_loop", "-1", "-i", str(self.bgm_audio),
            "-stream_loop", "-1", "-i", str(self.scratch_sfx),
            "-i", str(self.ding_sfx),
            "-filter_complex",
            f"[1:a]volume=1.35,apad[vocal];"
            f"[2:a]volume=0.18,afade=t=out:st={fade_start:.1f}:d=2.5[bgm];"
            f"[3:a]volume=0.15,afade=t=out:st={fade_start:.1f}:d=2.0[scratch];"
            f"[4:a]adelay={ding_time}|{ding_time},volume=0.4[ding];"
            f"[vocal][bgm][scratch][ding]amix=inputs=4:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{total_duration:.2f}",
            "-movflags", "+faststart",
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[!] FFmpeg complex composition failed, using direct fallback...")
            fallback_cmd = [
                "ffmpeg", "-y",
                "-i", str(raw_video_path),
                "-i", str(voiceover_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-t", f"{total_duration:.2f}",
                str(output_path)
            ]
            subprocess.run(fallback_cmd, check=True)

        print(f"[+] Final Video created successfully: {output_path} ({total_duration:.2f}s)")
        return str(output_path)


if __name__ == "__main__":
    composer = VideoComposer()
    print("VideoComposer initialized successfully.")
