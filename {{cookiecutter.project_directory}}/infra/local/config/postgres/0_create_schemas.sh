#!/bin/bash

set -eu
IFS=$'\n\t'

SCHEMAS=(
    "mart_analytics"
    "stg_randuser"
)

function create_schema() {
	local schema=$1
	echo "  Creating database '$schema'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" "$POSTGRES_DB"<<-EOSQL
	    CREATE SCHEMA IF NOT EXISTS $schema;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA $schema TO $POSTGRES_USER;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA $schema TO $POSTGRES_USER;
EOSQL
}

echo "Starting schemas creation"
for db in ${SCHEMAS[@]}; do
    create_schema $db
done
echo "Schemas created"
