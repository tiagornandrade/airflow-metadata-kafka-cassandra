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
    kafka_bootstrap_servers = 'localhost:9092'
    topic = 'airflow_metadata_topic'
    cassandra_contact_point = 'localhost'

    consumer_config = {
        'bootstrap.servers': kafka_bootstrap_servers,
        'group.id': 'flask-consumer-group',
        'auto.offset.reset': 'earliest',
    }

    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])

    auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    cassandra_cluster = Cluster([cassandra_contact_point], auth_provider=auth_provider)
    session = cassandra_cluster.connect()

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                logging.error("Erro ao receber mensagem do Kafka: %s", msg.error())
            else:
                try:
                    metadata = json.loads(msg.value().decode('utf-8'))
                    logging.info('Mensagem recebida: %s', metadata)

                    insert_query = "INSERT INTO metadata.airflow_execution (id, dag_id, execution_date) VALUES (?, ?, ?)"
                    session.execute(insert_query, (metadata['id'], metadata['dag_id'], metadata['execution_date']))

                except Exception as ex:
                    logging.error('Erro ao processar a mensagem: %s', str(ex))

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

    return jsonify({'status': 'Consumo e inserção no Cassandra bem-sucedidos!'})


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
