#!/bin/bash

HOST="localhost"
PORT="9000"
USER="admin"
PASSWORD="admin" #
DATABASE="default"

while getopts ":h:P:u:p:d:" opt; do
  case $opt in
    h) HOST="$OPTARG" ;;
    P) PORT="$OPTARG" ;;
    u) USER="$OPTARG" ;;
    p) PASSWORD="$OPTARG" ;;
    d) DATABASE="$OPTARG" ;;
    \?) echo "Неверный параметр: -$OPTARG" >&2; exit 1 ;;
  esac
done
shift $((OPTIND -1))

if [ -z "$1" ]; then
  echo "Ошибка: Укажите путь к SQL-скрипту"
  echo "Использование: $0 [-h хост] [-P порт] [-u пользователь] [-p пароль] [-d база_данных] путь_к_скрипту.sql"
  exit 1
fi

SQL_FILE="$1"

if [ ! -f "$SQL_FILE" ]; then
  echo "Ошибка: Файл $SQL_FILE не найден"
  exit 1
fi

# Формируем команду
CMD="clickhouse-client --host $HOST --port $PORT --user $USER --database $DATABASE --multiline --multiquery"

# Добавляем пароль если указан
if [ -n "$PASSWORD" ]; then
  CMD="$CMD --password $PASSWORD"
fi

# Выполняем скрипт
echo "Выполняю $SQL_FILE в ClickHouse ($HOST:$PORT)"
$CMD < "$SQL_FILE"

# Проверяем результат
if [ $? -eq 0 ]; then
  echo "Скрипт успешно выполнен"
else
  echo "Ошибка при выполнении скрипта"
  exit 1
fi