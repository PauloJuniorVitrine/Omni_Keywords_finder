"""
Sistema de A/B Testing para Configurações de Cauda Longa

Tracing ID: LONGTAIL-011
Data/Hora: 2024-12-20 17:45:00 UTC
Versão: 1.0
Status: ✅ IMPLEMENTADO

Este módulo implementa um sistema completo de A/B Testing para otimizar
configurações de análise de cauda longa, permitindo testar diferentes
parâmetros e medir seu impacto na qualidade das keywords.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
from pathlib import Path
import random
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StatusExperimento(Enum):
    """Status do experimento A/B."""
    PLANEJADO = "planejado"
    EM_EXECUCAO = "em_execucao"
    CONCLUIDO = "concluido"
    PAUSADO = "pausado"
    CANCELADO = "cancelado"


class TipoSegmentacao(Enum):
    """Tipos de segmentação para A/B Testing."""
    ALEATORIA = "aleatoria"
    POR_NICHO = "por_nicho"
    POR_VOLUME = "por_volume"
    POR_CONCORRENCIA = "por_concorrencia"
    POR_COMPLEXIDADE = "por_complexidade"


@dataclass
class ConfiguracaoTeste:
    """Configuração de teste A/B."""
    
    # Identificação
    id: str
    nome: str
    descricao: str
    
    # Parâmetros de teste
    min_palavras: float
    min_caracteres: float
    max_concorrencia: float
    score_minimo: float
    threshold_complexidade: float
    peso_volume: float
    peso_cpc: float
    peso_concorrencia: float
    
    # Metadados
    criado_em: datetime = field(default_factory=datetime.now)
    criado_por: str = "sistema"
    versao: str = "1.0"
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        # Normalizar pesos
        total_pesos = self.peso_volume + self.peso_cpc + self.peso_concorrencia
        if total_pesos > 0:
            self.peso_volume /= total_pesos
            self.peso_cpc /= total_pesos
            self.peso_concorrencia /= total_pesos
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "min_palavras": self.min_palavras,
            "min_caracteres": self.min_caracteres,
            "max_concorrencia": self.max_concorrencia,
            "score_minimo": self.score_minimo,
            "threshold_complexidade": self.threshold_complexidade,
            "peso_volume": self.peso_volume,
            "peso_cpc": self.peso_cpc,
            "peso_concorrencia": self.peso_concorrencia,
            "criado_em": self.criado_em.isoformat(),
            "criado_por": self.criado_por,
            "versao": self.versao
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfiguracaoTeste':
        """Cria a partir de dicionário."""
        data_copy = data.copy()
        data_copy["criado_em"] = datetime.fromisoformat(data_copy["criado_em"])
        return cls(**data_copy)


@dataclass
class ExperimentoAB:
    """Experimento A/B Testing."""
    
    # Identificação
    id: str
    nome: str
    descricao: str
    
    # Configurações
    configuracao_a: ConfiguracaoTeste  # Controle
    configuracao_b: ConfiguracaoTeste  # Variante
    
    # Parâmetros do experimento
    tamanho_amostra: int
    duracao_dias: int
    tipo_segmentacao: TipoSegmentacao
    nivel_significancia: float = 0.05
    poder_estatistico: float = 0.8
    
    # Status e controle
    status: StatusExperimento = StatusExperimento.PLANEJADO
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    
    # Resultados
    metricas_a: Dict[str, float] = field(default_factory=dict)
    metricas_b: Dict[str, float] = field(default_factory=dict)
    resultado_teste: Optional[Dict[str, Any]] = None
    
    # Metadados
    criado_em: datetime = field(default_factory=datetime.now)
    criado_por: str = "sistema"
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "configuracao_a": self.configuracao_a.to_dict(),
            "configuracao_b": self.configuracao_b.to_dict(),
            "tamanho_amostra": self.tamanho_amostra,
            "duracao_dias": self.duracao_dias,
            "tipo_segmentacao": self.tipo_segmentacao.value,
            "nivel_significancia": self.nivel_significancia,
            "poder_estatistico": self.poder_estatistico,
            "status": self.status.value,
            "data_inicio": self.data_inicio.isoformat() if self.data_inicio else None,
            "data_fim": self.data_fim.isoformat() if self.data_fim else None,
            "metricas_a": self.metricas_a,
            "metricas_b": self.metricas_b,
            "resultado_teste": self.resultado_teste,
            "criado_em": self.criado_em.isoformat(),
            "criado_por": self.criado_por
        }


@dataclass
class ResultadoTeste:
    """Resultado de teste estatístico."""
    
    # Métricas principais
    diferenca_media: float
    erro_padrao: float
    intervalo_confianca: Tuple[float, float]
    valor_p: float
    estatistica_t: float
    
    # Interpretação
    significativo: bool
    direcao: str  # "melhoria", "piora", "neutro"
    tamanho_efeito: float
    
    # Recomendações
    recomendacao: str
    confianca: float
    
    # Metadados
    timestamp: datetime = field(default_factory=datetime.now)
    tracing_id: str = field(default_factory=lambda: f"AB_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}")


class SistemaABTestingCaudaLonga:
    """
    Sistema de A/B Testing para configurações de cauda longa.
    
    Este sistema permite testar diferentes configurações de parâmetros
    e medir seu impacto na qualidade das keywords de cauda longa.
    """
    
    def __init__(self, diretorio_dados: str = "infrastructure/ab_testing/dados"):
        """
        Inicializa o sistema de A/B Testing.
        
        Args:
            diretorio_dados: Diretório para armazenar dados dos experimentos
        """
        self.diretorio_dados = Path(diretorio_dados)
        self.diretorio_dados.mkdir(parents=True, exist_ok=True)
        
        self.experimentos: Dict[str, ExperimentoAB] = {}
        self.resultados: Dict[str, List[ResultadoTeste]] = {}
        self.dados_experimentos: Dict[str, pd.DataFrame] = {}
        
        # Carregar experimentos existentes
        self._carregar_experimentos()
        
        logger.info(f"[LONGTAIL-011] Sistema de A/B Testing inicializado - {datetime.now()}")
    
    def _carregar_experimentos(self):
        """Carrega experimentos salvos anteriormente."""
        try:
            arquivo_experimentos = self.diretorio_dados / "experimentos.json"
            
            if arquivo_experimentos.exists():
                with open(arquivo_experimentos, 'r') as f:
                    dados = json.load(f)
                
                for exp_data in dados:
                    experimento = self._criar_experimento_from_dict(exp_data)
                    self.experimentos[experimento.id] = experimento
                
                logger.info(f"[LONGTAIL-011] {len(self.experimentos)} experimentos carregados")
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao carregar experimentos: {str(e)}")
    
    def _criar_experimento_from_dict(self, data: Dict[str, Any]) -> ExperimentoAB:
        """Cria experimento a partir de dicionário."""
        config_a = ConfiguracaoTeste.from_dict(data["configuracao_a"])
        config_b = ConfiguracaoTeste.from_dict(data["configuracao_b"])
        
        experimento = ExperimentoAB(
            id=data["id"],
            nome=data["nome"],
            descricao=data["descricao"],
            configuracao_a=config_a,
            configuracao_b=config_b,
            tamanho_amostra=data["tamanho_amostra"],
            duracao_dias=data["duracao_dias"],
            tipo_segmentacao=TipoSegmentacao(data["tipo_segmentacao"]),
            nivel_significancia=data["nivel_significancia"],
            poder_estatistico=data["poder_estatistico"],
            status=StatusExperimento(data["status"]),
            criado_em=datetime.fromisoformat(data["criado_em"]),
            criado_por=data["criado_por"]
        )
        
        # Carregar dados opcionais
        if data.get("data_inicio"):
            experimento.data_inicio = datetime.fromisoformat(data["data_inicio"])
        if data.get("data_fim"):
            experimento.data_fim = datetime.fromisoformat(data["data_fim"])
        
        experimento.metricas_a = data.get("metricas_a", {})
        experimento.metricas_b = data.get("metricas_b", {})
        experimento.resultado_teste = data.get("resultado_teste")
        
        return experimento
    
    def _salvar_experimentos(self):
        """Salva experimentos em arquivo."""
        try:
            arquivo_experimentos = self.diretorio_dados / "experimentos.json"
            
            dados = [exp.to_dict() for exp in self.experimentos.values()]
            
            with open(arquivo_experimentos, 'w') as f:
                json.dump(dados, f, indent=2)
            
            logger.info(f"[LONGTAIL-011] {len(dados)} experimentos salvos")
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao salvar experimentos: {str(e)}")
    
    def criar_experimento(
        self,
        nome: str,
        descricao: str,
        configuracao_a: Dict[str, float],
        configuracao_b: Dict[str, float],
        tamanho_amostra: int = 1000,
        duracao_dias: int = 7,
        tipo_segmentacao: TipoSegmentacao = TipoSegmentacao.ALEATORIA,
        nivel_significancia: float = 0.05,
        poder_estatistico: float = 0.8
    ) -> ExperimentoAB:
        """
        Cria um novo experimento A/B.
        
        Args:
            nome: Nome do experimento
            descricao: Descrição do experimento
            configuracao_a: Configuração de controle
            configuracao_b: Configuração de variante
            tamanho_amostra: Tamanho da amostra
            duracao_dias: Duração em dias
            tipo_segmentacao: Tipo de segmentação
            nivel_significancia: Nível de significância
            poder_estatistico: Poder estatístico
            
        Returns:
            Experimento criado
        """
        try:
            # Criar configurações
            config_a = ConfiguracaoTeste(
                id=f"config_a_{uuid.uuid4().hex[:8]}",
                nome=f"{nome} - Controle",
                descricao="Configuração de controle",
                **configuracao_a
            )
            
            config_b = ConfiguracaoTeste(
                id=f"config_b_{uuid.uuid4().hex[:8]}",
                nome=f"{nome} - Variante",
                descricao="Configuração de variante",
                **configuracao_b
            )
            
            # Criar experimento
            experimento = ExperimentoAB(
                id=str(uuid.uuid4()),
                nome=nome,
                descricao=descricao,
                configuracao_a=config_a,
                configuracao_b=config_b,
                tamanho_amostra=tamanho_amostra,
                duracao_dias=duracao_dias,
                tipo_segmentacao=tipo_segmentacao,
                nivel_significancia=nivel_significancia,
                poder_estatistico=poder_estatistico
            )
            
            # Salvar experimento
            self.experimentos[experimento.id] = experimento
            self._salvar_experimentos()
            
            logger.info(f"[LONGTAIL-011] Experimento criado: {experimento.id} - {nome}")
            return experimento
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao criar experimento: {str(e)}")
            raise
    
    def iniciar_experimento(self, experimento_id: str) -> bool:
        """
        Inicia um experimento.
        
        Args:
            experimento_id: ID do experimento
            
        Returns:
            True se iniciado com sucesso
        """
        try:
            if experimento_id not in self.experimentos:
                logger.error(f"[LONGTAIL-011] Experimento não encontrado: {experimento_id}")
                return False
            
            experimento = self.experimentos[experimento_id]
            
            if experimento.status != StatusExperimento.PLANEJADO:
                logger.warning(f"[LONGTAIL-011] Experimento não pode ser iniciado: {experimento.status}")
                return False
            
            # Atualizar status
            experimento.status = StatusExperimento.EM_EXECUCAO
            experimento.data_inicio = datetime.now()
            
            # Salvar alterações
            self._salvar_experimentos()
            
            logger.info(f"[LONGTAIL-011] Experimento iniciado: {experimento_id}")
            return True
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao iniciar experimento: {str(e)}")
            return False
    
    def pausar_experimento(self, experimento_id: str) -> bool:
        """
        Pausa um experimento.
        
        Args:
            experimento_id: ID do experimento
            
        Returns:
            True se pausado com sucesso
        """
        try:
            if experimento_id not in self.experimentos:
                return False
            
            experimento = self.experimentos[experimento_id]
            
            if experimento.status != StatusExperimento.EM_EXECUCAO:
                return False
            
            experimento.status = StatusExperimento.PAUSADO
            self._salvar_experimentos()
            
            logger.info(f"[LONGTAIL-011] Experimento pausado: {experimento_id}")
            return True
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao pausar experimento: {str(e)}")
            return False
    
    def cancelar_experimento(self, experimento_id: str) -> bool:
        """
        Cancela um experimento.
        
        Args:
            experimento_id: ID do experimento
            
        Returns:
            True se cancelado com sucesso
        """
        try:
            if experimento_id not in self.experimentos:
                return False
            
            experimento = self.experimentos[experimento_id]
            experimento.status = StatusExperimento.CANCELADO
            experimento.data_fim = datetime.now()
            
            self._salvar_experimentos()
            
            logger.info(f"[LONGTAIL-011] Experimento cancelado: {experimento_id}")
            return True
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao cancelar experimento: {str(e)}")
            return False
    
    def segmentar_keywords(
        self,
        keywords: List[Dict[str, Any]],
        experimento_id: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Segmenta keywords para grupos A e B.
        
        Args:
            keywords: Lista de keywords
            experimento_id: ID do experimento
            
        Returns:
            Tuple com grupos A e B
        """
        try:
            if experimento_id not in self.experimentos:
                raise ValueError(f"Experimento não encontrado: {experimento_id}")
            
            experimento = self.experimentos[experimento_id]
            
            if experimento.status != StatusExperimento.EM_EXECUCAO:
                raise ValueError(f"Experimento não está em execução: {experimento.status}")
            
            # Converter para DataFrame
            df = pd.DataFrame(keywords)
            
            # Aplicar segmentação baseada no tipo
            if experimento.tipo_segmentacao == TipoSegmentacao.ALEATORIA:
                # Segmentação aleatória
                df['grupo'] = np.random.choice(['A', 'B'], size=len(df), p=[0.5, 0.5])
            
            elif experimento.tipo_segmentacao == TipoSegmentacao.POR_NICHO:
                # Segmentação por nicho (simulada)
                df['grupo'] = np.random.choice(['A', 'B'], size=len(df), p=[0.5, 0.5])
            
            elif experimento.tipo_segmentacao == TipoSegmentacao.POR_VOLUME:
                # Segmentação por volume de busca
                df['grupo'] = np.where(df['volume_busca'] > df['volume_busca'].median(), 'A', 'B')
            
            elif experimento.tipo_segmentacao == TipoSegmentacao.POR_CONCORRENCIA:
                # Segmentação por concorrência
                df['grupo'] = np.where(df['concorrencia'] > df['concorrencia'].median(), 'A', 'B')
            
            elif experimento.tipo_segmentacao == TipoSegmentacao.POR_COMPLEXIDADE:
                # Segmentação por complexidade (número de palavras)
                df['complexidade'] = df['termo'].str.split().str.len()
                df['grupo'] = np.where(df['complexidade'] > df['complexidade'].median(), 'A', 'B')
            
            # Separar grupos
            grupo_a = df[df['grupo'] == 'A'].to_dict('records')
            grupo_b = df[df['grupo'] == 'B'].to_dict('records')
            
            # Limitar tamanho da amostra
            tamanho_por_grupo = experimento.tamanho_amostra // 2
            grupo_a = grupo_a[:tamanho_por_grupo]
            grupo_b = grupo_b[:tamanho_por_grupo]
            
            logger.info(f"[LONGTAIL-011] Keywords segmentadas - A: {len(grupo_a)}, B: {len(grupo_b)}")
            return grupo_a, grupo_b
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro na segmentação: {str(e)}")
            return [], []
    
    def aplicar_configuracao(
        self,
        keywords: List[Dict[str, Any]],
        configuracao: ConfiguracaoTeste
    ) -> List[Dict[str, Any]]:
        """
        Aplica configuração a um grupo de keywords.
        
        Args:
            keywords: Lista de keywords
            configuracao: Configuração a ser aplicada
            
        Returns:
            Keywords com configuração aplicada
        """
        try:
            resultados = []
            
            for keyword in keywords:
                # Aplicar filtros da configuração
                palavras = len(keyword['termo'].split())
                caracteres = len(keyword['termo'])
                concorrencia = keyword.get('concorrencia', 0.5)
                
                # Verificar critérios
                if (palavras >= configuracao.min_palavras and
                    caracteres >= configuracao.min_caracteres and
                    concorrencia <= configuracao.max_concorrencia):
                    
                    # Calcular score com pesos da configuração
                    volume = keyword.get('volume_busca', 0)
                    cpc = keyword.get('cpc', 0)
                    
                    score = (
                        volume * configuracao.peso_volume +
                        cpc * configuracao.peso_cpc +
                        (1 - concorrencia) * configuracao.peso_concorrencia
                    )
                    
                    # Aplicar threshold
                    if score >= configuracao.score_minimo:
                        keyword['score_calculado'] = score
                        keyword['configuracao_aplicada'] = configuracao.id
                        resultados.append(keyword)
            
            logger.info(f"[LONGTAIL-011] Configuração aplicada - {len(resultados)} keywords aprovadas")
            return resultados
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao aplicar configuração: {str(e)}")
            return []
    
    def coletar_metricas(
        self,
        keywords: List[Dict[str, Any]],
        grupo: str
    ) -> Dict[str, float]:
        """
        Coleta métricas de um grupo de keywords.
        
        Args:
            keywords: Lista de keywords
            grupo: Identificador do grupo (A ou B)
            
        Returns:
            Dicionário com métricas
        """
        try:
            if not keywords:
                return {}
            
            df = pd.DataFrame(keywords)
            
            metricas = {
                'total_keywords': len(keywords),
                'media_score': df['score_calculado'].mean() if 'score_calculado' in df.columns else 0,
                'media_volume': df['volume_busca'].mean() if 'volume_busca' in df.columns else 0,
                'media_cpc': df['cpc'].mean() if 'cpc' in df.columns else 0,
                'media_concorrencia': df['concorrencia'].mean() if 'concorrencia' in df.columns else 0,
                'taxa_aprovacao': len(keywords) / len(keywords) if keywords else 0,
                'desvio_padrao_score': df['score_calculado'].std() if 'score_calculado' in df.columns else 0,
                'mediana_score': df['score_calculado'].median() if 'score_calculado' in df.columns else 0
            }
            
            logger.info(f"[LONGTAIL-011] Métricas coletadas para grupo {grupo}: {len(metricas)} métricas")
            return metricas
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao coletar métricas: {str(e)}")
            return {}
    
    def executar_teste_estatistico(
        self,
        metricas_a: Dict[str, float],
        metricas_b: Dict[str, float],
        dados_a: List[Dict[str, Any]],
        dados_b: List[Dict[str, Any]],
        nivel_significancia: float = 0.05
    ) -> ResultadoTeste:
        """
        Executa teste estatístico entre grupos A e B.
        
        Args:
            metricas_a: Métricas do grupo A
            metricas_b: Métricas do grupo B
            dados_a: Dados brutos do grupo A
            dados_b: Dados brutos do grupo B
            nivel_significancia: Nível de significância
            
        Returns:
            Resultado do teste estatístico
        """
        try:
            # Converter dados para arrays
            scores_a = [key.get('score_calculado', 0) for key in dados_a]
            scores_b = [key.get('score_calculado', 0) for key in dados_b]
            
            if not scores_a or not scores_b:
                raise ValueError("Dados insuficientes para teste estatístico")
            
            # Teste t de Student
            t_stat, p_value = stats.ttest_ind(scores_a, scores_b)
            
            # Calcular diferença média
            diferenca_media = np.mean(scores_b) - np.mean(scores_a)
            
            # Calcular erro padrão
            erro_padrao = np.sqrt(
                (np.var(scores_a, ddof=1) / len(scores_a)) +
                (np.var(scores_b, ddof=1) / len(scores_b))
            )
            
            # Intervalo de confiança (95%)
            intervalo_confianca = (
                diferenca_media - 1.96 * erro_padrao,
                diferenca_media + 1.96 * erro_padrao
            )
            
            # Determinar significância
            significativo = p_value < nivel_significancia
            
            # Determinar direção
            if abs(diferenca_media) < 0.01:
                direcao = "neutro"
            elif diferenca_media > 0:
                direcao = "melhoria"
            else:
                direcao = "piora"
            
            # Calcular tamanho do efeito (Cohen'string_data data)
            pooled_std = np.sqrt(
                ((len(scores_a) - 1) * np.var(scores_a, ddof=1) +
                 (len(scores_b) - 1) * np.var(scores_b, ddof=1)) /
                (len(scores_a) + len(scores_b) - 2)
            )
            tamanho_efeito = diferenca_media / pooled_std if pooled_std > 0 else 0
            
            # Gerar recomendação
            if significativo:
                if direcao == "melhoria":
                    recomendacao = "Implementar variante B"
                    confianca = 1 - p_value
                elif direcao == "piora":
                    recomendacao = "Manter configuração A"
                    confianca = 1 - p_value
                else:
                    recomendacao = "Ambas configurações equivalentes"
                    confianca = 0.5
            else:
                recomendacao = "Teste inconclusivo - continuar experimento"
                confianca = 0.5
            
            resultado = ResultadoTeste(
                diferenca_media=diferenca_media,
                erro_padrao=erro_padrao,
                intervalo_confianca=intervalo_confianca,
                valor_p=p_value,
                estatistica_t=t_stat,
                significativo=significativo,
                direcao=direcao,
                tamanho_efeito=tamanho_efeito,
                recomendacao=recomendacao,
                confianca=confianca
            )
            
            logger.info(f"[LONGTAIL-011] Teste estatístico concluído - p-value: {p_value:.4f}, significativo: {significativo}")
            return resultado
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro no teste estatístico: {str(e)}")
            raise
    
    def processar_resultados_experimento(self, experimento_id: str) -> bool:
        """
        Processa resultados de um experimento.
        
        Args:
            experimento_id: ID do experimento
            
        Returns:
            True se processado com sucesso
        """
        try:
            if experimento_id not in self.experimentos:
                return False
            
            experimento = self.experimentos[experimento_id]
            
            if experimento.status != StatusExperimento.EM_EXECUCAO:
                return False
            
            # Verificar se experimento terminou
            if experimento.data_inicio:
                duracao_atual = (datetime.now() - experimento.data_inicio).days
                if duracao_atual < experimento.duracao_dias:
                    logger.info(f"[LONGTAIL-011] Experimento ainda em andamento: {duracao_atual}/{experimento.duracao_dias} dias")
                    return False
            
            # Carregar dados do experimento
            dados_a = self.dados_experimentos.get(f"{experimento_id}_A", [])
            dados_b = self.dados_experimentos.get(f"{experimento_id}_B", [])
            
            if not dados_a or not dados_b:
                logger.warning(f"[LONGTAIL-011] Dados insuficientes para processamento")
                return False
            
            # Coletar métricas
            metricas_a = self.coletar_metricas(dados_a, "A")
            metricas_b = self.coletar_metricas(dados_b, "B")
            
            # Executar teste estatístico
            resultado_teste = self.executar_teste_estatistico(
                metricas_a, metricas_b, dados_a, dados_b, experimento.nivel_significancia
            )
            
            # Atualizar experimento
            experimento.metricas_a = metricas_a
            experimento.metricas_b = metricas_b
            experimento.resultado_teste = resultado_teste.__dict__
            experimento.status = StatusExperimento.CONCLUIDO
            experimento.data_fim = datetime.now()
            
            # Salvar resultado
            if experimento_id not in self.resultados:
                self.resultados[experimento_id] = []
            self.resultados[experimento_id].append(resultado_teste)
            
            # Salvar alterações
            self._salvar_experimentos()
            self._salvar_resultados()
            
            logger.info(f"[LONGTAIL-011] Experimento processado: {experimento_id}")
            return True
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao processar resultados: {str(e)}")
            return False
    
    def _salvar_resultados(self):
        """Salva resultados dos experimentos."""
        try:
            arquivo_resultados = self.diretorio_dados / "resultados.json"
            
            dados_resultados = {}
            for exp_id, resultados in self.resultados.items():
                dados_resultados[exp_id] = [r.__dict__ for r in resultados]
            
            with open(arquivo_resultados, 'w') as f:
                json.dump(dados_resultados, f, indent=2, default=str)
            
            logger.info(f"[LONGTAIL-011] {len(dados_resultados)} conjuntos de resultados salvos")
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao salvar resultados: {str(e)}")
    
    def gerar_relatorio_experimento(self, experimento_id: str) -> Dict[str, Any]:
        """
        Gera relatório completo de um experimento.
        
        Args:
            experimento_id: ID do experimento
            
        Returns:
            Relatório do experimento
        """
        try:
            if experimento_id not in self.experimentos:
                return {"status": "erro", "mensagem": "Experimento não encontrado"}
            
            experimento = self.experimentos[experimento_id]
            
            relatorio = {
                "experimento": {
                    "id": experimento.id,
                    "nome": experimento.nome,
                    "descricao": experimento.descricao,
                    "status": experimento.status.value,
                    "data_inicio": experimento.data_inicio.isoformat() if experimento.data_inicio else None,
                    "data_fim": experimento.data_fim.isoformat() if experimento.data_fim else None,
                    "duracao_dias": experimento.duracao_dias,
                    "tamanho_amostra": experimento.tamanho_amostra,
                    "tipo_segmentacao": experimento.tipo_segmentacao.value
                },
                "configuracoes": {
                    "controle": experimento.configuracao_a.to_dict(),
                    "variante": experimento.configuracao_b.to_dict()
                },
                "metricas": {
                    "grupo_a": experimento.metricas_a,
                    "grupo_b": experimento.metricas_b
                },
                "resultado_teste": experimento.resultado_teste,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[LONGTAIL-011] Relatório gerado para experimento: {experimento_id}")
            return relatorio
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao gerar relatório: {str(e)}")
            return {"status": "erro", "mensagem": str(e)}
    
    def listar_experimentos(self, status: Optional[StatusExperimento] = None) -> List[Dict[str, Any]]:
        """
        Lista experimentos com filtro opcional por status.
        
        Args:
            status: Status para filtrar (opcional)
            
        Returns:
            Lista de experimentos
        """
        try:
            experimentos = []
            
            for exp in self.experimentos.values():
                if status is None or exp.status == status:
                    experimentos.append({
                        "id": exp.id,
                        "nome": exp.nome,
                        "status": exp.status.value,
                        "data_inicio": exp.data_inicio.isoformat() if exp.data_inicio else None,
                        "data_fim": exp.data_fim.isoformat() if exp.data_fim else None,
                        "tamanho_amostra": exp.tamanho_amostra,
                        "duracao_dias": exp.duracao_dias
                    })
            
            return experimentos
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao listar experimentos: {str(e)}")
            return []
    
    def calcular_tamanho_amostra(
        self,
        efeito_esperado: float,
        nivel_significancia: float = 0.05,
        poder_estatistico: float = 0.8
    ) -> int:
        """
        Calcula tamanho de amostra necessário.
        
        Args:
            efeito_esperado: Tamanho do efeito esperado
            nivel_significancia: Nível de significância
            poder_estatistico: Poder estatístico desejado
            
        Returns:
            Tamanho de amostra necessário
        """
        try:
            # Usar power analysis para calcular tamanho da amostra
            from scipy.stats import norm
            
            alpha = nivel_significancia
            beta = 1 - poder_estatistico
            
            z_alpha = norm.ppf(1 - alpha/2)
            z_beta = norm.ppf(1 - beta)
            
            # Fórmula para teste t de duas amostras
            tamanho_por_grupo = int(
                2 * ((z_alpha + z_beta) / efeito_esperado) ** 2
            )
            
            tamanho_total = tamanho_por_grupo * 2
            
            logger.info(f"[LONGTAIL-011] Tamanho de amostra calculado: {tamanho_total}")
            return tamanho_total
            
        except Exception as e:
            logger.error(f"[LONGTAIL-011] Erro ao calcular tamanho de amostra: {str(e)}")
            return 1000  # Valor padrão


# Função de conveniência para uso externo
def criar_sistema_ab_testing() -> SistemaABTestingCaudaLonga:
    """
    Cria e configura sistema de A/B Testing.
    
    Returns:
        Instância configurada do sistema
    """
    return SistemaABTestingCaudaLonga()


if __name__ == "__main__":
    # Teste básico do sistema
    sistema = criar_sistema_ab_testing()
    
    # Criar experimento de teste
    config_a = {
        "min_palavras": 3.0,
        "min_caracteres": 15.0,
        "max_concorrencia": 0.5,
        "score_minimo": 0.6,
        "threshold_complexidade": 0.7,
        "peso_volume": 0.4,
        "peso_cpc": 0.3,
        "peso_concorrencia": 0.3
    }
    
    config_b = {
        "min_palavras": 4.0,
        "min_caracteres": 18.0,
        "max_concorrencia": 0.4,
        "score_minimo": 0.7,
        "threshold_complexidade": 0.8,
        "peso_volume": 0.5,
        "peso_cpc": 0.2,
        "peso_concorrencia": 0.3
    }
    
    experimento = sistema.criar_experimento(
        nome="Teste Configuração Cauda Longa",
        descricao="Teste de configurações mais restritivas",
        configuracao_a=config_a,
        configuracao_b=config_b,
        tamanho_amostra=100,
        duracao_dias=3
    )
    
    print(f"Experimento criado: {experimento.id}")
    print(f"Status: {experimento.status.value}") 