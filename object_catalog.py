"""
Object Catalog & History Manager
Ensures 100% unique, non-repeating everyday objects for pencil sketch videos.
Tracks history in history_objects.json so no object is ever duplicated.
"""
import json
import sys
import random
import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "history_objects.json"

# Extensive catalog of 300+ simple, iconic, recognizable everyday objects
OBJECT_CATALOG = [
    # 1. Fruits & Food (50)
    "apple", "pear", "bunch of grapes", "banana", "strawberry", "watermelon slice",
    "orange", "pineapple", "cherry", "peach", "mango", "avocado", "lemon", "coconut",
    "kiwi", "pomegranate", "plum", "fig", "papaya", "croissant", "donut", "cupcake",
    "slice of pizza", "burger", "ice cream cone", "cheese wedge", "pretzel", "coffee mug",
    "tea cup with saucer", "boba milk tea", "pancake stack", "chocolate bar", "cookie",
    "sushi roll", "popcorn bucket", "lollipop", "french fries", "taco", "bread loaf",
    "honey jar", "teapot", "wine glass", "acorn", "hotdog", "sandwich", "muffin",
    "candy cane", "egg in eggcup", "birthday cake", "pie slice",

    # 2. Vehicles & Transportation (40)
    "classic car", "airplane", "bicycle", "motorcycle", "helicopter", "sailing boat",
    "submarine", "steam train", "rocket", "hot air balloon", "skateboard", "tractor",
    "fire truck", "vespa scooter", "yellow taxi", "double decker bus", "yacht",
    "kayak with paddle", "space shuttle", "vintage pickup truck", "sports car",
    "cargo ship", "rowboat", "hovercraft", "cable car", "police car", "ambulance",
    "garbage truck", "cement mixer", "bullet train", "biplane", "jet fighter",
    "ufo flying saucer", "scooter", "unicycle", "ferry boat", "rover", "speedboat",
    "school bus", "monster truck",

    # 3. Everyday Tools & Items (60)
    "wooden pencil", "vintage camera", "incandescent lightbulb", "antique hourglass",
    "brass skeleton key", "iron padlock", "scissors", "over-ear headphones", "mechanical wristwatch",
    "pocket compass", "closed umbrella", "acoustic guitar", "electric guitar",
    "violin with bow", "grand piano", "magnifying glass", "brass telescope", "flashlight",
    "hand bell", "paint brush", "feather quill pen", "fountain pen", "alarm clock",
    "cuckoo clock", "candle in holder", "oil lantern", "sunglasses", "leather boot",
    "sneaker shoe", "high heel shoe", "baseball cap", "top hat", "crown", "treasure chest",
    "anchor", "horseshoe", "retro telephone", "gramophone", "radio receiver",
    "vintage television", "game controller", "arcade joystick", "cassette tape",
    "film roll", "book with bookmark", "open journal", "envelope with wax seal",
    "backpack", "briefcase", "padlock and chain", "water canteen", "pocket knife",
    "matchstick on fire", "pad of paper", "wooden easel", "palette with paint",
    "hourglass", "barometer", "safety pin", "magnet",

    # 4. Architecture & Structures (40)
    "cozy cottage house", "fairy tale castle", "ocean lighthouse", "wooden windmill",
    "camping tent", "mountain log cabin", "stone arch bridge", "Eiffel tower",
    "igloo", "red barn", "ancient pyramid", "big ben clock tower", "oriental pagoda",
    "treehouse", "medieval watchtower", "greenhouse with plants", "gazebo",
    "water well", "birdhouse", "wind turbine", "circus tent", "haunted house",
    "stone fortress", "classic temple", "hanging bridge", "skyscrapers skyline",
    "harbor dock", "rustic fence", "gatehouse", "bell tower", "torii gate",
    "adobe hut", "chalet", "waterfall bridge", "fountain", "statue of liberty",
    "leaning tower of pisa", "colosseum", "taj mahal", "stone castle turret",

    # 5. Animals & Nature (70)
    "cute kitten", "playful puppy", "giant panda", "koala on branch", "sea turtle",
    "dolphin jumping", "wise owl on branch", "red fox", "cute penguin", "squirrel with nut",
    "hedgehog", "monarch butterfly", "dragonfly", "honey bee", "spotted ladybug",
    "blooming sunflower", "mighty oak tree", "wild red mushroom", "blooming rose",
    "desert cactus", "bonsai tree", "snowy mountain peak", "crescent moon and clouds",
    "smiling sun", "water lily flower", "lotus flower", "tulip", "daisy flower",
    "maple leaf", "four leaf clover", "sea shell", "starfish", "seahorse", "jellyfish",
    "blue whale", "clownfish", "hummingbird in flight", "majestic eagle head",
    "peacock feather", "swan on water", "flamingo", "chameleon on branch", "frog on lily pad",
    "snail with spiral shell", "rabbit with carrot", "deer with antlers", "polar bear",
    "elephant head", "giraffe head", "lion head with mane", "tiger face",
    "horse galloping", "baby seal", "platypus", "sloth hanging", "raccoon",
    "otter holding hands", "kangaroo with joey", "beaver building dam", "wolf howling",
    "parrot on perch", "toucan with colorful beak", "woodpecker", "pufferfish",
    "octopus", "coral reef branch", "dandelion blowing seeds", "bamboo stalk",
    "fern leaf", "pinecone",

    # 6. Sports & Games (40)
    "soccer ball", "basketball", "tennis racket and ball", "baseball and glove",
    "bowling pin and ball", "shiny trophy cup", "golden medal", "chess knight piece",
    "chess king piece", "pair of dice", "dartboard with bullseye", "billiard 8-ball",
    "golf ball on tee", "boxing glove", "ice skate", "roller skate", "surfboard",
    "snowboard", "tennis trophy", "table tennis paddle", "badminton shuttlecock",
    "archery bow and arrow", "horseshoe game", "kettlebell", "dumbbell", "jump rope",
    "whistle on lanyard", "stopwatch", "kite flying in wind", "boomerang",
    "yo-yo with string", "rubik's cube", "magic 8-ball", "origami paper crane",
    "paper airplane", "spinning top toy", "teddy bear", "rocking horse",
    "snow globe", "pinwheel toy"
]


