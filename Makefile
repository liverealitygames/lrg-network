# Makefile for lrg-network

.PHONY: help build up down migrate cities_light shell logs test format format-check optimize-images

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
	@echo "  format			Format code with Black"
	@echo "  format-check	Check code formatting (mirrors CI)"
	@echo "  optimize-images	Optimize images >500KB in static/resources/images/"

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

format:
	black .

format-check:
	black --check .

optimize-images:
	@echo "Optimizing images in static/resources/images/..."
	@cd static/resources/images && \
	for img in *.jpg *.png; do \
		if [ -f "$$img" ]; then \
			size=$$(stat -f%z "$$img" 2>/dev/null || stat -c%s "$$img" 2>/dev/null); \
			if [ "$$size" -gt 512000 ]; then \
				echo "Optimizing $$img ($$(numfmt --to=iec-i --suffix=B $$size))..."; \
				if echo "$$img" | grep -q "\.png$$"; then \
					newimg=$$(echo "$$img" | sed 's/\.png$$/\.jpg/'); \
					sips -s format jpeg -s formatOptions 85 "$$img" --out "$$newimg" && \
					sips -Z 1200 "$$newimg" && \
					rm "$$img" && \
					echo "Converted $$img to $$newimg"; \
				else \
					sips -s formatOptions 85 "$$img" && \
					sips -Z 1200 "$$img" && \
					echo "Optimized $$img"; \
				fi; \
			else \
				echo "Skipping $$img (already optimized: $$(numfmt --to=iec-i --suffix=B $$size))"; \
			fi; \
		fi; \
	done || \
	for img in *.jpg *.png; do \
		if [ -f "$$img" ]; then \
			size=$$(ls -l "$$img" | awk '{print $$5}'); \
			if [ "$$size" -gt 512000 ]; then \
				echo "Optimizing $$img ($$size bytes)..."; \
				if echo "$$img" | grep -q "\.png$$"; then \
					newimg=$$(echo "$$img" | sed 's/\.png$$/\.jpg/'); \
					sips -s format jpeg -s formatOptions 85 "$$img" --out "$$newimg" && \
					sips -Z 1200 "$$newimg" && \
					rm "$$img" && \
					echo "Converted $$img to $$newimg"; \
				else \
					sips -s formatOptions 85 "$$img" && \
					sips -Z 1200 "$$img" && \
					echo "Optimized $$img"; \
				fi; \
			fi; \
		fi; \
	done
	@echo "Image optimization complete!"
