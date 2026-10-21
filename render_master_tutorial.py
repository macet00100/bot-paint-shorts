"""
Assemble full AI Pencil Sketch Tutorial Video with 3 Stages + Hook + Reveal + Voice + ASMR + BGM.
"""
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

def build_full_tutorial_video():
    voice_path = TEMP_DIR / "ai_apple_voice.mp3"
    stage1_video = TEMP_DIR / "ltx_6s_apple.mp4"
    stage2_video = TEMP_DIR / "ltx_chained_apple.mp4"
    stage3_video = TEMP_DIR / "ltx_stage3_apple.mp4"
    final_frame = TEMP_DIR / "apple_stage3_last.jpg"
    
    bgm_path = ASSETS_DIR / "bgm.wav"
    scratch_path = ASSETS_DIR / "scratch.wav"
    ding_path = ASSETS_DIR / "ding.wav"
    
    output_video = OUTPUT_DIR / "ai_masterpiece_apple_tutorial.mp4"
    
    # Target resolution: 720x1280 (vertical 9:16)
    # Hook (0 - 3.5s): Ken burns zoom on finished art with text "Can you sketch this? 🍎"
    # S1 (3.5 - 13.5s, 10s): Stage 1 slow-motion 0.59x speed
    # S2 (13.5 - 23.8s, 10.3s): Stage 2 slow-motion 0.5x speed
    # S3 (23.8 - 30.8s, 7.0s): Stage 3 slow-motion 0.73x speed
    # Outro (30.8 - 37.3s, 6.5s): Reveal & Subscribe CTA
    
    filter_complex = (
        # 0: Hook image (3.5s)
        "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
        "zoompan=z='min(zoom+0.0015,1.15)':d=105:s=720x1280:fps=30,"
        "drawtext=text='HOW TO DRAW AN APPLE':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=180:box=1:boxcolor=black@0.65:boxborderw=15,"
        "drawtext=text='Step-by-step for Beginners':fontcolor=yellow:fontsize=32:x=(w-text_w)/2:y=260:box=1:boxcolor=black@0.5:boxborderw=10,"
        "setsar=1,fps=30[v_hook];"
        
        # 1: Stage 1 (stretched to 10.0s = 300 frames)
        "[1:v]setpts=1.7*PTS,scale=720:1280:flags=lanczos,unsharp=5:5:0.8:5:5:0.0,"
        "trim=duration=10.0,"
        "drawtext=text='Step 1 - Basic Outline':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=140:box=1:boxcolor=black@0.6:boxborderw=12,"
        "setsar=1,fps=30[v_s1];"
        
        # 2: Stage 2 (stretched to 10.3s = 309 frames)
        "[2:v]setpts=2.02*PTS,scale=720:1280:flags=lanczos,unsharp=5:5:0.8:5:5:0.0,"
        "trim=duration=10.3,"
        "drawtext=text='Step 2 - 45 Degree Shading':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=140:box=1:boxcolor=black@0.6:boxborderw=12,"
        "setsar=1,fps=30[v_s2];"
        
        # 3: Stage 3 (stretched to 7.0s = 210 frames)
        "[3:v]setpts=1.37*PTS,scale=720:1280:flags=lanczos,unsharp=5:5:0.8:5:5:0.0,"
        "trim=duration=7.0,"
        "drawtext=text='Step 3 - Stem and Highlights':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=140:box=1:boxcolor=black@0.6:boxborderw=12,"
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
        "-loop", "1", "-t", "3.5", "-i", str(final_frame),    # Input 0: Hook image
        "-i", str(stage1_video),                               # Input 1: Stage 1 video
        "-i", str(stage2_video),                               # Input 2: Stage 2 video
        "-i", str(stage3_video),                               # Input 3: Stage 3 video
        "-loop", "1", "-t", "6.5", "-i", str(final_frame),    # Input 4: Outro image
        "-i", str(voice_path),                                 # Input 5: Voiceover (37.25s)
        "-stream_loop", "-1", "-i", str(bgm_path),             # Input 6: Background music
        "-stream_loop", "-1", "-i", str(scratch_path),         # Input 7: Scratch ASMR
        "-i", str(ding_path),                                  # Input 8: Ding bell
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
        str(output_video)
    ]
    
    print("[*] Running FFmpeg master tutorial render...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[!] FFmpeg error:", res.stderr)
    else:
        print(f"[+] Successfully rendered masterpiece: {output_video}")

if __name__ == "__main__":
    build_full_tutorial_video()
