from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import ShortCircuitOperator

# import fix (version safe)
try:
    from airflow.operators.trigger_dagrun import TriggerDagRunOperator
except:
    from airflow.operators.dagrun_operator import TriggerDagRunOperator

from docker.types import Mount
import os


# CONFIG
DATA_PATH = "/opt/airflow/data"

REQUIRED_FILES = [
    "eu_fsf_sanctions.json",
    "inegi_playwright.json",
    "inegi_scraper.json",
    "kaldata.db",
    "telegraph.db",
]

LOCK_FILE = "/opt/airflow/data/merge.lock"


def all_outputs_ready():
    if os.path.exists(LOCK_FILE):
        print("Merge already triggered")
        return False

    existing = os.listdir(DATA_PATH)
    print("Existing:", existing)

    for f in REQUIRED_FILES:
        if f not in existing:
            print(f"Missing: {f}")
            return False

    print("ALL FILES READY")

    # lock 
    open(LOCK_FILE, "w").close()

    return True



# DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="inegi_playwright",
    description="INEGI sanctions scraper (Playwright)",
    default_args=default_args,
    start_date=datetime(2026, 2, 2),
    schedule_interval="@daily",
    catchup=False,
    tags=["inegi", "sanctions", "playwright", "production"],
) as dag:

    run_inegi_playwright = DockerOperator(
        task_id="run_inegi_playwright",
        image="inegi-playwright:v1",
        api_version="auto",
        auto_remove=True,
        network_mode="bridge",
        mounts=[
            Mount(
                source="C:/Users/User/desktop/docker-projects/data",
                target="/app/data",
                type="bind",
            )
        ],
        shm_size=1024 * 1024 * 1024,
        ipc_mode="host",
        execution_timeout=timedelta(minutes=30),
        tty=True,
        do_xcom_push=False,
        retries=0,
        mount_tmp_dir=False,
    )

    # CHECK
    # check_all_done = ShortCircuitOperator(
    #     task_id="check_all_outputs_ready",
    #     python_callable=all_outputs_ready,
    # )

    # TRIGGER MERGE
    trigger_merge = TriggerDagRunOperator(
        task_id="trigger_merge",
        trigger_dag_id="merge_all_scrapers",
    )

    # Critical 
    # run_inegi_playwright >> check_all_done >> trigger_merge
    run_inegi_playwright >> trigger_merge