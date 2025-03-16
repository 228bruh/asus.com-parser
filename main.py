import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time

options = webdriver.FirefoxOptions()
# options.add_argument("--headless")
service = Service("/usr/bin/geckodriver")
browser = webdriver.Firefox(service=service, options=options)


try:
    browser.get("https://www.asus.com/us/store/laptops/")
    wait = WebDriverWait(browser, 3)

    # accept cookies
    try:
        accept_btn = wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "btn-asus.btn-ok.btn-read-ck")))
        accept_btn.click()
        time.sleep(1)
    except Exception:
        print("Cookies popup not found, continuing...")

    # close stay_here wndw

    while True:
        try:
            loadMoreBtn = wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "StoreContent__showMore__3zU47")))
            loadMoreBtn.click()
            time.sleep(1)
        except Exception:
            break

    # topicLinks = browser.find_elements(By.CLASS_NAME, "")

finally:
    # browser.close()
    pass

# <button tabindex="0" aria-label="close" id="reminderIconClose" class="reminderIconClose"></button>