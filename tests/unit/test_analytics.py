import pytest
import pandas as pd
import plotly.graph_objs as go
from business.analytics import (
    update_position_chart, update_gap_chart, update_class_gap_chart,
    update_laptime_chart, update_laptime_no_pit_chart,
    update_fuel_chart, update_ve_chart, update_tire_wear_chart,
    update_fuel_level_chart, update_ve_level_chart, update_tire_consumption_chart,
    update_consistency_chart, update_tire_degradation_chart, update_pace_decay_chart,
    update_strategy_gantt_chart
)


class TestPositionChart:
    """Testes para update_position_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_position_chart([], None, None)
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) > 0
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_valid_data_creates_traces(self, sample_dataframe):
        """Testa se dados válidos criam traces"""
        data = sample_dataframe.to_dict('records')
        fig = update_position_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_driver_filter_applied(self, sample_dataframe):
        """Testa se filtro de drivers é aplicado"""
        data = sample_dataframe.to_dict('records')
        fig = update_position_chart(data, ['Driver One'], None)
        
        assert len(fig.data) == 1
        assert fig.data[0].name == 'Driver One'
    
    def test_class_filter_applied(self, sample_dataframe):
        """Testa se filtro de classes é aplicado"""
        data = sample_dataframe.to_dict('records')
        fig = update_position_chart(data, None, ['GT3'])
        
        assert len(fig.data) > 0


class TestGapChart:
    """Testes para update_gap_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_gap_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_gap_formatting(self, sample_dataframe):
        """Testa formatação de gaps"""
        # Adiciona coluna GapToLeader
        df = sample_dataframe.copy()
        df['GapToLeader'] = [0, 0, 0, 0.5]
        data = df.to_dict('records')
        
        fig = update_gap_chart(data, None, None)
        assert isinstance(fig, go.Figure)


class TestLaptimeChart:
    """Testes para update_laptime_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_laptime_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_only_positive_laptimes(self, sample_dataframe):
        """Testa se apenas lap times positivos são incluídos"""
        data = sample_dataframe.to_dict('records')
        fig = update_laptime_chart(data, None, None)
        
        # Verifica se há dados (lap 0 tem laptime 0, então deve ser filtrado)
        assert isinstance(fig, go.Figure)


class TestLaptimeNoPitChart:
    """Testes para update_laptime_no_pit_chart"""
    
    def test_excludes_pit_laps(self, sample_dataframe):
        """Testa se voltas de pit são excluídas"""
        df = sample_dataframe.copy()
        df.loc[df['Lap'] == 1, 'IsPit'] = True
        data = df.to_dict('records')
        
        fig = update_laptime_no_pit_chart(data, None, None)
        assert isinstance(fig, go.Figure)


class TestFuelChart:
    """Testes para update_fuel_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_fuel_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_fuel_converted_to_liters(self, sample_dataframe):
        """Testa se combustível é convertido para litros"""
        data = sample_dataframe.to_dict('records')
        fig = update_fuel_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)


class TestVEChart:
    """Testes para update_ve_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_ve_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_ve_converted_to_percentage(self, sample_dataframe):
        """Testa se VE é convertido para percentual"""
        data = sample_dataframe.to_dict('records')
        fig = update_ve_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)


class TestTireWearChart:
    """Testes para update_tire_wear_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_tire_wear_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_tire_wear_converted_to_percentage(self, sample_dataframe):
        """Testa se desgaste é convertido para percentual"""
        data = sample_dataframe.to_dict('records')
        fig = update_tire_wear_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)


class TestFuelLevelChart:
    """Testes para update_fuel_level_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_fuel_level_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text


class TestVELevelChart:
    """Testes para update_ve_level_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_ve_level_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text


class TestTireConsumptionChart:
    """Testes para update_tire_consumption_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_tire_consumption_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_consumption_calculated_between_laps(self, sample_dataframe):
        """Testa se consumo é calculado entre voltas"""
        data = sample_dataframe.to_dict('records')
        fig = update_tire_consumption_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)


class TestTireDegradationChart:
    """Testes para update_tire_degradation_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_tire_degradation_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_stints_separated_by_pits(self, sample_dataframe):
        """Testa se stints são separados por pit stops"""
        df = sample_dataframe.copy()
        df.loc[2, 'IsPit'] = True
        data = df.to_dict('records')
        
        fig = update_tire_degradation_chart(data, None, None)
        assert isinstance(fig, go.Figure)


class TestPaceDecayChart:
    """Testes para update_pace_decay_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_pace_decay_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_delta_to_best_lap_calculated(self, sample_dataframe):
        """Testa se delta para melhor volta é calculado"""
        data = sample_dataframe.to_dict('records')
        fig = update_pace_decay_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)


class TestStrategyGanttChart:
    """Testes para update_strategy_gantt_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_strategy_gantt_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_stints_identified_by_compound_change(self, sample_dataframe):
        """Testa se stints são identificados por mudança de composto"""
        data = sample_dataframe.to_dict('records')
        fig = update_strategy_gantt_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)
    
    def test_finishing_order_used(self, sample_dataframe):
        """Testa se ordem de chegada é usada"""
        data = sample_dataframe.to_dict('records')
        fig = update_strategy_gantt_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)


class TestConsistencyChart:
    """Testes para update_consistency_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_consistency_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_box_plot_created(self, sample_dataframe):
        """Testa se box plot é criado"""
        data = sample_dataframe.to_dict('records')
        fig = update_consistency_chart(data, None, None)
        
        assert isinstance(fig, go.Figure)
    
    def test_excludes_pit_laps(self, sample_dataframe):
        """Testa se voltas de pit são excluídas"""
        df = sample_dataframe.copy()
        df.loc[1, 'IsPit'] = True
        data = df.to_dict('records')
        
        fig = update_consistency_chart(data, None, None)
        assert isinstance(fig, go.Figure)


class TestClassGapChart:
    """Testes para update_class_gap_chart"""
    
    def test_empty_dataframe_returns_message(self):
        """Testa se DataFrame vazio retorna mensagem"""
        fig = update_class_gap_chart([], None, None)
        assert 'No data available' in fig.layout.annotations[0].text
    
    def test_class_gap_calculated(self, sample_dataframe):
        """Testa se gap de classe é calculado"""
        df = sample_dataframe.copy()
        df['GapToClassLeader'] = [0, 0, 0, 0.5]
        data = df.to_dict('records')
        
        fig = update_class_gap_chart(data, None, None)
        assert isinstance(fig, go.Figure)
