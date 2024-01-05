FROM apache/airflow:2.8.0

WORKDIR /opt/airflow

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["webserver"]
