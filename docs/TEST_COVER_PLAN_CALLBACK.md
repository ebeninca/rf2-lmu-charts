# Plano de Cobertura de Testes - callbacks.py

## Objetivo
Atingir 60% de cobertura de testes unitários no arquivo `presentation/callbacks.py` através de testes abrangentes e estruturados.

## Análise Atual

### Estado Atual dos Testes
- **Arquivo de testes existente**: `tests/unit/test_callbacks.py`
- **Cobertura atual**: ~25-30% (estimado)
- **Framework**: pytest
- **Estrutura**: Classes de teste organizadas por funcionalidade

### Funções Não Testadas (Principais Gaps)
1. **`register_callbacks()`** - Função principal de registro
2. **`render_tab_content()`** - Lógica complexa de renderização de abas
3. **`render_laptimes_content()`** - Renderização de conteúdo de tempos de volta
4. **`update_race_info()`** - Formatação completa de informações da corrida
5. **`render_events_content()`** - Renderização de eventos/incidentes
6. **`_create_laptimes_table()`** - Criação de tabela de tempos de volta
7. **Callbacks de storage** - Funções de armazenamento de estado

## Plano de Implementação

### Fase 1: Testes de Funções Auxiliares (1-2 horas)
**Prioridade**: Alta
**Estimativa**: 1-2 horas
**Cobertura esperada**: +15%

#### 1.1 Testes para `validate_file_size()`
```python
class TestValidateFileSize:
    def test_valid_small_file(self):
        """Testa arquivo XML dentro do limite de 50MB"""
        
    def test_file_at_limit(self):
        """Testa arquivo XML no limite exato de 50MB"""
        
    def test_file_over_limit(self):
        """Testa arquivo XML acima do limite de 50MB"""
        
    def test_zero_size_file(self):
        """Testa arquivo XML vazio"""
```

#### 1.2 Testes para `_create_laptimes_table()`
```python
class TestCreateLaptimesTable:
    def test_empty_dataframe(self):
        """Testa DataFrame vazio de tempos de volta"""
        
    def test_no_lap_data(self):
        """Testa sem dados de voltas do XML"""
        
    def test_valid_laptimes_data(self):
        """Testa com dados válidos de tempos de volta do XML"""
        
    def test_finishing_order_calculation(self):
        """Testa cálculo de ordem de chegada baseado em XML"""
```

### Fase 2: Testes de Callbacks de Storage (1 hora)
**Prioridade**: Média
**Estimativa**: 1 hora
**Cobertura esperada**: +10%

#### 2.1 Testes de Storage de Abas
```python
class TestStorageCallbacks:
    def test_store_selected_lap(self):
        """Testa armazenamento de volta selecionada"""
        
    def test_store_laptimes_tab(self):
        """Testa armazenamento de aba de tempos de volta"""
        
    def test_restore_laptimes_tab(self):
        """Testa restauração de aba de tempos de volta"""
```

### Fase 3: Testes de Renderização de Conteúdo (2-3 horas)
**Prioridade**: Alta
**Estimativa**: 2-3 horas
**Cobertura esperada**: +20%

#### 3.1 Testes para `render_events_content()`
```python
class TestRenderEventsContent:
    def test_chat_tab_with_messages(self):
        """Testa aba de chat com mensagens do XML"""
        
    def test_chat_tab_empty(self):
        """Testa aba de chat vazia (sem mensagens no XML)"""
        
    def test_incidents_tab_with_data(self):
        """Testa aba de incidentes com dados do XML"""
        
    def test_incidents_tab_empty(self):
        """Testa aba de incidentes vazia (sem incidentes no XML)"""
```

#### 3.2 Testes para `render_laptimes_content()`
```python
class TestRenderLaptimesContent:
    def test_charts_tab_rendering(self):
        """Testa renderização de aba de gráficos de tempos de volta"""
        
    def test_table_tab_rendering(self):
        """Testa renderização de aba de tabela de tempos de volta"""
        
    def test_empty_data_handling(self):
        """Testa tratamento de dados vazios do XML"""
```

### Fase 4: Testes de `render_tab_content()` (3-4 horas)
**Prioridade**: Crítica
**Estimativa**: 3-4 horas
**Cobertura esperada**: +25%

#### 4.1 Testes de Lógica de Filtros
```python
class TestRenderTabContentFilters:
    def test_standings_tab_class_filter_only(self):
        """Testa filtro de classe apenas para standings"""
        
    def test_driver_filter_application(self):
        """Testa aplicação de filtro de driver dos dados XML"""
        
    def test_class_filter_application(self):
        """Testa aplicação de filtro de classe dos dados XML"""
        
    def test_multiple_filters_combination(self):
        """Testa combinação de múltiplos filtros nos dados XML"""
        
    def test_prevent_update_for_standings_non_class_filters(self):
        """Testa prevenção de update para filtros não-classe em standings"""
```

#### 4.2 Testes de Renderização por Aba
```python
class TestRenderTabContentTabs:
    def test_standings_tab_rendering(self):
        """Testa renderização completa da aba standings com dados XML"""
        
    def test_position_tab_rendering(self):
        """Testa renderização da aba position com gráficos de dados XML"""
        
    def test_gap_tab_rendering(self):
        """Testa renderização da aba gap com gráficos de dados XML"""
        
    def test_laptimes_tab_rendering(self):
        """Testa renderização da aba laptimes com dados XML"""
        
    def test_fuel_tab_rendering(self):
        """Testa renderização da aba fuel com gráficos de dados XML"""
        
    def test_tires_tab_rendering(self):
        """Testa renderização da aba tires com gráficos de dados XML"""
```

