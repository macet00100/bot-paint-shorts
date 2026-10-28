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

            SCOPES = [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
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
            
            # Clean description without duplicate #shorts tags
            desc_clean = description.strip()
            if "#shorts" not in desc_clean.lower():
                desc_clean = f"{desc_clean}\n\n#shorts #kids #quiz #animation"

            body = {
                "snippet": {
                    "title": yt_title[:100],
                    "description": desc_clean,
                    "tags": tags or ["shorts", "kids quiz", "guessing game", "animation", "family friendly"],
                    "categoryId": "24"  # Entertainment / Family Animation
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
            print("[*] Launching headless browser for TikTok Studio upload...")
            with sync_playwright() as p:
                launch_kwargs = {
                    "headless": True,
                    "args": [
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-web-security"
                    ]
                }
                edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                if os.path.exists(edge_path):
                    launch_kwargs["executable_path"] = edge_path

                browser = p.chromium.launch(**launch_kwargs)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080}
                )
                # Stealth: hide webdriver flag
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                # Inject sessionid and sessionid_ss cookies
                context.add_cookies([
                    {
                        "name": "sessionid",
                        "value": TIKTOK_SESSION_COOKIE,
                        "domain": ".tiktok.com",
                        "path": "/",
                        "secure": True,
                        "httpOnly": True
                    },
                    {
                        "name": "sessionid_ss",
                        "value": TIKTOK_SESSION_COOKIE,
                        "domain": ".tiktok.com",
                        "path": "/",
                        "secure": True,
                        "httpOnly": True
                    }
                ])
                page = context.new_page()
                studio_url = "https://www.tiktok.com/tiktokstudio/upload?from=upload"
                print(f"[*] Navigating to {studio_url}...")
                page.goto(studio_url, timeout=60000)
                time.sleep(6)

                print(f"[*] TikTok page loaded. Current URL: {page.url} | Title: {page.title()}")

                # 1. Wait for attached file input (hidden by design in modern CSS)
                print("[*] Waiting for upload file input...")
                try:
                    page.wait_for_selector("input[type='file']", state="attached", timeout=45000)
                except Exception as te:
                    print(f"[!] Timeout waiting for file input on TikTok. Current URL: {page.url}")
                    try:
                        page.screenshot(path="tiktok_upload_error.png")
                        print("[+] Saved debug screenshot to tiktok_upload_error.png")
                    except Exception:
                        pass
                    raise te

                page.set_input_files("input[type='file']", str(video_path))
                print("[+] Video file attached to TikTok Studio. Waiting for video processing...")
                time.sleep(15)

                # 2. Dismiss Joyride onboarding tour / modal
                dismiss = page.locator('button:has-text("Đã hiểu"), button:has-text("Got it"), button[aria-label="Skip"], button[aria-label="Close"]')
                if dismiss.count() > 0:
                    try:
                        dismiss.first.click()
                        print("[+] Joyride onboarding tour dismissed.")
                        time.sleep(2)
                    except Exception:
                        pass

                # 3. Fill Caption
                caption_input = page.locator(".public-DraftEditor-content, div[contenteditable='true']")
                if caption_input.count() > 0:
                    try:
                        caption_input.first.fill(description)
                        print("[+] Video caption added.")
                    except Exception as ce:
                        print(f"[-] Could not fill caption: {ce}")

                time.sleep(3)

                # 4. Click Post button
                post_btn = page.locator('button[data-e2e="post_video_button"], button:has-text("Post"), button:has-text("Đăng")')
                if post_btn.count() > 0:
                    try:
                        post_btn.first.scroll_into_view_if_needed()
                        post_btn.first.click()
                        print("[+] Clicked Post button. Monitoring confirmation dialog...")
                    except Exception as be:
                        print(f"[-] Error clicking post button: {be}")

                # 5. Handle confirmation dialog if prompted (e.g. "Post now" / "Đăng ngay")
                for _ in range(8):
                    time.sleep(2)
                    dialog_confirm = page.locator('button:has-text("Post now"), button:has-text("Đăng ngay"), button:has-text("Tiếp tục đăng")')
                    if dialog_confirm.count() > 0:
                        print("[+] Confirmed post dialog ('Post now')!")
                        dialog_confirm.first.click()
                        time.sleep(5)
                        break

                time.sleep(10)
                browser.close()
                print("[+] TikTok video uploaded via automated session!")
                return {"platform": "TikTok", "status": "SUCCESS"}
        except Exception as e:
            print(f"[!] TikTok upload failed: {e}")
            return {"platform": "TikTok", "status": "ERROR", "message": str(e)}

    # ==========================================
    # UNIFIED MULTI-PLATFORM POSTER
    # ==========================================
    def upload_all(self, video_path, title, description, tags=None, topic_pkg=None):
        """
        Pushes the video to YouTube Shorts, Facebook Reels, and TikTok.
        Saves metadata log.
        Triggers instant community engagement (Auto-Like & First Pinned Comment).
        """
        results = {}
        print("\n" + "=" * 50)
        print(f"[*] Starting Multi-Platform Upload: {Path(video_path).name}")
        print("=" * 50)

        # 1. YouTube
        results["youtube"] = self.upload_to_youtube(video_path, title, description, tags)
        
        # 2. Facebook
        results["facebook"] = self.upload_to_facebook_reels(video_path, f"{title}\n{description}")
        
        # 3. TikTok (Disabled - Focusing 100% on YouTube Shorts & Facebook Reels)
        # results["tiktok"] = self.upload_to_tiktok(video_path, f"{title} {description}")
        results["tiktok"] = {"platform": "TikTok", "status": "SKIPPED", "message": "Disabled per user preference"}

        # Auto-like and auto-comment disabled per user preference
        print("[*] Auto-like and auto-comment are disabled.")

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
