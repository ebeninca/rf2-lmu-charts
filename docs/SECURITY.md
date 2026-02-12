# 🔒 Plano de Segurança - rFactor2/LMU Charts

## Ambiente
- **Servidor**: Gunicorn (multi-process)
- **Framework**: Dash (Flask-based)
- **Plataforma**: Hugging Face Spaces (Docker)
- **Exposição**: Pública (internet)

---

## 🎯 Objetivos de Segurança

1. Prevenir ataques DDoS e abuso de recursos
2. Proteger contra injeção de código malicioso
3. Limitar uso de memória e CPU
4. Validar uploads de arquivos
5. Prevenir XML External Entity (XXE) attacks
6. Rate limiting por IP
7. Sanitização de inputs

---

## 🛡️ Camadas de Proteção

### 1. **Configuração do Gunicorn** (Primeira Linha de Defesa)

#### `gunicorn.conf.py`
```python
import multiprocessing

# Workers
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Máximo 4 workers
worker_class = 'sync'
worker_connections = 100
max_requests = 1000  # Restart worker após 1000 requests (previne memory leaks)
max_requests_jitter = 50
timeout = 30  # 30 segundos timeout
keepalive = 5

# Limites de request
limit_request_line = 4096  # Tamanho máximo da linha de request
limit_request_fields = 100  # Máximo de headers
limit_request_field_size = 8190  # Tamanho máximo de cada header

# Security
forwarded_allow_ips = '*'  # Hugging Face proxy
proxy_protocol = False
proxy_allow_ips = '*'

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'warning'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

---

### 2. **Rate Limiting** (Prevenir DDoS)

#### Implementação com Flask-Limiter

**Instalar:**
```bash
pip install Flask-Limiter
```

**Código (`app.py`):**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Inicializar limiter
limiter = Limiter(
    app=app.server,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Rate limit específico para upload
@limiter.limit("10 per minute")
@app.server.route('/upload', methods=['POST'])
def upload_handler():
    pass
```

**Limites Recomendados:**
- Upload de arquivo: **10 por minuto por IP**
- Requests gerais: **50 por hora por IP**
- Burst: **200 por dia por IP**

---

### 3. **Validação de Upload de Arquivos**

#### Implementação Robusta

```python
import magic
import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_EXTENSIONS = {'.xml', '.xmlx'}
ALLOWED_MIME_TYPES = {'text/xml', 'application/xml'}

def validate_upload(contents, filename):
    """Validação completa de upload"""
    
    # 1. Validar extensão
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extensão não permitida: {file_ext}")
    
    # 2. Validar tamanho
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"Arquivo muito grande: {file_size/1024/1024:.1f}MB")
    
    # 3. Validar MIME type (magic bytes)
    mime = magic.from_buffer(contents, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Tipo de arquivo inválido: {mime}")
    
    # 4. Validar XML (prevenir XXE)
    try:
        # Desabilitar entidades externas
        parser = ET.XMLParser(resolve_entities=False)
        ET.fromstring(contents, parser=parser)
    except ET.ParseError as e:
        raise ValueError(f"XML malformado: {str(e)}")
    
    # 5. Sanitizar filename
    safe_filename = secure_filename(filename)
    
    return safe_filename
```

---

### 4. **Proteção contra XXE (XML External Entity)**

#### Parser Seguro

```python
import defusedxml.ElementTree as ET

def parse_xml_secure(xml_content):
    """Parser XML seguro contra XXE attacks"""
    try:
        # defusedxml previne:
        # - Billion laughs attack
        # - Quadratic blowup
        # - External entity expansion
        # - DTD retrieval
        root = ET.fromstring(xml_content)
        return root
    except ET.ParseError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
```

**Instalar:**
```bash
pip install defusedxml
```

---

### 5. **Content Security Policy (CSP)**

#### Headers de Segurança

```python
@app.server.after_request
def add_security_headers(response):
    """Adiciona headers de segurança"""
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.plot.ly; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data: https://flagcdn.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    
    # Prevenir clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevenir MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS Protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), payment=()'
    )
    
    return response
```

---

### 6. **Sanitização de Inputs**

#### Validação de Filtros

```python
import bleach

def sanitize_filter_input(value):
    """Sanitiza inputs de filtros"""
    if not value:
        return None
    
    # Remove HTML/JavaScript
    clean_value = bleach.clean(value, tags=[], strip=True)
    
    # Limita tamanho
    if len(clean_value) > 100:
        raise ValueError("Input muito longo")
    
    # Valida caracteres permitidos
    if not re.match(r'^[a-zA-Z0-9\s\-_#]+$', clean_value):
        raise ValueError("Caracteres inválidos")
    
    return clean_value
```

---

### 7. **Monitoramento e Logging**

#### Sistema de Logs