### Fase 5: Testes de `update_race_info()` (1-2 horas)
**Prioridade**: Alta
**Estimativa**: 1-2 horas
**Cobertura esperada**: +10%

```python
class TestUpdateRaceInfo:
    def test_empty_race_info(self):
        """Testa race_info vazio do XML"""
        
    def test_duration_formatting_hours_minutes(self):
        """Testa formatação de duração em horas/minutos do XML"""
        
    def test_duration_formatting_laps_only(self):
        """Testa formatação de duração em voltas do XML"""
        
    def test_server_name_display(self):
        """Testa exibição de nome do servidor do XML"""
        
    def test_track_info_with_flag(self):
        """Testa informações de pista com bandeira do XML"""
```

### Fase 6: Testes de Cenários de Falha e Edge Cases (1-2 horas)
**Prioridade**: Média
**Estimativa**: 1-2 horas
**Cobertura esperada**: +10%

#### 6.1 Testes de Falha Simples
```python
class TestErrorScenariosAndEdgeCases:
    def test_empty_dataframe_all_tabs(self):
        """Testa DataFrame vazio em todas as abas"""
        
    def test_malformed_xml_data_handling(self):
        """Testa tratamento de dados XML malformados"""
        
    def test_none_values_in_xml_data(self):
        """Testa valores None nos dados XML"""
        
    def test_invalid_tab_names(self):
        """Testa nomes de abas inválidos"""
        
    def test_missing_xml_fields(self):
        """Testa campos faltando no XML"""
        
    def test_invalid_xml_numeric_values(self):
        """Testa valores numéricos inválidos no XML"""
        
    def test_xml_file_not_found(self):
        """Testa arquivo XML não encontrado"""
        
    def test_corrupted_xml_file(self):
        """Testa arquivo XML corrompido"""
```

## Fixtures Necessários

### Novas Fixtures a Adicionar em `conftest.py`

```python
@pytest.fixture
def sample_xml_malformed():
    """XML malformado para testes de erro"""
    return '''<?xml version="1.0" encoding="utf-8"?>
    <RaceResults>
        <Driver Name="Driver1">
            <IncompleteTag>
        </Driver>
    </RaceResults>'''

@pytest.fixture
def sample_xml_missing_fields():
    """XML com campos faltando"""
    return {
        'track': None,
        'course': 'Main Course',
        'date': '2024-01-15 14:30:00',
        'laps': '10',
        'time': None,
        'server': 'Test Server'
    }

@pytest.fixture
def sample_xml_corrupted():
    """XML corrompido"""
    return '''<CorruptedData>
        <InvalidEncoding>���</InvalidEncoding>
        <BrokenStructure><<>>
    </CorruptedData>'''
```

## Configuração de Mocking

### Mocks Necessários
```python
# Em test_callbacks.py
@pytest.fixture
def mock_callback_context():
    """Mock do contexto de callback"""
    with patch('dash.callback_context') as mock_ctx:
        mock_ctx.triggered = [{'prop_id': 'tabs.value'}]
        yield mock_ctx
```

## Estrutura de Diretórios de Teste

```
tests/
├── unit/
│   ├── test_callbacks.py (expandido)
│   ├── conftest.py (com novas fixtures)
│   └── test_data/
│       ├── valid_race.xml
│       └── large_dataset.csv
```

## Execução do Plano

### Comandos de Teste
```bash
# Executar todos os testes de callbacks
pytest tests/unit/test_callbacks.py -v

# Executar com cobertura
pytest tests/unit/test_callbacks.py --cov=presentation.callbacks --cov-report=html --cov-report=term-missing

# Executar testes específicos por fase
pytest tests/unit/test_callbacks.py::TestValidateFileSize -v
pytest tests/unit/test_callbacks.py::TestRenderTabContent -v
```

### Monitoramento de Progresso
```bash
# Ver cobertura atual
coverage report --include="*/presentation/callbacks.py"

# Gerar relatório HTML
coverage html --include="*/presentation/callbacks.py"
```

## Critérios de Sucesso

### Métricas de Cobertura
- **Linhas cobertas**: Mínimo 60%
- **Branches cobertos**: Mínimo 50%
- **Funções cobertas**: 100% das funções públicas
- **Exceções testadas**: Todas as exceções levantadas

### Qualidade dos Testes
- **Assert por teste**: Mínimo 2 asserts
- **Tempo de execução**: Máximo 5 segundos por teste
- **Independência**: Cada teste deve ser independente
- **Repetibilidade**: Testes devem ser determinísticos

## Manutenção e Evolução

### Revisão Semanal
- Monitorar cobertura após mudanças no código
- Adicionar testes para novas funcionalidades
- Refatorar testes antigos se necessário

### Integração Contínua
- Adicionar verificação de cobertura no CI/CD
- Falhar build se cobertura < 60%
- Gerar alertas para queda de cobertura

## Próximos Passos

1. **Semana 1**: Implementar Fases 1 e 2 (funções auxiliares e storage)
2. **Semana 2**: Implementar Fases 3 e 4 (renderização de conteúdo)
3. **Semana 3**: Implementar Fases 5 e 6 (race info e edge cases)
4. **Semana 4**: Revisão, otimização e documentação final

### Estimativa Total: 6-8 horas de desenvolvimento
### Cobertura Final Esperada: 60-65%