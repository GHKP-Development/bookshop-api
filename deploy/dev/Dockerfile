FROM python:3.11-alpine3.19

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

RUN rm poetry.lock

RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && poetry lock --no-update

CMD ["python", "./main.py"]
