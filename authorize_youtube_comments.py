"""
One-click script to upgrade YouTube permissions.
Adds 'https://www.googleapis.com/auth/youtube.force-ssl' scope to youtube_token.json.
This enables:
1. Auto-Like videos upon publishing
2. Auto-Post first pinned comment
3. Auto-Reply to viewer comments 24/7 with Free AI
"""
import os
import sys
import json
import base64
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from config import BASE_DIR, YOUTUBE_CLIENT_SECRET_FILE, YOUTUBE_TOKEN_FILE

# Full scope for Upload, Like, Comment, and Reply
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def main():
    print("=" * 60)
    print("🔑 UPGRADE YOUTUBE PERMISSIONS (FOR LIKE, COMMENT & AUTO-REPLY)")
    print("=" * 60)

    if not os.path.exists(YOUTUBE_CLIENT_SECRET_FILE):
        print(f"[!] client_secret.json not found at {YOUTUBE_CLIENT_SECRET_FILE}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRET_FILE, SCOPES)
    print("\n[*] Opening browser for 1-click Google authorization...")
    print("[*] Please log in and click 'Allow' to grant YouTube comment & like permissions.\n")

    creds = flow.run_local_server(port=0)

    with open(YOUTUBE_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print("\n[+] SUCCESS! youtube_token.json updated with full Like & Comment permissions!")

    # Auto-sync to GitHub Secrets if sync script is present
    try:
        from sync_github_secrets import set_secret, public_key_b64
        token_b64 = base64.b64encode(Path(YOUTUBE_TOKEN_FILE).read_bytes()).decode("utf-8")
        set_secret("YOUTUBE_TOKEN_BASE64", token_b64)
        print("[+] Synced new token directly to GitHub Cloud Secrets!")
    except Exception:
        pass

    print("=" * 60)

if __name__ == "__main__":
    main()
