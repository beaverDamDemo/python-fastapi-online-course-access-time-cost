import psycopg2
import os
import re
import csv
from dotenv import load_dotenv
import argparse


# --- CONFIG ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

CSV_FOLDER = os.path.dirname(os.path.abspath(__file__))  # same folder as script
GREEN = "\033[92m"
YELLOW = "\033[93m"
VIOLET = "\033[95m"
RESET = "\033[0m"


def import_csv_to_db(csv_path, student_id, DATABASE_URL):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # 0. Ensure student_id exists in fastapi_students
    cur.execute(
        """
        INSERT INTO fastapi_students (student_id)
        OVERRIDING SYSTEM VALUE
        VALUES (%s)
        ON CONFLICT (student_id) DO NOTHING;
    """,
        (student_id,),
    )

    # 1. Create temp table
    cur.execute(
        """
        CREATE TEMP TABLE fastapi_tmp_import (
            timestamp TEXT,
            used_credits TEXT,
            credit_price TEXT
        );
    """
    )

    # 2. Load CSV into temp table
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)

        # Check if first row is a header
        try:
            float(rows[0][1].replace(",", "."))
            float(rows[0][2].replace(",", "."))
            has_header = False
        except (ValueError, IndexError):
            has_header = True

        # Write to temp file for COPY
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            writer = csv.writer(tmp, delimiter=";")
            for row in rows[1:] if has_header else rows:
                writer.writerow(row)
            tmp_path = tmp.name

        with open(tmp_path, "r", encoding="utf-8") as tmp_file:
            cur.copy_expert(
                "COPY fastapi_tmp_import(timestamp, used_credits, credit_price) FROM STDIN WITH (FORMAT csv, DELIMITER ';')",
                tmp_file,
            )

    # 3. Count rows in temp table
    cur.execute("SELECT COUNT(*) FROM fastapi_tmp_import;")
    row_count = cur.fetchone()[0]

    # 4. Insert into main table with fixed student_id
    cur.execute(
        """
        INSERT INTO fastapi_inserted_data (timestamp, used_credits, credit_price, student_id)
        SELECT
            timestamp::timestamptz,
            REPLACE(used_credits, ',', '.')::double precision,
            REPLACE(credit_price, ',', '.')::double precision,
            %s
        FROM fastapi_tmp_import;
    """,
        (student_id,),
    )

        # Compute period_start, period_end, and total
    cur.execute(
        """
        SELECT MIN(timestamp), MAX(timestamp), SUM(used_credits * credit_price)
        FROM fastapi_inserted_data
        WHERE student_id = %s;
        """,
        (student_id,),
    )
    period_start, period_end, total = cur.fetchone()

    # 6. Insert into invoices table
    cur.execute(
        """
        INSERT INTO fastapi_invoices (student_id, period_start, period_end, total)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """,
        (student_id, period_start, period_end, total),
    )
    invoice_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    # 5. Log to terminal (green for success)
    print(
        f"{GREEN}✅ Imported {row_count} rows from '{os.path.basename(csv_path)}' with student_id={student_id}{RESET}"
    )
    return row_count


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Import CSVs into the database")
    parser.add_argument(
        "--env", choices=["dev", "prod"], required=True, help="Which environment to use"
    )
    args = parser.parse_args()

    # Load the appropriate .env file
    env_file = ".env.dev" if args.env == "dev" else ".env.prod"

    if not os.path.exists(env_file):
        print(
            f"{YELLOW}❌ Environment file '{env_file}' not found. Please create it or specify the correct path.{RESET}"
        )
        return

    load_dotenv(dotenv_path=env_file)

    # Get the database URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print(f"{YELLOW}❌ DATABASE_URL not found in {env_file}{RESET}")
        return

    print(f"{GREEN}🔌 Connecting to database defined in {env_file}{RESET}")

    total_rows = 0
    for filename in os.listdir(CSV_FOLDER):
        print(f"{VIOLET}📄 Found file: {filename}{RESET}")

        if filename.lower().endswith(".csv") and "data-student-id-" in filename:
            match = re.search(r"data-student-id-(\d+)", filename)
            if match:
                student_id = int(match.group(1))
                csv_path = os.path.join(CSV_FOLDER, filename)
                print(f"{YELLOW}📄 Processing file: {filename}{RESET}")
                total_rows += import_csv_to_db(csv_path, student_id, DATABASE_URL)

    if total_rows == 0:
        print(f"{YELLOW}⚠️  No matching CSV files found in {CSV_FOLDER}{RESET}")
    else:
        print(f"{YELLOW}📊 Total rows inserted: {total_rows}{RESET}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
