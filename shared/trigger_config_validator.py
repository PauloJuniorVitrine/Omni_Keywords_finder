"""
Trigger Config Validator - Sistema de Validação de Configurações

Tracing ID: TRIGGER_CONFIG_VALIDATOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação Inicial

Responsável: Sistema de Documentação Enterprise
"""

import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severidade da validação"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Resultado de uma validação"""
    is_valid: bool
    severity: ValidationSeverity
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class TriggerConfig:
    """Configuração de trigger para documentação"""
    sensitive_files: List[str]
    auto_rerun_patterns: List[str]
    exclusion_patterns: List[str]
    semantic_threshold: float
    rollback_config: Dict[str, Any]
    compliance_config: Dict[str, Any]


class TriggerConfigValidator:
    """
    Validador de configurações de trigger para documentação enterprise
    
    Responsabilidades:
    - Validar arquivos sensíveis
    - Validar padrões de auto-rerun
    - Validar configurações de threshold
    - Validar configurações de rollback
    - Validar configurações de compliance
    """
    
    def __init__(self, config_path: str = "docs/trigger_config.json"):
        """
        Inicializa o validador
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = Path(config_path)
        self.config: Optional[TriggerConfig] = None
        self.validation_results: List[ValidationResult] = []
        
    def load_config(self) -> ValidationResult:
        """
        Carrega e valida a estrutura básica do arquivo de configuração
        
        Returns:
            ValidationResult com status da operação
        """
        try:
            if not self.config_path.exists():
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Arquivo de configuração não encontrado: {self.config_path}",
                    details={"path": str(self.config_path)}
                )
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validar estrutura básica
            required_fields = [
                'sensitive_files', 'auto_rerun_patterns', 'exclusion_patterns',
                'semantic_threshold', 'rollback_config', 'compliance_config'
            ]
            
            missing_fields = [field for field in required_fields if field not in config_data]
            if missing_fields:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Campos obrigatórios ausentes: {missing_fields}",
                    details={"missing_fields": missing_fields}
                )
            
            # Criar objeto de configuração
            self.config = TriggerConfig(
                sensitive_files=config_data.get('sensitive_files', []),
                auto_rerun_patterns=config_data.get('auto_rerun_patterns', []),
                exclusion_patterns=config_data.get('exclusion_patterns', []),
                semantic_threshold=config_data.get('semantic_threshold', 0.85),
                rollback_config=config_data.get('rollback_config', {}),
                compliance_config=config_data.get('compliance_config', {})
            )
            
            logger.info(f"Configuração carregada com sucesso: {self.config_path}")
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                message="Configuração carregada com sucesso"
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Erro de sintaxe JSON: {str(e)}",
                details={"error": str(e)}
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Erro ao carregar configuração: {str(e)}",
                details={"error": str(e)}
            )
    
    def validate_sensitive_files(self) -> ValidationResult:
        """
        Valida a lista de arquivos sensíveis
        
        Returns:
            ValidationResult com status da validação
        """
        if not self.config:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Configuração não carregada"
            )
        
        issues = []
        
        # Validar se a lista não está vazia
        if not self.config.sensitive_files:
            issues.append("Lista de arquivos sensíveis está vazia")
        
        # Validar padrões de arquivos sensíveis
        sensitive_patterns = [
            r'\.env$', r'\.key$', r'\.pem$', r'\.p12$', r'\.pfx$',
            r'config\.json$', r'secrets\.', r'password', r'token'
        ]
        
        for file_path in self.config.sensitive_files:
            # Verificar se o arquivo existe
            if not Path(file_path).exists():
                issues.append(f"Arquivo sensível não encontrado: {file_path}")
            
            # Verificar se o arquivo segue padrões sensíveis
            is_sensitive_pattern = any(re.search(pattern, file_path, re.IGNORECASE) 
                                     for pattern in sensitive_patterns)
            if not is_sensitive_pattern:
                issues.append(f"Arquivo pode não ser sensível: {file_path}")
        
        if issues:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Problemas encontrados na validação de arquivos sensíveis",
                details={"issues": issues}
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message=f"Validação de arquivos sensíveis aprovada ({len(self.config.sensitive_files)} arquivos)"
        )
    
    def validate_patterns(self) -> ValidationResult:
        """
        Valida os padrões de auto-rerun e exclusão
        
        Returns:
            ValidationResult com status da validação
        """
        if not self.config:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Configuração não carregada"
            )
        
        issues = []
        
        # Validar padrões de auto-rerun
        for pattern in self.config.auto_rerun_patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                issues.append(f"Padrão de auto-rerun inválido '{pattern}': {str(e)}")
        
        # Validar padrões de exclusão
        for pattern in self.config.exclusion_patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                issues.append(f"Padrão de exclusão inválido '{pattern}': {str(e)}")
        
        # Verificar sobreposição entre padrões
        for rerun_pattern in self.config.auto_rerun_patterns:
            for exclusion_pattern in self.config.exclusion_patterns:
                if rerun_pattern == exclusion_pattern:
                    issues.append(f"Padrão duplicado entre auto-rerun e exclusão: {rerun_pattern}")
        
        if issues:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Problemas encontrados na validação de padrões",
                details={"issues": issues}
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message=f"Validação de padrões aprovada ({len(self.config.auto_rerun_patterns)} auto-rerun, {len(self.config.exclusion_patterns)} exclusão)"
        )
    
    def validate_semantic_threshold(self) -> ValidationResult:
        """
        Valida o threshold semântico
        
        Returns:
            ValidationResult com status da validação
        """
        if not self.config:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Configuração não carregada"
            )
        
        threshold = self.config.semantic_threshold
        
        if not isinstance(threshold, (int, float)):
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Threshold semântico deve ser um número",
                details={"threshold": threshold, "type": type(threshold).__name__}
            )
        
        if threshold < 0.0 or threshold > 1.0:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Threshold semântico deve estar entre 0.0 e 1.0",
                details={"threshold": threshold}
            )
        
        # Validar se o threshold é adequado para o contexto
        if threshold < 0.7:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Threshold semântico muito baixo pode gerar falsos positivos",
                details={"threshold": threshold, "recommended_min": 0.7}
            )
        
        if threshold > 0.95:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Threshold semântico muito alto pode ignorar mudanças relevantes",
                details={"threshold": threshold, "recommended_max": 0.95}
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message=f"Threshold semântico válido: {threshold}"
        )
    
    def validate_rollback_config(self) -> ValidationResult:
        """
        Valida as configurações de rollback
        
        Returns:
            ValidationResult com status da validação
        """
        if not self.config:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Configuração não carregada"
            )
        
        rollback_config = self.config.rollback_config
        issues = []
        
        # Validar campos obrigatórios
        required_fields = ['enabled', 'max_snapshots', 'auto_rollback_threshold']
        for field in required_fields:
            if field not in rollback_config:
                issues.append(f"Campo obrigatório ausente: {field}")
        
        # Validar valores específicos
        if 'enabled' in rollback_config:
            if not isinstance(rollback_config['enabled'], bool):
                issues.append("Campo 'enabled' deve ser booleano")
        
        if 'max_snapshots' in rollback_config:
            max_snapshots = rollback_config['max_snapshots']
            if not isinstance(max_snapshots, int) or max_snapshots < 1:
                issues.append("Campo 'max_snapshots' deve ser um inteiro positivo")
        
        if 'auto_rollback_threshold' in rollback_config:
            threshold = rollback_config['auto_rollback_threshold']
            if not isinstance(threshold, (int, float)) or threshold < 0.0 or threshold > 1.0:
                issues.append("Campo 'auto_rollback_threshold' deve estar entre 0.0 e 1.0")
        
        if issues:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Problemas encontrados na configuração de rollback",
                details={"issues": issues}
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message="Configuração de rollback válida"
        )
    
    def validate_compliance_config(self) -> ValidationResult:
        """
        Valida as configurações de compliance
        
        Returns:
            ValidationResult com status da validação
        """
        if not self.config:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Configuração não carregada"
            )
        
        compliance_config = self.config.compliance_config
        issues = []
        
        # Validar padrões de compliance
        compliance_patterns = ['pci_dss', 'lgpd', 'gdpr', 'sox', 'hipaa']
        found_patterns = []
        
        for pattern in compliance_patterns:
            if pattern in compliance_config:
                found_patterns.append(pattern)
                config_value = compliance_config[pattern]
                if not isinstance(config_value, dict):
                    issues.append(f"Configuração '{pattern}' deve ser um objeto")
        
        if not found_patterns:
            issues.append("Nenhum padrão de compliance configurado")
        
        # Validar configurações específicas
        for pattern, config in compliance_config.items():
            if isinstance(config, dict):
                if 'enabled' in config and not isinstance(config['enabled'], bool):
                    issues.append(f"Campo 'enabled' em '{pattern}' deve ser booleano")
                
                if 'strict_mode' in config and not isinstance(config['strict_mode'], bool):
                    issues.append(f"Campo 'strict_mode' em '{pattern}' deve ser booleano")
        
        if issues:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Problemas encontrados na configuração de compliance",
                details={"issues": issues}
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message=f"Configuração de compliance válida ({len(found_patterns)} padrões)"
        )
    
    def validate_all(self) -> List[ValidationResult]:
        """
        Executa todas as validações
        
        Returns:
            Lista de ValidationResult com todos os resultados
        """
        self.validation_results = []
        
        # Carregar configuração
        load_result = self.load_config()
        self.validation_results.append(load_result)
        
        if not load_result.is_valid:
            return self.validation_results
        
        # Executar validações
        validations = [
            self.validate_sensitive_files,
            self.validate_patterns,
            self.validate_semantic_threshold,
            self.validate_rollback_config,
            self.validate_compliance_config
        ]
        
        for validation_func in validations:
            result = validation_func()
            self.validation_results.append(result)
            logger.info(f"Validação {validation_func.__name__}: {result.message}")
        
        return self.validation_results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo das validações
        
        Returns:
            Dicionário com resumo das validações
        """
        if not self.validation_results:
            return {"error": "Nenhuma validação executada"}
        
        total_validations = len(self.validation_results)
        errors = [r for r in self.validation_results if r.severity == ValidationSeverity.ERROR]
        warnings = [r for r in self.validation_results if r.severity == ValidationSeverity.WARNING]
        infos = [r for r in self.validation_results if r.severity == ValidationSeverity.INFO]
        
        is_overall_valid = all(r.is_valid for r in self.validation_results)
        
        return {
            "overall_valid": is_overall_valid,
            "total_validations": total_validations,
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(infos),
            "details": {
                "errors": [{"message": r.message, "details": r.details} for r in errors],
                "warnings": [{"message": r.message, "details": r.details} for r in warnings],
                "infos": [{"message": r.message, "details": r.details} for r in infos]
            }
        }
    
    def generate_report(self) -> str:
        """
        Gera um relatório de validação em formato texto
        
        Returns:
            String com o relatório formatado
        """
        summary = self.get_summary()
        
        report = f"""
=== RELATÓRIO DE VALIDAÇÃO DE TRIGGER CONFIG ===
Data: {self.config_path}
Status Geral: {'✅ VÁLIDO' if summary['overall_valid'] else '❌ INVÁLIDO'}

Estatísticas:
- Total de validações: {summary['total_validations']}
- Erros: {summary['errors']}
- Avisos: {summary['warnings']}
- Informações: {summary['infos']}

Detalhes:
"""
        
        if summary['details']['errors']:
            report += "\n❌ ERROS:\n"
            for error in summary['details']['errors']:
                report += f"  - {error['message']}\n"
                if error['details']:
                    report += f"    Detalhes: {error['details']}\n"
        
        if summary['details']['warnings']:
            report += "\n⚠️ AVISOS:\n"
            for warning in summary['details']['warnings']:
                report += f"  - {warning['message']}\n"
                if warning['details']:
                    report += f"    Detalhes: {warning['details']}\n"
        
        if summary['details']['infos']:
            report += "\nℹ️ INFORMAÇÕES:\n"
            for info in summary['details']['infos']:
                report += f"  - {info['message']}\n"
        
        return report


def main():
    """Função principal para execução standalone"""
    validator = TriggerConfigValidator()
    results = validator.validate_all()
    
    print(validator.generate_report())
    
    # Retornar código de saída apropriado
    summary = validator.get_summary()
    return 0 if summary['overall_valid'] else 1


if __name__ == "__main__":
    exit(main()) 