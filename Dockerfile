FROM python:3.10-slim

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copiar requirements
COPY requirements.txt ./

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app.py .
COPY data/ ./data/
COPY business/ ./business/
COPY presentation/ ./presentation/
COPY assets/ ./assets/
COPY samples/ ./samples/

# Criar diretório para logs
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Configurar permissões
RUN chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 7860

# Comando para produção (sem testes automáticos)
CMD ["python", "app.py"]
