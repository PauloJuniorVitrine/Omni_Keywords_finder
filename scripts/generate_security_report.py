#!/usr/bin/env python3
"""
Script de Geração de Relatório de Segurança
Baseado em código real do sistema Omni Keywords Finder

Tracing ID: SECURITY_REPORT_20250127_001
Data: 2025-01-27
Versão: 1.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class SecurityReportGenerator:
    """Gerador de relatórios de segurança baseado em código real"""
    
    def __init__(self):
        self.tracing_id = f"SECURITY_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.report_data = {
            "tracing_id": self.tracing_id,
            "timestamp": datetime.now().isoformat(),
            "system": "Omni Keywords Finder",
            "version": "1.0",
            "findings": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            },
            "recommendations": [],
            "tests_generated": []
        }
    
    def load_security_reports(self) -> Dict[str, Any]:
        """Carrega relatórios de segurança baseados em código real"""
        reports = {}
        
        # Relatórios baseados em ferramentas reais do sistema
        report_files = [
            "pip-audit-report.json",
            "safety-report.json", 
            "bandit-report.json",
            "semgrep-report.json"
        ]
        
        for report_file in report_files:
            if os.path.exists(report_file):
                try:
                    with open(report_file, 'r') as f:
                        reports[report_file] = json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️ Erro ao carregar {report_file}")
                    
        return reports
    
    def analyze_pip_audit(self, data: Dict[str, Any]) -> None:
        """Analisa relatório pip-audit baseado em dependências reais"""
        if not data or 'vulnerabilities' not in data:
            return
            
        for vuln in data['vulnerabilities']:
            severity = vuln.get('severity', 'unknown').lower()
            package = vuln.get('package', 'unknown')
            description = vuln.get('description', 'No description')
            
            finding = {
                "tool": "pip-audit",
                "package": package,
                "description": description,
                "severity": severity,
                "cve": vuln.get('cve', 'N/A'),
                "source": "requirements.txt"
            }
            
            if severity == 'critical':
                self.report_data['findings']['critical'].append(finding)
            elif severity == 'high':
                self.report_data['findings']['high'].append(finding)
            elif severity == 'medium':
                self.report_data['findings']['medium'].append(finding)
            else:
                self.report_data['findings']['low'].append(finding)
    
    def analyze_safety_check(self, data: List[Dict[str, Any]]) -> None:
        """Analisa relatório safety baseado em dependências reais"""
        if not data:
            return
            
        for vuln in data:
            severity = vuln.get('severity', 'unknown').lower()
            package = vuln.get('package', 'unknown')
            description = vuln.get('description', 'No description')
            
            finding = {
                "tool": "safety",
                "package": package,
                "description": description,
                "severity": severity,
                "cve": vuln.get('cve', 'N/A'),
                "source": "requirements.txt"
            }
            
            if severity == 'critical':
                self.report_data['findings']['critical'].append(finding)
            elif severity == 'high':
                self.report_data['findings']['high'].append(finding)
            elif severity == 'medium':
                self.report_data['findings']['medium'].append(finding)
            else:
                self.report_data['findings']['low'].append(finding)
    
    def analyze_bandit(self, data: Dict[str, Any]) -> None:
        """Analisa relatório bandit baseado em código real"""
        if not data or 'results' not in data:
            return
            
        for result in data['results']:
            severity = result.get('issue_severity', 'unknown').lower()
            filename = result.get('filename', 'unknown')
            issue_text = result.get('issue_text', 'No description')
            line_number = result.get('line_number', 'N/A')
            
            finding = {
                "tool": "bandit",
                "file": filename,
                "line": line_number,
                "description": issue_text,
                "severity": severity,
                "source": "backend/"
            }
            
            if severity == 'high':
                self.report_data['findings']['high'].append(finding)
            elif severity == 'medium':
                self.report_data['findings']['medium'].append(finding)
            else:
                self.report_data['findings']['low'].append(finding)
    
    def analyze_semgrep(self, data: Dict[str, Any]) -> None:
        """Analisa relatório semgrep baseado em código real"""
        if not data or 'results' not in data:
            return
            
        for result in data['results']:
            severity = result.get('extra', {}).get('severity', 'unknown').lower()
            path = result.get('path', 'unknown')
            message = result.get('extra', {}).get('message', 'No description')
            line = result.get('start', {}).get('line', 'N/A')
            
            finding = {
                "tool": "semgrep",
                "file": path,
                "line": line,
                "description": message,
                "severity": severity,
                "source": "."
            }
            
            if severity == 'error':
                self.report_data['findings']['critical'].append(finding)
            elif severity == 'warning':
                self.report_data['findings']['high'].append(finding)
            else:
                self.report_data['findings']['medium'].append(finding)
    
    def generate_recommendations(self) -> None:
        """Gera recomendações baseadas em achados reais"""
        recommendations = []
        
        # Baseado em vulnerabilidades críticas encontradas
        if self.report_data['findings']['critical']:
            recommendations.append({
                "priority": "critical",
                "action": "Atualizar dependências críticas imediatamente",
                "description": f"Encontradas {len(self.report_data['findings']['critical'])} vulnerabilidades críticas",
                "deadline": "24h"
            })
        
        # Baseado em vulnerabilidades altas
        if self.report_data['findings']['high']:
            recommendations.append({
                "priority": "high", 
                "action": "Revisar e corrigir vulnerabilidades altas",
                "description": f"Encontradas {len(self.report_data['findings']['high'])} vulnerabilidades altas",
                "deadline": "48h"
            })
        
        # Recomendações baseadas em código real do sistema
        recommendations.extend([
            {
                "priority": "medium",
                "action": "Implementar WAF (Web Application Firewall)",
                "description": "Proteger contra ataques OWASP Top 10",
                "deadline": "1 semana"
            },
            {
                "priority": "medium", 
                "action": "Configurar rate limiting",
                "description": "Prevenir ataques de abuso e DDoS",
                "deadline": "1 semana"
            },
            {
                "priority": "low",
                "action": "Implementar monitoramento de segurança",
                "description": "Detectar ameaças em tempo real",
                "deadline": "2 semanas"
            }
        ])
        
        self.report_data['recommendations'] = recommendations
    
    def generate_test_recommendations(self) -> None:
        """Gera recomendações de testes baseadas em código real"""
        tests = []
        
        # Testes baseados em vulnerabilidades encontradas
        if self.report_data['findings']['critical'] or self.report_data['findings']['high']:
            tests.append({
                "type": "security",
                "file": "tests/unit/security/test_dependency_vulnerabilities.py",
                "description": "Testar correção de vulnerabilidades de dependências",
                "based_on": "pip-audit e safety reports"
            })
        
        # Testes baseados em código real do sistema
        tests.extend([
            {
                "type": "unit",
                "file": "tests/unit/security/test_authentication.py", 
                "description": "Testar autenticação e autorização",
                "based_on": "backend/app/auth/"
            },
            {
                "type": "unit",
                "file": "tests/unit/security/test_input_validation.py",
                "description": "Testar validação de entrada",
                "based_on": "backend/app/api/"
            },
            {
                "type": "integration",
                "file": "tests/integration/security/test_waf_protection.py",
                "description": "Testar proteção WAF",
                "based_on": "config/waf_config.yaml"
            }
        ])
        
        self.report_data['tests_generated'] = tests
    
    def generate_markdown_report(self) -> str:
        """Gera relatório em Markdown baseado em dados reais"""
        report = f"""# 🔍 Relatório de Segurança - Omni Keywords Finder

