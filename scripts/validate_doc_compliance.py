#!/usr/bin/env python3
"""
🔍 Documentação Compliance Validator Script
🎯 Objetivo: Validar conformidade de documentação enterprise
📊 Tracing ID: DOC_COMPLIANCE_VALIDATOR_20250127_001
📅 Data: 2025-01-27
🔧 Status: Implementação Inicial
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import traceback
from dataclasses import dataclass, asdict

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.doc_generation_metrics import DocGenerationMetrics, MetricsCollector, MetricsAnalyzer
from infrastructure.validation.doc_quality_score import DocQualityAnalyzer
from infrastructure.security.advanced_security_system import SensitiveDataDetector
from shared.trigger_config_validator import TriggerConfigValidator
from infrastructure.ml.semantic_embeddings import SemanticEmbeddingService
from shared.compliance_validator import ComplianceValidator
from infrastructure.backup.rollback_system import RollbackSystem


@dataclass
class ComplianceReport:
    """Relatório de conformidade de documentação"""
    timestamp: str
    tracing_id: str
    overall_score: float
    quality_score: float
    security_score: float
    compliance_score: float
    performance_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    status: str  # PASS, FAIL, WARNING


class DocComplianceValidator:
    """
    Validador principal de conformidade de documentação enterprise
    """
    
    def __init__(self, config_path: str = "docs/trigger_config.json"):
        self.tracing_id = f"DOC_COMPLIANCE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config_path = config_path
        self.setup_logging()
        
        # Inicializar serviços
        self.quality_analyzer = DocQualityAnalyzer()
        self.security_detector = SensitiveDataDetector()
        self.metrics_collector = MetricsCollector()
        self.trigger_validator = TriggerConfigValidator()
        self.compliance_validator = ComplianceValidator()
        self.rollback_system = RollbackSystem()
        self.semantic_service = SemanticEmbeddingService()
        
        # Configurações
        self.quality_threshold = 0.85
        self.security_threshold = 1.0  # Zero tolerância
        self.compliance_threshold = 0.90
        self.performance_threshold = 0.80
        
        self.logger.info(f"[{self.tracing_id}] Inicializado validador de conformidade")
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        self.logger = logging.getLogger(f"DocComplianceValidator_{self.tracing_id}")
        self.logger.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '[%(levelname)string_data] [%(name)string_data] %(message)string_data - %(asctime)string_data'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def validate_quality(self, docs_path: str = "docs/") -> Tuple[float, List[Dict]]:
        """
        Validar qualidade da documentação
        """
        self.logger.info(f"[{self.tracing_id}] Iniciando validação de qualidade")
        
        issues = []
        total_score = 0.0
        doc_count = 0
        
        docs_dir = Path(docs_path)
        if not docs_dir.exists():
            issues.append({
                "type": "CRITICAL",
                "message": f"Diretório de documentação não encontrado: {docs_path}",
                "file": docs_path
            })
            return 0.0, issues
        
        # Analisar cada arquivo de documentação
        for doc_file in docs_dir.rglob("*.md"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Calcular qualidade
                quality_score = self.quality_analyzer.calculate_doc_quality_score(content)
                total_score += quality_score
                doc_count += 1
                
                if quality_score < self.quality_threshold:
                    issues.append({
                        "type": "WARNING",
                        "message": f"Qualidade abaixo do threshold: {quality_score:.2f}",
                        "file": str(doc_file),
                        "score": quality_score,
                        "threshold": self.quality_threshold
                    })
                
                self.logger.info(f"[{self.tracing_id}] {doc_file}: {quality_score:.2f}")
                
            except Exception as e:
                issues.append({
                    "type": "ERROR",
                    "message": f"Erro ao analisar arquivo: {str(e)}",
                    "file": str(doc_file)
                })
        
        avg_quality = total_score / doc_count if doc_count > 0 else 0.0
        self.logger.info(f"[{self.tracing_id}] Qualidade média: {avg_quality:.2f}")
        
        return avg_quality, issues
    
    def validate_security(self, docs_path: str = "docs/") -> Tuple[float, List[Dict]]:
        """
        Validar segurança da documentação
        """
        self.logger.info(f"[{self.tracing_id}] Iniciando validação de segurança")
        
        issues = []
        security_score = 1.0  # Começa com score perfeito
        
        docs_dir = Path(docs_path)
        if not docs_dir.exists():
            return 0.0, issues
        
        # Escanear documentação
        for doc_file in docs_dir.rglob("*.md"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detectar dados sensíveis
                sensitive_data = self.security_detector.scan_documentation(content)
                
                if sensitive_data:
                    security_score = 0.0  # Falha crítica
                    for data in sensitive_data:
                        issues.append({
                            "type": "CRITICAL",
                            "message": f"Dados sensíveis detectados: {data['type']}",
                            "file": str(doc_file),
                            "line": data.get('line', 'N/A'),
                            "pattern": data.get('pattern', 'N/A')
                        })
                
            except Exception as e:
                issues.append({
                    "type": "ERROR",
                    "message": f"Erro ao escanear arquivo: {str(e)}",
                    "file": str(doc_file)
                })
        
        self.logger.info(f"[{self.tracing_id}] Score de segurança: {security_score:.2f}")
        return security_score, issues
    
    def validate_compliance(self) -> Tuple[float, List[Dict]]:
        """
        Validar compliance (PCI-DSS, LGPD, etc.)
        """
        self.logger.info(f"[{self.tracing_id}] Iniciando validação de compliance")
        
        issues = []
        
        try:
            # Validar configurações de compliance
            compliance_result = self.compliance_validator.validate_all_standards()
            compliance_score = compliance_result.get('overall_score', 0.0)
            
            # Verificar violações
            violations = compliance_result.get('violations', [])
            for violation in violations:
                issues.append({
                    "type": "WARNING" if violation['severity'] == 'medium' else "CRITICAL",
                    "message": f"Violation de compliance: {violation['description']}",
                    "standard": violation.get('standard', 'N/A'),
                    "severity": violation.get('severity', 'unknown')
                })
            
            self.logger.info(f"[{self.tracing_id}] Score de compliance: {compliance_score:.2f}")
            return compliance_score, issues
            
        except Exception as e:
            issues.append({
                "type": "ERROR",
                "message": f"Erro na validação de compliance: {str(e)}"
            })
            return 0.0, issues
    
    def validate_performance(self) -> Tuple[float, List[Dict]]:
        """
        Validar métricas de performance
        """
        self.logger.info(f"[{self.tracing_id}] Iniciando validação de performance")
        
        issues = []
        performance_score = 1.0
        
        try:
            # Coletar métricas
            metrics = self.metrics_collector.collect_all_metrics()
            
            # Validar tempo de geração (< 5 minutos)
            generation_time = metrics.get('avg_generation_time', 0)
            if generation_time > 300:  # 5 minutos
                performance_score -= 0.2
                issues.append({
                    "type": "WARNING",
                    "message": f"Tempo de geração alto: {generation_time:.2f}string_data",
                    "threshold": 300
                })
            
            # Validar tokens consumidos (< 10.000)
            tokens_used = metrics.get('avg_tokens_used', 0)
            if tokens_used > 10000:
                performance_score -= 0.2
                issues.append({
                    "type": "WARNING",
                    "message": f"Tokens consumidos alto: {tokens_used}",
                    "threshold": 10000
                })
            
            # Validar cobertura de documentação (> 95%)
            doc_coverage = metrics.get('documentation_coverage', 0)
            if doc_coverage < 0.95:
                performance_score -= 0.3
                issues.append({
                    "type": "WARNING",
                    "message": f"Cobertura de documentação baixa: {doc_coverage:.2%}",
                    "threshold": "95%"
                })
            
            # Garantir score mínimo
            performance_score = max(0.0, performance_score)
            
            self.logger.info(f"[{self.tracing_id}] Score de performance: {performance_score:.2f}")
            return performance_score, issues
            
        except Exception as e:
            issues.append({
                "type": "ERROR",
                "message": f"Erro na validação de performance: {str(e)}"
            })
            return 0.0, issues
    
    def validate_trigger_config(self) -> Tuple[float, List[Dict]]:
        """
        Validar configuração de triggers
        """
        self.logger.info(f"[{self.tracing_id}] Iniciando validação de trigger config")
        
        issues = []
        config_score = 1.0
        
        try:
            # Validar arquivo de configuração
            validation_result = self.trigger_validator.validate_config_file(self.config_path)
            
            if not validation_result['is_valid']:
                config_score = 0.0
                for error in validation_result.get('errors', []):
                    issues.append({
                        "type": "CRITICAL",
                        "message": f"Erro na configuração: {error}",
                        "config_file": self.config_path
                    })
            
            self.logger.info(f"[{self.tracing_id}] Score de configuração: {config_score:.2f}")
            return config_score, issues
            
        except Exception as e:
            issues.append({
                "type": "ERROR",
                "message": f"Erro na validação de configuração: {str(e)}"
            })
            return 0.0, issues
    
    def generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """
        Gerar recomendações baseadas nos problemas encontrados
        """
        recommendations = []
        
        # Agrupar por tipo
        critical_issues = [index for index in issues if index['type'] == 'CRITICAL']
        warning_issues = [index for index in issues if index['type'] == 'WARNING']
        
        if critical_issues:
            recommendations.append("🔴 CRÍTICO: Corrija imediatamente os problemas de segurança e compliance")
        
        if warning_issues:
            recommendations.append("🟡 ATENÇÃO: Melhore a qualidade e performance da documentação")
        
        # Recomendações específicas
        for issue in issues:
            if "dados sensíveis" in issue.get('message', '').lower():
                recommendations.append("🔐 Remova dados sensíveis da documentação")
            
            if "qualidade" in issue.get('message', '').lower():
                recommendations.append("📝 Melhore a qualidade da documentação")
            
            if "performance" in issue.get('message', '').lower():
                recommendations.append("⚡ Otimize a performance da geração de documentação")
        
        return list(set(recommendations))  # Remover duplicatas
    
    def determine_status(self, scores: Dict[str, float]) -> str:
        """
        Determinar status geral baseado nos scores
        """
        if scores['security'] < self.security_threshold:
            return "FAIL"  # Falha crítica de segurança
        
        if scores['compliance'] < self.compliance_threshold:
            return "FAIL"  # Falha de compliance
        
        if scores['quality'] < self.quality_threshold:
            return "WARNING"  # Aviso de qualidade
        
        if scores['performance'] < self.performance_threshold:
            return "WARNING"  # Aviso de performance
        
        return "PASS"  # Tudo OK
    
    def run_validation(self, docs_path: str = "docs/") -> ComplianceReport:
        """
        Executar validação completa
        """
        self.logger.info(f"[{self.tracing_id}] Iniciando validação completa")
        
        start_time = datetime.now()
        
        # Executar todas as validações
        quality_score, quality_issues = self.validate_quality(docs_path)
        security_score, security_issues = self.validate_security(docs_path)
        compliance_score, compliance_issues = self.validate_compliance()
        performance_score, performance_issues = self.validate_performance()
        config_score, config_issues = self.validate_trigger_config()
        
        # Consolidar issues
        all_issues = quality_issues + security_issues + compliance_issues + performance_issues + config_issues
        
        # Calcular score geral (média ponderada)
        scores = {
            'quality': quality_score,
            'security': security_score,
            'compliance': compliance_score,
            'performance': performance_score,
            'config': config_score
        }
        
        overall_score = (
            quality_score * 0.3 +
            security_score * 0.3 +
            compliance_score * 0.25 +
            performance_score * 0.1 +
            config_score * 0.05
        )
        
        # Determinar status
        status = self.determine_status(scores)
        
        # Gerar recomendações
        recommendations = self.generate_recommendations(all_issues)
        
        # Criar relatório
        report = ComplianceReport(
            timestamp=datetime.now().isoformat(),
            tracing_id=self.tracing_id,
            overall_score=overall_score,
            quality_score=quality_score,
            security_score=security_score,
            compliance_score=compliance_score,
            performance_score=performance_score,
            issues=all_issues,
            recommendations=recommendations,
            status=status
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.logger.info(f"[{self.tracing_id}] Validação concluída em {duration:.2f}string_data")
        self.logger.info(f"[{self.tracing_id}] Status: {status}")
        self.logger.info(f"[{self.tracing_id}] Score geral: {overall_score:.2f}")
        
        return report
    
    def save_report(self, report: ComplianceReport, output_path: str = "logs/compliance_report.json"):
        """
        Salvar relatório em arquivo JSON
        """
        try:
            # Criar diretório se não existir
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Converter para dict
            report_dict = asdict(report)
            
            # Salvar arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"[{self.tracing_id}] Relatório salvo em: {output_path}")
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao salvar relatório: {str(e)}")
    
    def print_summary(self, report: ComplianceReport):
        """
        Imprimir resumo do relatório
        """
        print("\n" + "="*80)
        print("📋 RELATÓRIO DE CONFORMIDADE DE DOCUMENTAÇÃO ENTERPRISE")
        print("="*80)
        print(f"Tracing ID: {report.tracing_id}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Status: {report.status}")
        print(f"Score Geral: {report.overall_score:.2f}")
        print("-"*80)
        print("📊 SCORES DETALHADOS:")
        print(f"  Qualidade: {report.quality_score:.2f}")
        print(f"  Segurança: {report.security_score:.2f}")
        print(f"  Compliance: {report.compliance_score:.2f}")
        print(f"  Performance: {report.performance_score:.2f}")
        print("-"*80)
        
        if report.issues:
            print("🚨 PROBLEMAS ENCONTRADOS:")
            for index, issue in enumerate(report.issues, 1):
                print(f"  {index}. [{issue['type']}] {issue['message']}")
                if 'file' in issue:
                    print(f"     Arquivo: {issue['file']}")
        else:
            print("✅ Nenhum problema encontrado!")
        
        if report.recommendations:
            print("-"*80)
            print("💡 RECOMENDAÇÕES:")
            for index, rec in enumerate(report.recommendations, 1):
                print(f"  {index}. {rec}")
        
        print("="*80)


def main():
    """
    Função principal do script
    """
    parser = argparse.ArgumentParser(
        description="Validador de Conformidade de Documentação Enterprise"
    )
    parser.add_argument(
        "--docs-path",
        default="docs/",
        help="Caminho para a documentação (padrão: docs/)"
    )
    parser.add_argument(
        "--config-path",
        default="docs/trigger_config.json",
        help="Caminho para configuração de triggers (padrão: docs/trigger_config.json)"
    )
    parser.add_argument(
        "--output",
        default="logs/compliance_report.json",
        help="Caminho para salvar relatório (padrão: logs/compliance_report.json)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verbose com logs detalhados"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Criar validador
        validator = DocComplianceValidator(args.config_path)
        
        # Executar validação
        report = validator.run_validation(args.docs_path)
        
        # Salvar relatório
        validator.save_report(report, args.output)
        
        # Imprimir resumo
        validator.print_summary(report)
        
        # Retornar código de saída baseado no status
        if report.status == "FAIL":
            sys.exit(1)
        elif report.status == "WARNING":
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 