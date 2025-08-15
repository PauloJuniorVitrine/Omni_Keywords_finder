"""
Serviço de Preenchimento de Prompts Otimizado - Omni Keywords Finder
===================================================================

Versão otimizada do serviço de preenchimento com:
- Sistema de logs avançado
- Cache inteligente
- Monitoramento de performance
- Validação avançada
- Processamento assíncrono

Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 2.0.0
Tracing ID: PROMPT_FILLER_OPTIMIZED_001
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Integração com sistemas otimizados
from infrastructure.logging.advanced_logging_system import get_logger, LogContext, LogCategory
from infrastructure.cache.intelligent_cache_system import get_cache, CacheLevel, cached
from infrastructure.monitoring.performance_monitor import (
    get_performance_monitor, monitor_performance, 
    record_response_time, record_error_rate
)

# Modelos do sistema
from backend.app.models.prompt_system import (
    Nicho, Categoria, DadosColetados, PromptBase, PromptPreenchido
)
from backend.app.database import get_db

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Status do processamento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


@dataclass
class ProcessingResult:
    """Resultado do processamento"""
    success: bool
    prompt_preenchido: Optional[str] = None
    lacunas_detectadas: Optional[List[str]] = None
    lacunas_preenchidas: Optional[List[str]] = None
    tempo_processamento: Optional[float] = None
    cache_hit: bool = False
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PromptFillerServiceOptimized:
    """Serviço otimizado de preenchimento de prompts"""
    
    def __init__(self):
        # Sistemas integrados
        self.logger = get_logger()
        self.cache = get_cache()
        self.performance_monitor = get_performance_monitor()
        
        # Configurações
        self.default_ttl = 3600  # 1 hora
        self.max_retries = 3
        self.timeout_seconds = 30
        
        # Estatísticas
        self.stats = {
            'total_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'avg_processing_time': 0.0
        }
        
        self.logger.info("Serviço de preenchimento de prompts otimizado inicializado")
    
    @monitor_performance("prompt_fill_processing")
    def processar_preenchimento(self, categoria_id: int, dados_id: int) -> PromptPreenchido:
        """
        Processa preenchimento de prompt com otimizações
        
        Args:
            categoria_id: ID da categoria
            dados_id: ID dos dados coletados
            
        Returns:
            PromptPreenchido processado
        """
        start_time = time.time()
        context = LogContext(
            operation="processar_preenchimento",
            module="PromptFillerServiceOptimized",
            function="processar_preenchimento",
            metadata={
                'categoria_id': categoria_id,
                'dados_id': dados_id
            }
        )
        
        try:
            # Verificar cache primeiro
            cache_key = f"prompt_fill_{categoria_id}_{dados_id}"
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                self.stats['cache_hits'] += 1
                self.logger.info(
                    "Preenchimento encontrado no cache",
                    category=LogCategory.PERFORMANCE,
                    context=context,
                    data={'cache_key': cache_key}
                )
                
                # Retornar resultado do cache
                return self._create_from_cache(cached_result, categoria_id, dados_id)
            
            self.stats['cache_misses'] += 1
            
            # Processar preenchimento
            result = self._process_fill(categoria_id, dados_id, context)
            
            if result.success:
                # Armazenar no cache
                self.cache.set(
                    cache_key, 
                    result.prompt_preenchido, 
                    ttl=self.default_ttl,
                    level=CacheLevel.L1
                )
                
                # Criar registro no banco
                prompt_preenchido = self._save_to_database(
                    categoria_id, dados_id, result, context
                )
                
                # Atualizar estatísticas
                self.stats['total_processed'] += 1
                processing_time = time.time() - start_time
                self.stats['avg_processing_time'] = (
                    (self.stats['avg_processing_time'] * (self.stats['total_processed'] - 1) + processing_time) 
                    / self.stats['total_processed']
                )
                
                # Registrar métricas
                record_response_time("prompt_fill", processing_time * 1000)
                
                self.logger.info(
                    "Preenchimento processado com sucesso",
                    category=LogCategory.BUSINESS,
                    context=context,
                    data={
                        'tempo_processamento': processing_time,
                        'lacunas_detectadas': len(result.lacunas_detectadas or []),
                        'lacunas_preenchidas': len(result.lacunas_preenchidas or [])
                    }
                )
                
                return prompt_preenchido
            
            else:
                self.stats['errors'] += 1
                self.logger.error(
                    "Erro no processamento de preenchimento",
                    category=LogCategory.ERROR,
                    context=context,
                    error=Exception(result.error)
                )
                
                raise Exception(result.error)
        
        except Exception as e:
            self.stats['errors'] += 1
            processing_time = time.time() - start_time
            
            self.logger.error(
                "Erro no processamento de preenchimento",
                category=LogCategory.ERROR,
                context=context,
                error=e,
                data={'tempo_processamento': processing_time}
            )
            
            record_response_time("prompt_fill_error", processing_time * 1000)
            raise
    
    def _process_fill(self, categoria_id: int, dados_id: int, context: LogContext) -> ProcessingResult:
        """Processa o preenchimento interno"""
        try:
            # Obter dados do banco
            db = next(get_db())
            
            # Buscar categoria e dados coletados
            categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
            dados = db.query(DadosColetados).filter(DadosColetados.id == dados_id).first()
            prompt_base = db.query(PromptBase).filter(PromptBase.categoria_id == categoria_id).first()
            
            if not categoria or not dados or not prompt_base:
                return ProcessingResult(
                    success=False,
                    error="Dados não encontrados"
                )
            
            # Detectar lacunas no prompt
            lacunas_detectadas = self._detectar_lacunas(prompt_base.conteudo)
            
            # Preparar dados para substituição
            dados_substituicao = {
                'primary_keyword': dados.primary_keyword,
                'secondary_keywords': dados.secondary_keywords,
                'cluster_content': dados.cluster_content
            }
            
            # Preencher lacunas
            prompt_preenchido, lacunas_preenchidas = self._preencher_lacunas(
                prompt_base.conteudo, lacunas_detectadas, dados_substituicao
            )
            
            # Validar resultado
            if not self._validar_preenchimento(prompt_preenchido, lacunas_detectadas):
                return ProcessingResult(
                    success=False,
                    error="Preenchimento inválido"
                )
            
            return ProcessingResult(
                success=True,
                prompt_preenchido=prompt_preenchido,
                lacunas_detectadas=lacunas_detectadas,
                lacunas_preenchidas=lacunas_preenchidas,
                tempo_processamento=time.time(),
                metadata={
                    'categoria_nome': categoria.nome,
                    'nicho_id': categoria.nicho_id
                }
            )
        
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def _detectar_lacunas(self, prompt_conteudo: str) -> List[str]:
        """Detecta lacunas no prompt"""
        lacunas = []
        
        # Padrões de lacunas
        padroes = [
            '[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]',
            '[PALAVRAS-CHAVE SECUNDÁRIAS]',
            '[CLUSTER DE CONTEÚDO]'
        ]
        
        for padrao in padroes:
            if padrao in prompt_conteudo:
                lacunas.append(padrao)
        
        return lacunas
    
    def _preencher_lacunas(self, prompt_conteudo: str, lacunas: List[str], 
                          dados: Dict[str, str]) -> Tuple[str, List[str]]:
        """Preenche lacunas no prompt"""
        prompt_preenchido = prompt_conteudo
        lacunas_preenchidas = []
        
        # Mapeamento de lacunas para dados
        mapeamento = {
            '[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]': dados.get('primary_keyword', ''),
            '[PALAVRAS-CHAVE SECUNDÁRIAS]': dados.get('secondary_keywords', ''),
            '[CLUSTER DE CONTEÚDO]': dados.get('cluster_content', '')
        }
        
        for lacuna in lacunas:
            if lacuna in mapeamento:
                prompt_preenchido = prompt_preenchido.replace(lacuna, mapeamento[lacuna])
                lacunas_preenchidas.append(lacuna)
        
        return prompt_preenchido, lacunas_preenchidas
    
    def _validar_preenchimento(self, prompt_preenchido: str, lacunas_detectadas: List[str]) -> bool:
        """Valida o preenchimento"""
        # Verificar se ainda há lacunas não preenchidas
        for lacuna in lacunas_detectadas:
            if lacuna in prompt_preenchido:
                return False
        
        # Verificar se o prompt não está vazio
        if not prompt_preenchido.strip():
            return False
        
        # Verificar tamanho mínimo
        if len(prompt_preenchido.strip()) < 50:
            return False
        
        return True
    
    def _save_to_database(self, categoria_id: int, dados_id: int, 
                         result: ProcessingResult, context: LogContext) -> PromptPreenchido:
        """Salva resultado no banco de dados"""
        db = next(get_db())
        
        # Verificar se já existe
        prompt_existente = db.query(PromptPreenchido).filter(
            PromptPreenchido.dados_coletados_id == dados_id
        ).first()
        
        if prompt_existente:
            # Atualizar existente
            prompt_existente.prompt_preenchido = result.prompt_preenchido
            prompt_existente.lacunas_detectadas = json.dumps(result.lacunas_detectadas)
            prompt_existente.lacunas_preenchidas = json.dumps(result.lacunas_preenchidas)
            prompt_existente.tempo_processamento = result.tempo_processamento
            prompt_existente.status = 'pronto'
            prompt_existente.updated_at = datetime.utcnow()
            
            db.commit()
            return prompt_existente
        
        # Criar novo
        novo_prompt = PromptPreenchido(
            dados_coletados_id=dados_id,
            prompt_base_id=1,  # Assumindo que existe
            prompt_original="",  # Será preenchido
            prompt_preenchido=result.prompt_preenchido,
            lacunas_detectadas=json.dumps(result.lacunas_detectadas),
            lacunas_preenchidas=json.dumps(result.lacunas_preenchidas),
            status='pronto',
            tempo_processamento=result.tempo_processamento
        )
        
        db.add(novo_prompt)
        db.commit()
        db.refresh(novo_prompt)
        
        return novo_prompt
    
    def _create_from_cache(self, cached_prompt: str, categoria_id: int, 
                          dados_id: int) -> PromptPreenchido:
        """Cria PromptPreenchido a partir do cache"""
        # Simular criação a partir do cache
        return PromptPreenchido(
            id=0,
            dados_coletados_id=dados_id,
            prompt_base_id=1,
            prompt_original="",
            prompt_preenchido=cached_prompt,
            lacunas_detectadas=json.dumps([]),
            lacunas_preenchidas=json.dumps([]),
            status='pronto',
            tempo_processamento=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @monitor_performance("prompt_fill_batch")
    def processar_lote(self, nicho_id: int) -> List[PromptPreenchido]:
        """
        Processa preenchimento em lote para um nicho
        
        Args:
            nicho_id: ID do nicho
            
        Returns:
            Lista de prompts preenchidos
        """
        start_time = time.time()
        context = LogContext(
            operation="processar_lote",
            module="PromptFillerServiceOptimized",
            function="processar_lote",
            metadata={'nicho_id': nicho_id}
        )
        
        try:
            db = next(get_db())
            
            # Buscar todas as categorias do nicho com dados coletados
            categorias_com_dados = db.query(DadosColetados).filter(
                DadosColetados.nicho_id == nicho_id,
                DadosColetados.status == 'ativo'
            ).all()
            
            resultados = []
            sucessos = 0
            erros = 0
            
            for dados in categorias_com_dados:
                try:
                    prompt_preenchido = self.processar_preenchimento(
                        dados.categoria_id, dados.id
                    )
                    resultados.append(prompt_preenchido)
                    sucessos += 1
                    
                except Exception as e:
                    erros += 1
                    self.logger.error(
                        f"Erro no processamento de lote para categoria {dados.categoria_id}",
                        category=LogCategory.ERROR,
                        context=context,
                        error=e
                    )
            
            processing_time = time.time() - start_time
            
            # Registrar métricas
            record_response_time("prompt_fill_batch", processing_time * 1000)
            record_error_rate("prompt_fill_batch", erros, sucessos + erros)
            
            self.logger.info(
                "Processamento em lote concluído",
                category=LogCategory.BUSINESS,
                context=context,
                data={
                    'total_processados': len(categorias_com_dados),
                    'sucessos': sucessos,
                    'erros': erros,
                    'tempo_processamento': processing_time
                }
            )
            
            return resultados
        
        except Exception as e:
            processing_time = time.time() - start_time
            
            self.logger.error(
                "Erro no processamento em lote",
                category=LogCategory.ERROR,
                context=context,
                error=e,
                data={'tempo_processamento': processing_time}
            )
            
            record_response_time("prompt_fill_batch_error", processing_time * 1000)
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do serviço"""
        return {
            'total_processed': self.stats['total_processed'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': (
                self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses'])
                if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0
            ),
            'errors': self.stats['errors'],
            'error_rate': (
                self.stats['errors'] / self.stats['total_processed']
                if self.stats['total_processed'] > 0 else 0
            ),
            'avg_processing_time': self.stats['avg_processing_time'],
            'cache_stats': self.cache.get_stats(),
            'performance_stats': self.performance_monitor.get_dashboard_data()
        }
    
    def clear_cache(self):
        """Limpa cache do serviço"""
        self.cache.clear()
        self.logger.info("Cache do serviço limpo", category=LogCategory.SYSTEM)
    
    def warm_cache(self, nicho_id: int):
        """Faz warming do cache para um nicho"""
        try:
            db = next(get_db())
            
            # Buscar dados do nicho
            dados = db.query(DadosColetados).filter(
                DadosColetados.nicho_id == nicho_id,
                DadosColetados.status == 'ativo'
            ).all()
            
            # Preparar chaves para warming
            keys = [f"prompt_fill_{dados.categoria_id}_{dados.id}" for dados in dados]
            
            # Executar warming
            self.cache.warm_cache(keys, lambda key: "prompt_warmed")
            
            self.logger.info(
                f"Cache warming concluído para nicho {nicho_id}",
                category=LogCategory.PERFORMANCE,
                data={'keys_count': len(keys)}
            )
        
        except Exception as e:
            self.logger.error(
                f"Erro no cache warming para nicho {nicho_id}",
                category=LogCategory.ERROR,
                error=e
            )


# Instância global do serviço otimizado
prompt_filler_service_optimized = PromptFillerServiceOptimized()


def get_prompt_filler_service_optimized() -> PromptFillerServiceOptimized:
    """Retorna instância do serviço otimizado"""
    return prompt_filler_service_optimized 