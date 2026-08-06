from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import CMS_URL, HEADLESS
import os
import time


def start_download():

    options = webdriver.ChromeOptions()

    # Project Downloads folder
    download_path = os.path.abspath("Downloads")

    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    options.add_experimental_option("prefs", prefs)

    if HEADLESS:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.maximize_window()

    print("Download Folder :", download_path)
    print("Opening CMS Website...")

    driver.get(CMS_URL)

    wait = WebDriverWait(driver, 20)

    wait.until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )

    # Scroll to bottom
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollBy(0,500);")
        time.sleep(0.5)

        current_position = driver.execute_script(
            "return window.pageYOffset + window.innerHeight;"
        )

        if current_position >= last_height:
            break

    time.sleep(2)

    print("CMS Website Loaded Successfully.")

    return driver
