PGPASSWORD=postgres psql -c "CREATE ROLE mecha3 LOGIN CREATEDB ENCRYPTED PASSWORD 'mecha3'" -U postgres -h localhost
PGPASSWORD=postgres psql -c "CREATE DATABASE mecha3 WITH OWNER = mecha3" -U postgres -h localhost
curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter
chmod +x ./cc-test-reporter
./cc-test-reporter before-build
pytest -v --cov --cov-report xml --junit-xml=test-reports
