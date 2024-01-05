entrypoint: chmod +x entrypoint.sh

init:
	docker-compose up airflow-init

up:
	docker-compose up --build -d

down:
	docker compose down

restart: down up

install:
	pip install -r requirements.txt

run:
	python src/main.py

test:
	pytest tests/

exec-cassandra:
	docker exec -it cassandra cqlsh -u cassandra -p cassandra localhost 9042