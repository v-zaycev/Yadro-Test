FROM python:3.13-alpine

WORKDIR /app

# Копируем исходники
COPY src/ ./src/
COPY run.py .
COPY test_cases/ ./test_cases/

# Запуск
ENTRYPOINT ["python", "run.py"]