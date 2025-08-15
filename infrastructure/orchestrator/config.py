"""
Configuração do Orquestrador - Omni Keywords Finder

Configurações centralizadas para o fluxo completo de processamento.
Inclui parâmetros por nicho, limites de processamento e configurações
de integração com APIs externas.

Tracing ID: CONFIG_001_20241227
Versão: 2.0
Autor: IA-Cursor
Status: ✅ CONSOLIDADO E UNIFICADO
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NichoType(Enum):
    """Tipos de nichos suportados pelo sistema."""
    SAUDE = "saude"
    FINANCAS = "financas"
    TECNOLOGIA = "tecnologia"
    EDUCACAO = "educacao"
    VIAGENS = "viagens"
    ALIMENTACAO = "alimentacao"
    FITNESS = "fitness"
    NEGOCIOS = "negocios"
    AUTOMOVEIS = "automoveis"
    CASA = "casa"


@dataclass
class ColetaConfig:
    """Configurações específicas para etapa de coleta."""
    # Configurações gerais
    max_keywords_por_nicho: int = 1000
    timeout_segundos: int = 30
    retry_attempts: int = 3
    delay_entre_requests: float = 1.0
    
    # Coletores habilitados
    usar_google_keyword_planner: bool = True
    usar_google_suggest: bool = True
    usar_google_trends: bool = True
    usar_google_paa: bool = True
    usar_amazon: bool = True
    usar_reddit: bool = True
    usar_pinterest: bool = True
    usar_youtube: bool = True
    usar_tiktok: bool = True
    usar_instagram: bool = True
    usar_discord: bool = True
    usar_gsc: bool = True
    
    # Delays específicos por coletor
    delays_por_coletor: Dict[str, float] = field(default_factory=lambda: {
        'google_keyword_planner': 2.0,
        'google_suggest': 1.0,
        'google_trends': 1.5,
        'google_paa': 1.5,
        'amazon': 2.0,
        'reddit': 1.0,
        'pinterest': 1.0,
        'youtube': 1.5,
        'tiktok': 1.0,
        'instagram': 2.0,
        'discord': 1.0,
        'gsc': 1.0
    })


@dataclass
class ValidacaoConfig:
    """Configurações específicas para etapa de validação."""
    # Configurações Google Keyword Planner
    google_api_key: Optional[str] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_customer_id: Optional[str] = None
    
    # Critérios de validação
    min_search_volume: int = 100
    max_competition: float = 0.8
    min_cpc: float = 0.1
    max_cpc: float = 10.0
    rate_limit_requests_por_minuto: int = 60
    fallback_enabled: bool = True
    
    # Estratégia de validação
    estrategia_padrao: str = "cascata"  # cascata, paralela, consenso


@dataclass
class ProcessamentoConfig:
    """Configurações específicas para etapa de processamento."""
    # Configurações ML
    usar_ml: bool = True
    min_score_qualidade: float = 0.7
    max_keywords_por_cluster: int = 50
    use_ml_para_clustering: bool = True
    similarity_threshold: float = 0.8
    remove_duplicates: bool = True
    
    # Filtros de qualidade
    score_minimo: float = 0.0
    volume_minimo: int = 0
    cpc_maximo: float = float('inf')
    concorrencia_maxima: float = 1.0


@dataclass
class PreenchimentoConfig:
    """Configurações específicas para etapa de preenchimento."""
    max_prompts_por_keyword: int = 3
    use_ai_para_geracao: bool = True
    min_qualidade_prompt: float = 0.8
    templates_disponiveis: list = field(default_factory=lambda: [
        "blog_post", "social_media", "email", "landing_page"
    ])


@dataclass
class ExportacaoConfig:
    """Configurações específicas para etapa de exportação."""
    formato_saida: str = "zip"
    incluir_metadados: bool = True
    organizar_por_categoria: bool = True
    max_tamanho_arquivo_mb: int = 100
    cleanup_arquivos_antigos: bool = True
    dias_para_cleanup: int = 30


@dataclass
class NichoConfig:
    """Configuração completa para um nicho específico."""
    nome: str
    tipo: NichoType
    coleta: ColetaConfig = field(default_factory=ColetaConfig)
    validacao: ValidacaoConfig = field(default_factory=ValidacaoConfig)
    processamento: ProcessamentoConfig = field(default_factory=ProcessamentoConfig)
    preenchimento: PreenchimentoConfig = field(default_factory=PreenchimentoConfig)
    exportacao: ExportacaoConfig = field(default_factory=ExportacaoConfig)
    
    # Configurações específicas do nicho
    keywords_semente: list = field(default_factory=list)
    categorias: list = field(default_factory=list)
    idioma: str = "pt-BR"
    regiao: str = "BR"


@dataclass
class OrchestratorConfig:
    """Configuração principal do orquestrador."""
    
    # Configurações gerais
    tracing_id: str = "ORCHESTRATOR_001_20241227"
    modo_debug: bool = False
    log_level: str = "INFO"
    
    # Configurações de performance
    max_nichos_concorrentes: int = 1  # Processamento sequencial
    timeout_total_minutos: int = 120
    max_memoria_mb: int = 2048
    
    # Configurações de persistência
    persistir_progresso: bool = True
    diretorio_temporario: str = "/tmp/omni_orchestrator"
    diretorio_saida: str = "blogs/saida_zip"
    
    # Configurações de notificação
    notificar_progresso: bool = True
    notificar_erros: bool = True
    notificar_conclusao: bool = True
    
    # Configurações de métricas
    coletar_metricas: bool = True
    intervalo_metricas_segundos: int = 30
    
    # Nichos configurados
    nichos: Dict[str, NichoConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicialização pós-criação da instância."""
        self._carregar_configuracoes_padrao()
        self._validar_configuracoes()
    
    def _carregar_configuracoes_padrao(self):
        """Carrega configurações padrão para nichos comuns."""
        if not self.nichos:
            self.nichos = {
                "saude": NichoConfig(
                    nome="Saúde e Bem-estar",
                    tipo=NichoType.SAUDE,
                    keywords_semente=["saúde", "bem-estar", "medicina", "fitness"],
                    categorias=["nutrição", "exercícios", "medicina", "bem-estar"]
                ),
                "financas": NichoConfig(
                    nome="Finanças Pessoais",
                    tipo=NichoType.FINANCAS,
                    keywords_semente=["investimentos", "economia", "finanças", "dinheiro"],
                    categorias=["investimentos", "economia", "poupança", "crédito"]
                ),
                "tecnologia": NichoConfig(
                    nome="Tecnologia",
                    tipo=NichoType.TECNOLOGIA,
                    keywords_semente=["tecnologia", "programação", "software", "hardware"],
                    categorias=["programação", "hardware", "software", "mobile"]
                )
            }
    
    def _validar_configuracoes(self):
        """Valida as configurações carregadas."""
        if not self.nichos:
            raise ValueError("Pelo menos um nicho deve ser configurado")
        
        for nome_nicho, config in self.nichos.items():
            if not config.nome:
                raise ValueError(f"Nome do nicho '{nome_nicho}' não pode ser vazio")
            
            if config.coleta.max_keywords_por_nicho <= 0:
                raise ValueError(f"Max keywords por nicho deve ser > 0 para '{nome_nicho}'")
    
    def obter_config_nicho(self, nome_nicho: str) -> NichoConfig:
        """Obtém configuração de um nicho específico."""
        if nome_nicho not in self.nichos:
            raise ValueError(f"Nicho '{nome_nicho}' não encontrado nas configurações")
        
        return self.nichos[nome_nicho]
    
    def listar_nichos_disponiveis(self) -> list:
        """Lista todos os nichos configurados."""
        return list(self.nichos.keys())
    
    def adicionar_nicho(self, nome: str, config: NichoConfig):
        """Adiciona um novo nicho às configurações."""
        self.nichos[nome] = config
        logger.info(f"Nicho '{nome}' adicionado às configurações")
    
    def remover_nicho(self, nome: str):
        """Remove um nicho das configurações."""
        if nome in self.nichos:
            del self.nichos[nome]
            logger.info(f"Nicho '{nome}' removido das configurações")
        else:
            logger.warning(f"Nicho '{nome}' não encontrado para remoção")


def obter_config() -> OrchestratorConfig:
    """Obtém configuração padrão do orquestrador."""
    return OrchestratorConfig()


def carregar_config_do_arquivo(caminho_arquivo: str) -> OrchestratorConfig:
    """Carrega configuração de um arquivo."""
    # TODO: Implementar carregamento de arquivo YAML/JSON
    logger.info(f"Carregando configuração de: {caminho_arquivo}")
    return obter_config()


def salvar_config_para_arquivo(config: OrchestratorConfig, caminho_arquivo: str):
    """Salva configuração em um arquivo."""
    # TODO: Implementar salvamento em arquivo YAML/JSON
    logger.info(f"Salvando configuração em: {caminho_arquivo}") 