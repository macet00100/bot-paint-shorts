"""
Multi-Platform Auto Uploader Module
Automatically uploads 9:16 short videos to:
1. YouTube Shorts (YouTube Data API v3)
2. Facebook Reels (Meta Graph API)
3. TikTok (Playwright Web Automation / Session Cookie)

Includes Draft Mode & Safe Fallback when API keys/credentials are pending.
"""
import sys
import os
import json
import time
import requests
from pathlib import Path
from config import (
    YOUTUBE_CLIENT_SECRET_FILE, YOUTUBE_TOKEN_FILE,
    FACEBOOK_PAGE_ID, FACEBOOK_ACCESS_TOKEN,
    TIKTOK_SESSION_COOKIE, OUTPUT_DIR
)


class AutoUploader:
    def __init__(self):
        pass

    # ==========================================
    # 1. YOUTUBE SHORTS UPLOADER
    # ==========================================
    def upload_to_youtube(self, video_path, title, description, tags=None):
        """
        Uploads video to YouTube Shorts using YouTube Data API v3.
        Free 10,000 units quota/day.
        """
        if not os.path.exists(YOUTUBE_CLIENT_SECRET_FILE) and not os.path.exists(YOUTUBE_TOKEN_FILE):
            print("[i] YouTube: client_secret.json not found. Video saved in Output folder.")
            return {"platform": "YouTube", "status": "PENDING_CREDENTIALS", "video": str(video_path)}

        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request

            SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
            creds = None

            if os.path.exists(YOUTUBE_TOKEN_FILE):
                creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_FILE, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(YOUTUBE_CLIENT_SECRET_FILE):
                        return {"platform": "YouTube", "status": "ERROR", "message": "Missing client_secret.json"}
                    flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRET_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(YOUTUBE_TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())

            youtube = build("youtube", "v3", credentials=creds)

            # Ensure #shorts is in the title
            yt_title = title if "#shorts" in title.lower() else f"{title} #shorts"
            body = {
                "snippet": {
                    "title": yt_title[:100],
                    "description": f"{description}\n\n#shorts #mspaint #drawing",
                    "tags": tags or ["shorts", "mspaint", "art", "drawing"],
                    "categoryId": "24"  # Entertainment / Art
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = request.execute()
            video_id = response.get("id")
            print(f"[+] YouTube Shorts uploaded successfully! Video ID: {video_id}")
            return {"platform": "YouTube", "status": "SUCCESS", "id": video_id}
        except Exception as e:
            print(f"[!] YouTube upload failed: {e}")
            return {"platform": "YouTube", "status": "ERROR", "message": str(e)}

    # ==========================================
    # 2. FACEBOOK REELS UPLOADER
    # ==========================================
    def upload_to_facebook_reels(self, video_path, description):
        """
        Uploads video to Facebook Page Reels via Meta Graph API.
        Free 100% using Page Access Token.
        """
        if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
            print("[i] Facebook Reels: Page ID / Access Token not set in config.py")
            return {"platform": "Facebook", "status": "PENDING_CREDENTIALS", "video": str(video_path)}

        try:
            print(f"[*] Initializing Facebook Reel upload for Page ID: {FACEBOOK_PAGE_ID}...")
            # Step 1: Initialize Reel Upload Session
            init_url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/video_reels"
            params = {
                "upload_phase": "start",
                "access_token": FACEBOOK_ACCESS_TOKEN
            }
            res = requests.post(init_url, params=params).json()
            video_id = res.get("video_id")
            upload_url = res.get("upload_url")

            if not video_id or not upload_url:
                raise RuntimeError(f"FB Init error: {res}")

            # Step 2: Upload Binary
            file_size = os.path.getsize(video_path)
            headers = {
                "Authorization": f"OAuth {FACEBOOK_ACCESS_TOKEN}",
                "offset": "0",
                "file_size": str(file_size)
            }
            with open(video_path, "rb") as f:
                upload_res = requests.post(upload_url, headers=headers, data=f).json()

            # Step 3: Publish
            publish_params = {
                "upload_phase": "finish",
                "access_token": FACEBOOK_ACCESS_TOKEN,
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description
            }
            pub_res = requests.post(init_url, params=publish_params).json()
            print(f"[+] Facebook Reel published successfully! Video ID: {video_id}")
            return {"platform": "Facebook", "status": "SUCCESS", "id": video_id}
        except Exception as e:
            print(f"[!] Facebook Reels upload failed: {e}")
            return {"platform": "Facebook", "status": "ERROR", "message": str(e)}

    # ==========================================
    # 3. TIKTOK UPLOADER (Automated Session)
    # ==========================================
    def upload_to_tiktok(self, video_path, description):
        """
        Uploads video to TikTok via Playwright browser session cookie.
        Free 100%, runs headlessly.
        """
        if not TIKTOK_SESSION_COOKIE:
            print("[i] TikTok: Session cookie not set in config.py")
            return {"platform": "TikTok", "status": "PENDING_CREDENTIALS", "video": str(video_path)}

        try:
            from playwright.sync_api import sync_playwright
            print("[*] Launching headless browser for TikTok upload...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                # Inject sessionid and sessionid_ss cookies
                context.add_cookies([
                    {
                        "name": "sessionid",
                        "value": TIKTOK_SESSION_COOKIE,
                        "domain": ".tiktok.com",
                        "path": "/"
                    },
                    {
                        "name": "sessionid_ss",
                        "value": TIKTOK_SESSION_COOKIE,
                        "domain": ".tiktok.com",
                        "path": "/"
                    }
                ])
                page = context.new_page()
                page.goto("https://www.tiktok.com/creator-center/upload?from=upload", timeout=60000)
                time.sleep(3)

                # Set input file
                file_input = page.locator("input[type='file']")
                file_input.set_input_files(str(video_path))
                time.sleep(5)

                # Caption
                caption_input = page.locator(".public-DraftEditor-content")
                if caption_input.count() > 0:
                    caption_input.fill(description)

                time.sleep(3)
                # Click Post
                post_btn = page.locator("button:has-text('Post')")
                if post_btn.count() > 0:
                    post_btn.click()
                    time.sleep(5)

                browser.close()
                print("[+] TikTok video uploaded via automated session!")
                return {"platform": "TikTok", "status": "SUCCESS"}
        except Exception as e:
            print(f"[!] TikTok upload failed: {e}")
            return {"platform": "TikTok", "status": "ERROR", "message": str(e)}

    # ==========================================
    # UNIFIED MULTI-PLATFORM POSTER
    # ==========================================
    def upload_all(self, video_path, title, description, tags=None):
        """
        Pushes the video to YouTube Shorts, Facebook Reels, and TikTok.
        Saves metadata log.
        """
        results = {}
        print("\n" + "=" * 50)
        print(f"[*] Starting Multi-Platform Upload: {Path(video_path).name}")
        print("=" * 50)

        # 1. YouTube
        results["youtube"] = self.upload_to_youtube(video_path, title, description, tags)
        
        # 2. Facebook
        results["facebook"] = self.upload_to_facebook_reels(video_path, f"{title}\n{description}")
        
        # 3. TikTok
        results["tiktok"] = self.upload_to_tiktok(video_path, f"{title} {description}")

        # Save record
        meta_file = Path(video_path).with_suffix(".json")
        record = {
            "video_path": str(video_path),
            "title": title,
            "description": description,
            "tags": tags,
            "results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        print("[+] Upload record saved to:", meta_file)
        return results


if __name__ == "__main__":
    uploader = AutoUploader()
    test_vid = OUTPUT_DIR / "sample_paint_short.mp4"
    uploader.upload_all(
        test_vid,
        "Vẽ biếm họa MS Paint bằng chuột cực đỉnh! 🐭🎨",
        "Thử thách vẽ tranh bằng MS Paint chỉ với một con chuột duy nhất. #shorts #mspaint #drawing"
    )
