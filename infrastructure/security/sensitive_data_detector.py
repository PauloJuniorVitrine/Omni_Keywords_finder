"""
Sistema de Detecção de Dados Sensíveis para Documentação Enterprise
Tracing ID: SENSITIVE_DATA_DETECTOR_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa o sistema de detecção e mascaramento de dados sensíveis
em documentação, seguindo padrões enterprise de segurança e compliance
(PCI-DSS, LGPD, GDPR).
"""

import os
import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Union, Any, Set
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from shared.logger import logger
from shared.config import BASE_DIR

class SensitivityLevel(Enum):
    """Níveis de sensibilidade dos dados."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SensitiveDataPattern:
    """
    Padrão para detecção de dados sensíveis.
    
    Define um padrão regex e suas características de sensibilidade.
    """
    name: str
    pattern: str
    description: str
    sensitivity_level: SensitivityLevel
    replacement_template: str
    examples: List[str]
    compliance_standards: List[str]  # PCI-DSS, LGPD, GDPR, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return asdict(self)

@dataclass
class DetectedSensitiveData:
    """
    Dados sensíveis detectados.
    
    Registra informações sobre dados sensíveis encontrados.
    """
    pattern_name: str
    sensitivity_level: SensitivityLevel
    original_value: str
    masked_value: str
    line_number: Optional[int]
    file_path: str
    context: str
    timestamp: str
    compliance_standards: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return asdict(self)

class SensitiveDataDetector:
    """
    Detector de dados sensíveis para documentação enterprise.
    
    Implementa detecção baseada em:
    - Padrões regex configuráveis
    - Múltiplos níveis de sensibilidade
    - Compliance com padrões internacionais
    - Mascaramento inteligente
    - Auditoria completa
    """
    
    def __init__(self, 
                 config_file: Optional[str] = None,
                 enable_ai_detection: bool = False,
                 log_incidents: bool = True):
        """
        Inicializa o detector de dados sensíveis.
        
        Args:
            config_file: Arquivo de configuração de padrões
            enable_ai_detection: Se deve usar detecção por IA
            log_incidents: Se deve registrar incidentes
        """
        self.enable_ai_detection = enable_ai_detection
        self.log_incidents = log_incidents
        self.detection_history: List[DetectedSensitiveData] = []
        self.incident_count = 0
        
        # Carregar padrões padrão
        self.patterns = self._load_default_patterns()
        
        # Carregar configuração personalizada se fornecida
        if config_file and os.path.exists(config_file):
            self._load_custom_patterns(config_file)
        
        # Compilar padrões regex para performance
        self._compile_patterns()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "sensitive_data_detector_initialized",
            "status": "success",
            "source": "SensitiveDataDetector.__init__",
            "details": {
                "patterns_loaded": len(self.patterns),
                "enable_ai_detection": enable_ai_detection,
                "log_incidents": log_incidents
            }
        })
    
    def _load_default_patterns(self) -> List[SensitiveDataPattern]:
        """
        Carrega padrões padrão de detecção.
        
        Returns:
            Lista de padrões padrão
        """
        return [
            # AWS Access Keys
            SensitiveDataPattern(
                name="aws_access_key",
                pattern=r'AKIA[0-9A-Z]{16}',
                description="AWS Access Key ID",
                sensitivity_level=SensitivityLevel.CRITICAL,
                replacement_template="AKIA[MASKED]",
                examples=["AKIAIOSFODNN7EXAMPLE"],
                compliance_standards=["PCI-DSS", "ISO-27001"]
            ),
            
            # AWS Secret Keys
            SensitiveDataPattern(
                name="aws_secret_key",
                pattern=r'[0-9a-zA-Z/+]{40}',
                description="AWS Secret Access Key",
                sensitivity_level=SensitivityLevel.CRITICAL,
                replacement_template="[MASKED_SECRET_KEY]",
                examples=["wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"],
                compliance_standards=["PCI-DSS", "ISO-27001"]
            ),
            
            # Google API Keys
            SensitiveDataPattern(
                name="google_api_key",
                pattern=r'AIza[0-9A-Za-data-_]{35}',
                description="Google API Key",
                sensitivity_level=SensitivityLevel.HIGH,
                replacement_template="AIza[MASKED]",
                examples=["AIzaSyBOti4mM-6x9WDnZIjIeyEU2Op8jS0PcA"],
                compliance_standards=["PCI-DSS"]
            ),
            
            # Passwords (genérico)
            SensitiveDataPattern(
                name="password_generic",
                pattern=r'(?index)(password|senha|pwd)\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',
                description="Password field",
                sensitivity_level=SensitivityLevel.HIGH,
                replacement_template="password: [MASKED]",
                examples=["password: mysecret123", "senha=123456"],
                compliance_standards=["PCI-DSS", "LGPD", "GDPR"]
            ),
            
            # Secrets (genérico)
            SensitiveDataPattern(
                name="secret_generic",
                pattern=r'(?index)(secret|token|key)\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',
                description="Generic secret field",
                sensitivity_level=SensitivityLevel.HIGH,
                replacement_template="secret: [MASKED]",
                examples=["secret: abc123", "token=xyz789"],
                compliance_standards=["PCI-DSS", "LGPD", "GDPR"]
            ),
            
            # CPF (Brasil)
            SensitiveDataPattern(
                name="cpf_brazil",
                pattern=r'\b\data{3}\.?\data{3}\.?\data{3}-?\data{2}\b',
                description="CPF (Brazilian ID)",
                sensitivity_level=SensitivityLevel.CRITICAL,
                replacement_template="[MASKED_CPF]",
                examples=["123.456.789-00", "12345678900"],
                compliance_standards=["LGPD"]
            ),
            
            # CNPJ (Brasil)
            SensitiveDataPattern(
                name="cnpj_brazil",
                pattern=r'\b\data{2}\.?\data{3}\.?\data{3}/?0001-?\data{2}\b',
                description="CNPJ (Brazilian Company ID)",
                sensitivity_level=SensitivityLevel.HIGH,
                replacement_template="[MASKED_CNPJ]",
                examples=["12.345.678/0001-90", "12345678000190"],
                compliance_standards=["LGPD"]
            ),
            
            # Credit Card Numbers
            SensitiveDataPattern(
                name="credit_card",
                pattern=r'\b\data{4}[-\string_data]?\data{4}[-\string_data]?\data{4}[-\string_data]?\data{4}\b',
                description="Credit Card Number",
                sensitivity_level=SensitivityLevel.CRITICAL,
                replacement_template="[MASKED_CC]",
                examples=["4111-1111-1111-1111", "4111111111111111"],
                compliance_standards=["PCI-DSS"]
            ),
            
            # Email Addresses (em contexto sensível)
            SensitiveDataPattern(
                name="email_sensitive",
                pattern=r'(?index)(email|e-mail)\string_data*[:=]\string_data*["\']?[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}["\']?',
                description="Email in sensitive context",
                sensitivity_level=SensitivityLevel.MEDIUM,
                replacement_template="email: [MASKED_EMAIL]",
                examples=["email: user@example.com"],
                compliance_standards=["LGPD", "GDPR"]
            ),
            
            # Phone Numbers
            SensitiveDataPattern(
                name="phone_number",
                pattern=r'(?index)(phone|telefone|tel)\string_data*[:=]\string_data*["\']?[\+]?[\data\string_data\-\(\)]{10,}["\']?',
                description="Phone Number",
                sensitivity_level=SensitivityLevel.MEDIUM,
                replacement_template="phone: [MASKED_PHONE]",
                examples=["phone: +55 11 99999-9999", "telefone: (11) 99999-9999"],
                compliance_standards=["LGPD", "GDPR"]
            ),
            
            # Database Connection Strings
            SensitiveDataPattern(
                name="db_connection",
                pattern=r'(?index)(mysql|postgresql|mongodb|redis)://[^/\string_data]+:[^@\string_data]+@[^\string_data]+',
                description="Database Connection String",
                sensitivity_level=SensitivityLevel.CRITICAL,
                replacement_template="[MASKED_DB_CONNECTION]",
                examples=["mysql://user:pass@localhost:3306/db"],
                compliance_standards=["PCI-DSS", "ISO-27001"]
            ),
            
            # JWT Tokens
            SensitiveDataPattern(
                name="jwt_token",
                pattern=r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
                description="JWT Token",
                sensitivity_level=SensitivityLevel.HIGH,
                replacement_template="[MASKED_JWT]",
                examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
                compliance_standards=["PCI-DSS"]
            ),
            
            # Private Keys
            SensitiveDataPattern(
                name="private_key",
                pattern=r'-----BEGIN\string_data+(RSA\string_data+)?PRIVATE\string_data+KEY-----[\string_data\S]*?-----END\string_data+(RSA\string_data+)?PRIVATE\string_data+KEY-----',
                description="Private Key",
                sensitivity_level=SensitivityLevel.CRITICAL,
                replacement_template="[MASKED_PRIVATE_KEY]",
                examples=["-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSj..."],
                compliance_standards=["PCI-DSS", "ISO-27001"]
            ),
            
            # API Keys (genérico)
            SensitiveDataPattern(
                name="api_key_generic",
                pattern=r'(?index)(api[_-]?key|apikey)\string_data*[:=]\string_data*["\']?[a-zA-Z0-9_-]{20,}["\']?',
                description="Generic API Key",
                sensitivity_level=SensitivityLevel.HIGH,
                replacement_template="api_key: [MASKED]",
                examples=["api_key: abc123def456ghi789", "API_KEY=xyz789abc123"],
                compliance_standards=["PCI-DSS"]
            )
        ]
    
    def _load_custom_patterns(self, config_file: str) -> None:
        """
        Carrega padrões personalizados de arquivo de configuração.
        
        Args:
            config_file: Caminho do arquivo de configuração
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            custom_patterns = config.get('patterns', [])
            
            for pattern_data in custom_patterns:
                pattern = SensitiveDataPattern(
                    name=pattern_data['name'],
                    pattern=pattern_data['pattern'],
                    description=pattern_data['description'],
                    sensitivity_level=SensitivityLevel(pattern_data['sensitivity_level']),
                    replacement_template=pattern_data['replacement_template'],
                    examples=pattern_data.get('examples', []),
                    compliance_standards=pattern_data.get('compliance_standards', [])
                )
                self.patterns.append(pattern)
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "custom_patterns_loaded",
                "status": "success",
                "source": "SensitiveDataDetector._load_custom_patterns",
                "details": {
                    "config_file": config_file,
                    "patterns_loaded": len(custom_patterns)
                }
            })
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "custom_patterns_load_failed",
                "status": "error",
                "source": "SensitiveDataDetector._load_custom_patterns",
                "details": {
                    "config_file": config_file,
                    "error": str(e)
                }
            })
    
    def _compile_patterns(self) -> None:
        """
        Compila padrões regex para melhor performance.
        """
        for pattern in self.patterns:
            try:
                pattern.compiled_regex = re.compile(pattern.pattern, re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "pattern_compilation_failed",
                    "status": "error",
                    "source": "SensitiveDataDetector._compile_patterns",
                    "details": {
                        "pattern_name": pattern.name,
                        "pattern": pattern.pattern,
                        "error": str(e)
                    }
                })
    
    def _generate_masked_value(self, 
                             original_value: str, 
                             pattern: SensitiveDataPattern) -> str:
        """
        Gera valor mascarado para dados sensíveis.
        
        Args:
            original_value: Valor original
            pattern: Padrão de detecção
            
        Returns:
            Valor mascarado
        """
        # Usar template de substituição se fornecido
        if pattern.replacement_template:
            return pattern.replacement_template
        
        # Mascaramento padrão baseado no tipo
        if "key" in pattern.name.lower():
            if len(original_value) > 8:
                return original_value[:4] + "[MASKED]" + original_value[-4:]
            else:
                return "[MASKED_KEY]"
        elif "password" in pattern.name.lower() or "secret" in pattern.name.lower():
            return "[MASKED_PASSWORD]"
        elif "email" in pattern.name.lower():
            parts = original_value.split('@')
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                if len(username) > 2:
                    masked_username = username[:2] + "[MASKED]"
                else:
                    masked_username = "[MASKED]"
                return f"{masked_username}@{domain}"
            else:
                return "[MASKED_EMAIL]"
        elif "phone" in pattern.name.lower():
            return "[MASKED_PHONE]"
        elif "cpf" in pattern.name.lower():
            return "[MASKED_CPF]"
        elif "cnpj" in pattern.name.lower():
            return "[MASKED_CNPJ]"
        elif "credit" in pattern.name.lower():
            return "[MASKED_CC]"
        else:
            # Mascaramento genérico
            if len(original_value) > 6:
                return original_value[:3] + "[MASKED]" + original_value[-3:]
            else:
                return "[MASKED]"
    
    def scan_text(self, 
                  text: str, 
                  file_path: str = "unknown",
                  context_lines: int = 3) -> List[DetectedSensitiveData]:
        """
        Escaneia texto em busca de dados sensíveis.
        
        Args:
            text: Texto para escanear
            file_path: Caminho do arquivo (para auditoria)
            context_lines: Número de linhas de contexto
            
        Returns:
            Lista de dados sensíveis detectados
        """
        detected_data = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.patterns:
                if hasattr(pattern, 'compiled_regex'):
                    matches = pattern.compiled_regex.finditer(line)
                    
                    for match in matches:
                        original_value = match.group(0)
                        masked_value = self._generate_masked_value(original_value, pattern)
                        
                        # Gerar contexto
                        start_line = max(1, line_num - context_lines)
                        end_line = min(len(lines), line_num + context_lines)
                        context_lines_list = lines[start_line-1:end_line]
                        context = '\n'.join(context_lines_list)
                        
                        # Criar registro de detecção
                        detected = DetectedSensitiveData(
                            pattern_name=pattern.name,
                            sensitivity_level=pattern.sensitivity_level,
                            original_value=original_value,
                            masked_value=masked_value,
                            line_number=line_num,
                            file_path=file_path,
                            context=context,
                            timestamp=datetime.utcnow().isoformat(),
                            compliance_standards=pattern.compliance_standards
                        )
                        
                        detected_data.append(detected)
                        
                        # Registrar incidente se configurado
                        if self.log_incidents:
                            self._log_incident(detected)
        
        # Adicionar ao histórico
        self.detection_history.extend(detected_data)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "text_scan_completed",
            "status": "success",
            "source": "SensitiveDataDetector.scan_text",
            "details": {
                "file_path": file_path,
                "detections_count": len(detected_data),
                "text_length": len(text)
            }
        })
        
        return detected_data
    
    def scan_file(self, file_path: str) -> List[DetectedSensitiveData]:
        """
        Escaneia arquivo em busca de dados sensíveis.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Lista de dados sensíveis detectados
            
        Raises:
            FileNotFoundError: Se arquivo não for encontrado
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.scan_text(content, file_path)
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "file_scan_failed",
                "status": "error",
                "source": "SensitiveDataDetector.scan_file",
                "details": {
                    "file_path": file_path,
                    "error": str(e)
                }
            })
            raise
    
    def scan_directory(self, 
                      directory_path: str, 
                      file_extensions: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None) -> Dict[str, List[DetectedSensitiveData]]:
        """
        Escaneia diretório em busca de dados sensíveis.
        
        Args:
            directory_path: Caminho do diretório
            file_extensions: Extensões de arquivo para incluir
            exclude_patterns: Padrões para excluir
            
        Returns:
            Dicionário com resultados por arquivo
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Diretório não encontrado: {directory_path}")
        
        results = {}
        scanned_files = 0
        
        for root, dirs, files in os.walk(directory_path):
            # Aplicar filtros de exclusão
            if exclude_patterns:
                dirs[:] = [data for data in dirs if not any(re.search(pattern, data) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Verificar extensão
                if file_extensions:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext not in file_extensions:
                        continue
                
                # Verificar padrões de exclusão
                if exclude_patterns and any(re.search(pattern, file_path) for pattern in exclude_patterns):
                    continue
                
                try:
                    detections = self.scan_file(file_path)
                    if detections:
                        results[file_path] = detections
                    scanned_files += 1
                    
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "file_scan_skipped",
                        "status": "warning",
                        "source": "SensitiveDataDetector.scan_directory",
                        "details": {
                            "file_path": file_path,
                            "error": str(e)
                        }
                    })
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "directory_scan_completed",
            "status": "success",
            "source": "SensitiveDataDetector.scan_directory",
            "details": {
                "directory_path": directory_path,
                "scanned_files": scanned_files,
                "files_with_detections": len(results)
            }
        })
        
        return results
    
    def mask_sensitive_data(self, text: str, file_path: str = "unknown") -> Tuple[str, List[DetectedSensitiveData]]:
        """
        Mascara dados sensíveis em texto.
        
        Args:
            text: Texto para mascarar
            file_path: Caminho do arquivo (para auditoria)
            
        Returns:
            Tupla (texto mascarado, lista de detecções)
        """
        detected_data = self.scan_text(text, file_path)
        masked_text = text
        
        # Aplicar mascaramento em ordem reversa para não afetar índices
        for detection in reversed(detected_data):
            masked_text = masked_text.replace(detection.original_value, detection.masked_value)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "text_masking_completed",
            "status": "success",
            "source": "SensitiveDataDetector.mask_sensitive_data",
            "details": {
                "file_path": file_path,
                "detections_count": len(detected_data),
                "original_length": len(text),
                "masked_length": len(masked_text)
            }
        })
        
        return masked_text, detected_data
    
    def _log_incident(self, detection: DetectedSensitiveData) -> None:
        """
        Registra incidente de dados sensíveis.
        
        Args:
            detection: Dados sensíveis detectados
        """
        self.incident_count += 1
        
        logger.warning({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "sensitive_data_incident",
            "status": "warning",
            "source": "SensitiveDataDetector._log_incident",
            "details": {
                "incident_id": f"INC_{self.incident_count:06d}",
                "pattern_name": detection.pattern_name,
                "sensitivity_level": detection.sensitivity_level.value,
                "file_path": detection.file_path,
                "line_number": detection.line_number,
                "compliance_standards": detection.compliance_standards,
                "original_value_length": len(detection.original_value)
            }
        })
    
    def get_detection_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo das detecções realizadas.
        
        Returns:
            Dicionário com estatísticas das detecções
        """
        if not self.detection_history:
            return {"message": "Nenhuma detecção realizada ainda"}
        
        # Estatísticas por nível de sensibilidade
        level_counts = {}
        pattern_counts = {}
        file_counts = {}
        compliance_counts = {}
        
        for detection in self.detection_history:
            # Contar por nível
            level = detection.sensitivity_level.value
            level_counts[level] = level_counts.get(level, 0) + 1
            
            # Contar por padrão
            pattern_counts[detection.pattern_name] = pattern_counts.get(detection.pattern_name, 0) + 1
            
            # Contar por arquivo
            file_counts[detection.file_path] = file_counts.get(detection.file_path, 0) + 1
            
            # Contar por padrão de compliance
            for standard in detection.compliance_standards:
                compliance_counts[standard] = compliance_counts.get(standard, 0) + 1
        
        return {
            "total_detections": len(self.detection_history),
            "incident_count": self.incident_count,
            "by_sensitivity_level": level_counts,
            "by_pattern": pattern_counts,
            "by_file": file_counts,
            "by_compliance_standard": compliance_counts,
            "first_detection": self.detection_history[0].timestamp if self.detection_history else None,
            "last_detection": self.detection_history[-1].timestamp if self.detection_history else None
        }
    
    def export_detection_report(self, 
                               output_path: str,
                               format: str = "json") -> str:
        """
        Exporta relatório de detecções.
        
        Args:
            output_path: Caminho do arquivo de saída
            format: Formato de saída ('json' ou 'csv')
            
        Returns:
            Caminho do arquivo exportado
        """
        try:
            if format.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "report_timestamp": datetime.utcnow().isoformat(),
                        "summary": self.get_detection_summary(),
                        "detections": [detection.to_dict() for detection in self.detection_history]
                    }, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp', 'pattern_name', 'sensitivity_level', 
                        'file_path', 'line_number', 'compliance_standards'
                    ])
                    
                    for detection in self.detection_history:
                        writer.writerow([
                            detection.timestamp,
                            detection.pattern_name,
                            detection.sensitivity_level.value,
                            detection.file_path,
                            detection.line_number,
                            ','.join(detection.compliance_standards)
                        ])
            
            else:
                raise ValueError(f"Formato não suportado: {format}")
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "detection_report_exported",
                "status": "success",
                "source": "SensitiveDataDetector.export_detection_report",
                "details": {
                    "output_path": output_path,
                    "format": format,
                    "detections_count": len(self.detection_history)
                }
            })
            
            return output_path
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "detection_report_export_failed",
                "status": "error",
                "source": "SensitiveDataDetector.export_detection_report",
                "details": {
                    "output_path": output_path,
                    "format": format,
                    "error": str(e)
                }
            })
            raise
    
    def clear_history(self) -> None:
        """
        Limpa histórico de detecções.
        """
        self.detection_history.clear()
        self.incident_count = 0
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "detection_history_cleared",
            "status": "success",
            "source": "SensitiveDataDetector.clear_history",
            "details": {}
        }) 