from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import uuid
import json
from datetime import datetime


def consume_and_insert():
    consumer = KafkaConsumer(
        'airflow_metadata_topic',
        group_id='flask-consumer-group',
        bootstrap_servers=['localhost:9092']
    )

    cluster = Cluster(['localhost'])
    session = cluster.connect('metadata')

    insert_statement = session.prepare(
        "INSERT INTO airflow_execution (id, dag_id, execution_date) VALUES (?, ?, ?)"
    )

    for message in consumer:
        decoded_message = message.value.decode('utf-8')

        try:
            message_data = json.loads(decoded_message)

            id = uuid.uuid4()
            dag_id = message_data.get('dag_id', '')

            execution_date_str = message_data.get('execution_date', '')
            execution_date = datetime.strptime(execution_date_str,
                                               '%Y-%m-%dT%H:%M:%S.%f') if execution_date_str else None

            session.execute(insert_statement, (id, dag_id, execution_date))
            print(f'Dados inseridos no Cassandra: id={id}, dag_id={dag_id}, execution_date={execution_date}')

        except json.JSONDecodeError as e:
            print(f"Aviso: Ignorando mensagem com formato JSON inválido: {decoded_message}")
            continue
        except ValueError as e:
            print(
                f"Aviso: Ignorando mensagem com 'id' inválido, 'execution_date' inválido ou formato de data inválido: {decoded_message}")
            continue

    cluster.shutdown()


consume_and_insert()
