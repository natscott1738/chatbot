SHELL := /bin/bash

.PHONY: dev up down logs test lint fmt rebuild ingest repl

dev:
	./scripts/bootstrap.sh

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f --tail=200

test:
	docker-compose run --rm backend sh -lc "pytest -q"

lint:
	docker-compose run --rm backend sh -lc "ruff check ."

fmt:
	docker-compose run --rm backend sh -lc "ruff check . --fix && black ."

rebuild:
	docker-compose build --no-cache backend

ingest:
	docker-compose run --rm backend sh -lc "python backend/scripts/ingest_docs.py"

repl:
	python cli/chat_repl.py
