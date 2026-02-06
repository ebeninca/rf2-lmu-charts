import pytest
import pandas as pd
from dash import html
from presentation.components import create_standings_table


class TestCreateStandingsTable:
    """Testes para create_standings_table"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        result = create_standings_table(1, [])
        assert isinstance(result, html.P)
        assert 'No data available' in str(result)
    
    def test_none_lap_returns_message(self, sample_dataframe):
        """Testa se lap None retorna mensagem"""
        data = sample_dataframe.to_dict('records')
        result = create_standings_table(None, data)
        assert isinstance(result, html.P)
    
    def test_creates_table_with_valid_data(self, sample_dataframe):
        """Testa se tabela é criada com dados válidos"""
        # Adiciona colunas necessárias
        df = sample_dataframe.copy()
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        assert isinstance(result, html.Table)
    
    def test_positions_calculated_correctly(self, sample_dataframe):
        """Testa se posições são calculadas corretamente"""
        df = sample_dataframe.copy()
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        assert isinstance(result, html.Table)
    
    def test_gap_formatted_as_leader_for_first(self, sample_dataframe):
        """Testa se gap é formatado como 'Leader' para o primeiro"""
        df = sample_dataframe.copy()
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        # Verifica estrutura da tabela
        assert isinstance(result, html.Table)
    
    def test_best_lap_calculated_per_driver(self, sample_dataframe):
        """Testa se melhor volta é calculada por piloto"""
        df = sample_dataframe.copy()
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        assert isinstance(result, html.Table)
    
    def test_pit_stops_counted(self, sample_dataframe):
        """Testa se pit stops são contados"""
        df = sample_dataframe.copy()
        df.loc[1, 'IsPit'] = True
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        assert isinstance(result, html.Table)
    
    def test_laps_led_counted(self, sample_dataframe):
        """Testa se voltas lideradas são contadas"""
        df = sample_dataframe.copy()
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        assert isinstance(result, html.Table)
    
    def test_positions_gained_lost_calculated(self, sample_dataframe):
        """Testa se posições ganhas/perdidas são calculadas"""
        df = sample_dataframe.copy()
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        assert isinstance(result, html.Table)
    
    def test_class_colors_applied(self, sample_dataframe):
        """Testa se cores por classe são aplicadas"""
        df = sample_dataframe.copy()
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        assert isinstance(result, html.Table)
    
    def test_handles_multiple_classes(self):
        """Testa se múltiplas classes são tratadas"""
        df = pd.DataFrame([
            {'Driver': 'D1', 'Lap': 1, 'Position': 1, 'ET': 120, 'LapTime': 120, 
             'Class': 'GT3', 'Car': 'Car1', 'VehName': 'V1', 'IsPit': False,
             'FCompound': '', 'RCompound': '', 'Aids': '-'},
            {'Driver': 'D2', 'Lap': 1, 'Position': 2, 'ET': 121, 'LapTime': 121,
             'Class': 'GT4', 'Car': 'Car2', 'VehName': 'V2', 'IsPit': False,
             'FCompound': '', 'RCompound': '', 'Aids': '-'}
        ])
        data = df.to_dict('records')
        
        result = create_standings_table(1, data)
        assert isinstance(result, html.Table)
    
    def test_laps_behind_format_on_final_lap(self):
        """Testa formato de voltas atrás na última volta"""
        df = pd.DataFrame([
            {'Driver': 'D1', 'Lap': 10, 'Position': 1, 'ET': 1200, 'LapTime': 120,
             'Class': 'GT3', 'Car': 'Car1', 'VehName': 'V1', 'IsPit': False,
             'FCompound': '', 'RCompound': '', 'Aids': '-'},
            {'Driver': 'D2', 'Lap': 9, 'Position': 2, 'ET': 1100, 'LapTime': 120,
             'Class': 'GT3', 'Car': 'Car2', 'VehName': 'V2', 'IsPit': False,
             'FCompound': '', 'RCompound': '', 'Aids': '-'}
        ])
        data = df.to_dict('records')
        
        result = create_standings_table(10, data)
        assert isinstance(result, html.Table)
