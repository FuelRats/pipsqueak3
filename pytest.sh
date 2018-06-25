export P_HOST
psql -c 'CREATE ROLE mecha3 LOGIN CREATEDB' -U postgres -h $P_HOST
psql -c 'CREATE DATABASE mecha3 WITH OWNER = mecha3' -U postgres -h $P_HOST
pytest -v --cov --cov-report xml --junit-xml=test-reports/junit.xml
exitcode=$?
if [ $exitcode -ne 0 ] then exit 1 fi
cp coverage.xml /test-data/coverage.xml
