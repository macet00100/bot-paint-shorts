"""
Kids Art Engine - Generates 3D Pixar Character Cutouts and Glowing Mystery Silhouettes.
Uses free Pollinations AI (FLUX) + AI Salient Object Removal (rembg).
Works on ALL animals, dinosaurs, fruits, and vehicles (regardless of character color).
100% FREE, Zero API Key required, Zero Watermarks.
"""
import urllib.request
import urllib.parse
from pathlib import Path
import cv2
import numpy as np
import rembg

from config import BASE_DIR, TEMP_DIR, ASSETS_DIR

CHARACTERS_DIR = ASSETS_DIR / "kids_characters"
CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)


class KidsArtEngine:
    def __init__(self):
        pass

    def get_character_assets(self, topic_pkg: dict) -> tuple[Path, Path]:
        """
        Returns (cutout_png_path, silhouette_png_path) for the given quiz topic.
        Caches character cutouts in assets/kids_characters/ so they don't need re-downloading.
        """
        topic_id = topic_pkg["id"]
        cutout_path = CHARACTERS_DIR / f"{topic_id}.png"
        silhouette_path = TEMP_DIR / f"{topic_id}_silhouette.png"

        # If already cached and valid, regenerate silhouette if needed and return
        if cutout_path.exists():
            img = cv2.imread(str(cutout_path), cv2.IMREAD_UNCHANGED)
            if img is not None and img.shape[2] == 4 and np.count_nonzero(img[:, :, 3] > 30) > 10000:
                print(f"[+] Using verified cached character cutout: {cutout_path.name}")
                self._generate_silhouette_from_cutout(cutout_path, silhouette_path)
                return cutout_path, silhouette_path

        print(f"[*] Generating 3D Pixar character art for '{topic_pkg['name']}' via Pollinations AI...")
        prompt = topic_pkg["image_prompt"].replace("on bright solid neon green screen background, chroma key", "on clean solid plain white background")
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"

        raw_download_path = TEMP_DIR / f"{topic_id}_raw.jpg"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=45) as resp, open(raw_download_path, "wb") as f:
            f.write(resp.read())

        print(f"[+] Downloaded raw image. Applying AI background removal (rembg)...")
        self._process_image_with_rembg(raw_download_path, cutout_path, silhouette_path)

        # Cleanup raw download to keep disk 100% clean
        if raw_download_path.exists():
            raw_download_path.unlink()

        return cutout_path, silhouette_path

    def _process_image_with_rembg(self, raw_jpg_path: Path, cutout_png_path: Path, silhouette_png_path: Path):
        img = cv2.imread(str(raw_jpg_path))
        h, w = img.shape[:2]
        # Crop bottom 45px to eliminate watermark
        img = img[:h - 45, :]

        # AI Salient background removal
        rgba = rembg.remove(img)
        cv2.imwrite(str(cutout_png_path), rgba)

        self._generate_silhouette_from_cutout(cutout_png_path, silhouette_png_path)
        print(f"[+] Saved transparent character: {cutout_png_path.name}")

    @staticmethod
    def _generate_silhouette_from_cutout(cutout_path: Path, silhouette_path: Path):
        rgba = cv2.imread(str(cutout_path), cv2.IMREAD_UNCHANGED)
        h, w = rgba.shape[:2]
        alpha = rgba[:, :, 3]

        sil = np.zeros((h, w, 4), dtype=np.uint8)
        contours, _ = cv2.findContours((alpha > 30).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(sil, contours, -1, (70, 20, 50, 255), -1)  # Solid dark fill
        cv2.drawContours(sil, contours, -1, (0, 230, 255, 255), 14) # Glowing neon border
        cv2.imwrite(str(silhouette_path), sil)


if __name__ == "__main__":
    from kids_catalog import KIDS_TOPICS
    engine = KidsArtEngine()
    cutout, sil = engine.get_character_assets(KIDS_TOPICS[1]) # baby_panda
    print("Cutout:", cutout, "Silhouette:", sil)
