from PIL import Image, ImageFilter
import numpy as np


def resize_based_on_width(im, basewidth):
    """以basewidth為基準，縮放圖片"""
    wpercent = basewidth / float(im.size[0])
    hsize = int((float(im.size[1]) * float(wpercent)))
    im = im.resize((basewidth, hsize), Image.Resampling.LANCZOS)
    return im


def resize_based_on_height(im, baseheight):
    """以baseheight為基準，縮放圖片"""
    hpercent = baseheight / float(im.size[1])
    wsize = int((float(im.size[0]) * float(hpercent)))
    im = im.resize((wsize, baseheight), Image.Resampling.LANCZOS)
    return im


def process_img(im, basewidth, baseheight):
    if im.size[0] / im.size[1] > 815 / 475:
        im = resize_based_on_width(im, basewidth)
    else:
        im = resize_based_on_height(im, baseheight)

    # change transparent image background to white color
    is_transparency = "A" in im.getbands()
    if is_transparency:
        white = (255, 255, 255)
        new_img = Image.new("RGB", im.size, white)
        new_img.paste(im, mask=im.split()[3])
        im = new_img

    # simplify the image
    im = im.convert("RGB")
    im = im.quantize(colors=16)
    im = im.convert("RGB")
    im = im.filter(ImageFilter.MedianFilter(size=3))
    img_arr = np.asarray(im)
    return img_arr, im.size


def is_close_to_white(color, threshold=70):
    """
    Determines if a color is close to white in the RGB color space.
    color: a tuple of RGB values (red, green, blue) in the range [0, 255].
    threshold: the maximum distance from pure white to consider a color close to white.
    """
    white = (255, 255, 255)
    distance = sum([(color[i] - white[i]) ** 2 for i in range(3)])
    return distance <= threshold**2


def to_hex(rgb):
    hex_color = "#" + "".join([hex(x)[2:].zfill(2) for x in rgb])
    return hex_color


def compute_line(img_row):
    """1 image row to line"""
    line = []
    start = 0
    # convert each continuous color into 'start', 'end', 'hex_color' dict
    for i in range(len(img_row)):
        if i == len(img_row) - 1 or not (img_row[i] == img_row[i + 1]).all():
            end = i
            rgb = tuple(img_row[i])
            if not is_close_to_white(rgb):
                hex_color = to_hex(rgb)
                line.append({"start": start, "end": end, "hex_color": hex_color})
            start = i + 1

    return line
