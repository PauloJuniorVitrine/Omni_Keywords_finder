# Script PowerShell para resetar ambiente, iniciar backend Flask e rodar testes de integração

# Finaliza todos os processos Python
Write-Host 'Finalizando processos Python...'
taskkill /F /IM python.exe

# Limpa caches de bytecode
Write-Host 'Limpando __pycache__ e arquivos .pyc...'
Get-ChildItem -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Inicia o backend Flask em background
Write-Host 'Iniciando backend Flask...'
Start-Process -NoNewWindow -FilePath python -ArgumentList 'app/main.py'
Start-Sleep -Seconds 5

# Executa os testes de integração
Write-Host 'Executando testes de integração...'
pytest tests/integration --disable-warnings -v 