from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta
import uuid
import json
import time
from google.cloud import bigquery, storage
from collections import defaultdict

# ---------------------------
# Metadata logging function
# ---------------------------
def log_metadata(run_id, file_location, stage, status, start_time, end_time, row_count=None, column_count=None):
    PROJECT_ID = "x-oxygen-468806-d1"
    DATASET_ID = "P1"
    TABLE_ID = "metadata_log"

    bq_client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    filename = file_location.split("/")[-1] if file_location else None

    row = {
        "run_id": run_id,
        "filename": filename,
        "file_path": file_location,
        "stage": stage,
        "status": status,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "row_count": row_count,
        "column_count": column_count,
        "timestamp": datetime.utcnow().isoformat()
    }

    errors = bq_client.insert_rows_json(table_ref, [row])
    if errors:
        print(f"Error logging metadata for {stage}: {errors}")
    else:
        print(f"Metadata logged for {stage}: {status}")

# ---------------------------
# Default DAG arguments
# ---------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ---------------------------
# DAG Definition
# ---------------------------
with DAG(
    dag_id='new_sensor_preprocess_bq_sdp_notify',
    default_args=default_args,
    description='Sensor DAG with multiple stages: file check -> preliminary checks -> BQ dump -> SDP -> notification',
    schedule_interval=None,
    start_date=datetime(2025, 8, 29),
    catchup=False,
    max_active_runs=1,
    tags=['sensor', 'preprocess', 'bq', 'sdp', 'notify']
) as dag:

    # ---------------------------
    # Stage 0: Wait for file in GCS
    # ---------------------------
    wait_for_gcs_file = GCSObjectExistenceSensor(
        task_id="wait_for_gcs_file",
        bucket="landing_bucket_01",
        object="staging/myfile.jsonl",
        poke_interval=30,
        timeout=60 * 60,
    )

    # ---------------------------
    # Stage 1: Detect new file and generate run_id
    # ---------------------------
    def gcs_file_detected(ti, **kwargs):
        start_time = datetime.utcnow()

        bucket_name = 'landing_bucket_01'
        prefix = 'staging/'

        storage_client = storage.Client()
        blobs = list(storage_client.list_blobs(bucket_name, prefix=prefix))
        if not blobs:
            raise ValueError(f"No files found under gs://{bucket_name}/{prefix}")

        latest_blob = max(blobs, key=lambda b: b.updated)
        file_location = f"gs://{bucket_name}/{latest_blob.name}"
        run_id = str(uuid.uuid4())

        end_time = datetime.utcnow()
        log_metadata(run_id, file_location, stage="check_for_files", status="success",
                     start_time=start_time, end_time=end_time)

        ti.xcom_push(key='file_location', value=file_location)
        ti.xcom_push(key='run_id', value=run_id)

        print(f"Detected file: {file_location}, run_id: {run_id}")

    check_for_files_task = PythonOperator(
        task_id='check_for_files',
        python_callable=gcs_file_detected
    )

    # ---------------------------
    # Stage 2: Preliminary checks via Bash script
    # ---------------------------
    preliminary_checks_task = BashOperator(
        task_id="preliminary_checks",
        bash_command=(
            "gsutil cp gs://landing_bucket_01/scripts/jsonl_check.py /tmp/jsonl_check.py && "
            "python /tmp/jsonl_check.py "
            "{{ ti.xcom_pull(key='file_location', task_ids='check_for_files') }}"
        )
    )

    # ---------------------------
    # Stage 3: Dump data to BigQuery
    # ---------------------------
##

    

    def infer_bq_type_from_values(values):
        """Infer BigQuery type from a list of non-null values."""
        # If no values (all nulls) → default STRING
        if not values:
            return "STRING"

        # Check type hierarchy
        all_int = all(isinstance(v, int) for v in values)
        all_float = all(isinstance(v, (int, float)) for v in values)
        all_bool = all(isinstance(v, bool) for v in values)

        if all_bool:
            return "BOOLEAN"
        elif all_int:
            return "INTEGER"
        elif all_float:
            return "FLOAT"
        else:
            return "STRING"


