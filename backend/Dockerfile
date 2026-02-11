FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY constraints.txt .

RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir \
       -r requirements.txt -c constraints.txt

COPY . .

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
