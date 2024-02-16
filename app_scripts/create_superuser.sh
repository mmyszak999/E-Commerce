#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

create_superuser() {
python << END
import sys
import uuid

import psycopg2
try:
    connection = psycopg2.connect(
        dbname="${TEST_POSTGRES_DB}" if "$1" == "test_db" else "${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
    user_id = uuid.uuid4()
    cursor = connection.cursor()
    user_insert_query = f"""INSERT INTO "user"
    (ID, FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD, BIRTH_DATE, IS_SUPERUSER, IS_STAFF, IS_ACTIVE)
    VALUES ('{user_id}', '${SUPERUSER_FIRST_NAME}', '${SUPERUSER_LAST_NAME}', '${SUPERUSER_EMAIL}',
    '${SUPERUSER_USERNAME}', '${SUPERUSER_PASSWORD}', '${SUPERUSER_BIRTHDATE}', TRUE, TRUE, TRUE)
    """
    cursor.execute(user_insert_query)


    address_insert_query = f"""INSERT INTO "user_address"
    (ID, COUNTRY, STATE, CITY, POSTAL_CODE, STREET, HOUSE_NUMBER, APARTMENT_NUMBER, USER_ID)
    VALUES ('{uuid.uuid4()}', 'USA', 'Texas', 'Houston',
    '34567', 'Walker Avenue', '35', '2', '{user_id}')
    """
    cursor.execute(address_insert_query)
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