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
        "value": "00A3F7EB036C3AD121D2CC02B1FBBAB3DA2237E41418EF53CB80BD3485A2CFDD66CD278FD7FC17B098C75B56FD7C276ACBE79959DB662364D7C4F0DA494A1AE045AD750BFFFE75AD9941025C567701502BA5FE01AAE1F1E4736F58F834B9671F14CEAA6788E39213A039223B62C19BB32CBB17176903ADE58B9C727D560508A94985D52F805063EB907DB55F2788ABE33D6B4B0B8F19ED3208769362A7103E442782CCE279E7DF0A2A1E3E36804BEA8F997E8E0321BEE24B8B390C2720FBC45182CB604A487F5A8B38D2B83A1E1391C03EA2541B4FBD992AC45089A2D402ADEFD748670E5394F4B76F6524070D6134522037A8F04D6861822371EFA8E682E3EB078172DAC4DFD232436C2E457CBA63A685247914D3F935495CB5A883024EBC8FE9EDD32915DF288B8E87A439F97AA75D4E36BD9645896CAD9A4F7428C5AE3B4F1F2702E758E84B7CAEA7FE4F26DC4CC08E48BCE5B9A51FA94FA20F02AD4F30BEB0",
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
