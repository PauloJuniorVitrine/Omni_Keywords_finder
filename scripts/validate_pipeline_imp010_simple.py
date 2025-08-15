#!/usr/bin/env python3
"""
📋 IMP-010: Validação Simplificada do Pipeline CI/CD
🎯 Objetivo: Validar componentes principais do pipeline robusto
📅 Criado: 2024-12-27
🔄 Versão: 1.0
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

class SimplePipelineValidator:
    """Validador simplificado do pipeline CI/CD."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'PENDING',
            'checks': {},
            'metrics': {},
            'recommendations': []
        }
        
    def validate_github_workflows(self) -> Dict:
        """Validar workflows do GitHub Actions."""
        print("🔍 Validando GitHub Workflows...")
        
        workflows = [
            '.github/workflows/ci-robust.yml',
            '.github/workflows/cd-robust.yml',
            '.github/workflows/cd-staging.yml',
            '.github/workflows/cd-production.yml',
            '.github/workflows/frontend-ci.yml',
            '.github/workflows/security-advanced.yml'
        ]
        
        results = {
            'status': 'PASS',
            'workflows_found': 0,
            'workflows_valid': 0,
            'issues': []
        }
        
        for workflow in workflows:
            if os.path.exists(workflow):
                results['workflows_found'] += 1
                
                try:
                    with open(workflow, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Verificações básicas
                    checks = [
                        ('name:', 'Nome do workflow'),
                        ('on:', 'Triggers'),
                        ('jobs:', 'Jobs definidos'),
                        ('runs-on:', 'Runner especificado'),
                        ('steps:', 'Steps definidos')
                    ]
                    
                    workflow_valid = True
                    for check, description in checks:
                        if check not in content:
                            results['issues'].append(f"{workflow}: {description} ausente")
                            workflow_valid = False
                    
                    if workflow_valid:
                        results['workflows_valid'] += 1
                        
                except Exception as e:
                    results['issues'].append(f"{workflow}: Erro ao ler arquivo - {str(e)}")
                    results['status'] = 'FAIL'
            else:
                results['issues'].append(f"Workflow não encontrado: {workflow}")
                results['status'] = 'FAIL'
        
        if results['workflows_found'] == 0:
            results['status'] = 'FAIL'
            results['issues'].append("Nenhum workflow encontrado")
        
        print(f"✅ Workflows: {results['workflows_valid']}/{results['workflows_found']} válidos")
        return results
    
    def validate_docker_configuration(self) -> Dict:
        """Validar configuração Docker."""
        print("🐳 Validando configuração Docker...")
        
        results = {
            'status': 'PASS',
            'files_found': 0,
            'files_valid': 0,
            'issues': []
        }
        
        docker_files = [
            'Dockerfile',
            'docker-compose.yml',
            'docker-compose.observability.yml'
        ]
        
        for docker_file in docker_files:
            if os.path.exists(docker_file):
                results['files_found'] += 1
                
                try:
                    with open(docker_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificações específicas por tipo
                    if docker_file == 'Dockerfile':
                        checks = [
                            ('FROM', 'Imagem base'),
                            ('WORKDIR', 'Diretório de trabalho'),
                            ('COPY', 'Cópia de arquivos'),
                            ('EXPOSE', 'Porta exposta'),
                            ('CMD', 'Comando padrão')
                        ]
                    elif 'docker-compose' in docker_file:
                        checks = [
                            ('version:', 'Versão do compose'),
                            ('services:', 'Serviços definidos'),
                            ('networks:', 'Redes definidas')
                        ]
                    
                    file_valid = True
                    for check, description in checks:
                        if check not in content:
                            results['issues'].append(f"{docker_file}: {description} ausente")
                            file_valid = False
                    
                    if file_valid:
                        results['files_valid'] += 1
                        
                except Exception as e:
                    results['issues'].append(f"{docker_file}: Erro ao ler arquivo - {str(e)}")
                    results['status'] = 'FAIL'
            else:
                results['issues'].append(f"Arquivo Docker não encontrado: {docker_file}")
                results['status'] = 'FAIL'
        
        print(f"✅ Docker: {results['files_valid']}/{results['files_found']} arquivos válidos")
        return results
    
    def validate_kubernetes_configuration(self) -> Dict:
        """Validar configuração Kubernetes."""
        print("☸️ Validando configuração Kubernetes...")
        
        results = {
            'status': 'PASS',
            'files_found': 0,
            'files_valid': 0,
            'issues': []
        }
        
        # Verificar se existe diretório k8s
        k8s_dir = 'k8s'
        if not os.path.exists(k8s_dir):
            results['status'] = 'FAIL'
            results['issues'].append("Diretório k8s não encontrado")
            return results
        
        # Verificar arquivos importantes
        k8s_files = [
            'k8s/base/namespace.yaml',
            'k8s/base/deployment.yaml',
            'k8s/base/service.yaml',
            'k8s/base/configmap.yaml',
            'k8s/base/secrets.yaml',
            'k8s/base/ingress.yaml'
        ]
        
        for k8s_file in k8s_files:
            if os.path.exists(k8s_file):
                results['files_found'] += 1
                
                try:
                    with open(k8s_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificações básicas de YAML
                    checks = [
                        ('apiVersion:', 'API Version'),
                        ('kind:', 'Tipo de recurso'),
                        ('metadata:', 'Metadados'),
                        ('spec:', 'Especificação')
                    ]
                    
                    file_valid = True
                    for check, description in checks:
                        if check not in content:
                            results['issues'].append(f"{k8s_file}: {description} ausente")
                            file_valid = False
                    
                    if file_valid:
                        results['files_valid'] += 1
                        
                except Exception as e:
                    results['issues'].append(f"{k8s_file}: Erro ao ler arquivo - {str(e)}")
                    results['status'] = 'FAIL'
            else:
                results['issues'].append(f"Arquivo K8s não encontrado: {k8s_file}")
                results['status'] = 'FAIL'
        
        print(f"✅ Kubernetes: {results['files_valid']}/{results['files_found']} arquivos válidos")
        return results
    
    def validate_terraform_configuration(self) -> Dict:
        """Validar configuração Terraform."""
        print("🏗️ Validando configuração Terraform...")
        
        results = {
            'status': 'PASS',
            'files_found': 0,
            'files_valid': 0,
            'issues': []
        }
        
        terraform_files = [
            'terraform/main.tf',
            'terraform/variables.tf',
            'terraform/outputs.tf',
            'terraform/iam.tf'
        ]
        
        for tf_file in terraform_files:
            if os.path.exists(tf_file):
                results['files_found'] += 1
                
                try:
                    with open(tf_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificações básicas
                    checks = [
                        ('terraform', 'Bloco terraform'),
                        ('provider', 'Provider definido'),
                        ('resource', 'Recursos definidos')
                    ]
                    
                    file_valid = True
                    for check, description in checks:
                        if check not in content:
                            results['issues'].append(f"{tf_file}: {description} ausente")
                            file_valid = False
                    
                    if file_valid:
                        results['files_valid'] += 1
                        
                except Exception as e:
                    results['issues'].append(f"{tf_file}: Erro ao ler arquivo - {str(e)}")
                    results['status'] = 'FAIL'
            else:
                results['issues'].append(f"Arquivo Terraform não encontrado: {tf_file}")
                results['status'] = 'FAIL'
        
        print(f"✅ Terraform: {results['files_valid']}/{results['files_found']} arquivos válidos")
        return results
    
    def validate_monitoring_configuration(self) -> Dict:
        """Validar configuração de monitoramento."""
        print("📊 Validando configuração de monitoramento...")
        
        results = {
            'status': 'PASS',
            'components_found': 0,
            'components_valid': 0,
            'issues': []
        }
        
        monitoring_components = [
            'config/telemetry/prometheus.yml',
            'config/telemetry/grafana/',
            'config/telemetry/alertmanager.yml',
            'config/telemetry/promtail.yml'
        ]
        
        for component in monitoring_components:
            if os.path.exists(component):
                results['components_found'] += 1
                
                try:
                    if os.path.isfile(component):
                        with open(component, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Verificações específicas
                        if 'prometheus' in component:
                            checks = ['global:', 'scrape_configs:']
                        elif 'alertmanager' in component:
                            checks = ['global:', 'route:', 'receivers:']
                        else:
                            checks = ['config:', 'settings:']
                        
                        component_valid = True
                        for check in checks:
                            if check not in content:
                                results['issues'].append(f"{component}: Configuração {check} ausente")
                                component_valid = False
                        
                        if component_valid:
                            results['components_valid'] += 1
                    else:
                        # É um diretório
                        results['components_valid'] += 1
                        
                except Exception as e:
                    results['issues'].append(f"{component}: Erro ao ler arquivo - {str(e)}")
                    results['status'] = 'FAIL'
            else:
                results['issues'].append(f"Componente de monitoramento não encontrado: {component}")
                results['status'] = 'FAIL'
        
        print(f"✅ Monitoramento: {results['components_valid']}/{results['components_found']} componentes válidos")
        return results
    
    def validate_security_configuration(self) -> Dict:
        """Validar configuração de segurança."""
        print("🔒 Validando configuração de segurança...")
        
        results = {
            'status': 'PASS',
            'security_files_found': 0,
            'security_files_valid': 0,
            'issues': []
        }
        
        security_files = [
            '.github/workflows/security-advanced.yml',
            'infrastructure/security/',
            'scripts/security_scan.py'
        ]
        
        for security_file in security_files:
            if os.path.exists(security_file):
                results['security_files_found'] += 1
                
                try:
                    if os.path.isfile(security_file):
                        with open(security_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Verificações de segurança
                        security_checks = [
                            ('bandit', 'Análise de segurança Python'),
                            ('trivy', 'Scan de vulnerabilidades'),
                            ('safety', 'Verificação de dependências')
                        ]
                        
                        file_valid = True
                        for check, description in security_checks:
                            if check in content:
                                file_valid = True
                                break
                        
                        if file_valid:
                            results['security_files_valid'] += 1
                        else:
                            results['issues'].append(f"{security_file}: Ferramentas de segurança não encontradas")
                    else:
                        # É um diretório
                        results['security_files_valid'] += 1
                        
                except Exception as e:
                    results['issues'].append(f"{security_file}: Erro ao ler arquivo - {str(e)}")
                    results['status'] = 'FAIL'
            else:
                results['issues'].append(f"Arquivo de segurança não encontrado: {security_file}")
                results['status'] = 'FAIL'
        
        print(f"✅ Segurança: {results['security_files_valid']}/{results['security_files_found']} arquivos válidos")
        return results
    
    def validate_documentation(self) -> Dict:
        """Validar documentação do pipeline."""
        print("📚 Validando documentação...")
        
        results = {
            'status': 'PASS',
            'docs_found': 0,
            'docs_valid': 0,
            'issues': []
        }
        
        documentation_files = [
            'docs/IMP010_GUIA_DEPLOY_COMPLETO.md',
            'docs/cicd_architecture.md',
            'docs/DEPLOY_PRACTICES.md',
            'docs/monitoring.md',
            'README.md'
        ]
        
        for doc_file in documentation_files:
            if os.path.exists(doc_file):
                results['docs_found'] += 1
                
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificações de documentação
                    doc_checks = [
                        ('#', 'Títulos'),
                        ('##', 'Seções'),
                        ('```', 'Blocos de código'),
                        ('-', 'Listas')
                    ]
                    
                    file_valid = True
                    for check, description in doc_checks:
                        if check not in content:
                            results['issues'].append(f"{doc_file}: {description} ausente")
                            file_valid = False
                    
                    if file_valid:
                        results['docs_valid'] += 1
                        
                except Exception as e:
                    results['issues'].append(f"{doc_file}: Erro ao ler arquivo - {str(e)}")
                    results['status'] = 'FAIL'
            else:
                results['issues'].append(f"Documentação não encontrada: {doc_file}")
                results['status'] = 'FAIL'
        
        print(f"✅ Documentação: {results['docs_valid']}/{results['docs_found']} arquivos válidos")
        return results
    
    def calculate_metrics(self) -> Dict:
        """Calcular métricas do pipeline."""
        print("📈 Calculando métricas...")
        
        metrics = {
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'coverage_percentage': 0.0,
            'build_time_target': '< 10 min',
            'deploy_time_target': '< 5 min',
            'rollback_time_target': '< 2 min'
        }
        
        for check_name, check_result in self.results['checks'].items():
            metrics['total_checks'] += 1
            if check_result['status'] == 'PASS':
                metrics['passed_checks'] += 1
            else:
                metrics['failed_checks'] += 1
        
        if metrics['total_checks'] > 0:
            metrics['coverage_percentage'] = (metrics['passed_checks'] / metrics['total_checks']) * 100
        
        return metrics
    
    def generate_recommendations(self) -> List[str]:
        """Gerar recomendações baseadas nos resultados."""
        recommendations = []
        
        # Análise dos resultados
        failed_checks = [name for name, result in self.results['checks'].items() 
                        if result['status'] == 'FAIL']
        
        if failed_checks:
            recommendations.append(f"❌ Corrigir {len(failed_checks)} verificações falhadas: {', '.join(failed_checks)}")
        
        # Verificações específicas
        if 'github_workflows' in self.results['checks']:
            workflow_result = self.results['checks']['github_workflows']
            if workflow_result['workflows_found'] < 6:
                recommendations.append("📋 Adicionar workflows GitHub Actions faltantes")
        
        if 'docker_configuration' in self.results['checks']:
            docker_result = self.results['checks']['docker_configuration']
            if docker_result['files_found'] < 3:
                recommendations.append("🐳 Completar configuração Docker")
        
        if 'kubernetes_configuration' in self.results['checks']:
            k8s_result = self.results['checks']['kubernetes_configuration']
            if k8s_result['files_found'] < 6:
                recommendations.append("☸️ Completar configuração Kubernetes")
        
        # Recomendações gerais
        if not recommendations:
            recommendations.append("✅ Pipeline CI/CD está bem configurado")
            recommendations.append("🚀 Pronto para deploy em produção")
        
        return recommendations
    
    def run_validation(self) -> Dict:
        """Executar validação completa do pipeline."""
        print("🚀 Iniciando validação completa do pipeline CI/CD...")
        
        # Executar todas as validações
        self.results['checks'] = {
            'github_workflows': self.validate_github_workflows(),
            'docker_configuration': self.validate_docker_configuration(),
            'kubernetes_configuration': self.validate_kubernetes_configuration(),
            'terraform_configuration': self.validate_terraform_configuration(),
            'monitoring_configuration': self.validate_monitoring_configuration(),
            'security_configuration': self.validate_security_configuration(),
            'documentation': self.validate_documentation()
        }
        
        # Calcular métricas
        self.results['metrics'] = self.calculate_metrics()
        
        # Gerar recomendações
        self.results['recommendations'] = self.generate_recommendations()
        
        # Determinar status geral
        failed_checks = [result for result in self.results['checks'].values() 
                        if result['status'] == 'FAIL']
        
        if failed_checks:
            self.results['overall_status'] = 'FAIL'
        else:
            self.results['overall_status'] = 'PASS'
        
        print(f"✅ Validação concluída. Status: {self.results['overall_status']}")
        return self.results
    
    def save_results(self, filename: str = 'pipeline_validation_results.json'):
        """Salvar resultados da validação."""
        os.makedirs('logs', exist_ok=True)
        
        with open(f'logs/{filename}', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Resultados salvos em logs/{filename}")
    
    def print_summary(self):
        """Imprimir resumo da validação."""
        print("\n" + "="*80)
        print("📋 RESUMO DA VALIDAÇÃO DO PIPELINE CI/CD - IMP-010")
        print("="*80)
        
        print(f"\n🕒 Timestamp: {self.results['timestamp']}")
        print(f"📊 Status Geral: {self.results['overall_status']}")
        
        print(f"\n📈 Métricas:")
        metrics = self.results['metrics']
        print(f"   • Total de verificações: {metrics['total_checks']}")
        print(f"   • Verificações aprovadas: {metrics['passed_checks']}")
        print(f"   • Verificações falhadas: {metrics['failed_checks']}")
        print(f"   • Cobertura: {metrics['coverage_percentage']:.1f}%")
        
        print(f"\n🔍 Detalhes por Componente:")
        for check_name, check_result in self.results['checks'].items():
            status_emoji = "✅" if check_result['status'] == 'PASS' else "❌"
            print(f"   {status_emoji} {check_name.replace('_', ' ').title()}: {check_result['status']}")
            
            if check_result['issues']:
                for issue in check_result['issues'][:3]:  # Mostrar apenas 3 primeiros
                    print(f"      ⚠️  {issue}")
                if len(check_result['issues']) > 3:
                    print(f"      ... e mais {len(check_result['issues']) - 3} issues")
        
        print(f"\n💡 Recomendações:")
        for recommendation in self.results['recommendations']:
            print(f"   {recommendation}")
        
        print("\n" + "="*80)

def main():
    """Função principal."""
    print("🚀 IMP-010: Validação Completa do Pipeline CI/CD")
    print("="*60)
    
    # Criar validador
    validator = SimplePipelineValidator()
    
    try:
        # Executar validação
        results = validator.run_validation()
        
        # Salvar resultados
        validator.save_results()
        
        # Imprimir resumo
        validator.print_summary()
        
        # Retornar código de saída
        if results['overall_status'] == 'PASS':
            print("\n🎉 Pipeline CI/CD validado com sucesso!")
            sys.exit(0)
        else:
            print("\n⚠️  Pipeline CI/CD precisa de ajustes.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Erro durante validação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 