# 🧪 TESTES DE CARGA CRÍTICOS - AUTENTICAÇÃO

## 📋 Visão Geral

Este diretório contém os testes de carga críticos para os endpoints de autenticação do sistema Omni Keywords Finder.

---

## 🎯 Endpoints Testados

### ✅ Implementados

1. **`locustfile_auth_login_v1.py`** - Teste de carga em `/api/auth/login`
   - Status: ✅ Implementado
   - Cenários: Login válido, credenciais inválidas, dados malformados, rate limiting
   - Script: `run_auth_login_test.py`

2. **`locustfile_auth_logout_v1.py`** - Teste de carga em `/api/auth/logout`
   - Status: ✅ Implementado
   - Cenários: Logout válido, token expirado, sem token, token malformado, logout concorrente
   - Script: `run_auth_logout_test.py`

3. **`locustfile_auth_refresh_v1.py`** - Teste de carga em `/api/auth/refresh`
   - Status: ✅ Implementado
   - Cenários: Refresh token válido, expirado, inválido, tipo incorreto, payload malformado, concorrência
   - Script: `run_auth_refresh_test.py`

### 🔄 Próximos

4. **`locustfile_auth_register_v1.py`** - Teste de carga em `/api/auth/register`
   - Status: ⏳ Pendente
   - Cenários: Registro válido, dados duplicados, validação de campos, rate limiting

5. **`locustfile_auth_oauth2_v1.py`** - Teste de carga em `/api/auth/oauth2/*`
   - Status: ⏳ Pendente
   - Cenários: Login OAuth2, callback, tokens de terceiros

---

## 🚀 Como Executar

### Pré-requisitos

```bash
# Instalar dependências
pip install locust requests pyjwt

# Verificar se o servidor está rodando
curl http://localhost:8000/health
```

### Execução Individual

```bash
# Teste de Login
python run_auth_login_test.py

# Teste de Logout
python run_auth_logout_test.py

# Teste de Refresh
python run_auth_refresh_test.py
```

### Execução com Parâmetros

```bash
# Executar com configurações customizadas
python run_auth_refresh_test.py --host http://localhost:8000 --users 100 --run-time 10m

# Executar em modo web (interface gráfica)
python run_auth_refresh_test.py --web
```

### Execução via Locust Direto

```bash
# Login
locust -f locustfile_auth_login_v1.py --host=http://localhost:8000

# Logout
locust -f locustfile_auth_logout_v1.py --host=http://localhost:8000

# Refresh
locust -f locustfile_auth_refresh_v1.py --host=http://localhost:8000
```

---

## 📊 Métricas e Relatórios

### Arquivos Gerados

Cada teste gera os seguintes arquivos na pasta `reports/`:

- `auth_*_test_report.html` - Relatório HTML detalhado
- `auth_*_test_report.json` - Dados brutos em JSON
- `auth_*_test_report.csv` - Dados em CSV
- `auth_*_test.log` - Logs da execução
- `auth_*_test_summary.md` - Resumo executivo

### Métricas Coletadas

- **Performance**: Tempo de resposta, throughput, latência
- **Confiabilidade**: Taxa de sucesso, falhas, erros
- **Segurança**: Validação de tokens, rate limiting, concorrência
- **Escalabilidade**: Comportamento sob carga

---

## 🔍 Cenários de Teste

### Login (`/api/auth/login`)

| Cenário | Frequência | Objetivo |
|---------|------------|----------|
| Credenciais válidas | 60% | Testar fluxo normal |
| Credenciais inválidas | 25% | Testar rejeição |
| Dados malformados | 10% | Testar validação |
| Rate limiting | 5% | Testar limites |

### Logout (`/api/auth/logout`)

| Cenário | Frequência | Objetivo |
|---------|------------|----------|
| Token válido | 70% | Testar logout normal |
| Token expirado | 15% | Testar token expirado |
| Sem token | 10% | Testar autenticação |
| Token malformado | 5% | Testar validação |

### Refresh (`/api/auth/refresh`)

| Cenário | Frequência | Objetivo |
|---------|------------|----------|
| Refresh token válido | 40% | Testar renovação normal |
| Refresh token expirado | 20% | Testar rejeição de expirado |
| Refresh token inválido | 15% | Testar validação |
| Tipo de token incorreto | 10% | Testar segurança |
| Payload malformado | 10% | Testar validação |
| Concorrência | 5% | Testar race conditions |

---

## 🛡️ Abordagens de Segurança

### Validação de Tokens

