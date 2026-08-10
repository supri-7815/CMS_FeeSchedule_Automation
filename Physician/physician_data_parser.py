import csv
import io
import os
import re
from decimal import Decimal, InvalidOperation


FIELD_MAP = [
    "YEAR",
    "CARRIER",
    "LOCALITY",
    "HCPCS",
    "MODIFIER",
    "NON_FACILITY_RATE",
    "FACILITY_RATE",
    "FILLER",
    "PCTC_INDICATOR",
    "STATUS_CODE",
    "MULTIPLE_SURGERY_INDICATOR",
    "THERAPY_NON_FACILITY",
    "THERAPY_FACILITY",
    "OPPS_INDICATOR",
    "OPPS_NON_FACILITY",
    "OPPS_FACILITY",
]


def safe_decimal(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value == "-":
        return None

    value = value.replace(",", "")

    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid decimal value: {value}") from exc


def get_file_order(path):

    filename = os.path.basename(path).upper()

    # ---------------------------------------------------------
    # 2024
    # ---------------------------------------------------------

    # 2024 A
    if filename == "PFALL24.TXT":
        return (2024, 1)

    # 2024 AR
    if filename == "PFALL24R.TXT":
        return (2024, 2)

    # 2024 C
    if filename == "PFREV3.TXT":
        return (2024, 3)

    # ---------------------------------------------------------
    # 2025
    # ---------------------------------------------------------

    # 2025 A
    if filename == "PFALL25.TXT":
        return (2025, 1)

    # 2025 B
    if filename == "PFREV2.TXT":
        return (2025, 2)

    # 2025 C
    if filename == "PFREV25C.TXT":
        return (2025, 3)

    # 2025 D
    if filename == "PFREV4.TXT":
        return (2025, 4)

    # ---------------------------------------------------------
    # 2026
    # ---------------------------------------------------------

    # 2026 A / AR
    if filename == "PFALL26AR.TXT":
        return (2026, 1)

    # 2026 B
    if filename == "PFREV26B.TXT":
        return (2026, 2)

    # 2026 C
    if filename == "PFREV26C.TXT":
        return (2026, 3)

    # ---------------------------------------------------------
    # Unknown file
    # ---------------------------------------------------------

    return (9999, 9999)
def parse_physician_txt_files(txt_file_paths):

    latest_records = {}

    total_malformed = 0
    total_footer_skipped = 0
    per_file_counts = {}

    # Oldest quarter -> newest quarter
    ordered_paths = sorted(
        txt_file_paths,
        key=get_file_order
    )

    for path in ordered_paths:

        filename = os.path.basename(path)

        valid_count = 0
        malformed_count = 0
        footer_to_skip = 0

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as fh:

                all_lines = fh.readlines()

            # Ignore last 4 lines of every TXT
            if len(all_lines) >= 4:
                footer_to_skip = 4
                lines_to_parse = all_lines[:-4]
            else:
                footer_to_skip = len(all_lines)
                lines_to_parse = []

            total_footer_skipped += footer_to_skip

            reader = csv.reader(
                io.StringIO("".join(lines_to_parse))
            )

            for row in reader:

                row = [
                    column.strip()
                    for column in row
                ]

                if not row:
                    continue

                if len(row) != 16:
                    malformed_count += 1
                    total_malformed += 1
                    continue

                try:

                    record = {
                        "YEAR": int(row[0]),

                        "CARRIER": (
                            row[1] if row[1] else None
                        ),

                        "LOCALITY": (
                            row[2] if row[2] else None
                        ),

                        "HCPCS": (
                            row[3] if row[3] else None
                        ),

                        "MODIFIER": (
                            row[4] if row[4] else None
                        ),

                        "NON_FACILITY_RATE":
                            safe_decimal(row[5]),

                        "FACILITY_RATE":
                            safe_decimal(row[6]),

                        "FILLER": (
                            row[7] if row[7] else None
                        ),

                        "PCTC_INDICATOR": (
                            row[8] if row[8] else None
                        ),

                        "STATUS_CODE": (
                            row[9] if row[9] else None
                        ),

                        "MULTIPLE_SURGERY_INDICATOR": (
                            row[10] if row[10] else None
                        ),

                        "THERAPY_NON_FACILITY":
                            safe_decimal(row[11]),

                        "THERAPY_FACILITY":
                            safe_decimal(row[12]),

                        "OPPS_INDICATOR": (
                            row[13] if row[13] else None
                        ),

                        "OPPS_NON_FACILITY":
                            safe_decimal(row[14]),

                        "OPPS_FACILITY":
                            safe_decimal(row[15])
                    }

                except Exception:

                    malformed_count += 1
                    total_malformed += 1
                    continue

                # ------------------------------------------------
                # BUSINESS KEY
                # YEAR + HCPCS
                #
                # Files are processed oldest -> newest.
                # Therefore the latest quarter overwrites
                # the previous quarter automatically.
                # ------------------------------------------------

                hcpcs = record["HCPCS"]

                if hcpcs:

                    key = (
                        record["YEAR"],
                        hcpcs
                    )

                    latest_records[key] = record

                valid_count += 1

        except FileNotFoundError:

            per_file_counts[filename] = {
                "valid": 0,
                "malformed": 0,
                "footer_skipped": 0
            }

            continue

        per_file_counts[filename] = {
            "valid": valid_count,
            "malformed": malformed_count,
            "footer_skipped": footer_to_skip
        }

    # Final unique records only
    records = list(
        latest_records.values()
    )

    source_records = sum(
        item["valid"]
        for item in per_file_counts.values()
    )

    print("\nPhysician parsing completed")
    print(
        f"Source records processed : {source_records}"
    )
    print(
        f"Unique YEAR + HCPCS      : {len(records)}"
    )

    return (
        records,
        len(records),
        total_malformed,
        per_file_counts
    )