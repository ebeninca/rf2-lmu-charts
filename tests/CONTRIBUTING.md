# Guia para Adicionar Novos Testes

## Template Básico de Teste

```python
import pytest
from seu_modulo import sua_funcao


class TestSuaFuncao:
    """Testes para sua_funcao"""
    
    def test_caso_normal(self):
        """Testa comportamento normal"""
        # Arrange (Preparar)
        input_data = "test"
        expected = "TEST"
        
        # Act (Executar)
        result = sua_funcao(input_data)
        
        # Assert (Verificar)
        assert result == expected
    
    def test_caso_edge(self):
        """Testa caso extremo"""
        assert sua_funcao("") == ""
    
    def test_caso_erro(self):
        """Testa tratamento de erro"""
        with pytest.raises(ValueError):
            sua_funcao(None)
```

## Usando Fixtures

```python
@pytest.fixture
def sample_data():
    """Dados de exemplo para testes"""
    return {
        'key': 'value',
        'number': 42
    }


class TestComFixture:
    def test_usando_fixture(self, sample_data):
        """Testa usando fixture"""
        assert sample_data['number'] == 42
```

## Parametrização

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_multiplos_casos(input, expected):
    """Testa múltiplos casos de uma vez"""
    assert sua_funcao(input) == expected
```

## Testando Exceções

```python
def test_levanta_excecao():
    """Testa se exceção é levantada"""
    with pytest.raises(ValueError) as exc_info:
        funcao_que_falha()
    
    assert "mensagem esperada" in str(exc_info.value)
```

## Mockando Dependências

```python
from unittest.mock import Mock, patch

def test_com_mock():
    """Testa com mock"""
    mock_obj = Mock()
    mock_obj.metodo.return_value = "mocked"
    
    result = funcao_que_usa_mock(mock_obj)
    
    assert result == "mocked"
    mock_obj.metodo.assert_called_once()


@patch('modulo.funcao_externa')
def test_com_patch(mock_funcao):
    """Testa com patch"""
    mock_funcao.return_value = 42
    
    result = funcao_que_chama_externa()
    
    assert result == 42
```

## Testando DataFrames

```python
import pandas as pd
from pandas.testing import assert_frame_equal

def test_dataframe():
    """Testa operação com DataFrame"""
    df_input = pd.DataFrame({'A': [1, 2, 3]})
    df_expected = pd.DataFrame({'A': [2, 4, 6]})
    
    df_result = funcao_que_processa_df(df_input)
    
    assert_frame_equal(df_result, df_expected)
```

## Testando Gráficos Plotly

```python
import plotly.graph_objs as go

def test_grafico():
    """Testa criação de gráfico"""
    fig = criar_grafico(data)
    
    # Verifica tipo
    assert isinstance(fig, go.Figure)
    
    # Verifica traces
    assert len(fig.data) > 0
    
    # Verifica título
    assert 'Título' in fig.layout.title.text
```

## Estrutura de Arquivo de Teste

```python
"""
Testes para modulo.py

Este arquivo testa todas as funções do módulo modulo.py
"""
import pytest
from modulo import funcao1, funcao2


class TestFuncao1:
    """Testes para funcao1"""
    
    def test_caso_basico(self):
        """Testa caso básico"""
        pass
    
    def test_caso_edge(self):
        """Testa caso extremo"""
        pass


class TestFuncao2:
    """Testes para funcao2"""
    
    def test_caso_basico(self):
        """Testa caso básico"""
        pass
```

## Boas Práticas

### 1. Nomes Descritivos
```python
# ❌ Ruim
def test_1():
    pass

# ✅ Bom
def test_parse_xml_with_empty_driver_list_returns_empty_dataframe():
    pass
```

### 2. Um Assert por Teste (quando possível)
```python
# ❌ Ruim
def test_funcao():
    assert funcao(1) == 2
    assert funcao(2) == 4
    assert funcao(3) == 6

# ✅ Bom
@pytest.mark.parametrize("input,expected", [(1, 2), (2, 4), (3, 6)])
def test_funcao(input, expected):
    assert funcao(input) == expected
