"""
Generates high quality cartoon / kid sound effects for the guessing game.
- pop.wav: Bouncy cartoon bubble pop
- tick.wav: Woodblock clock tick
- fanfare.wav: Cheerful celebratory chime / harp glissando
- cheerful_bgm.wav: Upbeat, bouncy, joyful marimba melody for kids
"""
import numpy as np
import wave
from pathlib import Path

SAMPLE_RATE = 44100
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def save_wav(filename, data):
    # Normalize to 16-bit PCM
    data = np.clip(data, -1.0, 1.0)
    data = (data * 32767).astype(np.int16)
    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data.tobytes())

# 1. Bubble Pop (50ms)
t = np.linspace(0, 0.08, int(SAMPLE_RATE * 0.08), endpoint=False)
# Pitch sweeps from 400Hz up to 1200Hz
freq = np.linspace(350, 1100, len(t))
phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
pop_env = np.sin(np.pi * np.linspace(0, 1, len(t))) ** 2
pop_audio = np.sin(phase) * pop_env * 0.8
save_wav(ASSETS_DIR / "pop.wav", pop_audio)

# 2. Woodblock Tick (40ms)
t = np.linspace(0, 0.06, int(SAMPLE_RATE * 0.06), endpoint=False)
tick_env = np.exp(-t * 80)
tick_audio = (np.sin(2 * np.pi * 950 * t) + 0.4 * np.sin(2 * np.pi * 1400 * t)) * tick_env * 0.7
save_wav(ASSETS_DIR / "tick.wav", tick_audio)

# 3. Celebratory Fanfare / Chime (1.5s)
duration = 2.0
t_total = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
fanfare_audio = np.zeros_like(t_total)
# Arpeggio of sweet bell tones: C5, E5, G5, C6, E6, G6, C7
notes = [523.25, 659.25, 783.99, 1046.50, 1318.51, 1567.98, 2093.00]
for idx, freq in enumerate(notes):
    start_t = idx * 0.12
    note_dur = duration - start_t
    if note_dur <= 0:
        continue
    t_note = np.linspace(0, note_dur, int(SAMPLE_RATE * note_dur), endpoint=False)
    env = np.exp(-t_note * 4.5)
    # Bell harmonics
    tone = (np.sin(2 * np.pi * freq * t_note) +
            0.5 * np.sin(2 * np.pi * freq * 2 * t_note) +
            0.2 * np.sin(2 * np.pi * freq * 3 * t_note)) * env
    start_idx = int(start_t * SAMPLE_RATE)
    fanfare_audio[start_idx:start_idx + len(tone)] += tone * 0.25

save_wav(ASSETS_DIR / "fanfare.wav", fanfare_audio)

# 4. Cheerful Upbeat Kids Marimba BGM (35s loop)
bgm_dur = 38.0
t_bgm = np.linspace(0, bgm_dur, int(SAMPLE_RATE * bgm_dur), endpoint=False)
bgm_audio = np.zeros_like(t_bgm)

# Marimba pattern: bouncy C - G - Am - F
# Chords frequencies:
chords = [
    [261.63, 329.63, 392.00, 523.25], # C major
    [196.00, 246.94, 293.66, 392.00], # G major
    [220.00, 261.63, 329.63, 440.00], # A minor
    [174.61, 220.00, 261.63, 349.23], # F major
]

bpm = 124.0
beat_len = 60.0 / bpm
step_len = beat_len / 2 # 8th notes

total_steps = int(bgm_dur / step_len)
for s in range(total_steps):
    step_time = s * step_len
    chord_idx = (s // 8) % len(chords)
    chord = chords[chord_idx]
    
    # Marimba arpeggio note
    note_freq = chord[s % 4] * (2.0 if (s % 2 == 1) else 1.0)
    
    # Note envelope (plucky marimba)
    note_samples = int(SAMPLE_RATE * 0.25)
    if int(step_time * SAMPLE_RATE) + note_samples >= len(bgm_audio):
        break
    t_n = np.linspace(0, 0.25, note_samples, endpoint=False)
    env_m = np.exp(-t_n * 16.0)
    marimba_tone = (np.sin(2 * np.pi * note_freq * t_n) +
                    0.3 * np.sin(2 * np.pi * note_freq * 2.75 * t_n)) * env_m * 0.22
    
    idx_s = int(step_time * SAMPLE_RATE)
    bgm_audio[idx_s:idx_s + note_samples] += marimba_tone

    # Bass note on downbeats
    if s % 4 == 0:
        bass_freq = chord[0] * 0.5
        t_b = np.linspace(0, 0.4, int(SAMPLE_RATE * 0.4), endpoint=False)
        env_b = np.exp(-t_b * 8.0)
        bass_tone = np.sin(2 * np.pi * bass_freq * t_b) * env_b * 0.35
        rem = min(len(bass_tone), len(bgm_audio) - idx_s)
        bgm_audio[idx_s:idx_s + rem] += bass_tone[:rem]

save_wav(ASSETS_DIR / "cheerful_bgm.wav", bgm_audio)
print("Generated pop.wav, tick.wav, fanfare.wav, cheerful_bgm.wav successfully!")
