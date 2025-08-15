import os
import glob
import datetime
from typing import Dict, List, Optional, Any

def checar_cobertura():
    cobertura = 0
    if os.path.exists('test-results/coverage.xml'):
        with open('test-results/coverage.xml') as f:
            for line in f:
                if 'line-rate' in line:
                    try:
                        cobertura = float(line.split('line-rate="')[1].split('"')[0]) * 100
                    except Exception:
                        pass
    return cobertura

def checar_changelog():
    return os.path.exists('CHANGELOG.md')

def checar_logs_erro():
    erros = []
    if os.path.exists('logs/omni_keywords.log'):
        with open('logs/omni_keywords.log', encoding='utf-8') as f:
            for line in f.readlines()[-100:]:
                if 'error' in line.lower() or 'fail' in line.lower():
                    erros.append(line.strip())
    return erros

def checar_artefatos():
    obrigatorios = [
        'README.md', 'CHANGELOG.md', 'requirements.txt', 'env.example',
        'docs/explanation.md', 'docs/monitoramento.md', 'docs/security.md',
        'docs/disaster_recovery.md', 'docs/playbooks/onboarding.md',
        'docs/playbooks/troubleshooting.md', 'docs/playbooks/release_checklist.md'
    ]
    faltando = [a for a in obrigatorios if not os.path.exists(a)]
    return faltando

def gerar_relatorio():
    data = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    cobertura = checar_cobertura()
    changelog = checar_changelog()
    erros = checar_logs_erro()
    faltando = checar_artefatos()
    rel = f"""
# Relatório de Release — {data}

- Cobertura de testes: {cobertura:.2f}%
- Changelog presente: {'Sim' if changelog else 'Não'}
- Artefatos obrigatórios faltando: {', '.join(faltando) if faltando else 'Nenhum'}
- Logs de erro recentes: {len(erros)}

## Logs de erro (últimos 100)
"""
    rel += '\n'.join(erros[:20])
    with open('docs/relatorio_release.md', 'w', encoding='utf-8') as f:
        f.write(rel)
    print(rel)

if __name__ == '__main__':
    gerar_relatorio() 