"""
Pure Python Audio Mixer for Kids Mystery Video
Guarantees 100% reliable, frame-accurate mixing without FFmpeg amix cutoff bugs.
Mixes:
- 6 Voiceover segments
- BGM cheerful marimba loop (entire 34.6s)
- Cute animal roar clue
- Bubble pop SFX for clues
- Woodblock clock ticks for 5-4-3-2-1 countdown
- Celebratory fanfare & kids cheering for reveal
- Bell ding for Like & Subscribe CTA
"""
import wave
import numpy as np
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"

SAMPLE_RATE = 44100
TOTAL_DURATION = 34.60
TOTAL_SAMPLES = int(SAMPLE_RATE * TOTAL_DURATION)

def load_audio_as_float(path, target_sr=SAMPLE_RATE):
    """Loads any mp3 or wav as float32 numpy array at target_sr (mono)."""
    temp_wav = TEMP_DIR / f"_resample_{Path(path).stem}.wav"
    cmd = [
        "ffmpeg", "-y", "-i", str(path),
        "-ac", "1", "-ar", str(target_sr),
        "-f", "wav", str(temp_wav)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    with wave.open(str(temp_wav), "rb") as wf:
        data = wf.readframes(wf.getnframes())
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    if temp_wav.exists():
        temp_wav.unlink()
    return samples

def overlay(canvas, sound, start_time_sec, volume=1.0):
    """Overlays sound onto canvas at start_time_sec with specified volume."""
    start_idx = int(start_time_sec * SAMPLE_RATE)
    if start_idx >= len(canvas):
        return
    end_idx = min(len(canvas), start_idx + len(sound))
    length = end_idx - start_idx
    canvas[start_idx:end_idx] += sound[:length] * volume

def build_composite_audio(output_audio_path):
    print("[*] Mixing multi-track kids audio in Python (sample-accurate)...")
    master = np.zeros(TOTAL_SAMPLES, dtype=np.float32)

    # 1. Background Music (cheerful marimba loop, volume = 0.28, fade out last 2s)
    bgm = load_audio_as_float(ASSETS_DIR / "cheerful_bgm.wav")
    # Loop BGM to fill duration
    bgm_looped = np.tile(bgm, int(np.ceil(TOTAL_DURATION / (len(bgm)/SAMPLE_RATE))))[:TOTAL_SAMPLES]
    # Apply fade out
    fade_len = int(2.5 * SAMPLE_RATE)
    fade_curve = np.linspace(1.0, 0.0, fade_len)
    bgm_looped[-fade_len:] *= fade_curve
    master += bgm_looped * 0.28

    # 2. Voiceover clips (volume = 1.35)
    v_hook = load_audio_as_float(TEMP_DIR / "p1_hook.mp3")
    v_clue1 = load_audio_as_float(TEMP_DIR / "p2_clue1.mp3")
    v_clue2 = load_audio_as_float(TEMP_DIR / "p3_clue2.mp3")
    v_countdown = load_audio_as_float(TEMP_DIR / "p4_countdown.mp3")
    v_reveal = load_audio_as_float(TEMP_DIR / "p5_reveal.mp3")
    v_outro = load_audio_as_float(TEMP_DIR / "p6_outro.mp3")

    overlay(master, v_hook, 0.0, volume=1.35)
    overlay(master, v_clue1, 6.0, volume=1.35)
    overlay(master, v_clue2, 10.0, volume=1.35)
    overlay(master, v_countdown, 14.0, volume=1.35)
    overlay(master, v_reveal, 19.2, volume=1.40)
    overlay(master, v_outro, 26.5, volume=1.35)

    # 3. Sound Effects:
    # Lion roar clue at 3.3s
    roar = load_audio_as_float(ASSETS_DIR / "lion_cub_roar.wav")
    overlay(master, roar, 3.2, volume=0.85)

    # Pop SFX when clue cards slide in
    pop = load_audio_as_float(ASSETS_DIR / "pop.wav")
    overlay(master, pop, 6.0, volume=0.7)
    overlay(master, pop, 10.0, volume=0.7)

    # Countdown ticks (5, 4, 3, 2, 1 at 14.2s, 15.2s, 16.2s, 17.2s, 18.2s)
    tick = load_audio_as_float(ASSETS_DIR / "tick.wav")
    for t_tick in [14.2, 15.2, 16.2, 17.2, 18.2]:
        overlay(master, tick, t_tick, volume=0.75)

    # Celebration fanfare chime at 19.2s
    fanfare = load_audio_as_float(ASSETS_DIR / "fanfare.wav")
    overlay(master, fanfare, 19.2, volume=0.90)

    # Ding bell at 26.8s (Subscribe CTA)
    ding = load_audio_as_float(ASSETS_DIR / "ding.wav")
    overlay(master, ding, 26.8, volume=0.65)

    # Normalize & soft clip to prevent distortion
    max_val = np.max(np.abs(master))
    if max_val > 0.95:
        master = master * (0.95 / max_val)

    # Save to 16-bit PCM WAV
    int_samples = (master * 32767).astype(np.int16)
    with wave.open(str(output_audio_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_samples.tobytes())

    print(f"[+] Master kids audio generated successfully: {output_audio_path} ({len(master)/SAMPLE_RATE:.2f}s)")
    return output_audio_path

def merge_video_and_audio(raw_video_path, audio_path, output_mp4_path):
    print(f"[*] Merging raw video + master audio into final MP4...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_video_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(output_mp4_path)
    ]
    subprocess.run(cmd, check=True)
    print(f"[SUCCESS] Complete kids video ready: {output_mp4_path}")

if __name__ == "__main__":
    audio_path = TEMP_DIR / "master_kids_audio.wav"
    build_composite_audio(audio_path)
    final_video = OUTPUT_DIR / "kids_mystery_lion_demo.mp4"
    merge_video_and_audio(TEMP_DIR / "kids_raw_render.mp4", audio_path, final_video)
