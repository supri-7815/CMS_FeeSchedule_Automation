from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def download_2026(driver, file_name):

    wait = WebDriverWait(driver, 20)

    # Click Related Link
    related_link = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, file_name)
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        related_link
    )

    time.sleep(1)

    related_link.click()

    # Click Accept button
    accept_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@value='Accept']")
        )
    )

    accept_button.click()

    # Wait for download
    time.sleep(10)


def download_old_year(driver, file_name):

    wait = WebDriverWait(driver, 20)

    download_link = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, file_name)
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        download_link
    )

    time.sleep(1)

    download_link.click()

    # Wait for download
    time.sleep(10)