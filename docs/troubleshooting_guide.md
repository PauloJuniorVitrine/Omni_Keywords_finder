# 🛠️ **GUIA DE TROUBLESHOOTING: SISTEMA DE CREDENCIAIS**

## 📋 **VISÃO GERAL**

Este guia fornece soluções para os problemas mais comuns encontrados no sistema de credenciais do Omni Keywords Finder. Cada seção inclui sintomas, causas prováveis e soluções passo a passo.

---

## 🚨 **PROBLEMAS CRÍTICOS**

### **1. Sistema de Criptografia Falhou**

#### **Sintomas**
- Erro: "Falha na criptografia"
- Credenciais não são salvas
- Sistema retorna erro 500
- Logs mostram "EncryptionError"

#### **Causas Prováveis**
1. Chave mestra não configurada
2. Chave mestra inválida
3. Permissões de arquivo incorretas
4. Biblioteca de criptografia corrompida

#### **Soluções**

**Passo 1: Verificar Configuração da Chave Mestra**
```bash
# Verificar se a variável está definida
echo $CREDENTIAL_MASTER_KEY

# Se não estiver definida, configurar:
export CREDENTIAL_MASTER_KEY="sua-chave-aqui"
```

**Passo 2: Validar Formato da Chave**
```python
import base64
import os

# Verificar se a chave tem 256 bits (32 bytes)
master_key = os.getenv('CREDENTIAL_MASTER_KEY')
if master_key:
    key_bytes = base64.b64decode(master_key)
    print(f"Tamanho da chave: {len(key_bytes)} bytes")
    if len(key_bytes) != 32:
        print("ERRO: Chave deve ter 32 bytes (256 bits)")
```

**Passo 3: Gerar Nova Chave (se necessário)**
```python
import secrets
import base64

# Gerar nova chave mestra
new_key = secrets.token_bytes(32)
encoded_key = base64.b64encode(new_key).decode('utf-8')
print(f"Nova chave: {encoded_key}")
```

**Passo 4: Verificar Permissões**
```bash
# Verificar permissões do diretório de configuração
ls -la config/
chmod 600 config/credentials_config.json
chown www-data:www-data config/credentials_config.json
```

### **2. Falha na Validação de Credenciais**

#### **Sintomas**
- Todas as validações falham
- Erro: "Rate limit excedido"
- Sistema não consegue conectar com APIs
- Timeout em todas as validações

#### **Causas Prováveis**
1. Rate limiting ativo
2. Problemas de conectividade
3. APIs externas indisponíveis
4. Configuração de proxy incorreta

#### **Soluções**

**Passo 1: Verificar Rate Limiting**
```bash
# Verificar status do rate limiter
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/status

# Resetar rate limit (se necessário)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/reset/openai
```

**Passo 2: Testar Conectividade**
```bash
# Testar conectividade com APIs externas
curl -I https://api.openai.com/v1/models
curl -I https://api.deepseek.com/v1/models
curl -I https://api.anthropic.com/v1/messages
```

**Passo 3: Verificar Configuração de Rede**
```bash
# Verificar proxy (se aplicável)
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Testar DNS
nslookup api.openai.com
nslookup api.deepseek.com
```

**Passo 4: Verificar Logs de Erro**
```bash
# Verificar logs do sistema
tail -f logs/credential_errors.log

# Verificar logs de auditoria
tail -f logs/audit_credentials.log
```

---

## ⚠️ **PROBLEMAS DE CONFIGURAÇÃO**

### **3. Credenciais Não São Salvas**

#### **Sintomas**
- Dados não persistem após salvar
- Interface mostra "Salvo" mas dados desaparecem
- Erro: "Erro ao salvar configuração"
- Backup não é criado

#### **Causas Prováveis**
1. Permissões de escrita insuficientes
2. Espaço em disco insuficiente
3. Arquivo de configuração corrompido
4. Problemas de validação

#### **Soluções**

**Passo 1: Verificar Permissões**
```bash
# Verificar permissões do diretório
ls -la config/
ls -la config/credentials_config.json

# Corrigir permissões
chmod 755 config/
chmod 644 config/credentials_config.json
chown www-data:www-data config/credentials_config.json
```

