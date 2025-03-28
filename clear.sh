#!/bin/bash

# Получаем директорию, в которой находится скрипт
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


# Находим и удаляем все директории __pycache__
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} +

# Удаляем все данные из БД

rm -r .postgres
rm -r .redis

echo "Очистка завершена."