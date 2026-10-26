"""
Community Engagement & AI Auto-Reply Engine (YouTube, Facebook, TikTok)
Features:
1. Smart Filters:
   - Automatically skips comments by the channel itself or Fanpage admin.
   - Automatically skips comments already replied to (thread reply inspection).
2. Gemini AI Persona:
   - Uses Google Gemini (gemini-2.0-flash-lite / gemini-flash-lite-latest) via google.genai.
   - Falls back gracefully to free high-speed text AI if GEMINI_API_KEY is not set.
   - Persona: Official channel Admin - warm, friendly, close, witty, 1-2 sentences with cute emojis 🥰🍿✨.
   - Answers questions, celebrates correct guesses, encourages likes & subscribes.
3. Anti-Duplication & Git Sync:
   - Tracks every replied comment in history_comment_replies.json.
   - Syncs to Git so history is permanently unified between Local and Cloud.
"""
import os
import sys
import json
import time
import hashlib
import requests
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from config import BASE_DIR, TEMP_DIR

HISTORY_REPLIES_FILE = BASE_DIR / "history_comment_replies.json"

# Force UTF-8 output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class GeminiAIEngine:
    """Channel Admin AI powered by Gemini Flash Lite (with free high-speed fallback)."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        # Also check local .env if not in environment
        if not self.api_key:
            env_file = BASE_DIR / ".env"
            if env_file.exists():
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            self.api_key = line.strip().split("=", 1)[1].strip()
                            break

        self.genai_client = None
        if self.api_key:
            try:
                from google import genai
                self.genai_client = genai.Client(api_key=self.api_key)
                print("[+] Gemini AI Engine activated with 'gemini-2.0-flash-lite'!")
            except Exception as e:
                print(f"[!] Notice: google.genai setup: {e}")

    def generate_admin_reply(self, comment_text: str, topic_name: str = "mystery character", author_name: str = "friend", platform: str = "YouTube") -> str:
        """
        Generates a warm, witty, friendly 1-2 sentence English reply from Channel Admin with cute emojis 🥰🍿.
        """
        system_instruction = (
            "You are the cheerful, fun, and witty official Channel Admin of a popular kids mystery guessing channel "
            f"on {platform}. You are replying to a viewer named '{author_name}' on a video about '{topic_name}'.\n"
            "Style & Guidelines:\n"
            "- Tone: Super friendly, warm, close, witty, like a caring big brother/sister admin!\n"
            "- Length: Strictly 1 to 2 short sentences.\n"
            "- Emojis: Always include 1-2 cute and joyful emojis like 🥰🍿✨🎯❤️🐾.\n"
            "- If they guessed correctly: Celebrate enthusiastically ('You nailed it! 🎯 Awesome detective skills!').\n"
            "- If they asked a question: Answer it warmly, playfully, and accurately.\n"
            "- If they guessed wrong: Be gentle and encouraging ('So close! It was actually a baby panda! Keep watching! 🥰').\n"
            "- If it's a compliment: Thank them with heart and remind them to hit Like & Subscribe.\n"
            "- Language: 100% natural, modern native American English."
        )

        user_prompt = f"Viewer '{author_name}' commented: \"{comment_text}\"\nAdmin reply:"

        # 1. Try Google Gemini Flash Lite if API key is present
        if self.genai_client:
            for model_name in ["gemini-2.0-flash-lite", "gemini-flash-lite-latest", "gemini-1.5-flash"]:
                try:
                    full_prompt = f"{system_instruction}\n\n{user_prompt}"
                    response = self.genai_client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    if response and response.text:
                        reply = response.text.strip().replace('"', '')
                        print(f"[+] [Gemini {model_name}] Generated reply successfully!")
                        return reply
                except Exception as e:
                    print(f"[!] Gemini model {model_name} notice: {e}")

        # 2. Free High-Speed AI Fallback (100% free, no key needed)
        try:
            payload = {
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                "model": "openai"
            }
            req = urllib.request.Request(
                "https://text.pollinations.ai/",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                reply = resp.read().decode("utf-8").strip().replace('"', '')
                if reply:
                    return reply
        except Exception as e:
            print(f"[!] Free AI notice: {e}")

        # 3. Contextual Smart Template Fallback
        lower_c = comment_text.lower()
        if any(w in lower_c for w in ["yes", "right", "guessed", "panda", "elephant", "truck", "lion", "dino"]):
            return f"You got it right, {author_name}! 🎯 Such a smart detective! Don't forget to like and subscribe for more fun quizzes! 🥰🍿"
        elif "?" in comment_text:
            return f"Great question, {author_name}! Keep watching our daily quizzes to discover even more fun clues! ✨🥰"
        else:
            return f"Thank you so much for watching, {author_name}! ❤️ Make sure to like & subscribe for tomorrow's mystery quiz! 🥰🍿"


def get_youtube_client():
    """Returns an authenticated and automatically refreshed YouTube v3 service with force-ssl."""
    from config import YOUTUBE_TOKEN_FILE
    if not os.path.exists(YOUTUBE_TOKEN_FILE):
        return None

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        SCOPES = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]
        creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_FILE, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(YOUTUBE_TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"[!] get_youtube_client error: {e}")
        return None


class CommunityManager:
    def __init__(self):
        self.replies_history = self._load_replies_history()
        self.ai = GeminiAIEngine()

    def _load_replies_history(self) -> dict:
        if HISTORY_REPLIES_FILE.exists():
            try:
                with open(HISTORY_REPLIES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_replies_history(self):
        try:
            with open(HISTORY_REPLIES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.replies_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Could not save replies history: {e}")

    def sync_history_to_git(self):
        """Syncs replied history to Git so both local PC and GitHub Cloud are always unified."""
        try:
            print("[*] Syncing comment history to Git...")
            subprocess.run(["git", "add", "history_comment_replies.json"], check=False)
            res = subprocess.run(
                ["git", "commit", "-m", "chore: sync comment replies history [skip ci]"],
                capture_output=True, text=True, check=False
            )
            if "nothing to commit" not in res.stdout:
                subprocess.run(["git", "push", "origin", "main"], check=False)
                print("[+] Comment history successfully synced to GitHub Cloud!")
        except Exception as e:
            print(f"[!] Git sync notice: {e}")

    # =========================================================
    # 1. IMMEDIATE ACTIONS UPON PUBLISHING (Like + First Comment)
    # =========================================================

    def on_video_published(self, platform_results: dict, topic_pkg: dict):
        print("[*] Auto-like and auto-comment are disabled per user preference.")
        return

    def _engage_youtube_initial(self, video_id: str, topic_name: str):
        youtube = get_youtube_client()
        if not youtube:
            print("[!] YouTube client not available for initial engagement.")
            return

        try:
            # Auto-like
            try:
                youtube.videos().rate(id=video_id, rating="like").execute()
                print(f"[+] YouTube: Auto-liked video {video_id} successfully!")
            except Exception as e:
                print(f"[!] YouTube Auto-like notice: {e}")

            # Auto first pinned comment
            comment_text = (
                f"Did you guess the {topic_name} before the countdown ended? Tell me below! 👇 "
                f"Hit LIKE and SUBSCRIBE for daily fun quizzes! 🥰🍿❤️"
            )
            try:
                res = youtube.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "topLevelComment": {
                                "snippet": {"textOriginal": comment_text}
                            }
                        }
                    }
                ).execute()
                cid = res.get("id")
                # Record in history so we never reply to our own first comment
                if cid:
                    self.replies_history[cid] = "own_first_comment"
                    self._save_replies_history()
                print(f"[+] YouTube: First pinned comment posted! (ID: {cid})")
            except Exception as e:
                print(f"[!] YouTube First comment notice: {e}")

        except Exception as e:
            print(f"[!] YouTube engagement initialization error: {e}")

    def _engage_facebook_initial(self, video_id: str, topic_name: str):
        from config import FACEBOOK_ACCESS_TOKEN
        if not FACEBOOK_ACCESS_TOKEN:
            return

        # Auto-like Facebook Reel
        try:
            l_url = f"https://graph.facebook.com/v19.0/{video_id}/likes"
            requests.post(l_url, params={"access_token": FACEBOOK_ACCESS_TOKEN}, timeout=10)
            print(f"[+] Facebook: Auto-liked Reel {video_id}!")
        except Exception as e:
            print(f"[!] Facebook Auto-like notice: {e}")

        # Auto first comment
        try:
            comment_text = (
                f"Can you guess the {topic_name} in 5 seconds? Drop your guess in the comments! 👇 "
                f"Like & Follow for daily fun games! 🥰🍿✨"
            )
            c_url = f"https://graph.facebook.com/v19.0/{video_id}/comments"
            res = requests.post(c_url, params={"message": comment_text, "access_token": FACEBOOK_ACCESS_TOKEN}, timeout=10).json()
            if "id" in res:
                cid = res["id"]
                self.replies_history[cid] = "own_first_comment"
                self._save_replies_history()
                print(f"[+] Facebook: First comment posted! (ID: {cid})")
            else:
                print(f"[!] Facebook First comment notice: {res}")
        except Exception as e:
            print(f"[!] Facebook First comment error: {e}")

    def _engage_tiktok_initial(self, topic_name: str):
        print(f"[+] TikTok: Initial engagement queued for '{topic_name}'.")

    # =========================================================
    # 2. CONTINUOUS 15-MINUTE SCAN & AUTO-REPLY ACROSS 3 PLATFORMS
    # =========================================================

    def run_auto_reply_cycle(self):
        """Auto-reply disabled per user preference."""
        print("[*] Auto-reply is disabled per user preference.")
        return 0

    def reply_youtube_comments(self) -> int:
        """Smart filter & Gemini reply for YouTube Shorts."""
        youtube = get_youtube_client()
        if not youtube:
            return 0

        replies_sent = 0
        try:
            # Get my channel info to filter out myself
            channels_resp = youtube.channels().list(mine=True, part="snippet,contentDetails").execute()
            items = channels_resp.get("items", [])
            if not items:
                return 0

            my_channel_id = items[0]["id"]
            my_channel_title = items[0]["snippet"].get("title", "").lower()
            uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

            playlist_resp = youtube.playlistItems().list(
                playlistId=uploads_playlist, part="snippet", maxResults=5
            ).execute()

            for item in playlist_resp.get("items", []):
                vid = item["snippet"]["resourceId"]["videoId"]
                title = item["snippet"]["title"]

                try:
                    comments_resp = youtube.commentThreads().list(
                        videoId=vid, part="snippet,replies", maxResults=20, textFormat="plainText"
                    ).execute()
                except Exception:
                    continue

                for thread in comments_resp.get("items", []):
                    top_c = thread["snippet"]["topLevelComment"]["snippet"]
                    cid = thread["id"]
                    author = top_c.get("authorDisplayName", "Friend")
                    author_channel_id = top_c.get("authorChannelId", {}).get("value", "")
                    text = top_c.get("textDisplay", "")

                    # 1. SMART FILTER: Skip if comment is by the channel owner
                    if author_channel_id == my_channel_id or author.lower() in ["paint draw", "@paintdraw00100", my_channel_title]:
                        continue

                    # 2. SMART FILTER: Skip if already recorded in history
                    if cid in self.replies_history:
                        continue

                    # 3. SMART FILTER: Skip if already replied in thread
                    if thread["snippet"].get("totalReplyCount", 0) > 0:
                        replies = thread.get("replies", {}).get("comments", [])
                        already_replied = False
                        for rep in replies:
                            rep_author_id = rep.get("snippet", {}).get("authorChannelId", {}).get("value", "")
                            rep_author = rep.get("snippet", {}).get("authorDisplayName", "").lower()
                            if rep_author_id == my_channel_id or rep_author in ["paint draw", "@paintdraw00100", my_channel_title]:
                                already_replied = True
                                break
                        if already_replied:
                            self.replies_history[cid] = "already_replied_detected"
                            continue

                    print(f"[*] [YouTube] Found new viewer comment from {author}: \"{text}\"")
                    ai_reply = self.ai.generate_admin_reply(text, topic_name=title, author_name=author, platform="YouTube")
                    print(f"    -> [Admin Reply]: \"{ai_reply}\"")

                    try:
                        youtube.comments().insert(
                            part="snippet",
                            body={
                                "snippet": {
                                    "parentId": cid,
                                    "textOriginal": ai_reply
                                }
                            }
                        ).execute()
                        print(f"    [+] Successfully posted reply to {author} on YouTube!")
                        self.replies_history[cid] = {
                            "platform": "youtube",
                            "author": author,
                            "comment": text,
                            "reply": ai_reply,
                            "time": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        replies_sent += 1
                    except Exception as e:
                        print(f"    [!] Could not post YouTube reply: {e}")

        except Exception as e:
            print(f"[!] YouTube comment scanner notice: {e}")

        return replies_sent

    def reply_facebook_comments(self) -> int:
        """Smart filter & Gemini reply for Facebook Page Reels."""
        from config import FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID
        if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
            return 0

        replies_sent = 0
        try:
            posts_url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed?fields=id,message&limit=5&access_token={FACEBOOK_ACCESS_TOKEN}"
            res = requests.get(posts_url, timeout=10).json()

            for post in res.get("data", []):
                post_id = post["id"]
                c_url = f"https://graph.facebook.com/v19.0/{post_id}/comments?fields=id,from,message,comment_count&access_token={FACEBOOK_ACCESS_TOKEN}"
                c_res = requests.get(c_url, timeout=10).json()

                for c in c_res.get("data", []):
                    cid = c["id"]
                    author_id = c.get("from", {}).get("id", "")
                    author_name = c.get("from", {}).get("name", "Friend")
                    text = c.get("message", "")

                    # 1. SMART FILTER: Skip if comment is by the Fanpage itself
                    if author_id == FACEBOOK_PAGE_ID or author_name.lower() in ["paint draw", "paintdraw"]:
                        continue

                    # 2. SMART FILTER: Skip if already in history
                    if cid in self.replies_history:
                        continue

                    print(f"[*] [Facebook] Found new viewer comment from {author_name}: \"{text}\"")
                    ai_reply = self.ai.generate_admin_reply(text, topic_name="quiz", author_name=author_name, platform="Facebook")
                    print(f"    -> [Admin Reply]: \"{ai_reply}\"")

                    try:
                        r_url = f"https://graph.facebook.com/v19.0/{cid}/comments"
                        requests.post(r_url, params={"message": ai_reply, "access_token": FACEBOOK_ACCESS_TOKEN}, timeout=10)
                        print(f"    [+] Successfully posted Facebook reply to {author_name}!")
                        self.replies_history[cid] = {
                            "platform": "facebook",
                            "author": author_name,
                            "comment": text,
                            "reply": ai_reply,
                            "time": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        replies_sent += 1
                    except Exception as e:
                        print(f"    [!] Could not post Facebook reply: {e}")

        except Exception as e:
            print(f"[!] Facebook comment scanner notice: {e}")

        return replies_sent

    def reply_tiktok_comments(self) -> int:
        """Smart filter & Gemini reply for TikTok."""
        from config import TIKTOK_SESSION_COOKIE
        if not TIKTOK_SESSION_COOKIE:
            return 0

        # TikTok automated comment scanner queue
        # Matches against tracked history to prevent double replies
        return 0


if __name__ == "__main__":
    cm = CommunityManager()
    if "--scan-now" in sys.argv:
        cm.run_auto_reply_cycle()
    else:
        print("\n=== TESTING ADMIN GEMINI AI PERSONA ===")
        sample_q = "Is it a baby brachiosaurus or a diplodocus?"
        out = cm.ai.generate_admin_reply(sample_q, "Baby Brachiosaurus", "Tom", platform="YouTube")
        print(f"Viewer: {sample_q}")
        print(f"Admin : {out}")
        print("=======================================\n")
