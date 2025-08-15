"""
Testes Unitários para Advanced Template Service
Serviço de Templates Avançados - Omni Keywords Finder

Prompt: Implementação de testes unitários para serviço de templates avançados
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import hashlib
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from backend.app.services.advanced_template_service import (
    AdvancedTemplateService,
    TemplateMetadata,
    ABTestConfig,
    TemplateType,
    TemplateStatus
)
from backend.app.models.prompt_system import PromptBase, LogOperacao
from backend.app.schemas.prompt_system_schemas import TemplateCreate, TemplateResponse, TemplateVersion, ABTestResult


class TestTemplateType:
    """Testes para enum TemplateType"""
    
    def test_template_type_values(self):
        """Testa valores do enum TemplateType"""
        assert TemplateType.ECOMMERCE.value == "ecommerce"
        assert TemplateType.SAUDE.value == "saude"
        assert TemplateType.TECNOLOGIA.value == "tecnologia"
        assert TemplateType.EDUCACAO.value == "educacao"
        assert TemplateType.FINANCAS.value == "financas"
        assert TemplateType.MARKETING.value == "marketing"
        assert TemplateType.CUSTOM.value == "custom"


class TestTemplateStatus:
    """Testes para enum TemplateStatus"""
    
    def test_template_status_values(self):
        """Testa valores do enum TemplateStatus"""
        assert TemplateStatus.DRAFT.value == "draft"
        assert TemplateStatus.ACTIVE.value == "active"
        assert TemplateStatus.ARCHIVED.value == "archived"
        assert TemplateStatus.TESTING.value == "testing"


class TestTemplateMetadata:
    """Testes para TemplateMetadata"""
    
    def test_template_metadata_creation(self):
        """Testa criação de TemplateMetadata"""
        metadata = TemplateMetadata(
            template_id="test_template_001",
            nome="Template de Teste",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="test_user",
            descricao="Template para testes",
            tags=["marketing", "test"],
            variaveis=["nome", "produto", "preco"]
        )
        
        assert metadata.template_id == "test_template_001"
        assert metadata.nome == "Template de Teste"
        assert metadata.tipo == TemplateType.MARKETING
        assert metadata.versao == "1.0.0"
        assert metadata.autor == "test_user"
        assert metadata.descricao == "Template para testes"
        assert metadata.tags == ["marketing", "test"]
        assert metadata.variaveis == ["nome", "produto", "preco"]
        assert metadata.performance_score == 0.0
        assert metadata.uso_count == 0
        assert isinstance(metadata.created_at, datetime)
        assert isinstance(metadata.updated_at, datetime)
    
    def test_template_metadata_with_performance(self):
        """Testa criação de TemplateMetadata com performance"""
        metadata = TemplateMetadata(
            template_id="perf_template_001",
            nome="Template Performático",
            tipo=TemplateType.TECNOLOGIA,
            versao="2.1.0",
            autor="dev_user",
            descricao="Template otimizado",
            tags=["tech", "optimized"],
            variaveis=["app", "feature"],
            performance_score=0.95,
            uso_count=150
        )
        
        assert metadata.performance_score == 0.95
        assert metadata.uso_count == 150


class TestABTestConfig:
    """Testes para ABTestConfig"""
    
    def test_ab_test_config_creation(self):
        """Testa criação de ABTestConfig"""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=7)
        
        ab_test = ABTestConfig(
            test_id="abtest_001",
            template_a_id="template_a",
            template_b_id="template_b",
            nicho_id=1,
            categoria_id=2,
            start_date=start_date,
            end_date=end_date
        )
        
        assert ab_test.test_id == "abtest_001"
        assert ab_test.template_a_id == "template_a"
        assert ab_test.template_b_id == "template_b"
        assert ab_test.nicho_id == 1
        assert ab_test.categoria_id == 2
        assert ab_test.start_date == start_date
        assert ab_test.end_date == end_date
        assert ab_test.traffic_split == 0.5
        assert ab_test.metrics == ["conversion_rate", "quality_score"]
        assert ab_test.status == "active"
    
    def test_ab_test_config_custom(self):
        """Testa criação de ABTestConfig com configurações customizadas"""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=14)
        
        ab_test = ABTestConfig(
            test_id="abtest_002",
            template_a_id="template_a",
            template_b_id="template_b",
            nicho_id=3,
            categoria_id=4,
            start_date=start_date,
            end_date=end_date,
            traffic_split=0.7,
            metrics=["click_rate", "engagement"],
            status="paused"
        )
        
        assert ab_test.traffic_split == 0.7
        assert ab_test.metrics == ["click_rate", "engagement"]
        assert ab_test.status == "paused"


class TestAdvancedTemplateService:
    """Testes para AdvancedTemplateService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def template_service(self, mock_db):
        """Instância do AdvancedTemplateService para testes"""
        return AdvancedTemplateService(mock_db)
    
    def test_template_service_initialization(self, template_service, mock_db):
        """Testa inicialização do AdvancedTemplateService"""
        assert template_service.db == mock_db
        assert isinstance(template_service.templates, dict)
        assert isinstance(template_service.ab_tests, dict)
        assert isinstance(template_service.template_versions, dict)
    
    def test_load_templates(self, template_service, mock_db):
        """Testa carregamento de templates"""
        # Mock de prompts base
        mock_prompt1 = Mock()
        mock_prompt1.id = 1
        mock_prompt1.nome_arquivo = "ecommerce_prompt.txt"
        mock_prompt1.conteudo = "Crie um artigo sobre [produto] para [loja]"
        mock_prompt1.created_at = datetime.utcnow()
        
        mock_prompt2 = Mock()
        mock_prompt2.id = 2
        mock_prompt2.nome_arquivo = "tech_prompt.txt"
        mock_prompt2.conteudo = "Desenvolva um [app] com [tecnologia]"
        mock_prompt2.created_at = datetime.utcnow()
        
        mock_db.query.return_value.all.return_value = [mock_prompt1, mock_prompt2]
        
        # Recarregar templates
        template_service._load_templates()
        
        assert len(template_service.templates) == 2
        assert "template_1" in template_service.templates
        assert "template_2" in template_service.templates
        
        # Verificar se tipos foram detectados corretamente
        assert template_service.templates["template_1"].tipo == TemplateType.ECOMMERCE
        assert template_service.templates["template_2"].tipo == TemplateType.TECNOLOGIA
    
    def test_detect_template_type_ecommerce(self, template_service):
        """Testa detecção de tipo ecommerce"""
        content = "Crie um artigo sobre produto para loja online com vendas e compras"
        template_type = template_service._detect_template_type(content)
        assert template_type == TemplateType.ECOMMERCE
    
    def test_detect_template_type_saude(self, template_service):
        """Testa detecção de tipo saúde"""
        content = "Artigo sobre saúde e medicina com tratamento de sintomas"
        template_type = template_service._detect_template_type(content)
        assert template_type == TemplateType.SAUDE
    
    def test_detect_template_type_tecnologia(self, template_service):
        """Testa detecção de tipo tecnologia"""
        content = "Desenvolva software com programação e tecnologia digital"
        template_type = template_service._detect_template_type(content)
        assert template_type == TemplateType.TECNOLOGIA
    
    def test_detect_template_type_educacao(self, template_service):
        """Testa detecção de tipo educação"""
        content = "Curso de educação com aprendizado e estudo"
        template_type = template_service._detect_template_type(content)
        assert template_type == TemplateType.EDUCACAO
    
    def test_detect_template_type_financas(self, template_service):
        """Testa detecção de tipo finanças"""
        content = "Investimento em finanças com dinheiro e economia"
        template_type = template_service._detect_template_type(content)
        assert template_type == TemplateType.FINANCAS
    
    def test_detect_template_type_marketing(self, template_service):
        """Testa detecção de tipo marketing"""
        content = "Campanha de marketing com publicidade e vendas"
        template_type = template_service._detect_template_type(content)
        assert template_type == TemplateType.MARKETING
    
    def test_detect_template_type_custom(self, template_service):
        """Testa detecção de tipo custom"""
        content = "Conteúdo genérico sem palavras-chave específicas"
        template_type = template_service._detect_template_type(content)
        assert template_type == TemplateType.CUSTOM
    
    def test_extract_variables_brackets(self, template_service):
        """Testa extração de variáveis com colchetes"""
        content = "Crie um artigo sobre [produto] para [loja] com [preco]"
        variables = template_service._extract_variables(content)
        assert "produto" in variables
        assert "loja" in variables
        assert "preco" in variables
        assert len(variables) == 3
    
    def test_extract_variables_braces(self, template_service):
        """Testa extração de variáveis com chaves"""
        content = "Desenvolva {app} com {tecnologia} e {framework}"
        variables = template_service._extract_variables(content)
        assert "app" in variables
        assert "tecnologia" in variables
        assert "framework" in variables
        assert len(variables) == 3
    
    def test_extract_variables_dollar(self, template_service):
        """Testa extração de variáveis com dólar"""
        content = "Crie $nome com $descricao e $categoria"
        variables = template_service._extract_variables(content)
        assert "nome" in variables
        assert "descricao" in variables
        assert "categoria" in variables
        assert len(variables) == 3
    
    def test_extract_variables_mixed(self, template_service):
        """Testa extração de variáveis mistas"""
        content = "Use [produto] com {tecnologia} e $preco"
        variables = template_service._extract_variables(content)
        assert "produto" in variables
        assert "tecnologia" in variables
        assert "preco" in variables
        assert len(variables) == 3
    
    def test_create_template(self, template_service, mock_db):
        """Testa criação de template"""
        with patch('time.time', return_value=1640995200):
            template_data = TemplateCreate(
                nome="Template de Teste",
                content="Crie um artigo sobre [produto] para [loja]",
                autor="test_user",
                descricao="Template para testes",
                tags=["test", "marketing"]
            )
            
            template = template_service.create_template(template_data)
        
        assert template.template_id == "template_1640995200"
        assert template.nome == "Template de Teste"
        assert template.tipo == TemplateType.ECOMMERCE
        assert template.versao == "1.0.0"
        assert template.autor == "test_user"
        assert template.descricao == "Template para testes"
        assert template.tags == ["test", "marketing"]
        assert "produto" in template.variaveis
        assert "loja" in template.variaveis
        
        # Verificar se foi adicionado ao dicionário
        assert template.template_id in template_service.templates
        
        # Verificar se versão foi criada
        assert template.template_id in template_service.template_versions
        assert len(template_service.template_versions[template.template_id]) == 1
    
    def test_update_template(self, template_service, mock_db):
        """Testa atualização de template"""
        # Criar template inicial
        template_id = "test_template"
        template = TemplateMetadata(
            template_id=template_id,
            nome="Template Original",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="original_user",
            descricao="Template original",
            tags=["original"],
            variaveis=["var1"]
        )
        template_service.templates[template_id] = template
        
        # Criar versão inicial
        initial_version = TemplateVersion(
            version_id="v1.0.0-abc123",
            template_id=template_id,
            content="Conteúdo original",
            changes="Versão inicial",
            author="original_user",
            created_at=datetime.utcnow()
        )
        template_service.template_versions[template_id] = [initial_version]
        
        # Atualizar template
        new_content = "Conteúdo atualizado com [nova_variavel]"
        updated_template = template_service.update_template(
            template_id=template_id,
            content=new_content,
            author="update_user",
            changes="Atualização de conteúdo"
        )
        
        assert updated_template.versao.startswith("1.0.1")
        assert updated_template.updated_at > template.created_at
        assert "nova_variavel" in updated_template.variaveis
        
        # Verificar se nova versão foi criada
        versions = template_service.template_versions[template_id]
        assert len(versions) == 2
        assert versions[0].content == new_content
        assert versions[0].changes == "Atualização de conteúdo"
    
    def test_update_template_not_found(self, template_service):
        """Testa atualização de template inexistente"""
        with pytest.raises(ValueError, match="Template nonexistent_template não encontrado"):
            template_service.update_template(
                template_id="nonexistent_template",
                content="novo conteúdo",
                author="test_user",
                changes="teste"
            )
    
    def test_get_template_versions(self, template_service):
        """Testa obtenção de versões de template"""
        template_id = "test_template"
        
        # Criar versões de teste
        version1 = TemplateVersion(
            version_id="v1.0.0",
            template_id=template_id,
            content="Versão 1",
            changes="Primeira versão",
            author="user1",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        
        version2 = TemplateVersion(
            version_id="v1.0.1",
            template_id=template_id,
            content="Versão 2",
            changes="Segunda versão",
            author="user2",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        
        template_service.template_versions[template_id] = [version1, version2]
        
        versions = template_service.get_template_versions(template_id)
        
        assert len(versions) == 2
        # Verificar se está ordenado por data (mais recente primeiro)
        assert versions[0].version_id == "v1.0.1"
        assert versions[1].version_id == "v1.0.0"
    
    def test_get_template_versions_not_found(self, template_service):
        """Testa obtenção de versões de template inexistente"""
        versions = template_service.get_template_versions("nonexistent_template")
        assert versions == []
    
    def test_rollback_template(self, template_service, mock_db):
        """Testa rollback de template"""
        template_id = "test_template"
        
        # Criar template
        template = TemplateMetadata(
            template_id=template_id,
            nome="Template Teste",
            tipo=TemplateType.MARKETING,
            versao="1.0.1",
            autor="test_user",
            descricao="Template para teste",
            tags=["test"],
            variaveis=["var1"]
        )
        template_service.templates[template_id] = template
        
        # Criar versões
        version1 = TemplateVersion(
            version_id="v1.0.0",
            template_id=template_id,
            content="Conteúdo versão 1.0.0",
            changes="Versão inicial",
            author="user1",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        
        version2 = TemplateVersion(
            version_id="v1.0.1",
            template_id=template_id,
            content="Conteúdo versão 1.0.1",
            changes="Atualização",
            author="user2",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        
        template_service.template_versions[template_id] = [version2, version1]
        
        # Fazer rollback para versão 1.0.0
        with patch.object(template_service, 'update_template') as mock_update:
            mock_update.return_value = template
            result = template_service.rollback_template(
                template_id=template_id,
                version_id="v1.0.0",
                author="rollback_user"
            )
        
        mock_update.assert_called_once_with(
            template_id=template_id,
            content="Conteúdo versão 1.0.0",
            author="rollback_user",
            changes="Rollback para versão v1.0.0"
        )
    
    def test_rollback_template_not_found(self, template_service):
        """Testa rollback de template inexistente"""
        with pytest.raises(ValueError, match="Template nonexistent_template não encontrado"):
            template_service.rollback_template(
                template_id="nonexistent_template",
                version_id="v1.0.0",
                author="test_user"
            )
    
    def test_rollback_version_not_found(self, template_service):
        """Testa rollback para versão inexistente"""
        template_id = "test_template"
        
        # Criar template sem versões
        template = TemplateMetadata(
            template_id=template_id,
            nome="Template Teste",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="test_user",
            descricao="Template para teste",
            tags=["test"],
            variaveis=["var1"]
        )
        template_service.templates[template_id] = template
        template_service.template_versions[template_id] = []
        
        with pytest.raises(ValueError, match="Versão v1.0.0 não encontrada"):
            template_service.rollback_template(
                template_id=template_id,
                version_id="v1.0.0",
                author="test_user"
            )
    
    def test_create_ab_test(self, template_service, mock_db):
        """Testa criação de teste A/B"""
        # Criar templates de teste
        template_a = TemplateMetadata(
            template_id="template_a",
            nome="Template A",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="user_a",
            descricao="Template A",
            tags=["marketing"],
            variaveis=["var1"]
        )
        
        template_b = TemplateMetadata(
            template_id="template_b",
            nome="Template B",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="user_b",
            descricao="Template B",
            tags=["marketing"],
            variaveis=["var1"]
        )
        
        template_service.templates["template_a"] = template_a
        template_service.templates["template_b"] = template_b
        
        with patch('time.time', return_value=1640995200):
            ab_test = template_service.create_ab_test(
                template_a_id="template_a",
                template_b_id="template_b",
                nicho_id=1,
                categoria_id=2,
                duration_days=7
            )
        
        assert ab_test.test_id == "abtest_1640995200"
        assert ab_test.template_a_id == "template_a"
        assert ab_test.template_b_id == "template_b"
        assert ab_test.nicho_id == 1
        assert ab_test.categoria_id == 2
        assert ab_test.traffic_split == 0.5
        assert ab_test.status == "active"
        
        # Verificar se foi adicionado ao dicionário
        assert ab_test.test_id in template_service.ab_tests
    
    def test_create_ab_test_template_not_found(self, template_service):
        """Testa criação de teste A/B com template inexistente"""
        with pytest.raises(ValueError, match="Um ou ambos os templates não encontrados"):
            template_service.create_ab_test(
                template_a_id="nonexistent_a",
                template_b_id="nonexistent_b",
                nicho_id=1,
                categoria_id=2
            )
    
    def test_get_ab_test_results(self, template_service):
        """Testa obtenção de resultados de teste A/B"""
        # Criar teste A/B
        ab_test = ABTestConfig(
            test_id="test_ab_001",
            template_a_id="template_a",
            template_b_id="template_b",
            nicho_id=1,
            categoria_id=2,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7)
        )
        template_service.ab_tests["test_ab_001"] = ab_test
        
        results = template_service.get_ab_test_results("test_ab_001")
        
        assert results.test_id == "test_ab_001"
        assert results.template_a_id == "template_a"
        assert results.template_b_id == "template_b"
        assert results.winner in ["A", "B"]
        assert results.confidence_level == 0.95
        assert results.test_duration_days == 7
        assert results.total_participants == 295
        
        # Verificar métricas
        assert "conversion_rate" in results.template_a_metrics
        assert "quality_score" in results.template_a_metrics
        assert "usage_count" in results.template_a_metrics
        assert "conversion_rate" in results.template_b_metrics
        assert "quality_score" in results.template_b_metrics
        assert "usage_count" in results.template_b_metrics
    
    def test_get_ab_test_results_not_found(self, template_service):
        """Testa obtenção de resultados de teste A/B inexistente"""
        with pytest.raises(ValueError, match="Teste A/B nonexistent_test não encontrado"):
            template_service.get_ab_test_results("nonexistent_test")
    
    def test_suggest_template_improvements(self, template_service):
        """Testa sugestões de melhorias para template"""
        template_id = "test_template"
        
        # Criar template com baixa performance
        template = TemplateMetadata(
            template_id=template_id,
            nome="Template Teste",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="test_user",
            descricao="Template para teste",
            tags=["test"],
            variaveis=["var1", "var2", "var3", "var4", "var5", "var6"],
            performance_score=0.5,
            uso_count=5
        )
        template_service.templates[template_id] = template
        
        # Criar versões antigas
        old_version = TemplateVersion(
            version_id="v1.0.0",
            template_id=template_id,
            content="Conteúdo antigo",
            changes="Versão inicial",
            author="user1",
            created_at=datetime.utcnow() - timedelta(days=35)
        )
        
        new_version = TemplateVersion(
            version_id="v1.0.1",
            template_id=template_id,
            content="Conteúdo novo",
            changes="Atualização",
            author="user2",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        
        template_service.template_versions[template_id] = [new_version, old_version]
        
        suggestions = template_service.suggest_template_improvements(template_id)
        
        assert len(suggestions) >= 3
        
        # Verificar tipos de sugestões
        suggestion_types = [s["type"] for s in suggestions]
        assert "performance" in suggestion_types
        assert "usage" in suggestion_types
        assert "complexity" in suggestion_types
        assert "freshness" in suggestion_types
    
    def test_suggest_template_improvements_not_found(self, template_service):
        """Testa sugestões para template inexistente"""
        with pytest.raises(ValueError, match="Template nonexistent_template não encontrado"):
            template_service.suggest_template_improvements("nonexistent_template")
    
    def test_get_templates_by_type(self, template_service):
        """Testa obtenção de templates por tipo"""
        # Criar templates de diferentes tipos
        marketing_template = TemplateMetadata(
            template_id="marketing_1",
            nome="Marketing Template",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="user1",
            descricao="Template de marketing",
            tags=["marketing"],
            variaveis=["var1"]
        )
        
        tech_template = TemplateMetadata(
            template_id="tech_1",
            nome="Tech Template",
            tipo=TemplateType.TECNOLOGIA,
            versao="1.0.0",
            autor="user2",
            descricao="Template de tecnologia",
            tags=["tech"],
            variaveis=["var1"]
        )
        
        template_service.templates["marketing_1"] = marketing_template
        template_service.templates["tech_1"] = tech_template
        
        marketing_templates = template_service.get_templates_by_type(TemplateType.MARKETING)
        assert len(marketing_templates) == 1
        assert marketing_templates[0].template_id == "marketing_1"
        
        tech_templates = template_service.get_templates_by_type(TemplateType.TECNOLOGIA)
        assert len(tech_templates) == 1
        assert tech_templates[0].template_id == "tech_1"
    
    def test_search_templates(self, template_service):
        """Testa busca de templates"""
        # Criar templates para busca
        template1 = TemplateMetadata(
            template_id="search_1",
            nome="Template de Marketing Digital",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="user1",
            descricao="Template para marketing digital",
            tags=["marketing", "digital"],
            variaveis=["var1"]
        )
        
        template2 = TemplateMetadata(
            template_id="search_2",
            nome="Template de Vendas",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="user2",
            descricao="Template para vendas online",
            tags=["vendas", "online"],
            variaveis=["var1"]
        )
        
        template_service.templates["search_1"] = template1
        template_service.templates["search_2"] = template2
        
        # Buscar por nome
        results = template_service.search_templates("Marketing")
        assert len(results) == 1
        assert results[0].template_id == "search_1"
        
        # Buscar por descrição
        results = template_service.search_templates("vendas")
        assert len(results) == 1
        assert results[0].template_id == "search_2"
        
        # Buscar por tag
        results = template_service.search_templates("digital")
        assert len(results) == 1
        assert results[0].template_id == "search_1"
    
    def test_log_template_operation(self, template_service, mock_db):
        """Testa registro de log de operação de template"""
        template_service._log_template_operation("create", "test_template", "test_user")
        
        # Verificar se log foi adicionado ao banco
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Verificar se o log adicionado é do tipo correto
        log_entry = mock_db.add.call_args[0][0]
        assert isinstance(log_entry, LogOperacao)
        assert log_entry.operacao == "template_create"
        assert "test_template" in log_entry.detalhes
        assert "test_user" in log_entry.detalhes
    
    def test_get_template_statistics(self, template_service):
        """Testa obtenção de estatísticas dos templates"""
        # Criar templates de teste
        template1 = TemplateMetadata(
            template_id="stat_1",
            nome="Template 1",
            tipo=TemplateType.MARKETING,
            versao="1.0.0",
            autor="user1",
            descricao="Template 1",
            tags=["marketing"],
            variaveis=["var1"]
        )
        
        template2 = TemplateMetadata(
            template_id="stat_2",
            nome="Template 2",
            tipo=TemplateType.TECNOLOGIA,
            versao="1.0.0",
            autor="user2",
            descricao="Template 2",
            tags=["tech"],
            variaveis=["var1"]
        )
        
        template_service.templates["stat_1"] = template1
        template_service.templates["stat_2"] = template2
        
        # Criar versões
        version1 = TemplateVersion(
            version_id="v1.0.0",
            template_id="stat_1",
            content="Conteúdo 1",
            changes="Versão inicial",
            author="user1",
            created_at=datetime.utcnow()
        )
        
        version2 = TemplateVersion(
            version_id="v1.0.1",
            template_id="stat_1",
            content="Conteúdo 1 atualizado",
            changes="Atualização",
            author="user1",
            created_at=datetime.utcnow()
        )
        
        template_service.template_versions["stat_1"] = [version1, version2]
        template_service.template_versions["stat_2"] = [version1]
        
        # Criar teste A/B ativo
        ab_test = ABTestConfig(
            test_id="abtest_001",
            template_a_id="stat_1",
            template_b_id="stat_2",
            nicho_id=1,
            categoria_id=2,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
            status="active"
        )
        template_service.ab_tests["abtest_001"] = ab_test
        
        stats = template_service.get_template_statistics()
        
        assert stats["total_templates"] == 2
        assert stats["total_versions"] == 3
        assert stats["templates_by_type"]["marketing"] == 1
        assert stats["templates_by_type"]["tecnologia"] == 1
        assert stats["active_ab_tests"] == 1
        assert stats["average_versions_per_template"] == 1.5


class TestAdvancedTemplateServiceIntegration:
    """Testes de integração para AdvancedTemplateService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def template_service(self, mock_db):
        """Instância do AdvancedTemplateService para testes"""
        return AdvancedTemplateService(mock_db)
    
    def test_full_template_lifecycle(self, template_service, mock_db):
        """Testa ciclo completo de vida do template"""
        # 1. Criar template
        template_data = TemplateCreate(
            nome="Template de Integração",
            content="Crie um artigo sobre [produto] para [loja] com [preco]",
            autor="integration_user",
            descricao="Template para teste de integração",
            tags=["integration", "test"]
        )
        
        template = template_service.create_template(template_data)
        assert template.template_id in template_service.templates
        
        # 2. Atualizar template
        updated_template = template_service.update_template(
            template_id=template.template_id,
            content="Crie um artigo sobre [produto] para [loja] com [preco] e [desconto]",
            author="update_user",
            changes="Adicionada variável desconto"
        )
        
        assert updated_template.versao.startswith("1.0.1")
        assert "desconto" in updated_template.variaveis
        
        # 3. Verificar versões
        versions = template_service.get_template_versions(template.template_id)
        assert len(versions) == 2
        
        # 4. Buscar template
        search_results = template_service.search_templates("integração")
        assert len(search_results) == 1
        assert search_results[0].template_id == template.template_id
        
        # 5. Obter sugestões
        suggestions = template_service.suggest_template_improvements(template.template_id)
        assert isinstance(suggestions, list)
        
        # 6. Obter estatísticas
        stats = template_service.get_template_statistics()
        assert stats["total_templates"] >= 1


class TestAdvancedTemplateServiceErrorHandling:
    """Testes de tratamento de erros para AdvancedTemplateService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def template_service(self, mock_db):
        """Instância do AdvancedTemplateService para testes"""
        return AdvancedTemplateService(mock_db)
    
    def test_database_error_handling(self, template_service, mock_db):
        """Testa tratamento de erro de banco de dados"""
        # Simular erro de banco
        mock_db.add.side_effect = Exception("Database error")
        
        # Deve continuar funcionando sem quebrar
        template_service._log_template_operation("test", "test_template", "test_user")
        
        # Verificar se o erro foi tratado graciosamente
        assert True  # Se chegou aqui, não quebrou
    
    def test_template_creation_error_handling(self, template_service):
        """Testa tratamento de erro na criação de template"""
        # Simular erro na criação
        with patch('time.time', side_effect=Exception("Time error")):
            with pytest.raises(Exception):
                template_data = TemplateCreate(
                    nome="Error Template",
                    content="Test content",
                    autor="test_user",
                    descricao="Test description",
                    tags=["test"]
                )
                template_service.create_template(template_data)


class TestAdvancedTemplateServicePerformance:
    """Testes de performance para AdvancedTemplateService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def template_service(self, mock_db):
        """Instância do AdvancedTemplateService para testes"""
        return AdvancedTemplateService(mock_db)
    
    def test_multiple_template_operations_performance(self, template_service, mock_db):
        """Testa performance de múltiplas operações de template"""
        import time
        
        start_time = time.time()
        
        # Criar múltiplos templates
        for i in range(10):
            template_data = TemplateCreate(
                nome=f"Template {i}",
                content=f"Crie um artigo sobre [produto_{i}] para [loja_{i}]",
                autor=f"user_{i}",
                descricao=f"Template {i} para teste",
                tags=[f"tag_{i}"]
            )
            
            template = template_service.create_template(template_data)
            assert template.template_id in template_service.templates
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 10 templates
        
        # Verificar se todos foram criados
        assert len(template_service.templates) == 10


if __name__ == "__main__":
    pytest.main([__file__]) 