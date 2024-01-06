import json
import uuid
import logging
import requests
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


default_args = {
    "owner": "data-eng",
    "start_date": datetime(2024, 1, 1),
}


def call_flask_endpoint():
    flask_endpoint_url = 'http://localhost:5000/send_metadata'

    try:
        response = requests.post(flask_endpoint_url)
        response.raise_for_status()
        logging.info('Response: %s', response.text)
        logging.info('HTTP Status Code: %s', response.status_code)
    except requests.exceptions.RequestException as e:
        logging.error('Erro ao chamar o endpoint Flask: %s', str(e))


def get_kafka_endpoint():
    kafka_endpoint_url = 'http://localhost:5000/consume_and_insert'

    try:
        response = requests.get(kafka_endpoint_url)
        response.raise_for_status()
        logging.info('Response: %s', response.text)
        logging.info('HTTP Status Code: %s', response.status_code)
    except requests.exceptions.RequestException as e:
        logging.error('Erro ao chamar o endpoint Kafka: %s', str(e))


with DAG(
    "dummy_dag",
    default_args=default_args,
    description="DAG dummy",
    schedule_interval="@once",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

    start = DummyOperator(task_id="start")

    wait_for_flask = DummyOperator(task_id="wait_for_flask")

    end = DummyOperator(task_id="end")

    cassandra_task = PythonOperator(
        task_id='cassandra_task',
        python_callable=get_kafka_endpoint,
    )

    kafka_task = PythonOperator(
        task_id='kafka_task',
        python_callable=call_flask_endpoint,
    )

    start >> wait_for_flask >> cassandra_task >> kafka_task >> end
