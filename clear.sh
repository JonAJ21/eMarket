#!/bin/bash

# Получаем директорию, в которой находится скрипт
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Начинаем очистку __pycache__ начиная с директории: $SCRIPT_DIR"

# Находим и удаляем все директории __pycache__
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} +

echo "Очистка __pycache__ завершена."