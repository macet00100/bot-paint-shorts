"""
Kids Mystery Guessing Game - Automated Video Generator Engine (1080x1920 9:16 Vertical)
Renders complete, interactive, high-retention shorts videos:
- Dynamic animated cartoon background with floating bubbles
- Top Header banner & Sub-banners
- Glowing mystery silhouette with gentle suspense pulse
- Clue cards sliding in with pop SFX
- Bouncing 5-second countdown circular coins with woodblock ticks
- Confetti particle explosion & 3D Pixar character reveal
- Cheerful Marimba BGM + Celebration fanfare + CTA ding bell
- 100% Python sample-accurate audio mixer (Zero FFmpeg cutoff bugs)
"""
import math
import random
import wave
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import BASE_DIR, TEMP_DIR, OUTPUT_DIR, ASSETS_DIR

WIDTH = 1080
HEIGHT = 1920
FPS = 30
SAMPLE_RATE = 44100
TOTAL_DURATION = 34.60
TOTAL_FRAMES = int(FPS * TOTAL_DURATION)
TOTAL_SAMPLES = int(SAMPLE_RATE * TOTAL_DURATION)

LOCAL_FONT = Path(__file__).resolve().parent / "assets" / "fonts" / "comicbd.ttf"
if LOCAL_FONT.exists():
    FONT_PATH = str(LOCAL_FONT)
elif Path("C:/Windows/Fonts/comicbd.ttf").exists():
    FONT_PATH = "C:/Windows/Fonts/comicbd.ttf"
else:
    FONT_PATH = "comicbd.ttf" 

try:
    FONT_TITLE = ImageFont.truetype(FONT_PATH, 74)
    FONT_SUB = ImageFont.truetype(FONT_PATH, 48)
    FONT_CLUE = ImageFont.truetype(FONT_PATH, 42)
    FONT_COUNTDOWN = ImageFont.truetype(FONT_PATH, 160)
    FONT_CTA = ImageFont.truetype(FONT_PATH, 48)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUB = ImageFont.load_default()
    FONT_CLUE = ImageFont.load_default()
    FONT_COUNTDOWN = ImageFont.load_default()
    FONT_CTA = ImageFont.load_default()


