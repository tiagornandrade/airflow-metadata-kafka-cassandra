import json
import uuid
import logging
from datetime import datetime
from flask import Flask, jsonify
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from confluent_kafka import Producer, Consumer, KafkaException

app = Flask(__name__)


def delivery_report(err, msg):
    if err is not None:
        logging.error('Erro ao enviar a mensagem: %s', err)
    else:
        logging.info('Mensagem enviada para o tópico: %s [%s]', msg.topic(), msg.partition())


def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


@app.route('/send_metadata', methods=['POST'])
def send_metadata():
    bootstrap_servers = 'localhost:9092'
    topic = 'airflow_metadata_topic'
    metadata = {'id': str(uuid.uuid4()), 'dag_id': 'dummy_execution', 'execution_date': datetime.now()}

    producer_config = {
        'bootstrap.servers': bootstrap_servers,
    }

    producer = Producer(producer_config)

    try:
        json_data = json.dumps(metadata, default=datetime_serializer)
        producer.produce(topic, key=None, value=json_data, callback=delivery_report)
        producer.flush()

    except KafkaException as e:
        logging.error('Erro ao enviar mensagem para Kafka: %s', str(e))
    except Exception as ex:
        logging.error('Erro inesperado: %s', str(ex))

    return 'Metadata enviado para o Kafka com sucesso!'


@app.route('/consume_and_insert', methods=['GET'])
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


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
