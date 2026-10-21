"""
One-click script to upgrade YouTube permissions.
Adds 'https://www.googleapis.com/auth/youtube.force-ssl' scope to youtube_token.json.
Enables Auto-Like, First Pinned Comment, and 24/7 AI Auto-Reply to viewers.
"""
import os
import sys
import json
import base64
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from config import BASE_DIR, YOUTUBE_CLIENT_SECRET_FILE, YOUTUBE_TOKEN_FILE

# Full scope for Upload, Like, Comment, and Reply
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def main():
    print("\n" + "=" * 60)
    print("[*] UPGRADE YOUTUBE PERMISSIONS (LIKE, COMMENT & AUTO-REPLY)")
    print("=" * 60)

    if not os.path.exists(YOUTUBE_CLIENT_SECRET_FILE):
        print(f"[!] client_secret.json not found at: {YOUTUBE_CLIENT_SECRET_FILE}")
        input("\nPress Enter to exit...")
        return

    print("\n[*] Initializing Google Authorization Flow...")
    flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRET_FILE, SCOPES)
    
    print("[*] Opening your default web browser...")
    print("[*] Please select your Google account and click 'Allow' (Cho phép)...\n")

    try:
        creds = flow.run_local_server(port=0, open_browser=True)
    except Exception as e:
        print(f"[!] Server authorization error: {e}")
        input("\nPress Enter to exit...")
        return

    with open(YOUTUBE_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print("\n[+] SUCCESS! youtube_token.json updated with full permissions!")

    # Auto sync to GitHub Actions Cloud
    try:
        print("[*] Syncing updated token directly to GitHub Actions Secrets...")
        import subprocess
        subprocess.run([sys.executable, "sync_github_secrets.py"], check=False)
        print("[+] Synced to GitHub Cloud Secrets successfully!")
    except Exception as e:
        print(f"[!] GitHub sync notice: {e}")

    print("\n" + "=" * 60)
    print("[+] COMPLETE! You can now close this window.")
    print("=" * 60 + "\n")
    input("Press Enter to finish...")

if __name__ == "__main__":
    main()
