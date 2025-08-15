#!/usr/bin/env python3
"""
Script de Validação Final - Item 13.1
Tracing ID: VALIDATION_FINAL_20250127_001

Executa validação completa do sistema de documentação enterprise:
- DocQualityScore > 0.85 para todos os módulos
- Similaridade semântica > 0.85 para todas as funções
- Zero vazamentos de dados sensíveis
- Rollback automático funcional
- 100% dos arquivos de documentação gerados
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

# Adicionar paths para imports
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.validation.doc_quality_score import DocQualityAnalyzer
from infrastructure.ml.semantic_embeddings import SemanticEmbeddingService
from infrastructure.security.advanced_security_system import SensitiveDataDetector
from infrastructure.backup.rollback_system import RollbackSystem
from shared.doc_generation_metrics import DocGenerationMetrics
from shared.compliance_validator import ComplianceValidator

@dataclass
class ValidationResult:
    """Resultado de uma validação específica"""
    test_name: str
    status: bool
    score: float
    details: str
    timestamp: str

class FinalValidationRunner:
    """Executor da validação final completa"""
    
    def __init__(self):
        self.tracing_id = "VALIDATION_FINAL_20250127_001"
        self.results: List[ValidationResult] = []
        self.start_time = time.time()
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)string_data] [%(levelname)string_data] [%(name)string_data] %(message)string_data',
            handlers=[
                logging.FileHandler(f'logs/final_validation_{time.strftime("%Y%m%data")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Inicializar serviços
        self.doc_analyzer = DocQualityAnalyzer()
        self.semantic_service = SemanticEmbeddingService()
        self.security_detector = SensitiveDataDetector()
        self.rollback_system = RollbackSystem()
        self.metrics = DocGenerationMetrics()
        self.compliance_validator = ComplianceValidator()
        
        self.logger.info(f"[{self.tracing_id}] Iniciando validação final")
    
    def validate_doc_quality_scores(self) -> ValidationResult:
        """Valida DocQualityScore > 0.85 para todos os módulos"""
        self.logger.info("Validando DocQualityScore dos módulos...")
        
        try:
            # Listar todos os módulos Python
            modules = self._find_python_modules()
            scores = []
            
            for module_path in modules:
                score = self.doc_analyzer.calculate_doc_quality_score(module_path)
                scores.append(score)
                
                if score < 0.85:
                    self.logger.warning(f"Módulo {module_path} com score baixo: {score}")
            
            avg_score = sum(scores) / len(scores) if scores else 0
            min_score = min(scores) if scores else 0
            all_above_threshold = all(score >= 0.85 for score in scores)
            
            details = f"Total: {len(modules)} módulos, Média: {avg_score:.3f}, Mínimo: {min_score:.3f}"
            
            return ValidationResult(
                test_name="DocQualityScore Validation",
                status=all_above_threshold,
                score=avg_score,
                details=details,
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
            
        except Exception as e:
            self.logger.error(f"Erro na validação de DocQualityScore: {e}")
            return ValidationResult(
                test_name="DocQualityScore Validation",
                status=False,
                score=0.0,
                details=f"Erro: {str(e)}",
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
    
    def validate_semantic_similarity(self) -> ValidationResult:
        """Valida similaridade semântica > 0.85 para todas as funções"""
        self.logger.info("Validando similaridade semântica das funções...")
        
        try:
            # Listar todas as funções Python
            functions = self._find_python_functions()
            similarities = []
            
            for func_path in functions:
                # Gerar embedding da função
                func_content = self._read_file_content(func_path)
                embedding = self.semantic_service.generate_embedding(func_content)
                
                # Comparar com documentação esperada
                doc_path = func_path.replace('.py', '_docs.md')
                if os.path.exists(doc_path):
                    doc_content = self._read_file_content(doc_path)
                    doc_embedding = self.semantic_service.generate_embedding(doc_content)
                    
                    similarity = self.semantic_service.calculate_similarity(embedding, doc_embedding)
                    similarities.append(similarity)
                    
                    if similarity < 0.85:
                        self.logger.warning(f"Função {func_path} com similaridade baixa: {similarity}")
            
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            min_similarity = min(similarities) if similarities else 0
            all_above_threshold = all(sim >= 0.85 for sim in similarities)
            
            details = f"Total: {len(functions)} funções, Média: {avg_similarity:.3f}, Mínimo: {min_similarity:.3f}"
            
            return ValidationResult(
                test_name="Semantic Similarity Validation",
                status=all_above_threshold,
                score=avg_similarity,
                details=details,
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
            
        except Exception as e:
            self.logger.error(f"Erro na validação de similaridade semântica: {e}")
            return ValidationResult(
                test_name="Semantic Similarity Validation",
                status=False,
                score=0.0,
                details=f"Erro: {str(e)}",
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
    
    def validate_sensitive_data_leaks(self) -> ValidationResult:
        """Valida zero vazamentos de dados sensíveis"""
        self.logger.info("Validando vazamentos de dados sensíveis...")
        
        try:
            # Escanear toda a documentação
            doc_files = self._find_documentation_files()
            leaks_found = []
            
            for doc_file in doc_files:
                content = self._read_file_content(doc_file)
                leaks = self.security_detector.scan_documentation(content)
                
                if leaks:
                    leaks_found.extend(leaks)
                    self.logger.warning(f"Vazamentos encontrados em {doc_file}: {leaks}")
            
            has_leaks = len(leaks_found) > 0
            details = f"Arquivos escaneados: {len(doc_files)}, Vazamentos encontrados: {len(leaks_found)}"
            
            return ValidationResult(
                test_name="Sensitive Data Leaks Validation",
                status=not has_leaks,
                score=1.0 if not has_leaks else 0.0,
                details=details,
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
            
        except Exception as e:
            self.logger.error(f"Erro na validação de vazamentos: {e}")
            return ValidationResult(
                test_name="Sensitive Data Leaks Validation",
                status=False,
                score=0.0,
                details=f"Erro: {str(e)}",
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
    
    def validate_rollback_functionality(self) -> ValidationResult:
        """Valida rollback automático funcional"""
        self.logger.info("Validando funcionalidade de rollback...")
        
        try:
            # Criar snapshot de teste
            snapshot_id = self.rollback_system.create_snapshot("test_validation")
            
            # Simular mudança
            test_file = "test_rollback_file.txt"
            with open(test_file, 'w') as f:
                f.write("test content")
            
            # Detectar divergência e fazer rollback
            divergence_detected = self.rollback_system.detect_divergence_and_rollback()
            
            # Verificar se arquivo foi removido
            file_exists = os.path.exists(test_file)
            
            # Limpar arquivo de teste se ainda existir
            if file_exists:
                os.remove(test_file)
            
            details = f"Snapshot criado: {snapshot_id}, Divergência detectada: {divergence_detected}, Rollback executado: {not file_exists}"
            
            return ValidationResult(
                test_name="Rollback Functionality Validation",
                status=divergence_detected and not file_exists,
                score=1.0 if divergence_detected and not file_exists else 0.0,
                details=details,
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
            
        except Exception as e:
            self.logger.error(f"Erro na validação de rollback: {e}")
            return ValidationResult(
                test_name="Rollback Functionality Validation",
                status=False,
                score=0.0,
                details=f"Erro: {str(e)}",
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
    
    def validate_documentation_coverage(self) -> ValidationResult:
        """Valida 100% dos arquivos de documentação gerados"""
        self.logger.info("Validando cobertura de documentação...")
        
        try:
            # Listar arquivos que deveriam ter documentação
            expected_docs = self._get_expected_documentation_files()
            existing_docs = self._find_documentation_files()
            
            missing_docs = []
            for expected_doc in expected_docs:
                if not any(existing_doc.endswith(expected_doc) for existing_doc in existing_docs):
                    missing_docs.append(expected_doc)
            
            coverage_percentage = (len(expected_docs) - len(missing_docs)) / len(expected_docs) * 100 if expected_docs else 100
            all_generated = len(missing_docs) == 0
            
            details = f"Esperados: {len(expected_docs)}, Gerados: {len(existing_docs)}, Faltando: {len(missing_docs)}, Cobertura: {coverage_percentage:.1f}%"
            
            return ValidationResult(
                test_name="Documentation Coverage Validation",
                status=all_generated,
                score=coverage_percentage / 100,
                details=details,
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
            
        except Exception as e:
            self.logger.error(f"Erro na validação de cobertura: {e}")
            return ValidationResult(
                test_name="Documentation Coverage Validation",
                status=False,
                score=0.0,
                details=f"Erro: {str(e)}",
                timestamp=time.strftime("%Y-%m-%data %H:%M:%S")
            )
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Executa todas as validações"""
        self.logger.info(f"[{self.tracing_id}] Iniciando execução de todas as validações")
        
        # Executar validações
        self.results.append(self.validate_doc_quality_scores())
        self.results.append(self.validate_semantic_similarity())
        self.results.append(self.validate_sensitive_data_leaks())
        self.results.append(self.validate_rollback_functionality())
        self.results.append(self.validate_documentation_coverage())
        
        # Calcular métricas finais
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.status)
        avg_score = sum(result.score for result in self.results) / total_tests if total_tests > 0 else 0
        
        execution_time = time.time() - self.start_time
        
        # Gerar relatório
        report = {
            "tracing_id": self.tracing_id,
            "timestamp": time.strftime("%Y-%m-%data %H:%M:%S"),
            "execution_time_seconds": execution_time,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "average_score": avg_score,
            "results": [
                {
                    "test_name": result.test_name,
                    "status": result.status,
                    "score": result.score,
                    "details": result.details,
                    "timestamp": result.timestamp
                }
                for result in self.results
            ]
        }
        
        # Salvar relatório
        self._save_report(report)
        
        self.logger.info(f"[{self.tracing_id}] Validação final concluída")
        self.logger.info(f"Tempo de execução: {execution_time:.2f}string_data")
        self.logger.info(f"Taxa de sucesso: {report['success_rate']:.1f}%")
        self.logger.info(f"Score médio: {avg_score:.3f}")
        
        return report
    
    def _find_python_modules(self) -> List[str]:
        """Encontra todos os módulos Python"""
        modules = []
        for root, dirs, files in os.walk("."):
            if "venv" in root or "__pycache__" in root or ".git" in root:
                continue
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    modules.append(os.path.join(root, file))
        return modules
    
    def _find_python_functions(self) -> List[str]:
        """Encontra arquivos com funções Python"""
        return self._find_python_modules()
    
    def _find_documentation_files(self) -> List[str]:
        """Encontra arquivos de documentação"""
        docs = []
        for root, dirs, files in os.walk("."):
            if "venv" in root or "__pycache__" in root or ".git" in root:
                continue
            for file in files:
                if file.endswith((".md", ".rst", ".txt")) and "doc" in file.lower():
                    docs.append(os.path.join(root, file))
        return docs
    
    def _get_expected_documentation_files(self) -> List[str]:
        """Lista arquivos de documentação esperados"""
        return [
            "semantic_contracts.md",
            "log_based_suggestions.md",
            "graphql_schema_docs.md",
            "protobuf_schema_docs.md",
            "openapi_docs.md",
            "trigger_config.json"
        ]
    
    def _read_file_content(self, file_path: str) -> str:
        """Lê conteúdo de arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
    
    def _save_report(self, report: Dict[str, Any]):
        """Salva relatório de validação"""
        report_file = f"logs/final_validation_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("logs", exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Relatório salvo em: {report_file}")

def main():
    """Função principal"""
    runner = FinalValidationRunner()
    report = runner.run_all_validations()
    
    # Retornar código de saída baseado no sucesso
    if report["success_rate"] == 100:
        print("✅ Validação final: TODOS OS TESTES PASSARAM")
        sys.exit(0)
    else:
        print(f"⚠️ Validação final: {report['failed_tests']} TESTES FALHARAM")
        sys.exit(1)

if __name__ == "__main__":
    main() 