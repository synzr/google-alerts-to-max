# этап сборки
FROM python:3.12-slim AS builder

WORKDIR /install

# установляем нативные зависимости
RUN apt-get update

RUN apt-get install \
    -y \
    --no-install-recommends \
    gcc libxml2-dev libxslt1-dev

RUN rm -rf /var/lib/apt/lists/*

# копируем requirements.txt
COPY requirements.txt .

# установляем Python-зависимости
RUN pip install \
        --prefix=/install \
        --no-cache-dir \
        -r requirements.txt

# этап приложения
FROM python:3.14-slim

# настройка Python окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONENCODING=utf-8
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# копируем собранные зависимости
COPY --from=builder /install /usr/local

# копируем приложение
COPY . .

CMD [ "python", "-m", "google_alerts_to_max" ]
