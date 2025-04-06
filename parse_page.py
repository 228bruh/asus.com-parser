from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
import asyncio
import aiohttp
from bs4 import BeautifulSoup

def create_browser():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    service = Service("/usr/bin/geckodriver")
    browser = webdriver.Firefox(service=service, options=options)

    return browser

def accept_cookies_close_popup(wait):
    try:
        acceptBtn = wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "btn-asus.btn-ok.btn-read-ck")))
        acceptBtn.click()
        closeBtn = wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "reminderIconClose")))
        closeBtn.click()
    except Exception:
        pass

def load_full_page(wait):
    while True:
        try:
            loadMoreBtn = wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "StoreContent__showMore__3zU47")))
            loadMoreBtn.click()
        except Exception:
            break

def syns_parse(browser):
    products = []
    cards = browser.find_elements(By.CSS_SELECTOR, "div.store_content_product")

    for card in cards:
        try:
            name = card.find_element(By.TAG_NAME, "h2").get_attribute("innerHTML").replace(" <br>", "").replace(";", " ").strip()
            price = card.find_element(By.CLASS_NAME, "ProductCardNormalStore2__price__-bEGR").text
            products.append((name, price))
        except Exception:
            continue

    return products

def asyns_parse():
    pass