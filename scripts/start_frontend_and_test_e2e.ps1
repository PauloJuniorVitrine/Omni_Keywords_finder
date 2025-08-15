# Inicia o frontend React em background
Start-Process powershell -ArgumentList 'cd app; npm run dev'

# Aguarda o frontend subir
Start-Sleep -Seconds 10

# Executa os testes Cypress E2E
npx cypress run --spec tests/e2e/specs/governanca.cy.ts 