"""
Trend Research Module (100% English - US/Global Viral Topics)
Automatically scans US Google Trends & Global Entertainment News RSS,
picks the most entertaining topic, and generates English caricature concepts,
prompts, and scripts.
"""
import sys
import random
import re
import feedparser

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Negative keywords to avoid sensitive/tragic news
SENSITIVE_KEYWORDS = [
    "kill", "dead", "death", "murder", "accident", "shooting", "crash",
    "war", "attack", "terror", "arrested", "hospital", "died", "suicide"
]


class TrendResearcher:
    def __init__(self):
        pass

    def fetch_google_trends(self, geo="US"):
        """Fetch trending topics from US Google Trends RSS"""
        url = f"https://trends.google.com/trending/rss?geo={geo}"
        try:
            feed = feedparser.parse(url)
            trends = []
            for entry in feed.entries:
                trends.append({
                    "title": entry.title,
                    "description": entry.get("summary", ""),
                    "source": f"Google Trends {geo}"
                })
            return trends
        except Exception as e:
            print(f"[!] Error fetching US Google Trends: {e}")
            return []

    def fetch_google_news(self):
        """Fetch US Entertainment & Tech headlines"""
        url = "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-US&gl=US&ceid=US:en"
        try:
            feed = feedparser.parse(url)
            news = []
            for entry in feed.entries[:15]:
                clean_t = entry.title.split(" - ")[0].strip()
                news.append({
                    "title": clean_t,
                    "description": entry.get("summary", ""),
                    "source": "US Entertainment News"
                })
            return news
        except Exception as e:
            print(f"[!] Error fetching US News: {e}")
            return []

    def filter_safe_trends(self, items):
        """Filter out sensitive/tragic news"""
        filtered = []
        for item in items:
            title_lower = item["title"].lower()
            if any(k in title_lower for k in SENSITIVE_KEYWORDS):
                continue
            filtered.append(item)
        return filtered if filtered else items

    def pick_best_trend(self):
        """Select top viral trend"""
        trends_us = self.fetch_google_trends("US")
        news_us = self.fetch_google_news()
        all_items = trends_us + news_us
        safe_items = self.filter_safe_trends(all_items)

        if not safe_items:
            # Fallback viral concepts
            viral_fallbacks = [
                "Elon Musk building giant AI robot cat",
                "Cats ruling the corporate boardroom",
                "Gaming streamer vs impossible boss level",
                "Coffee addicted programmer fighting bug at 3 AM"
            ]
            return {"title": random.choice(viral_fallbacks), "source": "Viral Fallback"}

        top_slice = safe_items[:min(5, len(safe_items))]
        return random.choice(top_slice)

    def generate_caricature_package(self, trend_item=None):
        """
        Creates complete English creative package:
        - Image Prompt for 2K Caricature
        - English Video Script (25-27s voiceover pacing)
        - English Titles & Captions
        """
        if not trend_item:
            trend_item = self.pick_best_trend()

        title = trend_item["title"]
        print(f"[*] Researched Trend: '{title}' from {trend_item.get('source', 'Web')}")

        clean_subject = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip()

        # Detailed prompt for high quality comic caricature
        image_prompt = (
            f"masterpiece colorful caricature cartoon illustration of {clean_subject}, "
            f"satirical editorial cartoon style, funny expressive character with exaggerated hilarious facial features, "
            f"bold clean ink outlines, vibrant watercolor digital paint, whimsical humor, "
            f"in the style of classic comic magazine cover art, 4k resolution, high detail"
        )

        # Video Title for YouTube Shorts / TikTok
        video_title = f"Drawing '{clean_subject}' using ONLY MS Paint! 🐭🎨"

        # English 26-second voiceover script
        script_hook = f"Can you believe this caricature of {clean_subject} was drawn 100% in MS Paint with only a computer mouse? Let's find out!"
        script_sketch = "Starting with the pencil tool. Sketching these curves with a cheap mouse is an absolute nightmare for my wrist!"
        script_color = "Now let's bring it to life with vibrant colors! Filling in each section, look at how hilarious and expressive it looks!"
        script_reveal = "And boom! Here is the finished masterpiece after struggling with the mouse for hours!"
        script_cta = "Rate this drawing from 1 to 10 in the comments, and don't forget to hit like and subscribe for more speed arts!"

        full_script = f"{script_hook} {script_sketch} {script_color} {script_reveal} {script_cta}"

        hashtags = [
            "#shorts", "#mspaint", "#drawingchallenge", "#speedpaint",
            "#caricature", "#satisfyingart", "#artchallenge", "#trending", "#viral"
        ]

        return {
            "topic": title,
            "video_title": video_title,
            "image_prompt": image_prompt,
            "script_sections": {
                "hook": script_hook,
                "sketch": script_sketch,
                "color": script_color,
                "reveal": script_reveal,
                "cta": script_cta
            },
            "full_script": full_script,
            "hashtags": " ".join(hashtags)
        }


if __name__ == "__main__":
    r = TrendResearcher()
    pkg = r.generate_caricature_package()
    print("\n--- ENGLISH PACKAGE ---")
    print("Topic:", pkg["topic"])
    print("Video Title:", pkg["video_title"])
    print("Full Script:", pkg["full_script"])
