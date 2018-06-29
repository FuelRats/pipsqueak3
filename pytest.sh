export P_HOST
pytest -v --cov --cov-report xml --junit-xml=test-reports/junit.xml
exitcode=$?
if [ $exitcode -ne 0 ] 
  then exit 1 
fi
cp coverage.xml /test-data/coverage.xml
cp -r ./test-reports /test-data/.
