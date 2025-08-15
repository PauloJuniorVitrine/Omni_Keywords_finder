#!/usr/bin/env python3
"""
Script Principal de Geração de Documentação Enterprise
Tracing ID: GENERATE_ENTERPRISE_DOCS_20250127_001
Data: 2025-01-27
Versão: 1.0

Objetivo: Orquestrar geração completa de documentação enterprise,
integrando todos os sistemas de qualidade, segurança, compliance
e métricas em um pipeline automatizado.
"""

import os
import sys
import json
import logging
import argparse
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from infrastructure.ml.semantic_embeddings import SemanticEmbeddingService
    from infrastructure.validation.doc_quality_score import DocQualityAnalyzer
    from infrastructure.security.advanced_security_system import SensitiveDataDetector
    from infrastructure.backup.rollback_system import RollbackSystem
    from shared.doc_generation_metrics import DocGenerationMetrics, MetricsCollector, MetricsAnalyzer
    from shared.semantic_contracts_generator import SemanticContractsGenerator
    from shared.log_analyzer import LogAnalyzer
    from shared.api_docs_generator import APIDocsGenerator
    from shared.trigger_config_validator import TriggerConfigValidator
    from shared.compliance_validator import ComplianceValidator
    from scripts.validate_doc_compliance import DocComplianceValidator
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de que todos os módulos estão implementados")
    sys.exit(1)


@dataclass
class GenerationConfig:
    """Configuração de geração de documentação"""
    docs_path: str = "docs/"
    output_path: str = "docs/enterprise/"
    backup_enabled: bool = True
    quality_threshold: float = 0.85
    security_threshold: float = 1.0
    compliance_threshold: float = 0.90
    max_workers: int = 4
    verbose: bool = False


@dataclass
class GenerationResult:
    """Resultado da geração de documentação"""
    timestamp: str
    tracing_id: str
    success: bool
    duration: float
    files_generated: int
    files_processed: int
    quality_score: float
    security_score: float
    compliance_score: float
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    metrics: Dict[str, Any]