**Passo 2: Verificar Espaço em Disco**
```bash
# Verificar espaço disponível
df -h

# Verificar tamanho do arquivo de configuração
ls -lh config/credentials_config.json

# Limpar arquivos temporários se necessário
find /tmp -name "*.tmp" -mtime +1 -delete
```

**Passo 3: Validar Arquivo de Configuração**
```python
import json

# Verificar se o arquivo é JSON válido
try:
    with open('config/credentials_config.json', 'r') as f:
        config = json.load(f)
    print("Arquivo de configuração válido")
except json.JSONDecodeError as e:
    print(f"Arquivo corrompido: {e}")
    # Restaurar backup se disponível
```

**Passo 4: Verificar Logs de Erro**
```bash
# Verificar logs específicos de salvamento
grep "save_config" logs/credential_errors.log
grep "permission" logs/credential_errors.log
```

### **4. Validação de Credenciais Falha**

#### **Sintomas**
- Credenciais válidas são rejeitadas
- Erro: "Credencial inválida"
- Validação demora muito tempo
- Falsos positivos/negativos

#### **Causas Prováveis**
1. Formato de credencial incorreto
2. Credencial expirada
3. Limites de API atingidos
4. Problemas de validação específicos do provedor

#### **Soluções**

**Passo 1: Verificar Formato da Credencial**
```python
# Validar formato OpenAI
def validate_openai_key(key):
    return key.startswith('sk-') and len(key) >= 20

# Validar formato DeepSeek
def validate_deepseek_key(key):
    return key.startswith('sk-') and len(key) >= 20

# Validar formato Claude
def validate_claude_key(key):
    return key.startswith('sk-ant-') and len(key) >= 25
```

**Passo 2: Testar Credencial Manualmente**
```bash
# Testar OpenAI
curl -H "Authorization: Bearer sk-..." \
  https://api.openai.com/v1/models

# Testar DeepSeek
curl -H "Authorization: Bearer sk-..." \
  https://api.deepseek.com/v1/models

# Testar Claude
curl -H "Authorization: Bearer sk-ant-..." \
  https://api.anthropic.com/v1/messages
```

**Passo 3: Verificar Limites de API**
```bash
# Verificar uso atual
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/status/openai

# Verificar rate limits
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/metrics
```

**Passo 4: Verificar Logs de Validação**
```bash
# Verificar logs específicos de validação
grep "validation" logs/credential_errors.log
grep "openai" logs/credential_errors.log
```

---

## 🔧 **PROBLEMAS DE PERFORMANCE**

### **5. Validação Muito Lenta**

#### **Sintomas**
- Validações demoram >30 segundos
- Interface fica travada durante validação
- Timeout em validações
- Sistema fica lento

#### **Causas Prováveis**
1. Problemas de conectividade
2. APIs externas lentas
3. Rate limiting ativo
4. Configuração de timeout inadequada

#### **Soluções**

**Passo 1: Verificar Conectividade**
```bash
# Testar latência para APIs
ping api.openai.com
ping api.deepseek.com
ping api.anthropic.com

# Testar velocidade de download
curl -w "@curl-format.txt" -o /dev/null -s https://api.openai.com/v1/models
```

**Passo 2: Ajustar Timeouts**
```python
# Configurar timeouts adequados
TIMEOUT_CONFIG = {
    'openai': 10,
    'deepseek': 10,
    'claude': 15,
    'gemini': 8
}
```

**Passo 3: Implementar Cache**
```python
# Cache de validações para reduzir latência
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def cached_validate_credential(provider, credential_hash):
    # Implementar cache de validação
    pass
```

**Passo 4: Verificar Métricas de Performance**
```bash
# Verificar métricas de performance
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/metrics

# Verificar logs de performance
grep "performance" logs/credential_errors.log
```

### **6. Sistema Consome Muita Memória**

#### **Sintomas**
- Uso de memória >1GB
- Sistema fica lento
- OOM (Out of Memory) errors
- Vazamentos de memória

