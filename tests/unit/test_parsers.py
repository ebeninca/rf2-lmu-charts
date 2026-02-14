import pytest
import pandas as pd
import xml.etree.ElementTree as ET
from data.parsers import parse_xml_scores


class TestParseXmlScores:
    """Testes para a função parse_xml_scores"""
    
    def test_parse_valid_xml(self, sample_xml):
        """Testa parsing de XML válido"""
        df, race_info, incidents = parse_xml_scores(sample_xml)
        
        assert not df.empty
        assert len(df) > 0
        assert 'Driver' in df.columns
        assert 'Lap' in df.columns
        assert 'Position' in df.columns
    
    def test_parse_empty_xml(self, empty_xml):
        """Testa parsing de XML vazio"""
        df, race_info, incidents = parse_xml_scores(empty_xml)
        
        assert df.empty
        assert race_info == {}
        assert incidents == {'chat': [], 'incident': [], 'penalty': []}
    
    def test_parse_invalid_xml_raises_exception(self, invalid_xml):
        """Testa se XML malformado levanta exceção"""
        with pytest.raises(ET.ParseError):
            parse_xml_scores(invalid_xml)
    
    def test_extracts_race_info(self, sample_xml):
        """Testa extração de informações da corrida"""
        _, race_info, _ = parse_xml_scores(sample_xml)
        
        assert race_info['track'] == 'Spa-Francorchamps'
        assert race_info['course'] == 'Grand Prix'
        assert race_info['laps'] == '20'
        assert race_info['server'] == 'Test Server'
        assert race_info['track_length'] == '7004'
    
    def test_extracts_chat_messages(self, sample_xml):
        """Testa extração de mensagens de chat"""
        _, _, incidents = parse_xml_scores(sample_xml)
        
        assert len(incidents['chat']) == 1
        assert incidents['chat'][0]['et'] == '60.5'
        assert 'Hello' in incidents['chat'][0]['message']
    
    def test_extracts_incidents(self, sample_xml):
        """Testa extração de incidentes"""
        _, _, incidents = parse_xml_scores(sample_xml)
        
        assert len(incidents['incident']) == 1
        assert incidents['incident'][0]['et'] == '120.0'
        assert 'Contact' in incidents['incident'][0]['message']
    
    def test_extracts_penalties(self, sample_xml):
        """Testa extração de penalidades"""
        _, _, incidents = parse_xml_scores(sample_xml)
        
        assert len(incidents['penalty']) == 1
        assert incidents['penalty'][0]['et'] == '180.5'
        assert 'penalty' in incidents['penalty'][0]['message']
    
    def test_multiple_drivers_parsed(self, sample_xml):
        """Testa parsing de múltiplos pilotos"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        drivers = df['Driver'].unique()
        assert len(drivers) == 2
        assert 'Driver One' in drivers
        assert 'Driver Two' in drivers
    
    def test_gap_to_leader_calculated(self, sample_xml):
        """Testa cálculo de gap para o líder"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        assert 'GapToLeader' in df.columns
        lap1_data = df[df['Lap'] == 1]
        leader_gap = lap1_data[lap1_data['Position'] == 1]['GapToLeader'].iloc[0]
        assert leader_gap == 0
    
    def test_gap_to_class_leader_calculated(self, sample_xml):
        """Testa cálculo de gap para o líder da classe"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        assert 'GapToClassLeader' in df.columns
        assert 'ClassLeaderET' in df.columns
    
    def test_pit_stop_flag_identified(self, sample_xml):
        """Testa identificação de pit stops"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        pit_laps = df[df['IsPit'] == True]
        assert len(pit_laps) > 0
    
    def test_fuel_consumption_calculated(self, sample_xml):
        """Testa cálculo de consumo de combustível"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        fuel_data = df[(df['Lap'] > 0) & (df['FuelUsed'] > 0)]
        assert len(fuel_data) > 0
    
    def test_tire_wear_calculated(self, sample_xml):
        """Testa cálculo de desgaste de pneus"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        tire_data = df[(df['Lap'] > 0) & (df['TireWear'] > 0)]
        assert len(tire_data) > 0
        # Verifica se é média dos 4 pneus
        first_lap = tire_data.iloc[0]
        expected_avg = (first_lap['TWFL'] + first_lap['TWFR'] + first_lap['TWRL'] + first_lap['TWRR']) / 4
        assert abs(first_lap['TireWear'] - expected_avg) < 0.01
    
    def test_aids_parsing(self, sample_xml):
        """Testa parsing de aids"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        driver_one = df[df['Driver'] == 'Driver One'].iloc[0]
        assert 'TC3' in driver_one['Aids']
        assert 'ABS' in driver_one['Aids']
        
        driver_two = df[df['Driver'] == 'Driver Two'].iloc[0]
        assert 'PC' in driver_two['Aids']
    
    def test_tire_compounds_extracted(self, sample_xml):
        """Testa extração de compostos de pneus"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        lap_data = df[(df['Lap'] > 0) & (df['Driver'] == 'Driver One')].iloc[0]
        assert lap_data['FCompound'] == 'Dry,Soft'
        assert lap_data['RCompound'] == 'Dry,Soft'
    
    def test_sector_times_extracted(self, sample_xml):
        """Testa extração de tempos de setor"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        lap_data = df[(df['Lap'] > 0)].iloc[0]
        assert lap_data['S1'] > 0
        assert lap_data['S2'] > 0
        assert lap_data['S3'] > 0
    
    def test_invalid_lap_time_returns_zero(self):
        """Testa se lap time inválido retorna zero"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<RaceResults>
    <Driver>
        <Name>Test Driver</Name>
        <GridPos>1</GridPos>
        <Lap num="1" p="1" et="120.0">--.----</Lap>
    </Driver>
