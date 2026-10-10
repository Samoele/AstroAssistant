import os
import math
from PIL import Image

INPUT_IMAGE = "Penguin_Sprite.jpg"
OUTPUT_IMAGE = "../frontend/public/sprites/penguin-sprites.png"
COLS = 4
ROWS = 6
CELL_SIZE = 64

# Target pure magenta: (255, 0, 255)
KEY_R, KEY_G, KEY_B = 255, 0, 255
THRESHOLD = 85.0  # Catch subtle pink/magenta edge pixels

def process_sprite_sheet():
    if not os.path.exists(INPUT_IMAGE):
        print(f"Cannot find {INPUT_IMAGE}")
        return

    img = Image.open(INPUT_IMAGE).convert("RGBA")
    target_width = COLS * CELL_SIZE
    target_height = ROWS * CELL_SIZE
    img = img.resize((target_width, target_height), Image.Resampling.NEAREST)

    pixels = img.getdata()
    cleaned = []

    for r, g, b, a in pixels:
        # Distance from pure magenta in 3D color space
        dist = math.sqrt((r - KEY_R) ** 2 + (g - KEY_G) ** 2 + (b - KEY_B) ** 2)
        if dist < THRESHOLD or (r > 160 and b > 160 and g < 110):
            cleaned.append((0, 0, 0, 0))
        else:
            cleaned.append((r, g, b, a))

    img.putdata(cleaned)
    os.makedirs(os.path.dirname(OUTPUT_IMAGE), exist_ok=True)
    img.save(OUTPUT_IMAGE, "PNG")
    print(f"Cleaned magenta fringe: saved to {OUTPUT_IMAGE}")

if __name__ == "__main__":
    process_sprite_sheet()