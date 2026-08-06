from download import download_2026, download_old_year
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import success


CMS_URL = "https://www.cms.gov/medicare/payment/fee-schedules/clinical-laboratory-fee-schedule-clfs/files"


def open_latest_files(driver):

    wait = WebDriverWait(driver, 20)

    # Wait for CMS table
    wait.until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )

    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")

    latest_files = []
    processed_years = set()

    # Get latest file for each year
    for row in rows:

        cols = row.find_elements(By.TAG_NAME, "td")

        if len(cols) != 3:
            continue

        file_text = cols[0].text.strip()

        if "File Name" not in file_text:
            continue

        year = cols[2].text.replace("Calendar Year", "").strip()

        if year not in processed_years:

            processed_years.add(year)

            file_name = file_text.replace("File Name", "").strip()

            latest_files.append({
                "year": year,
                "file_name": file_name
            })

    # Download files
    for file in latest_files:

        wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//a[contains(text(),'{file['file_name']}')]"
                )
            )
        ).click()

        if file["year"] == "2026":
            download_2026(driver, file["file_name"])
        else:
            download_old_year(driver, file["file_name"])

        success(f"{file['year']} : {file['file_name']} downloaded")

        # Always return to CMS main page
        driver.get(CMS_URL)

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )