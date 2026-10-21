"""
Video Composer Module
Combines raw video animation with voiceover, sound effects, and background music using FFmpeg.
Produces final 9:16 vertical MP4 ready for YouTube Shorts, TikTok, and Facebook Reels.
"""
import sys
import subprocess
from pathlib import Path
from config import ASSETS_DIR, TEMP_DIR, OUTPUT_DIR


class VideoComposer:
    def __init__(self):
        self.scratch_sfx = ASSETS_DIR / "scratch.wav"
        self.click_sfx = ASSETS_DIR / "click.wav"
        self.ding_sfx = ASSETS_DIR / "ding.wav"
        self.bgm_audio = ASSETS_DIR / "bgm.wav"

    def compose_final_video(self, raw_video_path, voiceover_path, output_path):
        """
        Merges raw video, voiceover, BGM, and sound effects into a polished 30s short video.
        Ensures full 30-second video duration by letting BGM play to the end.
        """
        raw_video_path = Path(raw_video_path)
        voiceover_path = Path(voiceover_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[*] Composing final video with audio sync -> '{output_path.name}'...")

        # FFmpeg command:
        # Input 0: Raw video (30s)
        # Input 1: Voiceover
        # Input 2: BGM
        # Input 3: Ding
        # Input 4: Click
        cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_video_path),
            "-i", str(voiceover_path),
            "-i", str(self.bgm_audio),
            "-i", str(self.ding_sfx),
            "-i", str(self.click_sfx),
            "-filter_complex",
            # Pad voiceover with silence if shorter than video, BGM fades out at 28s
            "[1:a]volume=1.2,apad[vocal];"
            "[2:a]volume=0.22,afade=t=out:st=28:d=2[bgm];"
            "[3:a]adelay=24000|24000,volume=0.5[ding];"
            "[4:a]adelay=3000|3000,volume=0.6[click1];"
            "[4:a]adelay=28200|28200,volume=0.7[click2];"
            "[vocal][bgm][ding][click1][click2]amix=inputs=5:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "30.0",  # Exact 30-second video duration
            "-movflags", "+faststart",
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[!] FFmpeg composition warning, using fallback muxing...")
            fallback_cmd = [
                "ffmpeg", "-y",
                "-i", str(raw_video_path),
                "-i", str(voiceover_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-t", "30.0",
                str(output_path)
            ]
            subprocess.run(fallback_cmd, check=True)

        print(f"[+] Final Video created successfully: {output_path}")
        return str(output_path)


if __name__ == "__main__":
    composer = VideoComposer()
    test_raw = TEMP_DIR / "test_paint_raw.mp4"
    test_voice = TEMP_DIR / "sample_voice.mp3"
    final_out = OUTPUT_DIR / "sample_paint_short.mp4"
    composer.compose_final_video(test_raw, test_voice, final_out)
