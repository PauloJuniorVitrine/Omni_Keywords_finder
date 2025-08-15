# Playbook de Onboarding — Omni Keywords Finder

## 1. Preparação do Ambiente
- Instale Python 3.11+, Node.js 18+, npm 9+
- Clone o repositório e crie o ambiente virtual:
```sh
git clone <repo>
cd omni_keywords_finder
python -m venv .venv
.venv/Scripts/activate  # Windows
```
- Instale dependências:
```sh
pip install -r requirements.txt
cd app && npm install
```

## 2. Configuração de Variáveis
- Copie `.env.example` para `.env` e preencha as variáveis obrigatórias.
- Configure credenciais de APIs e, se necessário, integração com Vault.

## 3. Execução Inicial
- Inicie Redis, Celery e Flask:
```sh
redis-server
celery -A app.worker worker --loglevel=info
$env:PYTHONPATH=(Get-Location).Path; python app/main.py
```
- Inicie o frontend:
```sh
cd app && npm run dev
```
- Acesse http://localhost:5000 (backend) e http://localhost:3000 (frontend)

## 4. Execução de Testes
- Unitários/integrados:
```sh
pytest
```
- E2E:
```sh
npx playwright test
npx cypress run
```

## 5. Checklist de Validação
- [ ] Backend e frontend sobem sem erros
- [ ] Testes unitários e E2E passam 100%
- [ ] Dashboard e métricas acessíveis
- [ ] Exportação e coleta funcionam

## 6. Links Úteis
- [README.md](../../README.md)
- [docs/explanation.md](../explanation.md)
- [docs/monitoramento.md](../monitoramento.md)
- [docs/security.md](../security.md)
- [docs/disaster_recovery.md](../disaster_recovery.md) 