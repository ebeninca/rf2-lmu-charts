# Testes Unitários - rFactor2-lmu-graphs

## Estrutura de Testes

```
tests/
├── conftest.py                    # Fixtures compartilhadas
├── test_data/                     # Dados de teste
│   └── valid_race.xml
├── unit/                          # Testes unitários
│   ├── data/
│   │   ├── test_parsers.py       # 25+ testes
│   │   └── test_track_flags.py   # 10+ testes
│   ├── business/
│   │   └── test_analytics.py     # 40+ testes
│   ├── presentation/
│   │   ├── test_callbacks.py     # 30+ testes
│   │   ├── test_components.py    # 15+ testes
│   │   └── test_layouts.py       # 20+ testes
│   └── test_app.py               # 15+ testes
└── integration/
    └── test_app_integration.py   # 20+ testes
```

## Instalação

```bash
pip install -r requirements-dev.txt
```

## Executar Testes

### Todos os testes
```bash
pytest
```

### Com cobertura
```bash
pytest --cov
```

### Apenas testes unitários
```bash
pytest tests/unit/
```

### Apenas testes de integração
```bash
pytest tests/integration/
```

### Teste específico
```bash
pytest tests/unit/data/test_parsers.py
```

### Com verbose
```bash
pytest -v
```

### Parar no primeiro erro
```bash
pytest -x
```

## Cobertura

Gerar relatório HTML de cobertura:
```bash
pytest --cov --cov-report=html
```

Abrir relatório:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Estrutura dos Testes

### Fixtures (conftest.py)
- `sample_xml`: XML de corrida válido
- `empty_xml`: XML vazio
- `invalid_xml`: XML malformado
- `sample_dataframe`: DataFrame com dados de corrida
- `sample_race_info`: Informações da corrida
- `sample_incidents`: Incidentes (chat, incidents, penalties)

### Testes por Módulo

#### data/parsers.py (25+ testes)
- ✅ Parsing de XML válido
- ✅ Tratamento de XML vazio/inválido
- ✅ Extração de race info
- ✅ Extração de chat/incidents/penalties
- ✅ Cálculo de gaps
- ✅ Detecção de pit stops
- ✅ Parsing de aids
- ✅ Extração de compostos de pneus
- ✅ Validação de valores numéricos

#### data/track_flags.py (10+ testes)
- ✅ Circuitos conhecidos
- ✅ Case insensitive
- ✅ Circuitos desconhecidos
- ✅ Match parcial
- ✅ Validação de mapeamentos

#### business/analytics.py (40+ testes)
- ✅ Todos os 15 gráficos testados
- ✅ DataFrame vazio
- ✅ Filtros aplicados
- ✅ Formatação de dados
- ✅ Cálculos específicos

#### presentation/components.py (15+ testes)
- ✅ Criação de tabela de standings
- ✅ Cálculo de posições
- ✅ Formatação de gaps
- ✅ Contagem de pit stops
- ✅ Cores por classe

#### presentation/layouts.py (20+ testes)
- ✅ Layout principal
- ✅ Seção de filtros
- ✅ Seção de tabs
- ✅ Componentes presentes

#### presentation/callbacks.py (30+ testes)
- ✅ Upload de arquivo
- ✅ Atualização de filtros
- ✅ Renderização de tabs
- ✅ Exibição de race info
- ✅ Eventos (chat, incidents, penalties)

#### app.py (15+ testes)
- ✅ Inicialização do app
- ✅ Carregamento de dados
- ✅ Registro de callbacks
- ✅ Configuração

#### integration/ (20+ testes)
- ✅ Fluxo completo parse → visualização
- ✅ Aplicação de filtros
- ✅ Consistência de dados
- ✅ Tratamento de erros

## Métricas de Qualidade

### Cobertura Esperada
- **Global**: ≥ 80%
- **data/parsers.py**: ≥ 90%
- **business/analytics.py**: ≥ 85%
- **presentation/**: ≥ 75%

### Total de Testes
- **Unitários**: ~155 testes
- **Integração**: ~20 testes
- **Total**: ~175 testes

## Boas Práticas Implementadas

1. ✅ **Arrange-Act-Assert**: Estrutura clara em todos os testes
2. ✅ **Fixtures**: Reutilização de dados de teste
3. ✅ **Parametrização**: Múltiplos casos com `@pytest.mark.parametrize`
4. ✅ **Isolamento**: Testes independentes
5. ✅ **Nomes Descritivos**: `test_parse_xml_with_invalid_lap_time_returns_zero`
6. ✅ **Cobertura**: Casos normais, edge cases e erros
7. ✅ **Documentação**: Docstrings em todas as classes de teste

## CI/CD

Para integrar com GitHub Actions, adicione `.github/workflows/tests.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Troubleshooting

### Erro de importação
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Testes lentos
```bash
pytest -n auto  # Execução paralela (requer pytest-xdist)
```

### Debug de teste específico
```bash
pytest tests/unit/data/test_parsers.py::TestParseXmlScores::test_parse_valid_xml -v -s
```

## Próximos Passos

1. ✅ Implementar testes E2E com Selenium (opcional)
2. ✅ Adicionar testes de performance
3. ✅ Integrar com codecov.io
4. ✅ Adicionar badges no README principal
5. ✅ Configurar pre-commit hooks

## Contribuindo

Ao adicionar novos recursos:
1. Escreva testes primeiro (TDD)
2. Mantenha cobertura ≥ 80%
3. Execute `pytest` antes de commit
4. Documente casos edge

## Contato

Para dúvidas sobre os testes, abra uma issue no repositório.
