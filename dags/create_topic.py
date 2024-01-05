from airflow import DAG
from datetime import datetime
from confluent_kafka.admin import AdminClient, NewTopic
from airflow.operators.python_operator import PythonOperator

default_args = {
    "owner": "data-eng",
    "start_date": datetime(2024, 1, 1),
}


def create_topic():
    bootstrap_servers = 'localhost:9092'
    admin_config = {'bootstrap.servers': bootstrap_servers}
    topic_name = 'airflow_metadata_topic'
    admin_client = AdminClient(admin_config)
    new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
    topic_list = [new_topic]
    admin_client.create_topics(topic_list)

with DAG(
    dag_id="create_topic",
    description="Create topic",
    default_args=default_args,
    schedule_interval="@once",
    catchup=False,
    tags=["example"],
) as dag:

    create_topic_task = PythonOperator(
        task_id="create_topic",
        python_callable=create_topic,
    )

    create_topic_task