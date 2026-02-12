import os
import re
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.utils import secure_filename

# Constantes de segurança
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_EXTENSIONS = {'.xml', '.xmlx'}
ALLOWED_MIME_TYPES = {'text/xml', 'application/xml'}

# Configurar logging de segurança
os.makedirs('logs', exist_ok=True)
handler = RotatingFileHandler(
    'logs/security.log',
    maxBytes=10*1024*1024,
    backupCount=5
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
security_logger = logging.getLogger('security')
security_logger.addHandler(handler)
security_logger.setLevel(logging.WARNING)


def log_suspicious_activity(ip, action, details):
    """Logar eventos suspeitos"""
    security_logger.warning(f"Suspicious activity - IP: {ip}, Action: {action}, Details: {details}")


def validate_upload(contents, filename):
    """Validação completa de upload"""
    import xml.etree.ElementTree as ET
    
    # 1. Validar extensão
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extensão não permitida: {file_ext}")
    
    # 2. Validar tamanho
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"Arquivo muito grande: {file_size/1024/1024:.1f}MB")
    
    # 3. Validar se é texto válido
    try:
        if isinstance(contents, bytes):
            contents_str = contents.decode('utf-8')
        else:
            contents_str = contents
    except UnicodeDecodeError:
        raise ValueError("Arquivo não é texto válido UTF-8")
    
    # 4. Validar XML básico (estrutura)
    # Não usar defusedxml aqui pois bloqueia entidades internas legítimas
    # A proteção XXE é feita no parser_secure.py
    try:
        ET.fromstring(contents_str.encode('utf-8'))
    except ET.ParseError as e:
        raise ValueError(f"XML malformado: {str(e)}")
    
    # 5. Sanitizar filename
    safe_filename = secure_filename(filename)
    
    return safe_filename, contents_str


def sanitize_filter_input(value):
    """Sanitiza inputs de filtros"""
    if not value:
        return None
    
    # Converte para string
    clean_value = str(value).strip()
    
    # Limita tamanho
    if len(clean_value) > 100:
        raise ValueError("Input muito longo")
    
    # Valida caracteres permitidos (alfanuméricos, espaços, hífen, underscore, hashtag)
    if not re.match(r'^[a-zA-Z0-9\s\-_#]+$', clean_value):
        raise ValueError("Caracteres inválidos")
    
    return clean_value


def add_security_headers(response):
    """Adiciona headers de segurança"""
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.plot.ly; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data: https://flagcdn.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=()'
    return response
