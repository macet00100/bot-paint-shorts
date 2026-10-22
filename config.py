"""
Configuration file for Automated MS Paint Video Bot (100% English - US/Global View)
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"

# Load local .env if present (git-ignored, safe for public repos)
env_file = BASE_DIR / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass

for directory in [ASSETS_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Video Specifications (9:16 for Shorts / TikTok / Reels - matching POV reference)
VIDEO_WIDTH = 720
VIDEO_HEIGHT = 1280
FPS = 24
TARGET_DURATION = 35  # seconds (< 60s)

# Timeline breakdown (in seconds, total = 30s)
DURATION_HOOK = 3.0       # 0s - 3s: Finished art preview + hook
DURATION_SKETCH = 11.0    # 3s - 14s: Pencil line art drawing in Paint
DURATION_COLOR = 10.0     # 14s - 24s: Palette picking & coloring in Paint
DURATION_REVEAL = 3.0     # 24s - 27s: Final 2K masterpiece zoom
DURATION_CTA = 3.0        # 27s - 30s: Like & Subscribe cursor click

# Voiceover Settings (100% English for US / International views)
# Native American English voices:
# "en-US-ChristopherNeural" (Energetic, friendly male - YouTuber style)
# "en-US-JennyNeural" (Vibrant, engaging female)
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-ChristopherNeural")
TTS_FALLBACK_VOICE = "en-US-GuyNeural"
TTS_RATE = "+10%"  # fast-paced energy for US Shorts

# Trend Research Settings (Target US & Global viral topics)
TREND_REGIONS = ["US"]
# 4 Golden slots for US/International audiences (converted to Vietnam Time UTC+7):
# 1. 03:15 VN = 04:15 PM EDT (US Afternoon Rush / Kids after-school)
# 2. 07:15 VN = 08:15 PM EDT (US Prime Time Evening / Peak family scrolling)
# 3. 19:15 VN = 08:15 AM EDT (US Morning commute & Europe afternoon)
# 4. 23:15 VN = 12:15 PM EDT (US Lunch break peak & Europe evening)
SCHEDULE_TIMES = ["03:15", "07:15", "19:15", "23:15"]  # Vietnam Time (UTC+7)

# AI Image Settings (100% Free)
IMAGE_PROVIDER = "pollinations"
IMAGE_MODEL = "turbo"
POLLINATIONS_WIDTH = 1080
POLLINATIONS_HEIGHT = 1440

# Platform Upload Credentials (read from environment or .env, safe for public git)
YOUTUBE_CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", str(BASE_DIR / "client_secret.json"))
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", str(BASE_DIR / "youtube_token.json"))

FACEBOOK_PAGE_ID = os.getenv("FB_PAGE_ID", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")

TIKTOK_SESSION_COOKIE = os.getenv("TIKTOK_SESSION_COOKIE", "")
