up:
	docker compose up -d

down:
	docker compose down

restart:
	down && up

install:
	pip install -r requirements.txt

run:
	python src/main.py

test:
	pytest tests/