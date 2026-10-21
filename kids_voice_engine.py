"""
Kids Voice Engine - Native English Child Voiceover Generator.
Uses Edge-TTS with en-US-AnaNeural (high-energy, joyful Disney/Pixar kid narrator).
100% FREE, Zero API Key required, Unlimited generation.
"""
import asyncio
import edge_tts
from pathlib import Path
from config import TEMP_DIR


class KidsVoiceEngine:
    def __init__(self, voice="en-US-AnaNeural", rate="+3%"):
        self.voice = voice
        self.rate = rate

    def generate_voiceover_segments(self, quiz_pkg: dict) -> dict:
        """
        Generates the 6 synchronized voice segments for the given quiz package.
        Returns dict mapping segment key to generated MP3 Path.
        """
        category_name = quiz_pkg.get("category", "animal").rstrip("s")
        if category_name == "vehicle":
            mystery_noun = "mystery vehicle"
        elif category_name == "fruit":
            mystery_noun = "mystery fruit"
        elif category_name == "dinosaur":
            mystery_noun = "mystery dinosaur"
        else:
            mystery_noun = "mystery animal"

        segments = {
            "hook": f"Can you guess this {mystery_noun} in five seconds? Listen closely!",
            "clue1": f"{quiz_pkg['clue1'].replace('CLUE 1:', '').strip()}",
            "clue2": f"{quiz_pkg['clue2'].replace('CLUE 2:', '').strip()}",
            "countdown": "Ready? Five, four, three, two, one!",
            "reveal": f"Tada! {quiz_pkg['reveal_text']} Yay! You did it, little explorer! You are super smart!",
            "outro": "Did you guess it right? Tell me in the comments, and subscribe for tomorrow's mystery game! Bye-bye!"
        }

        output_paths = {}
        for key, text in segments.items():
            path = TEMP_DIR / f"voice_seg_{key}.mp3"
            asyncio.run(self._synth(text, path))
            output_paths[key] = path

        print(f"[+] All 6 voice segments generated successfully for '{quiz_pkg['name']}'")
        return output_paths

    async def _synth(self, text: str, dest_path: Path):
        comm = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await comm.save(str(dest_path))


if __name__ == "__main__":
    from kids_catalog import KIDS_TOPICS
    engine = KidsVoiceEngine()
    paths = engine.generate_voiceover_segments(KIDS_TOPICS[0])
    print("Voice segments:", paths)
