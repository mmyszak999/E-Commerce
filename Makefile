db-user = postgres
location = tests

build:
		docker-compose build

up:		
		docker-compose up	

down:
		docker-compose down

migrations:
		docker-compose exec web bash -c "alembic revision --autogenerate"
		docker-compose exec web bash -c "alembic upgrade head"

stamp-migrations:
		docker-compose exec web bash -c "alembic stamp base"

test:
		docker-compose exec web bash -c "pytest $(location)"

backend-bash:
		docker-compose exec web bash

db-bash: 
		docker-compose exec db bash

db-shell:
		docker-compose exec db psql -U ${db-user}

create-superuser:
		docker-compose exec web bash -c "bash ./app_scripts/create_superuser.sh main_db"
