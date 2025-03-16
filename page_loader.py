from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

def create_browser():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    service = Service("/usr/bin/geckodriver")
    browser = webdriver.Firefox(service=service, options=options)

    return browser

def accept_cookies(wait):
    try:
        acceptBtn = wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "btn-asus.btn-ok.btn-read-ck")))
        acceptBtn.click()
    except Exception:
        pass

def close_stayHere_popup(wait):
    try:
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