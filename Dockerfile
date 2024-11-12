FROM python:3.11-slim as builder

WORKDIR /TaskManagment

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/TaskManagment/venv

COPY requirements.txt .
RUN /opt/TaskManagment/venv/bin/pip install --upgrade pip && \
    /opt/TaskManagment/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /TaskManagment

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/TaskManagment/venv /opt/TaskManagment/venv

COPY . .

ENV PATH="/opt/TaskManagment/venv/bin:$PATH"

CMD ["python3", "bot/Main.py"]
