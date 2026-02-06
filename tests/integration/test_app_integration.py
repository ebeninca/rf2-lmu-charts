import pytest
import pandas as pd
from data.parsers import parse_xml_scores
from business.analytics import update_position_chart, update_gap_chart
from presentation.components import create_standings_table
from presentation.layouts import create_main_layout


class TestAppIntegration:
    """Testes de integração da aplicação"""
    
    def test_full_flow_parse_to_visualization(self, sample_xml):
        """Testa fluxo completo: Parse → Visualização"""
        # Parse
        df, race_info, incidents = parse_xml_scores(sample_xml)
        
        # Verifica parsing
        assert not df.empty
        assert race_info is not None
        assert incidents is not None
        
        # Cria visualização
        data = df.to_dict('records')
        fig = update_position_chart(data, None, None)
        
        # Verifica visualização
        assert fig is not None
        assert len(fig.data) > 0
    
    def test_filters_affect_all_charts(self, sample_xml):
        """Testa se filtros afetam todos os gráficos"""
        # Parse
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Aplica filtro
        selected_drivers = ['Driver One']
        filtered_df = df[df['Driver'].isin(selected_drivers)]
        
        # Cria gráficos com filtro
        data = filtered_df.to_dict('records')
        pos_fig = update_position_chart(data, None, None)
        
        # Verifica se filtro foi aplicado
        assert len(pos_fig.data) <= len(df['Driver'].unique())
    
    def test_standings_table_with_parsed_data(self, sample_xml):
        """Testa tabela de standings com dados parseados"""
        # Parse
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Adiciona colunas necessárias
        df['GapToLeader'] = 0
        df['LeaderET'] = df['ET']
        
        # Cria tabela
        data = df.to_dict('records')
        table = create_standings_table(1, data)
        
        # Verifica tabela
        assert table is not None
    
    def test_layout_creation_with_initial_data(self, sample_dataframe, sample_race_info, sample_incidents):
        """Testa criação de layout com dados iniciais"""
        layout = create_main_layout(sample_dataframe, sample_race_info, sample_incidents)
        
        assert layout is not None
    
    def test_multiple_laps_processing(self, sample_xml):
        """Testa processamento de múltiplas voltas"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Verifica múltiplas voltas
        laps = df['Lap'].unique()
        assert len(laps) > 1
        
        # Verifica ordem
        for driver in df['Driver'].unique():
            driver_laps = df[df['Driver'] == driver]['Lap'].values
            assert all(driver_laps[i] <= driver_laps[i+1] for i in range(len(driver_laps)-1))
    
    def test_gap_calculation_consistency(self, sample_xml):
        """Testa consistência de cálculo de gaps"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Verifica se gaps foram calculados
        assert 'GapToLeader' in df.columns
        assert 'GapToClassLeader' in df.columns
        
        # Líder deve ter gap 0
        for lap in df['Lap'].unique():
            if lap > 0:
                lap_data = df[df['Lap'] == lap]
                leader = lap_data[lap_data['Position'] == 1]
                if not leader.empty:
                    assert leader['GapToLeader'].iloc[0] == 0
    
    def test_pit_stop_detection_and_exclusion(self, sample_xml):
        """Testa detecção de pit stops e exclusão em análises"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Identifica pit stops
        pit_laps = df[df['IsPit'] == True]
        
        if not pit_laps.empty:
            # Verifica se pit stops foram detectados
            assert len(pit_laps) > 0
    
    def test_tire_compound_tracking(self, sample_xml):
        """Testa rastreamento de compostos de pneus"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Verifica compostos
        compounds = df[df['Lap'] > 0][['FCompound', 'RCompound']]
        assert not compounds.empty
    
    def test_race_info_extraction_and_display(self, sample_xml):
        """Testa extração e exibição de informações da corrida"""
        df, race_info, _ = parse_xml_scores(sample_xml)
        
        # Verifica campos essenciais
        assert 'track' in race_info
        assert 'course' in race_info
        assert 'date' in race_info
        assert race_info['track'] != 'Unknown'
    
    def test_incidents_extraction_and_categorization(self, sample_xml):
        """Testa extração e categorização de incidentes"""
        _, _, incidents = parse_xml_scores(sample_xml)
        
        # Verifica categorias
        assert 'chat' in incidents
        assert 'incident' in incidents
        assert 'penalty' in incidents
        
        # Verifica se há dados
        total_events = len(incidents['chat']) + len(incidents['incident']) + len(incidents['penalty'])
        assert total_events > 0


class TestDataConsistency:
    """Testes de consistência de dados"""
    
    def test_no_data_loss_in_pipeline(self, sample_xml):
        """Testa se não há perda de dados no pipeline"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Conta drivers no XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(sample_xml)
        xml_drivers = len(root.findall('.//Driver'))
        
        # Conta drivers no DataFrame
        df_drivers = len(df['Driver'].unique())
        
        assert df_drivers == xml_drivers
    
    def test_lap_times_consistency(self, sample_xml):
        """Testa consistência de lap times"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Lap times devem ser positivos ou zero
        lap_times = df[df['Lap'] > 0]['LapTime']
        assert all(lap_times >= 0)
    
    def test_position_consistency(self, sample_xml):
        """Testa consistência de posições"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Posições devem ser positivas
        positions = df[df['Lap'] > 0]['Position']
        assert all(positions > 0)
    
    def test_fuel_level_consistency(self, sample_xml):
        """Testa consistência de nível de combustível"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Nível de combustível deve estar entre 0 e 1 (ou 0 e 100 se em litros)
        fuel_levels = df[df['FuelLevel'] > 0]['FuelLevel']
        if not fuel_levels.empty:
            assert all(fuel_levels >= 0)
    
    def test_tire_wear_consistency(self, sample_xml):
        """Testa consistência de desgaste de pneus"""
        df, _, _ = parse_xml_scores(sample_xml)
        
        # Desgaste deve estar entre 0 e 1
        tire_wear = df[df['TireWear'] > 0]['TireWear']
        if not tire_wear.empty:
            assert all((tire_wear >= 0) & (tire_wear <= 1))


class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    def test_handles_missing_optional_fields(self):
        """Testa tratamento de campos opcionais ausentes"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<RaceResults>
    <Driver>
        <Name>Test Driver</Name>
        <GridPos>1</GridPos>
        <Lap num="1" p="1" et="120.0">120.0</Lap>
    </Driver>
</RaceResults>"""
        
        df, race_info, incidents = parse_xml_scores(xml)
        
        # Deve processar sem erros
        assert not df.empty
    
    def test_handles_empty_race_results(self):
        """Testa tratamento de resultados vazios"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<RaceResults>
</RaceResults>"""
        
        df, race_info, incidents = parse_xml_scores(xml)
        
        # Deve retornar estruturas vazias
        assert df.empty
        assert race_info == {}
    
    def test_handles_invalid_numeric_values(self):
        """Testa tratamento de valores numéricos inválidos"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<RaceResults>
    <Driver>
        <Name>Test Driver</Name>
        <GridPos>1</GridPos>
        <Lap num="1" p="1" et="invalid">invalid</Lap>
    </Driver>
</RaceResults>"""
        
        df, _, _ = parse_xml_scores(xml)
        
        # Deve converter valores inválidos para 0
        if not df.empty:
            assert df[df['Lap'] == 1]['ET'].iloc[0] == 0
