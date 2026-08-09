import pymysql
from utils import success

HOST = "127.0.0.1"
PORT = 3306
USER = "root"
PASSWORD = "Supriii@123"
DATABASE = "cms_fee_schedule"


def get_connection():

    return pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        autocommit=True
    )


def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    print("Creating table...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CLFS_DATA(

        PROCEDURE_FEE_YEAR INT,

        PROCEDURE_CODE VARCHAR(20),

        MDCRC_CARRIER_ID VARCHAR(20),

        MDCR_FEE_SCHD_ID VARCHAR(20),

        PCD_MODIFIER VARCHAR(20),

        FEE_SCHD_PRICE DECIMAL(10,2),

        POS_FEE_SCHD_PRICE DECIMAL(10,2),

        FEE_SCHD_TYPE_CODE VARCHAR(10),

        PRIMARY KEY (PROCEDURE_FEE_YEAR, PROCEDURE_CODE)

    )
    """)

    connection.commit()

    print("Table created successfully.")

    cursor.close()
    connection.close()
def save_records(records):

    connection = get_connection()
    cursor = connection.cursor()

    # Read existing Procedure Code + Year combinations
    cursor.execute("""
        SELECT PROCEDURE_CODE, PROCEDURE_FEE_YEAR
        FROM CLFS_DATA
    """)

    existing_records = {
        (row[0], row[1])
        for row in cursor.fetchall()
    }

    new_records = 0
    updated_records = 0

    data = []

    for record in records:

        key = (
            record["HCPCS"],
            int(record["YEAR"])
        )

        if key in existing_records:
            updated_records += 1
        else:
            new_records += 1
            existing_records.add(key)

        data.append((
            record["HCPCS"],
            None,
            None,
            record["MODIFIER"],
            int(record["YEAR"]),
            float(record["RATE"]),
            float(record["RATE"]),
            record["INDICATOR"]
        ))

    query = """
    INSERT INTO CLFS_DATA
    (
        PROCEDURE_CODE,
        MDCRC_CARRIER_ID,
        MDCR_FEE_SCHD_ID,
        PCD_MODIFIER,
        PROCEDURE_FEE_YEAR,
        FEE_SCHD_PRICE,
        POS_FEE_SCHD_PRICE,
        FEE_SCHD_TYPE_CODE
    )

    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s)

    ON DUPLICATE KEY UPDATE

        PCD_MODIFIER = VALUES(PCD_MODIFIER),
        FEE_SCHD_PRICE = VALUES(FEE_SCHD_PRICE),
        POS_FEE_SCHD_PRICE = VALUES(POS_FEE_SCHD_PRICE),
        FEE_SCHD_TYPE_CODE = VALUES(FEE_SCHD_TYPE_CODE);
    """

    cursor.executemany(query, data)

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*)
        FROM CLFS_DATA
    """)

    total_records = cursor.fetchone()[0]

    success(f"Database              : {DATABASE}")
    success("Table                 : CLFS_DATA")
    success(f"New Procedures        : {new_records}")
    success(f"Updated Procedures    : {updated_records}")
    success(f"Unique HCPCS+Year     : {total_records}")
    success(f"Records Processed     : {len(records)}")

    cursor.close()
    connection.close()