from selenium.webdriver.support.ui import WebDriverWait
import page_loader

browser = page_loader.create_browser()

try:
    browser.get("https://www.asus.com/us/store/laptops/")
    wait = WebDriverWait(browser, 5)

    page_loader.accept_cookies(wait)
    page_loader.close_stayHere_popup(wait)

    page_loader.load_full_page(wait)

finally:
    # browser.close()
    pass