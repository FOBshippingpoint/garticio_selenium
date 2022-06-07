# 啟動 Chrome 必須先下載 Chrome 驅動器(https://sites.google.com/chromium.org/driver/)
# 將 Chrome 驅動器放置同路徑下，或設定於系統環境變數中的 Path
# driver = webdriver.Chrome('chromedriver.exe')
# driver = webdriver.Chrome()
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.binary_location = (
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
)
driver = webdriver.Chrome(chrome_options=options)
driver.get("http://google.com/")
driver.switch_to.active_element.send_keys("牛逼牛逼")
print("Chrome Browser Invoked")


# driver = webdriver.Chrome(ChromeDriverManager().install())
