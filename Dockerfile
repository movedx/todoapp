FROM python:3.10-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

ENV PORT 443

WORKDIR $APP_HOME

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

CMD exec gunicorn --certfile=cert.pem --keyfile=key.pem --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app


EXPOSE 443
EXPOSE 80
