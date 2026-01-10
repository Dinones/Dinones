###########################################################################################################################
# Generate a transparent PNG skills banner from local PNG icons.                                                          #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

import os
import math
from typing import List
from PIL import Image, ImageDraw, ImageFont

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

# Directory with source PNG icons and output path for the banner
PNG_DIR = "png"
OUT_PATH = os.path.join(".", "Skills.png")

# Display label and filename pairs in the desired order
FILES = [
    ("Python", "Python.png"),
    ("Google Cloud", "Google Cloud.png"),
    ("Git", "Git.png"),
    ("Linux", "Linux.png"),
    ("Flask", "Flask.png"),
    ("OpenCV", "Opencv.png"),
    ("PyQt", "PyQt.png"),
    ("LaTeX", "Latex.png"),
    ("Raspberry Pi", "Raspberry Pi.png"),
    ("Arduino", "Arduino.png"),
]

# Grid layout and typography
COLUMNS = 10
ICON_SIZE = 56
PADDING_X = 1
PADDING_Y = 18
LABEL_GAP = 10
FONT_SIZE = 16
TEXT_COLOR_WHITE = (255, 255, 255, 255)
TEXT_COLOR_BLACK = (0, 0, 0, 255)
OVERSAMPLE = 2

# Trim transparent padding before scaling to reduce dead space
TRIM_TRANSPARENT = True

###########################################################################################################################
###########################################################################################################################

def load_font(size: int) -> ImageFont.ImageFont:

    """
    Load a usable system font.

    Args:
        size: Font size in pixels.

    Returns:
        A PIL ImageFont instance, falling back to the PIL default font.
    """

    for name in ["segoeui.ttf", "Arial.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, size=size)
        except Exception:
            continue
    return ImageFont.load_default()

###########################################################################################################################
###########################################################################################################################

def trim_transparent(im: Image.Image) -> Image.Image:

    """
    Trim fully transparent borders from an RGBA image.

    Args:
        im: Input image.

    Returns:
        Cropped image; if fully transparent, returns the original.
    """

    if im.mode != "RGBA":
        im = im.convert("RGBA")
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im

###########################################################################################################################
###########################################################################################################################

def fit_center(im: Image.Image, size: int) -> Image.Image:

    """
    Scale down to fit and center the icon in a size x size RGBA tile.

    Args:
        im: Input image.
        size: Output tile size in pixels.

    Returns:
        A size x size RGBA image with the icon centered.
    """

    im = im.convert("RGBA")
    if TRIM_TRANSPARENT:
        im = trim_transparent(im)

    # Reserved for potential higher-res rendering before downsampling
    target = size * OVERSAMPLE

    w, h = im.size
    if w == 0 or h == 0:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # Never upscale; keep small icons crisp rather than blurry
    scale = min(1.0, size / w, size / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    im = im.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - nw) // 2
    y = (size - nh) // 2
    canvas.alpha_composite(im, (x, y))
    return canvas

###########################################################################################################################
###########################################################################################################################

def main(text_color: List[int], file_name: str) -> None:

    """
    Build the banner and write it to disk.

    Args:
        text_color (List[int]): Color value in format [R, G, B, A]. 
        file_name (str): Outpute file name.

    Returns:
        None.
    """

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    # Load and normalize all icons
    font = load_font(FONT_SIZE)
    items = []
    for label, fname in FILES:
        path = os.path.join(PNG_DIR, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing file: {path}")
        im = Image.open(path).convert("RGBA")
        im = fit_center(im, ICON_SIZE)
        items.append((label, im))

    # Determine grid size
    n = len(items)
    cols = min(COLUMNS, n)
    rows = math.ceil(n / cols)

    # Measure maximum label size to keep cells consistent
    tmp = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    max_text_w = 0
    text_h = 0
    for label, _ in items:
        bbox = d.textbbox((0, 0), label, font=font)
        max_text_w = max(max_text_w, bbox[2] - bbox[0])
        text_h = max(text_h, bbox[3] - bbox[1])

    # Compute the final canvas size
    cell_w = max(ICON_SIZE, max_text_w) + PADDING_X
    cell_h = ICON_SIZE + LABEL_GAP + text_h + PADDING_Y
    width = cell_w * cols + PADDING_X
    height = cell_h * rows + PADDING_Y

    # Compose icons and labels into a transparent canvas
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    for i, (label, icon) in enumerate(items):
        r = i // cols
        c = i % cols

        x0 = PADDING_X + c * cell_w
        y0 = PADDING_Y + r * cell_h

        icon_x = x0 + (cell_w - PADDING_X - ICON_SIZE) // 2
        icon_y = y0
        canvas.alpha_composite(icon, (icon_x, icon_y))

        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        text_x = x0 + (cell_w - PADDING_X - tw) // 2
        text_y = icon_y + ICON_SIZE + LABEL_GAP
        draw.text((text_x, text_y), label, font=font, fill=text_color)

    # Save the image
    canvas.save(file_name)
    print(f"Saved: {file_name}  ({width}x{height})")

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    main(TEXT_COLOR_BLACK, 'Skills Black.png')
    main(TEXT_COLOR_WHITE, 'Skills White.png')
