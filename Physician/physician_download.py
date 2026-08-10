import os
import time
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DOWNLOAD_FOLDER = os.path.abspath("Downloads")


def wait_for_download(before_files, timeout=120):

    start = time.time()

    while True:

        current_files = set(os.listdir(DOWNLOAD_FOLDER))

        new_files = current_files - before_files

        completed_files = [
            file for file in new_files
            if not file.lower().endswith(
                (".crdownload", ".tmp", ".part")
            )
        ]

        downloading = any(
            file.lower().endswith(
                (".crdownload", ".tmp", ".part")
            )
            for file in current_files
        )

        if completed_files and not downloading:
            time.sleep(2)
            return completed_files

        if time.time() - start > timeout:
            raise Exception(
                "Physician file download timed out."
            )

        time.sleep(1)


def download_physician_file(driver):

    wait = WebDriverWait(driver, 30)

    os.makedirs(
        DOWNLOAD_FOLDER,
        exist_ok=True
    )

    # Record files before clicking
    before_files = set(
        os.listdir(DOWNLOAD_FOLDER)
    )

    print("Looking for Downloads section...")

    download_link = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//h2[contains("
                "translate(.,"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'),"
                "'downloads')]"
                "/following::a["
                "contains(@href,'.zip') or "
                "contains(@href,'.txt')"
                "][1]"
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        download_link
    )

    time.sleep(1)

    print("Clicking Physician download link...")

    download_link.click()

    downloaded_files = wait_for_download(
        before_files
    )

    print("\nPhysician Files Downloaded")
    print("----------------------------------------")

    for file in downloaded_files:
        print(file)

    print("----------------------------------------")

    return downloaded_files


def clean_physician_downloads():

    os.makedirs(
        DOWNLOAD_FOLDER,
        exist_ok=True
    )

    for file in os.listdir(DOWNLOAD_FOLDER):

        path = os.path.join(DOWNLOAD_FOLDER, file)

        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass

    print("✓ Physician Downloads folder cleaned")