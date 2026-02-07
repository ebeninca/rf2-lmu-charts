import pytest
from data.track_flags import get_country_flag, TRACK_COUNTRY_MAP, COUNTRY_NAMES


class TestGetCountryFlag:
    """Testes para a função get_country_flag"""
    
    def test_known_track_returns_correct_code(self):
        """Testa se circuitos conhecidos retornam código correto"""
        code, name = get_country_flag('Spa-Francorchamps')
        assert code == 'BE'
        assert name == 'Belgium'
    
    def test_case_insensitive_matching(self):
        """Testa se a busca é case insensitive"""
        assert get_country_flag('spa')[0] == 'BE'
        assert get_country_flag('SPA')[0] == 'BE'
        assert get_country_flag('Spa')[0] == 'BE'
    
    def test_unknown_track_returns_empty(self):
        """Testa se circuito desconhecido retorna strings vazias"""
        code, name = get_country_flag('Unknown Circuit')
        assert code == ''
        assert name == ''
    
    def test_none_returns_empty(self):
        """Testa se None retorna strings vazias"""
        code, name = get_country_flag(None)
        assert code == ''
        assert name == ''
    
    def test_unknown_string_returns_empty(self):
        """Testa se 'Unknown' retorna strings vazias"""
        code, name = get_country_flag('Unknown')
        assert code == ''
        assert name == ''
    
    def test_partial_match(self):
        """Testa se match parcial funciona"""
        code, name = get_country_flag('Circuit de Spa-Francorchamps')
        assert code == 'BE'
        assert name == 'Belgium'
    
    @pytest.mark.parametrize("track,expected_code", [
        ('Monza', 'IT'),
        ('Silverstone', 'GB'),
        ('Nürburgring', 'DE'),
        ('Barcelona', 'ES'),
        ('Interlagos', 'BR'),
        ('Suzuka', 'JP'),
        ('Sebring', 'US'),
    ])
    def test_multiple_known_tracks(self, track, expected_code):
        """Testa múltiplos circuitos conhecidos"""
        code, _ = get_country_flag(track)
        assert code == expected_code
    
    def test_all_mapped_tracks_have_country_names(self):
        """Testa se todos os códigos de país têm nomes correspondentes"""
        for track, country_code in TRACK_COUNTRY_MAP.items():
            assert country_code in COUNTRY_NAMES, f"Country code {country_code} for {track} not in COUNTRY_NAMES"
    
    def test_empty_string_returns_empty(self):
        """Testa se string vazia retorna strings vazias"""
        code, name = get_country_flag('')
        assert code == ''
        assert name == ''
