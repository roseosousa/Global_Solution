## Dockerfile para empacotar a aplicação (Python + R)
# Base: imagem com R. Instalamos Python e dependências do sistema para compilar pacotes R.
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev libssl-dev python3-dev git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /wheels

COPY requirements.txt /wheels/requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip wheel -r /wheels/requirements.txt -w /wheels/wheels

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libffi7 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# install python deps from pre-built wheels
COPY --from=builder /wheels/wheels /wheels
COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-index --find-links /wheels -r /app/requirements.txt \
    && rm -rf /wheels

COPY . /app
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

ENV PORT=5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]