- **JWT Validation**: Verificação de assinatura e claims
- **Expiration Check**: Validação de tempo de expiração
- **Blacklist Check**: Verificação de tokens revogados
- **Type Validation**: Validação de tipo de token

### Rate Limiting

- **Per User**: Limite por usuário
- **Per IP**: Limite por endereço IP
- **Per Endpoint**: Limite específico por endpoint
- **Burst Protection**: Proteção contra picos

### Concorrência

- **Token Rotation**: Rotação automática de tokens
- **Family Tracking**: Rastreamento de famílias de tokens
- **Conflict Resolution**: Resolução de conflitos
- **Atomic Operations**: Operações atômicas

---

## 📈 Critérios de Sucesso

### Performance

- **Tempo de Resposta**: < 2000ms (médio)
- **Throughput**: > 50 req/s
- **Latência P95**: < 5000ms
- **Taxa de Falha**: < 5%

### Segurança

- **Tokens Expirados**: 100% rejeitados
- **Tokens Inválidos**: 100% rejeitados
- **Rate Limiting**: Funcionando corretamente
- **Concorrência**: Sem vazamentos de segurança

### Confiabilidade

- **Disponibilidade**: > 99%
- **Consistência**: Respostas consistentes
- **Recuperação**: Após falhas
- **Monitoramento**: Logs completos

---

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Servidor
API_HOST=http://localhost:8000
API_PORT=8000

# Teste
TEST_USERS=50
TEST_SPAWN_RATE=10
TEST_DURATION=5m

# Segurança
JWT_SECRET_KEY=your-secret-key
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key
REDIS_URL=redis://localhost:6379/0
```

### Configuração de Teste

```python
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "endpoint": "/api/auth/refresh",
    "rate_limit": 100,
    "concurrent_users": 50,
    "test_duration": 300,
    "think_time": (1, 3),
}
```

---

## 📋 Checklist de Validação

### Pré-Teste

- [ ] Servidor rodando e acessível
- [ ] Database conectado e funcionando
- [ ] Redis disponível para rate limiting
- [ ] Logs configurados e funcionando
- [ ] Monitoramento ativo
- [ ] Backup dos dados críticos

### Durante o Teste

- [ ] Métricas sendo coletadas
- [ ] Logs sendo monitorados
- [ ] Performance sendo observada
- [ ] Erros sendo registrados
- [ ] Alertas configurados
- [ ] Recursos sendo monitorados

### Pós-Teste

- [ ] Relatórios gerados
- [ ] Análise realizada
- [ ] Recomendações criadas
- [ ] Documentação atualizada
- [ ] Próximos passos definidos
- [ ] Limpeza de dados de teste

---

## 🚨 Troubleshooting

### Problemas Comuns

1. **Servidor não responde**
   ```bash
   # Verificar se está rodando
   curl http://localhost:8000/health
   
   # Verificar logs
   tail -f logs/server.log
   ```

2. **Rate limiting muito agressivo**
   ```bash
   # Ajustar configurações
   export RATE_LIMIT_REQUESTS=1000
   export RATE_LIMIT_WINDOW=60
   ```

3. **Tokens inválidos**
   ```bash
   # Verificar configuração JWT
   echo $JWT_SECRET_KEY
   echo $JWT_REFRESH_SECRET_KEY
   ```

4. **Performance ruim**
   ```bash
   # Verificar recursos
   htop
   free -h
   df -h
   ```

### Logs Importantes

```bash
# Logs do servidor
tail -f logs/server.log | grep "auth"

# Logs do teste
tail -f reports/auth_*_test.log

# Logs de erro
tail -f logs/error.log
```

---

## 📚 Documentação Adicional

- [Diagramas de Fluxo](docs/load-testing/diagrams/)
- [Métricas e KPIs](docs/load-testing/metrics.md)
- [Guia de Troubleshooting](docs/load-testing/troubleshooting.md)
- [Checklist Completo](../CHECKLIST_TESTES_CARGA_CRITICIDADE.md)

---

## 🤝 Contribuição

Para adicionar novos testes ou melhorar os existentes:

1. Siga o padrão de nomenclatura
2. Implemente as abordagens CoCoT, ToT, ReAct
3. Adicione documentação visual
4. Atualize este README
5. Execute testes de validação

---

## 📞 Suporte

Para dúvidas ou problemas:

- **Issues**: Abra uma issue no repositório
- **Documentação**: Consulte a documentação técnica
- **Logs**: Verifique os logs de execução
- **Métricas**: Analise os relatórios gerados 