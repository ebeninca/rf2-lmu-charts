"""
Testes para validar implementação de segurança
"""

import pytest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestSecurityImports:
    """Testes de imports de segurança"""
    
    def test_flask_limiter_installed(self):
        """Testa se Flask-Limiter está instalado"""
        from flask_limiter import Limiter
        assert Limiter is not None
    
    def test_werkzeug_installed(self):
        """Testa se Werkzeug está instalado"""
        from werkzeug.utils import secure_filename
        assert secure_filename is not None


class TestSecurityModule:
    """Testes para o módulo de segurança"""
    
    def test_security_module_exists(self):
        """Testa se o módulo security.py existe"""
        import security.security as security
        assert security is not None
    
    def test_validate_upload_function_exists(self):
        """Testa se função validate_upload existe"""
        import security.security as security
        assert hasattr(security, 'validate_upload')
        assert callable(security.validate_upload)
    
    def test_sanitize_filter_input_function_exists(self):
        """Testa se função sanitize_filter_input existe"""
        import security.security as security
        assert hasattr(security, 'sanitize_filter_input')
        assert callable(security.sanitize_filter_input)
    
    def test_add_security_headers_function_exists(self):
        """Testa se função add_security_headers existe"""
        import security.security as security
        assert hasattr(security, 'add_security_headers')
        assert callable(security.add_security_headers)
    
    def test_log_suspicious_activity_function_exists(self):
        """Testa se função log_suspicious_activity existe"""
        import security.security as security
        assert hasattr(security, 'log_suspicious_activity')
        assert callable(security.log_suspicious_activity)


class TestSecureParser:
    """Testes para o parser seguro"""
    
    def test_parsers_secure_exists(self):
        """Testa se arquivo parsers_secure.py existe"""
        from data.parsers_secure import parse_xml_scores, parse_xml_secure
        assert parse_xml_scores is not None
        assert parse_xml_secure is not None
    
    def test_parse_xml_scores_function_exists(self):
        """Testa se função parse_xml_scores existe"""
        from data.parsers_secure import parse_xml_scores
        assert callable(parse_xml_scores)
    
    def test_parse_xml_secure_function_exists(self):
        """Testa se função parse_xml_secure existe"""
        from data.parsers_secure import parse_xml_secure
        assert callable(parse_xml_secure)


class TestGunicornConfig:
    """Testes para configuração do Gunicorn"""
    
    def test_gunicorn_config_exists(self):
        """Testa se arquivo gunicorn.conf.py existe"""
        assert os.path.exists('gunicorn.conf.py')


class TestEnvExample:
    """Testes para arquivo .env.example"""
    
    def test_env_example_exists(self):
        """Testa se arquivo .env.example existe"""
        assert os.path.exists('.env.example')


class TestGitignore:
    """Testes para .gitignore com entradas de segurança"""
    
    def test_gitignore_exists(self):
        """Testa se arquivo .gitignore existe"""
        assert os.path.exists('.gitignore')
    
    def test_gitignore_has_env_entry(self):
        """Testa se .gitignore contém entrada .env"""
        with open('.gitignore', 'r') as f:
            content = f.read()
        assert '.env' in content
    
    def test_gitignore_has_logs_entry(self):
        """Testa se .gitignore contém entrada logs/"""
        with open('.gitignore', 'r') as f:
            content = f.read()
        assert 'logs/' in content
    
    def test_gitignore_has_log_extension_entry(self):
        """Testa se .gitignore contém entrada *.log"""
        with open('.gitignore', 'r') as f:
            content = f.read()
        assert '*.log' in content


class TestXXEProtection:
    """Testes para proteção contra XXE"""
    
    def test_xxe_external_entity_blocked(self):
        """Testa se entidades externas (XXE) são bloqueadas"""
        from data.parsers_secure import parse_xml_secure
        
        # XML malicioso com entidade EXTERNA (XXE attack)
        malicious_xml = '''<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>'''
        
        try:
            result = parse_xml_secure(malicious_xml)
            # Se chegou aqui, verificar se a entidade foi expandida
            if result.text and 'root:' in result.text:
                pytest.fail("XXE não foi bloqueado - arquivo foi lido!")
            else:
                # XXE foi bloqueado corretamente
                assert True
        except Exception:
            # Exceção é esperada quando XXE é bloqueado
            assert True



def test_file_invalid_extension():
    """Testa se arquivo com extensão inválida é bloqueado"""
    from security.security import validate_upload
    
    with pytest.raises(ValueError):
        validate_upload(b"test", "malicious.exe")


def test_file_too_large():
    """Testa se arquivo muito grande é bloqueado"""
    from security.security import validate_upload
    
    # Simular arquivo 25MB
    large_content = b"x" * (25 * 1024 * 1024)
    
    with pytest.raises(ValueError):
        validate_upload(large_content, "large.xml")


def test_file_malformed_xml():
    """Testa se XML malformado é bloqueado"""
    from security.security import validate_upload
    
    with pytest.raises(ValueError):
        validate_upload(b"<invalid>xml", "invalid.xml")


def test_file_valid_xml():
    """Testa se XML válido é aceito"""
    from security.security import validate_upload
    
    valid_xml = b'<?xml version="1.0"?><root><test>valid</test></root>'
    safe_name, content = validate_upload(valid_xml, "valid.xml")
    
    assert safe_name is not None
    assert content is not None


class TestLogsDirectory:
    """Testes para o diretório de logs"""
    
    def test_logs_directory_can_be_created(self):
        """Testa se diretório logs pode ser criado"""
        os.makedirs('logs', exist_ok=True)
        assert os.path.exists('logs')
        assert os.path.isdir('logs')
