# coding: utf-8

import os
import time
import logging
import zipfile
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from retrying import retry

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s')

CHROME_DIR = "chrome-win64"
CHROMEDRIVER_DIR = "chromedriver-win64"

CHROME_URL = "https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.88/win64/chrome-win64.zip"
CHROMEDRIVER_URL = "https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.88/win64/chromedriver-win64.zip"

def download_and_extract(url, output_dir):
    zip_path = output_dir + ".zip"
    if not os.path.exists(output_dir):
        logging.info(f"⬇️ Downloading: {url}")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        os.remove(zip_path)

def prepare_browser():
    download_and_extract(CHROME_URL, CHROME_DIR)
    download_and_extract(CHROMEDRIVER_URL, CHROMEDRIVER_DIR)

    chrome_path = os.path.abspath(f"{CHROME_DIR}/chrome.exe")
    chromedriver_path = os.path.abspath(f"{CHROMEDRIVER_DIR}/chromedriver.exe")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_path
    chrome_options.add_extension("NetEaseMusicWorldPlus.crx")

    service = Service(chromedriver_path)
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.implicitly_wait(20)
    return browser

@retry(wait_random_min=5000, wait_random_max=10000, stop_max_attempt_number=3)
def enter_iframe(browser):
    logging.info("Enter login iframe")
    time.sleep(5)
    try:
        iframe = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[starts-with(@id,'x-URS-iframe')]"))
        )
        browser.switch_to.frame(iframe)
        logging.info("Switched to login iframe")
    except Exception as e:
        logging.error(f"Failed to enter iframe: {e}")
        browser.save_screenshot("debug_iframe.png")
        raise
    return browser

@retry(wait_random_min=1000, wait_random_max=3000, stop_max_attempt_number=5)
def extension_login():
    logging.info("Load Chrome extension NetEaseMusicWorldPlus")
    logging.info("Initializing Chrome WebDriver (fixed version 134.0.6998.88)")

    try:
        browser = prepare_browser()
    except Exception as e:
        logging.error(f"❌ Failed to initialize ChromeDriver: {e}")
        return

    browser.get('https://music.163.com')

    logging.info("Injecting Cookie to skip login")
    browser.add_cookie({
        "name": "MUSIC_U",
        "value": "006488A24DDA176491C740DBBF48A8554206AE841E06F4C7702BA181030A19C7F2F8F52775CD41228A7EDF73B79D33061BBE3EF99B78211F6161E677A1A6C86ADEE33CF584AE8C16AD925A2E35BC58612E95984F5E9ACA1F30F86EA0E750B3DAC34F2DE2073541CC2F0C4E856CAADF6F2F1634ACA00BF9CF37270A22BA3F60EB813D327340AA0665B22745AF1C36A1B2C5B6D1CA6092C6E07CF7F9AFAB5178DEB639FA4C97F8F2EC6CDA698BE348BCE26494DF2EB7B0C98E77D7D7CCD3550277AA43219FBAC03AEBC0935A74B99BE6EAFD5F35B27967B5EB9B967C595BCFB1BBE8E4C734E41C56D513C8B5AA1656FE35887050765A3697FC2125F16D569DA789792D2202F8B4F7950CB30BA4CA4551EECEDA31CDD0842763C0B981C781BFA370ABE328A3EE164048C7B9F5F92B7D2F66CE0580E95FE7403E0A7173B9185415092C38982C9CBD0C7ABB243939F2B0BCCD52AE8CBE4BCFCD3E338FBCFF0A1D2FE4E6",
        "domain": ".music.163.com"
    })

    browser.refresh()
    time.sleep(5)
    browser.save_screenshot("debug_after_cookie.png")
    logging.info("✅ Cookie login successful")

    logging.info("Unlock finished")
    time.sleep(10)
    browser.quit()

if __name__ == '__main__':
    try:
        extension_login()
    except Exception as e:
        logging.error(f"Failed to execute login script: {e}")
