"""
Helper script to print GitHub Secrets for Cloud 24/7 automation.
Run this script to easily copy the credentials into GitHub:
Repo -> Settings -> Secrets and variables -> Actions -> New repository secret
"""
import os
import sys
import base64
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent

print("\n" + "=" * 60)
print("🔑 GITHUB ACTIONS SECRETS (FOR 24/7 RUNNING WHILE PC IS OFF)")
print("Add these to: https://github.com/macet00100/bot-paint-shorts/settings/secrets/actions")
print("=" * 60 + "\n")

# 1. YouTube Client Secret
cs_file = BASE_DIR / "client_secret.json"
if cs_file.exists():
    cs_b64 = base64.b64encode(cs_file.read_bytes()).decode("utf-8")
    print("--- 1. YOUTUBE_CLIENT_SECRET_BASE64 ---")
    print(cs_b64)
    print()

# 2. YouTube Token
token_file = BASE_DIR / "youtube_token.json"
if token_file.exists():
    token_b64 = base64.b64encode(token_file.read_bytes()).decode("utf-8")
    print("--- 2. YOUTUBE_TOKEN_BASE64 ---")
    print(token_b64)
    print()

# 3. Environment Variables from .env
env_file = BASE_DIR / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k in ["FB_PAGE_ID", "FB_ACCESS_TOKEN", "TIKTOK_SESSION_COOKIE"]:
                    print(f"--- {k} ---")
                    print(v)
                    print()

print("=" * 60)
print("Done! Once pasted into GitHub Secrets, GitHub will auto-upload 24/7 forever!")
print("=" * 60 + "\n")
