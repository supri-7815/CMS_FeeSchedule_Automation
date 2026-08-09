import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "Downloads")


def wait_for_download(timeout=120):

    start = time.time()

    while True:

        downloading = any(
            file.endswith(".crdownload") or file.endswith(".tmp")
            for file in os.listdir(DOWNLOAD_FOLDER)
        )

        if not downloading:
            break

        if time.time() - start > timeout:
            raise Exception("Download timed out.")

        time.sleep(0.5)

    # Give Chrome a moment to release the download
    time.sleep(2)
def download_2026(driver, file_name=None):

    wait = WebDriverWait(driver, 30)

    # Already on details page
    related_link = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//h2[contains(.,'Related Links')]/following::a[contains(@href,'.zip')][1]"
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        related_link
    )

    related_link.click()

    accept_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@value='Accept']")
        )
    )

    accept_button.click()

    wait_for_download()


def download_old_year(driver, file_name=None):

    wait = WebDriverWait(driver, 30)

    try:

        # Related Links
        related_link = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//h2[contains(.,'Related Links')]/following::a[contains(@href,'.zip')][1]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            related_link
        )

        related_link.click()

        try:

            accept_button = WebDriverWait(driver,5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,"//input[@value='Accept']")
                )
            )

            accept_button.click()

        except TimeoutException:
            pass

        wait_for_download()

        return

    except TimeoutException:
        pass

    # Downloads section
    download_link = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//h2[contains(.,'Downloads')]/following::a[contains(@href,'.zip')][1]"
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        download_link
    )

    download_link.click()

    wait_for_download()