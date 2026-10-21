"""
Account Connection Wizard & Cloud Secrets Generator
Interactive setup for:
1. YouTube Shorts (OAuth2 login & token generation)
2. Facebook Reels (Page ID & Access Token test & Permanent Token Exchanger)
3. TikTok (Session Cookie validator)
4. GitHub Actions Secrets Generator (for 100% Free Cloud 24/7)
"""
import sys
import os
import base64
import json
import requests
from pathlib import Path
from config import (
    BASE_DIR, YOUTUBE_CLIENT_SECRET_FILE, YOUTUBE_TOKEN_FILE,
    FACEBOOK_PAGE_ID, FACEBOOK_ACCESS_TOKEN, TIKTOK_SESSION_COOKIE
)

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def connect_youtube():
    print("\n--- 1. YOUTUBE SHORTS CONNECTION ---")
    secret_path = Path(YOUTUBE_CLIENT_SECRET_FILE)
    if not secret_path.exists():
        print("[!] File 'client_secret.json' not found in bot folder.")
        return False

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
        print("[*] Opening browser for Google login consent...")
        creds = flow.run_local_server(port=0)
        with open(YOUTUBE_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print(f"[+] YouTube connected successfully! Token saved to: {YOUTUBE_TOKEN_FILE}")
        return True
    except Exception as e:
        print(f"[!] YouTube connection failed: {e}")
        return False


def exchange_permanent_facebook_token(app_id, app_secret, user_short_token, target_page_name="Paint Draw"):
    """
    Exchanges a short-lived user token into a NEVER-EXPIRING Page Access Token.
    1. Exchange short-lived token for long-lived user token (60 days)
    2. Query GET /me/accounts with long-lived token to get Page Access Token (Never expires)
    """
    print("\n--- CONVERTING TO PERMANENT FACEBOOK PAGE TOKEN ---")
    try:
        # Step 1: Exchange for long-lived user token
        print("[*] Step 1: Exchanging for 60-day user token...")
        exchange_url = "https://graph.facebook.com/v19.0/oauth/access_token"
        p1 = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": user_short_token
        }
        r1 = requests.get(exchange_url, params=p1).json()
        long_user_token = r1.get("access_token")
        if not long_user_token:
            print(f"[!] Failed to get long-lived user token: {r1}")
            return None

        # Step 2: Get permanent page token
        print("[*] Step 2: Fetching Never-Expiring Page Token...")
        accounts_url = "https://graph.facebook.com/v19.0/me/accounts"
        r2 = requests.get(accounts_url, params={"access_token": long_user_token}).json()
        
        pages = r2.get("data", [])
        if not pages:
            print(f"[!] No pages found or error: {r2}")
            return None

        for p in pages:
            p_name = p.get("name", "")
            p_id = p.get("id", "")
            p_token = p.get("access_token", "")
            print(f"    -> Found Page: '{p_name}' (ID: {p_id})")
            if target_page_name.lower() in p_name.lower() or len(pages) == 1:
                print("\n[+] SUCCESS! Permanent Page Token generated:")
                print(f"    PAGE ID:            {p_id}")
                print(f"    PERMANENT TOKEN:    {p_token[:25]}... (Never expires)")
                return {"page_id": p_id, "access_token": p_token, "page_name": p_name}

        # If not matched specifically, return the first one
        first_p = pages[0]
        return {"page_id": first_p["id"], "access_token": first_p["access_token"], "page_name": first_p["name"]}

    except Exception as e:
        print(f"[!] Error exchanging permanent token: {e}")
        return None


def test_facebook(page_id, access_token):
    print("\n--- 2. FACEBOOK REELS TEST ---")
    url = f"https://graph.facebook.com/v19.0/{page_id}?fields=name,id&access_token={access_token}"
    try:
        res = requests.get(url).json()
        if "id" in res:
            print(f"[+] Facebook Page verified: '{res.get('name')}' (ID: {res.get('id')})")
            return True
        else:
            print(f"[!] Facebook verification error: {res}")
            return False
    except Exception as e:
        print(f"[!] Facebook test failed: {e}")
        return False


def test_tiktok(session_cookie):
    print("\n--- 3. TIKTOK SESSION TEST ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": f"sessionid={session_cookie};"
    }
    try:
        r = requests.get("https://www.tiktok.com/creator-center/upload", headers=headers, timeout=15)
        if "login" not in r.url.lower():
            print("[+] TikTok session cookie verified! Creator Studio accessible.")
            return True
        else:
            print("[!] TikTok cookie expired or invalid (redirected to login).")
            return False
    except Exception as e:
        print(f"[!] TikTok test error: {e}")
        return False


def generate_github_cloud_secrets():
    print("\n" + "=" * 60)
    print("      GITHUB ACTIONS CLOUD SECRETS (FOR 100% FREE CLOUD 24/7)")
    print("=" * 60)
    print("To run 24/7 in the cloud without keeping your PC on:")
    print("1. Push this project to your GitHub repository (recommended: Private).")
    print("2. In your repo: Go to 'Settings' -> 'Secrets and variables' -> 'Actions'.")
    print("3. Click 'New repository secret' and add the following 5 secrets:\n")

    if os.path.exists(YOUTUBE_CLIENT_SECRET_FILE):
        with open(YOUTUBE_CLIENT_SECRET_FILE, "rb") as f:
            b64_secret = base64.b64encode(f.read()).decode("utf-8")
        print("--- [SECRET 1/5] ---")
        print("Name:  YOUTUBE_CLIENT_SECRET_BASE64")
        print(f"Value: {b64_secret}\n")

    if os.path.exists(YOUTUBE_TOKEN_FILE):
        with open(YOUTUBE_TOKEN_FILE, "rb") as f:
            b64_token = base64.b64encode(f.read()).decode("utf-8")
        print("--- [SECRET 2/5] ---")
        print("Name:  YOUTUBE_TOKEN_BASE64")
        print(f"Value: {b64_token}\n")

    print("--- [SECRET 3/5] ---")
    print("Name:  FB_PAGE_ID")
    print(f"Value: {FACEBOOK_PAGE_ID}\n")

    print("--- [SECRET 4/5] ---")
    print("Name:  FB_ACCESS_TOKEN")
    print(f"Value: {FACEBOOK_ACCESS_TOKEN}\n")

    print("--- [SECRET 5/5] ---")
    print("Name:  TIKTOK_SESSION_COOKIE")
    print(f"Value: {TIKTOK_SESSION_COOKIE}\n")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if "--youtube" in sys.argv:
            connect_youtube()
        elif "--cloud-secrets" in sys.argv:
            generate_github_cloud_secrets()
    else:
        generate_github_cloud_secrets()
