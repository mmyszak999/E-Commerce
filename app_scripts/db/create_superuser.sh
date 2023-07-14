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
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )

    cursor = connection.cursor()

    postgres_insert_query = """INSERT INTO "user"
    (FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD, BIRTH_DATE, IS_SUPERUSER)
    VALUES ('MOKEBE', 'SUPERUSER', 'superuser@mail.com', 'SuperUser', 'password123', '1999-04-20', TRUE)
    """
    cursor.execute(postgres_insert_query)
    connection.commit()


except (psycopg2.OperationalError, psycopg2.errors.UniqueViolation):
    sys.exit(-1)
sys.exit(0)

END
}
create_superuser;
done
>&2 echo 'Superuser created'

exec "$@"