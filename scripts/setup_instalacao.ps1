# Script de setup automatizado para Omni Keywords Finder

Write-Host "[1/5] Criando ambiente virtual Python..."
python -m venv .venv

Write-Host "[2/5] Ativando ambiente virtual..."
.venv\Scripts\activate

Write-Host "[3/5] Instalando dependências Python..."
pip install -r requirements.txt

Write-Host "[4/5] Instalando dependências do frontend (React/Vite)..."
cd app
npm install
cd ..

Write-Host "[5/5] Setup concluído!"
Write-Host "- Ative o ambiente virtual: .venv\Scripts\activate"
Write-Host "- Configure as variáveis de ambiente conforme README.md"
Write-Host "- Inicie o backend e frontend conforme instruções"
Write-Host "- Para rodar testes E2E: ./scripts/start_frontend_and_test_e2e.ps1" 