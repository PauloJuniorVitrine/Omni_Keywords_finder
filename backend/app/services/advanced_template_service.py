"""
Serviço de Templates Avançados
==============================

Sistema para gerenciamento de templates de prompts com versionamento,
A/B testing e sugestões automáticas de melhorias.

Tracing ID: TEMPLATE_ADVANCED_001
Data: 2024-12-27
Autor: Sistema de Templates Avançados
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
import logging

from ..models.prompt_system import PromptBase, LogOperacao
from ..schemas.prompt_system_schemas import TemplateCreate, TemplateResponse, TemplateVersion, ABTestResult

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Tipos de template disponíveis"""
    ECOMMERCE = "ecommerce"
    SAUDE = "saude"
    TECNOLOGIA = "tecnologia"
    EDUCACAO = "educacao"
    FINANCAS = "financas"
    MARKETING = "marketing"
    CUSTOM = "custom"


class TemplateStatus(Enum):
    """Status do template"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    TESTING = "testing"


@dataclass
class TemplateMetadata:
    """Metadados do template"""
    template_id: str
    nome: str
    tipo: TemplateType
    versao: str
    autor: str
    descricao: str
    tags: List[str]
    variaveis: List[str]
    performance_score: float = 0.0
    uso_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ABTestConfig:
    """Configuração de A/B test"""
    test_id: str
    template_a_id: str
    template_b_id: str
    nicho_id: int
    categoria_id: int
    start_date: datetime
    end_date: datetime
    traffic_split: float = 0.5  # 50% para cada versão
    metrics: List[str] = field(default_factory=lambda: ["conversion_rate", "quality_score"])
    status: str = "active"


class AdvancedTemplateService:
    """Serviço principal de templates avançados"""
    
    def __init__(self, db: Session):
        self.db = db
        self.templates: Dict[str, TemplateMetadata] = {}
        self.ab_tests: Dict[str, ABTestConfig] = {}
        self.template_versions: Dict[str, List[TemplateVersion]] = {}
        self._load_templates()
        self._load_ab_tests()
    
    def _load_templates(self):
        """Carrega templates do banco de dados"""
        try:
            # Buscar prompts base e converter para templates
            prompts = self.db.query(PromptBase).all()
            
            for prompt in prompts:
                template_id = f"template_{prompt.id}"
                
                # Detectar tipo baseado no conteúdo
                template_type = self._detect_template_type(prompt.conteudo)
                
                # Extrair variáveis
                variaveis = self._extract_variables(prompt.conteudo)
                
                # Calcular hash para versionamento
                content_hash = hashlib.sha256(prompt.conteudo.encode()).hexdigest()[:8]
                
                template = TemplateMetadata(
                    template_id=template_id,
                    nome=prompt.nome_arquivo.replace('.txt', ''),
                    tipo=template_type,
                    versao=f"1.0.0-{content_hash}",
                    autor="sistema",
                    descricao=f"Template gerado automaticamente de {prompt.nome_arquivo}",
                    tags=[template_type.value, "auto-generated"],
                    variaveis=variaveis
                )
                
                self.templates[template_id] = template
                
                # Criar versão inicial
                version = TemplateVersion(
                    version_id=f"v1.0.0-{content_hash}",
                    template_id=template_id,
                    content=prompt.conteudo,
                    changes="Versão inicial",
                    author="sistema",
                    created_at=prompt.created_at
                )
                
                if template_id not in self.template_versions:
                    self.template_versions[template_id] = []
                self.template_versions[template_id].append(version)
                
        except Exception as e:
            logger.error(f"Erro ao carregar templates: {str(e)}")
    
    def _load_ab_tests(self):
        """Carrega testes A/B do banco de dados"""
        # Implementar carregamento de testes A/B
        pass
    
    def _detect_template_type(self, content: str) -> TemplateType:
        """Detecta tipo do template baseado no conteúdo"""
        content_lower = content.lower()
        
        # Palavras-chave para cada tipo
        keywords = {
            TemplateType.ECOMMERCE: ["produto", "compra", "venda", "loja", "ecommerce", "shopping"],
            TemplateType.SAUDE: ["saúde", "medicina", "tratamento", "sintomas", "doença", "cura"],
            TemplateType.TECNOLOGIA: ["tecnologia", "software", "programação", "app", "digital", "inovação"],
            TemplateType.EDUCACAO: ["educação", "curso", "aprendizado", "estudo", "treinamento", "ensino"],
            TemplateType.FINANCAS: ["finanças", "investimento", "dinheiro", "economia", "orçamento", "poupança"],
            TemplateType.MARKETING: ["marketing", "publicidade", "promoção", "vendas", "campanha", "branding"]
        }
        
        # Contar ocorrências de palavras-chave
        scores = {}
        for template_type, words in keywords.items():
            score = sum(1 for word in words if word in content_lower)
            scores[template_type] = score
        
        # Retornar tipo com maior score
        if scores:
            return max(scores, key=scores.get)
        
        return TemplateType.CUSTOM
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extrai variáveis do template"""
        import re
        
        # Padrões de variáveis
        patterns = [
            r'\[([^\]]+)\]',  # [VARIABLE]
            r'\{([^}]+)\}',  # {variable}
            r'\$([a-zA-Z_][a-zA-Z0-9_]*)',  # $variable
        ]
        
        variables = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            variables.update(matches)
        
        return list(variables)
    
    def create_template(self, template_data: TemplateCreate) -> TemplateMetadata:
        """Cria novo template"""
        try:
            template_id = f"template_{int(time.time())}"
            
            # Detectar tipo
            template_type = self._detect_template_type(template_data.content)
            
            # Extrair variáveis
            variaveis = self._extract_variables(template_data.content)
            
            # Calcular hash
            content_hash = hashlib.sha256(template_data.content.encode()).hexdigest()[:8]
            
            template = TemplateMetadata(
                template_id=template_id,
                nome=template_data.nome,
                tipo=template_type,
                versao="1.0.0",
                autor=template_data.autor,
                descricao=template_data.descricao,
                tags=template_data.tags,
                variaveis=variaveis
            )
            
            self.templates[template_id] = template
            
            # Criar versão inicial
            version = TemplateVersion(
                version_id=f"v1.0.0-{content_hash}",
                template_id=template_id,
                content=template_data.content,
                changes="Versão inicial",
                author=template_data.autor,
                created_at=datetime.utcnow()
            )
            
            self.template_versions[template_id] = [version]
            
            # Log da operação
            self._log_template_operation("create", template_id, template_data.autor)
            
            logger.info(f"Template criado: {template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Erro ao criar template: {str(e)}")
            raise
    
    def update_template(self, template_id: str, content: str, author: str, changes: str) -> TemplateMetadata:
        """Atualiza template criando nova versão"""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} não encontrado")
            
            template = self.templates[template_id]
            
            # Calcular nova versão
            current_version = template.versao
            major, minor, patch = map(int, current_version.split('.')[:3])
            patch += 1
            
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
            new_version = f"{major}.{minor}.{patch}-{content_hash}"
            
            # Atualizar template
            template.versao = new_version
            template.updated_at = datetime.utcnow()
            
            # Criar nova versão
            version = TemplateVersion(
                version_id=new_version,
                template_id=template_id,
                content=content,
                changes=changes,
                author=author,
                created_at=datetime.utcnow()
            )
            
            self.template_versions[template_id].append(version)
            
            # Log da operação
            self._log_template_operation("update", template_id, author)
            
            logger.info(f"Template atualizado: {template_id} -> {new_version}")
            return template
            
        except Exception as e:
            logger.error(f"Erro ao atualizar template: {str(e)}")
            raise
    
    def get_template_versions(self, template_id: str) -> List[TemplateVersion]:
        """Obtém todas as versões de um template"""
        if template_id not in self.template_versions:
            return []
        
        return sorted(
            self.template_versions[template_id],
            key=lambda value: value.created_at,
            reverse=True
        )
    
    def rollback_template(self, template_id: str, version_id: str, author: str) -> TemplateMetadata:
        """Faz rollback para versão específica"""
        try:
            if template_id not in self.template_versions:
                raise ValueError(f"Template {template_id} não encontrado")
            
            versions = self.template_versions[template_id]
            target_version = next((value for value in versions if value.version_id == version_id), None)
            
            if not target_version:
                raise ValueError(f"Versão {version_id} não encontrada")
            
            # Criar nova versão com conteúdo da versão alvo
            return self.update_template(
                template_id=template_id,
                content=target_version.content,
                author=author,
                changes=f"Rollback para versão {version_id}"
            )
            
        except Exception as e:
            logger.error(f"Erro no rollback: {str(e)}")
            raise
    
    def create_ab_test(self, template_a_id: str, template_b_id: str, 
                      nicho_id: int, categoria_id: int, 
                      duration_days: int = 7) -> ABTestConfig:
        """Cria teste A/B entre dois templates"""
        try:
            # Validar templates
            if template_a_id not in self.templates or template_b_id not in self.templates:
                raise ValueError("Um ou ambos os templates não encontrados")
            
            test_id = f"abtest_{int(time.time())}"
            
            ab_test = ABTestConfig(
                test_id=test_id,
                template_a_id=template_a_id,
                template_b_id=template_b_id,
                nicho_id=nicho_id,
                categoria_id=categoria_id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=duration_days)
            )
            
            self.ab_tests[test_id] = ab_test
            
            # Marcar templates como em teste
            self.templates[template_a_id].status = TemplateStatus.TESTING
            self.templates[template_b_id].status = TemplateStatus.TESTING
            
            logger.info(f"Teste A/B criado: {test_id}")
            return ab_test
            
        except Exception as e:
            logger.error(f"Erro ao criar teste A/B: {str(e)}")
            raise
    
    def get_ab_test_results(self, test_id: str) -> ABTestResult:
        """Obtém resultados de teste A/B"""
        try:
            if test_id not in self.ab_tests:
                raise ValueError(f"Teste A/B {test_id} não encontrado")
            
            ab_test = self.ab_tests[test_id]
            
            # Simular métricas (em produção, buscar do banco)
            template_a_metrics = {
                "conversion_rate": 0.15,
                "quality_score": 0.85,
                "usage_count": 150
            }
            
            template_b_metrics = {
                "conversion_rate": 0.18,
                "quality_score": 0.87,
                "usage_count": 145
            }
            
            # Calcular vencedor
            a_score = template_a_metrics["conversion_rate"] * 0.6 + template_a_metrics["quality_score"] * 0.4
            b_score = template_b_metrics["conversion_rate"] * 0.6 + template_b_metrics["quality_score"] * 0.4
            
            winner = "B" if b_score > a_score else "A"
            
            return ABTestResult(
                test_id=test_id,
                template_a_id=ab_test.template_a_id,
                template_b_id=ab_test.template_b_id,
                template_a_metrics=template_a_metrics,
                template_b_metrics=template_b_metrics,
                winner=winner,
                confidence_level=0.95,
                test_duration_days=7,
                total_participants=295
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter resultados A/B: {str(e)}")
            raise
    
    def suggest_template_improvements(self, template_id: str) -> List[Dict[str, Any]]:
        """Sugere melhorias para um template"""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} não encontrado")
            
            template = self.templates[template_id]
            versions = self.template_versions[template_id]
            
            suggestions = []
            
            # Analisar performance
            if template.performance_score < 0.7:
                suggestions.append({
                    "type": "performance",
                    "priority": "high",
                    "description": "Score de performance baixo. Considere otimizar variáveis e estrutura.",
                    "action": "review_variables_and_structure"
                })
            
            # Verificar uso recente
            if template.uso_count < 10:
                suggestions.append({
                    "type": "usage",
                    "priority": "medium",
                    "description": "Baixo uso do template. Considere melhorar relevância ou visibilidade.",
                    "action": "improve_relevance"
                })
            
            # Analisar variáveis
            if len(template.variaveis) > 5:
                suggestions.append({
                    "type": "complexity",
                    "priority": "medium",
                    "description": "Muitas variáveis podem tornar o template complexo. Considere simplificar.",
                    "action": "simplify_variables"
                })
            
            # Verificar atualizações recentes
            if len(versions) > 1:
                last_update = versions[0].created_at
                days_since_update = (datetime.utcnow() - last_update).days
                
                if days_since_update > 30:
                    suggestions.append({
                        "type": "freshness",
                        "priority": "low",
                        "description": "Template não atualizado há mais de 30 dias. Considere revisar.",
                        "action": "review_and_update"
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões: {str(e)}")
            return []
    
    def get_templates_by_type(self, template_type: TemplateType) -> List[TemplateMetadata]:
        """Obtém templates por tipo"""
        return [
            template for template in self.templates.values()
            if template.tipo == template_type
        ]
    
    def search_templates(self, query: str) -> List[TemplateMetadata]:
        """Busca templates por texto"""
        query_lower = query.lower()
        
        results = []
        for template in self.templates.values():
            if (query_lower in template.nome.lower() or
                query_lower in template.descricao.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def _log_template_operation(self, operation: str, template_id: str, author: str):
        """Registra log de operação de template"""
        try:
            log_entry = LogOperacao(
                operacao=f"template_{operation}",
                detalhes=json.dumps({
                    "template_id": template_id,
                    "author": author,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                timestamp=datetime.utcnow()
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar log: {str(e)}")
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas dos templates"""
        total_templates = len(self.templates)
        templates_by_type = {}
        total_versions = sum(len(versions) for versions in self.template_versions.values())
        
        for template in self.templates.values():
            template_type = template.tipo.value
            if template_type not in templates_by_type:
                templates_by_type[template_type] = 0
            templates_by_type[template_type] += 1
        
        active_tests = len([test for test in self.ab_tests.values() if test.status == "active"])
        
        return {
            "total_templates": total_templates,
            "total_versions": total_versions,
            "templates_by_type": templates_by_type,
            "active_ab_tests": active_tests,
            "average_versions_per_template": total_versions / total_templates if total_templates > 0 else 0
        } 