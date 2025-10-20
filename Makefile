# Makefile for lrg-network

.PHONY: help build up down migrate cities_light shell logs test

help:
	@echo "Makefile commands:"
	@echo "  build         	Build Docker images"
	@echo "  up            	Start containers (detached)"
	@echo "  down          	Stop and remove containers"
	@echo "  makemigrations	Create new migrations"
	@echo "  migrate		Run Django migrations inside web container"
	@echo "  cities_light	Load cities_light data"
	@echo "  shell			Open Django shell inside web container"
	@echo "  logs			Show logs from all containers"
	@echo "  test			Run tests (if implemented)"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

makemigrations:
	docker compose exec web python manage.py makemigrations games

migrate:
	docker compose exec web python manage.py migrate

cities_light:
	docker compose exec web python manage.py cities_light

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f

test:
	docker compose exec web python manage.py test

audit:
	pip-audit -r requirements.txt || (echo "\n⚠️  Security vulnerabilities found!" && exit 1)
