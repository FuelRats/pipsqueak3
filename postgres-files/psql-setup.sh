#! /bin/sh
pg_ctl -w start
psql -c 'CREATE ROLE mecha3 LOGIN CREATEDB;'
psql -c 'CREATE DATABASE mecha3 WITH OWNER = mecha3;'