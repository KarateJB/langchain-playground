.PHONY: build run run_agent down

build:
				docker compose build --no-cache

run_postgres:
				docker compose up -d postgres

run_agent:
				docker compose up -d --no-deps agent
				# docker compose run agent

run:
				docker compose up -d

stop:
				docker compose stop

down:
				docker compose down
