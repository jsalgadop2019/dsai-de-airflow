# Proyecto Integrador de Ingeniería de Datos

## Descripción

Este repositorio contiene la implementación de un pipeline ETL (Extract, Transform, Load) para el seguimiento automatizado del gasto presupuestal en el Instituto Tecnológico de la Producción (ITP). El objetivo principal es cargar datos en formato raw desde un repositorio local a un Data Lake en Azure Blob Storage, utilizando Apache Airflow para la orquestación. 

El proyecto resuelve el problema de negocio de mejorar la visibilidad y predictibilidad del avance presupuestal mediante herramientas de ingeniería de datos. Los datos ingeridos incluyen órdenes de servicio y tablas complementarias (locadores, sedes, metas, pedidos, entregables, pagos, catálogo de servicios y tipos de documentos), extraídos de una base de datos SQL Server y almacenados como CSV localmente.

El alcance de este avance se limita a la ingesta en la zona raw, sin transformaciones intermedias. En fases futuras, se integrarán dashboards y modelos de machine learning (como regresión lineal) para predicciones.

**Componentes Principales:**
- **Fuentes de Datos:** Archivos CSV locales generados desde SQL Server.
- **Editor de DAGs:** VS Code con Python.
- **Orquestador:** Apache Airflow en Docker.
- **Almacenamiento:** Azure Data Lake (Blob Storage).

**Justificación:** VS Code es liviano y compatible con Python; Airflow facilita la automatización de flujos; Azure integra bien con herramientas de ML y dashboards.

## Prerrequisitos

Para recrear el escenario, asegúrese de tener instalados los siguientes elementos:
- Python 3.8 o superior.
- Docker Desktop (para ejecutar Airflow en contenedores).
- Visual Studio Code (recomendado para editar DAGs).
- Cuenta en Azure con acceso a Blob Storage (cree un contenedor llamado "datalake").
- Git para clonar el repositorio.
- Acceso a una base de datos SQL Server (o simule datos CSV manualmente).
- Bibliotecas Python: `azure-storage-blob`, `apache-airflow` (instaladas en el entorno de Airflow).

## Instalación

1. **Clonar el Repositorio:**
   ```
   git clone https://github.com/jsalgadop2019/dsai-de-airflow.git
   cd dsai-de-airflow
   ```

2. **Configurar Ramas con Gitflow:**
   - Inicialice Gitflow si no está configurado: `git flow init` (instale git-flow si es necesario: `sudo apt install git-flow` en Linux o equivalente).
   - Cree la rama `develop` desde `main`: `git checkout -b develop`.
   - Cree ramas de features para cambios: `git checkout -b feature/nombre-feature develop`.
   - Fusionar features a develop: `git checkout develop && git merge feature/nombre-feature`.
   - Para releases, fusione `develop` a `main` vía pull request.

3. **Instalar Apache Airflow con Docker:**
   - Descargue el archivo `docker-compose.yaml` oficial de Airflow desde [la documentación de Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).
   - Ejecute: `docker-compose up -d` para iniciar Airflow (incluye PostgreSQL como metadata DB por defecto).
   - Acceda a la interfaz web en `http://localhost:8080` (usuario/contraseña predeterminados: airflow/airflow).
   - Instale paquetes adicionales en el contenedor si es necesario (por ejemplo, para Azure: edite `docker-compose.yaml` para agregar `azure-storage-blob` en `AIRFLOW__CORE__EXTRA_PACKAGES`).

4. **Configurar Conexión a Azure en Airflow:**
   - En la interfaz de Airflow, vaya a Admin > Connections.
   - Cree una nueva conexión:
     - Conn Id: `utec_blob_storage`.
     - Conn Type: Azure Blob Storage (Wasb).
     - Login: Su cuenta de Azure Storage.
     - Password: La clave de acceso de la cuenta.
     - Extra: `{"blob_prefix": "wasb://"}` (ajuste según su configuración).

5. **Preparar Datos Locales:**
   - Cree una carpeta `data` en la raíz del repositorio.
   - Extraiga datos de SQL Server usando scripts Python o SQL (ejemplo básico):
     ```python
     import pandas as pd
     import pyodbc

     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=su-servidor;DATABASE=su-db;UID=usuario;PWD=contraseña')
     query = "SELECT * FROM ordenes_servicio"  # Ajuste la consulta
     df = pd.read_sql(query, conn)
     df.to_csv('data/ordenes.csv', index=False)  # Repita para otras tablas
     ```
   - Asegúrese de que los CSV incluyan formateo básico (por ejemplo, rellenado con ceros, conversión a strings).

## Uso

1. **Colocar el DAG en Airflow:**
   - Copie el archivo `dags/g3_utec.py` del repositorio a la carpeta `dags` de su instancia de Airflow (montada en Docker).
   - El DAG sube archivos CSV desde `./data` a `raw/airflow/G3/` en Azure, agregando sufijo de fecha (por ejemplo, `ordenes_20251102.csv`).
   - Frecuencia: Diaria a las 01:00 (UTC-5, Lima). Fecha de inicio: 2025-01-01. Catchup: False.

2. **Ejecutar el DAG:**
   - En la interfaz de Airflow, active el DAG `g3_utec`.
   - Dispare manualmente: Vaya a DAGs > g3_utec > Trigger DAG.
   - Monitoree logs en la interfaz para verificar éxito.

3. **Manejo de Errores:**
   - Errores comunes: Archivo ausente, conexión fallida, permisos.
   - En producción, agregue tareas de validación (por ejemplo, chequeo de esquema), reintentos (retries=3), logging y notificaciones (por ejemplo, vía email con Airflow operators).

4. **Validación:**
   - Verifique en Azure Portal: Storage Account > Containers > datalake > raw/airflow/G3/.
   - Revise logs en Airflow para confirmar la ejecución sin errores.

## Organización del Código

- **dags/g3_utec.py:** DAG principal con tarea `call_upload`. Usa decoradores `@dag` y `@task`. Constantes al inicio para rutas y conexiones.
- Estructura simple para prototipo; evolucione agregando validaciones y notificaciones.

## Resultados Esperados

- El DAG se ejecuta correctamente, cargando CSVs en raw zone.
- Ejemplo de salida: `ordenes_20251102.csv` en Azure.

## Desafíos y Aprendizajes

- **Desafíos:** Adecuación a VS Code, Airflow y Gitflow; diseño de CSVs para datos presupuestales.
- **Aprendizajes:** Automatización de flujos con DAGs; Gitflow para colaboración; integración de Python, Docker, Azure y DataOps.

## Contribuyentes

- Basurto Siuce, Eder
- Palacios Chilo, Jorge Luis
- Salgado Paraguay, Julio César
- Soriano Ricalde, Richard Clever

**Curso:** Data Engineering, Maestría en Ciencia de Datos & Inteligencia Artificial.  
**Profesor:** Ángel Tintaya Monroy.
