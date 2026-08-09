from download import download_2026, download_old_year
from utils import success

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

CMS_URL = "https://www.cms.gov/medicare/payment/fee-schedules/clinical-laboratory-fee-schedule-clfs/files"


def get_quarter(file_name):

    file_name = file_name.upper()

    if "Q4" in file_name:
        return 4
    elif "Q3" in file_name:
        return 3
    elif "Q2" in file_name:
        return 2
    elif "Q1" in file_name:
        return 1

    return 0


def collect_files(driver, wait):

    files = []

    # ---------------- PAGE 1 ----------------

    wait.until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )

    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")

    for row in rows:

        cols = row.find_elements(By.TAG_NAME, "td")

        if len(cols) != 3:
            continue

        file_name = cols[0].text.replace("File Name", "").strip()
        year = cols[2].text.replace("Calendar Year", "").strip()

        if year in ["2024", "2025", "2026"] and "CLABQ" in file_name.upper():

            files.append({
                "year": int(year),
                "quarter": get_quarter(file_name),
                "file": file_name
            })

    # ---------------- PAGE 2 ----------------

    try:

        page2 = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "2"))
        )

        page2.click()

        time.sleep(2)

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )

        rows = driver.find_elements(By.XPATH, "//table//tbody/tr")

        for row in rows:

            cols = row.find_elements(By.TAG_NAME, "td")

            if len(cols) != 3:
                continue

            file_name = cols[0].text.replace("File Name", "").strip()
            year = cols[2].text.replace("Calendar Year", "").strip()

            if year == "2024" and "CLABQ1" in file_name.upper():

                files.append({
                    "year": 2024,
                    "quarter": 1,
                    "file": file_name
                })

    except Exception:
        pass

    return files


def open_latest_files(driver):

    wait = WebDriverWait(driver, 20)

    files = collect_files(driver, wait)

    # Sort: 2026 Q3 -> 2024 Q1
    files.sort(
        key=lambda x: (x["year"], x["quarter"]),
        reverse=True
    )

    print("\nDownloading Files")
    print("------------------------------------------------------------")

    for item in files:

        driver.get(CMS_URL)

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )

        # 2024 Q1 is on Page 2
        if item["year"] == 2024 and item["quarter"] == 1:

            page2 = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "2"))
            )

            page2.click()

            time.sleep(2)

            wait.until(
                EC.presence_of_element_located((By.XPATH, "//table"))
            )

        print(f"\nOpening : {item['file']}")

        file_link = wait.until(
            EC.element_to_be_clickable(
                (
                    By.LINK_TEXT,
                    item["file"]
                )
            )
        )

        file_link.click()

        if item["year"] == 2026:
            download_2026(driver)
        else:
            download_old_year(driver)

        success(f"{item['file']} downloaded")