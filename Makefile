run:
	poetry run python app/main.py

format:
	poetry run black .

lint:
	poetry run black --check .

test:
	poetry run pytest .

load-schemas:
	./scripts/load_schemas.sh
	./scripts/load_runner_schemas.sh