class EnterpriseDocGenerator:
    """
    Gerador principal de documentação enterprise
    """
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.tracing_id = f"ENTERPRISE_DOCS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.setup_logging()
        
        # Inicializar serviços
        self.initialize_services()
        
        # Métricas
        self.metrics_collector = MetricsCollector()
        self.metrics_analyzer = MetricsAnalyzer()
        
        self.logger.info(f"[{self.tracing_id}] Inicializado gerador enterprise")
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        self.logger = logging.getLogger(f"EnterpriseDocGenerator_{self.tracing_id}")
        self.logger.setLevel(logging.DEBUG if self.config.verbose else logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if self.config.verbose else logging.INFO)
        
        # Handler para arquivo
        log_dir = Path("logs/enterprise")
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / f"generation_{self.tracing_id}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Formato
        formatter = logging.Formatter(
            '[%(levelname)string_data] [%(name)string_data] %(message)string_data - %(asctime)string_data'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def initialize_services(self):
        """Inicializar todos os serviços necessários"""
        try:
            self.logger.info(f"[{self.tracing_id}] Inicializando serviços...")
            
            # Serviços de ML e análise
            self.semantic_service = SemanticEmbeddingService()
            self.quality_analyzer = DocQualityAnalyzer()
            self.security_detector = SensitiveDataDetector()
            
            # Sistema de backup e rollback
            self.rollback_system = RollbackSystem()
            
            # Geradores de documentação
            self.contracts_generator = SemanticContractsGenerator()
            self.log_analyzer = LogAnalyzer()
            self.api_docs_generator = APIDocsGenerator()
            
            # Validadores
            self.trigger_validator = TriggerConfigValidator()
            self.compliance_validator = ComplianceValidator()
            self.compliance_checker = DocComplianceValidator()
            
            self.logger.info(f"[{self.tracing_id}] Todos os serviços inicializados")
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro na inicialização: {str(e)}")
            raise
    
    def create_backup(self) -> bool:
        """Criar backup antes da geração"""
        if not self.config.backup_enabled:
            return True
        
        try:
            self.logger.info(f"[{self.tracing_id}] Criando backup...")
            
            # Criar snapshot do estado atual
            snapshot_id = self.rollback_system.create_snapshot(
                description=f"Backup antes da geração {self.tracing_id}"
            )
            
            self.logger.info(f"[{self.tracing_id}] Backup criado: {snapshot_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro no backup: {str(e)}")
            return False
    
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """Validar ambiente antes da geração"""
        errors = []
        
        try:
            self.logger.info(f"[{self.tracing_id}] Validando ambiente...")
            
            # Verificar diretórios
            docs_path = Path(self.config.docs_path)
            if not docs_path.exists():
                docs_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"[{self.tracing_id}] Diretório criado: {docs_path}")
            
            output_path = Path(self.config.output_path)
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"[{self.tracing_id}] Diretório criado: {output_path}")
            
            # Verificar configuração de triggers
            trigger_config_path = "docs/trigger_config.json"
            if not Path(trigger_config_path).exists():
                errors.append(f"Arquivo de configuração não encontrado: {trigger_config_path}")
            
            # Verificar permissões de escrita
            if not os.access(output_path, os.W_OK):
                errors.append(f"Sem permissão de escrita em: {output_path}")
            
            # Verificar serviços
            if not self.semantic_service:
                errors.append("Serviço semântico não inicializado")
            
            if not self.quality_analyzer:
                errors.append("Analisador de qualidade não inicializado")
            
            if len(errors) == 0:
                self.logger.info(f"[{self.tracing_id}] Ambiente validado com sucesso")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Erro na validação: {str(e)}")
            return False, errors
    
    def generate_semantic_contracts(self) -> Tuple[bool, List[Dict]]:
        """Gerar contratos semânticos"""
        try:
            self.logger.info(f"[{self.tracing_id}] Gerando contratos semânticos...")
            
            # Gerar documentação de módulos
            modules_docs = self.contracts_generator.generate_module_docs()
            
            # Gerar documentação de funções
            functions_docs = self.contracts_generator.generate_function_docs()
            
            # Salvar contratos
            contracts_file = Path(self.config.output_path) / "semantic_contracts.md"
            with open(contracts_file, 'w', encoding='utf-8') as f:
                f.write("# Contratos Semânticos\n\n")
                f.write(f"Gerado em: {datetime.now().isoformat()}\n")
                f.write(f"Tracing ID: {self.tracing_id}\n\n")
                
                f.write("## Módulos\n\n")
                for module, doc in modules_docs.items():
                    f.write(f"### {module}\n")
                    f.write(f"{doc}\n\n")
                
                f.write("## Funções\n\n")
                for func, doc in functions_docs.items():
                    f.write(f"### {func}\n")
                    f.write(f"{doc}\n\n")
            
            self.logger.info(f"[{self.tracing_id}] Contratos semânticos gerados: {contracts_file}")
            return True, []
            
        except Exception as e:
            error_msg = f"Erro na geração de contratos: {str(e)}"
            self.logger.error(f"[{self.tracing_id}] {error_msg}")
            return False, [{"type": "ERROR", "message": error_msg}]
    
    def generate_log_based_suggestions(self) -> Tuple[bool, List[Dict]]:
        """Gerar sugestões baseadas em logs"""
        try:
            self.logger.info(f"[{self.tracing_id}] Gerando sugestões baseadas em logs...")
            
            # Analisar logs
            suggestions = self.log_analyzer.extract_suggestions()
            improvements = self.log_analyzer.prioritize_improvements()
            
            # Salvar sugestões
            suggestions_file = Path(self.config.output_path) / "log_based_suggestions.md"
            with open(suggestions_file, 'w', encoding='utf-8') as f:
                f.write("# Sugestões Baseadas em Logs\n\n")
                f.write(f"Gerado em: {datetime.now().isoformat()}\n")
                f.write(f"Tracing ID: {self.tracing_id}\n\n")
                
                f.write("## Sugestões de Melhoria\n\n")
                for index, suggestion in enumerate(suggestions, 1):
                    f.write(f"{index}. {suggestion}\n")
                
                f.write("\n## Melhorias Prioritárias\n\n")
                for index, improvement in enumerate(improvements, 1):
                    f.write(f"{index}. {improvement}\n")
            
            self.logger.info(f"[{self.tracing_id}] Sugestões baseadas em logs geradas: {suggestions_file}")
            return True, []
            
        except Exception as e:
            error_msg = f"Erro na geração de sugestões: {str(e)}"
            self.logger.error(f"[{self.tracing_id}] {error_msg}")
            return False, [{"type": "ERROR", "message": error_msg}]
    
    def generate_api_documentation(self) -> Tuple[bool, List[Dict]]:
        """Gerar documentação de APIs"""
        try:
            self.logger.info(f"[{self.tracing_id}] Gerando documentação de APIs...")
            
            # Detectar e gerar documentação GraphQL
            graphql_docs = self.api_docs_generator.generate_graphql_docs()
            
            # Detectar e gerar documentação Protobuf
            protobuf_docs = self.api_docs_generator.generate_protobuf_docs()
            
            # Detectar e gerar documentação OpenAPI
            openapi_docs = self.api_docs_generator.generate_openapi_docs()
            
            # Salvar documentação de APIs
            api_docs_file = Path(self.config.output_path) / "api_documentation.md"
            with open(api_docs_file, 'w', encoding='utf-8') as f:
                f.write("# Documentação de APIs\n\n")
                f.write(f"Gerado em: {datetime.now().isoformat()}\n")
                f.write(f"Tracing ID: {self.tracing_id}\n\n")
                
                if graphql_docs:
                    f.write("## GraphQL\n\n")
                    f.write(graphql_docs)
                    f.write("\n\n")
                
                if protobuf_docs:
                    f.write("## Protobuf\n\n")
                    f.write(protobuf_docs)
                    f.write("\n\n")
                
                if openapi_docs:
                    f.write("## OpenAPI\n\n")
                    f.write(openapi_docs)
                    f.write("\n\n")
            
            self.logger.info(f"[{self.tracing_id}] Documentação de APIs gerada: {api_docs_file}")
            return True, []
            
        except Exception as e:
            error_msg = f"Erro na geração de documentação de APIs: {str(e)}"
            self.logger.error(f"[{self.tracing_id}] {error_msg}")
            return False, [{"type": "ERROR", "message": error_msg}]
    
    def generate_quality_report(self) -> Tuple[bool, List[Dict]]:
        """Gerar relatório de qualidade"""
        try:
            self.logger.info(f"[{self.tracing_id}] Gerando relatório de qualidade...")
            
            # Analisar qualidade de todos os arquivos
            quality_scores = {}
            total_score = 0.0
            file_count = 0
            
            docs_path = Path(self.config.docs_path)
            for doc_file in docs_path.rglob("*.md"):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    quality_score = self.quality_analyzer.calculate_doc_quality_score(content)
                    quality_scores[str(doc_file)] = quality_score
                    total_score += quality_score
                    file_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"[{self.tracing_id}] Erro ao analisar {doc_file}: {str(e)}")
            
            avg_quality = total_score / file_count if file_count > 0 else 0.0
            
            # Salvar relatório
            quality_file = Path(self.config.output_path) / "quality_report.md"
            with open(quality_file, 'w', encoding='utf-8') as f:
                f.write("# Relatório de Qualidade\n\n")
                f.write(f"Gerado em: {datetime.now().isoformat()}\n")
                f.write(f"Tracing ID: {self.tracing_id}\n\n")
                
                f.write(f"## Resumo\n\n")
                f.write(f"- **Arquivos analisados**: {file_count}\n")
                f.write(f"- **Qualidade média**: {avg_quality:.2f}\n")
                f.write(f"- **Threshold**: {self.config.quality_threshold}\n")
                f.write(f"- **Status**: {'✅ APROVADO' if avg_quality >= self.config.quality_threshold else '❌ REPROVADO'}\n\n")
                
                f.write("## Detalhes por Arquivo\n\n")
                for file_path, score in quality_scores.items():
                    status = "✅" if score >= self.config.quality_threshold else "❌"
                    f.write(f"- {status} {file_path}: {score:.2f}\n")
            
            self.logger.info(f"[{self.tracing_id}] Relatório de qualidade gerado: {quality_file}")
            return True, []
            
        except Exception as e:
            error_msg = f"Erro na geração de relatório de qualidade: {str(e)}"
            self.logger.error(f"[{self.tracing_id}] {error_msg}")
            return False, [{"type": "ERROR", "message": error_msg}]
    
    def generate_security_report(self) -> Tuple[bool, List[Dict]]:
        """Gerar relatório de segurança"""
        try:
            self.logger.info(f"[{self.tracing_id}] Gerando relatório de segurança...")
            
            # Escanear todos os arquivos
            security_incidents = []
            docs_path = Path(self.config.docs_path)
            
            for doc_file in docs_path.rglob("*.md"):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    sensitive_data = self.security_detector.scan_documentation(content)
                    if sensitive_data:
                        for data in sensitive_data:
                            security_incidents.append({
                                'file': str(doc_file),
                                'type': data['type'],
                                'line': data.get('line', 'N/A'),
                                'pattern': data.get('pattern', 'N/A'),
                                'severity': 'CRITICAL'
                            })
                    
                except Exception as e:
                    self.logger.warning(f"[{self.tracing_id}] Erro ao escanear {doc_file}: {str(e)}")
            
            # Salvar relatório
            security_file = Path(self.config.output_path) / "security_report.md"
            with open(security_file, 'w', encoding='utf-8') as f:
                f.write("# Relatório de Segurança\n\n")
                f.write(f"Gerado em: {datetime.now().isoformat()}\n")
                f.write(f"Tracing ID: {self.tracing_id}\n\n")
                
                f.write(f"## Resumo\n\n")
                f.write(f"- **Incidentes encontrados**: {len(security_incidents)}\n")
                f.write(f"- **Status**: {'❌ FALHA' if security_incidents else '✅ APROVADO'}\n\n")
                
                if security_incidents:
                    f.write("## Incidentes de Segurança\n\n")
                    for index, incident in enumerate(security_incidents, 1):
                        f.write(f"### Incidente {index}\n")
                        f.write(f"- **Arquivo**: {incident['file']}\n")
                        f.write(f"- **Tipo**: {incident['type']}\n")
                        f.write(f"- **Linha**: {incident['line']}\n")
                        f.write(f"- **Padrão**: {incident['pattern']}\n")
                        f.write(f"- **Severidade**: {incident['severity']}\n\n")
                else:
                    f.write("✅ Nenhum incidente de segurança encontrado.\n\n")
            
            self.logger.info(f"[{self.tracing_id}] Relatório de segurança gerado: {security_file}")
            return True, []
            
        except Exception as e:
            error_msg = f"Erro na geração de relatório de segurança: {str(e)}"
            self.logger.error(f"[{self.tracing_id}] {error_msg}")
            return False, [{"type": "ERROR", "message": error_msg}]
    
    def generate_compliance_report(self) -> Tuple[bool, List[Dict]]:
        """Gerar relatório de compliance"""
        try:
            self.logger.info(f"[{self.tracing_id}] Gerando relatório de compliance...")
            
            # Validar compliance
            compliance_result = self.compliance_validator.validate_all_standards()
            
            # Salvar relatório
            compliance_file = Path(self.config.output_path) / "compliance_report.md"
            with open(compliance_file, 'w', encoding='utf-8') as f:
                f.write("# Relatório de Compliance\n\n")
                f.write(f"Gerado em: {datetime.now().isoformat()}\n")
                f.write(f"Tracing ID: {self.tracing_id}\n\n")
                
                f.write(f"## Resumo\n\n")
                f.write(f"- **Score geral**: {compliance_result.get('overall_score', 0):.2f}\n")
                f.write(f"- **Violações**: {len(compliance_result.get('violations', []))}\n")
                f.write(f"- **Status**: {'✅ APROVADO' if compliance_result.get('overall_score', 0) >= self.config.compliance_threshold else '❌ REPROVADO'}\n\n")
                
                violations = compliance_result.get('violations', [])
                if violations:
                    f.write("## Violações\n\n")
                    for index, violation in enumerate(violations, 1):
                        f.write(f"### Violação {index}\n")
                        f.write(f"- **Descrição**: {violation.get('description', 'N/A')}\n")
                        f.write(f"- **Padrão**: {violation.get('standard', 'N/A')}\n")
                        f.write(f"- **Severidade**: {violation.get('severity', 'N/A')}\n\n")
                else:
                    f.write("✅ Nenhuma violação de compliance encontrada.\n\n")
            
            self.logger.info(f"[{self.tracing_id}] Relatório de compliance gerado: {compliance_file}")
            return True, []
            
        except Exception as e:
            error_msg = f"Erro na geração de relatório de compliance: {str(e)}"
            self.logger.error(f"[{self.tracing_id}] {error_msg}")
            return False, [{"type": "ERROR", "message": error_msg}]
    
    def generate_metrics_report(self) -> Tuple[bool, List[Dict]]:
        """Gerar relatório de métricas"""
        try:
            self.logger.info(f"[{self.tracing_id}] Gerando relatório de métricas...")
            
            # Coletar métricas
            metrics = self.metrics_collector.collect_all_metrics()
            analysis = self.metrics_analyzer.analyze_metrics(metrics)
            
            # Salvar relatório
            metrics_file = Path(self.config.output_path) / "metrics_report.md"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                f.write("# Relatório de Métricas\n\n")
                f.write(f"Gerado em: {datetime.now().isoformat()}\n")
                f.write(f"Tracing ID: {self.tracing_id}\n\n")
                
                f.write("## Métricas de Performance\n\n")
                f.write(f"- **Tempo médio de geração**: {metrics.get('avg_generation_time', 0):.2f}string_data\n")
                f.write(f"- **Tokens consumidos**: {metrics.get('avg_tokens_used', 0)}\n")
                f.write(f"- **Cobertura de documentação**: {metrics.get('documentation_coverage', 0):.2%}\n\n")
                
                f.write("## Análise de Tendências\n\n")
                for trend in analysis.get('trends', []):
                    f.write(f"- {trend}\n")
                
                f.write("\n## Otimizações Recomendadas\n\n")
                for optimization in analysis.get('optimizations', []):
                    f.write(f"- {optimization}\n")
            
            self.logger.info(f"[{self.tracing_id}] Relatório de métricas gerado: {metrics_file}")
            return True, []
            
        except Exception as e:
            error_msg = f"Erro na geração de relatório de métricas: {str(e)}"
            self.logger.error(f"[{self.tracing_id}] {error_msg}")
            return False, [{"type": "ERROR", "message": error_msg}]
    
    def generate_summary_report(self, results: Dict[str, Any]) -> bool:
        """Gerar relatório resumo"""
        try:
            self.logger.info(f"[{self.tracing_id}] Gerando relatório resumo...")
            
            summary_file = Path(self.config.output_path) / "summary_report.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("# Relatório Resumo - Geração de Documentação Enterprise\n\n")
                f.write(f"**Tracing ID**: {self.tracing_id}\n")
                f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n")
                f.write(f"**Versão**: 1.0\n\n")
                
                f.write("## 📊 Resumo Executivo\n\n")
                f.write(f"- **Status**: {'✅ SUCESSO' if results['success'] else '❌ FALHA'}\n")
                f.write(f"- **Duração**: {results['duration']:.2f}string_data\n")
                f.write(f"- **Arquivos gerados**: {results['files_generated']}\n")
                f.write(f"- **Arquivos processados**: {results['files_processed']}\n\n")
                
                f.write("## 📈 Scores de Qualidade\n\n")
                f.write(f"- **Qualidade**: {results['quality_score']:.2f}\n")
                f.write(f"- **Segurança**: {results['security_score']:.2f}\n")
                f.write(f"- **Compliance**: {results['compliance_score']:.2f}\n\n")
                
                if results['errors']:
                    f.write("## ❌ Erros\n\n")
                    for index, error in enumerate(results['errors'], 1):
                        f.write(f"{index}. {error['message']}\n")
                    f.write("\n")
                
                if results['warnings']:
                    f.write("## ⚠️ Avisos\n\n")
                    for index, warning in enumerate(results['warnings'], 1):
                        f.write(f"{index}. {warning['message']}\n")
                    f.write("\n")
                
                f.write("## 📁 Arquivos Gerados\n\n")
                output_path = Path(self.config.output_path)
                for file_path in output_path.glob("*.md"):
                    f.write(f"- `{file_path.name}`\n")
                
                f.write("\n---\n")
                f.write("*Gerado automaticamente pelo EnterpriseDocGenerator*\n")
            
            self.logger.info(f"[{self.tracing_id}] Relatório resumo gerado: {summary_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao gerar relatório resumo: {str(e)}")
            return False
    
    def run_generation_pipeline(self) -> GenerationResult:
        """Executar pipeline completo de geração"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"[{self.tracing_id}] Iniciando pipeline de geração...")
            
            # 1. Criar backup
            if not self.create_backup():
                self.logger.warning(f"[{self.tracing_id}] Backup falhou, continuando...")
            
            # 2. Validar ambiente
            env_valid, env_errors = self.validate_environment()
            if not env_valid:
                raise Exception(f"Ambiente inválido: {', '.join(env_errors)}")
            
            # 3. Executar gerações em paralelo
            generation_tasks = [
                ("semantic_contracts", self.generate_semantic_contracts),
                ("log_suggestions", self.generate_log_based_suggestions),
                ("api_docs", self.generate_api_documentation),
                ("quality_report", self.generate_quality_report),
                ("security_report", self.generate_security_report),
                ("compliance_report", self.generate_compliance_report),
                ("metrics_report", self.generate_metrics_report)
            ]
            
            results = {}
            errors = []
            warnings = []
            
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_task = {
                    executor.submit(task_func): task_name 
                    for task_name, task_func in generation_tasks
                }
                
                for future in as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        success, task_errors = future.result()
                        results[task_name] = success
                        
                        if not success:
                            errors.extend(task_errors)
                        elif task_errors:
                            warnings.extend(task_errors)
                            
                    except Exception as e:
                        error_msg = f"Erro na tarefa {task_name}: {str(e)}"
                        self.logger.error(f"[{self.tracing_id}] {error_msg}")
                        errors.append({"type": "ERROR", "message": error_msg})
                        results[task_name] = False
            
            # 4. Validar compliance final
            self.logger.info(f"[{self.tracing_id}] Executando validação final de compliance...")
            compliance_report = self.compliance_checker.run_validation(self.config.docs_path)
            
            # 5. Gerar relatório resumo
            summary_data = {
                'success': len(errors) == 0,
                'duration': (datetime.now() - start_time).total_seconds(),
                'files_generated': len([r for r in results.values() if r]),
                'files_processed': len(results),
                'quality_score': compliance_report.quality_score,
                'security_score': compliance_report.security_score,
                'compliance_score': compliance_report.compliance_score,
                'errors': errors,
                'warnings': warnings
            }
            
            self.generate_summary_report(summary_data)
            
            # 6. Coletar métricas finais
            final_metrics = self.metrics_collector.collect_all_metrics()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Criar resultado
            result = GenerationResult(
                timestamp=datetime.now().isoformat(),
                tracing_id=self.tracing_id,
                success=len(errors) == 0,
                duration=duration,
                files_generated=summary_data['files_generated'],
                files_processed=summary_data['files_processed'],
                quality_score=compliance_report.quality_score,
                security_score=compliance_report.security_score,
                compliance_score=compliance_report.compliance_score,
                errors=errors,
                warnings=warnings,
                metrics=final_metrics
            )
            
            self.logger.info(f"[{self.tracing_id}] Pipeline concluído em {duration:.2f}string_data")
            self.logger.info(f"[{self.tracing_id}] Sucesso: {result.success}")
            self.logger.info(f"[{self.tracing_id}] Arquivos gerados: {result.files_generated}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro no pipeline: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Rollback em caso de erro
            if self.config.backup_enabled:
                self.logger.info(f"[{self.tracing_id}] Executando rollback...")
                try:
                    self.rollback_system.restore_latest_snapshot()
                    self.logger.info(f"[{self.tracing_id}] Rollback executado com sucesso")
                except Exception as rollback_error:
                    self.logger.error(f"[{self.tracing_id}] Erro no rollback: {str(rollback_error)}")
            
            # Retornar resultado de erro
            return GenerationResult(
                timestamp=datetime.now().isoformat(),
                tracing_id=self.tracing_id,
                success=False,
                duration=(datetime.now() - start_time).total_seconds(),
                files_generated=0,
                files_processed=0,
                quality_score=0.0,
                security_score=0.0,
                compliance_score=0.0,
                errors=[{"type": "CRITICAL", "message": str(e)}],
                warnings=[],
                metrics={}
            )
    
    def save_result(self, result: GenerationResult, output_path: str = "logs/generation_result.json"):
        """Salvar resultado da geração"""
        try:
            # Criar diretório se não existir
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Converter para dict
            result_dict = asdict(result)
            
            # Salvar arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"[{self.tracing_id}] Resultado salvo em: {output_path}")
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao salvar resultado: {str(e)}")
    
    def print_summary(self, result: GenerationResult):
        """Imprimir resumo da geração"""
        print("\n" + "="*80)
        print("🚀 RELATÓRIO DE GERAÇÃO DE DOCUMENTAÇÃO ENTERPRISE")
        print("="*80)
        print(f"Tracing ID: {result.tracing_id}")
        print(f"Timestamp: {result.timestamp}")
        print(f"Status: {'✅ SUCESSO' if result.success else '❌ FALHA'}")
        print(f"Duração: {result.duration:.2f}string_data")
        print("-"*80)
        print("📊 ESTATÍSTICAS:")
        print(f"  Arquivos gerados: {result.files_generated}")
        print(f"  Arquivos processados: {result.files_processed}")
        print(f"  Score de qualidade: {result.quality_score:.2f}")
        print(f"  Score de segurança: {result.security_score:.2f}")
        print(f"  Score de compliance: {result.compliance_score:.2f}")
        print("-"*80)
        
        if result.errors:
            print("❌ ERROS:")
            for index, error in enumerate(result.errors, 1):
                print(f"  {index}. {error['message']}")
        else:
            print("✅ Nenhum erro encontrado!")
        
        if result.warnings:
            print("-"*80)
            print("⚠️ AVISOS:")
            for index, warning in enumerate(result.warnings, 1):
                print(f"  {index}. {warning['message']}")
        
        print("="*80)


def main():
    """
    Função principal do script
    """
    parser = argparse.ArgumentParser(
        description="Gerador de Documentação Enterprise"
    )
    parser.add_argument(
        "--docs-path",
        default="docs/",
        help="Caminho para documentação (padrão: docs/)"
    )
    parser.add_argument(
        "--output-path",
        default="docs/enterprise/",
        help="Caminho de saída (padrão: docs/enterprise/)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Desabilitar backup automático"
    )
    parser.add_argument(
        "--quality-threshold",
        type=float,
        default=0.85,
        help="Threshold de qualidade (padrão: 0.85)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Número máximo de workers paralelos (padrão: 4)"
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
        # Criar configuração
        config = GenerationConfig(
            docs_path=args.docs_path,
            output_path=args.output_path,
            backup_enabled=not args.no_backup,
            quality_threshold=args.quality_threshold,
            max_workers=args.max_workers,
            verbose=args.verbose
        )
        
        # Criar gerador
        generator = EnterpriseDocGenerator(config)
        
        # Executar pipeline
        result = generator.run_generation_pipeline()
        
        # Salvar resultado
        generator.save_result(result)
        
        # Imprimir resumo
        generator.print_summary(result)
        
        # Retornar código de saída
        if result.success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 