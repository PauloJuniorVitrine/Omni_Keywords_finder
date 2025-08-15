# 🚀 INSTALAÇÃO - OMNİ KEYWORDS FINDER

## 📋 Visão Geral

Este documento fornece instruções completas para instalar e configurar o **Omni Keywords Finder** em diferentes ambientes.

## 🎯 Ambientes Suportados

- **Desenvolvimento**: Para desenvolvedores e testes locais
- **Produção**: Para ambientes de produção
- **Completo**: Todas as dependências (dev + prod)

## ⚡ Instalação Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/omni_keywords_finder.git
cd omni_keywords_finder
```

### 2. Instalação Automatizada (Recomendado)
```bash
# Instalação automática (detecta ambiente)
python scripts/install_dependencies.py

# Ou especificar ambiente
python scripts/install_dependencies.py --env dev
python scripts/install_dependencies.py --env prod
python scripts/install_dependencies.py --env full
```

### 3. Instalação Manual

#### Desenvolvimento
```bash
pip install -r requirements-dev.txt
```

#### Produção
```bash
pip install -r requirements-prod.txt
```

#### Completo
```bash
pip install -r requirements.txt
```

## 🔧 Configuração

### 1. Arquivo de Ambiente
O script de instalação cria automaticamente um arquivo `.env` com configurações básicas. Edite conforme necessário:

```bash
# Editar configurações
nano .env
```

### 2. Modelos SpaCy (Obrigatório)
```bash
# Instalar modelos de linguagem
python -m spacy download pt_core_news_lg
python -m spacy download en_core_web_lg
```

### 3. Banco de Dados
```bash
# Inicializar banco de dados
flask db upgrade
```

## 🧪 Validação da Instalação

### 1. Testes Automáticos
```bash
# Executar todos os testes
pytest tests/ -v

# Executar testes específicos
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

### 2. Verificação Manual
```bash
# Verificar importações principais
python -c "import flask, fastapi, pandas, numpy, sqlalchemy; print('✅ Todas as dependências OK')"

# Verificar modelos SpaCy
python -c "import spacy; spacy.load('pt_core_news_lg'); spacy.load('en_core_web_lg'); print('✅ Modelos SpaCy OK')"
```

### 3. Verificação de Segurança
```bash
# Auditoria de dependências
pip-audit

# Verificação de segurança
safety check

# Análise estática de código
bandit -r .
```

## 🚀 Executando a Aplicação

### 1. Modo Desenvolvimento
```bash
# Flask (padrão)
flask run

# FastAPI
uvicorn backend.app.main:app --reload

# Ambos
python scripts/run_development.py
```

### 2. Modo Produção
```bash
# Gunicorn (recomendado)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app.main:app

# Uvicorn
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### 3. Docker
```bash
# Construir imagem
docker build -t omni-keywords-finder .

# Executar container
docker run -p 8000:8000 omni-keywords-finder
```

## 📊 Monitoramento

### 1. Métricas
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Jaeger**: http://localhost:16686

### 2. Logs
```bash
# Visualizar logs em tempo real
tail -f logs/app.log

# Logs estruturados
tail -f logs/structured.log
```

### 3. Health Check
```bash
# Verificar saúde da aplicação
curl http://localhost:8000/health

# Verificar métricas
curl http://localhost:8000/metrics
```

## 🔒 Segurança

### 1. Configurações Críticas
```bash
# Gerar chave secreta
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Configurar variáveis de ambiente
export SECRET_KEY="sua-chave-secreta-aqui"
export JWT_SECRET_KEY="sua-chave-jwt-aqui"
```

### 2. Firewall
```bash
# Configurar firewall (Ubuntu/Debian)
sudo ufw allow 8000
sudo ufw allow 22
sudo ufw enable
```

### 3. SSL/TLS
```bash
# Certificado auto-assinado (desenvolvimento)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configurar HTTPS
uvicorn backend.app.main:app --ssl-keyfile key.pem --ssl-certfile cert.pem
```

## 🐛 Solução de Problemas

### Problemas Comuns

#### 1. Erro de Dependências
```bash
# Limpar cache do pip
pip cache purge

# Reinstalar dependências
pip install --force-reinstall -r requirements.txt
```

#### 2. Erro de Modelos SpaCy
```bash
# Verificar instalação do SpaCy
python -c "import spacy; print(spacy.__version__)"

# Reinstalar modelos
python -m spacy download pt_core_news_lg --force
python -m spacy download en_core_web_lg --force
```

#### 3. Erro de Banco de Dados
```bash
# Resetar banco de dados
rm instance/db.sqlite3
flask db upgrade
```

#### 4. Erro de Porta em Uso
```bash
# Encontrar processo usando a porta
lsof -i :8000

# Matar processo
kill -9 <PID>
```

### Logs de Erro
```bash
# Verificar logs de erro
tail -f logs/error.log

# Logs de debug
tail -f logs/debug.log
```

## 📈 Performance

### 1. Otimizações Recomendadas
```bash
# Configurar Redis
redis-server

# Configurar Celery
celery -A backend.app.celery worker --loglevel=info

# Configurar cache
export CACHE_TYPE=redis
export CACHE_REDIS_URL=redis://localhost:6379/1
```

### 2. Monitoramento de Performance
```bash
# Profiling com cProfile
python -m cProfile -o profile.stats app.py

# Análise de memória
python -m memory_profiler app.py
```

## 🔄 Atualizações

### 1. Atualizar Dependências
```bash
# Verificar atualizações
pip list --outdated

# Atualizar dependências
pip install --upgrade -r requirements.txt

# Verificar segurança após atualização
pip-audit
safety check
```

### 2. Atualizar Aplicação
```bash
# Pull das mudanças
git pull origin main

# Atualizar banco de dados
flask db upgrade

# Reiniciar aplicação
sudo systemctl restart omni-keywords-finder
```

## 📞 Suporte

### 1. Documentação
- [Guia de Desenvolvimento](docs/DEVELOPMENT.md)
- [Guia de API](docs/API.md)
- [Guia de Deploy](docs/DEPLOYMENT.md)

### 2. Comunidade
- [Issues](https://github.com/seu-usuario/omni_keywords_finder/issues)
- [Discussions](https://github.com/seu-usuario/omni_keywords_finder/discussions)

### 3. Logs de Instalação
```bash
# Verificar logs de instalação
cat logs/dependency_installation.log

# Relatório de instalação
cat logs/installation_report_*.json
```

## ✅ Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas
- [ ] Modelos SpaCy instalados
- [ ] Arquivo .env configurado
- [ ] Banco de dados inicializado
- [ ] Testes passando
- [ ] Verificação de segurança OK
- [ ] Aplicação rodando
- [ ] Health check OK
- [ ] Logs funcionando

## 🎉 Próximos Passos

1. **Configure as variáveis de ambiente** no arquivo `.env`
2. **Execute a aplicação**: `flask run`
3. **Acesse a interface**: http://localhost:5000
4. **Configure monitoramento**: Prometheus, Grafana, Jaeger
5. **Configure backup**: Scripts automáticos
6. **Configure CI/CD**: GitHub Actions ou similar

---

**🎯 Status**: ✅ Pronto para Produção  
**📅 Última Atualização**: 2025-01-27  
**🔗 Versão**: 3.0.0 