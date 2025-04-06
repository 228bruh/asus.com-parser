from selenium.webdriver.support.ui import WebDriverWait
import parse_page

browser = parse_page.create_browser()
url = "https://www.asus.com/us/store/laptops/"

try:
    browser.get(url)
    wait = WebDriverWait(browser, 5)

    parse_page.accept_cookies_close_popup(wait)
    parse_page.load_full_page(wait)

    products = parse_page.syns_parse(browser)
    for name, price in products:
        print(f"{name}\t{price}")

finally:
    browser.close()