</RaceResults>"""
        df, _, _ = parse_xml_scores(xml)
        assert df[df['Lap'] == 1]['LapTime'].iloc[0] == 0
    
    def test_negative_et_returns_zero(self):
        """Testa se ET negativo retorna zero"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<RaceResults>
    <Driver>
        <Name>Test Driver</Name>
        <GridPos>1</GridPos>
        <Lap num="1" p="1" et="-10.0">120.0</Lap>
    </Driver>
</RaceResults>"""
        df, _, _ = parse_xml_scores(xml)
        assert df[df['Lap'] == 1]['ET'].iloc[0] == 0
    
    def test_missing_attribute_handled_gracefully(self):
        """Testa se a falta de um atributo é tratada, resultando em valor padrão"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<RaceResults>
    <Driver>
        <Name>Test Driver</Name>
        <GridPos>1</GridPos>
        <Lap num="1" p="1">120.0</Lap>
    </Driver>
</RaceResults>"""
        df, _, _ = parse_xml_scores(xml)
        assert df[df['Lap'] == 1]['ET'].iloc[0] == 0
    
    def test_grid_position_creates_lap_zero(self, sample_xml):
        """Testa se GridPos cria lap 0"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        lap_zero = df[df['Lap'] == 0]
        assert len(lap_zero) > 0
        assert lap_zero['Position'].iloc[0] > 0
    
    def test_no_nan_or_inf_values(self, sample_xml):
        """Testa se não há valores NaN ou infinitos"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        assert not df.isnull().any().any()
        assert not (df.select_dtypes(include=['float64', 'int64']) == float('inf')).any().any()
    
    def test_numeric_columns_properly_typed(self, sample_xml):
        """Testa se colunas numéricas têm tipo correto"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        numeric_cols = ['Lap', 'Position', 'ET', 'LapTime', 'FuelUsed', 'FuelLevel']
        for col in numeric_cols:
            assert pd.api.types.is_numeric_dtype(df[col])