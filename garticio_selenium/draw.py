from PIL import Image, ImageFilter
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from pynput.mouse import Button, Controller as MouseController
from selenium.webdriver.common.by import By
import numpy as np
import time


# Colors available in gartic.io (RGB)
COLORS = [
    (0, 0, 0),
    (102, 102, 102),
    (0, 23, 246),
    (255, 255, 255),
    (170, 170, 170),
    (38, 201, 255),
    (0, 141, 38),
    (169, 35, 12),
    (150, 65, 18),
    (0, 255, 77),
    (255, 0, 19),
    (255, 120, 41),
    (176, 112, 28),
    (153, 0, 78),
    (147, 104, 103),
    (255, 201, 38),
    (255, 0, 143),
    (254, 175, 168),
    # gartic.io doesn't display these colors.
    # thus, user cannot even click these
    # (0, 217, 163),
    # (133, 178, 0),
    # (128, 0, 255),
    # (5, 44, 108),
    # (185, 115, 255),
    # (255, 247, 63),
]


def color_diff(rgb1, rgb2):
    """計算CIE2000色差"""
    color1_rgb = sRGBColor(*rgb1, is_upscaled=True)
    color2_rgb = sRGBColor(*rgb2, is_upscaled=True)
    color1_lab = convert_color(color1_rgb, LabColor)
    color2_lab = convert_color(color2_rgb, LabColor)
    delta_e = delta_e_cie2000(color1_lab, color2_lab)
    return delta_e


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


def process_img(im, basewidth=200, baseheight=116):
    if im.size[0] / im.size[1] > 815 / 475:
        im = resize_based_on_width(im, basewidth)
    else:
        im = resize_based_on_height(im, baseheight)

    # change transparent image background to white color
    is_transparency = "A" in im.getbands()
    if is_transparency:
        new_img = Image.new("RGB", im.size, (255, 255, 255))
        new_img.paste(im, mask=im.split()[3])
        im = new_img

    im = im.filter(ImageFilter.MedianFilter(size=1))
    im = im.convert("RGB")
    im = im.quantize(24)
    im = im.convert("RGB")
    a = np.asarray(im)
    return a, im.size


def compute_line(a):
    """1 image row to line"""
    line = []
    start = 0
    color_id_map = {}
    # convert each continuous color into 'start', 'end', 'color_id' dict
    for i in range(len(a) - 1):
        if (a[i] != a[i + 1]).all():
            end = i

            min_color_id = None
            color_key = tuple(a[i])
            color_already_cached = color_key in color_id_map
            if color_already_cached:
                min_color_id = color_id_map[color_key]
            else:
                # find the closest color in COLORS
                for j in range(len(COLORS)):
                    delta = color_diff(a[i], COLORS[j])
                    if min_color_id is None:
                        min_color_id = j
                        min_delta = delta
                    else:
                        if delta < min_delta:
                            min_color_id = j
                            min_delta = delta

                color_id_map[color_key] = min_color_id

            # actually, I don't know what 3 means
            color_not_white = min_color_id != 3
            if color_not_white:
                seg = {"start": start, "end": end, "color_id": min_color_id}
                line.append(seg)
            # next
            start = i + 1

    return line


def get_color_elems(driver):
    color_elem_map = {}
    for i in range(len(COLORS)):
        color_elem_map[i] = driver.find_element(
            By.XPATH,
            f"/html/body/div[2]/div/div[2]/div[1]/div/div/div[1]/div[2]/div/div[2]/div[1]/div[{i+1}]",
        )
    return color_elem_map


def draw_by_color(driver, lines, xoffset=10, yoffset=10, gap=1, line_height=None):
    if line_height is None:
        line_height = gap

    color_map = {}
    for y, line in enumerate(lines):
        for seg in line:
            seg["y"] = y
            if seg["color_id"] not in color_map:
                color_map[seg["color_id"]] = [seg]
            else:
                color_map[seg["color_id"]] += [seg]

    mouse = MouseController()
    color_elem_map = get_color_elems(driver)
    for color_id, color_line in color_map.items():
        color_elem_map[color_id].click()
        for seg in color_line:
            mouse.position = (
                xoffset + seg["start"] * gap,
                yoffset + seg["y"] * line_height,
            )

            if seg["start"] == seg["end"]:
                mouse.click(Button.left)
            else:
                mouse.press(Button.left)
                # time.sleep(0.005)
                mouse.move((seg["end"] - seg["start"]) * gap, 0)
                time.sleep(0.0001)
                mouse.release(Button.left)
