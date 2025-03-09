import os
from selenium import webdriver
import sys
import time


os.setsid()

url = sys.argv[1]
cookies = sys.argv[2:]

options = webdriver.ChromeOptions()
options.add_argument("enable-automation")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(options=options)
print("Chrome started", file=sys.stderr, flush=True)

if cookies:
    # Selenium can only set the cookies attached to the current domain
    driver.get("https://mediumrare.q.2025.ugractf.ru/randomterminator")
    for cookie in cookies:
        name, value, path = cookie.split(";")
        driver.add_cookie({"name": name, "value": value, "sameSite": "Strict", "path": path})

driver.set_page_load_timeout(10)
driver.get(url)
time.sleep(5)

driver.quit()
