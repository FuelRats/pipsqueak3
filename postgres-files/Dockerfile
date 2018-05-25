# Use alpine image
FROM postgres:alpine
# Bind a directory to store PostGres data and databases
ENV PGDATA /psql-data
COPY ./psql-startup.sh ./
RUN chmod +x ./psql-startup.sh

