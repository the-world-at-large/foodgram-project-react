FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY foodgram_backend/ .

CMD ["gunicorn", "foodgram_backend.wsgi:application", "--bind", "0:8000" ]
