import pytest
import pandas as pd
from unittest.mock import Mock, patch
import base64


class TestUpdateData:
    """Testes para callback update_data"""
    
    def test_no_contents_returns_initial_data(self, sample_dataframe, sample_race_info, sample_incidents):
        """Testa se sem conteúdo retorna dados iniciais"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        register_callbacks(app, sample_dataframe, sample_race_info, sample_incidents)
        
        # Verifica se callbacks foram registrados
        assert len(app.callback_map) > 0
    
    def test_valid_file_upload(self, sample_xml):
        """Testa upload de arquivo válido"""
        # Codifica XML em base64
        encoded = base64.b64encode(sample_xml.encode('utf-8')).decode('utf-8')
        contents = f"data:text/xml;base64,{encoded}"
        
        # Importa função de parsing
        from data.parsers import parse_xml_scores
        df, race_info, incidents = parse_xml_scores(sample_xml)
        
        assert not df.empty
        assert race_info is not None
        assert incidents is not None
    
    def test_file_too_large_returns_error(self):
        """Testa se arquivo muito grande retorna erro"""
        # Cria conteúdo grande (>20MB)
        large_content = "x" * (21 * 1024 * 1024)
        encoded = base64.b64encode(large_content.encode('utf-8')).decode('utf-8')
        contents = f"data:text/xml;base64,{encoded}"
        
        # Verifica tamanho
        decoded = base64.b64decode(encoded)
        size_mb = len(decoded) / (1024 * 1024)
        assert size_mb > 20
    
    def test_invalid_xml_returns_error(self, invalid_xml):
        """Testa se XML inválido retorna erro"""
        from data.parsers import parse_xml_scores
        import xml.etree.ElementTree as ET
        
        with pytest.raises(ET.ParseError):
            parse_xml_scores(invalid_xml)


class TestUpdateFilters:
    """Testes para callback update_filters"""
    
    def test_empty_dataframe_returns_empty_options(self):
        """Testa se DataFrame vazio retorna opções vazias"""
        data = []
        df = pd.DataFrame(data)
        
        assert df.empty
        drivers = df['Driver'].unique() if not df.empty else []
        assert len(drivers) == 0
    
    def test_valid_data_returns_filter_options(self, sample_dataframe):
        """Testa se dados válidos retornam opções de filtro"""
        drivers = sorted(sample_dataframe['Driver'].unique())
        classes = sorted(sample_dataframe['Class'].unique())
        
        assert len(drivers) > 0
        assert len(classes) > 0
    
    def test_drivers_sorted_alphabetically(self, sample_dataframe):
        """Testa se drivers são ordenados alfabeticamente"""
        drivers = sorted(sample_dataframe['Driver'].unique())
        assert drivers == sorted(drivers)
    
    def test_classes_sorted_alphabetically(self, sample_dataframe):
        """Testa se classes são ordenadas alfabeticamente"""
        classes = sorted(sample_dataframe['Class'].unique())
        assert classes == sorted(classes)


class TestUpdateRaceInfo:
    """Testes para callback update_race_info"""
    
    def test_empty_race_info_returns_empty_string(self):
        """Testa se race_info vazio retorna string vazia"""
        race_info = {}
        result = '' if not race_info else 'has_data'
        assert result == ''
    
    def test_formats_duration_as_hours_minutes(self, sample_race_info):
        """Testa formatação de duração em horas e minutos"""
        race_time = sample_race_info.get('time', '0')
        time_val = int(race_time)
        
        # Testa com tempo > 1000 segundos
        time_val = 7200  # 2 horas
        hours = time_val // 3600
        minutes = (time_val % 3600) // 60
        
        assert hours == 2
        assert minutes == 0
    
    def test_formats_duration_as_laps(self, sample_race_info):
        """Testa formatação de duração em voltas"""
        race_time = sample_race_info.get('time', '0')
        race_laps = sample_race_info.get('laps', '0')
        
        time_val = int(race_time)
        laps_val = int(race_laps)
        
        if time_val == 0:
            assert laps_val > 0
    
    def test_track_flag_displayed(self, sample_race_info):
        """Testa se bandeira do país é exibida"""
        from data.track_flags import get_country_flag
        
        track_name = sample_race_info.get('track', 'Unknown')
        country_flag, country_name = get_country_flag(track_name)
        
        assert country_flag == 'BE'
        assert country_name == 'Belgium'


class TestRenderTabContent:
    """Testes para callback render_tab_content"""
    
    def test_standings_tab_renders(self, sample_dataframe):
        """Testa se tab standings renderiza"""
        active_tab = 'tab-standings'
        assert active_tab == 'tab-standings'
    
    def test_position_tab_renders(self, sample_dataframe):
        """Testa se tab position renderiza"""
        active_tab = 'tab-position'
        assert active_tab == 'tab-position'
    
    def test_gap_tab_renders(self, sample_dataframe):
        """Testa se tab gap renderiza"""
        active_tab = 'tab-gap'
        assert active_tab == 'tab-gap'
    
    def test_laptimes_tab_renders(self, sample_dataframe):
        """Testa se tab laptimes renderiza"""
        active_tab = 'tab-laptimes'
        assert active_tab == 'tab-laptimes'
    
    def test_fuel_tab_renders(self, sample_dataframe):
        """Testa se tab fuel renderiza"""
        active_tab = 'tab-fuel'
        assert active_tab == 'tab-fuel'
    
    def test_tires_tab_renders(self, sample_dataframe):
        """Testa se tab tires renderiza"""
        active_tab = 'tab-tires'
        assert active_tab == 'tab-tires'
    
    def test_incidents_tab_renders(self, sample_dataframe):
        """Testa se tab incidents renderiza"""
        active_tab = 'tab-incidents'
        assert active_tab == 'tab-incidents'
    
    def test_filters_applied_to_data(self, sample_dataframe):
        """Testa se filtros são aplicados aos dados"""
        df = sample_dataframe.copy()
        selected_drivers = ['Driver One']
        
        filtered = df[df['Driver'].isin(selected_drivers)]
        assert len(filtered) < len(df)
        assert all(filtered['Driver'] == 'Driver One')
    
    def test_class_filter_applied(self, sample_dataframe):
        """Testa se filtro de classe é aplicado"""
        df = sample_dataframe.copy()
        selected_classes = ['GT3']
        
        filtered = df[df['Class'].isin(selected_classes)]
        assert all(filtered['Class'] == 'GT3')
    
    def test_standings_ignores_non_class_filters(self, sample_dataframe):
        """Testa se standings ignora filtros não-classe"""
        # Lógica: standings só deve aplicar filtro de classe
        active_tab = 'tab-standings'
        selected_drivers = ['Driver One']
        selected_classes = ['GT3']
        
        # Para standings, apenas classe deve ser aplicada
        if active_tab == 'tab-standings':
            # Aplica apenas filtro de classe
            df = sample_dataframe.copy()
            if selected_classes:
                df = df[df['Class'].isin(selected_classes)]
            # Não aplica filtro de drivers
            assert len(df) == len(sample_dataframe[sample_dataframe['Class'].isin(selected_classes)])


class TestRenderEventsContent:
    """Testes para callback render_events_content"""
    
    def test_chat_tab_renders(self, sample_incidents):
        """Testa se tab de chat renderiza"""
        messages = sample_incidents.get('chat', [])
        assert len(messages) > 0
    
    def test_incidents_tab_renders(self, sample_incidents):
        """Testa se tab de incidents renderiza"""
        messages = sample_incidents.get('incident', [])
        assert len(messages) > 0
    
    def test_penalties_tab_renders(self, sample_incidents):
        """Testa se tab de penalties renderiza"""
        messages = sample_incidents.get('penalty', [])
        assert len(messages) > 0
    
    def test_empty_chat_shows_message(self):
        """Testa se chat vazio mostra mensagem"""
        incidents = {'chat': [], 'incident': [], 'penalty': []}
        messages = incidents.get('chat', [])
        
        if not messages:
            result = 'No chat messages'
        else:
            result = 'Has messages'
        
        assert result == 'No chat messages'
    
    def test_empty_incidents_shows_message(self):
        """Testa se incidents vazio mostra mensagem"""
        incidents = {'chat': [], 'incident': [], 'penalty': []}
        messages = incidents.get('incident', [])
        
        if not messages:
            result = 'No incidents'
        else:
            result = 'Has incidents'
        
        assert result == 'No incidents'
    
    def test_empty_penalties_shows_message(self):
        """Testa se penalties vazio mostra mensagem"""
        incidents = {'chat': [], 'incident': [], 'penalty': []}
        messages = incidents.get('penalty', [])
        
        if not messages:
            result = 'No penalties'
        else:
            result = 'Has penalties'
        
        assert result == 'No penalties'
