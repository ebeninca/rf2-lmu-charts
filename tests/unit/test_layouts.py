import pytest
import pandas as pd
from dash import html, dcc
from presentation.layouts import create_main_layout, create_filters_section, create_tabs_section


class TestCreateMainLayout:
    """Testes para create_main_layout"""
    
    def test_creates_html_div(self, sample_dataframe, sample_race_info, sample_incidents):
        """Testa se retorna um Div HTML"""
        layout = create_main_layout(sample_dataframe, sample_race_info, sample_incidents)
        assert isinstance(layout, html.Div)
    
    def test_contains_upload_component(self, sample_dataframe, sample_race_info, sample_incidents):
        """Testa se contém componente de upload"""
        layout = create_main_layout(sample_dataframe, sample_race_info, sample_incidents)
        # Verifica se há um dcc.Upload no layout
        has_upload = self._find_component_by_type(layout, dcc.Upload)
        assert has_upload
    
    def test_contains_tabs(self, sample_dataframe, sample_race_info, sample_incidents):
        """Testa se contém tabs"""
        layout = create_main_layout(sample_dataframe, sample_race_info, sample_incidents)
        has_tabs = self._find_component_by_type(layout, dcc.Tabs)
        assert has_tabs
    
    def test_contains_stores(self, sample_dataframe, sample_race_info, sample_incidents):
        """Testa se contém stores para dados"""
        layout = create_main_layout(sample_dataframe, sample_race_info, sample_incidents)
        has_store = self._find_component_by_type(layout, dcc.Store)
        assert has_store
    
    def test_contains_filters(self, sample_dataframe, sample_race_info, sample_incidents):
        """Testa se contém filtros"""
        layout = create_main_layout(sample_dataframe, sample_race_info, sample_incidents)
        has_dropdown = self._find_component_by_type(layout, dcc.Dropdown)
        assert has_dropdown
    
    def _find_component_by_type(self, component, component_type):
        """Função auxiliar para encontrar componente por tipo"""
        if isinstance(component, component_type):
            return True
        if hasattr(component, 'children'):
            children = component.children
            if isinstance(children, list):
                for child in children:
                    if self._find_component_by_type(child, component_type):
                        return True
            elif children is not None:
                return self._find_component_by_type(children, component_type)
        return False


class TestCreateFiltersSection:
    """Testes para create_filters_section"""
    
    def test_creates_html_div(self):
        """Testa se retorna um Div HTML"""
        filters = create_filters_section()
        assert isinstance(filters, html.Div)
    
    def test_contains_class_filter(self):
        """Testa se contém filtro de classe"""
        filters = create_filters_section()
        has_class_filter = self._find_component_by_id(filters, 'class-filter')
        assert has_class_filter
    
    def test_contains_driver_filter(self):
        """Testa se contém filtro de drivers"""
        filters = create_filters_section()
        has_driver_filter = self._find_component_by_id(filters, 'driver-filter')
        assert has_driver_filter
    
    def test_contains_car_filter(self):
        """Testa se contém filtro de carros"""
        filters = create_filters_section()
        has_car_filter = self._find_component_by_id(filters, 'car-filter')
        assert has_car_filter
    
    def test_contains_vehicle_filter(self):
        """Testa se contém filtro de veículos"""
        filters = create_filters_section()
        has_veh_filter = self._find_component_by_id(filters, 'veh-filter')
        assert has_veh_filter
    
    def test_contains_cartype_filter(self):
        """Testa se contém filtro de tipo de carro"""
        filters = create_filters_section()
        has_cartype_filter = self._find_component_by_id(filters, 'cartype-filter')
        assert has_cartype_filter
    
    def _find_component_by_id(self, component, component_id):
        """Função auxiliar para encontrar componente por ID"""
        if hasattr(component, 'id') and component.id == component_id:
            return True
        if hasattr(component, 'children'):
            children = component.children
            if isinstance(children, list):
                for child in children:
                    if self._find_component_by_id(child, component_id):
                        return True
            elif children is not None:
                return self._find_component_by_id(children, component_id)
        return False


class TestCreateTabsSection:
    """Testes para create_tabs_section"""
    
    def test_creates_tabs_component(self):
        """Testa se retorna componente Tabs"""
        tabs = create_tabs_section()
        assert isinstance(tabs, dcc.Tabs)
    
    def test_has_correct_id(self):
        """Testa se tem ID correto"""
        tabs = create_tabs_section()
        assert tabs.id == 'tabs'
    
    def test_has_default_value(self):
        """Testa se tem valor padrão"""
        tabs = create_tabs_section()
        assert tabs.value == 'tab-standings'
    
    def test_contains_standings_tab(self):
        """Testa se contém tab de standings"""
        tabs = create_tabs_section()
        tab_values = [tab.value for tab in tabs.children]
        assert 'tab-standings' in tab_values
    
    def test_contains_position_tab(self):
        """Testa se contém tab de posição"""
        tabs = create_tabs_section()
        tab_values = [tab.value for tab in tabs.children]
        assert 'tab-position' in tab_values
    
    def test_contains_gap_tab(self):
        """Testa se contém tab de gap"""
        tabs = create_tabs_section()
        tab_values = [tab.value for tab in tabs.children]
        assert 'tab-gap' in tab_values
    
    def test_contains_laptimes_tab(self):
        """Testa se contém tab de lap times"""
        tabs = create_tabs_section()
        tab_values = [tab.value for tab in tabs.children]
        assert 'tab-laptimes' in tab_values
    
    def test_contains_fuel_tab(self):
        """Testa se contém tab de combustível"""
        tabs = create_tabs_section()
        tab_values = [tab.value for tab in tabs.children]
        assert 'tab-fuel' in tab_values
    
    def test_contains_tires_tab(self):
        """Testa se contém tab de pneus"""
        tabs = create_tabs_section()
        tab_values = [tab.value for tab in tabs.children]
        assert 'tab-tires' in tab_values
    
    def test_contains_incidents_tab(self):
        """Testa se contém tab de incidentes"""
        tabs = create_tabs_section()
        tab_values = [tab.value for tab in tabs.children]
        assert 'tab-incidents' in tab_values
    
    def test_has_all_seven_tabs(self):
        """Testa se tem todas as 7 tabs"""
        tabs = create_tabs_section()
        assert len(tabs.children) == 7
