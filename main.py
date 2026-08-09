import time
from datetime import datetime

from downloader import start_download
from navigator import open_latest_files
from parser import clean_folders, extract_zip_files
from database import create_table, save_records
from utils import header, step, success, summary


def main():

    start_time = time.time()

    header()

    # STEP 1
    step("STEP 1 : Cleaning Working Directories")
    clean_folders()
    success("Downloads folder cleaned")
    success("Extracted folder cleaned")

    # STEP 2
    step("STEP 2 : Opening CMS Website")
    driver = start_download()
    success("CMS website loaded successfully")

    # STEP 3
    step("STEP 3 : Downloading Latest CLFS Files")
    open_latest_files(driver)

    driver.quit()

    # STEP 4
    step("STEP 4 : Extracting ZIP Files")
    yearly_records = extract_zip_files()

    # STEP 5
    step("STEP 5 : Reading & Parsing TXT Files")

    # STEP 6
    step("STEP 6 : Updating MySQL Database")

    create_table()

    for year in sorted(yearly_records.keys()):

        print(f"\nProcessing Year : {year}")
        print("------------------------------------------------------------")

        records = yearly_records[year]

        success(f"Records Parsed : {len(records)}")

        save_records(records)

    end_time = time.time()

    execution_time = round(end_time - start_time, 2)

    summary()

    print(f"Status               : SUCCESS")
    print(f"Execution Time       : {execution_time} Seconds")
    print(f"Execution Date       : {datetime.now().strftime('%d-%m-%Y')}")
    print(f"Execution Time Stamp : {datetime.now().strftime('%I:%M:%S %p')}")

    print("\nThank You!")


if __name__ == "__main__":
    main()