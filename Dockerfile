FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY data/ ./data/
COPY business/ ./business/
COPY presentation/ ./presentation/
COPY assets/ ./assets/

EXPOSE 7860

CMD ["python", "app.py"]
