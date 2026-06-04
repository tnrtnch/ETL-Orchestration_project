from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook

import os
import json
import sqlite3
import hashlib
import time


# PATHS
DATA_PATH = "/opt/airflow/data"
print("DATA_PATH:", DATA_PATH)
print("FILES:", os.listdir(DATA_PATH))


OUTPUT_FILE = os.path.join(DATA_PATH, "final_output.json")
LOCK_FILE = os.path.join(DATA_PATH, "merge.lock")
print("LOCK EXISTS:", os.path.exists(LOCK_FILE))



# UNIQUE KEY
def generate_key(item):
    key = (
        item.get("proveedor")
        or item.get("name")
        or item.get("title")
        or item.get("url")
        or item.get("numero")
    )


    if isinstance(key, list):
        key = "_".join(sorted(set(key)))

    if not key:
        key = json.dumps(item, sort_keys=True)

    source = item.get("origin") or item.get("source") or ""

    final_key = f"{key}_{source}"

    return hashlib.md5(final_key.encode("utf-8")).hexdigest()



# MERGE FUNCTION
def merge_all():
    if os.path.exists(LOCK_FILE):
        age = time.time() - os.path.getmtime(LOCK_FILE)
        if age < 600:  # 10 min
            print(" Merge already running, skipping...")
            return

    # CREATE LOCK
    open(LOCK_FILE, "w").close()

    try:
        all_items = []

        print(f"📂 DATA PATH: {DATA_PATH}")

        
        # READ FILES
        for root, dirs, files in os.walk(DATA_PATH):
            for file in files:
                file_path = os.path.join(root, file)

                if file == "final_output.json":
                    continue

                # SQLITE
                if file.endswith(".db"):
                    try:
                        print(f"\nREADING DB: {file}")

                        conn = sqlite3.connect(file_path)
                        cursor = conn.cursor()

                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table';"
                        )
                        table = cursor.fetchone()[0]

                        cursor.execute(f"SELECT * FROM {table}")
                        rows = cursor.fetchall()
                        columns = [col[0] for col in cursor.description]

                        for row in rows:
                            item = dict(zip(columns, row))
                            item["source"] = file
                            all_items.append(item)

                        conn.close()

                    except Exception as e:
                        print(f"DB ERROR {file}: {e}")

                # JSON
                elif file.endswith(".json"):
                    try:
                        print(f"\nREADING JSON: {file}")

                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)

                        # if isinstance(data, dict):
                        #     if "data" in data:
                        #         data = data["data"]
                        #     elif "items" in data:
                        #         data = data["items"]
                        #     else:
                        #         data = [data]

                        # if not isinstance(data, list):
                        #     data = []

                        # if isinstance(data, dict):
                        #     for key in ["data", "items", "results", "records"]:
                        #         if key in data:
                        #             data = data[key]
                        #             break
                        #     else:
                        #         data = [data]

                        if isinstance(data, dict):
                            if "data" in data and isinstance(data["data"], list):
                                data = data["data"]
                            elif "items" in data and isinstance(data["items"], list):
                                data = data["items"]
                            elif "results" in data and isinstance(data["results"], list):
                                data = data["results"]
                            else:
                                print(f"UNKNOWN JSON STRUCTURE: {file}")
                                data = []


                        for item in data:
                            if isinstance(item, dict):
                                item["source"] = file
                                all_items.append(item)

                    except Exception as e:
                        print(f"JSON ERROR {file}: {e}")

        print(f"\nTOTAL BEFORE DEDUP: {len(all_items)}")


        # DEDUP
        seen = set()
        unique_items = []

        for item in all_items:
            try:
                key = generate_key(item)

                if key not in seen:
                    seen.add(key)
                    unique_items.append(item)

            except Exception as e:
                print(f"DEDUP ERROR: {e}")

        print(f"AFTER DEDUP: {len(unique_items)}")


        # SAVE
        save_to_postgres(unique_items)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(unique_items, f, ensure_ascii=False, indent=2)

        print(f"JSON OUTPUT: {OUTPUT_FILE}")

    except Exception as e:
        print("MERGE ERROR:", e)

    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            print("LOCK REMOVED")



def save_to_postgres(items):
    hook = PostgresHook(postgres_conn_id="postgres_default")
    conn = hook.get_conn()
    cursor = conn.cursor()

    for item in items:
        try:
            key = generate_key(item)

            # SANCTIONS         
            if (
                item.get("sanction_numbers")
                or item.get("numero")
                or item.get("proveedor")
                or item.get("sanctions")
                or item.get("schema")
            ):
                
                name = (
                    item.get("proveedor")
                    or item.get("name")
                    or item.get("Entity_name")
                )

                cursor.execute(
                    """
                    INSERT INTO sanctions (name, extra, source, unique_key)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (unique_key) DO UPDATE SET
                        extra = EXCLUDED.extra,
                        source = EXCLUDED.source
                    """,
                    (name, json.dumps(item), item.get("source"), key),
                )

    

            # NEWS
            elif item.get("title") and item.get("body"):

                url = item.get("url")

                if not url:
                    url = hashlib.md5(
                        (item.get("title","") + item.get("body","")).encode()
                    ).hexdigest()

                cursor.execute(
                    """
                    INSERT INTO news (title, body, author, url, source)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        body = EXCLUDED.body,
                        author = EXCLUDED.author,
                        source = EXCLUDED.source
                    """,
                    (
                        item.get("title"),
                        item.get("body"),
                        item.get("author"),
                        url,
                        item.get("source"),
                    ),
                )


            # RAW
            else:
                cursor.execute(
                    """
                    INSERT INTO raw_data (data, source, unique_key)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (unique_key) DO NOTHING
                    """,
                    (
                        json.dumps(item), 
                        item.get("source"),
                        key,
                    ),
                )

        except Exception as e:
            conn.rollback()
            print("DB INSERT ERROR:", e)

    conn.commit()
    cursor.close()




# DAG
with DAG(
    dag_id="merge_all_scrapers",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["merge", "final"],
) as dag:

    merge_task = PythonOperator(
        task_id="merge_all_outputs",
        python_callable=merge_all,
    )

