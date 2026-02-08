FROM python:3.10-slim

# Criar usuário não-root
RUN useradd -m -u 1000 rlc

# Switch to the user
USER rlc

# Set home to the user's home directory
ENV HOME=/home/rlc \
    PATH=/home/rlc/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY --chown=rlc app.py .
COPY --chown=rlc server.py .
COPY --chown=rlc data/ ./data/
COPY --chown=rlc business/ ./business/
COPY --chown=rlc presentation/ ./presentation/
COPY --chown=rlc assets/ ./assets/
COPY --chown=rlc samples/ ./samples/

CMD ["gunicorn", "-w", "5", "-b", "0.0.0.0:7860", "--timeout", "120", "server:server"]
