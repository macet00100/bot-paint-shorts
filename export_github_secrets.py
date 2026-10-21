"""
GitHub Secrets Exporter Helper
Encodes local API tokens into Base64 format ready to paste into GitHub Secrets:
Settings -> Secrets and variables -> Actions -> New repository secret
"""
import os
import sys
import base64
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Force UTF-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def export_secrets():
    print("=" * 60)
    print("  GITHUB REPOSITORY SECRETS (FOR 24/7 CLOUD AUTOMATION)")
    print("=" * 60)
    print("Go to: https://github.com/macet00100/bot-paint-shorts/settings/secrets/actions")
    print("Click 'New repository secret' and add each of the following:\n")

    # 1. YOUTUBE_CLIENT_SECRET_BASE64
    cs_path = BASE_DIR / "client_secret.json"
    if cs_path.exists():
        with open(cs_path, "rb") as f:
            b64_cs = base64.b64encode(f.read()).decode("utf-8")
        print("SECRET 1:")
        print("Name:  YOUTUBE_CLIENT_SECRET_BASE64")
        print(f"Value: {b64_cs}\n")
    else:
        print("[!] client_secret.json not found locally.\n")

    # 2. YOUTUBE_TOKEN_BASE64
    yt_token_path = BASE_DIR / "youtube_token.json"
    if yt_token_path.exists():
        with open(yt_token_path, "rb") as f:
            b64_yt = base64.b64encode(f.read()).decode("utf-8")
        print("SECRET 2:")
        print("Name:  YOUTUBE_TOKEN_BASE64")
        print(f"Value: {b64_yt}\n")
    else:
        print("[!] youtube_token.json not found locally.\n")

    # Read .env for Facebook & TikTok
    env_vars = {}
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()

    # 3. FB_PAGE_ID
    fb_pid = env_vars.get("FB_PAGE_ID", os.getenv("FB_PAGE_ID", ""))
    print("SECRET 3:")
    print("Name:  FB_PAGE_ID")
    print(f"Value: {fb_pid}\n")

    # 4. FB_ACCESS_TOKEN
    fb_token = env_vars.get("FB_ACCESS_TOKEN", os.getenv("FB_ACCESS_TOKEN", ""))
    print("SECRET 4:")
    print("Name:  FB_ACCESS_TOKEN")
    print(f"Value: {fb_token}\n")

    # 5. TIKTOK_SESSION_COOKIE
    tt_cookie = env_vars.get("TIKTOK_SESSION_COOKIE", os.getenv("TIKTOK_SESSION_COOKIE", ""))
    print("SECRET 5:")
    print("Name:  TIKTOK_SESSION_COOKIE")
    print(f"Value: {tt_cookie}\n")

    print("=" * 60)
    print("Once these 5 secrets are added to GitHub, your bot will run")
    print("automatically 24/7 in GitHub's cloud without needing your computer on!")
    print("=" * 60)


if __name__ == "__main__":
    export_secrets()
