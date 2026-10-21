"""
AI Artist Module
Generates 2K caricature images for free using Pollinations / Free Cloud Endpoints,
with automatic watermark removal and high-resolution upscaling.
"""
import sys
import time
import requests
from PIL import Image, ImageEnhance
from pathlib import Path
from config import ASSETS_DIR, TEMP_DIR, IMAGE_MODEL


class AIArtist:
    def __init__(self):
        pass

    def generate_caricature_image(self, prompt, output_path, target_width=1080, target_height=1440):
        """
        Generates a caricature image via Pollinations (100% free, no API key needed).
        Upscales and enhances to 2K resolution.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[*] AI Artist generating caricature: '{prompt[:60]}...'")

        # Encode URL parameters
        encoded_prompt = requests.utils.quote(prompt)
        # We request high quality image
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?"
            f"width=768&height=1024&model={IMAGE_MODEL}&nologo=true"
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Attempt download with retries (Pollinations has 45s cooldown on free IP)
        success = False
        for attempt in range(1, 4):
            try:
                print(f"    -> Requesting image (Attempt {attempt}/3)...")
                response = requests.get(url, headers=headers, timeout=60)
                if response.status_code == 200 and len(response.content) > 10000:
                    temp_raw = TEMP_DIR / "raw_generated.jpg"
                    with open(temp_raw, "wb") as f:
                        f.write(response.content)
                    success = True
                    break
                elif response.status_code == 402:
                    print(f"    [!] Pollinations IP cooldown (402), waiting 15s to retry...")
                    time.sleep(15)
                else:
                    print(f"    [!] Received HTTP {response.status_code}, retrying...")
                    time.sleep(5)
            except Exception as e:
                print(f"    [!] Error during image request: {e}")
                time.sleep(5)

        if not success:
            print("[!] Could not fetch from Pollinations, using existing reference or generating fallback art...")
            ref_path = ASSETS_DIR / "paint_reference.jpg"
            if ref_path.exists():
                img = Image.open(ref_path)
            else:
                img = Image.new("RGB", (target_width, target_height), (240, 240, 240))
        else:
            img = Image.open(temp_raw)

        # Clean watermark if present at bottom right
        w, h = img.size
        # Crop 35px from bottom if it's from pollinations logo
        crop_box = (0, 0, w, h - 35)
        clean_img = img.crop(crop_box)

        # Upscale to 2K (1080 x 1440 or custom target) with high-fidelity Lanczos
        upscaled = clean_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Crisp contrast and sharpness enhancement for graphite pencil art
        enhancer = ImageEnhance.Sharpness(upscaled)
        sharpened = enhancer.enhance(1.3)
        contrast_enhancer = ImageEnhance.Contrast(sharpened)
        polished = contrast_enhancer.enhance(1.15)

        polished.save(output_path, quality=95)
        print(f"[+] 2K Sketch Image saved to: {output_path} ({target_width}x{target_height})")
        return str(output_path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    artist = AIArtist()
    sample_prompt = (
        "colorful caricature cartoon illustration of a funny cute cat dressed as a king, "
        "whimsical comic art, bold outlines, vibrant colors, 4k digital masterpiece"
    )
    test_out = TEMP_DIR / "test_2k_caricature.jpg"
    artist.generate_caricature_image(sample_prompt, test_out)
