FROM python:3.10-slim

WORKDIR /app

# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app.py .
COPY data/ ./data/
COPY business/ ./business/
COPY presentation/ ./presentation/
COPY assets/ ./assets/
COPY samples/ ./samples/

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta do Hugging Face Spaces
EXPOSE 7860

CMD ["python", "app.py"]