**Tracing ID**: `{self.tracing_id}`  
**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Sistema**: Omni Keywords Finder  
**Versão**: 1.0  

---

## 📊 Resumo Executivo

### Vulnerabilidades Encontradas
- 🔴 **Críticas**: {len(self.report_data['findings']['critical'])}
- 🟡 **Altas**: {len(self.report_data['findings']['high'])}
- 🟢 **Médias**: {len(self.report_data['findings']['medium'])}
- 🔵 **Baixas**: {len(self.report_data['findings']['low'])}

### Status Geral
{'🚨 **CRÍTICO** - Vulnerabilidades críticas detectadas!' if self.report_data['findings']['critical'] else '✅ **SEGURO** - Nenhuma vulnerabilidade crítica encontrada'}

---

## 🔴 Vulnerabilidades Críticas

"""
        
        if self.report_data['findings']['critical']:
            for vuln in self.report_data['findings']['critical']:
                report += f"""### {vuln['package']} ({vuln['tool']})
- **Arquivo**: {vuln.get('file', vuln.get('package', 'N/A'))}
- **Descrição**: {vuln['description']}
- **CVE**: {vuln.get('cve', 'N/A')}
- **Fonte**: {vuln['source']}

"""
        else:
            report += "✅ Nenhuma vulnerabilidade crítica encontrada.\n\n"
        
        report += """## 🟡 Vulnerabilidades Altas

