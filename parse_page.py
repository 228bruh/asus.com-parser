from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time

def create_browser():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    service = Service("/usr/bin/geckodriver")
    browser = webdriver.Firefox(service=service, options=options)
    return browser

def accept_cookies(wait):
    try:
        acceptBtn = wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")))
        acceptBtn.click()
    except Exception:
        pass

def load_full_page(wait, browser):
    while True:
        try:
            loadMoreBtn = wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#loadmore_button")))
            loadMoreBtn.click()
        except Exception:
            break

def get_product_links(browser):
    links = []
    elements = browser.find_elements(By.CSS_SELECTOR, "div.OfferBox > div > div > div > h3 > a")
    for el in elements:
        try:
            href = el.get_attribute("href")
            if href:
                links.append(href)
        except Exception:
            continue
    return links

# ============= SYNS =============
def syns_parse(links):
    products = []

    with requests.Session() as session:
        for link in links:
            try:
                r = session.get(link)
                soup = BeautifulSoup(r.text, "html.parser")

                name = soup.select_one("h1 > span").get_text().strip()
                price = soup.select_one("span.VersionOfferPrice:nth-child(3)").get_text().strip()

                products.append([name, price])

            except Exception:
                products.append(["Not found", "Not found"])

    return products

# ============= ASYNS =============
semaphore = asyncio.Semaphore(10)

async def fetch(session, url):
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as r:
                if r.status == 200:
                    return await r.text()
        except Exception:
            pass
        return None

def parse(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        name = soup.select_one("h1 > span").get_text().strip()
        price = soup.select_one("span.VersionOfferPrice:nth-child(3)").get_text().strip()
        return [name, price]
    except Exception:
        return ["Not found", "Not found"]

async def asyns_parse(links):
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = []

        tasks = [asyncio.create_task(fetch(session, url)) for url in links]
        pages = await asyncio.gather(*tasks)

        for html in pages:
            if html:
                results.append(parse(html))
            else:
                results.append(["Not found", "Not found"])

    return results