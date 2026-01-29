FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY 2025_10_26_01_40_42-54R1.xml .

EXPOSE 7860

CMD ["python", "app.py"]
