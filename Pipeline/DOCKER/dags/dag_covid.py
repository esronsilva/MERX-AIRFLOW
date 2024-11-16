import datetime
import requests
import logging
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import timezone

def connect_to_api():
    base_api_url = Variable.get("api_covid")
    if not base_api_url:
        raise ValueError("A variável 'api_covid' não está definida no Airflow")
    
    start_date = "2019-10-01"
    api_url = f"{base_api_url}?start_date={start_date}"
    
    response = requests.get(api_url)
    if response.status_code == 200:
        logging.info(f"Resposta da API: {response.json()}")
        return response.json()
    else:
        raise Exception(f"Erro na requisição da API: {response.status_code}")


def process_data(**kwargs):
    data = kwargs['ti'].xcom_pull(task_ids='connect_to_api')
    if isinstance(data, dict) and 'data' in data:
        return data['data']
    else:
        raise ValueError("Formato de dados inesperado: 'data' não encontrado ou estrutura inválida.")


def convert_datetime(datetime_str):
    if datetime_str:
        try:
            return datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError as e:
            logging.error(f"Erro ao converter datetime: {e}, valor recebido: {datetime_str}")
            raise
    return None

def insert_data_into_db(**kwargs):
    states_data = kwargs['ti'].xcom_pull(task_ids='process_data')
    hook = PostgresHook(postgres_conn_id='airflow-merx')
    conn = hook.get_conn()
    cursor = conn.cursor()

    for state in states_data:
        formatted_datetime = convert_datetime(state.get('datetime'))
        state_data = (
            state.get('uid', None),
            state.get('uf', None),
            state.get('state', None),
            state.get('cases', None),
            state.get('deaths', None),
            state.get('suspects', None),
            state.get('refuses', None),
            state.get('broadcast', None),
            state.get('comments', None),
            formatted_datetime
        )

 
        cursor.execute("SELECT datetime FROM covid_data WHERE uid = %s", (state_data[0],))
    result = cursor.fetchone()

    if result:
        existing_datetime = result[0]
        

        if existing_datetime.tzinfo is None:
            existing_datetime = existing_datetime.replace(tzinfo=timezone.utc)
        
        if formatted_datetime > existing_datetime:
            cursor.execute("""
                UPDATE covid_data
                SET uf = %s, state = %s, cases = %s, deaths = %s, suspects = %s, refuses = %s,
                    broadcast = %s, comments = %s, datetime = %s
                WHERE uid = %s
            """, state_data[1:] + (state_data[0],))
    else:
        cursor.execute("""
            INSERT INTO covid_data
            (uid, uf, state, cases, deaths, suspects, refuses, broadcast, comments, datetime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, state_data)

    conn.commit()
    cursor.close()
    conn.close()

with DAG(
    'dag_executa_covid',
    start_date=datetime.datetime(2019, 11, 15),
    schedule_interval='0 0 * * *',
    catchup=False
) as dag:

    connect_api_task = PythonOperator(
        task_id="connect_to_api",
        python_callable=connect_to_api
    )

    process_data_task = PythonOperator(
        task_id="process_data",
        python_callable=process_data,
        provide_context=True
    )

    insert_data_task = PythonOperator(
        task_id="insert_data_into_db",
        python_callable=insert_data_into_db,
        provide_context=True
    )

    connect_api_task >> process_data_task >> insert_data_task