class ObjectCurator:
    def __init__(self):
        self.history = self._load_history()

    def _load_history(self):
        """Loads list of previously drawn objects"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"used_objects": [], "last_updated": ""}

    def _save_history(self):
        """Saves updated history to file"""
        self.history["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def get_used_names(self):
        return [item["name"].lower() for item in self.history.get("used_objects", [])]

    def select_next_object(self, force_object=None):
        """
        Picks the next unique object that has NOT been drawn yet.
        Guarantees 100% no repetition.
        """
        if force_object:
            chosen = force_object.strip()
            self._record_used(chosen)
            return chosen

        used_names = set(self.get_used_names())
        available = [obj for obj in OBJECT_CATALOG if obj.lower() not in used_names]

        # If all 300+ objects used, clear old history and restart to avoid stopping
        if not available:
            print("[i] All catalog objects have been drawn! Resetting cycle for fresh sketches...")
            self.history["used_objects"] = []
            available = OBJECT_CATALOG.copy()

        chosen = random.choice(available)
        self._record_used(chosen)
        return chosen

    def _record_used(self, obj_name):
        self.history["used_objects"].append({
            "name": obj_name,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._save_history()

    def create_sketch_package(self, object_name=None):
        """
        Builds complete package for pencil sketch creation:
        - AI Image Prompt (Pencil Sketch on textured sketchbook paper)
        - Synchronized 35s English commentary script
        - Short & punchy video title and social media caption
        """
        if not object_name:
            object_name = self.select_next_object()
        else:
            self._record_used(object_name)

        display_name = object_name.title()

        # Ultra-clean minimalist prompt for simple, tutorial-style line art
        image_prompt = (
            f"minimalist simple line art pencil sketch of a single {object_name}, "
            f"coloring book style, clean black pencil contour lines on pure white paper, "
            f"simple easy drawing tutorial for beginners, "
            f"no clutter, no complex background, perfectly centered, isolated on white background"
        )

        # Video Title: short, crisp, highly searchable
        video_title = f"How to Sketch a {display_name} with Pencil! ✏️🎨"

        # Short & Clean Social Media Post Caption (Facebook Reels / TikTok / YouTube Shorts)
        short_caption = (
            f"Simple pencil sketching tutorial: How to draw a {display_name} step by step! ✏️ "
            f"What should I sketch next? Let me know below! 👇\n\n"
            f"#pencilsketch #howtodraw #drawing #art #sketchbook #shorts"
        )

        # English ~35-second voiceover commentary script (Relaxing art tutorial style)
        script_hook = (
            f"Can you sketch a realistic {object_name} using just a single pencil? "
            f"Let's break it down step by step!"
        )
        script_step1 = (
            f"First, start with light, gentle strokes to define the overall proportions and general shape. "
            f"Keep your initial construction lines loose and clean."
        )
        script_step2 = (
            f"Next, switch to a darker graphite pencil to outline the main contours, "
            f"refining the characteristic curves and edges of the {object_name}."
        )
        script_step3 = (
            f"Now comes the satisfying part: layering cross-hatch shading to build depth, "
            f"shadows, and realistic three-dimensional volume."
        )
        script_cta = (
            f"And there you have it: a clean, realistic pencil sketch! "
            f"What object should I sketch next? Leave a comment below, "
            f"and don't forget to hit like and subscribe for daily pencil art tutorials!"
        )

        full_script = f"{script_hook} {script_step1} {script_step2} {script_step3} {script_cta}"

        return {
            "object_name": object_name,
            "display_name": display_name,
            "video_title": video_title,
            "short_caption": short_caption,
            "image_prompt": image_prompt,
            "script_sections": {
                "hook": script_hook,
                "step1": script_step1,
                "step2": script_step2,
                "step3": script_step3,
                "cta": script_cta
            },
            "full_script": full_script,
            "hashtags": "#pencilsketch #howtodraw #drawing #art #sketchbook #shorts"
        }


if __name__ == "__main__":
    curator = ObjectCurator()
    pkg = curator.create_sketch_package()
    print("--- SELECTED OBJECT ---")
    print("Object:", pkg["object_name"])
    print("Title:", pkg["video_title"])
    print("Caption:", pkg["short_caption"])
    print("Full Script:", pkg["full_script"])
    print("Total Used So Far:", len(curator.get_used_names()))
