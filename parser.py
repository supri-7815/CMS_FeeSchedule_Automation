import os
import re
import shutil
import zipfile
from utils import success

DOWNLOAD_FOLDER = "Downloads"
EXTRACT_FOLDER = "Extracted"


def clean_folders():

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(EXTRACT_FOLDER, exist_ok=True)

    # Clean Downloads
    for item in os.listdir(DOWNLOAD_FOLDER):

        item_path = os.path.join(DOWNLOAD_FOLDER, item)

        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path, ignore_errors=True)
        except:
            pass

    # Clean Extracted
    for item in os.listdir(EXTRACT_FOLDER):

        item_path = os.path.join(EXTRACT_FOLDER, item)

        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path, ignore_errors=True)

                if os.path.exists(item_path):
                    os.system(f'rmdir /s /q "{item_path}"')
        except:
            pass


def extract_zip_files():

    os.makedirs(EXTRACT_FOLDER, exist_ok=True)

    zip_files = [
        file for file in os.listdir(DOWNLOAD_FOLDER)
        if file.lower().endswith(".zip")
    ]

    if not zip_files:
        return []

    for zip_file in zip_files:

        zip_path = os.path.join(DOWNLOAD_FOLDER, zip_file)

        folder_name = os.path.splitext(zip_file)[0]

        extract_path = os.path.join(EXTRACT_FOLDER, folder_name)

        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

    print("\nZIP Files Found")
    print("------------------------------------------------------------")

    for file in sorted(zip_files):
        print(file)

    print("------------------------------------------------------------")

    success(f"ZIP Files Extracted : {len(zip_files)}")

    return read_txt_files()


def get_quarter(file_name):

    file_name = file_name.upper()

    match = re.search(r"Q([1-4])", file_name)

    if match:
        return int(match.group(1))

    return 0


def read_txt_files():

    yearly_records = {
        2024: [],
        2025: [],
        2026: []
    }

    txt_files = []

    for root, dirs, files in os.walk(EXTRACT_FOLDER):

        for file in files:

            if file.lower().endswith(".txt"):
                txt_files.append(os.path.join(root, file))

    file_records = []

    for txt in txt_files:

        current_records = []

        with open(txt, "r", encoding="utf-8", errors="ignore") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if (
                    line.startswith("HDR")
                    or line.startswith("YEAR")
                    or line.startswith("2026 Clinical")
                    or line.startswith("CPT codes")
                    or line.startswith("The Department")
                ):
                    continue

                values = line.split("~")

                if len(values) < 7:
                    continue

                record = {
                    "YEAR": values[0].strip(),
                    "HCPCS": values[1].strip(),
                    "MODIFIER": values[2].strip(),
                    "EFFECTIVE_DATE": values[3].strip(),
                    "INDICATOR": values[4].strip(),
                    "RATE": values[5].strip(),
                    "SHORT_DESCRIPTION": values[6].strip()
                }

                current_records.append(record)

        if current_records:

            year = int(current_records[0]["YEAR"])

            filename = os.path.basename(txt)

            quarter = get_quarter(filename)

            file_records.append(
                (
                    year,
                    quarter,
                    filename,
                    current_records
                )
            )

    # Sort by Year then Quarter
    file_records.sort(
        key=lambda x: (
            x[0],
            x[1]
        )
    )

    print("\nTXT Processing Order")
    print("------------------------------------------------------------")

    total_records = 0

    for year, quarter, filename, current_records in file_records:

        print(f"{year} Q{quarter}  -->  {filename}")

        if year not in yearly_records:
            yearly_records[year] = []

        yearly_records[year].extend(current_records)

        total_records += len(current_records)

    print("------------------------------------------------------------")

    success(f"TXT Files Found      : {len(txt_files)}")
    success(f"Records Parsed      : {total_records}")

    return yearly_records