#### **Causas Prováveis**
1. Cache não está sendo limpo
2. Logs muito grandes
3. Sessões não são fechadas
4. Configuração inadequada

#### **Soluções**

**Passo 1: Verificar Uso de Memória**
```bash
# Verificar uso atual de memória
free -h
ps aux | grep python

# Verificar processos específicos
ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -10
```

**Passo 2: Limpar Cache**
```python
# Limpar cache de validação
def clear_validation_cache():
    cached_validate_credential.cache_clear()

# Limpar cache de criptografia
def clear_encryption_cache():
    # Implementar limpeza de cache
    pass
```

**Passo 3: Rotacionar Logs**
```bash
# Rotacionar logs grandes
logrotate -f /etc/logrotate.d/credentials

# Limpar logs antigos
find logs/ -name "*.log" -mtime +7 -delete
```

**Passo 4: Otimizar Configuração**
```python
# Configurações de memória
MEMORY_CONFIG = {
    'max_cache_size': 100,
    'max_log_size': '100MB',
    'cleanup_interval': 3600  # 1 hora
}
```

---

## 🔒 **PROBLEMAS DE SEGURANÇA**

### **7. Acesso Não Autorizado**

#### **Sintomas**
- Tentativas de login falhadas
- Logs mostram IPs suspeitos
- Credenciais aparecem em logs
- Alertas de segurança

#### **Causas Prováveis**
1. Credenciais comprometidas
2. Ataque de força bruta
3. Configuração de segurança inadequada
4. Logs expostos

#### **Soluções**

**Passo 1: Verificar Logs de Segurança**
```bash
# Verificar tentativas de acesso
grep "unauthorized" logs/security.log
grep "failed_login" logs/audit.log

# Verificar IPs suspeitos
grep "suspicious" logs/security.log
```

**Passo 2: Implementar Bloqueio de IP**
```python
# Bloquear IPs suspeitos
def block_suspicious_ip(ip_address):
    # Implementar bloqueio
    pass

# Verificar se IP está bloqueado
def is_ip_blocked(ip_address):
    # Verificar bloqueio
    pass
```

**Passo 3: Rotacionar Credenciais**
```python
# Forçar rotação de credenciais
def force_credential_rotation(provider):
    # Implementar rotação forçada
    pass
```

**Passo 4: Verificar Configuração de Segurança**
```bash
# Verificar permissões de arquivos
find . -name "*.key" -exec ls -la {} \;
find . -name "*.pem" -exec ls -la {} \;

# Verificar variáveis de ambiente
env | grep -i key
env | grep -i secret
```

### **8. Dados Criptografados Corrompidos**

#### **Sintomas**
- Erro: "Falha na descriptografia"
- Dados não podem ser lidos
- Backup não funciona
- Sistema não inicia

#### **Causas Prováveis**
1. Chave mestra alterada
2. Dados corrompidos
3. Problemas de encoding
4. Backup inválido

#### **Soluções**

**Passo 1: Verificar Integridade dos Dados**
```python
# Verificar integridade dos dados criptografados
def verify_encrypted_data_integrity(encrypted_data):
    try:
        # Verificar formato
        if not encrypted_data.startswith('AES256_GCM:'):
            return False
        
        # Verificar tamanho mínimo
        data = base64.b64decode(encrypted_data[10:])
        if len(data) < 28:  # IV(12) + Tag(16)
            return False
        
        return True
    except Exception:
        return False
```

**Passo 2: Restaurar de Backup**
```bash
# Listar backups disponíveis
ls -la backup/credentials_*.enc

# Restaurar backup mais recente
python -c "
from app.services.credential_backup import restore_from_backup
restore_from_backup('backup/credentials_20250127_103000.enc', 'admin')
"
```

**Passo 3: Recriar Chave Mestra**
```python
# Gerar nova chave mestra
import secrets
import base64

new_key = secrets.token_bytes(32)
encoded_key = base64.b64encode(new_key).decode('utf-8')
print(f"Nova chave mestra: {encoded_key}")

# Re-criptografar dados existentes
def re_encrypt_all_credentials(new_master_key):
    # Implementar re-criptografia
    pass
```

