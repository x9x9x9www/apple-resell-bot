#!/usr/bin/env bash
set -e

# Переход в директорию проекта
cd "$(dirname "$0")"

# Проверка наличия .env
if [ ! -f .env ]; then
  echo "❌ Ошибка: Файл .env не найден в корне проекта!"
  exit 1
fi

# Проверка наличия виртуального окружения
if [ -f "./.venv/bin/python3" ]; then
  PYTHON_EXEC="./.venv/bin/python3"
elif [ -f "./.venv/bin/python" ]; then
  PYTHON_EXEC="./.venv/bin/python"
else
  echo "⚠️ Виртуальное окружение .venv не найдено. Используется системный python3..."
  PYTHON_EXEC="python3"
fi

echo "🚀 Запуск бота Перекупочка..."
exec "$PYTHON_EXEC" main.py "$@"
