"""
Kids Mystery Guessing Game - Video Engine (1080x1920 Full HD 9:16 Vertical)
Renders a 100% automated, high-retention kids interactive quiz video:
- Hook & Mystery Silhouette with glowing border
- Animal roar sound clue
- Clue cards sliding in with pop SFX
- Bouncing 5-second animated countdown
- Confetti explosion & 3D Pixar Baby Lion reveal
- Celebration fanfare & Subscribe CTA
- Perfect voice & SFX audio mixing
"""
import math
import random
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30

FONT_PATH = "C:/Windows/Fonts/comicbd.ttf"
FONT_TITLE = ImageFont.truetype(FONT_PATH, 76)
FONT_SUB = ImageFont.truetype(FONT_PATH, 48)
FONT_CLUE = ImageFont.truetype(FONT_PATH, 44)
FONT_COUNTDOWN = ImageFont.truetype(FONT_PATH, 160)
FONT_CTA = ImageFont.truetype(FONT_PATH, 50)

# Pre-generate particles for confetti explosion (starts at frame 576 = ~19.2s)
random.seed(42)
CONFETTI_COLORS = [
    (255, 60, 60), (255, 200, 0), (0, 220, 255),
    (120, 255, 60), (255, 100, 220), (255, 255, 255)
]
PARTICLES = []
for _ in range(120):
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(8, 32)
    PARTICLES.append({
        "x": 540.0,
        "y": 950.0,
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed - random.uniform(6, 14),
        "size": random.randint(14, 26),
        "color": random.choice(CONFETTI_COLORS),
        "rot": random.uniform(0, 360),
        "vrot": random.uniform(-15, 15)
    })

def make_gradient_background(frame_idx, total_frames):
    """
    Creates a warm, joyful sunny sky gradient with subtle floating circles.
    """
    # Top color: Sky Cyan (240, 180, 50) in BGR
    # Bottom color: Warm Sunshine Yellow (100, 230, 255) in BGR
    t = frame_idx / total_frames
    base = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    # Fast vertical gradient
    y_vals = np.linspace(0, 1, HEIGHT)[:, None]
    top_c = np.array([245, 190, 70])    # Soft cyan-blue
    bot_c = np.array([120, 235, 255])   # Warm golden yellow
    gradient_1d = (top_c * (1 - y_vals) + bot_c * y_vals).astype(np.uint8)
    base[:, :] = gradient_1d[:, None, :]
    
    # Floating decorative soft bubbles
    for i in range(12):
        bx = int((i * 95 + frame_idx * 1.5) % (WIDTH + 100) - 50)
        by = int((i * 170 + math.sin(frame_idx * 0.05 + i) * 60) % HEIGHT)
        radius = int(35 + 15 * math.sin(i))
        cv2.circle(base, (bx, by), radius, (255, 255, 255), -1)
    
    # Blur background slightly to make bubbles soft
    base = cv2.GaussianBlur(base, (31, 31), 0)
    return base

