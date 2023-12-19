FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install gunicorn==20.1.0
RUN pip3 install -r requirements.txt --no-cache-dir

COPY foodgram_backend/ .

ENV PATH="/app:$PATH"

CMD ["gunicorn", "foodgram_backend.wsgi:application", "--bind", "0:8000"]
