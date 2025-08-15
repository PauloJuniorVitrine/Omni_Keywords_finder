"""
Serviço Unificado de Prompts
Responsável por gerenciar templates dinâmicos, cache de prompts e carregamento via arquivos TXT.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 1.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import re

from shared.logger import logger
from domain.models import Keyword, Cluster

@dataclass
class PromptTemplate:
    """Template de prompt com metadados."""
    id: str
    name: str
    content: str
    placeholders: List[str]
    category: str
    version: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

@dataclass
class PromptCache:
    """Cache de prompt com TTL."""
    content: str
    hash: str
    created_at: datetime
    ttl: int  # segundos
    access_count: int

class PromptUnifiedService:
    """
    Serviço unificado para gerenciamento de prompts.
    
    Funcionalidades:
    - Carregamento de templates via arquivos TXT
    - Cache inteligente com TTL
    - CRUD completo de prompts
    - Validação de templates
    - Sistema de versionamento
    """
    
    def __init__(
        self,
        templates_dir: str = "prompts/templates",
        cache_enabled: bool = True,
        cache_ttl: int = 3600,  # 1 hora
        max_cache_size: int = 1000
    ):
        """
        Inicializa o serviço unificado de prompts.
        
        Args:
            templates_dir: Diretório de templates
            cache_enabled: Habilita cache de prompts
            cache_ttl: TTL do cache em segundos
            max_cache_size: Tamanho máximo do cache
        """
        self.templates_dir = Path(templates_dir)
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        
        # Cache de prompts
        self.prompt_cache: Dict[str, PromptCache] = {}
        self.template_cache: Dict[str, PromptTemplate] = {}
        
        # Criar diretório se não existir
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Padrões de placeholders
        self.placeholder_patterns = {
            'primary_keyword': r'\{primary_keyword\}',
            'secondary_keywords': r'\{secondary_keywords\}',
            'cluster_id': r'\{cluster_id\}',
            'cluster_name': r'\{cluster_name\}',
            'categoria': r'\{categoria\}',
            'fase_funil': r'\{fase_funil\}',
            'data': r'\{data\}',
            'usuario': r'\{usuario\}'
        }
        
        logger.info(f"PromptUnifiedService initialized with templates_dir: {templates_dir}")
    
    def carregar_template_txt(self, file_path: str) -> PromptTemplate:
        """
        Carrega template de arquivo TXT.
        
        Args:
            file_path: Caminho do arquivo TXT
            
        Returns:
            Template carregado
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Template file not found: {file_path}")
            
            # Ler conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrair metadados do cabeçalho (se existir)
            metadata = self._extrair_metadados_txt(content)
            
            # Detectar placeholders
            placeholders = self._detectar_placeholders(content)
            
            # Gerar ID único
            template_id = hashlib.md5(f"{file_path}_{content}".encode()).hexdigest()
            
            # Criar template
            template = PromptTemplate(
                id=template_id,
                name=file_path.stem,
                content=content,
                placeholders=placeholders,
                category=metadata.get('category', 'default'),
                version=metadata.get('version', '1.0.0'),
                created_at=datetime.fromtimestamp(file_path.stat().st_ctime),
                updated_at=datetime.fromtimestamp(file_path.stat().st_mtime),
                metadata=metadata
            )
            
            # Armazenar no cache
            if self.cache_enabled:
                self.template_cache[template_id] = template
            
            logger.info(f"Template loaded from TXT: {file_path.name} ({len(placeholders)} placeholders)")
            return template
            
        except Exception as e:
            logger.error(f"Error loading template from TXT: {e}")
            raise
    
    def salvar_template_txt(self, template: PromptTemplate, file_path: str) -> bool:
        """
        Salva template em arquivo TXT.
        
        Args:
            template: Template a ser salvo
            file_path: Caminho do arquivo
            
        Returns:
            True se salvo com sucesso
        """
        try:
            file_path = Path(file_path)
            
            # Preparar conteúdo com metadados
            content = self._preparar_conteudo_txt(template)
            
            # Salvar arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Template saved to TXT: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving template to TXT: {e}")
            return False
    
    def criar_template(
        self,
        name: str,
        content: str,
        category: str = "default",
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromptTemplate:
        """
        Cria novo template.
        
        Args:
            name: Nome do template
            content: Conteúdo do template
            category: Categoria do template
            version: Versão do template
            metadata: Metadados adicionais
            
        Returns:
            Template criado
        """
        # Validar conteúdo
        if not self._validar_template_content(content):
            raise ValueError("Invalid template content")
        
        # Detectar placeholders
        placeholders = self._detectar_placeholders(content)
        
        # Gerar ID único
        template_id = hashlib.md5(f"{name}_{content}_{time.time()}".encode()).hexdigest()
        
        # Criar template
        template = PromptTemplate(
            id=template_id,
            name=name,
            content=content,
            placeholders=placeholders,
            category=category,
            version=version,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Armazenar no cache
        if self.cache_enabled:
            self.template_cache[template_id] = template
        
        logger.info(f"Template created: {name} ({len(placeholders)} placeholders)")
        return template
    
    def atualizar_template(
        self,
        template_id: str,
        content: Optional[str] = None,
        name: Optional[str] = None,
        category: Optional[str] = None,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[PromptTemplate]:
        """
        Atualiza template existente.
        
        Args:
            template_id: ID do template
            content: Novo conteúdo
            name: Novo nome
            category: Nova categoria
            version: Nova versão
            metadata: Novos metadados
            
        Returns:
            Template atualizado ou None se não encontrado
        """
        if template_id not in self.template_cache:
            logger.warning(f"Template not found: {template_id}")
            return None
        
        template = self.template_cache[template_id]
        
        # Atualizar campos
        if content is not None:
            if not self._validar_template_content(content):
                raise ValueError("Invalid template content")
            template.content = content
            template.placeholders = self._detectar_placeholders(content)
        
        if name is not None:
            template.name = name
        
        if category is not None:
            template.category = category
        
        if version is not None:
            template.version = version
        
        if metadata is not None:
            template.metadata.update(metadata)
        
        template.updated_at = datetime.utcnow()
        
        logger.info(f"Template updated: {template.name}")
        return template
    
    def remover_template(self, template_id: str) -> bool:
        """
        Remove template.
        
        Args:
            template_id: ID do template
            
        Returns:
            True se removido com sucesso
        """
        if template_id in self.template_cache:
            template = self.template_cache[template_id]
            del self.template_cache[template_id]
            
            # Limpar cache de prompts relacionados
            self._limpar_cache_por_template(template_id)
            
            logger.info(f"Template removed: {template.name}")
            return True
        
        logger.warning(f"Template not found for removal: {template_id}")
        return False
    
    def listar_templates(
        self,
        category: Optional[str] = None,
        version: Optional[str] = None
    ) -> List[PromptTemplate]:
        """
        Lista templates com filtros opcionais.
        
        Args:
            category: Filtrar por categoria
            version: Filtrar por versão
            
        Returns:
            Lista de templates
        """
        templates = list(self.template_cache.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if version:
            templates = [t for t in templates if t.version == version]
        
        return sorted(templates, key=lambda t: t.updated_at, reverse=True)
    
    def buscar_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Busca template por ID.
        
        Args:
            template_id: ID do template
            
        Returns:
            Template encontrado ou None
        """
        return self.template_cache.get(template_id)
    
    def buscar_template_por_nome(self, name: str) -> Optional[PromptTemplate]:
        """
        Busca template por nome.
        
        Args:
            name: Nome do template
            
        Returns:
            Template encontrado ou None
        """
        for template in self.template_cache.values():
            if template.name == name:
                return template
        return None
    
    def gerar_prompt(
        self,
        template_id: str,
        dados: Dict[str, Any],
        cache_key: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Gera prompt a partir de template e dados.
        
        Args:
            template_id: ID do template
            dados: Dados para substituição
            cache_key: Chave personalizada para cache
            
        Returns:
            Tuple (prompt gerado, metadados)
        """
        # Buscar template
        template = self.buscar_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Verificar cache
        if self.cache_enabled and cache_key:
            cached_result = self._buscar_cache_prompt(cache_key)
            if cached_result:
                logger.info(f"Prompt retrieved from cache: {cache_key}")
                return cached_result
        
        # Gerar prompt
        start_time = time.time()
        prompt_gerado = self._substituir_placeholders(template.content, dados)
        
        # Preparar metadados
        metadata = {
            'template_id': template_id,
            'template_name': template.name,
            'template_version': template.version,
            'placeholders_used': list(dados.keys()),
            'placeholders_available': template.placeholders,
            'generation_time': time.time() - start_time,
            'prompt_length': len(prompt_gerado),
            'word_count': len(prompt_gerado.split())
        }
        
        # Armazenar no cache
        if self.cache_enabled and cache_key:
            self._armazenar_cache_prompt(cache_key, prompt_gerado, metadata)
        
        logger.info(f"Prompt generated from template: {template.name}")
        return prompt_gerado, metadata
    
    def _detectar_placeholders(self, content: str) -> List[str]:
        """Detecta placeholders no conteúdo."""
        placeholders = []
        for pattern in self.placeholder_patterns.values():
            matches = re.findall(pattern, content)
            placeholders.extend(matches)
        return list(set(placeholders))
    
    def _substituir_placeholders(self, content: str, dados: Dict[str, Any]) -> str:
        """Substitui placeholders pelos dados."""
        prompt = content
        
        # Substituir placeholders conhecidos
        for placeholder, pattern in self.placeholder_patterns.items():
            if placeholder in dados:
                value = str(dados[placeholder])
                prompt = re.sub(pattern, value, prompt)
        
        # Substituir placeholders dinâmicos
        for key, value in dados.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        
        # Remover placeholders não preenchidos
        prompt = re.sub(r'\{[^}]+\}', '', prompt)
        
        return prompt
    
    def _validar_template_content(self, content: str) -> bool:
        """Valida conteúdo do template."""
        if not content or len(content.strip()) < 10:
            return False
        
        # Verificar se tem pelo menos um placeholder
        placeholders = self._detectar_placeholders(content)
        if not placeholders:
            return False
        
        return True
    
    def _extrair_metadados_txt(self, content: str) -> Dict[str, Any]:
        """Extrai metadados do cabeçalho TXT."""
        metadata = {}
        
        # Procurar por comentários no início do arquivo
        lines = content.split('\n')
        for line in lines[:10]:  # Primeiras 10 linhas
            line = line.strip()
            if line.startswith('#') or line.startswith('//'):
                # Formato: # key: value
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.lstrip('#').lstrip('/').strip()
                    value = value.strip()
                    metadata[key] = value
        
        return metadata
    
    def _preparar_conteudo_txt(self, template: PromptTemplate) -> str:
        """Prepara conteúdo para salvar em TXT."""
        content = f"# Template: {template.name}\n"
        content += f"# Version: {template.version}\n"
        content += f"# Category: {template.category}\n"
        content += f"# Created: {template.created_at.isoformat()}\n"
        content += f"# Updated: {template.updated_at.isoformat()}\n"
        
        # Adicionar metadados customizados
        for key, value in template.metadata.items():
            content += f"# {key}: {value}\n"
        
        content += "\n"
        content += template.content
        
        return content
    
    def _buscar_cache_prompt(self, cache_key: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Busca prompt no cache."""
        if cache_key in self.prompt_cache:
            cache_entry = self.prompt_cache[cache_key]
            
            # Verificar TTL
            if time.time() - cache_entry.created_at.timestamp() < cache_entry.ttl:
                cache_entry.access_count += 1
                return cache_entry.content, {'cache_hit': True, 'access_count': cache_entry.access_count}
            else:
                # Expirou, remover
                del self.prompt_cache[cache_key]
        
        return None
    
    def _armazenar_cache_prompt(self, cache_key: str, content: str, metadata: Dict[str, Any]):
        """Armazena prompt no cache."""
        # Verificar tamanho do cache
        if len(self.prompt_cache) >= self.max_cache_size:
            # Remover entrada mais antiga
            oldest_key = min(self.prompt_cache.keys(), 
                           key=lambda key: self.prompt_cache[key].created_at.timestamp())
            del self.prompt_cache[oldest_key]
        
        # Criar entrada de cache
        cache_entry = PromptCache(
            content=content,
            hash=hashlib.md5(content.encode()).hexdigest(),
            created_at=datetime.utcnow(),
            ttl=self.cache_ttl,
            access_count=1
        )
        
        self.prompt_cache[cache_key] = cache_entry
    
    def _limpar_cache_por_template(self, template_id: str):
        """Limpa cache de prompts relacionados ao template."""
        keys_to_remove = []
        for key in self.prompt_cache.keys():
            if template_id in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.prompt_cache[key]
    
    def limpar_cache(self):
        """Limpa todo o cache."""
        self.prompt_cache.clear()
        self.template_cache.clear()
        logger.info("Prompt cache cleared")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do serviço."""
        return {
            'templates_count': len(self.template_cache),
            'prompt_cache_size': len(self.prompt_cache),
            'cache_enabled': self.cache_enabled,
            'cache_ttl': self.cache_ttl,
            'max_cache_size': self.max_cache_size,
            'templates_dir': str(self.templates_dir)
        }
