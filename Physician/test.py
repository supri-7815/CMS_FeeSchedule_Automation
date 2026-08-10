import os
import shutil
import sys

# Ensure project root is on sys.path

PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from Physician.physician_parser import extract_physician_files
from Physician.physician_navigator import open_physician_files
from Physician.physician_data_parser import parse_physician_txt_files
from Physician.physician_database import save_physician_records


DOWNLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Downloads"
)


def clean_downloads():

    os.makedirs(
        DOWNLOAD_FOLDER,
        exist_ok=True
    )

    for file in os.listdir(DOWNLOAD_FOLDER):

        path = os.path.join(
            DOWNLOAD_FOLDER,
            file
        )

        if os.path.isfile(path) or os.path.islink(path):

            os.remove(path)

        elif os.path.isdir(path):

            shutil.rmtree(path)


def test_download():

    clean_downloads()

    options = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    options.add_experimental_option(
        "prefs",
        prefs
    )

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    driver.maximize_window()

    try:

        # =====================================================
        # STEP 1 - DOWNLOAD
        # =====================================================

        print("\n============================================================")
        print("DOWNLOADING PHYSICIAN FILES")
        print("============================================================")

        files, download_map, failed_downloads = (
            open_physician_files(driver)
        )

        print("\n✓ All Physician files downloaded")

        # =====================================================
        # IMPORTANT:
        # CLOSE CMS BROWSER IMMEDIATELY
        # =====================================================

        try:
            driver.quit()
            driver = None

            print("✓ CMS browser closed successfully")

        except Exception as exc:
            print(
                f"⚠ CMS browser close warning: {exc}"
            )

        # =====================================================
        # STEP 2 - EXTRACTION
        # Browser is NO LONGER running here
        # =====================================================

        print("\n============================================================")
        print("EXTRACTING PHYSICIAN FILES")
        print("============================================================")

        txt_files, extraction_summary = (
            extract_physician_files()
        )

        print(
            f"\n✓ Physician TXT Files Found : "
            f"{len(txt_files)}"
        )

        # =====================================================
        # STEP 3 - PARSING
        # =====================================================

        print("\n============================================================")
        print("PARSING PHYSICIAN FILES")
        print("============================================================")

        (
            parsed_records,
            total_valid,
            malformed_count,
            per_file_counts
        ) = parse_physician_txt_files(
            txt_files
        )

        print("\n✓ Physician parsing completed")
        print(
            f"Source records processed : "
            f"{total_valid}"
        )

        # =====================================================
        # STEP 4 - DATABASE
        # =====================================================

        print("\n============================================================")
        print("UPDATING DATABASE")
        print("============================================================")

        db_result = save_physician_records(
            parsed_records,
            batch_size=5000
        )

        # =====================================================
        # STEP 5 - FINAL OUTPUT
        # =====================================================

        print("\n============================================================")
        print("        PHYSICIAN FEE SCHEDULE AUTOMATION")
        print("============================================================")

        print(
            f"\n✓ Physician files downloaded : "
            f"{len(download_map)}"
        )

        print(
            f"✓ TXT files extracted        : "
            f"{len(txt_files)}"
        )

        print(
            f"✓ Physician records parsed   : "
            f"{total_valid}"
        )

        print(
            f"✓ New Physician records      : "
            f"{db_result['new_records']}"
        )

        print(
            f"✓ Updated Physician records  : "
            f"{db_result['updated_records']}"
        )

        print(
            f"✓ Records processed          : "
            f"{db_result['processed']}"
        )

        print("\n============================================================")
        print("                    SUMMARY")
        print("============================================================")

        print("Status          : SUCCESS")
        print(
            f"Physician Files : {len(download_map)}"
        )
        print(
            f"TXT Files       : {len(txt_files)}"
        )
        print(
            f"Records Parsed  : {total_valid}"
        )
        print(
            f"Records Inserted: {db_result['new_records']}"
        )
        print(
            f"Records Updated : {db_result['updated_records']}"
        )
        print("Database        : CLFS_DATA")

        print("\nThank You!")

    except Exception as exc:

        print("\n============================================================")
        print("PHYSICIAN AUTOMATION FAILED")
        print("============================================================")
        print(f"Error : {exc}")

        raise

    finally:

        # Close browser only if it wasn't already closed
        if driver is not None:

            try:
                driver.quit()

                print(
                    "\n✓ CMS browser closed successfully"
                )

            except Exception as exc:

                print(
                    f"\n⚠ CMS browser was already closed: "
                    f"{exc}"
                )
if __name__ == "__main__":
    test_download()