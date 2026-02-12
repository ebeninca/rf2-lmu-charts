# ✅ Checklist de Deploy - Segurança

## Antes do Deploy

### 1. Testes de Segurança
- [ ] Executar `python test_security.py`
- [ ] Verificar que 9/9 testes passam
- [ ] Revisar logs de segurança em `logs/security.log`

### 2. Dependências
- [ ] Verificar `requirements.txt` atualizado
- [ ] Confirmar versões de segurança:
  - [ ] Flask-Limiter==3.5.0
  - [ ] defusedxml==0.7.1
  - [ ] Werkzeug==3.0.1

### 3. Configuração
- [ ] Arquivo `gunicorn.conf.py` presente
- [ ] Arquivo `security.py` presente
- [ ] Arquivo `data/parsers_secure.py` presente
- [ ] Arquivo `.env.example` presente (NÃO commitar .env real)

### 4. Docker
- [ ] Dockerfile usa usuário não-root (appuser)
- [ ] Dockerfile copia `gunicorn.conf.py`
- [ ] Dockerfile copia `security.py`
- [ ] Dockerfile cria diretório `logs/`

### 5. Variáveis de Ambiente
- [ ] Criar arquivo `.env` (se necessário)
- [ ] Definir `SECRET_KEY` aleatório
- [ ] Definir `FLASK_SECRET_KEY` aleatório
- [ ] Confirmar que `.env` está no `.gitignore`

### 6. Arquivos Sensíveis
- [ ] `.env` no `.gitignore`
- [ ] `logs/` no `.gitignore`
- [ ] `*.log` no `.gitignore`
- [ ] Nenhum secret commitado

---

## Durante o Deploy

### 1. Build Docker
```bash
docker build -t rf2-lmu-charts .
```
- [ ] Build sem erros
- [ ] Imagem criada com sucesso

### 2. Teste Local
```bash
docker run -p 7860:7860 rf2-lmu-charts
```
- [ ] Container inicia sem erros
- [ ] Aplicação responde em http://localhost:7860
- [ ] Upload de arquivo funciona
- [ ] Rate limiting ativo

### 3. Verificar Logs
```bash
docker logs <container_id>
```
- [ ] Gunicorn iniciado com configuração correta
- [ ] Número de workers correto (max 4)
- [ ] Timeout configurado (30s)

---

## Após o Deploy

### 1. Testes de Segurança em Produção

#### Teste 1: Upload Normal
- [ ] Upload de arquivo .xml válido (< 20MB) funciona
- [ ] Dados são processados corretamente

#### Teste 2: Upload Inválido - Extensão
- [ ] Upload de arquivo .exe é rejeitado
- [ ] Mensagem de erro apropriada

#### Teste 3: Upload Inválido - Tamanho
- [ ] Upload de arquivo > 20MB é rejeitado
- [ ] Mensagem de erro apropriada

#### Teste 4: Rate Limiting
```bash
# Fazer 60 requests em 1 minuto
for i in {1..60}; do curl https://seu-app.com/; done
```
- [ ] Após 50 requests, recebe erro 429 (Too Many Requests)

#### Teste 5: Security Headers
```bash
curl -I https://seu-app.com/
```
- [ ] Header `Content-Security-Policy` presente
- [ ] Header `X-Frame-Options: DENY` presente
- [ ] Header `X-Content-Type-Options: nosniff` presente
- [ ] Header `X-XSS-Protection` presente

#### Teste 6: XXE Attack
- [ ] Upload de XML com entidade externa é rejeitado
- [ ] Evento registrado em logs

### 2. Monitoramento

#### Logs de Segurança
- [ ] Verificar `logs/security.log` existe
- [ ] Configurar rotação de logs (10MB, 5 backups)
- [ ] Monitorar eventos suspeitos

#### Métricas
- [ ] Monitorar taxa de requests por IP
- [ ] Monitorar uploads rejeitados
- [ ] Monitorar timeouts

### 3. Alertas (Opcional)
- [ ] Configurar alerta para uploads > 20MB
- [ ] Configurar alerta para rate limiting atingido
- [ ] Configurar alerta para tentativas de XXE

---

## Manutenção Contínua

### Semanal
- [ ] Revisar `logs/security.log`
- [ ] Verificar IPs com muitos requests rejeitados
- [ ] Verificar tentativas de upload malicioso

### Mensal
- [ ] Atualizar dependências de segurança
- [ ] Executar `python test_security.py`
- [ ] Revisar configuração de rate limiting

### Trimestral
- [ ] Audit de segurança completo
- [ ] Revisar e atualizar SECURITY.md
- [ ] Testar cenários de ataque

---

## Troubleshooting

### Problema: Rate limiting muito restritivo
**Solução**: Ajustar limites em `app.py`:
```python
default_limits=["500 per day", "100 per hour"]
```

### Problema: Uploads legítimos sendo rejeitados
**Solução**: Verificar logs em `logs/security.log` para identificar causa

### Problema: Timeout em arquivos grandes
**Solução**: Ajustar timeout em `security.py`:
```python
with time_limit(20):  # Aumentar para 20s
```

### Problema: Container não inicia
**Solução**: Verificar permissões do usuário appuser no Dockerfile

---

## Contatos de Emergência

### Segurança
- Revisar: `SECURITY.md`
- Implementação: `SECURITY_IMPLEMENTATION.md`
- Testes: `python test_security.py`

### Suporte
- Issues: GitHub Issues
- Logs: `logs/security.log`

---

## ✅ Checklist Final

Antes de marcar como completo:
- [ ] Todos os testes de segurança passando
- [ ] Aplicação funcionando em produção
- [ ] Logs de segurança sendo gerados
- [ ] Rate limiting ativo
- [ ] Security headers presentes
- [ ] Documentação atualizada
- [ ] Equipe treinada em procedimentos de segurança

---

## 🎉 Deploy Completo

Data: _______________
Responsável: _______________
Versão: _______________

Assinatura: _______________
