import os
import re

from PIL import Image, ImageDraw, ImageFont


def beautiful_s2_to_16_9_labelled(im: Image, txt: str) -> Image:
    AR = 9 / 16
    width, height = im.size
    bottom = round((height + AR * height) / 2)
    top = round((height - AR * height) / 2)
    left = 0
    right = width
    pix_per_char = 12

    # crop the image to aspect ratio, AR
    im = im.crop((left, top, right, bottom))

    # extract latlon and date strings using regex
    match_date = re.search(r"\d\d\s\D\D\D\s\d\d\d\d", txt)
    match_latlon = re.search(r"\(.*\)", txt)

    top_line = txt[: match_latlon.start()]
    bottom_line = txt[match_latlon.start() : match_date.end()].replace(",", "")  # noqa

    # draw a semi-opaque box to hold our annotations.
    # set the width of the box based on the length of our text annotations.
    left_align = (
        im.width - int(max(len(top_line), len(bottom_line)) * pix_per_char) - 10
    )

    draw = ImageDraw.Draw(im, "RGBA")
    draw.rounded_rectangle(
        (left_align - 25, 1155, 2300, 1300),
        fill=(255, 255, 255, 176),
        outline=None,
        width=3,
        radius=20,
    )

    top_row_anchor = (left_align, 1170)
    bottom_row_anchor = (left_align, 1200)

    # finally, add our text annotations
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 20, encoding="unic"
    )
    draw.text(top_row_anchor, top_line, (120, 120, 120, 196), font=font)
    draw.text(bottom_row_anchor, bottom_line, (120, 120, 120, 196), font=font)

    return im


def format_s2_url(url: str) -> str:
    base, ext = os.path.splitext(url)
    return base + "?format=jpg&name=4096x4096"


def null_url_parser(url: str) -> str:
    return url
