from decimal import Decimal
from database import get_connection


def normalize_nullable_string(value):
    if value is None:
        return None

    text = str(value).strip()

    if text == "" or text == "-":
        return None

    return text


def normalize_decimal(value):
    if value is None:
        return None

    if isinstance(value, Decimal):
        return value

    text = str(value).strip()

    if text == "" or text == "-":
        return None

    text = text.replace(",", "")

    try:
        return Decimal(text)
    except Exception as exc:
        raise ValueError(
            f"Invalid decimal value: {value}"
        ) from exc


def build_physician_row(record):
    return (
        int(record["YEAR"]),
        normalize_nullable_string(record["HCPCS"]),
        normalize_nullable_string(record["CARRIER"]),
        normalize_nullable_string(record["LOCALITY"]),
        normalize_nullable_string(record["MODIFIER"]),
        normalize_decimal(record["NON_FACILITY_RATE"]),
        normalize_decimal(record["FACILITY_RATE"]),
        normalize_nullable_string(record["STATUS_CODE"]),
    )


def save_physician_records(records, batch_size=5000):

    connection = get_connection()
    cursor = connection.cursor()

    total = len(records)

    print("\nStarting Physician database update...")
    print("------------------------------------------------------------")
    print(f"Physician records received : {total}")

    # ========================================================
    # STEP 1
    # Create temporary staging table
    # ========================================================

    print("Creating temporary staging table...")

    cursor.execute("""
        CREATE TEMPORARY TABLE physician_stage (
            PROCEDURE_FEE_YEAR INT NOT NULL,
            PROCEDURE_CODE VARCHAR(20) NOT NULL,
            MDCRC_CARRIER_ID VARCHAR(20),
            MDCR_FEE_SCHD_ID VARCHAR(20),
            PCD_MODIFIER VARCHAR(20),
            FEE_SCHD_PRICE DECIMAL(10,2),
            POS_FEE_SCHD_PRICE DECIMAL(10,2),
            FEE_SCHD_TYPE_CODE VARCHAR(10),

            PRIMARY KEY (
                PROCEDURE_FEE_YEAR,
                PROCEDURE_CODE
            )
        ) ENGINE=InnoDB
    """)

    # ========================================================
    # STEP 2
    # Prepare unique YEAR + HCPCS records
    #
    # Latest record wins because parser already gives
    # records in old -> new quarter order.
    # ========================================================

    unique_records = {}

    for record in records:

        (
            year,
            procedure_code,
            carrier,
            locality,
            modifier,
            non_facility_rate,
            facility_rate,
            status_code
        ) = build_physician_row(record)

        if procedure_code is None:
            continue

        key = (
            year,
            procedure_code
        )

        # Latest quarter overwrites previous quarter
        unique_records[key] = (
            year,
            procedure_code,
            carrier,
            locality,
            modifier,
            non_facility_rate,
            facility_rate,
            status_code
        )

    unique_data = list(unique_records.values())

    print(
        f"Unique YEAR + HCPCS records : "
        f"{len(unique_data)}"
    )

    # ========================================================
    # STEP 3
    # Bulk insert into temporary table
    # ========================================================

    stage_insert = """
        INSERT INTO physician_stage
        (
            PROCEDURE_FEE_YEAR,
            PROCEDURE_CODE,
            MDCRC_CARRIER_ID,
            MDCR_FEE_SCHD_ID,
            PCD_MODIFIER,
            FEE_SCHD_PRICE,
            POS_FEE_SCHD_PRICE,
            FEE_SCHD_TYPE_CODE
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s
        )
    """

    print("Loading staging table...")

    for start in range(0, len(unique_data), batch_size):

        batch = unique_data[
            start:start + batch_size
        ]

        cursor.executemany(
            stage_insert,
            batch
        )

        print(
            f"Staging : "
            f"{min(start + batch_size, len(unique_data))}"
            f"/{len(unique_data)}"
        )

    connection.commit()

    # ========================================================
    # STEP 4
    # UPDATE existing Physician records
    #
    # Clinical records are NOT touched because of the
    # Physician identification condition.
    # ========================================================

    print("Updating existing Physician records...")

    cursor.execute("""
        UPDATE CLFS_DATA c
        INNER JOIN physician_stage s
            ON c.PROCEDURE_FEE_YEAR = s.PROCEDURE_FEE_YEAR
           AND c.PROCEDURE_CODE = s.PROCEDURE_CODE

        SET
            c.FEE_SCHD_PRICE = s.FEE_SCHD_PRICE,
            c.POS_FEE_SCHD_PRICE = s.POS_FEE_SCHD_PRICE,
            c.FEE_SCHD_TYPE_CODE = s.FEE_SCHD_TYPE_CODE,
            c.MDCRC_CARRIER_ID = s.MDCRC_CARRIER_ID,
            c.MDCR_FEE_SCHD_ID = s.MDCR_FEE_SCHD_ID,
            c.PCD_MODIFIER = s.PCD_MODIFIER

        WHERE c.MDCRC_CARRIER_ID IS NOT NULL
          AND c.MDCR_FEE_SCHD_ID IS NOT NULL
    """)

    updated_records = cursor.rowcount

    connection.commit()

    print(
        f"Updated Physician records : "
        f"{updated_records}"
    )

    # ========================================================
    # STEP 5
    # INSERT new Physician records
    #
    # Clinical records are ignored.
    # ========================================================

    print("Inserting new Physician records...")

    cursor.execute("""
        INSERT INTO CLFS_DATA
        (
            PROCEDURE_FEE_YEAR,
            PROCEDURE_CODE,
            MDCRC_CARRIER_ID,
            MDCR_FEE_SCHD_ID,
            PCD_MODIFIER,
            FEE_SCHD_PRICE,
            POS_FEE_SCHD_PRICE,
            FEE_SCHD_TYPE_CODE
        )

        SELECT
            s.PROCEDURE_FEE_YEAR,
            s.PROCEDURE_CODE,
            s.MDCRC_CARRIER_ID,
            s.MDCR_FEE_SCHD_ID,
            s.PCD_MODIFIER,
            s.FEE_SCHD_PRICE,
            s.POS_FEE_SCHD_PRICE,
            s.FEE_SCHD_TYPE_CODE

        FROM physician_stage s

        LEFT JOIN CLFS_DATA c
            ON c.PROCEDURE_FEE_YEAR =
               s.PROCEDURE_FEE_YEAR

           AND c.PROCEDURE_CODE =
               s.PROCEDURE_CODE

           AND c.MDCRC_CARRIER_ID IS NOT NULL
           AND c.MDCR_FEE_SCHD_ID IS NOT NULL

        WHERE c.PROCEDURE_CODE IS NULL
    """)

    new_records = cursor.rowcount

    connection.commit()

    print(
        f"New Physician records : "
        f"{new_records}"
    )

    # ========================================================
    # STEP 6
    # Final count
    # ========================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM CLFS_DATA
    """)

    total_records = cursor.fetchone()[0]

    # ========================================================
    # STEP 7
    # Physician count
    # ========================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM CLFS_DATA
        WHERE MDCRC_CARRIER_ID IS NOT NULL
          AND MDCR_FEE_SCHD_ID IS NOT NULL
    """)

    physician_total = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    print("\n------------------------------------------------------------")
    print("CMS table                  : CLFS_DATA")
    print(
        f"New Physician records      : "
        f"{new_records}"
    )
    print(
        f"Updated Physician records  : "
        f"{updated_records}"
    )
    print(
        f"Unique records processed   : "
        f"{len(unique_data)}"
    )
    print(
        f"Physician total rows       : "
        f"{physician_total}"
    )
    print(
        f"CMS total rows             : "
        f"{total_records}"
    )
    print(
        "Physician database update completed successfully."
    )

    return {
        "processed": len(unique_data),
        "total_rows": total_records,
        "new_records": new_records,
        "updated_records": updated_records
    }