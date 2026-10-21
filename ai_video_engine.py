"""
AI Video Generation Engine (Hugging Face LTX-Video Distilled)
Generates photorealistic POV drawing tutorials with a real living human hand,
muscular flexibility, pencil grip physics, and dynamic graphite shading on paper.
"""
import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

import cv2
from gradio_client import Client, handle_file

from config import BASE_DIR, TEMP_DIR, OUTPUT_DIR, ASSETS_DIR

# Ensure UTF-8 output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class AIVideoEngine:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.space_name = "Lightricks/ltx-video-distilled"
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            print(f"[*] Connecting to Hugging Face AI Video Space ({self.space_name})...")
            self.client = Client(self.space_name, token=self.hf_token)
            print("[+] Connected to Hugging Face AI Video Space successfully!")
        except Exception as e:
            print(f"[!] Warning: Could not initialize Hugging Face client: {e}")
            self.client = None

    def generate_stage1_outline(self, object_name: str, duration: float = 6.0) -> Path:
        """
        Generates Stage 1 Text-to-Video: POV hand drawing the pencil outline.
        """
        prompt = (
            f"POV close up top-down shot of a real artist hand holding a graphite pencil, "
            f"smoothly sketching a simple {object_name} outline on clean white paper on a wooden desk, "
            f"soft studio lighting, ultra realistic 4k cinematic"
        )
        negative_prompt = "worst quality, blurry, cartoon, 3d render, watermark, text, signature, distorted fingers, stiff plastic hand"
        
        print(f"[*] Generating Stage 1 (Outline T2V) for '{object_name}'...")
        t0 = time.time()
        res = self.client.predict(
            prompt=prompt,
            negative_prompt=negative_prompt,
            input_image_filepath=None,
            input_video_filepath=None,
            height_ui=704,
            width_ui=512,
            mode="text-to-video",
            duration_ui=duration,
            ui_frames_to_use=9,
            seed_ui=42,
            randomize_seed=True,
            ui_guidance_scale=3.0,
            improve_texture_flag=True,
            api_name="/text_to_video"
        )
        video_temp_path = res[0]["video"]
        dest_path = TEMP_DIR / f"ai_{object_name.replace(' ', '_')}_s1.mp4"
        shutil.copy(video_temp_path, dest_path)
        print(f"[+] Stage 1 finished in {time.time() - t0:.1f}s -> {dest_path.name}")
        return dest_path

    def generate_stage_continuation(self, input_image_path: Path, prompt: str, stage_tag: str, duration: float = 5.0) -> Path:
        """
        Generates chained Stage Image-to-Video continuing from the previous frame.
        """
        negative_prompt = "worst quality, blurry, distorted hand, cartoon, 3d render, watermark, signature"
        print(f"[*] Generating {stage_tag} (I2V Continuation)...")
        t0 = time.time()
        res = self.client.predict(
            prompt=prompt,
            negative_prompt=negative_prompt,
            input_image_filepath=handle_file(str(input_image_path)),
            input_video_filepath=None,
            height_ui=704,
            width_ui=512,
            mode="image-to-video",
            duration_ui=duration,
            ui_frames_to_use=9,
            seed_ui=42,
            randomize_seed=True,
            ui_guidance_scale=3.0,
            improve_texture_flag=True,
            api_name="/image_to_video"
        )
        video_temp_path = res[0]["video"]
        dest_path = TEMP_DIR / f"ai_{stage_tag}.mp4"
        shutil.copy(video_temp_path, dest_path)
        print(f"[+] {stage_tag} finished in {time.time() - t0:.1f}s -> {dest_path.name}")
        return dest_path

    @staticmethod
    def extract_last_frame(video_path: Path, output_frame_path: Path) -> Path:
        """
        Extracts the very last frame of a video to serve as the keyframe for the next stage.
        """
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total_frames - 1))
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError(f"Could not read last frame from {video_path}")
        cv2.imwrite(str(output_frame_path), frame)
        return output_frame_path

    def render_full_tutorial(
        self,
        object_name: str,
        display_name: str,
        voiceover_path: Path,
        output_video_path: Path
    ) -> Path:
        """
        Generates complete 3-stage living AI video, then muxes voiceover, BGM, ASMR, and text overlays
        into a finalized 9:16 vertical 720x1280 MP4.
        """
        safe_name = object_name.replace(" ", "_")
        
        # 1. Stage 1: Outline
        s1_video = self.generate_stage1_outline(object_name, duration=6.0)
        s1_last_frame = TEMP_DIR / f"ai_{safe_name}_s1_last.jpg"
        self.extract_last_frame(s1_video, s1_last_frame)

        # 2. Stage 2: Shading & Hatching
        s2_prompt = (
            f"POV close up top-down shot of artist hand using pencil to add graphite shading and 45 degree shadow details "
            f"to the {object_name} sketch on paper, pencil tip moving smoothly, cinematic lighting, 4k"
        )
        s2_video = self.generate_stage_continuation(s1_last_frame, s2_prompt, f"{safe_name}_s2", duration=5.0)
        s2_last_frame = TEMP_DIR / f"ai_{safe_name}_s2_last.jpg"
        self.extract_last_frame(s2_video, s2_last_frame)

        # 3. Stage 3: Highlights & Reveal
        s3_prompt = (
            f"POV close up top-down shot of artist hand putting final graphite pencil highlights on the {object_name} sketch "
            f"and gently lifting hand to reveal completed pencil drawing on paper, 4k ultra realistic, cinematic desk lighting"
        )
        s3_video = self.generate_stage_continuation(s2_last_frame, s3_prompt, f"{safe_name}_s3", duration=5.0)
        final_frame = TEMP_DIR / f"ai_{safe_name}_final.jpg"
        self.extract_last_frame(s3_video, final_frame)

        # 4. Master FFmpeg Composition
        print(f"[*] Assembling master tutorial video for '{display_name}'...")
        bgm_path = ASSETS_DIR / "bgm.wav"
        scratch_path = ASSETS_DIR / "scratch.wav"
        ding_path = ASSETS_DIR / "ding.wav"

        upper_title = f"HOW TO DRAW {display_name.upper()}"

        filter_complex = (
            # 0: Hook image (3.5s)
            "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
            "zoompan=z='min(zoom+0.0015,1.15)':d=105:s=720x1280:fps=30,"
            f"drawtext=text='{upper_title}':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=180:box=1:boxcolor=black@0.65:boxborderw=15,"
            "drawtext=text='Step-by-step for Beginners':fontcolor=yellow:fontsize=32:x=(w-text_w)/2:y=260:box=1:boxcolor=black@0.5:boxborderw=10,"
            "setsar=1,fps=30[v_hook];"

            # 1: Stage 1 (stretched to 10.0s)
            "[1:v]setpts=1.7*PTS,scale=720:1280:flags=lanczos,unsharp=5:5:0.8:5:5:0.0,"
            "trim=duration=10.0,"
            "drawtext=text='Step 1 - Basic Outline':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=140:box=1:boxcolor=black@0.6:boxborderw=12,"
            "setsar=1,fps=30[v_s1];"

            # 2: Stage 2 (stretched to 10.3s)
            "[2:v]setpts=2.02*PTS,scale=720:1280:flags=lanczos,unsharp=5:5:0.8:5:5:0.0,"
            "trim=duration=10.3,"
            "drawtext=text='Step 2 - 45 Degree Shading':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=140:box=1:boxcolor=black@0.6:boxborderw=12,"
            "setsar=1,fps=30[v_s2];"

            # 3: Stage 3 (stretched to 7.0s)
            "[3:v]setpts=1.37*PTS,scale=720:1280:flags=lanczos,unsharp=5:5:0.8:5:5:0.0,"
            "trim=duration=7.0,"
            "drawtext=text='Step 3 - Details and Highlights':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=140:box=1:boxcolor=black@0.6:boxborderw=12,"
            "setsar=1,fps=30[v_s3];"

            # 4: Outro reveal (6.5s)
            "[4:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
            "zoompan=z='if(lte(zoom,1.0),1.1,max(1.001,zoom-0.0015))':d=195:s=720x1280:fps=30,"
            "drawtext=text='MASTERPIECE COMPLETE!':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=180:box=1:boxcolor=black@0.7:boxborderw=15,"
            "drawtext=text='SUBSCRIBE FOR DAILY ART':fontcolor=red:fontsize=36:x=(w-text_w)/2:y=1050:box=1:boxcolor=white@0.9:boxborderw=14,"
            "setsar=1,fps=30[v_outro];"

            # Concat video streams
            "[v_hook][v_s1][v_s2][v_s3][v_outro]concat=n=5:v=1[v_full];"

            # Audio mixing
            "[5:a]volume=1.35,apad[vocal];"
            "[6:a]volume=0.20,afade=t=out:st=34.0:d=3.0[bgm];"
            "[7:a]volume=0.18,afade=t=out:st=30.0:d=2.0[scratch];"
            "[8:a]adelay=30500|30500,volume=0.45[ding];"
            "[vocal][bgm][scratch][ding]amix=inputs=4:duration=first:dropout_transition=2[a_full]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", "3.5", "-i", str(final_frame),
            "-i", str(s1_video),
            "-i", str(s2_video),
            "-i", str(s3_video),
            "-loop", "1", "-t", "6.5", "-i", str(final_frame),
            "-i", str(voiceover_path),
            "-stream_loop", "-1", "-i", str(bgm_path),
            "-stream_loop", "-1", "-i", str(scratch_path),
            "-i", str(ding_path),
            "-filter_complex", filter_complex,
            "-map", "[v_full]",
            "-map", "[a_full]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "37.25",
            "-movflags", "+faststart",
            str(output_video_path)
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg assembly failed: {res.stderr}")

        print(f"[+] Masterpiece AI tutorial created successfully: {output_video_path}")
        return output_video_path


if __name__ == "__main__":
    engine = AIVideoEngine()
    print("[+] AIVideoEngine initialized and ready.")
