#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} +

find "$SCRIPT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} +

rm -r .postgres
rm -r .redis
rm -r .grafana
rm -r .prometheus
rm -r .clickhouse
rm -r .mongodb
rm -r .postgres-airflow
rm -r .minio

echo "Cleared"