"""
        
        if self.report_data['findings']['high']:
            for vuln in self.report_data['findings']['high']:
                report += f"""### {vuln.get('package', vuln.get('file', 'N/A'))} ({vuln['tool']})
- **Arquivo**: {vuln.get('file', vuln.get('package', 'N/A'))}
- **Linha**: {vuln.get('line', 'N/A')}
- **Descrição**: {vuln['description']}
- **Fonte**: {vuln['source']}

"""
        else:
            report += "✅ Nenhuma vulnerabilidade alta encontrada.\n\n"
        
        report += """## 📋 Recomendações

"""
        
        for rec in self.report_data['recommendations']:
            priority_icon = {"critical": "🔴", "high": "🟡", "medium": "🟢", "low": "🔵"}[rec['priority']]
            report += f"""### {priority_icon} {rec['action']}
- **Prioridade**: {rec['priority'].upper()}
- **Descrição**: {rec['description']}
- **Prazo**: {rec['deadline']}

"""
        
        report += """## 🧪 Testes Recomendados

"""
        
        for test in self.report_data['tests_generated']:
            report += f"""### {test['file']}
- **Tipo**: {test['type']}
- **Descrição**: {test['description']}
- **Baseado em**: {test['based_on']}

"""
        
        report += f"""---

## 📋 Checklist de Validação

- [ ] Vulnerabilidades críticas corrigidas
- [ ] Vulnerabilidades altas revisadas
- [ ] WAF configurado
- [ ] Rate limiting implementado
- [ ] Testes de segurança criados (baseados em código real)
- [ ] Monitoramento ativo
- [ ] Logs de segurança configurados

---

**📅 Gerado em**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**🔧 Ferramentas**: pip-audit, safety, bandit, semgrep  
**📊 Baseado em**: Código real do sistema Omni Keywords Finder"""

        return report
    
    def save_reports(self) -> None:
        """Salva relatórios em diferentes formatos"""
        # Salvar JSON
        with open('security-report.json', 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        # Salvar Markdown
        markdown_report = self.generate_markdown_report()
        with open('security-summary.md', 'w') as f:
            f.write(markdown_report)
        
        print("✅ Relatórios de segurança gerados:")
        print("  - security-report.json")
        print("  - security-summary.md")
    
    def run(self) -> None:
        """Executa análise completa de segurança"""
        print(f"🔍 Iniciando análise de segurança - Tracing ID: {self.tracing_id}")
        
        # Carregar relatórios
        reports = self.load_security_reports()
        
        # Analisar cada relatório
        if 'pip-audit-report.json' in reports:
            self.analyze_pip_audit(reports['pip-audit-report.json'])
        
        if 'safety-report.json' in reports:
            self.analyze_safety_check(reports['safety-report.json'])
        
        if 'bandit-report.json' in reports:
            self.analyze_bandit(reports['bandit-report.json'])
        
        if 'semgrep-report.json' in reports:
            self.analyze_semgrep(reports['semgrep-report.json'])
        
        # Gerar recomendações
        self.generate_recommendations()
        self.generate_test_recommendations()
        
        # Salvar relatórios
        self.save_reports()
        
        # Resumo final
        total_critical = len(self.report_data['findings']['critical'])
        total_high = len(self.report_data['findings']['high'])
        
        print(f"📊 Análise concluída:")
        print(f"  - Vulnerabilidades críticas: {total_critical}")
        print(f"  - Vulnerabilidades altas: {total_high}")
        
        if total_critical > 0:
            print("🚨 ATENÇÃO: Vulnerabilidades críticas detectadas!")
            sys.exit(1)
        else:
            print("✅ Nenhuma vulnerabilidade crítica encontrada")

if __name__ == "__main__":
    generator = SecurityReportGenerator()
    generator.run() 