def overlay_rgba(base_bgr, overlay_rgba, x, y, scale=1.0, alpha_mult=1.0):
    """
    Overlays RGBA image onto BGR background at center (x, y).
    """
    h_ov, w_ov = overlay_rgba.shape[:2]
    new_w = max(1, int(w_ov * scale))
    new_h = max(1, int(h_ov * scale))
    
    resized = cv2.resize(overlay_rgba, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    x1 = int(x - new_w // 2)
    y1 = int(y - new_h // 2)
    x2 = x1 + new_w
    y2 = y1 + new_h
    
    # Clip to base bounds
    bx1 = max(0, x1)
    by1 = max(0, y1)
    bx2 = min(WIDTH, x2)
    by2 = min(HEIGHT, y2)
    
    if bx1 >= bx2 or by1 >= by2:
        return
    
    ox1 = bx1 - x1
    oy1 = by1 - y1
    ox2 = ox1 + (bx2 - bx1)
    oy2 = oy1 + (by2 - by1)
    
    patch = resized[oy1:oy2, ox1:ox2]
    alpha = (patch[:, :, 3].astype(float) / 255.0) * alpha_mult
    
    for c in range(3):
        base_bgr[by1:by2, bx1:bx2, c] = (
            patch[:, :, c] * alpha + base_bgr[by1:by2, bx1:bx2, c] * (1.0 - alpha)
        ).astype(np.uint8)

def draw_circular_badge(draw, text, font, cx, cy, radius, bg_color, border_color=(255, 255, 255), border_w=10):
    """
    Draws a perfect circular badge with drop shadow and centered text (for ? and countdown numbers).
    """
    # Shadow
    draw.ellipse([cx - radius + 6, cy - radius + 8, cx + radius + 6, cy + radius + 8], fill=(30, 30, 30, 80))
    # Border
    draw.ellipse([cx - radius - border_w, cy - radius - border_w, cx + radius + border_w, cy + radius + border_w], fill=border_color)
    # Body
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=bg_color)
    # Centered text
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2 - bbox[0], cy - th // 2 - bbox[1] - 4), text, font=font, fill=(255, 255, 255))

def draw_pill_card(draw, text, font, cy, bg_color, border_color, text_color, slide_offset=0):
    """
    Draws a colorful pill-shaped card with drop shadow and border.
    """
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    pad_x = 55
    pad_y = 26
    cx = WIDTH // 2 + slide_offset
    x1 = cx - tw // 2 - pad_x
    y1 = cy - th // 2 - pad_y
    x2 = cx + tw // 2 + pad_x
    y2 = cy + th // 2 + pad_y
    r = (y2 - y1) // 2
    
    # Shadow
    draw.rounded_rectangle([x1 + 6, y1 + 8, x2 + 6, y2 + 8], radius=r, fill=(40, 40, 40, 90))
    # Border
    draw.rounded_rectangle([x1 - 4, y1 - 4, x2 + 4, y2 + 4], radius=r + 4, fill=border_color)
    # Body
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=bg_color)
    # Text
    draw.text((cx - tw // 2 - bbox[0], cy - th // 2 - bbox[1] - 4), text, font=font, fill=text_color)

def render_kids_video():
    raw_video_path = TEMP_DIR / "kids_raw_render.mp4"
    sil_img = cv2.imread(str(TEMP_DIR / "lion_mystery_silhouette.png"), cv2.IMREAD_UNCHANGED)
    lion_img = cv2.imread(str(TEMP_DIR / "lion_clean_transparent.png"), cv2.IMREAD_UNCHANGED)
    
    # Target duration: 34.6 seconds = 1038 frames at 30 fps
    total_frames = 1038
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(raw_video_path), fourcc, FPS, (WIDTH, HEIGHT))
    
    # Timeline keyframes (in frames):
    # 0 to 180 (0.0s - 6.0s): Hook & Mystery Silhouette + Question Mark
    # 180 to 300 (6.0s - 10.0s): Clue 1 slides in
    # 300 to 420 (10.0s - 14.0s): Clue 2 slides in
    # 420 to 576 (14.0s - 19.2s): Bouncing 5-second countdown
    # 576 to 795 (19.2s - 26.5s): Big Reveal & Celebration
    # 795 to 1038 (26.5s - 34.6s): Outro & Subscribe CTA
    
    print("[*] Rendering Kids Mystery Video frames (1080x1920 @ 30fps)...")
    
    for f in range(total_frames):
        sec = f / FPS
        bg = make_gradient_background(f, total_frames)
        
        # Center of Animal/Silhouette
        center_x = 540
        center_y = 1000
        
        is_revealed = (f >= 576)
        
        if not is_revealed:
            # Silhouette breathing pulse
            pulse_scale = 1.05 + 0.03 * math.sin(f * 0.12)
            overlay_rgba(bg, sil_img, center_x, center_y, scale=pulse_scale)
        else:
            # Reveal: Lion bounces in joyfully
            reveal_progress = min(1.0, (f - 576) / 20.0)
            # Elastic overshoot scale from 0.4 up to 1.15 then settling at 1.05
            bounce = 1.05 + 0.04 * math.sin((f - 576) * 0.15)
            if reveal_progress < 1.0:
                scale_anim = 0.5 + 0.55 * math.sin(reveal_progress * math.pi / 2)
            else:
                scale_anim = bounce
            
            overlay_rgba(bg, lion_img, center_x, center_y, scale=scale_anim)
            
            # Animate Confetti Particles
            confetti_t = (f - 576) / FPS
            if confetti_t < 4.0:
                for p in PARTICLES:
                    px = int(p["x"] + p["vx"] * (f - 576))
                    py = int(p["y"] + p["vy"] * (f - 576) + 0.5 * 18 * (confetti_t ** 2) * 30)
                    if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                        cv2.circle(bg, (px, py), p["size"], p["color"], -1)
        
        # Convert to PIL Image for high-end text and UI rendering
        img_pil = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil, "RGBA")
        
        # Top Header Banner
        header_bounce = int(8 * math.sin(f * 0.1))
        draw_pill_card(
            draw, "GUESS THE ANIMAL!", FONT_TITLE,
            cy=210 + header_bounce,
            bg_color=(255, 190, 0),
            border_color=(255, 255, 255),
            text_color=(40, 20, 0)
        )
        
        # UI overlays per phase
        if f < 180:
            # Phase 1: Hook
            draw_pill_card(
                draw, "Can you guess who it is?", FONT_SUB,
                cy=330,
                bg_color=(255, 255, 255),
                border_color=(255, 180, 0),
                text_color=(50, 50, 50)
            )
            # Bouncing circular question mark over silhouette
            qm_bounce = int(12 * math.sin(f * 0.2))
            draw_circular_badge(
                draw, "?", FONT_COUNTDOWN,
                cx=540, cy=960 + qm_bounce, radius=120,
                bg_color=(255, 60, 60),
                border_color=(255, 255, 255),
                border_w=12
            )
            
        elif 180 <= f < 300:
            # Phase 2: Clue 1 slides in from left
            slide1 = max(0, int(1200 * (1.0 - (f - 180) / 15.0)))
            draw_pill_card(
                draw, "CLUE 1: Golden fluffy mane!", FONT_CLUE,
                cy=350,
                bg_color=(255, 255, 255),
                border_color=(255, 120, 0),
                text_color=(200, 80, 0),
                slide_offset=-slide1
            )
            
        elif 300 <= f < 420:
            # Phase 3: Clue 1 + Clue 2 slides in from right
            draw_pill_card(
                draw, "CLUE 1: Golden fluffy mane!", FONT_CLUE,
                cy=340,
                bg_color=(255, 255, 255),
                border_color=(255, 120, 0),
                text_color=(200, 80, 0)
            )
            slide2 = max(0, int(1200 * (1.0 - (f - 300) / 15.0)))
            draw_pill_card(
                draw, "CLUE 2: King of the Jungle!", FONT_CLUE,
                cy=450,
                bg_color=(255, 240, 200),
                border_color=(255, 180, 0),
                text_color=(160, 70, 0),
                slide_offset=slide2
            )
            
        elif 420 <= f < 576:
            # Phase 4: 5-Second Countdown (frames 420 to 576)
            countdown_val = max(1, 5 - int((f - 420) / 31))
            draw_pill_card(
                draw, "COUNTDOWN TIME!", FONT_SUB,
                cy=340,
                bg_color=(255, 255, 255),
                border_color=(255, 60, 60),
                text_color=(220, 30, 30)
            )
            # Big bouncing countdown circular coin
            cd_bounce = int(12 * abs(math.sin(f * 0.3)))
            cd_colors = [
                (255, 60, 60), (255, 120, 0), (255, 200, 0),
                (0, 200, 255), (100, 240, 60)
            ]
            draw_circular_badge(
                draw, str(countdown_val), FONT_COUNTDOWN,
                cx=540, cy=960 - cd_bounce, radius=130,
                bg_color=cd_colors[countdown_val - 1],
                border_color=(255, 255, 255),
                border_w=14
            )
            
        elif 576 <= f < 795:
            # Phase 5: The Big Reveal
            draw_pill_card(
                draw, "IT'S A BABY LION!", FONT_TITLE,
                cy=360,
                bg_color=(255, 60, 100),
                border_color=(255, 255, 255),
                text_color=(255, 255, 255)
            )
            draw_pill_card(
                draw, "King of the Jungle!", FONT_SUB,
                cy=480,
                bg_color=(255, 255, 255),
                border_color=(255, 190, 0),
                text_color=(200, 100, 0)
            )
            
        else:
            # Phase 6: Outro & Call to Action
            draw_pill_card(
                draw, "Did you guess it right?", FONT_SUB,
                cy=350,
                bg_color=(255, 255, 255),
                border_color=(0, 200, 255),
                text_color=(0, 120, 200)
            )
            # Pulsing Subscribe Button
            sub_pulse = int(6 * math.sin(f * 0.2))
            draw_pill_card(
                draw, "SUBSCRIBE FOR DAILY GAMES!", FONT_CTA,
                cy=1620 + sub_pulse,
                bg_color=(255, 40, 60),
                border_color=(255, 255, 255),
                text_color=(255, 255, 255)
            )
            
        # Convert back to OpenCV BGR
        final_frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        out.write(final_frame)
        
        if f % 150 == 0:
            print(f"    Rendered {f}/{total_frames} frames ({f/FPS:.1f}s)...")
            
    out.release()
    print("[+] Video frames rendered successfully!")
    return raw_video_path

def compose_kids_audio(raw_video_path, output_video_path):
    """
    Combines video with voice clips, SFX, and upbeat BGM using FFmpeg.
    """
    print("[*] Assembling multi-track audio & SFX mix...")
    
    v_hook = TEMP_DIR / "p1_hook.mp3"
    v_clue1 = TEMP_DIR / "p2_clue1.mp3"
    v_clue2 = TEMP_DIR / "p3_clue2.mp3"
    v_countdown = TEMP_DIR / "p4_countdown.mp3"
    v_reveal = TEMP_DIR / "p5_reveal.mp3"
    v_outro = TEMP_DIR / "p6_outro.mp3"
    
    bgm = ASSETS_DIR / "cheerful_bgm.wav"
    pop_sfx = ASSETS_DIR / "pop.wav"
    tick_sfx = ASSETS_DIR / "tick.wav"
    fanfare_sfx = ASSETS_DIR / "fanfare.wav"
    ding_sfx = ASSETS_DIR / "ding.wav"
    roar_sfx = ASSETS_DIR / "lion_cub_roar.wav"
    
    # Audio Timeline mapping (in milliseconds):
    # p1_hook: 0ms
    # roar: 3200ms
    # p2_clue1: 6000ms | pop: 6000ms
    # p3_clue2: 10000ms | pop: 10000ms
    # p4_countdown: 14000ms
    # ticks: 14200, 15200, 16200, 17200, 18200
    # p5_reveal: 19200ms | fanfare: 19200ms
    # p6_outro: 26500ms | ding: 26800ms
    
    filter_complex = (
        "[1:a]volume=1.35[v1];"
        "[2:a]adelay=6000|6000,volume=1.35[v2];"
        "[3:a]adelay=10000|10000,volume=1.35[v3];"
        "[4:a]adelay=14000|14000,volume=1.35[v4];"
        "[5:a]adelay=19200|19200,volume=1.40[v5];"
        "[6:a]adelay=26500|26500,volume=1.35[v6];"
        
        "[7:a]volume=0.22,afade=t=out:st=32.0:d=2.5[bgm_track];"
        
        "[8:a]adelay=3200|3200,volume=0.75[roar];"
        "[9:a]adelay=6000|6000,volume=0.6[pop1];"
        "[10:a]adelay=10000|10000,volume=0.6[pop2];"
        "[11:a]adelay=14200|14200,volume=0.6[t1];"
        "[12:a]adelay=15200|15200,volume=0.6[t2];"
        "[13:a]adelay=16200|16200,volume=0.6[t3];"
        "[14:a]adelay=17200|17200,volume=0.6[t4];"
        "[15:a]adelay=18200|18200,volume=0.6[t5];"
        "[16:a]adelay=19200|19200,volume=0.85[fanfare];"
        "[17:a]adelay=26800|26800,volume=0.5[ding];"
        
        "[v1][v2][v3][v4][v5][v6][bgm_track][roar][pop1][pop2][t1][t2][t3][t4][t5][fanfare][ding]"
        "amix=inputs=17:duration=first:dropout_transition=2[aout]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_video_path),
        "-i", str(v_hook),
        "-i", str(v_clue1),
        "-i", str(v_clue2),
        "-i", str(v_countdown),
        "-i", str(v_reveal),
        "-i", str(v_outro),
        "-i", str(bgm),
        "-i", str(roar_sfx),
        "-i", str(pop_sfx),
        "-i", str(pop_sfx),
        "-i", str(tick_sfx),
        "-i", str(tick_sfx),
        "-i", str(tick_sfx),
        "-i", str(tick_sfx),
        "-i", str(tick_sfx),
        "-i", str(fanfare_sfx),
        "-i", str(ding_sfx),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "34.6",
        "-movflags", "+faststart",
        str(output_video_path)
    ]
    
    subprocess.run(cmd, check=True)
    print(f"[SUCCESS] Final Kids Video created: {output_video_path}")

if __name__ == "__main__":
    raw_path = render_kids_video()
    final_path = OUTPUT_DIR / "kids_mystery_lion_demo.mp4"
    compose_kids_audio(raw_path, final_path)