```

### 3. Arrange-Act-Assert
```python
def test_exemplo():
    # Arrange: Preparar dados
    data = criar_dados_teste()
    
    # Act: Executar função
    result = processar(data)
    
    # Assert: Verificar resultado
    assert result == esperado
```

### 4. Testes Independentes
```python
# ❌ Ruim - testes dependentes
class TestDependente:
    def test_1(self):
        self.data = [1, 2, 3]
    
    def test_2(self):
        # Depende de test_1
        assert len(self.data) == 3

# ✅ Bom - testes independentes
class TestIndependente:
    @pytest.fixture
    def data(self):
        return [1, 2, 3]
    
    def test_1(self, data):
        assert data[0] == 1
    
    def test_2(self, data):
        assert len(data) == 3
```

### 5. Docstrings
```python
def test_parse_xml_with_invalid_format():
    """
    Testa se parse_xml levanta ParseError quando XML é inválido.
    
    Given: Um XML malformado
    When: parse_xml é chamado
    Then: ParseError deve ser levantada
    """
    pass
```

## Comandos Úteis

```bash
# Executar teste específico
pytest tests/unit/data/test_parsers.py::TestParseXmlScores::test_parse_valid_xml

# Executar com verbose
pytest -v

# Parar no primeiro erro
pytest -x

# Mostrar print statements
pytest -s

# Executar apenas testes marcados
pytest -m "slow"

# Executar testes em paralelo
pytest -n auto  # requer pytest-xdist

# Gerar relatório JUnit
pytest --junitxml=report.xml
```

## Marcadores Personalizados

```python
# Definir em pytest.ini
[pytest]
markers =
    slow: marca testes lentos
    integration: marca testes de integração
    unit: marca testes unitários

# Usar nos testes
@pytest.mark.slow
def test_operacao_lenta():
    pass

@pytest.mark.integration
def test_integracao():
    pass
```

## Exemplo Completo

```python
"""
Testes para data/parsers.py
"""
import pytest
import pandas as pd
from data.parsers import parse_xml_scores


class TestParseXmlScores:
    """Testes para função parse_xml_scores"""
    
    @pytest.fixture
    def valid_xml(self):
        """XML válido para testes"""
        return """<?xml version="1.0"?>
        <RaceResults>
            <Driver>
                <Name>Test Driver</Name>
            </Driver>
        </RaceResults>"""
    
    def test_parse_valid_xml_returns_dataframe(self, valid_xml):
        """
        Testa se XML válido retorna DataFrame.
        
        Given: Um XML válido
        When: parse_xml_scores é chamado
        Then: Deve retornar DataFrame não vazio
        """
        # Arrange
        expected_columns = ['Driver', 'Lap', 'Position']
        
        # Act
        df, race_info, incidents = parse_xml_scores(valid_xml)
        
        # Assert
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert all(col in df.columns for col in expected_columns)
    
    def test_parse_empty_xml_returns_empty_dataframe(self):
        """Testa se XML vazio retorna DataFrame vazio"""
        # Arrange
        empty_xml = """<?xml version="1.0"?><RaceResults></RaceResults>"""
        
        # Act
        df, _, _ = parse_xml_scores(empty_xml)
        
        # Assert
        assert df.empty
    
    @pytest.mark.parametrize("invalid_xml", [
        "not xml",
        "<?xml version='1.0'?><unclosed>",
        "",
    ])
    def test_parse_invalid_xml_raises_error(self, invalid_xml):
        """Testa se XML inválido levanta erro"""
        with pytest.raises(Exception):
            parse_xml_scores(invalid_xml)
```

## Checklist para Novos Testes

- [ ] Nome descritivo do teste
- [ ] Docstring explicando o teste
- [ ] Arrange-Act-Assert structure
- [ ] Teste independente (não depende de outros)
- [ ] Usa fixtures quando apropriado
- [ ] Testa casos normais
- [ ] Testa casos extremos (edge cases)
- [ ] Testa tratamento de erros
- [ ] Assertions claras
- [ ] Executa rapidamente (< 1s se possível)

## Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
