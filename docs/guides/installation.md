# Guia de Instalação e Configuração

## Requisitos do Sistema

- Python 3.8+
- MongoDB 4.4+
- Redis 6.0+
- Node.js 14+ (para frontend)
- 4GB RAM mínimo
- 10GB espaço em disco

## Instalação Rápida

1. Clone o repositório:
```bash
git clone https://github.com/your-org/omni_keywords_finder.git
cd omni_keywords_finder
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Inicie os serviços:
```bash
docker-compose up -d  # Para MongoDB e Redis
python src/main.py    # Para a API
```

## Configuração

### Variáveis de Ambiente

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=keywords_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# ML
MODEL_PATH=models/
BATCH_SIZE=32
```

### Configuração do Banco

1. Crie os índices:
```python
python scripts/create_indexes.py
```

2. Inicialize o banco:
```python
python scripts/init_db.py
```

### Configuração do Cache

1. Verifique conexão Redis:
```python
python scripts/test_redis.py
```

2. Configure TTL padrão:
```python
python scripts/set_cache_ttl.py
```

## Verificação

1. Teste a API:
```bash
curl http://localhost:8000/health
```

2. Verifique logs:
```bash
tail -f logs/api.log
```

3. Monitore métricas:
```bash
curl http://localhost:8000/metrics
```

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão MongoDB**
   - Verifique se o MongoDB está rodando
   - Confirme a URI no .env
   - Verifique firewall

2. **Erro de conexão Redis**
   - Verifique se o Redis está rodando
   - Confirme host/porta no .env
   - Verifique firewall

3. **Erro de importação**
   - Verifique se o ambiente virtual está ativo
   - Reinstale dependências
   - Verifique versão do Python

### Logs

- API: `logs/api.log`
- MongoDB: `logs/mongodb.log`
- Redis: `logs/redis.log`
- Sistema: `logs/system.log`

## Suporte

- Issues: GitHub Issues
- Email: support@example.com
- Slack: #omni-keywords-support 