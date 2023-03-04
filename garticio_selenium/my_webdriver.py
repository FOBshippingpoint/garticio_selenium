from collections import defaultdict
import tempfile
from threading import Thread
import time
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from img_tool import compute_line, process_img
from datetime import datetime
from pynput.mouse import Button, Controller
from pynput import keyboard
from collections import defaultdict

EC_CAN_USER_DRAW = EC.presence_of_element_located(
    (By.CSS_SELECTOR, "#hint > div > button")
)
GARTIC_IO_URL = "https://gartic.io"


class MyWebDriver:
    def __init__(self, root, suffix, color_num, zoom, sleep_ms):
        # suffix: google image search suffix string
        self.suffix = suffix
        # color_num: number of colors to quantize
        self.color_num = color_num
        # zoom: image size in percentage
        self.zoom = zoom
        # sleep_ms: next stroke sleep time in ms
        self.sleep_ms = sleep_ms

        options = Options()
        options.add_extension("uBlock-Origin.crx")
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.named_windows = defaultdict()
        self.wait = WebDriverWait(self.driver, timeout=999999)
        self.root = root

    def set_cur_window_with_name(self, name):
        self.named_windows[name] = self.driver.current_window_handle

    def switch_to_named_window(self, name):
        window = self.named_windows[name]
        self.driver.switch_to.window(window)

    def start(self):
        self.driver.get(GARTIC_IO_URL)
        self.set_cur_window_with_name("garticio")
        self.set_username()

        while True:
            self.root.event_generate("<<Waiting>>")
            answer = self.find_answer()
            self.open_google_img_search(answer)
            self.root.event_generate("<<OpenImageSearch>>")
            with self.save_img_as_tmp() as tmp:
                self.root.event_generate("<<StartPrint>>")
                result = self.draw_from_tmp_img(tmp)
                if result == "complete":
                    self.root.event_generate("<<EndPrint>>")
                elif result == "time's_up":
                    self.root.event_generate("<<Time'sUp>>")
                    time.sleep(2)
                elif result == "user_stop":
                    self.root.event_generate("<<UserStop>>")
            self.wait.until_not(EC_CAN_USER_DRAW)

    def set_username(self, username="印表機"):
        name_input = self.driver.find_element(By.TAG_NAME, "input")
        name_input.click()
        name_input.send_keys(Keys.CONTROL, "a")
        name_input.send_keys(username)

    def find_answer(self):
        self.switch_to_named_window("garticio")
        self.wait.until(EC_CAN_USER_DRAW)
        # word contains many divs, so innerText will have \n, need to remove
        word = self.driver.find_element(By.CLASS_NAME, "word")
        words = word.get_attribute("innerText")
        answer = words.replace("\n", "")

        return answer

    def open_google_img_search(self, answer):
        query = answer + "+" + self.suffix
        self.driver.switch_to.new_window("tab")
        self.driver.get(f"https://www.google.com/search?q={query}&tbm=isch&hl=zh-TW")
        self.set_cur_window_with_name("google_image_search")

    def save_img_as_tmp(self):
        self.switch_to_named_window("google_image_search")

        while True:
            img = self.wait.until(lambda d: d.find_element(By.CLASS_NAME, "KAlRDb"))
            img_src = img.get_attribute("src")
            try:
                img_data = requests.get(img_src).content
                tmp = tempfile.TemporaryFile()
                tmp.write(img_data)
                self.switch_to_named_window("google_image_search")
                self.driver.close()
                break
            except Exception as e:
                print(e)
                self.root.event_generate("<<ImageFetchError>>")
                continue

        return tmp

    def draw_from_tmp_img(self, tmp):
        self.switch_to_named_window("garticio")
        self.wait.until(EC_CAN_USER_DRAW)

        gap = 2.5
        canvas_rect = self.compute_canvas_rect()

        zoom = self.zoom / 100
        with Image.open(tmp) as im:
            img_arr, (img_width, img_height) = process_img(
                im,
                basewidth=int(canvas_rect["width"] / gap * zoom),
                baseheight=int(canvas_rect["height"] / gap * zoom),
                quantize_color_num=self.color_num
            )
            xoffset = int(
                canvas_rect["x"] + (canvas_rect["width"] - img_width * gap) / 2
            )
            yoffset = int(
                canvas_rect["y"] + (canvas_rect["height"] - img_height * gap) / 2
            )

            lines = map(compute_line, img_arr)

            result = self.print_lines(
                lines=lines, xoffset=xoffset, yoffset=yoffset, gap=gap
            )
            return result

    def compute_canvas_rect(self):
        canvas = self.driver.find_element(By.ID, "drawing")
        hint = self.driver.find_element(By.ID, "hint")
        # ref: https://stackoverflow.com/questions/42807676/pythonselenium-on-screen-position-of-element
        # Assume there is equal amount of browser chrome on the left and right sides of the screen.
        browser_xoffset = self.driver.execute_script(
            "return window.screenX + (window.outerWidth - window.innerWidth) / 2 - window.scrollX;"
        )
        # Assume all the browser chrome is on the top of the screen and none on the bottom.
        browser_yoffset = self.driver.execute_script(
            "return window.screenY + (window.outerHeight - window.innerHeight) - window.scrollY;"
        )
        canvas_rect = {
            "x": canvas.rect["x"] + browser_xoffset,
            "y": canvas.rect["y"] + browser_yoffset + hint.rect["height"] / 2,
            "width": canvas.rect["width"],
            "height": canvas.rect["height"] - hint.rect["height"] / 2,
        }

        return canvas_rect

    def print_lines(self, lines, xoffset, yoffset, gap):
        color_map = defaultdict(list)
        for y, line in enumerate(lines):
            for seg in line:
                seg["y"] = y
                color_map[seg["hex_color"]].append(seg)

        mouse = Controller()
        color_selector = self.driver.find_element(By.ID, "colorsRange")

        self.stop = False
        self.pause = False

        self.listener = keyboard.Listener(on_press=self.on_press_stop, suppress=True)
        self.listener.start()

        for hex_color, line in color_map.items():
            try:
                self.change_brush_color(color_selector, hex_color)
            except:
                return "time's_up"
            for seg in line:
                if self.stop:
                    return "user_stop"
                elif self.pause:
                    self.root.event_generate("<<UserPause>>")
                    while self.pause:
                        pass
                    self.root.event_generate("<<StartPrint>>")
                else:
                    mouse.position = (
                        xoffset + seg["start"] * gap,
                        yoffset + seg["y"] * gap,
                    )

                    is_dot = seg["start"] == seg["end"]
                    if is_dot:
                        mouse.click(Button.left)
                    else:
                        mouse.press(Button.left)
                        time.sleep(self.sleep_ms / 1000)
                        mouse.move((seg["end"] - seg["start"]) * gap, 0)
                        time.sleep(self.sleep_ms / 1000)
                        mouse.release(Button.left)

        self.listener.stop()
        return "complete"

    def change_brush_color(self, color_selector, hex_color):
        color_selector.click()
        action = ActionChains(self.driver)
        action.key_down(Keys.SHIFT)
        action.send_keys(Keys.TAB)
        action.key_up(Keys.SHIFT)
        action.send_keys(Keys.UP)
        action.key_down(Keys.SHIFT)
        action.send_keys(Keys.TAB)
        action.key_up(Keys.SHIFT)
        action.send_keys(hex_color)
        action.send_keys(Keys.ENTER).perform()

    def close(self):
        self.driver.quit()

    def on_press_stop(self, key):
        if key == keyboard.Key.f3:
            self.pause = not self.pause
        elif key == keyboard.Key.f4:
            self.listener.stop()
            self.stop = True