**Passo 4: Verificar Encoding**
```python
# Verificar encoding dos dados
def check_encoding(data):
    try:
        data.encode('utf-8')
        return True
    except UnicodeEncodeError:
        return False
```

---

## 📊 **PROBLEMAS DE MONITORAMENTO**

### **9. Alertas Não Funcionam**

#### **Sintomas**
- Alertas não são enviados
- Notificações não chegam
- Dashboard não atualiza
- Métricas não são coletadas

#### **Causas Prováveis**
1. Configuração de notificações incorreta
2. Problemas de conectividade
3. Rate limiting de notificações
4. Configuração de alertas inadequada

#### **Soluções**

**Passo 1: Verificar Configuração de Notificações**
```bash
# Verificar configuração do Slack
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H "Content-type: application/json" \
  -d '{"text":"Teste de notificação"}'

# Verificar configuração do Discord
curl -X POST https://discord.com/api/webhooks/YOUR/WEBHOOK/URL \
  -H "Content-type: application/json" \
  -d '{"content":"Teste de notificação"}'
```

**Passo 2: Verificar Logs de Notificação**
```bash
# Verificar logs de notificação
grep "notification" logs/audit.log
grep "alert" logs/audit.log

# Verificar erros de envio
grep "failed" logs/notification.log
```

**Passo 3: Testar Sistema de Alertas**
```python
# Testar envio de alerta manual
def test_alert_system():
    # Implementar teste de alertas
    pass

# Verificar configuração de alertas
def check_alert_configuration():
    # Verificar configuração
    pass
```

**Passo 4: Verificar Métricas**
```bash
# Verificar métricas de notificação
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/metrics

# Verificar status do sistema
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/health
```

### **10. Dashboard Não Atualiza**

#### **Sintomas**
- Dados desatualizados no dashboard
- Métricas não mudam
- Status não reflete realidade
- Cache não é limpo

#### **Causas Prováveis**
1. Cache não está sendo invalidado
2. Problemas de atualização em tempo real
3. Configuração de refresh inadequada
4. Problemas de conectividade com backend

#### **Soluções**

**Passo 1: Verificar Cache do Frontend**
```javascript
// Limpar cache do navegador
localStorage.clear();
sessionStorage.clear();

// Forçar refresh da página
window.location.reload(true);
```

**Passo 2: Verificar WebSocket/SSE**
```javascript
// Verificar conexão WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/credentials');
ws.onopen = () => console.log('WebSocket conectado');
ws.onerror = (error) => console.error('Erro WebSocket:', error);
```

**Passo 3: Verificar API de Status**
```bash
# Verificar se API está respondendo
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/status

# Verificar se dados estão atualizados
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/config
```

**Passo 4: Verificar Logs do Frontend**
```bash
# Verificar logs do navegador (DevTools)
# Console -> Verificar erros JavaScript
# Network -> Verificar requisições falhadas
```

---

## 🔍 **DIAGNÓSTICO AVANÇADO**

### **11. Scripts de Diagnóstico**

#### **Script de Verificação Completa**
```bash
#!/bin/bash
# Script de diagnóstico completo

echo "=== DIAGNÓSTICO DO SISTEMA DE CREDENCIAIS ==="

# Verificar variáveis de ambiente
echo "1. Verificando variáveis de ambiente..."
if [ -z "$CREDENTIAL_MASTER_KEY" ]; then
    echo "ERRO: CREDENTIAL_MASTER_KEY não configurada"
else
    echo "✓ CREDENTIAL_MASTER_KEY configurada"
fi

# Verificar conectividade
echo "2. Verificando conectividade..."
curl -I https://api.openai.com/v1/models > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Conectividade com OpenAI OK"
else
    echo "ERRO: Problema de conectividade com OpenAI"
fi

# Verificar permissões
echo "3. Verificando permissões..."
if [ -w "config/credentials_config.json" ]; then
    echo "✓ Permissões de escrita OK"
else
    echo "ERRO: Sem permissão de escrita"
fi

# Verificar logs
echo "4. Verificando logs..."
if [ -f "logs/credential_errors.log" ]; then
    echo "✓ Arquivo de logs existe"
    echo "Últimos erros:"
    tail -5 logs/credential_errors.log
else
    echo "ERRO: Arquivo de logs não encontrado"
fi

# Verificar métricas
echo "5. Verificando métricas..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/metrics > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ API de métricas respondendo"
else
    echo "ERRO: API de métricas não responde"
fi

echo "=== DIAGNÓSTICO CONCLUÍDO ==="
```

