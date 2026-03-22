from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

# import your scripts
from scripts.download_dataset import download_olist_data
from scripts.upload_to_minio import upload_to_minio
from scripts.load_to_postgres import load_to_postgres


default_args = {
    "owner": "ares",
    "retries": 1,
}


with DAG(
    dag_id="olist_elt_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # manual trigger
    catchup=False,
) as dag:

    # 1. Download dataset
    download_task = PythonOperator(
        task_id="download_dataset",
        python_callable=download_olist_data,
    )

    # 2. Upload to MinIO
    upload_task = PythonOperator(
        task_id="upload_to_minio",
        python_callable=upload_to_minio,
    )

    # 3. Load to Postgres (raw layer)
    load_task = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres,
    )

    # 4. Run dbt models
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt/olist_project && dbt run",
    )

    # 5. Run dbt tests
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt/olist_project && dbt test",
    )

    # dependencies
    download_task >> upload_task >> load_task >> dbt_run >> dbt_test