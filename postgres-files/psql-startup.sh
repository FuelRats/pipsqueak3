su postgres -c './docker-entrypoint.sh'
su postgres -c "psql -c 'CREATE ROLE mecha3 LOGIN CREATEDB;'"
su postgres -c "psql -c 'CREATE DATABASE mecha3 WITH OWNER = mecha3;'"