class KidsVideoEngine:
    def __init__(self):
        self.particles = self._init_particles()

    def _init_particles(self):
        random.seed(42)
        confetti_colors = [
            (255, 60, 60), (255, 200, 0), (0, 220, 255),
            (120, 255, 60), (255, 100, 220), (255, 255, 255)
        ]
        particles = []
        for _ in range(130):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 34)
            particles.append({
                "x": 540.0,
                "y": 950.0,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - random.uniform(6, 15),
                "size": random.randint(14, 26),
                "color": random.choice(confetti_colors)
            })
        return particles

    def _make_background(self, frame_idx):
        base = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        y_vals = np.linspace(0, 1, HEIGHT)[:, None]
        top_c = np.array([245, 190, 70])    # Soft cyan-blue
        bot_c = np.array([120, 235, 255])   # Warm golden yellow
        gradient_1d = (top_c * (1 - y_vals) + bot_c * y_vals).astype(np.uint8)
        base[:, :] = gradient_1d[:, None, :]

        for i in range(12):
            bx = int((i * 95 + frame_idx * 1.5) % (WIDTH + 100) - 50)
            by = int((i * 170 + math.sin(frame_idx * 0.05 + i) * 60) % HEIGHT)
            radius = int(35 + 15 * math.sin(i))
            cv2.circle(base, (bx, by), radius, (255, 255, 255), -1)

        return cv2.GaussianBlur(base, (31, 31), 0)

    @staticmethod
    def _overlay_rgba(base_bgr, overlay_rgba, x, y, scale=1.0, alpha_mult=1.0):
        h_ov, w_ov = overlay_rgba.shape[:2]
        new_w = max(1, int(w_ov * scale))
        new_h = max(1, int(h_ov * scale))
        resized = cv2.resize(overlay_rgba, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        x1 = int(x - new_w // 2)
        y1 = int(y - new_h // 2)
        x2 = x1 + new_w
        y2 = y1 + new_h

        bx1, by1 = max(0, x1), max(0, y1)
        bx2, by2 = min(WIDTH, x2), min(HEIGHT, y2)
        if bx1 >= bx2 or by1 >= by2:
            return

        ox1, oy1 = bx1 - x1, by1 - y1
        ox2, oy2 = ox1 + (bx2 - bx1), oy1 + (by2 - by1)

        patch = resized[oy1:oy2, ox1:ox2]
        alpha = (patch[:, :, 3].astype(float) / 255.0) * alpha_mult

        for c in range(3):
            base_bgr[by1:by2, bx1:bx2, c] = (
                patch[:, :, c] * alpha + base_bgr[by1:by2, bx1:bx2, c] * (1.0 - alpha)
            ).astype(np.uint8)

    @classmethod
    def _draw_multiline_pill_card(cls, draw, text, font, cy, bg_color, border_color, text_color, max_width=880, slide_offset=0):
        words = text.split()
        lines = []
        cur_line = []
        pad_x, pad_y = 42, 16
        avail_w = max_width - 2 * pad_x

        for w in words:
            test_line = " ".join(cur_line + [w])
            bbox = font.getbbox(test_line)
            if (bbox[2] - bbox[0]) <= avail_w:
                cur_line.append(w)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                    cur_line = [w]
                else:
                    lines.append(w)
                    cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        line_heights = []
        line_widths = []
        for l in lines:
            bbox = font.getbbox(l)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])

        max_line_w = max(line_widths) if line_widths else 100
        line_spacing = 8
        total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)

        cx = WIDTH // 2 + slide_offset
        card_w = min(max_width, max_line_w + 2 * pad_x)
        card_h = total_text_h + 2 * pad_y

        x1 = cx - card_w // 2
        y1 = cy - card_h // 2
        x2 = cx + card_w // 2
        y2 = cy + card_h // 2
        r = min(32, card_h // 2)

        draw.rounded_rectangle([x1 + 6, y1 + 8, x2 + 6, y2 + 8], radius=r, fill=(40, 40, 40, 90))
        draw.rounded_rectangle([x1 - 4, y1 - 4, x2 + 4, y2 + 4], radius=r + 4, fill=border_color)
        draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=bg_color)

        cur_y = y1 + pad_y
        for i, l in enumerate(lines):
            lw = line_widths[i]
            lh = line_heights[i]
            lx = cx - lw // 2
            bbox = font.getbbox(l)
            draw.text((lx - bbox[0], cur_y - bbox[1]), l, font=font, fill=text_color)
            cur_y += lh + line_spacing

    @staticmethod
    def _draw_pill_card(draw, text, font, cy, bg_color, border_color, text_color, slide_offset=0):
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad_x, pad_y = 50, 22
        cx = WIDTH // 2 + slide_offset
        x1, y1 = cx - tw // 2 - pad_x, cy - th // 2 - pad_y
        x2, y2 = cx + tw // 2 + pad_x, cy + th // 2 + pad_y
        r = (y2 - y1) // 2

        draw.rounded_rectangle([x1 + 6, y1 + 8, x2 + 6, y2 + 8], radius=r, fill=(40, 40, 40, 90))
        draw.rounded_rectangle([x1 - 4, y1 - 4, x2 + 4, y2 + 4], radius=r + 4, fill=border_color)
        draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=bg_color)
        draw.text((cx - tw // 2 - bbox[0], cy - th // 2 - bbox[1] - 4), text, font=font, fill=text_color)

    @staticmethod
    def _draw_circular_badge(draw, text, font, cx, cy, radius, bg_color, border_color=(255, 255, 255), border_w=12):
        draw.ellipse([cx - radius + 6, cy - radius + 8, cx + radius + 6, cy + radius + 8], fill=(30, 30, 30, 80))
        draw.ellipse([cx - radius - border_w, cy - radius - border_w, cx + radius + border_w, cy + radius + border_w], fill=border_color)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=bg_color)
        bbox = font.getbbox(text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw // 2 - bbox[0], cy - th // 2 - bbox[1] - 4), text, font=font, fill=(255, 255, 255))

    def render_video_frames(self, quiz_pkg: dict, cutout_path: Path, sil_path: Path, output_raw_path: Path):
        sil_img = cv2.imread(str(sil_path), cv2.IMREAD_UNCHANGED)
        cutout_img = cv2.imread(str(cutout_path), cv2.IMREAD_UNCHANGED)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(output_raw_path), fourcc, FPS, (WIDTH, HEIGHT))

        category_noun = quiz_pkg.get("category", "animal").upper()
        if category_noun.endswith("S"):
            header_title = f"GUESS THE {category_noun[:-1]}!"
        else:
            header_title = f"GUESS THE {category_noun}!"

        reveal_title = quiz_pkg["reveal_text"].upper()
        clue1_text = quiz_pkg["clue1"]
        clue2_text = quiz_pkg["clue2"]

        print(f"[*] Rendering {TOTAL_FRAMES} video frames for '{quiz_pkg['name']}'...")
        for f in range(TOTAL_FRAMES):
            bg = self._make_background(f)
            center_x, center_y = 540, 1060
            is_revealed = (f >= 576)

            if not is_revealed:
                pulse_scale = 1.05 + 0.03 * math.sin(f * 0.12)
                self._overlay_rgba(bg, sil_img, center_x, center_y, scale=pulse_scale)
            else:
                reveal_progress = min(1.0, (f - 576) / 20.0)
                bounce = 1.05 + 0.04 * math.sin((f - 576) * 0.15)
                scale_anim = (0.5 + 0.55 * math.sin(reveal_progress * math.pi / 2)) if (reveal_progress < 1.0) else bounce
                self._overlay_rgba(bg, cutout_img, center_x, center_y, scale=scale_anim)

                confetti_t = (f - 576) / FPS
                if confetti_t < 4.0:
                    for p in self.particles:
                        px = int(p["x"] + p["vx"] * (f - 576))
                        py = int(p["y"] + p["vy"] * (f - 576) + 0.5 * 18 * (confetti_t ** 2) * 30)
                        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                            cv2.circle(bg, (px, py), p["size"], p["color"], -1)

            img_pil = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil, "RGBA")

            # Header Banner (Positioned in YouTube Safe Zone below top controls: cy=285)
            header_bounce = int(8 * math.sin(f * 0.1))
            self._draw_pill_card(draw, header_title, FONT_TITLE, cy=285 + header_bounce,
                                 bg_color=(255, 190, 0), border_color=(255, 255, 255), text_color=(40, 20, 0))

            if f < 180:
                self._draw_pill_card(draw, "Can you guess who it is?", FONT_SUB, cy=405,
                                     bg_color=(255, 255, 255), border_color=(255, 180, 0), text_color=(50, 50, 50))
                qm_bounce = int(12 * math.sin(f * 0.2))
                self._draw_circular_badge(draw, "?", FONT_COUNTDOWN, cx=540, cy=1040 + qm_bounce,
                                          radius=120, bg_color=(255, 60, 60))

            elif 180 <= f < 300:
                slide1 = max(0, int(1200 * (1.0 - (f - 180) / 15.0)))
                self._draw_multiline_pill_card(draw, clue1_text, FONT_CLUE, cy=415,
                                               bg_color=(255, 255, 255), border_color=(255, 120, 0), text_color=(200, 80, 0),
                                               slide_offset=-slide1)

            elif 300 <= f < 420:
                self._draw_multiline_pill_card(draw, clue1_text, FONT_CLUE, cy=400,
                                               bg_color=(255, 255, 255), border_color=(255, 120, 0), text_color=(200, 80, 0))
                slide2 = max(0, int(1200 * (1.0 - (f - 300) / 15.0)))
                self._draw_multiline_pill_card(draw, clue2_text, FONT_CLUE, cy=520,
                                               bg_color=(255, 240, 200), border_color=(255, 180, 0), text_color=(160, 70, 0),
                                               slide_offset=slide2)

            elif 420 <= f < 576:
                countdown_val = max(1, 5 - int((f - 420) / 31))
                self._draw_pill_card(draw, "COUNTDOWN TIME!", FONT_SUB, cy=405,
                                     bg_color=(255, 255, 255), border_color=(255, 60, 60), text_color=(220, 30, 30))
                cd_bounce = int(12 * abs(math.sin(f * 0.3)))
                cd_colors = [(255, 60, 60), (255, 120, 0), (255, 200, 0), (0, 200, 255), (100, 240, 60)]
                self._draw_circular_badge(draw, str(countdown_val), FONT_COUNTDOWN,
                                          cx=540, cy=1040 - cd_bounce, radius=130,
                                          bg_color=cd_colors[countdown_val - 1])

            elif 576 <= f < 795:
                self._draw_pill_card(draw, reveal_title, FONT_TITLE, cy=410,
                                     bg_color=(255, 60, 100), border_color=(255, 255, 255), text_color=(255, 255, 255))
                self._draw_multiline_pill_card(draw, quiz_pkg.get("fun_fact", "Super Smart Explorer!"), FONT_CLUE, cy=535,
                                               bg_color=(255, 255, 255), border_color=(255, 190, 0), text_color=(200, 100, 0))

            else:
                self._draw_pill_card(draw, "Did you guess it right?", FONT_SUB, cy=405,
                                     bg_color=(255, 255, 255), border_color=(0, 200, 255), text_color=(0, 120, 200))
                sub_pulse = int(6 * math.sin(f * 0.2))
                self._draw_pill_card(draw, "SUBSCRIBE FOR DAILY GAMES!", FONT_CTA, cy=1540 + sub_pulse,
                                     bg_color=(255, 40, 60), border_color=(255, 255, 255), text_color=(255, 255, 255))

            final_frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            out.write(final_frame)

        out.release()
        print("[+] Video frames rendered successfully!")

    def _load_audio(self, path):
        temp_wav = TEMP_DIR / f"_tmp_{Path(path).stem}.wav"
        subprocess.run(["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "wav", str(temp_wav)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        with wave.open(str(temp_wav), "rb") as wf:
            data = wf.readframes(wf.getnframes())
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if temp_wav.exists():
            temp_wav.unlink()
        return samples

    def _overlay_audio(self, master, sound, start_sec, volume=1.0):
        start_idx = int(start_sec * SAMPLE_RATE)
        if start_idx >= len(master):
            return
        end_idx = min(len(master), start_idx + len(sound))
        length = end_idx - start_idx
        master[start_idx:end_idx] += sound[:length] * volume

    def mix_audio_track(self, voice_paths: dict, output_audio_path: Path):
        print("[*] Mixing audio in Python (sample-accurate, zero cutoff)...")
        master = np.zeros(TOTAL_SAMPLES, dtype=np.float32)

        # 1. BGM (cheerful marimba, volume 0.28, fade out last 2s)
        bgm = self._load_audio(ASSETS_DIR / "cheerful_bgm.wav")
        bgm_looped = np.tile(bgm, int(np.ceil(TOTAL_DURATION / (len(bgm)/SAMPLE_RATE))))[:TOTAL_SAMPLES]
        fade_len = int(2.5 * SAMPLE_RATE)
        bgm_looped[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)
        master += bgm_looped * 0.28

        # 2. Voice clips
        self._overlay_audio(master, self._load_audio(voice_paths["hook"]), 0.0, volume=1.35)
        self._overlay_audio(master, self._load_audio(voice_paths["clue1"]), 6.0, volume=1.35)
        self._overlay_audio(master, self._load_audio(voice_paths["clue2"]), 10.0, volume=1.35)
        self._overlay_audio(master, self._load_audio(voice_paths["countdown"]), 14.0, volume=1.35)
        self._overlay_audio(master, self._load_audio(voice_paths["reveal"]), 19.2, volume=1.40)
        self._overlay_audio(master, self._load_audio(voice_paths["outro"]), 26.5, volume=1.35)

        # 3. SFX
        roar = self._load_audio(ASSETS_DIR / "lion_cub_roar.wav")
        self._overlay_audio(master, roar, 3.2, volume=0.85)

        pop = self._load_audio(ASSETS_DIR / "pop.wav")
        self._overlay_audio(master, pop, 6.0, volume=0.7)
        self._overlay_audio(master, pop, 10.0, volume=0.7)

        tick = self._load_audio(ASSETS_DIR / "tick.wav")
        for t_tick in [14.2, 15.2, 16.2, 17.2, 18.2]:
            self._overlay_audio(master, tick, t_tick, volume=0.75)

        fanfare = self._load_audio(ASSETS_DIR / "fanfare.wav")
        self._overlay_audio(master, fanfare, 19.2, volume=0.90)

        ding = self._load_audio(ASSETS_DIR / "ding.wav")
        self._overlay_audio(master, ding, 26.8, volume=0.65)

        max_val = np.max(np.abs(master))
        if max_val > 0.95:
            master = master * (0.95 / max_val)

        int_samples = (master * 32767).astype(np.int16)
        with wave.open(str(output_audio_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(int_samples.tobytes())

        print(f"[+] Master audio generated: {output_audio_path.name}")
        return output_audio_path

    def assemble_final_mp4(self, raw_video_path: Path, audio_path: Path, output_mp4_path: Path):
        print(f"[*] Muxing final MP4 -> {output_mp4_path.name}...")
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
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[SUCCESS] Finished Video: {output_mp4_path}")
        return output_mp4_path


if __name__ == "__main__":
    engine = KidsVideoEngine()
    print("KidsVideoEngine initialized.")