```python
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging
handler = RotatingFileHandler(
    'logs/security.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

security_logger = logging.getLogger('security')
security_logger.addHandler(handler)
security_logger.setLevel(logging.WARNING)

# Logar eventos suspeitos
def log_suspicious_activity(ip, action, details):
    security_logger.warning(
        f"Suspicious activity - IP: {ip}, Action: {action}, Details: {details}"
    )
```

---

### 8. **Proteção de Recursos (Memory/CPU)**

#### Limites de Processamento

```python
import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    """Context manager para timeout de operações"""
    def signal_handler(signum, frame):
        raise TimeoutException("Operação excedeu tempo limite")
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Uso
try:
    with time_limit(10):  # 10 segundos máximo
        df, race_info, incidents = parse_xml_scores(xml_content)
except TimeoutException:
    return error_message("Processamento muito lento")
```

---

### 9. **Dockerfile Seguro**

#### Configuração de Segurança

```dockerfile
FROM python:3.10-slim

# Usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar apenas dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copiar e instalar dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY --chown=appuser:appuser . .

# Criar diretório de logs com permissões restritas
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Mudar para usuário não-root
USER appuser

# Limites de recursos
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=2

EXPOSE 7860

# Usar Gunicorn com configuração segura
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:server"]
```

---

### 10. **Variáveis de Ambiente Seguras**

#### `.env` (Nunca commitar!)

```bash
# Secrets
SECRET_KEY=<random-256-bit-key>
FLASK_SECRET_KEY=<random-256-bit-key>

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_ENABLED=true

# Logging
LOG_LEVEL=WARNING
SECURITY_LOG_ENABLED=true

# Limites
MAX_UPLOAD_SIZE=20971520  # 20MB
MAX_WORKERS=4
REQUEST_TIMEOUT=30
```

---

## 🚨 Detecção de Ataques

### Padrões Suspeitos para Monitorar

1. **Upload Excessivo**
   - Mais de 10 uploads por minuto do mesmo IP
   - Arquivos > 20MB
   - Extensões não permitidas

2. **XML Malicioso**
   - Entidades externas (XXE)
   - Arquivos > 100MB descomprimidos
   - Profundidade de nesting > 100

3. **Request Flooding**
   - Mais de 100 requests por minuto
   - Requests com User-Agent suspeito
   - Requests sem Referer

4. **Path Traversal**
   - `../` em filenames
   - Caracteres especiais em paths

---

## 📊 Métricas de Segurança

### Monitorar no Hugging Face Spaces

1. **CPU Usage** - Alertar se > 80% por 5 minutos
2. **Memory Usage** - Alertar se > 90%
3. **Request Rate** - Alertar se > 1000/min
4. **Error Rate** - Alertar se > 5%
5. **Upload Size** - Alertar se média > 15MB

---

## 🔧 Implementação Prioritária

### Fase 1 (Crítico - Implementar Agora)
- [x] Validação de upload (tamanho, extensão, MIME)
- [ ] Rate limiting básico
- [ ] Parser XML seguro (defusedxml)
- [ ] Headers de segurança

### Fase 2 (Importante - Próxima Sprint)
- [ ] Gunicorn configuration
- [ ] Logging de segurança
- [ ] Timeout de operações
- [ ] Sanitização de inputs

### Fase 3 (Desejável - Futuro)
- [ ] WAF (Web Application Firewall)
- [ ] IP Blacklist automático
- [ ] Honeypot endpoints
- [ ] CAPTCHA para uploads

---

## 🎯 Checklist de Deploy

- [ ] `gunicorn.conf.py` configurado
- [ ] Flask-Limiter instalado e configurado
- [ ] defusedxml substituindo xml.etree
- [ ] Security headers implementados
- [ ] Dockerfile usando usuário não-root
- [ ] Variáveis de ambiente configuradas no HF Spaces
- [ ] Logs de segurança habilitados
- [ ] Testes de carga realizados
- [ ] Documentação de incidentes criada

---

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Gunicorn Security](https://docs.gunicorn.org/en/stable/settings.html#security)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Hugging Face Spaces Security](https://huggingface.co/docs/hub/spaces-overview)
- [XML Security](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)

---

## 🆘 Resposta a Incidentes

### Em caso de ataque detectado:

1. **Identificar** - Verificar logs e métricas
2. **Isolar** - Bloquear IP atacante
3. **Mitigar** - Aumentar rate limits temporariamente
4. **Documentar** - Registrar incidente
5. **Revisar** - Atualizar regras de segurança

### Contatos de Emergência:
- Hugging Face Support: https://huggingface.co/support
- GitHub Issues: https://github.com/ebeninca/rf2-lmu-charts/issues

---

**Última atualização:** 2025-02-06  
**Responsável:** Equipe de Desenvolvimento  
**Revisão:** Trimestral
