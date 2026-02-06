import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_xml():
    """XML de corrida válido para testes - lê do arquivo valid_race.xml"""
    xml_path = Path(__file__).parent / 'test_data' / 'valid_race.xml'
    return xml_path.read_text(encoding='utf-8')


@pytest.fixture
def empty_xml():
    """XML vazio"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<RaceResults>
</RaceResults>"""


@pytest.fixture
def invalid_xml():
    """XML malformado"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<RaceResults>
    <Driver>
        <Name>Test</Name>
    </Driver>
"""


@pytest.fixture
def sample_dataframe():
    """DataFrame com dados de corrida"""
    return pd.DataFrame([
        {'Driver': 'Driver One', 'Lap': 0, 'Position': 1, 'ET': 0, 'LapTime': 0, 'IsPit': False,
         'FuelUsed': 0, 'FuelLevel': 0, 'VE': 0, 'VELevel': 0, 'TireWear': 0, 'Class': 'GT3',
         'Car': 'Team A #1', 'VehName': 'Car Model A', 'CarType': 'Type A', 'FCompound': '', 
         'RCompound': '', 'Aids': 'TC3,ABS', 'TWFL': 0, 'TWFR': 0, 'TWRL': 0, 'TWRR': 0,
         'S1': 0, 'S2': 0, 'S3': 0},
        {'Driver': 'Driver One', 'Lap': 1, 'Position': 1, 'ET': 120.5, 'LapTime': 120.5, 'IsPit': False,
         'FuelUsed': 0.05, 'FuelLevel': 0.95, 'VE': 0.1, 'VELevel': 0.9, 'TireWear': 0.965, 'Class': 'GT3',
         'Car': 'Team A #1', 'VehName': 'Car Model A', 'CarType': 'Type A', 'FCompound': 'Dry,Soft',
         'RCompound': 'Dry,Soft', 'Aids': 'TC3,ABS', 'TWFL': 0.98, 'TWFR': 0.97, 'TWRL': 0.96, 'TWRR': 0.95,
         'S1': 40.1, 'S2': 40.2, 'S3': 40.2},
        {'Driver': 'Driver Two', 'Lap': 0, 'Position': 2, 'ET': 0, 'LapTime': 0, 'IsPit': False,
         'FuelUsed': 0, 'FuelLevel': 0, 'VE': 0, 'VELevel': 0, 'TireWear': 0, 'Class': 'GT3',
         'Car': 'Team B #2', 'VehName': 'Car Model B', 'CarType': 'Type B', 'FCompound': '',
         'RCompound': '', 'Aids': 'PC', 'TWFL': 0, 'TWFR': 0, 'TWRL': 0, 'TWRR': 0,
         'S1': 0, 'S2': 0, 'S3': 0},
        {'Driver': 'Driver Two', 'Lap': 1, 'Position': 2, 'ET': 121.0, 'LapTime': 121.0, 'IsPit': False,
         'FuelUsed': 0.05, 'FuelLevel': 0.95, 'VE': 0, 'VELevel': 0, 'TireWear': 0.965, 'Class': 'GT3',
         'Car': 'Team B #2', 'VehName': 'Car Model B', 'CarType': 'Type B', 'FCompound': 'Dry,Medium',
         'RCompound': 'Dry,Medium', 'Aids': 'PC', 'TWFL': 0.98, 'TWFR': 0.97, 'TWRL': 0.96, 'TWRR': 0.95,
         'S1': 40.5, 'S2': 40.3, 'S3': 40.2}
    ])


@pytest.fixture
def sample_race_info():
    """Dicionário de informações da corrida"""
    return {
        'track': 'Spa-Francorchamps',
        'course': 'Grand Prix',
        'date': '2024-01-15 14:30:00',
        'laps': '20',
        'time': '0',
        'server': 'Test Server',
        'track_length': '7004',
        'mech_fail': '0',
        'damage_mult': '100',
        'fuel_mult': '1.0',
        'tire_mult': '1.0',
        'tire_warmers': '1',
        'game_version': '1.0.0.0'
    }


@pytest.fixture
def sample_incidents():
    """Dicionário de incidentes"""
    return {
        'chat': [{'et': '60.5', 'message': 'Driver One: Hello!'}],
        'incident': [{'et': '120.0', 'message': 'Contact between Driver One and Driver Two'}],
        'penalty': [{'et': '180.5', 'message': 'Driver Two: 5 second penalty'}]
    }
