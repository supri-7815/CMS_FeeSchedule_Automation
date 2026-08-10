from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from Physician.physician_download import download_physician_file, clean_physician_downloads

PHYSICIAN_URL = (
    "https://www.cms.gov/medicare/payment/fee-schedules/"
    "physician/national-payment-amount-file"
)


def collect_physician_files(driver, wait):

    files = []

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//table")
        )
    )

    rows = driver.find_elements(
        By.XPATH,
        "//table//tbody/tr"
    )

    for row in rows:
        # Try to extract the file name (link text) and year robustly
        try:
            link = row.find_element(By.XPATH, ".//a")
            file_name = link.text.strip()
        except Exception:
            # Fallback to first cell text
            cols = row.find_elements(By.TAG_NAME, "td")
            if not cols:
                continue
            file_name = cols[0].text.strip()

        # Look for a 4-digit year anywhere in the row (common in CMS tables)
        year = None
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            for c in cells:
                txt = c.text.strip()
                if txt in ["2024", "2025", "2026"]:
                    year = txt
                    break
                # sometimes year appears with extra text
                if len(txt) >= 4 and any(y in txt for y in ["2024", "2025", "2026"]):
                    for y in ["2024", "2025", "2026"]:
                        if y in txt:
                            year = y
                            break
                    if year:
                        break
        except Exception:
            year = None

        if year and file_name:
            files.append({
                "year": int(year),
                "file": file_name
            })

    return files


def open_physician_files(driver):

    wait = WebDriverWait(driver, 30)

    driver.get(PHYSICIAN_URL)

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//table")
        )
    )

    files = collect_physician_files(
        driver,
        wait
    )

    # Clean old Physician downloads before starting
    try:
        clean_physician_downloads()
    except Exception:
        pass

    # Process oldest year first
    files.sort(
        key=lambda x: x["year"]
    )

    print("\nPhysician Fee Schedule Files")
    print("------------------------------------------------------------")

    # Tracking lists
    download_map = []
    failed_downloads = []

    for item in files:

        print(
            f"\nOpening : {item['file']} "
            f"({item['year']})"
        )

        # Return to the main Physician file page
        driver.get(PHYSICIAN_URL)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//table")
            )
        )

        # Locate the link by exact normalized filename match to avoid partial matches
        expected = item["file"].strip()

        xpath = f"//table//a[normalize-space(.)=\"{expected}\"]"

        file_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

        # Verify the selected element's visible text matches exactly
        actual_filename = file_link.text.strip()

        if actual_filename != expected:
            raise Exception(
                f"Wrong file selected. Expected: {expected}, Found: {actual_filename}"
            )

        print("✓ Correct filename selected")

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            file_link
        )

        time.sleep(0.5)

        file_link.click()

        # Wait for the detail page
        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//h2[contains("
                    "translate(.,"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                    "'abcdefghijklmnopqrstuvwxyz'),"
                    "'downloads')]"
                )
            )
        )

        print(
            f"✓ Opened : {item['file']}"
        )
        # Attempt download and record actual downloaded filenames
        try:
            downloaded = download_physician_file(driver)

            if downloaded:
                downloaded_list = list(downloaded)

                for d in downloaded_list:
                    print(f"Requested CMS file : {item['file']}")
                    print(f"Downloaded ZIP     : {d}\n")

                download_map.append({
                    "requested": item["file"],
                    "downloaded": downloaded_list
                })

            else:
                print(f"⚠ {item['file']} - No files reported as downloaded")
                failed_downloads.append({"requested": item['file'], "error": "No files reported as downloaded"})

        except Exception as e:

            print(f"✖ {item['file']} - Download failed : {e}")
            failed_downloads.append({"requested": item['file'], "error": str(e)})

        # small pause between files
        time.sleep(1)

    return files, download_map, failed_downloads