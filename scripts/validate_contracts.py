"""
🔍 Contract Validation Script
🎯 Objetivo: Validação automática de contratos e detecção de breaking changes
📅 Data: 2025-01-27
🔗 Tracing ID: VALIDATE_CONTRACTS_001
📋 Ruleset: enterprise_control_layer.yaml
"""

import json
import os
import sys
import logging
import argparse
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hashlib
import difflib
from pathlib import Path
import yaml
import jsonschema
from jsonschema import validate, ValidationError
import requests
from dataclasses_json import dataclass_json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data'
)
logger = logging.getLogger(__name__)

class ChangeType(Enum):
    """Tipos de mudanças em contratos"""
    ADDITIVE = "additive"           # Nova funcionalidade (não breaking)
    BREAKING = "breaking"           # Mudança que quebra compatibilidade
    DEPRECATION = "deprecation"     # Deprecação (warning)
    REFACTOR = "refactor"           # Refatoração interna
    DOCUMENTATION = "documentation" # Mudança apenas na documentação

class ContractType(Enum):
    """Tipos de contratos"""
    API_SCHEMA = "api_schema"
    DATABASE_SCHEMA = "database_schema"
    EVENT_SCHEMA = "event_schema"
    CONFIG_SCHEMA = "config_schema"
    INTERFACE = "interface"

@dataclass_json
@dataclass
class ContractDefinition:
    """Definição de um contrato"""
    name: str
    type: ContractType
    version: str
    schema: Dict[str, Any]
    description: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    hash: str
    dependencies: List[str] = None
    breaking_changes: List[str] = None

@dataclass_json
@dataclass
class ContractChange:
    """Mudança detectada em um contrato"""
    contract_name: str
    contract_type: ContractType
    change_type: ChangeType
    field_path: str
    old_value: Any
    new_value: Any
    description: str
    severity: str
    impact: str
    migration_guide: Optional[str] = None

@dataclass_json
@dataclass
class ValidationReport:
    """Relatório de validação de contratos"""
    timestamp: datetime
    total_contracts: int
    validated_contracts: int
    failed_contracts: int
    breaking_changes: int
    warnings: int
    changes: List[ContractChange]
    summary: Dict[str, Any]
    recommendations: List[str]

