import sys
import getpass
sys_user = getpass.getuser()
sys.path.append(f"/home/{sys_user}/gtp/backend/")

from datetime import datetime,timedelta
from airflow.decorators import dag, task 
from src.misc.airflow_utils import alert_via_webhook

@dag(
    default_args={
        'owner' : 'mseidl',
        'retries' : 2,
        'email_on_failure': False,
        'retry_delay' : timedelta(minutes=5),
        'on_failure_callback': alert_via_webhook
    },
    dag_id='utility_sql_materialize',
    description='Aggregate materialized views on database',
    tags=['utility', 'daily'],
    start_date=datetime(2023,4,24),
    schedule='00 02 * * *'
)

def etl():
    @task()
    def run_unique_senders():
        from src.db_connector import DbConnector
        from src.adapters.adapter_sql import AdapterSQL
        adapter_params = {}
        load_params = {
            'load_type' : 'active_addresses_agg',
            'days' : 3, ## days as int or 'auto
        }

       # initialize adapter
        db_connector = DbConnector()
        ad = AdapterSQL(adapter_params, db_connector)
        # extract
        ad.extract(load_params)

    @task()
    def run_da_queries():
        from src.db_connector import DbConnector
        from src.adapters.adapter_sql import AdapterSQL
        adapter_params = {}
        load_params = {
            'load_type' : 'jinja', ## usd_to_eth or metrics or blockspace
            'queries' : ['da_metrics/upsert_fact_da_consumers_celestia_blob_size.sql.j2', 'da_metrics/upsert_fact_da_consumers_celestia_blob_fees.sql.j2'],
        }

        # initialize adapter
        db_connector = DbConnector()
        ad = AdapterSQL(adapter_params, db_connector)

        # extract
        ad.extract(load_params)

    run_unique_senders()
    run_da_queries()
etl()