###
def ensure_schema_updated(bq_client, table_ref, expected_fields, max_retries=5, wait_seconds=2):
    """
    Ensure that the BigQuery table schema includes all expected_fields.
    Retries until schema propagation completes.
    """
    for attempt in range(max_retries):
        table = bq_client.get_table(table_ref)
        existing_fields = {f.name for f in table.schema}

        missing = [f for f in expected_fields if f not in existing_fields]
        if not missing:
            print(f"Schema update verified. All expected columns exist: {expected_fields}")
            return table  # Updated schema

        print(f"Attempt {attempt+1}/{max_retries}: Missing columns {missing}, retrying in {wait_seconds}s...")
        time.sleep(wait_seconds)

    raise RuntimeError(f"Schema not updated after {max_retries} retries. Still missing: {missing}")


def dump_to_bq(ti, **kwargs):
    start_time = datetime.utcnow()
    file_location = ti.xcom_pull(key='file_location', task_ids='check_for_files')
    run_id = ti.xcom_pull(key='run_id', task_ids='check_for_files')

    log_metadata(run_id, file_location, stage="dump_to_bq", status="started",
                 start_time=start_time, end_time=start_time)

    PROJECT_ID = "x-oxygen-468806-d1"
    DATASET_ID = "P1"
    TABLE_ID = "jsonl_dump_2"

    bq_client = bigquery.Client(project=PROJECT_ID)
    storage_client = storage.Client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    # 1. Check if table exists
    try:
        table = bq_client.get_table(table_ref)
        table_exists = True
        existing_schema = {f.name: f.field_type for f in table.schema}
        print(f"Table {table_ref} exists, using schema: {existing_schema}")
    except Exception:
        table_exists = False
        existing_schema = {}
        print(f"Table {table_ref} does not exist, will create with autodetect.")

    # 2. Collect field values
    bucket_name, blob_name = file_location.replace("gs://", "").split("/", 1)
    blob = storage_client.bucket(bucket_name).blob(blob_name)
    raw_data = blob.download_as_bytes().decode("utf-8").splitlines()

    field_values = defaultdict(list)
    for line in raw_data:
        if not line.strip():
            continue
        record = json.loads(line)
        for field, value in record.items():
            if value is not None:
                field_values[field].append(value)

    # 3. Alter schema if needed
    if table_exists:
        alter_statements = []
        new_fields = []
        for field, values in field_values.items():
            if field not in existing_schema:
                inferred_type = infer_bq_type_from_values(values)
                alter_statements.append(f"ADD COLUMN IF NOT EXISTS {field} {inferred_type}")
                new_fields.append(field)

        if alter_statements:
            alter_query = f"ALTER TABLE `{table_ref}` " + ", ".join(alter_statements)
            print(f"Altering schema with: {alter_query}")
            bq_client.query(alter_query).result()

            # 🔑 Ensure schema really updated before proceeding
            table = ensure_schema_updated(bq_client, table_ref, new_fields)
            existing_schema = {f.name: f.field_type for f in table.schema}

    # 4. Load data
    if table_exists:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition="WRITE_APPEND",
            schema=table.schema  # Updated schema
        )
    else:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,
            write_disposition="WRITE_EMPTY"
        )

    load_job = bq_client.load_table_from_uri(file_location, table_ref, job_config=job_config)
    load_job.result()

    # 5. Log metadata
    table = bq_client.get_table(table_ref)
    row_count = table.num_rows
    column_count = len(table.schema)

    end_time = datetime.utcnow()
    log_metadata(run_id, file_location, stage="dump_to_bq", status="success",
                 start_time=start_time, end_time=end_time,
                 row_count=row_count, column_count=column_count)

    ti.xcom_push(key='file_location', value=file_location)
    ti.xcom_push(key='run_id', value=run_id)

###


#     def dump_to_bq(ti, **kwargs):
#         start_time = datetime.utcnow()

#         file_location = ti.xcom_pull(key='file_location', task_ids='check_for_files')
#         run_id = ti.xcom_pull(key='run_id', task_ids='check_for_files')

#         log_metadata(run_id, file_location, stage="dump_to_bq", status="started",
#                      start_time=start_time, end_time=start_time)

#         PROJECT_ID = "x-oxygen-468806-d1"
#         DATASET_ID = "P1"
#         TABLE_ID = "jsonl_dump_2"

#         bq_client = bigquery.Client(project=PROJECT_ID)
#         storage_client = storage.Client()
#         table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

#         # ---------------------------
#         # 1. Check if table exists
#         # ---------------------------
#         try:
#             table = bq_client.get_table(table_ref)
#             table_exists = True
#             existing_schema = {f.name: f.field_type for f in table.schema}
#             print(f"Table {table_ref} exists, using schema: {existing_schema}")
#         except Exception:
#             table_exists = False
#             existing_schema = {}
#             print(f"Table {table_ref} does not exist, will create with autodetect.")

