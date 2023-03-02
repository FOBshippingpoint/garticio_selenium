from PIL import Image, ImageFilter
from pynput.mouse import Button, Controller as MouseController
from selenium.webdriver.common.by import By
import numpy as np
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


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

    im = im.convert("RGB")
    im = im.quantize(colors=16)
    im = im.convert("RGB")
    im = im.filter(ImageFilter.MedianFilter(size=3))
    a = np.asarray(im)
    return a, im.size


def is_close_to_white(color, threshold=50):
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


def compute_line(a):
    """1 image row to line"""
    line = []
    start = 0
    # convert each continuous color into 'start', 'end', 'color_id' dict
    for i in range(len(a) - 1):
        if (a[i] != a[i + 1]).all():
            end = i
            if not is_close_to_white(tuple(a[i])):
                hex_color = to_hex(tuple(a[i]))
                seg = {
                    "start": start,
                    "end": end,
                    "hex_color": hex_color,
                }
                line.append(seg)
            # next
            start = i + 1

    return line


def draw_by_color(driver, lines, xoffset=10, yoffset=10, gap=1, line_height=None):
    if line_height is None:
        line_height = gap

    color_map = {}
    for y, line in enumerate(lines):
        for seg in line:
            seg["y"] = y
            if seg["hex_color"] in color_map:
                color_map[seg["hex_color"]] += [seg]
            else:
                color_map[seg["hex_color"]] = [seg]

    mouse = MouseController()
    color_range = driver.find_element(By.ID, "colorsRange")
    for hex_color, color_line in color_map.items():
        try:
            color_range.click()
        except:
            return
        action = ActionChains(driver)
        action.key_down(Keys.SHIFT)
        action.send_keys(Keys.TAB)
        action.key_up(Keys.SHIFT)
        action.send_keys(Keys.UP)
        action.key_down(Keys.SHIFT)
        action.send_keys(Keys.TAB)
        action.key_up(Keys.SHIFT)
        action.send_keys(hex_color)
        action.send_keys(Keys.ENTER).perform()

        for seg in color_line:
            mouse.position = (
                xoffset + seg["start"] * gap,
                yoffset + seg["y"] * line_height,
            )

            if seg["start"] == seg["end"]:
                mouse.click(Button.left)
            else:
                mouse.press(Button.left)
                time.sleep(0.0001)
                mouse.move((seg["end"] - seg["start"]) * gap, 0)
                time.sleep(0.0001)
                mouse.release(Button.left)
