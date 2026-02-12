FROM python:3.10-slim

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar apenas dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser server.py .
COPY --chown=appuser:appuser gunicorn.conf.py .
COPY --chown=appuser:appuser security.py .
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser business/ ./business/
COPY --chown=appuser:appuser presentation/ ./presentation/
COPY --chown=appuser:appuser assets/ ./assets/
COPY --chown=appuser:appuser samples/ ./samples/

# Criar diretório de logs com permissões restritas
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Mudar para usuário não-root
USER appuser

# Limites de recursos
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=2

EXPOSE 7860

CMD ["gunicorn", "-c", "gunicorn.conf.py", "server:server"]