#### **Script de Recuperação**
```bash
#!/bin/bash
# Script de recuperação automática

echo "=== RECUPERAÇÃO DO SISTEMA DE CREDENCIAIS ==="

# Backup da configuração atual
echo "1. Criando backup..."
cp config/credentials_config.json config/credentials_config.json.backup.$(date +%Y%m%d_%H%M%S)

# Limpar cache
echo "2. Limpando cache..."
rm -rf /tmp/credential_cache/*
rm -rf /tmp/encryption_cache/*

# Resetar rate limits
echo "3. Resetando rate limits..."
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/credentials/reset/all

# Verificar integridade
echo "4. Verificando integridade..."
python -c "
from app.services.credential_encryption import verify_integrity
if verify_integrity():
    print('✓ Integridade verificada')
else:
    print('ERRO: Problemas de integridade detectados')
"

# Restaurar configuração se necessário
echo "5. Restaurando configuração..."
if [ ! -f "config/credentials_config.json" ]; then
    echo "Restaurando de backup..."
    cp config/credentials_config.json.backup.* config/credentials_config.json
fi

echo "=== RECUPERAÇÃO CONCLUÍDA ==="
```

### **12. Logs de Diagnóstico**

#### **Comandos Úteis para Logs**
```bash
# Verificar logs em tempo real
tail -f logs/credential_errors.log
tail -f logs/audit.log
tail -f logs/security.log

# Filtrar logs por tipo
grep "ERROR" logs/credential_errors.log
grep "WARNING" logs/credential_errors.log
grep "CRITICAL" logs/credential_errors.log

# Filtrar logs por provedor
grep "openai" logs/credential_errors.log
grep "deepseek" logs/credential_errors.log
grep "claude" logs/credential_errors.log

# Filtrar logs por usuário
grep "user_123" logs/audit.log
grep "admin" logs/audit.log

# Verificar logs de performance
grep "performance" logs/credential_errors.log
grep "timeout" logs/credential_errors.log
grep "slow" logs/credential_errors.log
```

---

## 📞 **CONTATO E SUPORTE**

### **Informações para Suporte**

Ao contatar o suporte, forneça:

1. **Descrição do Problema**: Detalhes específicos
2. **Sintomas**: O que está acontecendo
3. **Passos para Reproduzir**: Como o problema ocorre
4. **Logs Relevantes**: Trechos dos logs de erro
5. **Configuração**: Versões e configurações
6. **Tentativas de Solução**: O que já foi tentado

### **Canais de Suporte**

- **📧 Email**: suporte@omnikeywordsfinder.com
- **💬 Chat**: Disponível no dashboard
- **📞 Telefone**: +55 (11) 99999-9999
- **📚 Documentação**: https://docs.omnikeywordsfinder.com

### **Horário de Atendimento**

- **Segunda a Sexta**: 8h às 18h (GMT-3)
- **Sábados**: 9h às 14h (GMT-3)
- **Emergências**: 24/7 para clientes premium

---

## 📚 **RECURSOS ADICIONAIS**

### **Documentação Relacionada**
- [Documentação da API de Credenciais](api_credentials_documentation.md)
- [Guia de Uso do Dashboard](dashboard_usage_guide.md)
- [Documentação de Criptografia](encryption_process_documentation.md)
- [Arquitetura do Sistema](architecture.md)

### **Ferramentas Úteis**
- **Monitoramento**: Grafana, Prometheus
- **Logs**: ELK Stack, Fluentd
- **Testes**: Postman, curl
- **Debugging**: pdb, logging

---

**Última atualização**: 2025-01-27
**Versão do guia**: 1.0
**Autor**: Paulo Júnior 