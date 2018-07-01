#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER mecha3 LOGIN;
	CREATE DATABASE mecha3;
	GRANT ALL PRIVILEGES ON DATABASE mecha3 TO mecha3;
EOSQL
