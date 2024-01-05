import logging
from datetime import datetime

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

default_args = {
    "owner": "data-eng",
    "start_date": datetime(2024, 1, 1),
}


def create_keyspace(session):
    session.execute("""
    CREATE KEYSPACE IF NOT EXISTS metadata
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)
    print('Keyspace created successfully')


def create_table(session):
    session.execute("""
    CREATE TABLE IF NOT EXISTS metadata.airflow_execution (
        id UUID PRIMARY KEY,
        dag_id TEXT,
        execution_date TIMESTAMP
    )
    """)
    print('Table created successfully')

with DAG (
    dag_id="create_or_update",
    description="Create or update the Cassandra keyspace and table",
    default_args=default_args,
    schedule_interval="@once",
    catchup=False,
    tags=["example"],
) as dag:

    def create_or_update():
        auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
        cassandra_contact_point = 'host.docker.internal'
        cluster = Cluster([cassandra_contact_point], auth_provider=auth_provider)
        session = cluster.connect()
        create_keyspace(session)
        create_table(session)

    create_or_update_task = PythonOperator(
        task_id="create_or_update",
        python_callable=create_or_update,
    )

    create_or_update_task
