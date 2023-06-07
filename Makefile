db-user = postgres

build:
		docker-compose build

up:		
		docker-compose up	

migrations:
		docker-compose exec web bash -c "alembic revision --autogenerate"
		docker-compose exec web bash -c "alembic upgrade head"

stamp-migrations:
		docker-compose exec web bash -c "alembic stamp base"

test:
		docker-compose exec app_backend bash -c "pytest ${location}"

backend-bash:
		docker-compose exec app_backend bash

db-bash: 
		docker-compose exec db bash

db-shell:
		docker-compose exec db psql -U ${db-user}