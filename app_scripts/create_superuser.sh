#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

create_superuser() {
python << END
import sys

import psycopg2
try:
    connection = psycopg2.connect(
        dbname="${TEST_POSTGRES_DB}" if "$1" == "test_db" else "${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )

    cursor = connection.cursor()
    postgres_insert_query = """INSERT INTO "user"
    (FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD, BIRTH_DATE, IS_SUPERUSER, IS_STAFF, IS_ACTIVE)
    VALUES ('${SUPERUSER_FIRST_NAME}', '${SUPERUSER_LAST_NAME}', '${SUPERUSER_EMAIL}',
    '${SUPERUSER_USERNAME}', '${SUPERUSER_PASSWORD}', '${SUPERUSER_BIRTHDATE}', TRUE, TRUE, TRUE)
    """
    cursor.execute(postgres_insert_query)
    connection.commit()
    print("successfully created superuser")
    connection.close()


except (psycopg2.OperationalError, psycopg2.errors.UniqueViolation):
    print("Couldn't create a superuser. Check if the superuser account is already created.")
    sys.exit(-1)
sys.exit(0)

END
}

create_superuser $1

exec "$@"