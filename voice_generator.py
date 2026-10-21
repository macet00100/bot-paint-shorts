"""
Voice Generator Module (100% English Native Voice)
Dual-Engine American English Voiceover:
1. Microsoft Edge TTS (en-US-ChristopherNeural: energetic US YouTuber style)
2. Google TTS (gTTS: lang='en', 100% reliable fallback)
"""
import sys
import os
import asyncio
import subprocess
from pathlib import Path
import edge_tts
from gtts import gTTS
from config import TTS_VOICE, TTS_FALLBACK_VOICE, TTS_RATE, TEMP_DIR

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class VoiceGenerator:
    def __init__(self, voice=TTS_VOICE, fallback_voice=TTS_FALLBACK_VOICE, rate=TTS_RATE):
        self.voice = voice
        self.fallback_voice = fallback_voice
        self.rate = rate

    async def _try_edge_tts(self, text, output_path, voice_name):
        communicate = edge_tts.Communicate(text, voice_name, rate=self.rate)
        await asyncio.wait_for(communicate.save(str(output_path)), timeout=20)
        return str(output_path)

    def _generate_gtts(self, text, output_path):
        """Generate reliable English speech via Google TTS"""
        raw_path = output_path.with_name(f"raw_{output_path.name}")
        tts = gTTS(text=text, lang="en", tld="com", slow=False)
        tts.save(str(raw_path))

        # Speed up slightly with atempo to ~1.15x for energetic Shorts
        cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_path),
            "-filter:a", "atempo=1.15",
            "-vn",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        try:
            raw_path.unlink()
        except Exception:
            pass
        return str(output_path)

    def generate_voiceover(self, text, output_path):
        """Generate voiceover audio with multi-engine fallback"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        safe_preview = text[:50].encode('ascii', errors='replace').decode('ascii')
        print(f"[*] Generating English voiceover: '{safe_preview}...'")

        # 1. Try Edge-TTS (en-US)
        for v in [self.voice, self.fallback_voice, "en-US-JennyNeural"]:
            try:
                print(f"    -> Trying Edge-TTS ({v})...")
                asyncio.run(self._try_edge_tts(text, output_path, v))
                if output_path.exists() and output_path.stat().st_size > 5000:
                    print(f"[+] Edge-TTS English Voiceover generated: {output_path}")
                    return str(output_path)
            except Exception as e:
                print(f"    [!] Edge-TTS attempt failed for {v}: {e}")

        # 2. Fallback: Google TTS
        print("    -> Switching to Google TTS (gTTS English) fallback...")
        try:
            self._generate_gtts(text, output_path)
            print(f"[+] Google TTS Voiceover generated: {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"[!] All TTS engines failed: {e}")
            raise RuntimeError(f"Voice generation failed: {e}")


if __name__ == "__main__":
    vg = VoiceGenerator()
    test_out = TEMP_DIR / "unified_en_voice.mp3"
    vg.generate_voiceover(
        "Can you believe this caricature was drawn 100% in MS Paint with only a mouse? Let's find out!",
        test_out
    )
