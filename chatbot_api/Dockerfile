# chatbot_api/Dockerfile

FROM python:3.9

WORKDIR /app

COPY ./src/ /app
COPY ./pyproject.toml /code/pyproject.toml

RUN pip install /code/.

EXPOSE 8000
CMD ["sh", "entrypoint.sh"]