class ContractValidator:
    """Validador de contratos com detecção de breaking changes"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.contracts_dir = self.base_path / "contracts"
        self.reports_dir = self.base_path / "reports"
        self.cache_dir = self.base_path / ".contract_cache"
        
        # Criar diretórios se não existirem
        self.contracts_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache de contratos
        self.contract_cache: Dict[str, ContractDefinition] = {}
        self._load_contract_cache()
    
    def _load_contract_cache(self):
        """Carrega cache de contratos"""
        cache_file = self.cache_dir / "contracts.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    for contract_data in data.values():
                        contract = ContractDefinition.from_dict(contract_data)
                        self.contract_cache[contract.name] = contract
                logger.info(f"[CONTRACT_VALIDATOR] Cache carregado: {len(self.contract_cache)} contratos")
            except Exception as e:
                logger.warning(f"[CONTRACT_VALIDATOR] Erro ao carregar cache: {str(e)}")
    
    def _save_contract_cache(self):
        """Salva cache de contratos"""
        cache_file = self.cache_dir / "contracts.json"
        try:
            data = {
                name: contract.to_dict() 
                for name, contract in self.contract_cache.items()
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"[CONTRACT_VALIDATOR] Erro ao salvar cache: {str(e)}")
    
    def discover_contracts(self) -> List[ContractDefinition]:
        """Descobre contratos no projeto"""
        contracts = []
        
        # Procurar por arquivos de contrato
        contract_patterns = [
            "**/*.schema.json",
            "**/*.contract.json", 
            "**/api-schema.json",
            "**/openapi.yaml",
            "**/openapi.yml",
            "**/swagger.yaml",
            "**/swagger.yml"
        ]
        
        for pattern in contract_patterns:
            for file_path in self.base_path.rglob(pattern):
                try:
                    contract = self._parse_contract_file(file_path)
                    if contract:
                        contracts.append(contract)
                except Exception as e:
                    logger.error(f"[CONTRACT_VALIDATOR] Erro ao processar {file_path}: {str(e)}")
        
        # Procurar por contratos TypeScript
        ts_patterns = [
            "**/*.types.ts",
            "**/*.interface.ts",
            "**/types/*.ts"
        ]
        
        for pattern in ts_patterns:
            for file_path in self.base_path.rglob(pattern):
                try:
                    contract = self._parse_typescript_contract(file_path)
                    if contract:
                        contracts.append(contract)
                except Exception as e:
                    logger.error(f"[CONTRACT_VALIDATOR] Erro ao processar {file_path}: {str(e)}")
        
        logger.info(f"[CONTRACT_VALIDATOR] {len(contracts)} contratos descobertos")
        return contracts
    
    def _parse_contract_file(self, file_path: Path) -> Optional[ContractDefinition]:
        """Processa arquivo de contrato"""
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Determinar tipo de contrato
            contract_type = self._determine_contract_type(file_path, data)
            
            # Gerar hash do conteúdo
            content_hash = self._generate_content_hash(data)
            
            # Extrair metadados
            name = data.get('title', file_path.stem)
            version = data.get('version', '1.0.0')
            description = data.get('description', f'Contract from {file_path}')
            tags = data.get('tags', [])
            
            contract = ContractDefinition(
                name=name,
                type=contract_type,
                version=version,
                schema=data,
                description=description,
                tags=tags,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                hash=content_hash
            )
            
            return contract
            
        except Exception as e:
            logger.error(f"[CONTRACT_VALIDATOR] Erro ao processar {file_path}: {str(e)}")
            return None
    
    def _parse_typescript_contract(self, file_path: Path) -> Optional[ContractDefinition]:
        """Processa contrato TypeScript"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extrair interfaces e tipos
            interfaces = self._extract_typescript_interfaces(content)
            
            if not interfaces:
                return None
            
            # Converter para schema JSON
            schema = self._convert_typescript_to_schema(interfaces)
            
            # Gerar hash
            content_hash = self._generate_content_hash(content)
            
            contract = ContractDefinition(
                name=file_path.stem,
                type=ContractType.INTERFACE,
                version='1.0.0',
                schema=schema,
                description=f'TypeScript interfaces from {file_path}',
                tags=['typescript', 'interface'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                hash=content_hash
            )
            
            return contract
            
        except Exception as e:
            logger.error(f"[CONTRACT_VALIDATOR] Erro ao processar TypeScript {file_path}: {str(e)}")
            return None
    
    def _determine_contract_type(self, file_path: Path, data: Dict[str, Any]) -> ContractType:
        """Determina o tipo de contrato baseado no arquivo e conteúdo"""
        file_name = file_path.name.lower()
        
        if 'openapi' in file_name or 'swagger' in file_name:
            return ContractType.API_SCHEMA
        elif 'database' in file_name or 'db' in file_name:
            return ContractType.DATABASE_SCHEMA
        elif 'event' in file_name or 'message' in file_name:
            return ContractType.EVENT_SCHEMA
        elif 'config' in file_name:
            return ContractType.CONFIG_SCHEMA
        else:
            # Tentar determinar pelo conteúdo
            if 'paths' in data or 'openapi' in data:
                return ContractType.API_SCHEMA
            elif 'tables' in data or 'columns' in data:
                return ContractType.DATABASE_SCHEMA
            elif 'events' in data or 'messages' in data:
                return ContractType.EVENT_SCHEMA
            else:
                return ContractType.INTERFACE
    
    def _generate_content_hash(self, content: Any) -> str:
        """Gera hash do conteúdo"""
        if isinstance(content, str):
            content_str = content
        else:
            content_str = json.dumps(content, sort_keys=True)
        
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    def _extract_typescript_interfaces(self, content: str) -> Dict[str, Any]:
        """Extrai interfaces TypeScript do código"""
        interfaces = {}
        
        # Padrões para interfaces
        import re
        
        # Interface pattern
        interface_pattern = r'interface\string_data+(\w+)\string_data*\{([^}]+)\}'
        type_pattern = r'type\string_data+(\w+)\string_data*=\string_data*([^;]+);'
        
        # Encontrar interfaces
        for match in re.finditer(interface_pattern, content, re.DOTALL):
            name = match.group(1)
            body = match.group(2)
            interfaces[name] = self._parse_typescript_body(body)
        
        # Encontrar tipos
        for match in re.finditer(type_pattern, content, re.DOTALL):
            name = match.group(1)
            definition = match.group(2)
            interfaces[name] = self._parse_typescript_type(definition)
        
        return interfaces
    
    def _parse_typescript_body(self, body: str) -> Dict[str, Any]:
        """Processa corpo de interface TypeScript"""
        properties = {}
        
        for line in body.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('//'):
                parts = line.split(':')
                if len(parts) >= 2:
                    prop_name = parts[0].strip()
                    prop_type = parts[1].strip().rstrip(';').rstrip(',')
                    properties[prop_name] = self._parse_typescript_type(prop_type)
        
        return {
            "type": "object",
            "properties": properties,
            "required": list(properties.keys())
        }
    
    def _parse_typescript_type(self, type_def: str) -> Dict[str, Any]:
        """Converte tipo TypeScript para schema JSON"""
        type_def = type_def.strip()
        
        if type_def == 'string':
            return {"type": "string"}
        elif type_def == 'number':
            return {"type": "number"}
        elif type_def == 'boolean':
            return {"type": "boolean"}
        elif type_def.startswith('string[]') or type_def.endswith('[]'):
            return {
                "type": "array",
                "items": {"type": "string"}
            }
        elif type_def.startswith('number[]'):
            return {
                "type": "array", 
                "items": {"type": "number"}
            }
        elif type_def == 'any':
            return {"type": "object"}
        else:
            return {"type": "string"}  # Fallback
    
    def _convert_typescript_to_schema(self, interfaces: Dict[str, Any]) -> Dict[str, Any]:
        """Converte interfaces TypeScript para schema JSON"""
        return {
            "type": "object",
            "definitions": interfaces,
            "properties": interfaces
        }
    
    def validate_contracts(self, contracts: List[ContractDefinition]) -> ValidationReport:
        """Valida contratos e detecta mudanças"""
        changes = []
        validated_count = 0
        failed_count = 0
        breaking_count = 0
        warnings_count = 0
        
        for contract in contracts:
            try:
                contract_changes = self._validate_single_contract(contract)
                changes.extend(contract_changes)
                
                # Contar tipos de mudanças
                for change in contract_changes:
                    if change.change_type == ChangeType.BREAKING:
                        breaking_count += 1
                    elif change.change_type == ChangeType.DEPRECATION:
                        warnings_count += 1
                
                validated_count += 1
                
            except Exception as e:
                logger.error(f"[CONTRACT_VALIDATOR] Erro ao validar {contract.name}: {str(e)}")
                failed_count += 1
        
        # Gerar resumo
        summary = {
            "total_contracts": len(contracts),
            "validated_contracts": validated_count,
            "failed_contracts": failed_count,
            "breaking_changes": breaking_count,
            "warnings": warnings_count,
            "changes_by_type": self._group_changes_by_type(changes),
            "changes_by_severity": self._group_changes_by_severity(changes)
        }
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(changes, summary)
        
        report = ValidationReport(
            timestamp=datetime.utcnow(),
            total_contracts=len(contracts),
            validated_contracts=validated_count,
            failed_contracts=failed_count,
            breaking_changes=breaking_count,
            warnings=warnings_count,
            changes=changes,
            summary=summary,
            recommendations=recommendations
        )
        
        return report
    
    def _validate_single_contract(self, contract: ContractDefinition) -> List[ContractChange]:
        """Valida um contrato individual"""
        changes = []
        
        # Verificar se contrato existe no cache
        if contract.name in self.contract_cache:
            cached_contract = self.contract_cache[contract.name]
            
            # Comparar hashes
            if contract.hash != cached_contract.hash:
                # Detectar mudanças específicas
                contract_changes = self._detect_schema_changes(
                    cached_contract.schema,
                    contract.schema,
                    contract.name,
                    contract.type
                )
                changes.extend(contract_changes)
        
        # Validar schema interno
        schema_errors = self._validate_schema_integrity(contract)
        for error in schema_errors:
            changes.append(ContractChange(
                contract_name=contract.name,
                contract_type=contract.type,
                change_type=ChangeType.BREAKING,
                field_path=error.get('path', ''),
                old_value=None,
                new_value=None,
                description=f"Schema validation error: {error.get('message', '')}",
                severity='error',
                impact='high'
            ))
        
        # Atualizar cache
        self.contract_cache[contract.name] = contract
        
        return changes
    
    def _detect_schema_changes(
        self, 
        old_schema: Dict[str, Any], 
        new_schema: Dict[str, Any], 
        contract_name: str, 
        contract_type: ContractType
    ) -> List[ContractChange]:
        """Detecta mudanças entre dois schemas"""
        changes = []
        
        # Comparar propriedades
        old_props = self._extract_properties(old_schema)
        new_props = self._extract_properties(new_schema)
        
        # Propriedades removidas (breaking)
        removed_props = old_props - new_props
        for prop in removed_props:
            changes.append(ContractChange(
                contract_name=contract_name,
                contract_type=contract_type,
                change_type=ChangeType.BREAKING,
                field_path=prop,
                old_value=old_schema.get(prop),
                new_value=None,
                description=f"Property '{prop}' was removed",
                severity='error',
                impact='high',
                migration_guide=f"Update code to remove references to '{prop}'"
            ))
        
        # Propriedades adicionadas (additive)
        added_props = new_props - old_props
        for prop in added_props:
            changes.append(ContractChange(
                contract_name=contract_name,
                contract_type=contract_type,
                change_type=ChangeType.ADDITIVE,
                field_path=prop,
                old_value=None,
                new_value=new_schema.get(prop),
                description=f"Property '{prop}' was added",
                severity='info',
                impact='low'
            ))
        
        # Propriedades modificadas
        common_props = old_props & new_props
        for prop in common_props:
            old_value = old_schema.get(prop)
            new_value = new_schema.get(prop)
            
            if old_value != new_value:
                change_type = self._determine_change_type(old_value, new_value)
                changes.append(ContractChange(
                    contract_name=contract_name,
                    contract_type=contract_type,
                    change_type=change_type,
                    field_path=prop,
                    old_value=old_value,
                    new_value=new_value,
                    description=f"Property '{prop}' was modified",
                    severity='warning' if change_type == ChangeType.BREAKING else 'info',
                    impact='medium' if change_type == ChangeType.BREAKING else 'low'
                ))
        
        return changes
    
    def _extract_properties(self, schema: Dict[str, Any]) -> Set[str]:
        """Extrai propriedades de um schema"""
        properties = set()
        
        if isinstance(schema, dict):
            if 'properties' in schema:
                properties.update(schema['properties'].keys())
            else:
                properties.update(schema.keys())
        
        return properties
    
    def _determine_change_type(self, old_value: Any, new_value: Any) -> ChangeType:
        """Determina o tipo de mudança baseado nos valores"""
        # Simplificado - em produção seria mais sofisticado
        if isinstance(old_value, type(new_value)):
            return ChangeType.REFACTOR
        else:
            return ChangeType.BREAKING
    
    def _validate_schema_integrity(self, contract: ContractDefinition) -> List[Dict[str, Any]]:
        """Valida integridade do schema"""
        errors = []
        
        try:
            # Validar schema JSON básico
            if contract.type == ContractType.API_SCHEMA:
                # Validar OpenAPI schema
                if 'openapi' in contract.schema:
                    # Validações específicas do OpenAPI
                    if 'paths' not in contract.schema:
                        errors.append({
                            'path': 'paths',
                            'message': 'OpenAPI schema must have paths'
                        })
            
            # Validar estrutura básica
            if not isinstance(contract.schema, dict):
                errors.append({
                    'path': 'schema',
                    'message': 'Schema must be an object'
                })
        
        except Exception as e:
            errors.append({
                'path': 'schema',
                'message': f'Schema validation error: {str(e)}'
            })
        
        return errors
    
    def _group_changes_by_type(self, changes: List[ContractChange]) -> Dict[str, int]:
        """Agrupa mudanças por tipo"""
        grouped = defaultdict(int)
        for change in changes:
            grouped[change.change_type.value] += 1
        return dict(grouped)
    
    def _group_changes_by_severity(self, changes: List[ContractChange]) -> Dict[str, int]:
        """Agrupa mudanças por severidade"""
        grouped = defaultdict(int)
        for change in changes:
            grouped[change.severity] += 1
        return dict(grouped)
    
    def _generate_recommendations(self, changes: List[ContractChange], summary: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nas mudanças"""
        recommendations = []
        
        if summary['breaking_changes'] > 0:
            recommendations.append(
                f"⚠️ {summary['breaking_changes']} breaking changes detected. "
                "Consider versioning your API or providing migration guides."
            )
        
        if summary['warnings'] > 0:
            recommendations.append(
                f"⚠️ {summary['warnings']} deprecation warnings. "
                "Plan to remove deprecated features in future versions."
            )
        
        if summary['failed_contracts'] > 0:
            recommendations.append(
                f"❌ {summary['failed_contracts']} contracts failed validation. "
                "Review and fix schema issues."
            )
        
        if not changes:
            recommendations.append("✅ No changes detected. All contracts are up to date.")
        
        return recommendations
    
    def save_report(self, report: ValidationReport, format: str = 'json') -> str:
        """Salva relatório em arquivo"""
        timestamp = report.timestamp.strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"contract_validation_report_{timestamp}.json"
            filepath = self.reports_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report.to_dict(), f, indent=2, default=str)
        
        elif format == 'html':
            filename = f"contract_validation_report_{timestamp}.html"
            filepath = self.reports_dir / filename
            
            html_content = self._generate_html_report(report)
            with open(filepath, 'w') as f:
                f.write(html_content)
        
        else:
            raise ValueError(f"Formato não suportado: {format}")
        
        logger.info(f"[CONTRACT_VALIDATOR] Relatório salvo: {filepath}")
        return str(filepath)
    
    def _generate_html_report(self, report: ValidationReport) -> str:
        """Gera relatório HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Contract Validation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .changes {{ margin: 20px 0; }}
                .change {{ background: white; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007cba; }}
                .breaking {{ border-left-color: #dc3232; }}
                .warning {{ border-left-color: #ffb900; }}
                .info {{ border-left-color: #00a32a; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 Contract Validation Report</h1>
                <p>Generated: {report.timestamp.strftime('%Y-%m-%data %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Contracts</h3>
                    <p>{report.total_contracts}</p>
                </div>
                <div class="metric">
                    <h3>Validated</h3>
                    <p>{report.validated_contracts}</p>
                </div>
                <div class="metric">
                    <h3>Failed</h3>
                    <p>{report.failed_contracts}</p>
                </div>
                <div class="metric">
                    <h3>Breaking Changes</h3>
                    <p>{report.breaking_changes}</p>
                </div>
            </div>
            
            <div class="changes">
                <h2>Changes Detected</h2>
                {self._generate_changes_html(report.changes)}
            </div>
            
            <div class="recommendations">
                <h2>Recommendations</h2>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
                </ul>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_changes_html(self, changes: List[ContractChange]) -> str:
        """Gera HTML para lista de mudanças"""
        if not changes:
            return "<p>No changes detected.</p>"
        
        html = ""
        for change in changes:
            css_class = change.severity
            html += f"""
            <div class="change {css_class}">
                <h4>{change.contract_name} - {change.field_path}</h4>
                <p><strong>Type:</strong> {change.change_type.value}</p>
                <p><strong>Description:</strong> {change.description}</p>
                <p><strong>Impact:</strong> {change.impact}</p>
                {f'<p><strong>Migration Guide:</strong> {change.migration_guide}</p>' if change.migration_guide else ''}
            </div>
            """
        return html

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description='Validate contracts and detect breaking changes')
    parser.add_argument('--path', default='.', help='Path to project root')
    parser.add_argument('--format', choices=['json', 'html'], default='json', help='Report format')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--ci', action='store_true', help='CI/CD mode (exit with error on breaking changes)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Inicializar validador
        validator = ContractValidator(args.path)
        
        # Descobrir contratos
        logger.info("🔍 Discovering contracts...")
        contracts = validator.discover_contracts()
        
        if not contracts:
            logger.warning("No contracts found")
            return
        
        # Validar contratos
        logger.info("✅ Validating contracts...")
        report = validator.validate_contracts(contracts)
        
        # Salvar relatório
        report_path = validator.save_report(report, args.format)
        
        # Exibir resumo
        print(f"\n📊 Contract Validation Summary:")
        print(f"   Total Contracts: {report.total_contracts}")
        print(f"   Validated: {report.validated_contracts}")
        print(f"   Failed: {report.failed_contracts}")
        print(f"   Breaking Changes: {report.breaking_changes}")
        print(f"   Warnings: {report.warnings}")
        print(f"   Report: {report_path}")
        
        # Exibir recomendações
        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"   {rec}")
        
        # Salvar cache
        validator._save_contract_cache()
        
        # Verificar se deve falhar em CI/CD
        if args.ci and report.breaking_changes > 0:
            logger.error(f"❌ {report.breaking_changes} breaking changes detected. CI/CD validation failed.")
            sys.exit(1)
        
        logger.info("✅ Contract validation completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Contract validation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 