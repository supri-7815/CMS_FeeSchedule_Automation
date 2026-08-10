import os
import zipfile
import shutil
import sys

# Add project root to Python path
PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_FOLDER)

from utils import success


DOWNLOAD_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "Downloads"
)

PHYSICIAN_EXTRACT_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "Physician_Extracted"
)


def clean_physician_extracted():

    if os.path.exists(PHYSICIAN_EXTRACT_FOLDER):

        shutil.rmtree(
            PHYSICIAN_EXTRACT_FOLDER,
            ignore_errors=True
        )

    os.makedirs(
        PHYSICIAN_EXTRACT_FOLDER,
        exist_ok=True
    )


def extract_physician_files():

    clean_physician_extracted()

    txt_files = []

    # Summary counters
    summary = {
        "outer_zips": 0,
        "qp_zips_extracted": 0,
        "nonqp_zips_skipped": 0,
        "direct_txt_files": 0
    }

    outer_zip_files = [
        file
        for file in os.listdir(DOWNLOAD_FOLDER)
        if file.lower().endswith(".zip")
    ]

    if not outer_zip_files:

        print("\nNo Physician ZIP files found.")

        return []


    print("\nPhysician ZIP Extraction")
    print("------------------------------------------------------------")


    for outer_zip in outer_zip_files:

        summary["outer_zips"] += 1

        outer_zip_path = os.path.join(
            DOWNLOAD_FOLDER,
            outer_zip
        )

        print(
            f"\nLEVEL 1 ZIP : {outer_zip}"
        )


        # ==================================================
        # LEVEL 1
        # pfrev26c.zip
        # ==================================================

        outer_folder = os.path.join(
            PHYSICIAN_EXTRACT_FOLDER,
            os.path.splitext(outer_zip)[0]
        )

        os.makedirs(
            outer_folder,
            exist_ok=True
        )

        # Extract outer ZIP into its folder
        with zipfile.ZipFile(outer_zip_path, "r") as zip_ref:
            zip_ref.extractall(outer_folder)

        print("✓ Outer ZIP extracted")

        # ==================================================
        # FIND ALL INNER ZIP FILES
        # ==================================================

        inner_zip_files = []

        for root, dirs, files in os.walk(outer_folder):

            for file in files:

                if file.lower().endswith(".zip"):

                    inner_zip_files.append(os.path.join(root, file))

        print(f"✓ Inner ZIP files found : {len(inner_zip_files)}")

        # If no inner ZIPs found, check for TXT files directly inside the outer folder (TYPE 1)
        if not inner_zip_files:

            direct_txt_found = False

            for root, dirs, files in os.walk(outer_folder):

                for file in files:

                    if file.lower().endswith(".txt"):

                        txt_path = os.path.join(root, file)

                        txt_files.append(txt_path)

                        print(f"✓ TXT FOUND : {file}")

                        direct_txt_found = True

            if direct_txt_found:
                print("✓ No nested QP ZIP")
                summary["direct_txt_files"] += 1
                continue

            print("⚠ No inner ZIP and no TXT files found")

            continue

        # ==================================================
        # SELECT ONLY *_QP.ZIP (TYPE 2)
        # ==================================================

        qp_zip_files = [
            file for file in inner_zip_files
            if os.path.basename(file).upper().endswith("_QP.ZIP")
        ]

        nonqp_files = [
            file for file in inner_zip_files
            if file not in qp_zip_files
        ]

        if not qp_zip_files:

            # Do not extract non-QP inner zips; but still check if outer contains txts
            any_txt = False
            for root, dirs, files in os.walk(outer_folder):
                for file in files:
                    if file.lower().endswith('.txt'):
                        txt_path = os.path.join(root, file)
                        txt_files.append(txt_path)
                        print(f"✓ TXT FOUND : {file}")
                        any_txt = True

            if any_txt:
                print("✓ No nested QP ZIP")
                summary["direct_txt_files"] += 1
                continue

            print("⚠ No QP ZIP found; non-QP ZIPs skipped")
            for np in nonqp_files:
                print(f"✓ nonQP ZIP skipped : {os.path.basename(np)}")
                summary["nonqp_zips_skipped"] += 1

            continue

        print(f"✓ QP ZIP selected : {', '.join(os.path.basename(p) for p in qp_zip_files)}")
        for np in nonqp_files:
            print(f"✓ nonQP ZIP skipped : {os.path.basename(np)}")

        for qp_zip_path in qp_zip_files:

            qp_zip_name = os.path.basename(qp_zip_path)

            print(f"\nLEVEL 2 ZIP : {qp_zip_name}")

            qp_folder = os.path.join(outer_folder, "QP_EXTRACTED")
            os.makedirs(qp_folder, exist_ok=True)

            with zipfile.ZipFile(qp_zip_path, "r") as qp_zip_ref:
                qp_zip_ref.extractall(qp_folder)

            print("✓ QP ZIP extracted")
            summary["qp_zips_extracted"] += 1

            # Find TXT files after QP extraction
            for root, dirs, files in os.walk(qp_folder):
                for file in files:
                    if file.lower().endswith('.txt'):
                        txt_path = os.path.join(root, file)
                        txt_files.append(txt_path)
                        print(f"✓ TXT FOUND : {file}")


    print(
        "\n------------------------------------------------------------"
    )

    success(
        f"Physician TXT Files Found : "
        f"{len(txt_files)}"
    )

    return txt_files, summary