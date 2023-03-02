import tempfile
import requests
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from draw import draw_by_color, make_line, process_img


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
            self.save_img()
            self.root.event_generate("<<StartDraw>>")
            self.draw_img()
            self.root.event_generate("<<EndDraw>>")
            self.wait.until_not(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#hint > div > button")
                )
            )

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
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#hint > div > button"))
        )
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

    def save_img(self):
        # switch to google_search window
        self.driver.switch_to.window(self.driver.window_handles[1])

        img = self.wait.until(lambda d: d.find_element(By.CLASS_NAME, "KAlRDb"))

        img_src = img.get_attribute("src")
        img_data = requests.get(img_src).content
        self.tmp = tempfile.TemporaryFile()
        self.tmp.write(img_data)
        self.img = Image.open(self.tmp)

    def draw_img(self):
        if len(self.driver.window_handles) > 1:
            self.driver.close()
        self.switch_to_garticio()

        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#hint > div > button"))
        )

        with self.img as im:
            w, h = (200, 116)
            a, size = process_img(im, w, h)
            lines = map(make_line, a)

            img_width = size[0]
            xoffset = (w - img_width) / 2 * 800 / w
            draw_by_color(
                driver=self.driver,
                lines=lines,
                gap=2.5,
                xoffset=750 + xoffset,
                yoffset=320,
            )
            self.tmp.close()

    def close(self):
        self.driver.quit()
