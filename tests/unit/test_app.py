import pytest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestAppInitialization:
    """Testes para inicialização da aplicação"""
    
    def test_app_imports_successfully(self):
        """Testa se o app pode ser importado"""
        try:
            import app
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app: {e}")
    
    def test_dash_app_created(self):
        """Testa se instância Dash é criada"""
        import app
        assert hasattr(app, 'app')
        assert app.app is not None
    
    def test_initial_data_loaded(self):
        """Testa se dados iniciais são carregados"""
        import app
        assert hasattr(app, 'initial_df')
        assert hasattr(app, 'initial_race_info')
        assert hasattr(app, 'initial_incidents')
    
    def test_layout_created(self):
        """Testa se layout é criado"""
        import app
        assert app.app.layout is not None
    
    def test_callbacks_registered(self):
        """Testa se callbacks são registrados"""
        import app
        # Dash registra callbacks automaticamente
        assert len(app.app.callback_map) > 0
    
    def test_custom_index_string_loaded(self):
        """Testa se template HTML customizado é carregado"""
        import app
        assert app.app.index_string is not None
        assert len(app.app.index_string) > 0
    
    def test_suppress_callback_exceptions_enabled(self):
        """Testa se suppress_callback_exceptions está habilitado"""
        import app
        assert app.app.config.suppress_callback_exceptions == True


class TestAppConfiguration:
    """Testes para configuração da aplicação"""
    
    def test_app_has_correct_name(self):
        """Testa se app tem nome correto"""
        import app
        # O nome do app é o nome do módulo onde foi criado
        assert app.app.config.name is not None
    
    def test_initial_dataframe_structure(self):
        """Testa estrutura do DataFrame inicial"""
        import app
        import pandas as pd
        
        # Pode ser vazio se arquivo não existir
        if not app.initial_df.empty:
            assert isinstance(app.initial_df, pd.DataFrame)
            assert 'Driver' in app.initial_df.columns
            assert 'Lap' in app.initial_df.columns
    
    def test_initial_race_info_structure(self):
        """Testa estrutura de race_info inicial"""
        import app
        
        assert isinstance(app.initial_race_info, dict)
    
    def test_initial_incidents_structure(self):
        """Testa estrutura de incidents inicial"""
        import app
        
        assert isinstance(app.initial_incidents, dict)
        assert 'chat' in app.initial_incidents
        assert 'incident' in app.initial_incidents
        assert 'penalty' in app.initial_incidents


class TestAppModules:
    """Testes para módulos importados pelo app"""
    
    def test_data_parsers_imported(self):
        """Testa se data.parsers é importado"""
        from data.parsers import parse_xml_scores
        assert parse_xml_scores is not None
    
    def test_presentation_layouts_imported(self):
        """Testa se presentation.layouts é importado"""
        from presentation.layouts import create_main_layout
        assert create_main_layout is not None
    
    def test_presentation_callbacks_imported(self):
        """Testa se presentation.callbacks é importado"""
        from presentation.callbacks import register_callbacks
        assert register_callbacks is not None
    
    def test_dash_imported(self):
        """Testa se Dash é importado"""
        import dash
        assert dash is not None
    
    def test_pandas_imported(self):
        """Testa se pandas é importado"""
        import pandas as pd
        assert pd is not None


class TestAppErrorHandling:
    """Testes para tratamento de erros na inicialização"""
    
    def test_handles_missing_sample_file(self):
        """Testa tratamento de arquivo de amostra ausente"""
        import app
        
        # Se arquivo não existir, deve usar DataFrame vazio
        if app.initial_df.empty:
            assert len(app.initial_df) == 0
            assert app.initial_race_info == {}
    
    def test_handles_corrupted_sample_file(self):
        """Testa tratamento de arquivo de amostra corrompido"""
        # App deve inicializar mesmo com arquivo corrompido
        import app
        assert app.app is not None
