#!/usr/bin/env python3
"""
Script de Verificação de Versões de Dependências
Omni Keywords Finder - Security Verification

Tracing ID: VERSION_VERIFICATION_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: ✅ PRONTO PARA USO
"""

import subprocess
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VersionVerifier:
    """Classe para verificar versões de dependências"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
        # Versões seguras esperadas (baseadas em vulnerabilidades conhecidas)
        self.secure_versions = {
            # Críticas
            'werkzeug': '2.3.8',
            'jinja2': '3.1.3',
            'pillow': '10.1.1',
            'cryptography': '41.0.8',
            'requests': '2.32.6',
            'beautifulsoup4': '4.11.0',
            'lxml': '4.9.0',
            'PyYAML': '6.0.2',
            
            # Altas
            'flask': '2.3.3',
            'fastapi': '0.100.6',
            'pandas': '2.2.6',
            'numpy': '1.26.6',
            'scikit-learn': '1.2.0',
            
            # Médias
            'redis': '4.6.6',
            'celery': '5.3.6',
            'aiohttp': '3.8.6',
            'httpx': '0.27.6',
            'spacy': '3.7.6',
            'sentence-transformers': '2.2.0',
            'boto3': '1.34.6'
        }
        
        # Mapeamento de nomes de importação
        self.import_names = {
            'beautifulsoup4': 'bs4',
            'PyYAML': 'yaml',
            'pillow': 'PIL',
            'scikit-learn': 'sklearn'
        }
    
    def get_installed_version(self, package: str) -> str:
        """Obtém a versão instalada de um pacote"""
        try:
            import_name = self.import_names.get(package, package)
            module = __import__(import_name)
            
            # Tenta diferentes atributos de versão
            version_attrs = ['__version__', 'VERSION', 'version']
            for attr in version_attrs:
                if hasattr(module, attr):
                    return getattr(module, attr)
            
            # Se não encontrar, tenta importar versão específica
            if hasattr(module, 'version'):
                return module.version
            
            return "N/A"
            
        except ImportError:
            return "NÃO INSTALADO"
        except Exception as e:
            logger.error(f"Erro ao verificar {package}: {e}")
            return "ERRO"
    
    def compare_versions(self, current: str, expected: str) -> Tuple[bool, str]:
        """Compara versões e retorna se está atualizado"""
        if current == "NÃO INSTALADO" or current == "ERRO" or current == "N/A":
            return False, f"Problema: {current}"
        
        try:
            from packaging import version
            current_ver = version.parse(current)
            expected_ver = version.parse(expected)
            
            if current_ver >= expected_ver:
                return True, "✅ Atualizado"
            else:
                return False, f"❌ Desatualizado (atual: {current}, esperado: {expected})"
                
        except ImportError:
            # Fallback simples se packaging não estiver disponível
            if current >= expected:
                return True, "✅ Atualizado"
            else:
                return False, f"❌ Desatualizado (atual: {current}, esperado: {expected})"
        except Exception as e:
            return False, f"❌ Erro na comparação: {e}"
    
    def verify_all_packages(self) -> Dict:
        """Verifica todas as dependências"""
        results = {
            'critical': {},
            'high': {},
            'medium': {},
            'summary': {
                'total': 0,
                'updated': 0,
                'outdated': 0,
                'not_installed': 0,
                'errors': 0
            }
        }
        
        # Categorias de vulnerabilidades
        critical_packages = ['werkzeug', 'jinja2', 'pillow', 'cryptography', 'requests', 'beautifulsoup4', 'lxml', 'PyYAML']
        high_packages = ['flask', 'fastapi', 'pandas', 'numpy', 'scikit-learn']
        medium_packages = ['redis', 'celery', 'aiohttp', 'httpx', 'spacy', 'sentence-transformers', 'boto3']
        
        all_packages = critical_packages + high_packages + medium_packages
        
        for package in all_packages:
            current_version = self.get_installed_version(package)
            expected_version = self.secure_versions.get(package, "N/A")
            
            is_updated, status = self.compare_versions(current_version, expected_version)
            
            package_info = {
                'current_version': current_version,
                'expected_version': expected_version,
                'is_updated': is_updated,
                'status': status
            }
            
            # Categorizar resultado
            if package in critical_packages:
                results['critical'][package] = package_info
            elif package in high_packages:
                results['high'][package] = package_info
            elif package in medium_packages:
                results['medium'][package] = package_info
            
            # Atualizar resumo
            results['summary']['total'] += 1
            if is_updated:
                results['summary']['updated'] += 1
            elif current_version == "NÃO INSTALADO":
                results['summary']['not_installed'] += 1
            elif current_version == "ERRO":
                results['summary']['errors'] += 1
            else:
                results['summary']['outdated'] += 1
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Gera relatório de verificação"""
        report = f"""
# 🔍 RELATÓRIO DE VERIFICAÇÃO DE VERSÕES

**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: {'✅ TODAS ATUALIZADAS' if results['summary']['outdated'] == 0 else '⚠️ ATUALIZAÇÕES NECESSÁRIAS'}

## 📊 RESUMO
- **Total de Pacotes**: {results['summary']['total']}
- **Atualizados**: {results['summary']['updated']} ✅
- **Desatualizados**: {results['summary']['outdated']} ❌
- **Não Instalados**: {results['summary']['not_installed']} ⚠️
- **Erros**: {results['summary']['errors']} 🚨

## 🔴 VULNERABILIDADES CRÍTICAS
"""
        
        for package, info in results['critical'].items():
            status_icon = "✅" if info['is_updated'] else "❌"
            report += f"- {status_icon} **{package}**: {info['current_version']} → {info['expected_version']} ({info['status']})\n"
        
        report += """
## 🟡 VULNERABILIDADES ALTAS
"""
        
        for package, info in results['high'].items():
            status_icon = "✅" if info['is_updated'] else "❌"
            report += f"- {status_icon} **{package}**: {info['current_version']} → {info['expected_version']} ({info['status']})\n"
        
        report += """
## 🟢 VULNERABILIDADES MÉDIAS
"""
        
        for package, info in results['medium'].items():
            status_icon = "✅" if info['is_updated'] else "❌"
            report += f"- {status_icon} **{package}**: {info['current_version']} → {info['expected_version']} ({info['status']})\n"
        
        # Comandos de atualização
        outdated_critical = [pkg for pkg, info in results['critical'].items() if not info['is_updated']]
        outdated_high = [pkg for pkg, info in results['high'].items() if not info['is_updated']]
        outdated_medium = [pkg for pkg, info in results['medium'].items() if not info['is_updated']]
        
        if outdated_critical or outdated_high or outdated_medium:
            report += """
## 🚀 COMANDOS DE ATUALIZAÇÃO NECESSÁRIOS
"""
            
            if outdated_critical:
                report += f"### Críticas:\n```bash\npip install --upgrade {' '.join(outdated_critical)}\n```\n"
            
            if outdated_high:
                report += f"### Altas:\n```bash\npip install --upgrade {' '.join(outdated_high)}\n```\n"
            
            if outdated_medium:
                report += f"### Médias:\n```bash\npip install --upgrade {' '.join(outdated_medium)}\n```\n"
        
        report += f"""
## 📈 SCORE DE SEGURANÇA
- **Score Atual**: {(results['summary']['updated'] / results['summary']['total'] * 10):.1f}/10
- **Status**: {'✅ SEGURO' if results['summary']['outdated'] == 0 else '⚠️ ATUALIZAÇÃO NECESSÁRIA'}

---
**Relatório gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
        
        return report
    
    def save_results(self, results: Dict, report: str):
        """Salva resultados em arquivos"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salvar JSON
        json_file = self.project_root / f"version_check_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Salvar relatório
        report_file = self.project_root / f"version_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Resultados salvos em: {json_file}")
        logger.info(f"Relatório salvo em: {report_file}")
        
        return json_file, report_file
    
    def run_verification(self) -> bool:
        """Executa verificação completa"""
        logger.info("🔍 Iniciando verificação de versões...")
        
        try:
            # Verificar todas as dependências
            results = self.verify_all_packages()
            
            # Gerar relatório
            report = self.generate_report(results)
            
            # Salvar resultados
            json_file, report_file = self.save_results(results, report)
            
            # Exibir relatório
            print(report)
            
            # Retornar sucesso se todas estiverem atualizadas
            success = results['summary']['outdated'] == 0
            
            if success:
                logger.info("✅ Todas as dependências estão atualizadas!")
            else:
                logger.warning(f"⚠️ {results['summary']['outdated']} dependências precisam ser atualizadas")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro durante verificação: {e}")
            return False

def main():
    """Função principal"""
    verifier = VersionVerifier()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        # Modo JSON apenas
        results = verifier.verify_all_packages()
        print(json.dumps(results, indent=2))
    else:
        # Modo completo
        success = verifier.run_verification()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 