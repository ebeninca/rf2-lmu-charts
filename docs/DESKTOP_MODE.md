# Modo Desktop - Documentação

## Visão Geral

O modo Desktop permite que a aplicação trabalhe com pastas contendo múltiplos arquivos XML, facilitando a análise de várias corridas sem precisar fazer upload individual de cada arquivo.

## Configuração

Configure o modo de operação através da variável de ambiente `APP_MODE` no arquivo `.env`:

```bash
# Modo Desktop - permite selecionar pastas com XMLs
APP_MODE=Desktop

# Modo Web (padrão) - permite upload de arquivo único
APP_MODE=Web
```

Se `APP_MODE` não estiver definido ou estiver vazio, o modo Web será usado por padrão.

## Funcionalidades

### Modo Web (Padrão)
- Upload de arquivo XML único
- Drag and drop de arquivo individual
- Processamento imediato após upload

### Modo Desktop
- Upload de pasta contendo múltiplos arquivos XML
- Lista interativa de arquivos disponíveis
- Carregamento instantâneo ao clicar em um arquivo da lista
- Suporte para arquivos `.xml` e `.xmlx`
- Filtragem automática de arquivos não-XML

## Como Usar - Modo Desktop

1. Configure `APP_MODE=Desktop` no arquivo `.env`
2. Inicie a aplicação
3. Selecione múltiplos arquivos XML de uma pasta:
   - **Opção 1 (Arrastar)**: Abra a pasta no explorador, selecione todos os XMLs (Ctrl+A / Cmd+A) e arraste para a área de upload
   - **Opção 2 (Clicar)**: Clique em "Select Multiple XML Files", navegue até a pasta, selecione todos (Ctrl+A / Cmd+A) e clique "Abrir"
4. Uma lista de arquivos XML será exibida
5. Clique em qualquer arquivo da lista para carregar seus dados instantaneamente
6. Os gráficos e tabelas serão atualizados automaticamente

**Nota Importante**: Navegadores web não permitem seleção direta de pastas por razões de segurança. Por isso, você seleciona múltiplos arquivos de uma pasta usando Ctrl+A (Windows/Linux) ou Cmd+A (macOS).

## Comportamento

### Modo Desktop
- O componente de upload aceita múltiplos arquivos (`multiple=True`)
- Apenas arquivos com extensão `.xml` ou `.xmlx` são listados
- Arquivos de outros tipos são ignorados silenciosamente
- Ao clicar em um arquivo, os dados são carregados sem necessidade de novo upload

### Modo Web
- O componente de upload aceita apenas um arquivo (`multiple=False`)
- Upload tradicional de arquivo único
- Processamento imediato após seleção

## Validações

Ambos os modos mantêm as mesmas validações de segurança:
- Tamanho máximo de arquivo: 20MB
- Validação de estrutura XML
- Proteção contra XXE attacks
- Validação de tipo MIME
- Rate limiting (apenas modo Web)

## Testes

Os testes unitários cobrem:
- ✅ Layout correto para cada modo
- ✅ Upload de pasta com arquivos XML válidos
- ✅ Upload de pasta sem arquivos XML
- ✅ Upload de pasta com tipos mistos de arquivo
- ✅ Carregamento de arquivo selecionado
- ✅ Tratamento de erros (arquivo inválido, muito grande, etc.)
- ✅ Comportamento quando modo não está configurado
- ✅ Isolamento entre modos (Desktop não afeta Web e vice-versa)

Execute os testes:
```bash
pytest tests/unit/test_desktop_mode.py -v
```

## Arquitetura

### Componentes Modificados

1. **presentation/layouts.py**
   - Detecta `APP_MODE` via `os.getenv()`
   - Ajusta texto do upload ("Select Folder" vs "Select XML File")
   - Configura `multiple=True` para Desktop
   - Adiciona `file-list-container` e `folder-files-store`

2. **presentation/callbacks.py**
   - `handle_folder_upload()`: Processa pasta e lista arquivos XML
   - `load_selected_file()`: Carrega arquivo selecionado da lista
   - `update_data()`: Modificado para ignorar Desktop mode

### Fluxo de Dados - Modo Desktop

```
1. Usuário seleciona pasta
   ↓
2. handle_folder_upload() filtra arquivos XML
   ↓
3. Lista de arquivos é exibida
   ↓
4. Usuário clica em arquivo
   ↓
5. load_selected_file() carrega e valida
   ↓
6. Dados são parseados e armazenados
   ↓
7. Interface é atualizada automaticamente
```

## Limitações

- Modo Desktop não suporta rate limiting (assumindo uso local)
- Todos os arquivos da pasta devem ser carregados na memória para listagem
- Limite de 20MB por arquivo individual mantido

## Compatibilidade

- ✅ Linux
- ✅ Windows
- ✅ macOS
- ✅ Docker (configurar via variável de ambiente)
- ✅ PyInstaller (standalone executables)
