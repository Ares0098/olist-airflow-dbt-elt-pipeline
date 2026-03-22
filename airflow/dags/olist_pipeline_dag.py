from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import subprocess
import os

# ----------------------
# Default args
# ----------------------
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

# ----------------------
# DAG definition
# ----------------------
dag = DAG(
    "olist_elt_pipeline",
    default_args=default_args,
    description="Olist ELT pipeline with MinIO, Postgres, and dbt",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

# ----------------------
# Paths inside Airflow container
# ----------------------
SCRIPTS_PATH = "/opt/airflow/scripts"
DBT_ROOT_PATH = "/opt/airflow/dbt"            # contains profiles.yml
DBT_PROJECT_PATH = os.path.join(DBT_ROOT_PATH, "olist_project")  # dbt_project.yml inside this folder

# ----------------------
# Tasks
# ----------------------
def download_and_upload():
    script = os.path.join(SCRIPTS_PATH, "download_and_upload_to_minio.py")
    subprocess.run(["python", script], check=True)


def load_raw_postgres():
    script = os.path.join(SCRIPTS_PATH, "load_to_postgres.py")
    subprocess.run(["python", script], check=True)


def dbt_run():
    subprocess.run(
        ["dbt", "run", "--profiles-dir", DBT_ROOT_PATH],
        check=True,
        cwd=DBT_PROJECT_PATH,
    )


def dbt_test():
    subprocess.run(
        ["dbt", "test", "--profiles-dir", DBT_ROOT_PATH],
        check=True,
        cwd=DBT_PROJECT_PATH,
    )


# ----------------------
# Airflow Operators
# ----------------------
task_download = PythonOperator(
    task_id="download_and_upload_to_minio",
    python_callable=download_and_upload,
    dag=dag,
)

task_load_postgres = PythonOperator(
    task_id="load_raw_to_postgres",
    python_callable=load_raw_postgres,
    dag=dag,
)

task_dbt_run = PythonOperator(
    task_id="dbt_run",
    python_callable=dbt_run,
    dag=dag,
)

task_dbt_test = PythonOperator(
    task_id="dbt_test",
    python_callable=dbt_test,
    dag=dag,
)

# ----------------------
# Task dependencies
# ----------------------
task_download >> task_load_postgres >> task_dbt_run >> task_dbt_test