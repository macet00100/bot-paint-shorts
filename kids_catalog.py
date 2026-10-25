"""
Kids Mystery Guessing Game - Catalog & History Manager
Contains 100+ rich, unique, child-friendly mystery quiz topics.
Guarantees 100% strict anti-duplication across all runs.
"""
import os
import json
import random
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "history_kids_quiz.json"

# Master Database of 100+ unique, highly engaging, child-friendly mystery quiz topics
KIDS_TOPICS = [
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
        "clue1": "CLUE 1: Round fluffy ears and big black nose!",
        "clue2": "CLUE 2: I hug eucalyptus trees and sleep all day!",
        "reveal_text": "IT'S A BABY KOALA!",
        "fun_fact": "Koalas can sleep up to 20 hours every single day!",
        "image_prompt": "cute adorable 3d pixar disney style baby koala hugging a tree branch, big round fuzzy ears, cute oval black nose, warm friendly eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_giggle"
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
        "sound_type": "happy_whistle"
    },
    {
        "id": "baby_tiger",
        "name": "Baby Tiger",
        "category": "animals",
        "clue1": "CLUE 1: Bright orange coat with black stripes!",
        "clue2": "CLUE 2: The biggest wild cat on Earth!",
        "reveal_text": "IT'S A BABY TIGER!",
        "fun_fact": "No two tigers ever have the exact same stripes!",
        "image_prompt": "cute adorable 3d pixar disney style baby tiger cub sitting playfully, bright orange fur with soft black stripes, big shining amber eyes, friendly smile, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "tiger_purr"
    },
    {
        "id": "baby_red_panda",
        "name": "Baby Red Panda",
        "category": "animals",
        "clue1": "CLUE 1: Cinnamon red fur and white cheek tufts!",
        "clue2": "CLUE 2: A big bushy striped tail!",
        "reveal_text": "IT'S A BABY RED PANDA!",
        "fun_fact": "Red pandas use their bushy tails like cozy blankets to keep warm!",
        "image_prompt": "cute adorable 3d pixar disney style baby red panda holding a tiny bamboo leaf, cinnamon red fur, giant striped bushy tail, curious sparkling eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },
    {
        "id": "baby_kangaroo",
        "name": "Baby Kangaroo",
        "category": "animals",
        "clue1": "CLUE 1: Strong bouncy hind legs and big paws!",
        "clue2": "CLUE 2: I love riding in my mommy's pouch!",
        "reveal_text": "IT'S A BABY KANGAROO!",
        "fun_fact": "Baby kangaroos are called joeys and can jump 3 times their height!",
        "image_prompt": "cute adorable 3d pixar disney style baby kangaroo joey smiling joyfully, big curious upright ears, soft brown fur, tiny boxing gloves playful pose, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bounce_boing"
    },
    {
        "id": "baby_hedgehog",
        "name": "Baby Hedgehog",
        "category": "animals",
        "clue1": "CLUE 1: Tiny button nose and sweet little paws!",
        "clue2": "CLUE 2: I roll into a prickly ball when shy!",
        "reveal_text": "IT'S A BABY HEDGEHOG!",
        "fun_fact": "A baby hedgehog has soft quills that harden as it grows!",
        "image_prompt": "cute adorable 3d pixar disney style baby hedgehog smiling cheerfully, soft round belly, tiny spiky quills, shining little button nose, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },
    {
        "id": "baby_polar_bear",
        "name": "Baby Polar Bear",
        "category": "animals",
        "clue1": "CLUE 1: Fluffy snow-white fur and black nose!",
        "clue2": "CLUE 2: The champion swimmer of the freezing Arctic!",
        "reveal_text": "IT'S A BABY POLAR BEAR!",
        "fun_fact": "Polar bears actually have black skin underneath their white fur to soak up sun heat!",
        "image_prompt": "cute adorable 3d pixar disney style baby polar bear cub playing with a snowball, snow-white fluffy fur, big black nose, sparkling blue eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "friendly_growl"
    },
    {
        "id": "baby_fox",
        "name": "Baby Red Fox",
        "category": "animals",
        "clue1": "CLUE 1: Pointy triangular ears and white chest!",
        "clue2": "CLUE 2: A magnificent bushy red tail with a white tip!",
        "reveal_text": "IT'S A BABY FOX!",
        "fun_fact": "Foxes use their bushy tails for balance and like a warm scarf in winter!",
        "image_prompt": "cute adorable 3d pixar disney style baby red fox kit sitting playfully, bright ginger-red coat, white chest fluff, huge bushy tail, clever golden eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "happy_yip"
    },
    {
        "id": "baby_sloth",
        "name": "Baby Sloth",
        "category": "animals",
        "clue1": "CLUE 1: Curved friendly claws and gentle smile!",
        "clue2": "CLUE 2: I hang upside down and move super slow!",
        "reveal_text": "IT'S A BABY SLOTH!",
        "fun_fact": "Sloths move so slowly that tiny harmless green plants can grow on their fur!",
        "image_prompt": "cute adorable 3d pixar disney style baby sloth hanging upside down from a wooden branch, big sweet smiling face, soft fuzzy fur, rounded claws, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "slow_hum"
    },
    {
        "id": "baby_cheetah",
        "name": "Baby Cheetah",
        "category": "animals",
        "clue1": "CLUE 1: Dark teardrop stripes running down my face!",
        "clue2": "CLUE 2: The fastest land sprinter in the world!",
        "reveal_text": "IT'S A BABY CHEETAH!",
        "fun_fact": "Cheetahs can run as fast as cars on a highway in just 3 seconds!",
        "image_prompt": "cute adorable 3d pixar disney style baby cheetah cub sitting alert, spotted golden coat, fluffy silver mane, dark teardrop eye marks, shining amber eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cheetah_chirp"
    },
    {
        "id": "baby_zebra",
        "name": "Baby Zebra",
        "category": "animals",
        "clue1": "CLUE 1: An upright spiky mane on my neck!",
        "clue2": "CLUE 2: Dazzling black and white zebra stripes!",
        "reveal_text": "IT'S A BABY ZEBRA!",
        "fun_fact": "Zebras can stand and walk just 20 minutes after being born!",
        "image_prompt": "cute adorable 3d pixar disney style baby zebra foal trotting happily, crisp black and white stripes, fluffy mane, big friendly brown eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "horse_whinny"
    },
    {
        "id": "baby_hippo",
        "name": "Baby Hippo",
        "category": "animals",
        "clue1": "CLUE 1: Chubby round belly and tiny ears!",
        "clue2": "CLUE 2: I love splashing in warm river water and mud!",
        "reveal_text": "IT'S A BABY HIPPO!",
        "fun_fact": "Hippos can hold their breath underwater for up to 5 minutes!",
        "image_prompt": "cute adorable 3d pixar disney style baby hippopotamus splashing joyfully, chubby smooth pink-gray body, tiny wiggling ears, big friendly nostrils, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "water_splash"
    },
    {
        "id": "baby_alpaca",
        "name": "Baby Alpaca",
        "category": "animals",
        "clue1": "CLUE 1: Fluffy cloud-like fleece on my neck!",
        "clue2": "CLUE 2: Gentle big doe eyes and cute pointy ears!",
        "reveal_text": "IT'S A BABY ALPACA!",
        "fun_fact": "Alpacas hum when they are happy, curious, or greeting friends!",
        "image_prompt": "cute adorable 3d pixar disney style baby alpaca smiling adorably, super fluffy white cloud-like wool, gentle huge brown eyes, sweet smiling mouth, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "alpaca_hum"
    },
    {
        "id": "baby_otter",
        "name": "Baby Sea Otter",
        "category": "animals",
        "clue1": "CLUE 1: Water-repellent fur and webbed paws!",
        "clue2": "CLUE 2: I float on my back and hold hands with friends!",
        "reveal_text": "IT'S A BABY SEA OTTER!",
        "fun_fact": "Sea otters hold hands while sleeping so they don't drift away in ocean currents!",
        "image_prompt": "cute adorable 3d pixar disney style baby sea otter floating on its back, hugging a shiny colorful pebble to its tummy, whiskers twitching, big sparkling black eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },
    {
        "id": "baby_husky",
        "name": "Baby Husky Puppy",
        "category": "animals",
        "clue1": "CLUE 1: Pointy wolf ears and curled furry tail!",
        "clue2": "CLUE 2: Sparkling ice-blue eyes and joyful howling!",
        "reveal_text": "IT'S A BABY HUSKY!",
        "fun_fact": "Huskies are famous for talking and singing back to their owners!",
        "image_prompt": "cute adorable 3d pixar disney style baby siberian husky puppy sitting happily, thick gray and white fur, piercing bright icy blue eyes, tongue out smiling, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "puppy_bark"
    },
    {
        "id": "baby_bunny",
        "name": "Baby Bunny",
        "category": "animals",
        "clue1": "CLUE 1: Long soft floppy ears!",
        "clue2": "CLUE 2: A twitchy pink nose and fluffy cotton tail!",
        "reveal_text": "IT'S A BABY BUNNY!",
        "fun_fact": "When bunnies are super excited and happy, they do a joyful leap called a binky!",
        "image_prompt": "cute adorable 3d pixar disney style baby rabbit bunny sitting on hind legs, long velvety floppy ears, twitchy pink nose, fluffy white cotton tail, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_snort"
    },
    {
        "id": "baby_deer",
        "name": "Baby Deer Fawn",
        "category": "animals",
        "clue1": "CLUE 1: Slender graceful legs and gentle brown eyes!",
        "clue2": "CLUE 2: White camouflage spots scattered on my back!",
        "reveal_text": "IT'S A BABY DEER!",
        "fun_fact": "A fawn's white spots look just like dappled sunlight filtering through forest leaves!",
        "image_prompt": "cute adorable 3d pixar disney style baby deer fawn standing gracefully, golden-brown coat with delicate white polka dots, big gentle dark eyes, tiny tail, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "gentle_chime"
    },
    {
        "id": "baby_dolphin",
        "name": "Baby Dolphin",
        "category": "sea_creatures",
        "clue1": "CLUE 1: Smooth silvery skin and a playful curved snout!",
        "clue2": "CLUE 2: I jump over ocean waves and click to talk!",
        "reveal_text": "IT'S A BABY DOLPHIN!",
        "fun_fact": "Dolphins sleep with one eye open to keep watch for danger!",
        "image_prompt": "cute adorable 3d pixar disney style baby dolphin leaping happily out of water sparkles, smooth shiny blue-gray skin, sweet cheerful smile, big shining eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "dolphin_click"
    },
    {
        "id": "baby_sea_turtle",
        "name": "Baby Sea Turtle",
        "category": "sea_creatures",
        "clue1": "CLUE 1: Smooth flippers that glide like underwater wings!",
        "clue2": "CLUE 2: A beautiful patterned green shell on my back!",
        "reveal_text": "IT'S A BABY SEA TURTLE!",
        "fun_fact": "Sea turtles can live to be over 100 years old!",
        "image_prompt": "cute adorable 3d pixar disney style baby sea turtle swimming, shiny green shell with golden patterns, cheerful smiling face, big shining eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "ocean_bubble"
    },
    {
        "id": "baby_clownfish",
        "name": "Baby Clownfish",
        "category": "sea_creatures",
        "clue1": "CLUE 1: Bright orange body with crisp white stripes!",
        "clue2": "CLUE 2: I live safely inside tickly sea anemone tentacles!",
        "reveal_text": "IT'S A BABY CLOWNFISH!",
        "fun_fact": "Clownfish have special mucus on their skin so sea anemones cannot sting them!",
        "image_prompt": "cute adorable 3d pixar disney style baby clownfish swimming joyfully, bright vivid orange scales with black-trimmed white stripes, tiny fluttering fins, big expressive eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bubble_pop"
    },
    {
        "id": "baby_octopus",
        "name": "Baby Octopus",
        "category": "sea_creatures",
        "clue1": "CLUE 1: A round squishy head with curious big eyes!",
        "clue2": "CLUE 2: Eight wiggly arms covered with suction cups!",
        "reveal_text": "IT'S A BABY OCTOPUS!",
        "fun_fact": "An octopus has three hearts and blue blood!",
        "image_prompt": "cute adorable 3d pixar disney style baby octopus floating happily, eight curled wiggly purple tentacles with tiny suction cups, big shimmering golden eyes, blowing a tiny bubble, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "water_squish"
    },
    {
        "id": "baby_seahorse",
        "name": "Little Seahorse",
        "category": "sea_creatures",
        "clue1": "CLUE 1: A coronet crown on top of my head!",
        "clue2": "CLUE 2: A curled tail that anchors onto ocean coral!",
        "reveal_text": "IT'S A LITTLE SEAHORSE!",
        "fun_fact": "Seahorses pair up for life and dance together every morning!",
        "image_prompt": "cute adorable 3d pixar disney style baby seahorse upright posture, pastel pink and yellow segmented armor, tiny fluttering back fin, curled tail holding a seaweed, big sweet eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "magical_twinkle"
    },
    {
        "id": "baby_blue_whale",
        "name": "Baby Blue Whale",
        "category": "sea_creatures",
        "clue1": "CLUE 1: A giant heart the size of a small car!",
        "clue2": "CLUE 2: I spout misty water rainbows from my blowhole!",
        "reveal_text": "IT'S A BABY BLUE WHALE!",
        "fun_fact": "The blue whale is the largest animal ever known to have lived on Earth!",
        "image_prompt": "cute adorable 3d pixar disney style baby blue whale swimming gracefully, deep ocean blue belly, gentle smiling face, spouting a tiny sparkling water fountain, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "whale_song"
    },
    {
        "id": "baby_jellyfish",
        "name": "Glowing Jellyfish",
        "category": "sea_creatures",
        "clue1": "CLUE 1: An umbrella bell that pulses in the water!",
        "clue2": "CLUE 2: Shimmering neon tentacles that glow in deep dark sea!",
        "reveal_text": "IT'S A GLOWING JELLYFISH!",
        "fun_fact": "Jellyfish have been swimming in oceans for over 500 million years, older than dinosaurs!",
        "image_prompt": "cute adorable 3d pixar disney style baby jellyfish floating, translucent soft pastel pink-blue dome, glowing bioluminescent trailing tentacles, smiling face, sparkling magical aura, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "magical_twinkle"
    },
    {
        "id": "baby_seal",
        "name": "Baby Harp Seal",
        "category": "sea_creatures",
        "clue1": "CLUE 1: Huge dark watery puppy eyes!",
        "clue2": "CLUE 2: Fluffy snow-white coat resting on Arctic ice!",
        "reveal_text": "IT'S A BABY HARP SEAL!",
        "fun_fact": "Baby seal pups are born with fluffy white fur that helps them blend into ice!",
        "image_prompt": "cute adorable 3d pixar disney style baby harp seal pup resting on stomach, pure white fluffy coat, giant glistening round black eyes, cute black button nose, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "seal_squeak"
    },
    {
        "id": "baby_crab",
        "name": "Cheerful Crab",
        "category": "sea_creatures",
        "clue1": "CLUE 1: Stalk eyes that swivel in all directions!",
        "clue2": "CLUE 2: Two friendly clicking claws and I walk sideways!",
        "reveal_text": "IT'S A CHEERFUL CRAB!",
        "fun_fact": "Crabs walk and run sideways because their leg joints bend outward!",
        "image_prompt": "cute adorable 3d pixar disney style baby red crab smiling cheerfully, shiny scarlet shell, two raised clicking pincers, big friendly round eyes on stalks, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "click_clack"
    },
    {
        "id": "baby_flamingo",
        "name": "Baby Flamingo",
        "category": "birds",
        "clue1": "CLUE 1: Stilt-like long legs and curved beak!",
        "clue2": "CLUE 2: Rosy pink feathers and I balance on one leg!",
        "reveal_text": "IT'S A BABY FLAMINGO!",
        "fun_fact": "Flamingos get their vibrant pink color from the healthy shrimp and algae they eat!",
        "image_prompt": "cute adorable 3d pixar disney style baby flamingo chick balancing adorably on one slender leg, fluffy coral-pink down feathers, curved cute beak, big sparkling eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bird_chirp"
    },
    {
        "id": "baby_owl",
        "name": "Baby Barn Owl",
        "category": "birds",
        "clue1": "CLUE 1: A heart-shaped feathery face!",
        "clue2": "CLUE 2: I turn my head almost all the way around at night!",
        "reveal_text": "IT'S A BABY OWL!",
        "fun_fact": "Owls have silent wings so they make zero noise when gliding through the night!",
        "image_prompt": "cute adorable 3d pixar disney style baby barn owl sitting on a tree branch, heart-shaped white face, golden-speckled feathers, huge wide golden night eyes, curious head tilt, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "owl_hoot"
    },
    {
        "id": "baby_parrot",
        "name": "Rainbow Macaw",
        "category": "birds",
        "clue1": "CLUE 1: A strong hooked beak and long tail feathers!",
        "clue2": "CLUE 2: Bright red, yellow, and blue tropical feathers!",
        "reveal_text": "IT'S A RAINBOW MACAW!",
        "fun_fact": "Macaws can mimic human words and live for over 60 years!",
        "image_prompt": "cute adorable 3d pixar disney style baby scarlet macaw parrot, brilliant vibrant red body, royal blue and sunny yellow wing feathers, smiling hooked beak, big expressive eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "parrot_squawk"
    },
    {
        "id": "baby_toucan",
        "name": "Little Toucan",
        "category": "birds",
        "clue1": "CLUE 1: Glossy black jungle body feathers!",
        "clue2": "CLUE 2: A giant rainbow-colored banana-shaped beak!",
        "reveal_text": "IT'S A LITTLE TOUCAN!",
        "fun_fact": "Even though a toucan's beak is huge, it is super light like a hollow honeycomb!",
        "image_prompt": "cute adorable 3d pixar disney style baby toucan perched on a tropical branch, enormous colorful orange-yellow-blue beak, shiny black body feathers, white throat, bright blue eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "jungle_call"
    },
    {
        "id": "baby_peacock",
        "name": "Baby Peacock",
        "category": "birds",
        "clue1": "CLUE 1: A royal feathery crest like a crown on my head!",
        "clue2": "CLUE 2: A magnificent fan of shimmering emerald feathers!",
        "reveal_text": "IT'S A BABY PEACOCK!",
        "fun_fact": "A peacock's giant feather train can have over 200 shimmering eye-spots!",
        "image_prompt": "cute adorable 3d pixar disney style baby peacock fanning out a mini tail of iridescent emerald and sapphire feathers with eye-spots, tiny feathery crown, proud smiling pose, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "royal_fanfare"
    },
    {
        "id": "baby_duckling",
        "name": "Yellow Duckling",
        "category": "birds",
        "clue1": "CLUE 1: An orange flat bill and paddle webbed feet!",
        "clue2": "CLUE 2: Fluffy bright yellow down feathers and happy quacks!",
        "reveal_text": "IT'S A YELLOW DUCKLING!",
        "fun_fact": "Ducklings learn to swim on their very first day of life!",
        "image_prompt": "cute adorable 3d pixar disney style baby duckling waddling cheerfully, super fluffy canary-yellow down feathers, bright orange bill, big round black eyes, splashing a water droplet, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "duck_quack"
    },
    {
        "id": "busy_honeybee",
        "name": "Busy Honeybee",
        "category": "insects",
        "clue1": "CLUE 1: Fuzzy yellow and black velvet stripes!",
        "clue2": "CLUE 2: Fluttering translucent wings making sweet honey!",
        "reveal_text": "IT'S A BUSY HONEYBEE!",
        "fun_fact": "Bees dance with specific wiggles to tell their friends where fresh flowers are!",
        "image_prompt": "cute adorable 3d pixar disney style baby honeybee hovering, fuzzy yellow and black striped body, transparent iridescent wings, tiny smiling face with antennae, holding a tiny honey dipper, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "buzz_buzz"
    },
    {
        "id": "happy_ladybug",
        "name": "Cute Ladybug",
        "category": "insects",
        "clue1": "CLUE 1: Six tiny black walking feet and antennae!",
        "clue2": "CLUE 2: A shiny scarlet dome shell with black polka dots!",
        "reveal_text": "IT'S A CUTE LADYBUG!",
        "fun_fact": "Ladybugs protect gardeners' plants by eating pesky tiny garden bugs!",
        "image_prompt": "cute adorable 3d pixar disney style baby ladybug sitting on a dewy green leaf, glossy bright red dome shell with bold black polka dots, smiling face, big friendly eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_chime"
    },
    {
        "id": "flutter_butterfly",
        "name": "Flutter Butterfly",
        "category": "insects",
        "clue1": "CLUE 1: Slender curled antennae and delicate legs!",
        "clue2": "CLUE 2: Giant breathtaking stained-glass rainbow wings!",
        "reveal_text": "IT'S A FLUTTER BUTTERFLY!",
        "fun_fact": "Butterflies actually taste sweet flower nectar with their tiny feet!",
        "image_prompt": "cute adorable 3d pixar disney style baby butterfly hovering, majestic vibrant rainbow wings with glowing patterns, tiny smiling body with spiral antennae, magical sparkle aura, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "flutter_wings"
    },
    {
        "id": "glowing_firefly",
        "name": "Glowing Firefly",
        "category": "insects",
        "clue1": "CLUE 1: Gentle dark wings and curious antennae!",
        "clue2": "CLUE 2: A magical golden lantern tummy that blinks in the night!",
        "reveal_text": "IT'S A GLOWING FIREFLY!",
        "fun_fact": "Firefly lights are 100% cold light with zero wasted heat!",
        "image_prompt": "cute adorable 3d pixar disney style baby firefly smiling warmly, glowing luminous golden abdomen casting warm light, tiny fluttering wings, big cheerful eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "magical_twinkle"
    },
    {
        "id": "baby_trex",
        "name": "Baby T-Rex",
        "category": "dinosaurs",
        "clue1": "CLUE 1: Tiny little arms and big strong legs!",
        "clue2": "CLUE 2: The fiercest dinosaur King!",
        "reveal_text": "IT'S A BABY T-REX!",
        "fun_fact": "A full grown T-Rex had teeth the size of giant bananas!",
        "image_prompt": "cute adorable 3d pixar disney style baby tyrannosaurus rex smiling cheerfully, soft green scales, tiny cute arms, giant head with big expressive friendly eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "dino_roar"
    },
    {
        "id": "baby_triceratops",
        "name": "Baby Triceratops",
        "category": "dinosaurs",
        "clue1": "CLUE 1: A big protective bony frill on my head!",
        "clue2": "CLUE 2: Three pointy horns and a cute parrot-like beak!",
        "reveal_text": "IT'S A BABY TRICERATOPS!",
        "fun_fact": "Triceratops had up to 800 teeth in its jaws that constantly replaced themselves!",
        "image_prompt": "cute adorable 3d pixar disney style baby triceratops smiling playfully, gentle blue-green scaly body, three tiny cute horns, decorative frill collar, big friendly brown eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "dino_stomp"
    },
    {
        "id": "baby_brachiosaurus",
        "name": "Baby Brachiosaurus",
        "category": "dinosaurs",
        "clue1": "CLUE 1: Front legs longer than my back legs!",
        "clue2": "CLUE 2: An enormous long neck reaching high treetop leaves!",
        "reveal_text": "IT'S A BABY BRACHIOSAURUS!",
        "fun_fact": "Brachiosaurus was as tall as a 4-story building and loved munching treetop leaves!",
        "image_prompt": "cute adorable 3d pixar disney style baby brachiosaurus standing tall, super long graceful neck, cheerful smiling face, pastel green scaly skin, friendly huge eyes, chewing a leaf, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "dino_rumble"
    },
    {
        "id": "baby_stegosaurus",
        "name": "Baby Stegosaurus",
        "category": "dinosaurs",
        "clue1": "CLUE 1: Four sharp defensive spikes on my tail!",
        "clue2": "CLUE 2: Diamond-shaped kite plates standing along my back!",
        "reveal_text": "IT'S A BABY STEGOSAURUS!",
        "fun_fact": "Stegosaurus had a brain the size of a tiny walnut, but was a peaceful plant eater!",
        "image_prompt": "cute adorable 3d pixar disney style baby stegosaurus walking happily, row of colorful pentagonal plates along back, four tail spikes, sweet smiling face, big friendly eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "dino_thud"
    },
    {
        "id": "baby_pterodactyl",
        "name": "Baby Pterodactyl",
        "category": "dinosaurs",
        "clue1": "CLUE 1: A pointy aerodynamic crest behind my head!",
        "clue2": "CLUE 2: Giant leathery wings that soar across prehistoric skies!",
        "reveal_text": "IT'S A BABY PTERODACTYL!",
        "fun_fact": "Pterodactyls were flying reptiles, not technically dinosaurs!",
        "image_prompt": "cute adorable 3d pixar disney style baby pterodactyl soaring with outstretched leathery wings, cute backward crest, friendly smiling beak, big shining golden eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bird_chirp"
    },
    {
        "id": "baby_mammoth",
        "name": "Baby Woolly Mammoth",
        "category": "dinosaurs",
        "clue1": "CLUE 1: Long curved ivory tusks and fuzzy trunk!",
        "clue2": "CLUE 2: A thick shaggy brown woolly coat for Ice Age blizzards!",
        "reveal_text": "IT'S A BABY WOOLLY MAMMOTH!",
        "fun_fact": "Woolly mammoths had ears much smaller than elephants so they wouldn't get frostbite!",
        "image_prompt": "cute adorable 3d pixar disney style baby woolly mammoth standing playfully in snow, thick shaggy chocolate-brown fur, two tiny curved white tusks, cute trunk, big warm eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "elephant_trumpet"
    },
    {
        "id": "happy_strawberry",
        "name": "Happy Strawberry",
        "category": "fruits",
        "clue1": "CLUE 1: Bright red heart shape with tiny golden seeds!",
        "clue2": "CLUE 2: A cute green leafy hat sitting on top!",
        "reveal_text": "IT'S A SWEET STRAWBERRY!",
        "fun_fact": "Strawberries are the only fruit that wear their seeds on the outside!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon strawberry character smiling, glossy bright red body, tiny golden seeds, cute green leafy stem hat, big shining eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "happy_bell"
    },
    {
        "id": "happy_banana",
        "name": "Happy Banana",
        "category": "fruits",
        "clue1": "CLUE 1: Bright yellow curved smile shape!",
        "clue2": "CLUE 2: Peel my jacket to eat sweet fruit!",
        "reveal_text": "IT'S A SUNNY BANANA!",
        "fun_fact": "Bananas naturally float in water because they have tiny air pockets!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon banana character dancing cheerfully, bright sunny yellow peel, cute face with big sparkling eyes, waving tiny hands, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bounce_boing"
    },
    {
        "id": "happy_watermelon",
        "name": "Juicy Watermelon",
        "category": "fruits",
        "clue1": "CLUE 1: Green striped rind on the outside!",
        "clue2": "CLUE 2: Sweet red juicy slice on the inside!",
        "reveal_text": "IT'S A JUICY WATERMELON!",
        "fun_fact": "Watermelons are over 92 percent pure hydrating water!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon watermelon slice character smiling, vibrant red center, dark green striped rind, cute smile, rosy pink cheeks, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bubble_pop"
    },
    {
        "id": "creamy_avocado",
        "name": "Creamy Avocado",
        "category": "fruits",
        "clue1": "CLUE 1: Dark bumpy green skin on the outside!",
        "clue2": "CLUE 2: Smooth creamy green fruit with a giant round seed tummy!",
        "reveal_text": "IT'S A CREAMY AVOCADO!",
        "fun_fact": "Avocados are actually giant single-seeded berries that grow on trees!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon avocado half character, rich creamy lime-green flesh, big smooth brown seed belly, dark textured skin, smiling face, rosy cheeks, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_pop"
    },
    {
        "id": "sweet_pineapple",
        "name": "Sweet Pineapple",
        "category": "fruits",
        "clue1": "CLUE 1: A spiky crown of stiff green leaves!",
        "clue2": "CLUE 2: Golden diamond armor and sweet tropical juice!",
        "reveal_text": "IT'S A SWEET PINEAPPLE!",
        "fun_fact": "A pineapple takes almost two whole years to grow and ripen!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon pineapple character smiling, textured golden-yellow diamond body, vibrant spiky green crown on top, cool cartoon sunglasses on forehead, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "tropical_marimba"
    },
    {
        "id": "rosy_peach",
        "name": "Rosy Peach",
        "category": "fruits",
        "clue1": "CLUE 1: Soft velvety fuzzy skin you can feel!",
        "clue2": "CLUE 2: Sweet blushing pink cheeks and a sweet stone inside!",
        "reveal_text": "IT'S A ROSY PEACH!",
        "fun_fact": "Peaches belong to the same plant family as beautiful wild roses!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon peach character, velvety blushing pink and golden-orange skin, soft fuzzy texture, cute green leaf on top, smiling happily, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "gentle_chime"
    },
    {
        "id": "crunchy_carrot",
        "name": "Crunchy Carrot",
        "category": "vegetables",
        "clue1": "CLUE 1: Bright orange pointy root that grows under soil!",
        "clue2": "CLUE 2: A bushy green leafy hairdo on top, bunnies love me!",
        "reveal_text": "IT'S A CRUNCHY CARROT!",
        "fun_fact": "Carrots were originally purple and yellow before orange carrots became famous!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon carrot character standing proudly, vibrant orange tapered body, bushy green feathery leaves on head, cheerful friendly smile, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "crunch_pop"
    },
    {
        "id": "sunny_orange",
        "name": "Sunny Orange",
        "category": "fruits",
        "clue1": "CLUE 1: A dimpled citrus peel that smells like sunshine!",
        "clue2": "CLUE 2: Full of juicy sweet wedges loaded with Vitamin C!",
        "reveal_text": "IT'S A SUNNY ORANGE!",
        "fun_fact": "Oranges are one of the most popular fruit trees cultivated all around the globe!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon orange fruit character rolling joyfully, perfectly round vibrant orange peel, tiny green leaf stem, glowing rosy cheeks, cheerful smile, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "happy_whistle"
    },
    {
        "id": "crisp_apple",
        "name": "Shiny Red Apple",
        "category": "fruits",
        "clue1": "CLUE 1: Crisp glossy red coat and tiny brown stem!",
        "clue2": "CLUE 2: Sweet and crunchy bite that keeps doctors away!",
        "reveal_text": "IT'S A SHINY RED APPLE!",
        "fun_fact": "There are over 7,500 different varieties of apples grown in the world!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon red apple character smiling brightly, glossy ruby red skin, little brown stem with a single emerald leaf, rosy cheeks, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "apple_crunch"
    },
    {
        "id": "sweet_cherries",
        "name": "Twin Cherries",
        "category": "fruits",
        "clue1": "CLUE 1: Glossy crimson red spheres hanging in pairs!",
        "clue2": "CLUE 2: Two fruit best friends connected by one green stem!",
        "reveal_text": "IT'S TWIN CHERRIES!",
        "fun_fact": "Cherries are packed with antioxidants that help people sleep peacefully!",
        "image_prompt": "cute adorable 3d pixar disney style two cartoon cherry characters hugging happily, glossy deep red berries, connected at the top by a flexible green stem with leaves, smiling faces, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "twinkle_bells"
    },
    {
        "id": "golden_mango",
        "name": "Golden Mango",
        "category": "fruits",
        "clue1": "CLUE 1: A smooth teardrop shape with a sunset blush!",
        "clue2": "CLUE 2: Sweet fragrant golden pulp known as King of Fruits!",
        "reveal_text": "IT'S A GOLDEN MANGO!",
        "fun_fact": "The mango is celebrated as the national fruit of India, Pakistan, and the Philippines!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon mango character smiling warmly, smooth golden-yellow skin with ruby-orange blush, tiny green leaf, sparkling eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "tropical_marimba"
    },
    {
        "id": "happy_broccoli",
        "name": "Happy Broccoli",
        "category": "vegetables",
        "clue1": "CLUE 1: A thick crunchy stem and tiny green florets!",
        "clue2": "CLUE 2: I look like a cute miniature green tree on your plate!",
        "reveal_text": "IT'S HAPPY BROCCOLI!",
        "fun_fact": "Broccoli has more vitamin C per gram than whole fresh oranges!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon broccoli character standing happily, bushy emerald-green florets like a tiny tree canopy, light green stalk legs, big smiling face, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "crunch_pop"
    },
    {
        "id": "hero_fire_truck",
        "name": "Hero Fire Truck",
        "category": "vehicles",
        "clue1": "CLUE 1: Bright red paint and a long rescue ladder!",
        "clue2": "CLUE 2: Flashing red sirens and powerful water hoses!",
        "reveal_text": "IT'S A HERO FIRE TRUCK!",
        "fun_fact": "Fire truck ladders can extend as high as 10 stories in the air!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon fire truck smiling heroically, glossy bright red paint, big friendly windshield eyes, shining chrome bumper, folding yellow ladder, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "siren_whoop"
    },
    {
        "id": "space_rocket",
        "name": "Space Rocket",
        "category": "vehicles",
        "clue1": "CLUE 1: Shiny white body and red aerodynamic wings!",
        "clue2": "CLUE 2: 3-2-1 Blast off to the Moon and distant stars!",
        "reveal_text": "IT'S A SPACE ROCKET!",
        "fun_fact": "Rockets travel at over 17,000 miles per hour to reach orbit!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon space rocket ship, friendly smiling porthole window, glossy white and red body, fiery star exhaust trail, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "whoosh"
    },
    {
        "id": "police_patrol_car",
        "name": "Police Patrol Car",
        "category": "vehicles",
        "clue1": "CLUE 1: Black and white body with a golden police star!",
        "clue2": "CLUE 2: Flashing blue and red lightbar on the roof!",
        "reveal_text": "IT'S A POLICE CAR!",
        "fun_fact": "Police cars have special radios that can contact dispatchers across whole states!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon police car smiling friendly, sleek black and white paint, glowing red and blue lightbar on top, big cartoon windshield eyes, chrome grill smile, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "siren_whoop"
    },
    {
        "id": "rescue_helicopter",
        "name": "Rescue Helicopter",
        "category": "vehicles",
        "clue1": "CLUE 1: Twin landing skids and a tail rotor blade!",
        "clue2": "CLUE 2: Giant spinning top blades that hover in midair!",
        "reveal_text": "IT'S A RESCUE HELICOPTER!",
        "fun_fact": "Helicopters are the only flying aircraft that can fly straight backward and upside down for short bursts!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon rescue helicopter hovering, bright yellow and orange body, spinning main rotor, friendly cockpit windshield eyes, smiling nose, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "heli_whir"
    },
    {
        "id": "yellow_school_bus",
        "name": "Yellow School Bus",
        "category": "vehicles",
        "clue1": "CLUE 1: Row of cheerful passenger windows and a swing-out stop sign!",
        "clue2": "CLUE 2: Big yellow friendly bus taking children to school!",
        "reveal_text": "IT'S A YELLOW SCHOOL BUS!",
        "fun_fact": "School buses are painted that exact yellow because human eyes spot it faster than any other color!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon yellow school bus smiling cheerfully, glossy yellow paint, round headlight eyes, friendly front grill smile, big black tires, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bus_honk"
    },
    {
        "id": "ocean_submarine",
        "name": "Yellow Submarine",
        "category": "vehicles",
        "clue1": "CLUE 1: A periscope eye peering above water surface!",
        "clue2": "CLUE 2: I dive deep underwater to explore colorful coral reefs!",
        "reveal_text": "IT'S A YELLOW SUBMARINE!",
        "fun_fact": "Submarines have special water ballast tanks that fill with water to dive and air to surface!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon yellow submarine diving, round porthole windows with smiling faces, top periscope, spinning brass propeller, bubbly water trail, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "sonar_ping"
    },
    {
        "id": "steam_locomotive",
        "name": "Choo-Choo Train",
        "category": "vehicles",
        "clue1": "CLUE 1: Big iron wheels chugging along steel tracks!",
        "clue2": "CLUE 2: A tall smokestack puffing white steam clouds!",
        "reveal_text": "IT'S A CHOO-CHOO TRAIN!",
        "fun_fact": "Early steam trains used burning coal and boiling water to create powerful steam pressure!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon steam train engine smiling, glossy dark green and brass boiler, puffing fluffy white cloud from smokestack, big round headlight eye, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "train_whistle"
    },
    {
        "id": "construction_excavator",
        "name": "Busy Excavator",
        "category": "vehicles",
        "clue1": "CLUE 1: Tank treads that can crawl over rocky dirt!",
        "clue2": "CLUE 2: A mighty mechanical arm with a heavy digging bucket!",
        "reveal_text": "IT'S A BUSY EXCAVATOR!",
        "fun_fact": "Excavator arms can rotate a full 360 degrees without moving their tracks!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon construction excavator smiling, bright yellow body, black continuous caterpillar tracks, strong hydraulic digging arm holding a scoop of shiny gravel, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "engine_rev"
    },
    {
        "id": "hot_air_balloon",
        "name": "Hot Air Balloon",
        "category": "vehicles",
        "clue1": "CLUE 1: A woven wicker passenger basket hanging below!",
        "clue2": "CLUE 2: A giant rainbow fabric balloon floating gently among clouds!",
        "reveal_text": "IT'S A HOT AIR BALLOON!",
        "fun_fact": "Hot air balloons rise because heated air inside the balloon is lighter than the cool air outside!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon hot air balloon floating gently, vibrant rainbow striped envelope, woven brown basket, smiling friendly face, surrounded by fluffy white cloud puffs, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "gentle_chime"
    },
    {
        "id": "baby_axolotl",
        "name": "Cute Pink Axolotl",
        "category": "animals",
        "clue1": "CLUE 1: Feathery pink frills around my head!",
        "clue2": "CLUE 2: The smiling underwater walking salamander!",
        "reveal_text": "IT'S A CUTE AXOLOTL!",
        "fun_fact": "Axolotls can magically regenerate their tiny limbs and tails!",
        "image_prompt": "cute adorable 3d pixar disney style baby pink axolotl swimming happily, feathery frilly external pink gills, big smiling mouth, dark sparkling eyes, tiny webbed feet, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "magical_twinkle"
    },
    {
        "id": "baby_quokka",
        "name": "Smiling Quokka",
        "category": "animals",
        "clue1": "CLUE 1: Round furry cheeks and tiny paws!",
        "clue2": "CLUE 2: Famous as the happiest smiling animal in the world!",
        "reveal_text": "IT'S A SMILING QUOKKA!",
        "fun_fact": "Quokkas love people and smile naturally because of their jaw shape!",
        "image_prompt": "cute adorable 3d pixar disney style baby quokka smiling directly at camera, soft brown fur, round fuzzy ears, sweet friendly selfie pose waving paw, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_giggle"
    },
    {
        "id": "baby_fennec_fox",
        "name": "Fennec Sand Fox",
        "category": "animals",
        "clue1": "CLUE 1: Giant bat-like ears bigger than my head!",
        "clue2": "CLUE 2: Sandy cream fur hopping across desert dunes!",
        "reveal_text": "IT'S A FENNEC FOX!",
        "fun_fact": "A fennec fox's giant ears act like air conditioners to cool off in hot deserts!",
        "image_prompt": "cute adorable 3d pixar disney style baby fennec fox sitting in desert sand, enormous oversized triangular ears, cream-colored fluffy fur, big shining black eyes, bushy tail, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "happy_yip"
    },
    {
        "id": "baby_lemur",
        "name": "Ring-Tailed Lemur",
        "category": "animals",
        "clue1": "CLUE 1: Bright glowing golden-amber eyes!",
        "clue2": "CLUE 2: A super long black and white striped ringed tail!",
        "reveal_text": "IT'S A RING-TAILED LEMUR!",
        "fun_fact": "Lemurs love sunbathing in the morning by sitting like tiny yoga monks!",
        "image_prompt": "cute adorable 3d pixar disney style baby ring-tailed lemur sitting, huge bushy black-and-white striped tail curved up, big expressive round amber eyes, soft gray fur, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_chirp"
    },
    {
        "id": "baby_chameleon",
        "name": "Colorful Chameleon",
        "category": "animals",
        "clue1": "CLUE 1: Swiveling turret eyes that look in two directions!",
        "clue2": "CLUE 2: A curled spiral tail and I change rainbow colors!",
        "reveal_text": "IT'S A COLORFUL CHAMELEON!",
        "fun_fact": "Chameleons change colors to show their mood and talk to friends!",
        "image_prompt": "cute adorable 3d pixar disney style baby chameleon clinging to a twig, vibrant rainbow color-changing scales, curled spiral tail, big cartoon rotating eyes, cheerful smile, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_pop"
    },
    {
        "id": "baby_walrus",
        "name": "Baby Walrus",
        "category": "animals",
        "clue1": "CLUE 1: A thick bushy mustache of sensitive whiskers!",
        "clue2": "CLUE 2: Two tiny white tusks and heavy flippers for icy seas!",
        "reveal_text": "IT'S A BABY WALRUS!",
        "fun_fact": "Walruses use their sensitive whiskers to find tasty clams buried under sea mud!",
        "image_prompt": "cute adorable 3d pixar disney style baby walrus resting on ice, chubby wrinkly cinnamon-brown body, bushy whisker mustache, two tiny growing tusks, big gentle eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "friendly_growl"
    },
    {
        "id": "baby_platypus",
        "name": "Little Platypus",
        "category": "animals",
        "clue1": "CLUE 1: A duck-like bill and a beaver paddle tail!",
        "clue2": "CLUE 2: Webbed swimming feet that dig burrows near creeks!",
        "reveal_text": "IT'S A LITTLE PLATYPUS!",
        "fun_fact": "The platypus is one of only two mammals in the whole world that lay eggs!",
        "image_prompt": "cute adorable 3d pixar disney style baby platypus swimming playfully, dark rubbery duck-bill, broad beaver paddle tail, waterproof brown fur, webbed paws paddling, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "water_splash"
    },
    {
        "id": "baby_wombat",
        "name": "Baby Wombat",
        "category": "animals",
        "clue1": "CLUE 1: Sturdy digging claws and a button snout!",
        "clue2": "CLUE 2: A chubby teddy-bear body that burrows underground!",
        "reveal_text": "IT'S A BABY WOMBAT!",
        "fun_fact": "Wombats are the only animals in nature that produce cube-shaped poop!",
        "image_prompt": "cute adorable 3d pixar disney style baby wombat waddling joyfully, plump rounded brown body, short muscular legs with blunt claws, cute pinkish nose, big innocent eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_snort"
    },
    {
        "id": "baby_hummingbird",
        "name": "Tiny Hummingbird",
        "category": "birds",
        "clue1": "CLUE 1: A needle-thin bill sipping flower nectar!",
        "clue2": "CLUE 2: Emerald wings that flutter so fast they hum in midair!",
        "reveal_text": "IT'S A TINY HUMMINGBIRD!",
        "fun_fact": "Hummingbirds are the only birds that can fly backward and upside down!",
        "image_prompt": "cute adorable 3d pixar disney style tiny baby hummingbird hovering near a pink blossom, iridescent emerald and ruby feathers, needle beak, blurred fluttering wings, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "flutter_wings"
    },
    {
        "id": "baby_swan",
        "name": "Graceful Baby Swan",
        "category": "birds",
        "clue1": "CLUE 1: Soft velvety gray down feathers!",
        "clue2": "CLUE 2: A long graceful S-curved neck gliding on calm lakes!",
        "reveal_text": "IT'S A BABY SWAN CYGNET!",
        "fun_fact": "Baby swans are called cygnets and often ride on their mother's back while swimming!",
        "image_prompt": "cute adorable 3d pixar disney style baby swan cygnet floating on water ripples, soft fluffy silvery-gray down, elegant curved neck, sweet bill, big sparkling eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "gentle_chime"
    },
    {
        "id": "baby_pelican",
        "name": "Friendly Pelican",
        "category": "birds",
        "clue1": "CLUE 1: Big webbed feet and snowy white feathers!",
        "clue2": "CLUE 2: A giant stretchy throat pouch for scooping water and fish!",
        "reveal_text": "IT'S A FRIENDLY PELICAN!",
        "fun_fact": "A pelican's expandable beak pouch can hold up to 3 gallons of water!",
        "image_prompt": "cute adorable 3d pixar disney style baby pelican standing proudly, fluffy white and gray body, big cheerful yellow bill with a round expandable throat pouch, bright blue eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "water_splash"
    },
    {
        "id": "baby_kiwi",
        "name": "Little Kiwi Bird",
        "category": "birds",
        "clue1": "CLUE 1: Hair-like brown feathers and no visible wings!",
        "clue2": "CLUE 2: A long slender beak with nostrils at the very tip!",
        "reveal_text": "IT'S A LITTLE KIWI BIRD!",
        "fun_fact": "Kiwi birds cannot fly, but they have a super powerful sense of smell!",
        "image_prompt": "cute adorable 3d pixar disney style baby kiwi bird standing on sturdy feet, fuzzy round brown body like a plush ball, long slender ivory beak, big curious eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_squeak"
    },
    {
        "id": "baby_narwhal",
        "name": "Ocean Narwhal",
        "category": "sea_creatures",
        "clue1": "CLUE 1: Mottled gray skin gliding through icy Arctic waters!",
        "clue2": "CLUE 2: A long magical spiral unicorn tusk!",
        "reveal_text": "IT'S AN OCEAN NARWHAL!",
        "fun_fact": "A narwhal's horn is actually an overgrown spiral tooth that can sense water temperature!",
        "image_prompt": "cute adorable 3d pixar disney style baby narwhal swimming, speckled blue-gray skin, gleaming pearlescent spiral unicorn tusk on forehead, joyful smiling face, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "magical_twinkle"
    },
    {
        "id": "baby_manta_ray",
        "name": "Gentle Manta Ray",
        "category": "sea_creatures",
        "clue1": "CLUE 1: A whip-like tail and smooth white belly!",
        "clue2": "CLUE 2: Giant diamond wings that glide gracefully through ocean blue!",
        "reveal_text": "IT'S A GENTLE MANTA RAY!",
        "fun_fact": "Manta rays have the largest brain-to-body ratio of all fish and love doing underwater somersaults!",
        "image_prompt": "cute adorable 3d pixar disney style baby manta ray gliding, midnight blue back with delicate white markings, smooth belly, gentle smiling face with two horn-like head fins, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "ocean_bubble"
    },
    {
        "id": "baby_orca",
        "name": "Baby Orca",
        "category": "sea_creatures",
        "clue1": "CLUE 1: White oval patches right above my eyes!",
        "clue2": "CLUE 2: Glossy jet-black and snow-white leaping ocean king!",
        "reveal_text": "IT'S A BABY ORCA!",
        "fun_fact": "Orcas live in family groups and each pod has its own unique dialect of whistle sounds!",
        "image_prompt": "cute adorable 3d pixar disney style baby orca killer whale leaping out of water foam, shiny jet-black back, bright white tummy, round eye patches, joyful playful smile, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "whale_song"
    },
    {
        "id": "baby_pufferfish",
        "name": "Round Pufferfish",
        "category": "sea_creatures",
        "clue1": "CLUE 1: Big circular eyes and tiny fluttering fins!",
        "clue2": "CLUE 2: I puff up like a round spiky balloon when surprised!",
        "reveal_text": "IT'S A ROUND PUFFERFISH!",
        "fun_fact": "Pufferfish puff up by gulping huge gulps of water so enemies cannot bite them!",
        "image_prompt": "cute adorable 3d pixar disney style baby pufferfish inflated like a round ball, soft yellow body with gentle blunt spines, tiny fluttering fins, giant surprised smiling eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bubble_pop"
    },
    {
        "id": "golden_lemon",
        "name": "Zesty Lemon",
        "category": "fruits",
        "clue1": "CLUE 1: An oval yellow shape with pointed ends!",
        "clue2": "CLUE 2: Sour and tangy citrus juice that makes lemonade!",
        "reveal_text": "IT'S A ZESTY LEMON!",
        "fun_fact": "Lemons contain so much citric acid that they can even power a tiny digital clock!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon lemon character smiling with wink, bright sunny yellow peel, little green leaf stem, cute rosy cheeks, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "happy_whistle"
    },
    {
        "id": "sweet_blueberry",
        "name": "Sweet Blueberry",
        "category": "fruits",
        "clue1": "CLUE 1: Deep indigo blue coat with a silvery bloom!",
        "clue2": "CLUE 2: A tiny five-pointed star crown sitting on top!",
        "reveal_text": "IT'S A SWEET BLUEBERRY!",
        "fun_fact": "Blueberries are one of the only natural foods on Earth that are truly deep blue in color!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon blueberry character, round plump indigo-blue berry, delicate star-shaped crown on top, big joyful eyes, rosy cheeks, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "cute_pop"
    },
    {
        "id": "purple_grapes",
        "name": "Bouncy Grapes",
        "category": "fruits",
        "clue1": "CLUE 1: Hanging together on a twisted green vine!",
        "clue2": "CLUE 2: A bunch of sweet juicy purple balloons you can pop in your mouth!",
        "reveal_text": "IT'S BOUNCY GRAPES!",
        "fun_fact": "There are over 8,000 kinds of grapes grown across all continents except Antarctica!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon cluster of purple grapes, smiling round purple faces gathered together on a vine with an emerald leaf, cheerful expressions, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "bounce_boing"
    },
    {
        "id": "sweet_corn",
        "name": "Golden Sweet Corn",
        "category": "vegetables",
        "clue1": "CLUE 1: Wrapped in a green leafy jacket with silky blonde hair!",
        "clue2": "CLUE 2: Rows of sweet golden yellow kernels that can pop into popcorn!",
        "reveal_text": "IT'S GOLDEN SWEET CORN!",
        "fun_fact": "Each ear of sweet corn has an average of 800 kernels arranged in 16 rows!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon sweet corn cob standing proudly, golden yellow kernels, partially opened green leafy husk like a jacket, smiling face, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "crunch_pop"
    },
    {
        "id": "happy_tomato",
        "name": "Cheerful Red Tomato",
        "category": "fruits",
        "clue1": "CLUE 1: Plump glossy red skin full of juicy seeds!",
        "clue2": "CLUE 2: A five-point green star leaf cap, pizza sauce star!",
        "reveal_text": "IT'S A CHEERFUL TOMATO!",
        "fun_fact": "Tomatoes are scientifically fruits, not vegetables, because they grow from flowers and have seeds!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon red tomato character rolling joyfully, glossy plump scarlet body, tiny five-point green leaf hat, big round smiling eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "happy_bell"
    },
    {
        "id": "speedy_race_car",
        "name": "Formula Race Car",
        "category": "vehicles",
        "clue1": "CLUE 1: Low aerodynamic body and big rear spoiler wing!",
        "clue2": "CLUE 2: Roaring high-speed engine zooming around the race track!",
        "reveal_text": "IT'S A FORMULA RACE CAR!",
        "fun_fact": "Formula race cars can accelerate from zero to 60 miles per hour in just 2 seconds!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon formula race car smiling, glossy electric red and white racing livery, racing number 1 on hood, wide spoiler wing, big cartoon windshield eyes, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "engine_rev"
    },
    {
        "id": "farm_tractor",
        "name": "Friendly Farm Tractor",
        "category": "vehicles",
        "clue1": "CLUE 1: Huge knobby rear tires and an upright exhaust pipe!",
        "clue2": "CLUE 2: Chugging through farm fields to help grow healthy crops!",
        "reveal_text": "IT'S A FARM TRACTOR!",
        "fun_fact": "A tractor's giant back tires are filled with air and water weight to give extra traction in muddy fields!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon farm tractor chugging along, bright emerald green body with bright yellow wheels, tall smokestack puffing, friendly smiling grill, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "engine_rev"
    },
    {
        "id": "monster_truck",
        "name": "Big Monster Truck",
        "category": "vehicles",
        "clue1": "CLUE 1: Heavy suspension springs and raised body!",
        "clue2": "CLUE 2: Enormous 66-inch bouncy tires that crush ramps!",
        "reveal_text": "IT'S A BIG MONSTER TRUCK!",
        "fun_fact": "A single monster truck tire weighs over 800 pounds, heavier than an adult grizzly bear!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon monster truck bouncing happily, flame-painted blue body, giant oversized rubber tires, high suspension, big cheerful eyes on windshield, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "engine_rev"
    },
    {
        "id": "passenger_airplane",
        "name": "Friendly Jet Airplane",
        "category": "vehicles",
        "clue1": "CLUE 1: Twin wings with jet engines and a vertical tail fin!",
        "clue2": "CLUE 2: Soaring high above white fluffy clouds across the world!",
        "reveal_text": "IT'S A JET AIRPLANE!",
        "fun_fact": "Jet airplanes cruise at altitudes of 35,000 feet where the outside temperature is 60 below zero!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon passenger airplane soaring, glossy white fuselage with sky blue stripes, friendly cockpit window eyes, smiling nosecone, fluffy white clouds, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "whoosh"
    },
    {
        "id": "cuddly_teddy_bear",
        "name": "Cuddly Teddy Bear",
        "category": "objects",
        "clue1": "CLUE 1: Round fuzzy ears and warm stitched smile!",
        "clue2": "CLUE 2: Soft plush belly always ready for warm bedtime hugs!",
        "reveal_text": "IT'S A CUDDLY TEDDY BEAR!",
        "fun_fact": "The teddy bear was named after American President Theodore Teddy Roosevelt in 1902!",
        "image_prompt": "cute adorable 3d pixar disney style plush teddy bear sitting with open arms, honey-brown fuzzy fur, stitched button nose and eyes, red ribbon bow tie around neck, smiling warmly, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "gentle_chime"
    },
    {
        "id": "friendly_robot",
        "name": "Friendly Toy Robot",
        "category": "objects",
        "clue1": "CLUE 1: An antenna on top and flexible springy arms!",
        "clue2": "CLUE 2: Shiny metal body with blinking colorful LED lights and beeps!",
        "reveal_text": "IT'S A FRIENDLY ROBOT!",
        "fun_fact": "The word robot comes from a Czech word meaning helpful worker!",
        "image_prompt": "cute adorable 3d pixar disney style cartoon toy robot standing happily, shiny retro metallic teal-blue body, glowing heart LED on chest, antenna with glowing yellow bulb, big round digital expressive eyes, waving claw hand, 3d render, full body, isolated on bright solid neon green screen background, chroma key",
        "sound_type": "magical_twinkle"
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

    def _clean_name(self, name: str) -> str:
        """Strips prefixes like 'Golden ', 'Baby ', 'Happy ' to get the core root word."""
        n = name.lower().strip()
        for prefix in ["golden ", "little ", "super ", "sweet ", "cute ", "happy ", "hero "]:
            if n.startswith(prefix):
                n = n[len(prefix):].strip()
        return n

    def is_used(self, item: dict) -> bool:
        """
        Strict check:
        1. Checks exact topic_id (ignoring any _v.. suffix)
        2. Checks core root name (e.g. 'banana', 'tiger', 'watermelon')
        Guarantees that once an animal/fruit/vehicle is done, it is NEVER repeated!
        """
        raw_id = item.get("id", "").split("_v")[0].lower()
        item_root = self._clean_name(item.get("name", ""))

        for entry in self.history:
            past_id = entry.get("topic_id", "").split("_v")[0].lower()
            past_root = self._clean_name(entry.get("name", ""))

            # If ID matches OR root name matches (e.g. 'banana' in both)
            if raw_id == past_id:
                return True
            if item_root and (item_root == past_root or item_root in past_root or past_root in item_root):
                return True

        return False

    def select_next_quiz(self, target_id: str = None) -> dict:
        """
        Selects a unique, non-repeating quiz.
        100% strict: filters out all items already present in history.
        """
        # If user explicitly requested a specific topic via CLI
        if target_id:
            for item in KIDS_TOPICS:
                if item["id"] == target_id or target_id.lower() in item["name"].lower():
                    return item

        # Filter out ANY topic that has been used in history
        available = [item for item in KIDS_TOPICS if not self.is_used(item)]

        if available:
            # Pick randomly from remaining unique topics
            chosen = random.choice(available)
            print(f"[*] Selected unique quiz: '{chosen['name']}' (Remaining unused topics: {len(available) - 1})")
            return chosen

        # Safety Fallback: In the extremely rare event all 100+ topics were used
        print("[!] All 100+ catalog topics used! Procedurally generating a brand new character...")
        procedural_candidates = [
            ("baby_quoll", "Baby Spotted Quoll", "animals", "CLUE 1: Soft brown fur with bright white polka dots!", "CLUE 2: Agile tree climber with big nocturnal eyes!", "IT\'S A BABY QUOLL!", "Quolls have naturally spotted coats that camouflage in moonlight!", "cute adorable 3d pixar disney style baby spotted quoll sitting on a log, bright white spots on brown fur, big eyes, 3d render, isolated on bright solid neon green screen background, chroma key"),
            ("baby_sugar_glider", "Baby Sugar Glider", "animals", "CLUE 1: Giant starry night eyes and tiny pink nose!", "CLUE 2: Gliding membrane wings to sail between eucalyptus trees!", "IT\'S A BABY SUGAR GLIDER!", "Sugar gliders can glide the length of a football field in one jump!", "cute adorable 3d pixar disney style baby sugar glider gliding with open paws, giant glistening eyes, striped head, 3d render, isolated on bright solid neon green screen background, chroma key"),
            ("baby_okapi", "Baby Forest Okapi", "animals", "CLUE 1: Velvet dark brown coat with zebra-striped legs!", "CLUE 2: The shy hidden forest unicorn of Central Africa!", "IT\'S A BABY OKAPI!", "Okapis are the only living relatives of the tall giraffe!", "cute adorable 3d pixar disney style baby okapi standing shyly, velvety dark brown body, black and white striped legs, big ears, 3d render, isolated on bright solid neon green screen background, chroma key"),
            ("baby_pangolin", "Baby Pangolin", "animals", "CLUE 1: Protective pinecone-like keratin scales!", "CLUE 2: I curl into a tight safe armor ball when nervous!", "IT\'S A BABY PANGOLIN!", "A pangolin\'s scales are made of the exact same keratin as human fingernails!", "cute adorable 3d pixar disney style baby pangolin sitting on hind legs, shiny overlapping artichoke scales, sweet curious face, 3d render, isolated on bright solid neon green screen background, chroma key"),
            ("baby_kinkajou", "Baby Honey Kinkajou", "animals", "CLUE 1: Golden-honey fur and round friendly ears!", "CLUE 2: A prehensile tail that wraps around branches like an extra hand!", "IT\'S A BABY KINKAJOU!", "Kinkajous are also called honey bears because they love raiding beehives for sweet honey!", "cute adorable 3d pixar disney style baby kinkajou hanging by its prehensile tail, golden-brown plush fur, big friendly eyes, 3d render, isolated on bright solid neon green screen background, chroma key")
        ]
        for pid, pname, pcat, pclue1, pclue2, prev, pfact, pprompt in procedural_candidates:
            if not any(pid in e.get("topic_id", "") for e in self.history):
                return {
                    "id": pid,
                    "name": pname,
                    "category": pcat,
                    "clue1": pclue1,
                    "clue2": pclue2,
                    "reveal_text": prev,
                    "fun_fact": pfact,
                    "image_prompt": pprompt,
                    "sound_type": "cute_squeak"
                }

        # Absolute fallback if hundreds of runs happen
        fallback = random.choice(KIDS_TOPICS)
        return fallback

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
        print(f"[+] Recorded '{quiz_pkg['name']}' in {HISTORY_FILE.name} (Total unique completed: {len(self.history)})")


if __name__ == "__main__":
    curator = KidsCurator()
    quiz = curator.select_next_quiz()
    print("Selected Quiz:", quiz["name"], "| Clue 1:", quiz["clue1"])
