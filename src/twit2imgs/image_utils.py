from PIL import Image, ImageDraw, ImageFont
import re
import string, random

def beautiful_s2_to_16_9_labelled(
    im: Image, 
    txt:str
) -> Image:
    
    AR = 9/16
    width, height = im.size
    bottom = round((height + AR*height)/2)
    top = round((height - AR*height)/2)
    left=0
    right=width
    pix_per_char = 12

    im = im.crop((left, top, right, bottom))

    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 20, encoding="unic")

    match_date = re.search("\d\d\s\D\D\D\s\d\d\d\d", txt)
    match_latlon = re.search("\(.*\)",txt)

    top_line = txt[:match_latlon.start()]
    bottom_line = txt[match_latlon.start():match_date.end()].replace(',','')

    left_align = im.width - int(max(len(top_line), len(bottom_line))*pix_per_char) - 10

    draw = ImageDraw.Draw(im, 'RGBA')
    draw.rounded_rectangle((left_align-25, 1155, 2300, 1300), fill=(255,255,255,130), outline=None,  width=3, radius=20)

    top_row_anchor = (left_align,1170)
    bottom_row_anchor = (left_align,1200)

    draw.text(top_row_anchor,top_line,(255,255,255,128), font=font)
    draw.text(bottom_row_anchor,bottom_line,(255,255,255,128), font=font)
    
    return im