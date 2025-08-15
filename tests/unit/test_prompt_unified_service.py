from typing import Dict, List, Optional, Any
"""
Testes unitários para PromptUnifiedService
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 1.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from infrastructure.processamento.prompt_unified_service import (
    PromptUnifiedService,
    PromptTemplate,
    PromptCache
)

class TestPromptUnifiedService:
    """Testes para PromptUnifiedService."""
    
    @pytest.fixture
    def service(self):
        """Fixture para serviço."""
        return PromptUnifiedService(
            templates_dir="test_templates",
            cache_enabled=True,
            cache_ttl=3600,
            max_cache_size=100
        )
    
    @pytest.fixture
    def sample_template_content(self):
        """Fixture para conteúdo de template."""
        return """# Template: Artigo Marketing Digital
# Version: 1.0.0
# Category: marketing
# Created: 2025-01-27T10:00:00
# Updated: 2025-01-27T10:00:00

Você deve gerar um artigo sobre {primary_keyword}.

Palavras-chave secundárias: {secondary_keywords}
Cluster: {cluster_id}
Categoria: {categoria}

O artigo deve incluir:
- Introdução sobre {primary_keyword}
- Estratégias relacionadas
- Conclusão com call-to-action

Estrutura:
<h1>{primary_keyword}: Guia Completo</h1>
<h2>O que é {primary_keyword}</h2>
<h3>Estratégias</h3>
<h2>Conclusão</h2>
"""
    
    @pytest.fixture
    def sample_data(self):
        """Fixture para dados de teste."""
        return {
            'primary_keyword': 'marketing digital',
            'secondary_keywords': 'seo, ads, social media',
            'cluster_id': 'cluster_001',
            'categoria': 'marketing',
            'fase_funil': 'consideration',
            'data': '2025-01-27',
            'usuario': 'admin'
        }
    
    def test_init(self, service):
        """Testa inicialização do serviço."""
        assert service.cache_enabled is True
        assert service.cache_ttl == 3600
        assert service.max_cache_size == 100
        assert isinstance(service.prompt_cache, dict)
        assert isinstance(service.template_cache, dict)
        assert service.templates_dir.exists()
    
    def test_carregar_template_txt(self, service, sample_template_content):
        """Testa carregamento de template TXT."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_template_content)
            temp_file = f.name
        
        try:
            template = service.carregar_template_txt(temp_file)
            
            assert isinstance(template, PromptTemplate)
            assert template.name == Path(temp_file).stem
            assert template.content == sample_template_content
            assert len(template.placeholders) > 0
            assert template.category == 'marketing'
            assert template.version == '1.0.0'
            assert isinstance(template.created_at, datetime)
            assert isinstance(template.updated_at, datetime)
            assert isinstance(template.metadata, dict)
            
        finally:
            os.unlink(temp_file)
    
    def test_carregar_template_txt_arquivo_inexistente(self, service):
        """Testa carregamento de arquivo inexistente."""
        with pytest.raises(FileNotFoundError):
            service.carregar_template_txt("arquivo_inexistente.txt")
    
    def test_salvar_template_txt(self, service, sample_template_content):
        """Testa salvamento de template TXT."""
        # Criar template
        template = service.criar_template(
            name="test_template",
            content=sample_template_content,
            category="test",
            version="1.0.0"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_file = f.name
        
        try:
            # Salvar template
            success = service.salvar_template_txt(template, temp_file)
            assert success is True
            
            # Verificar se arquivo foi criado
            assert os.path.exists(temp_file)
            
            # Ler arquivo e verificar conteúdo
            with open(temp_file, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            
            assert "# Template: test_template" in saved_content
            assert "# Version: 1.0.0" in saved_content
            assert "# Category: test" in saved_content
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_criar_template(self, service):
        """Testa criação de template."""
        content = "Artigo sobre {primary_keyword} com {secondary_keywords}"
        
        template = service.criar_template(
            name="test_template",
            content=content,
            category="test",
            version="1.0.0",
            metadata={"author": "test_user"}
        )
        
        assert isinstance(template, PromptTemplate)
        assert template.name == "test_template"
        assert template.content == content
        assert template.category == "test"
        assert template.version == "1.0.0"
        assert template.metadata["author"] == "test_user"
        assert len(template.placeholders) > 0
        assert "{primary_keyword}" in template.placeholders
        assert "{secondary_keywords}" in template.placeholders
    
    def test_criar_template_conteudo_invalido(self, service):
        """Testa criação de template com conteúdo inválido."""
        # Conteúdo muito curto
        with pytest.raises(ValueError):
            service.criar_template(
                name="test",
                content="Curto"
            )
        
        # Conteúdo sem placeholders
        with pytest.raises(ValueError):
            service.criar_template(
                name="test",
                content="Conteúdo sem placeholders válidos"
            )
    
    def test_atualizar_template(self, service):
        """Testa atualização de template."""
        # Criar template
        template = service.criar_template(
            name="original",
            content="Artigo sobre {primary_keyword}",
            category="original",
            version="1.0.0"
        )
        
        # Atualizar template
        updated_template = service.atualizar_template(
            template_id=template.id,
            content="Artigo atualizado sobre {primary_keyword}",
            name="updated",
            category="updated",
            version="2.0.0"
        )
        
        assert updated_template is not None
        assert updated_template.name == "updated"
        assert updated_template.category == "updated"
        assert updated_template.version == "2.0.0"
        assert "atualizado" in updated_template.content
    
    def test_atualizar_template_inexistente(self, service):
        """Testa atualização de template inexistente."""
        result = service.atualizar_template(
            template_id="inexistente",
            content="novo conteúdo"
        )
        
        assert result is None
    
    def test_remover_template(self, service):
        """Testa remoção de template."""
        # Criar template
        template = service.criar_template(
            name="to_remove",
            content="Artigo sobre {primary_keyword}"
        )
        
        # Remover template
        success = service.remover_template(template.id)
        assert success is True
        
        # Verificar se foi removido
        assert template.id not in service.template_cache
    
    def test_remover_template_inexistente(self, service):
        """Testa remoção de template inexistente."""
        success = service.remover_template("inexistente")
        assert success is False
    
    def test_listar_templates(self, service):
        """Testa listagem de templates."""
        # Criar templates
        template1 = service.criar_template(
            name="template1",
            content="Artigo sobre {primary_keyword}",
            category="marketing"
        )
        template2 = service.criar_template(
            name="template2",
            content="Artigo sobre {secondary_keywords}",
            category="seo"
        )
        
        # Listar todos
        all_templates = service.listar_templates()
        assert len(all_templates) >= 2
        
        # Filtrar por categoria
        marketing_templates = service.listar_templates(category="marketing")
        assert len(marketing_templates) >= 1
        assert all(t.category == "marketing" for t in marketing_templates)
        
        # Filtrar por versão
        v1_templates = service.listar_templates(version="1.0.0")
        assert len(v1_templates) >= 2
        assert all(t.version == "1.0.0" for t in v1_templates)
    
    def test_buscar_template(self, service):
        """Testa busca de template por ID."""
        template = service.criar_template(
            name="test_search",
            content="Artigo sobre {primary_keyword}"
        )
        
        found_template = service.buscar_template(template.id)
        assert found_template is not None
        assert found_template.id == template.id
        assert found_template.name == "test_search"
    
    def test_buscar_template_por_nome(self, service):
        """Testa busca de template por nome."""
        template = service.criar_template(
            name="test_name_search",
            content="Artigo sobre {primary_keyword}"
        )
        
        found_template = service.buscar_template_por_nome("test_name_search")
        assert found_template is not None
        assert found_template.name == "test_name_search"
    
    def test_gerar_prompt(self, service, sample_data):
        """Testa geração de prompt."""
        # Criar template
        template = service.criar_template(
            name="test_generation",
            content="Artigo sobre {primary_keyword} com {secondary_keywords}"
        )
        
        # Gerar prompt
        prompt, metadata = service.gerar_prompt(template.id, sample_data)
        
        assert isinstance(prompt, str)
        assert "marketing digital" in prompt
        assert "seo, ads, social media" in prompt
        
        assert isinstance(metadata, dict)
        assert metadata['template_id'] == template.id
        assert metadata['template_name'] == "test_generation"
        assert 'primary_keyword' in metadata['placeholders_used']
        assert 'secondary_keywords' in metadata['placeholders_used']
    
    def test_gerar_prompt_template_inexistente(self, service, sample_data):
        """Testa geração de prompt com template inexistente."""
        with pytest.raises(ValueError):
            service.gerar_prompt("inexistente", sample_data)
    
    def test_gerar_prompt_com_cache(self, service, sample_data):
        """Testa geração de prompt com cache."""
        # Criar template
        template = service.criar_template(
            name="test_cache",
            content="Artigo sobre {primary_keyword}"
        )
        
        cache_key = "test_cache_key"
        
        # Primeira geração
        prompt1, metadata1 = service.gerar_prompt(template.id, sample_data, cache_key)
        
        # Segunda geração (deve usar cache)
        prompt2, metadata2 = service.gerar_prompt(template.id, sample_data, cache_key)
        
        assert prompt1 == prompt2
        assert metadata1['template_id'] == metadata2['template_id']
    
    def test_detectar_placeholders(self, service):
        """Testa detecção de placeholders."""
        content = """
        Artigo sobre {primary_keyword}
        Incluir {secondary_keywords}
        Cluster: {cluster_id}
        Categoria: {categoria}
        """
        
        placeholders = service._detectar_placeholders(content)
        
        assert len(placeholders) >= 4
        assert "{primary_keyword}" in placeholders
        assert "{secondary_keywords}" in placeholders
        assert "{cluster_id}" in placeholders
        assert "{categoria}" in placeholders
    
    def test_substituir_placeholders(self, service, sample_data):
        """Testa substituição de placeholders."""
        content = "Artigo sobre {primary_keyword} com {secondary_keywords}"
        
        result = service._substituir_placeholders(content, sample_data)
        
        assert "marketing digital" in result
        assert "seo, ads, social media" in result
        assert "{primary_keyword}" not in result
        assert "{secondary_keywords}" not in result
    
    def test_validar_template_content(self, service):
        """Testa validação de conteúdo de template."""
        # Conteúdo válido
        valid_content = "Artigo sobre {primary_keyword} com {secondary_keywords}"
        assert service._validar_template_content(valid_content) is True
        
        # Conteúdo muito curto
        short_content = "Curto"
        assert service._validar_template_content(short_content) is False
        
        # Conteúdo sem placeholders
        no_placeholders = "Artigo sem placeholders válidos"
        assert service._validar_template_content(no_placeholders) is False
    
    def test_extrair_metadados_txt(self, service):
        """Testa extração de metadados de TXT."""
        content = """# Template: Test Template
# Version: 1.0.0
# Category: test
# Author: test_user

Conteúdo do template aqui.
"""
        
        metadata = service._extrair_metadados_txt(content)
        
        assert metadata['Template'] == 'Test Template'
        assert metadata['Version'] == '1.0.0'
        assert metadata['Category'] == 'test'
        assert metadata['Author'] == 'test_user'
    
    def test_preparar_conteudo_txt(self, service):
        """Testa preparação de conteúdo para TXT."""
        template = service.criar_template(
            name="test_prep",
            content="Artigo sobre {primary_keyword}",
            category="test",
            version="1.0.0",
            metadata={"author": "test_user"}
        )
        
        content = service._preparar_conteudo_txt(template)
        
        assert "# Template: test_prep" in content
        assert "# Version: 1.0.0" in content
        assert "# Category: test" in content
        assert "# author: test_user" in content
        assert "Artigo sobre {primary_keyword}" in content
    
    def test_buscar_cache_prompt(self, service):
        """Testa busca de prompt no cache."""
        # Adicionar entrada ao cache
        cache_entry = PromptCache(
            content="cached content",
            hash="test_hash",
            created_at=datetime.utcnow(),
            ttl=3600,
            access_count=1
        )
        service.prompt_cache["test_key"] = cache_entry
        
        # Buscar no cache
        result = service._buscar_cache_prompt("test_key")
        
        assert result is not None
        assert result[0] == "cached content"
        assert result[1]['cache_hit'] is True
    
    def test_buscar_cache_prompt_expirado(self, service):
        """Testa busca de prompt expirado no cache."""
        # Adicionar entrada expirada ao cache
        from datetime import timedelta
        expired_time = datetime.utcnow() - timedelta(hours=2)
        cache_entry = PromptCache(
            content="expired content",
            hash="test_hash",
            created_at=expired_time,
            ttl=3600,
            access_count=1
        )
        service.prompt_cache["expired_key"] = cache_entry
        
        # Buscar no cache (deve retornar None e remover entrada)
        result = service._buscar_cache_prompt("expired_key")
        
        assert result is None
        assert "expired_key" not in service.prompt_cache
    
    def test_armazenar_cache_prompt(self, service):
        """Testa armazenamento de prompt no cache."""
        content = "test content"
        metadata = {"test": "data"}
        
        service._armazenar_cache_prompt("test_key", content, metadata)
        
        assert "test_key" in service.prompt_cache
        cache_entry = service.prompt_cache["test_key"]
        assert cache_entry.content == content
        assert cache_entry.access_count == 1
    
    def test_armazenar_cache_prompt_limite_excedido(self, service):
        """Testa armazenamento com limite de cache excedido."""
        # Configurar cache pequeno
        service.max_cache_size = 2
        
        # Adicionar entradas até o limite
        service._armazenar_cache_prompt("key1", "content1", {})
        service._armazenar_cache_prompt("key2", "content2", {})
        
        # Adicionar mais uma entrada (deve remover a mais antiga)
        service._armazenar_cache_prompt("key3", "content3", {})
        
        assert len(service.prompt_cache) == 2
        assert "key3" in service.prompt_cache
    
    def test_limpar_cache_por_template(self, service):
        """Testa limpeza de cache por template."""
        # Adicionar entradas ao cache
        service.prompt_cache["template_123_cache1"] = Mock()
        service.prompt_cache["template_123_cache2"] = Mock()
        service.prompt_cache["other_cache"] = Mock()
        
        # Limpar cache do template
        service._limpar_cache_por_template("template_123")
        
        assert "template_123_cache1" not in service.prompt_cache
        assert "template_123_cache2" not in service.prompt_cache
        assert "other_cache" in service.prompt_cache
    
    def test_limpar_cache(self, service):
        """Testa limpeza completa do cache."""
        # Adicionar dados ao cache
        service.prompt_cache["test1"] = Mock()
        service.template_cache["test2"] = Mock()
        
        # Limpar cache
        service.limpar_cache()
        
        assert len(service.prompt_cache) == 0
        assert len(service.template_cache) == 0
    
    def test_obter_estatisticas(self, service):
        """Testa obtenção de estatísticas."""
        stats = service.obter_estatisticas()
        
        assert isinstance(stats, dict)
        assert 'templates_count' in stats
        assert 'prompt_cache_size' in stats
        assert 'cache_enabled' in stats
        assert 'cache_ttl' in stats
        assert 'max_cache_size' in stats
        assert 'templates_dir' in stats
        
        assert stats['cache_enabled'] is True
        assert stats['cache_ttl'] == 3600
        assert stats['max_cache_size'] == 100
    
    def test_placeholder_patterns(self, service):
        """Testa padrões de placeholders."""
        patterns = service.placeholder_patterns
        
        assert 'primary_keyword' in patterns
        assert 'secondary_keywords' in patterns
        assert 'cluster_id' in patterns
        assert 'cluster_name' in patterns
        assert 'categoria' in patterns
        assert 'fase_funil' in patterns
        assert 'data' in patterns
        assert 'usuario' in patterns
        
        # Testar regex patterns
        import re
        
        # Testar primary_keyword pattern
        test_primary = "{primary_keyword}"
        assert re.search(patterns['primary_keyword'], test_primary)
        
        # Testar secondary_keywords pattern
        test_secondary = "{secondary_keywords}"
        assert re.search(patterns['secondary_keywords'], test_secondary)
        
        # Testar cluster_id pattern
        test_cluster = "{cluster_id}"
        assert re.search(patterns['cluster_id'], test_cluster) 