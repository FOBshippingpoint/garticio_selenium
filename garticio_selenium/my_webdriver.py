import tempfile
import time
import requests
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from draw import draw_by_color, compute_line, process_img
from datetime import datetime

EC_CAN_USER_DRAW = EC.presence_of_element_located(
    (By.CSS_SELECTOR, "#hint > div > button")
)


class MyWebDriver:
    def __init__(self, root):
        options = Options()
        options.add_extension("uBlock-Origin.crx")
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.wait = WebDriverWait(self.driver, timeout=999999)
        self.root = root

    def start(self):
        self.driver.get("https://gartic.io/")
        self.set_username()
        while True:
            self.root.event_generate("<<Waiting>>")
            keyword = self.find_keyword()
            self.open_google_img_search(keyword)
            self.root.event_generate("<<OpenImageSearch>>")
            with self.save_img_as_tmp() as tmp:
                self.root.event_generate("<<StartDraw>>")
                result = self.draw_from_tmp_img(tmp)
                if result == "complete":
                    self.root.event_generate("<<EndDraw>>")
                elif result == "interrupt":
                    self.root.event_generate("<<DrawInterrupt>>")
                    time.sleep(2)
            self.wait.until_not(EC_CAN_USER_DRAW)

    def set_username(self, username="印表機"):
        name_input = self.driver.find_element(By.TAG_NAME, "input")
        name_input.click()
        name_input.send_keys(Keys.CONTROL, "a")
        name_input.send_keys(username)

    def switch_to_garticio(self):
        gartic_window = self.driver.window_handles[0]
        self.driver.switch_to.window(gartic_window)

    def find_keyword(self):
        self.switch_to_garticio()
        self.wait.until(EC_CAN_USER_DRAW)
        # word contains many divs, so innerText will have \n, need to remove
        word = self.driver.find_element(By.CLASS_NAME, "word")
        words = word.get_attribute("innerText")
        keyword = words.replace("\n", "")

        return keyword

    def open_google_img_search(self, keyword, suffix=""):
        if suffix == "":
            query = keyword
        else:
            query = keyword + "+" + suffix
        script = (
            f"window.open('https://www.google.com/search?q={query}&tbm=isch&hl=zh-TW');"
        )
        self.driver.execute_script(script)

    def save_img_as_tmp(self):
        # switch to google_search window
        self.driver.switch_to.window(self.driver.window_handles[1])

        while True:
            img = self.wait.until(lambda d: d.find_element(By.CLASS_NAME, "KAlRDb"))
            img_src = img.get_attribute("src")
            try:
                img_data = requests.get(img_src).content
                tmp = tempfile.TemporaryFile()
                tmp.write(img_data)
                break
            except:
                self.root.event_generate("<<ImageFetchError>>")
                continue

        return tmp

    def draw_from_tmp_img(self, tmp):
        # if the broswer tabs is greater than 1, we need to close google search page
        # still had space to improve these lines
        if len(self.driver.window_handles) > 1:
            self.driver.close()
        self.switch_to_garticio()
        self.wait.until(EC_CAN_USER_DRAW)

        with Image.open(tmp) as im:
            w, h = (200, 116)
            img_arr, size = process_img(im, w, h)
            lines = map(compute_line, img_arr)

            img_width = size[0]
            xoffset = (w - img_width) / 2 * 800 / w + 750
            try:
                draw_by_color(
                    driver=self.driver,
                    lines=lines,
                    xoffset=xoffset,
                    yoffset=320,
                    x_gap=2.5,
                )
            except:
                return "interrupt"

        return "complete"

    def close(self):
        self.driver.quit()
