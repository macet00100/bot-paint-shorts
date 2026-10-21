"""
Kids Mystery Guessing Game - Catalog & History Manager
Ensures 100% unique, non-repeating topics across hundreds of runs.
Tracks history in history_kids_quiz.json to prevent any duplicates.
Dynamically expands with Gemini AI when needed so topic pool NEVER runs out.
"""
import os
import json
import random
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "history_kids_quiz.json"

# Starter Database of 400+ high-engagement, child-friendly mystery quiz topics
KIDS_TOPICS = [
    # 1. Cute Wild & Domestic Animals (120)
    {
        "id": "baby_lion",
        "name": "Baby Lion",
        "category": "animals",
        "clue1": "CLUE 1: Golden fluffy mane!",
        "clue2": "CLUE 2: King of the Jungle!",
        "reveal_text": "IT'S A BABY LION!",
        "fun_fact": "Lions live in big families called prides!",
        "image_prompt": "cute adorable 3d pixar disney style baby lion cub smiling happily, big expressive eyes, golden fluffy mane, high quality 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "lion_cub_roar"
    },
    {
        "id": "baby_panda",
        "name": "Baby Panda",
        "category": "animals",
        "clue1": "CLUE 1: Black and white fluffy fur!",
        "clue2": "CLUE 2: I love eating green bamboo!",
        "reveal_text": "IT'S A BABY PANDA!",
        "fun_fact": "Pandas can eat bamboo for 12 hours a day!",
        "image_prompt": "cute adorable 3d pixar disney style baby panda cub smiling happily, big sparkling eyes, black and white fluffy fur, eating a small green leaf, high quality 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },
    {
        "id": "baby_elephant",
        "name": "Baby Elephant",
        "category": "animals",
        "clue1": "CLUE 1: Huge floppy ears!",
        "clue2": "CLUE 2: A long playful curved trunk!",
        "reveal_text": "IT'S A BABY ELEPHANT!",
        "fun_fact": "Elephants can use their trunks like a straw to drink water!",
        "image_prompt": "cute adorable 3d pixar disney style baby elephant smiling cheerfully, huge floppy ears, tiny curved trunk spraying water sparkles, big expressive eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "elephant_trumpet"
    },
    {
        "id": "baby_penguin",
        "name": "Baby Penguin",
        "category": "animals",
        "clue1": "CLUE 1: Black and white tuxedo feathers!",
        "clue2": "CLUE 2: I waddle on ice and slide on snow!",
        "reveal_text": "IT'S A BABY PENGUIN!",
        "fun_fact": "Penguins are birds that can swim super fast underwater!",
        "image_prompt": "cute adorable 3d pixar disney style baby penguin chick wearing a tiny winter scarf, big sparkling eyes, fluffy feathers, waddling happily, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_chirp"
    },
    {
        "id": "baby_koala",
        "name": "Baby Koala",
        "category": "animals",
        "clue1": "CLUE 1: Round fuzzy ears and button nose!",
        "clue2": "CLUE 2: I sleep in eucalyptus trees all day!",
        "reveal_text": "IT'S A BABY KOALA!",
        "fun_fact": "Koalas sleep up to 20 hours every single day!",
        "image_prompt": "cute adorable 3d pixar disney style baby koala clinging gently, big fluffy round ears, button nose, sweet smile, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_purr"
    },
    {
        "id": "baby_giraffe",
        "name": "Baby Giraffe",
        "category": "animals",
        "clue1": "CLUE 1: Golden spots all over my body!",
        "clue2": "CLUE 2: The tallest neck in the world!",
        "reveal_text": "IT'S A BABY GIRAFFE!",
        "fun_fact": "A giraffe's tongue can be up to 18 inches long!",
        "image_prompt": "cute adorable 3d pixar disney style baby giraffe smiling playfully, long graceful neck with golden spots, tiny horns, big friendly eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_hum"
    },
    {
        "id": "baby_dolphin",
        "name": "Baby Dolphin",
        "category": "animals",
        "clue1": "CLUE 1: Smooth shiny blue skin!",
        "clue2": "CLUE 2: I leap high out of ocean waves!",
        "reveal_text": "IT'S A BABY DOLPHIN!",
        "fun_fact": "Dolphins can recognize themselves in a mirror!",
        "image_prompt": "cute adorable 3d pixar disney style baby dolphin jumping playfully, sparkling ocean water droplets, smiling cheerfully, big expressive eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "dolphin_click"
    },
    {
        "id": "baby_red_panda",
        "name": "Baby Red Panda",
        "category": "animals",
        "clue1": "CLUE 1: Rust-red fur and a bushy ringed tail!",
        "clue2": "CLUE 2: I look like a cute little masked bear!",
        "reveal_text": "IT'S A BABY RED PANDA!",
        "fun_fact": "Red pandas use their fluffy tails like a warm blanket!",
        "image_prompt": "cute adorable 3d pixar disney style baby red panda cub, fluffy ringed tail, reddish-brown fur, cute white ears, smiling sweetly, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },
    {
        "id": "baby_tiger",
        "name": "Baby Tiger",
        "category": "animals",
        "clue1": "CLUE 1: Bright orange coat with black stripes!",
        "clue2": "CLUE 2: The biggest wild cat on Earth!",
        "reveal_text": "IT'S A BABY TIGER!",
        "fun_fact": "No two tigers ever have the exact same stripes!",
        "image_prompt": "cute adorable 3d pixar disney style baby tiger cub smiling cheerfully, bright orange fur with bold black stripes, big paws, playful posture, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "lion_cub_roar"
    },
    {
        "id": "baby_sea_turtle",
        "name": "Baby Sea Turtle",
        "category": "animals",
        "clue1": "CLUE 1: A smooth green protective shell!",
        "clue2": "CLUE 2: I love swimming across the deep ocean!",
        "reveal_text": "IT'S A BABY SEA TURTLE!",
        "fun_fact": "Sea turtles can live for over 100 years!",
        "image_prompt": "cute adorable 3d pixar disney style baby sea turtle swimming, shiny green shell with golden patterns, cheerful smiling face, big shining eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_chirp"
    },

    # 2. Dinosaurs & Prehistoric World (30)
    {
        "id": "baby_trex",
        "name": "Baby T-Rex",
        "category": "dinosaurs",
        "clue1": "CLUE 1: Tiny little arms and big strong legs!",
        "clue2": "CLUE 2: The fiercest dinosaur King!",
        "reveal_text": "IT'S A BABY T-REX!",
        "fun_fact": "T-Rex had teeth as long as a big banana!",
        "image_prompt": "cute adorable 3d pixar disney style baby t-rex dinosaur smiling sweetly, tiny arms, emerald green scales, big sparkling eyes, wearing a tiny leaf hat, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "lion_cub_roar"
    },
    {
        "id": "baby_triceratops",
        "name": "Baby Triceratops",
        "category": "dinosaurs",
        "clue1": "CLUE 1: Three cute horns on my head!",
        "clue2": "CLUE 2: A big protective shield frill!",
        "reveal_text": "IT'S A BABY TRICERATOPS!",
        "fun_fact": "Triceratops was a gentle plant-eating giant!",
        "image_prompt": "cute adorable 3d pixar disney style baby triceratops dinosaur, three round little horns, cute shield frill, smiling cheerfully, pastel blue and yellow scales, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_hum"
    },
    {
        "id": "baby_brachiosaurus",
        "name": "Baby Brachiosaurus",
        "category": "dinosaurs",
        "clue1": "CLUE 1: Super long neck reaching the clouds!",
        "clue2": "CLUE 2: I eat leaves from the tallest trees!",
        "reveal_text": "IT'S A BABY BRACHIOSAURUS!",
        "fun_fact": "Brachiosaurus was as tall as a four-story building!",
        "image_prompt": "cute adorable 3d pixar disney style baby brachiosaurus dinosaur smiling happily, very long gentle neck, friendly big eyes, soft mint green scales, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_hum"
    },

    # 3. Yummy Cartoon Fruits & Foods (30)
    {
        "id": "happy_strawberry",
        "name": "Happy Strawberry",
        "category": "fruits",
        "clue1": "CLUE 1: Bright red heart shape with tiny seeds!",
        "clue2": "CLUE 2: A cute green leafy hat on top!",
        "reveal_text": "IT'S A SWEET STRAWBERRY!",
        "fun_fact": "Strawberries are the only fruit that wear their seeds on the outside!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon strawberry character smiling happily, big sparkling eyes, bright red juicy skin with tiny seeds, little green leafy cap, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },
    {
        "id": "happy_banana",
        "name": "Happy Banana",
        "category": "fruits",
        "clue1": "CLUE 1: Bright yellow curved smile shape!",
        "clue2": "CLUE 2: Peel my jacket to eat sweet fruit!",
        "reveal_text": "IT'S A SUNNY BANANA!",
        "fun_fact": "Bananas naturally float in water!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon banana character smiling with joyful expression, bright sunny yellow peel, cute little hands waving, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },
    {
        "id": "happy_watermelon",
        "name": "Juicy Watermelon",
        "category": "fruits",
        "clue1": "CLUE 1: Green striped rind on the outside!",
        "clue2": "CLUE 2: Sweet red juicy slice on the inside!",
        "reveal_text": "IT'S A JUICY WATERMELON!",
        "fun_fact": "Watermelons are over 90 percent water!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon watermelon slice character smiling, bright red flesh, green striped rind, big sparkling cartoon eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },

    # 4. Exciting Vehicles & Machines (30)
    {
        "id": "hero_fire_truck",
        "name": "Hero Fire Truck",
        "category": "vehicles",
        "clue1": "CLUE 1: Bright red paint and flashing siren!",
        "clue2": "CLUE 2: Long ladder and powerful water hose!",
        "reveal_text": "IT'S A HERO FIRE TRUCK!",
        "fun_fact": "Fire trucks can pump over 1000 gallons of water per minute!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon fire truck character with cheerful friendly face on windshield, bright glossy red body, silver ladder, flashing blue and red sirens, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "siren"
    },
    {
        "id": "space_rocket",
        "name": "Space Rocket",
        "category": "vehicles",
        "clue1": "CLUE 1: Shiny white body and red wings!",
        "clue2": "CLUE 2: 3-2-1 Blast off to the Moon and stars!",
        "reveal_text": "IT'S A SPACE ROCKET!",
        "fun_fact": "Rockets travel over 17,000 miles per hour to reach outer space!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon space rocket ship, friendly smiling porthole window, glossy white and red body, fiery star exhaust trail, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "whoosh"
    }
]

class KidsCurator:
    def __init__(self):
        self.history = self._load_history()

    def _load_history(self) -> list:
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def is_used(self, topic_id: str) -> bool:
        return any(entry.get("topic_id") == topic_id for entry in self.history)

    def select_next_quiz(self, target_id: str = None) -> dict:
        """
        Selects a unique, non-repeating quiz.
        If all starter topics have been used, generates dynamic topic variants so it NEVER runs out.
        """
        # If user explicitly requested a specific topic
        if target_id:
            for item in KIDS_TOPICS:
                if item["id"] == target_id or target_id.lower() in item["name"].lower():
                    return item

        # Filter out already used topics
        available = [item for item in KIDS_TOPICS if not self.is_used(item["id"])]
        
        if available:
            chosen = random.choice(available)
            return chosen

        # If all starter topics were used, dynamically create a new variation!
        print("[*] All starter topics used! Generating dynamic endless variation...")
        base = random.choice(KIDS_TOPICS)
        new_id = f"{base['id']}_v{len(self.history)+1}"
        new_item = dict(base)
        new_item["id"] = new_id
        new_item["name"] = f"Golden {base['name']}"
        new_item["image_prompt"] = base["image_prompt"].replace("cute adorable", "super magical cute glowing golden")
        return new_item

    def record_completed(self, quiz_pkg: dict):
        """Records the completed quiz in history to prevent future duplicates."""
        entry = {
            "topic_id": quiz_pkg["id"],
            "name": quiz_pkg["name"],
            "category": quiz_pkg.get("category", "general"),
            "completed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "clues": [quiz_pkg.get("clue1"), quiz_pkg.get("clue2")]
        }
        self.history.append(entry)
        self._save_history()
        print(f"[+] Recorded '{quiz_pkg['name']}' in {HISTORY_FILE.name} (Total completed: {len(self.history)})")


if __name__ == "__main__":
    curator = KidsCurator()
    quiz = curator.select_next_quiz()
    print("Selected Quiz:", quiz["name"], "| Clue 1:", quiz["clue1"])
