from airflow.decorators import dag, task
from pendulum import timezone
from scripts.azure_upload import upload_to_adls
from scripts.helpers import add_date_suffix
from datetime import datetime, timedelta
import os

# Configuración centralizada de archivos
FILES_TO_UPLOAD = [
    "catalogo_servicios.csv",
    "entregables.csv",
    "locadores.csv",
    "metas.csv",
    "ordenes_detalles.csv",
    "pagos.csv",
    "pedidos.csv",
    "pedidos_detalles.csv",
    "sedes.csv",
    "tipos_documentos.csv"
]

LOCAL_BASE_PATH = "/opt/airflow/data"
CONTAINER_NAME = "datalake"
WASB_CONN_ID = "utec_blob_storage"
BLOB_BASE_PATH = "raw/airflow/G3"

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

@dag(
    dag_id="g3_masivo",
    description="Sube múltiples archivos CSV a Azure Blob Storage con sufijo de fecha (diario).",
    default_args=default_args,
    start_date=datetime(2025, 1, 1, tzinfo=timezone("America/Bogota")),
    schedule="0 1 * * *",
    catchup=False,
    tags=["utec", "blob", "upload", "multi-file"],
    max_active_runs=1,
)
def upload_dag():

    @task
    def upload_file(file_name: str):
        local_path = os.path.join(LOCAL_BASE_PATH, file_name)
        blob_name = f"{BLOB_BASE_PATH}/{file_name}"

        # Validación de existencia
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Archivo no encontrado: {local_path}")

        # Generar nombre con fecha
        dated_blob_name = add_date_suffix(blob_name)

        # Subir archivo
        upload_to_adls(
            local_file_path=local_path,
            container_name=CONTAINER_NAME,
            blob_name=dated_blob_name,
            wasb_conn_id=WASB_CONN_ID
        )

        return f"Subido: {file_name} → {dated_blob_name}"

    # Ejecutar una tarea por archivo (en paralelo)
    upload_file.expand(file_name=FILES_TO_UPLOAD)


dag = upload_dag()