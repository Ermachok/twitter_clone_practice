FROM python:3.12

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-root

COPY . .
ENV PYTHONPATH=/app

CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run python app/init_db.py && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