#         # ---------------------------
#         # 2. If table exists, scan JSON file for new fields
#         # ---------------------------
#         bucket_name, blob_name = file_location.replace("gs://", "").split("/", 1)
#         blob = storage_client.bucket(bucket_name).blob(blob_name)

#         raw_data = blob.download_as_bytes().decode("utf-8").splitlines()
#         field_values = defaultdict(list)

#         for line in raw_data:
#             if not line.strip():
#                 continue
#             record = json.loads(line)
#             for field, value in record.items():
#                 if value is not None:
#                     field_values[field].append(value)

#         ##
#         if table_exists:
#             alter_statements = []
#             for field, values in field_values.items():
#                 if field not in existing_schema:
#                     inferred_type = infer_bq_type_from_values(values)
#                     alter_statements.append(f"ADD COLUMN IF NOT EXISTS {field} {inferred_type}")

#             if alter_statements:
#                 alter_query = f"ALTER TABLE `{table_ref}` " + ", ".join(alter_statements)
#                 print(f"Altering schema with: {alter_query}")
#                 bq_client.query(alter_query).result()
#         ##
#         # ---------------------------
#         # 3. Configure load job
#         # ---------------------------
#         if table_exists:
#             # Use schema from table (prevents autodetect drift)
#             job_config = bigquery.LoadJobConfig(
#                 source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
#                 write_disposition="WRITE_APPEND",
#                 schema=table.schema
#             )
#         else:
#             # First time → autodetect
#             job_config = bigquery.LoadJobConfig(
#                 source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
#                 autodetect=True,
#                 write_disposition="WRITE_EMPTY"
#             )

#         # ---------------------------
#         # 4. Load into BigQuery
#         # ---------------------------
#         load_job = bq_client.load_table_from_uri(file_location, table_ref, job_config=job_config)
#         load_job.result()

#         # ---------------------------
#         # 5. Log metadata
#         # ---------------------------
#         table = bq_client.get_table(table_ref)
#         row_count = table.num_rows
#         column_count = len(table.schema)

#         end_time = datetime.utcnow()
#         log_metadata(run_id, file_location, stage="dump_to_bq", status="success",
#                      start_time=start_time, end_time=end_time,
#                      row_count=row_count, column_count=column_count)

#         ti.xcom_push(key='file_location', value=file_location)
#         ti.xcom_push(key='run_id', value=run_id)


# ##

    dump_to_bq_task = PythonOperator(
        task_id='dump_to_bq',
        python_callable=dump_to_bq
    )

    # ---------------------------
    # Stage 4: SDP process
    # ---------------------------
    def sdp_process(ti, **kwargs):
        start_time = datetime.utcnow()

        file_location = ti.xcom_pull(key='file_location', task_ids='dump_to_bq')
        run_id = ti.xcom_pull(key='run_id', task_ids='dump_to_bq')

        print(f"Starting SDP process for file: {file_location}, run_id: {run_id}")
        time.sleep(2)
        print("SDP process completed.")

        end_time = datetime.utcnow()
        log_metadata(run_id, file_location, stage="sdp_process", status="success",
                     start_time=start_time, end_time=end_time)

        ti.xcom_push(key='file_location', value=file_location)
        ti.xcom_push(key='run_id', value=run_id)

    sdp_process_task = PythonOperator(
        task_id='sdp_process',
        python_callable=sdp_process
    )

    # ---------------------------
    # Stage 5: Notify completion
    # ---------------------------
    def notify_completion(ti, **kwargs):
        start_time = datetime.utcnow()

        file_location = ti.xcom_pull(key='file_location', task_ids='sdp_process')
        run_id = ti.xcom_pull(key='run_id', task_ids='sdp_process')

        print(f"Sending completion notification for file: {file_location}, run_id: {run_id}")
        time.sleep(2)
        print("Notification sent successfully.")

        end_time = datetime.utcnow()
        log_metadata(run_id, file_location, stage="notify_completion", status="success",
                     start_time=start_time, end_time=end_time)

    notify_completion_task = PythonOperator(
        task_id='notify_completion',
        python_callable=notify_completion
    )

    # ---------------------------
    # DAG Flow
    # ---------------------------
    wait_for_gcs_file >> check_for_files_task >> preliminary_checks_task >> dump_to_bq_task >> sdp_process_task >> notify_completion_task
