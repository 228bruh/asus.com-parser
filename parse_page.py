from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp

class Parser:
    def __init__(self):
        self.url = "https://www.laptopsdirect.co.uk/ct/laptops-and-netbooks/laptops/gaming"
        self.links = []
        self._collect_links()

    def _create_browser(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        service = Service("/usr/bin/geckodriver")
        return webdriver.Firefox(service=service, options=options)

    def _accept_cookies(self, wait):
        try:
            acceptBtn = wait.until(expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")))
            acceptBtn.click()
        except Exception:
            pass

    def _load_full_page(self, wait):
        while True:
            try:
                loadMoreBtn = wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#loadmore_button")))
                loadMoreBtn.click()
            except Exception:
                break

    def _collect_links(self):
        browser = self._create_browser()
        wait = WebDriverWait(browser, 10)
        try:
            browser.get(self.url)
            self._accept_cookies(wait)
            print("Cookies accepted") ###
            self._load_full_page(wait)
            print("Page loaded") ###

            elements = browser.find_elements(By.CSS_SELECTOR, "div.OfferBox > div > div > div > h3 > a")
            for el in elements:
                try:
                    href = el.get_attribute("href")
                    if href:
                        self.links.append(href)
                except Exception:
                    continue
        finally:
            print(len(self.links)) ###
            browser.quit()


    # ============== SYNC ==============
    def sync_parse(self):
        products = []

        with requests.Session() as session:
            for link in self.links:
                try:
                    r = session.get(link, timeout=10)
                    soup = BeautifulSoup(r.text, "html.parser")

                    name = soup.select_one("h1 > span").get_text().strip()
                    price = soup.select_one("span.VersionOfferPrice:nth-child(3)").get_text().strip()

                    products.append([name, price])
                except Exception:
                    products.append(["Not found", "Not found"])

        return products


    # ============== ASYNC ==============
    async def _fetch(self, session, url, semaphore):
        async with semaphore:
            try:
                async with session.get(url, timeout=10) as r:
                    if r.status == 200:
                        return await r.text()
            except Exception:
                pass
            return None

    def _parse_html(self, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            name = soup.select_one("h1 > span").get_text().strip()
            price = soup.select_one("span.VersionOfferPrice:nth-child(3)").get_text().strip()
            return [name, price]
        except Exception:
            return ["Not found", "Not found"]

    async def _async_parse_impl(self):
        results = []
        semaphore = asyncio.Semaphore(10)

        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(self._fetch(session, url, semaphore)) for url in self.links]
            pages = await asyncio.gather(*tasks)

            for html in pages:
                if html:
                    results.append(self._parse_html(html))
                else:
                    results.append(["Not found", "Not found"])

        return results

    def async_parse(self):
        return asyncio.run(self._async_parse_impl())
