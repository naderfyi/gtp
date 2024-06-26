import sys
import getpass
sys_user = getpass.getuser()
sys.path.append(f"/home/{sys_user}/gtp/backend/")

import os
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from src.adapters.adapter_raw_rhino import AdapterRhino
from src.db_connector import DbConnector
from src.misc.airflow_utils import alert_via_webhook

@dag(
    default_args= {
        'owner': 'nader',
        'retries': 2,
        'email_on_failure': False,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': alert_via_webhook
    },
    dag_id='raw_rhino',
    description='Load raw tx data from Rhino',
    tags=['raw', 'daily'],
    start_date=datetime(2023, 9, 1),
    schedule='30 01 * * *'
)

def adapter_rhino_tx_loader():
    @task(execution_timeout=timedelta(minutes=45))
    def run_rhino():
        adapter_params = {
            'chain': 'rhino',
            'json_endpoint': os.getenv("RHINO_JSON"),
        }

        # Initialize DbConnector
        db_connector = DbConnector()

        # Initialize AdapterRhino
        adapter = AdapterRhino(adapter_params, db_connector)

        try:
            adapter.extract_raw()
            print("Successfully loaded transaction data for Rhino.")
        except Exception as e:
            print(f"Failed to load transaction data: {e}")
            raise

    run_rhino()
adapter_rhino_tx_loader()