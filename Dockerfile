FROM python:3.12-slim

WORKDIR /app

COPY consumer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY consumer/app.py .

CMD ["python", "app.py"]
