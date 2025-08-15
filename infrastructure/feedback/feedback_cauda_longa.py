"""
Sistema de Feedback e Aprendizado - Cauda Longa

Tracing ID: LONGTAIL-013
Data/Hora: 2024-12-20 17:55:00 UTC
Versão: 1.0
Status: ✅ IMPLEMENTADO

Este módulo implementa um sistema completo de feedback e aprendizado
para análise de cauda longa, permitindo coleta, análise e aprendizado
contínuo baseado no feedback dos usuários.
"""

import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
import asyncio
from textblob import TextBlob
import re

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TipoFeedback(Enum):
    """Tipos de feedback."""
    QUALIDADE = "qualidade"
    RELEVANCIA = "relevancia"
    UTILIDADE = "utilidade"
    PERFORMANCE = "performance"
    USABILIDADE = "usabilidade"
    SUGESTAO = "sugestao"
    BUG = "bug"


class Sentimento(Enum):
    """Sentimentos do feedback."""
    POSITIVO = "positivo"
    NEUTRO = "neutro"
    NEGATIVO = "negativo"


@dataclass
class Feedback:
    """Definição de um feedback."""
    
    id: str
    tipo: TipoFeedback
    usuario_id: str
    keyword_id: Optional[str] = None
    configuracao_id: Optional[str] = None
    
    # Conteúdo do feedback
    titulo: str = ""
    descricao: str = ""
    nota: Optional[int] = None  # 1-10
    sentimento: Optional[Sentimento] = None
    
    # Metadados
    timestamp: datetime = field(default_factory=datetime.now)
    contexto: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Processamento
    processado: bool = False
    score_impacto: float = 0.0
    acoes_geradas: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        if not self.id:
            self.id = str(uuid.uuid4())
        
        # Análise automática de sentimento se não fornecido
        if not self.sentimento and self.descricao:
            self.sentimento = self._analisar_sentimento()
    
    def _analisar_sentimento(self) -> Sentimento:
        """Analisa sentimento do texto automaticamente."""
        try:
            # Palavras positivas e negativas em português
            palavras_positivas = {
                "bom", "ótimo", "excelente", "perfeito", "maravilhoso", "fantástico",
                "incrível", "espetacular", "funciona", "útil", "eficiente", "rápido",
                "preciso", "confiável", "satisfeito", "recomendo", "gosto", "adoro"
            }
            
            palavras_negativas = {
                "ruim", "péssimo", "terrível", "horrível", "lento", "ineficiente",
                "impreciso", "confuso", "difícil", "frustrante", "decepcionante",
                "não funciona", "problema", "erro", "bug", "insatisfeito", "odeio"
            }
            
            texto = self.descricao.lower()
            palavras = re.findall(r'\b\w+\b', texto)
            
            positivas = sum(1 for palavra in palavras if palavra in palavras_positivas)
            negativas = sum(1 for palavra in palavras if palavra in palavras_negativas)
            
            if positivas > negativas:
                return Sentimento.POSITIVO
            elif negativas > positivas:
                return Sentimento.NEGATIVO
            else:
                return Sentimento.NEUTRO
                
        except Exception:
            return Sentimento.NEUTRO
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "tipo": self.tipo.value,
            "usuario_id": self.usuario_id,
            "keyword_id": self.keyword_id,
            "configuracao_id": self.configuracao_id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "nota": self.nota,
            "sentimento": self.sentimento.value if self.sentimento else None,
            "timestamp": self.timestamp.isoformat(),
            "contexto": self.contexto,
            "tags": self.tags,
            "processado": self.processado,
            "score_impacto": self.score_impacto,
            "acoes_geradas": self.acoes_geradas
        }


@dataclass
class AcaoAprendizado:
    """Ação gerada a partir do feedback."""
    
    id: str
    tipo: str
    descricao: str
    prioridade: int  # 1-5 (5 = máxima)
    impacto_esperado: float
    feedback_origem: List[str] = field(default_factory=list)
    status: str = "pendente"  # pendente, em_execucao, concluida, cancelada
    criado_em: datetime = field(default_factory=datetime.now)
    concluido_em: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "prioridade": self.prioridade,
            "impacto_esperado": self.impacto_esperado,
            "feedback_origem": self.feedback_origem,
            "status": self.status,
            "criado_em": self.criado_em.isoformat(),
            "concluido_em": self.concluido_em.isoformat() if self.concluido_em else None
        }


class SistemaFeedbackCaudaLonga:
    """
    Sistema de feedback e aprendizado para cauda longa.
    
    Este sistema coleta, analisa e aprende com feedback dos usuários
    para melhorar continuamente a qualidade das keywords de cauda longa.
    """
    
    def __init__(self, diretorio_dados: str = "infrastructure/feedback/dados"):
        """
        Inicializa o sistema de feedback.
        
        Args:
            diretorio_dados: Diretório para armazenar dados de feedback
        """
        self.diretorio_dados = Path(diretorio_dados)
        self.diretorio_dados.mkdir(parents=True, exist_ok=True)
        
        # Dados do sistema
        self.feedbacks: List[Feedback] = []
        self.acoes: List[AcaoAprendizado] = []
        self.estatisticas: Dict[str, Any] = {}
        
        # Configurações
        self.auto_processamento = True
        self.threshold_impacto = 0.5
        self.max_acoes_pendentes = 50
        
        # Carregar dados existentes
        self._carregar_dados()
        
        logger.info(f"[LONGTAIL-013] Sistema de feedback inicializado - {datetime.now()}")
    
    def _carregar_dados(self):
        """Carrega dados salvos anteriormente."""
        try:
            # Carregar feedbacks
            arquivo_feedbacks = self.diretorio_dados / "feedbacks.json"
            if arquivo_feedbacks.exists():
                with open(arquivo_feedbacks, 'r') as f:
                    dados = json.load(f)
                
                for feedback_data in dados:
                    feedback = self._criar_feedback_from_dict(feedback_data)
                    self.feedbacks.append(feedback)
            
            # Carregar ações
            arquivo_acoes = self.diretorio_dados / "acoes.json"
            if arquivo_acoes.exists():
                with open(arquivo_acoes, 'r') as f:
                    dados = json.load(f)
                
                for acao_data in dados:
                    acao = self._criar_acao_from_dict(acao_data)
                    self.acoes.append(acao)
            
            logger.info(f"[LONGTAIL-013] Dados carregados: {len(self.feedbacks)} feedbacks, {len(self.acoes)} ações")
            
        except Exception as e:
            logger.error(f"[LONGTAIL-013] Erro ao carregar dados: {str(e)}")
    
    def _criar_feedback_from_dict(self, data: Dict[str, Any]) -> Feedback:
        """Cria feedback a partir de dicionário."""
        feedback = Feedback(
            id=data["id"],
            tipo=TipoFeedback(data["tipo"]),
            usuario_id=data["usuario_id"],
            keyword_id=data.get("keyword_id"),
            configuracao_id=data.get("configuracao_id"),
            titulo=data.get("titulo", ""),
            descricao=data.get("descricao", ""),
            nota=data.get("nota"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            contexto=data.get("contexto", {}),
            tags=data.get("tags", []),
            processado=data.get("processado", False),
            score_impacto=data.get("score_impacto", 0.0),
            acoes_geradas=data.get("acoes_geradas", [])
        )
        
        if data.get("sentimento"):
            feedback.sentimento = Sentimento(data["sentimento"])
        
        return feedback
    
    def _criar_acao_from_dict(self, data: Dict[str, Any]) -> AcaoAprendizado:
        """Cria ação a partir de dicionário."""
        acao = AcaoAprendizado(
            id=data["id"],
            tipo=data["tipo"],
            descricao=data["descricao"],
            prioridade=data["prioridade"],
            impacto_esperado=data["impacto_esperado"],
            feedback_origem=data.get("feedback_origem", []),
            status=data.get("status", "pendente"),
            criado_em=datetime.fromisoformat(data["criado_em"])
        )
        
        if data.get("concluido_em"):
            acao.concluido_em = datetime.fromisoformat(data["concluido_em"])
        
        return acao
    
    def _salvar_dados(self):
        """Salva dados do sistema."""
        try:
            # Salvar feedbacks
            arquivo_feedbacks = self.diretorio_dados / "feedbacks.json"
            feedbacks_dados = [f.to_dict() for f in self.feedbacks]
            
            with open(arquivo_feedbacks, 'w') as f:
                json.dump(feedbacks_dados, f, indent=2, default=str)
            
            # Salvar ações
            arquivo_acoes = self.diretorio_dados / "acoes.json"
            acoes_dados = [a.to_dict() for a in self.acoes]
            
            with open(arquivo_acoes, 'w') as f:
                json.dump(acoes_dados, f, indent=2, default=str)
            
            logger.info(f"[LONGTAIL-013] Dados salvos: {len(feedbacks_dados)} feedbacks, {len(acoes_dados)} ações")
            
        except Exception as e:
            logger.error(f"[LONGTAIL-013] Erro ao salvar dados: {str(e)}")
    
    def registrar_feedback(
        self,
        tipo: TipoFeedback,
        usuario_id: str,
        titulo: str = "",
        descricao: str = "",
        nota: Optional[int] = None,
        keyword_id: Optional[str] = None,
        configuracao_id: Optional[str] = None,
        contexto: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Feedback:
        """
        Registra um novo feedback.
        
        Args:
            tipo: Tipo do feedback
            usuario_id: ID do usuário
            titulo: Título do feedback
            descricao: Descrição detalhada
            nota: Nota de 1-10
            keyword_id: ID da keyword relacionada
            configuracao_id: ID da configuração relacionada
            contexto: Contexto adicional
            tags: Tags para categorização
            
        Returns:
            Feedback registrado
        """
        try:
            feedback = Feedback(
                id=str(uuid.uuid4()),
                tipo=tipo,
                usuario_id=usuario_id,
                keyword_id=keyword_id,
                configuracao_id=configuracao_id,
                titulo=titulo,
                descricao=descricao,
                nota=nota,
                contexto=contexto or {},
                tags=tags or []
            )
            
            self.feedbacks.append(feedback)
            
            # Processamento automático se habilitado
            if self.auto_processamento:
                self.processar_feedback(feedback)
            
            # Salvar dados
            self._salvar_dados()
            
            logger.info(f"[LONGTAIL-013] Feedback registrado: {feedback.id} - {tipo.value}")
            return feedback
            
        except Exception as e:
            logger.error(f"[LONGTAIL-013] Erro ao registrar feedback: {str(e)}")
            raise
    
    def processar_feedback(self, feedback: Feedback) -> List[AcaoAprendizado]:
        """
        Processa um feedback e gera ações de aprendizado.
        
        Args:
            feedback: Feedback a ser processado
            
        Returns:
            Lista de ações geradas
        """
        try:
            acoes_geradas = []
            
            # Calcular score de impacto
            score_impacto = self._calcular_score_impacto(feedback)
            feedback.score_impacto = score_impacto
            
            # Gerar ações baseadas no tipo e conteúdo
            if feedback.tipo == TipoFeedback.QUALIDADE:
                acoes = self._gerar_acoes_qualidade(feedback)
            elif feedback.tipo == TipoFeedback.RELEVANCIA:
                acoes = self._gerar_acoes_relevancia(feedback)
            elif feedback.tipo == TipoFeedback.PERFORMANCE:
                acoes = self._gerar_acoes_performance(feedback)
            elif feedback.tipo == TipoFeedback.BUG:
                acoes = self._gerar_acoes_bug(feedback)
            else:
                acoes = self._gerar_acoes_gerais(feedback)
            
            # Filtrar ações por impacto
            acoes_filtradas = [
                acao for acao in acoes
                if acao.impacto_esperado >= self.threshold_impacto
            ]
            
            # Adicionar ações ao sistema
            for acao in acoes_filtradas:
                self.acoes.append(acao)
                acoes_geradas.append(acao.id)
            
            # Atualizar feedback
            feedback.processado = True
            feedback.acoes_geradas = acoes_geradas
            
            # Limitar número de ações pendentes
            self._limpar_acoes_excedentes()
            
            logger.info(f"[LONGTAIL-013] Feedback processado: {len(acoes_geradas)} ações geradas")
            return acoes_filtradas
            
        except Exception as e:
            logger.error(f"[LONGTAIL-013] Erro ao processar feedback: {str(e)}")
            return []
    
    def _calcular_score_impacto(self, feedback: Feedback) -> float:
        """Calcula score de impacto do feedback."""
        score = 0.0
        
        # Base no tipo
        pesos_tipo = {
            TipoFeedback.BUG: 0.9,
            TipoFeedback.PERFORMANCE: 0.8,
            TipoFeedback.QUALIDADE: 0.7,
            TipoFeedback.RELEVANCIA: 0.6,
            TipoFeedback.UTILIDADE: 0.5,
            TipoFeedback.USABILIDADE: 0.4,
            TipoFeedback.SUGESTAO: 0.3
        }
        score += pesos_tipo.get(feedback.tipo, 0.5)
        
        # Base na nota
        if feedback.nota is not None:
            if feedback.nota <= 3:
                score += 0.3  # Feedback negativo tem mais impacto
            elif feedback.nota >= 8:
                score += 0.1  # Feedback positivo tem menos impacto
            else:
                score += 0.2
        
        # Base no sentimento
        if feedback.sentimento == Sentimento.NEGATIVO:
            score += 0.2
        elif feedback.sentimento == Sentimento.POSITIVO:
            score += 0.1
        
        # Base no tamanho da descrição
        if len(feedback.descricao) > 100:
            score += 0.1  # Feedback detalhado tem mais impacto
        
        return min(score, 1.0)
    
    def _gerar_acoes_qualidade(self, feedback: Feedback) -> List[AcaoAprendizado]:
        """Gera ações para feedback de qualidade."""
        acoes = []
        
        if feedback.sentimento == Sentimento.NEGATIVO:
            acoes.append(AcaoAprendizado(
                id=str(uuid.uuid4()),
                tipo="revisar_criterios_qualidade",
                descricao=f"Revisar critérios de qualidade baseado no feedback: {feedback.titulo}",
                prioridade=4,
                impacto_esperado=0.7,
                feedback_origem=[feedback.id]
            ))
        
        if "precisão" in feedback.descricao.lower():
            acoes.append(AcaoAprendizado(
                id=str(uuid.uuid4()),
                tipo="melhorar_algoritmo_precisao",
                descricao="Melhorar algoritmo de precisão de keywords",
                prioridade=3,
                impacto_esperado=0.6,
                feedback_origem=[feedback.id]
            ))
        
        return acoes
    
    def _gerar_acoes_relevancia(self, feedback: Feedback) -> List[AcaoAprendizado]:
        """Gera ações para feedback de relevância."""
        acoes = []
        
        if feedback.sentimento == Sentimento.NEGATIVO:
            acoes.append(AcaoAprendizado(
                id=str(uuid.uuid4()),
                tipo="ajustar_filtros_relevancia",
                descricao=f"Ajustar filtros de relevância baseado no feedback: {feedback.titulo}",
                prioridade=3,
                impacto_esperado=0.6,
                feedback_origem=[feedback.id]
            ))
        
        return acoes
    
    def _gerar_acoes_performance(self, feedback: Feedback) -> List[AcaoAprendizado]:
        """Gera ações para feedback de performance."""
        acoes = []
        
        if "lento" in feedback.descricao.lower() or "demora" in feedback.descricao.lower():
            acoes.append(AcaoAprendizado(
                id=str(uuid.uuid4()),
                tipo="otimizar_performance_processamento",
                descricao="Otimizar performance do processamento de keywords",
                prioridade=4,
                impacto_esperado=0.8,
                feedback_origem=[feedback.id]
            ))
        
        if "memória" in feedback.descricao.lower() or "ram" in feedback.descricao.lower():
            acoes.append(AcaoAprendizado(
                id=str(uuid.uuid4()),
                tipo="otimizar_uso_memoria",
                descricao="Otimizar uso de memória no processamento",
                prioridade=3,
                impacto_esperado=0.6,
                feedback_origem=[feedback.id]
            ))
        
        return acoes
    
    def _gerar_acoes_bug(self, feedback: Feedback) -> List[AcaoAprendizado]:
        """Gera ações para feedback de bug."""
        acoes = []
        
        acoes.append(AcaoAprendizado(
            id=str(uuid.uuid4()),
            tipo="investigar_bug",
            descricao=f"Investigar bug reportado: {feedback.titulo}",
            prioridade=5,
            impacto_esperado=0.9,
            feedback_origem=[feedback.id]
        ))
        
        return acoes
    
    def _gerar_acoes_gerais(self, feedback: Feedback) -> List[AcaoAprendizado]:
        """Gera ações gerais para outros tipos de feedback."""
        acoes = []
        
        if feedback.sentimento == Sentimento.NEGATIVO:
            acoes.append(AcaoAprendizado(
                id=str(uuid.uuid4()),
                tipo="analisar_feedback_negativo",
                descricao=f"Analisar feedback negativo: {feedback.titulo}",
                prioridade=2,
                impacto_esperado=0.4,
                feedback_origem=[feedback.id]
            ))
        
        return acoes
    
    def _limpar_acoes_excedentes(self):
        """Remove ações excedentes baseado no limite."""
        acoes_pendentes = [a for a in self.acoes if a.status == "pendente"]
        
        if len(acoes_pendentes) > self.max_acoes_pendentes:
            # Ordenar por prioridade e impacto
            acoes_pendentes.sort(key=lambda value: (value.prioridade, value.impacto_esperado), reverse=True)
            
            # Manter apenas as mais importantes
            acoes_manter = acoes_pendentes[:self.max_acoes_pendentes]
            acoes_remover = acoes_pendentes[self.max_acoes_pendentes:]
            
            # Marcar como canceladas
            for acao in acoes_remover:
                acao.status = "cancelada"
            
            logger.info(f"[LONGTAIL-013] {len(acoes_remover)} ações canceladas por limite excedido")
    
    def obter_estatisticas_feedback(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Obtém estatísticas de feedback.
        
        Args:
            periodo_dias: Período em dias para análise
            
        Returns:
            Estatísticas de feedback
        """
        try:
            fim = datetime.now()
            inicio = fim - timedelta(days=periodo_dias)
            
            # Filtrar feedbacks do período
            feedbacks_periodo = [
                f for f in self.feedbacks
                if inicio <= f.timestamp <= fim
            ]
            
            if not feedbacks_periodo:
                return {"mensagem": "Nenhum feedback no período"}
            
            # Estatísticas por tipo
            tipos_count = defaultdict(int)
            sentimentos_count = defaultdict(int)
            notas = []
            
            for feedback in feedbacks_periodo:
                tipos_count[feedback.tipo.value] += 1
                if feedback.sentimento:
                    sentimentos_count[feedback.sentimento.value] += 1
                if feedback.nota:
                    notas.append(feedback.nota)
            
            # Calcular métricas
            estatisticas = {
                "periodo": {
                    "inicio": inicio.isoformat(),
                    "fim": fim.isoformat(),
                    "dias": periodo_dias
                },
                "total_feedbacks": len(feedbacks_periodo),
                "tipos": dict(tipos_count),
                "sentimentos": dict(sentimentos_count),
                "nota_media": np.mean(notas) if notas else 0,
                "nota_mediana": np.median(notas) if notas else 0,
                "feedbacks_processados": len([f for f in feedbacks_periodo if f.processado]),
                "acoes_geradas": len([f for f in feedbacks_periodo if f.acoes_geradas]),
                "score_impacto_medio": np.mean([f.score_impacto for f in feedbacks_periodo])
            }
            
            return estatisticas
            
        except Exception as e:
            logger.error(f"[LONGTAIL-013] Erro ao calcular estatísticas: {str(e)}")
            return {"erro": str(e)}
    
    def obter_acoes_pendentes(self, prioridade_minima: int = 1) -> List[AcaoAprendizado]:
        """
        Obtém ações pendentes ordenadas por prioridade.
        
        Args:
            prioridade_minima: Prioridade mínima para incluir
            
        Returns:
            Lista de ações pendentes
        """
        acoes_pendentes = [
            a for a in self.acoes
            if a.status == "pendente" and a.prioridade >= prioridade_minima
        ]
        
        # Ordenar por prioridade e impacto
        acoes_pendentes.sort(key=lambda value: (value.prioridade, value.impacto_esperado), reverse=True)
        
        return acoes_pendentes
    
    def marcar_acao_concluida(self, acao_id: str) -> bool:
        """
        Marca uma ação como concluída.
        
        Args:
            acao_id: ID da ação
            
        Returns:
            True se marcada com sucesso
        """
        try:
            acao = next((a for a in self.acoes if a.id == acao_id), None)
            
            if not acao:
                return False
            
            acao.status = "concluida"
            acao.concluido_em = datetime.now()
            
            self._salvar_dados()
            
            logger.info(f"[LONGTAIL-013] Ação concluída: {acao_id}")
            return True
            
        except Exception as e:
            logger.error(f"[LONGTAIL-013] Erro ao marcar ação como concluída: {str(e)}")
            return False
    
    def gerar_relatorio_aprendizado(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Gera relatório de aprendizado baseado no feedback.
        
        Args:
            periodo_dias: Período em dias para análise
            
        Returns:
            Relatório de aprendizado
        """
        try:
            fim = datetime.now()
            inicio = fim - timedelta(days=periodo_dias)
            
            # Feedbacks do período
            feedbacks_periodo = [
                f for f in self.feedbacks
                if inicio <= f.timestamp <= fim
            ]
            
            # Ações do período
            acoes_periodo = [
                a for a in self.acoes
                if inicio <= a.criado_em <= fim
            ]
            
            relatorio = {
                "periodo": {
                    "inicio": inicio.isoformat(),
                    "fim": fim.isoformat(),
                    "dias": periodo_dias
                },
                "resumo": {
                    "total_feedbacks": len(feedbacks_periodo),
                    "total_acoes": len(acoes_periodo),
                    "acoes_concluidas": len([a for a in acoes_periodo if a.status == "concluida"]),
                    "acoes_pendentes": len([a for a in acoes_periodo if a.status == "pendente"])
                },
                "insights": self._gerar_insights(feedbacks_periodo),
                "recomendacoes": self._gerar_recomendacoes(feedbacks_periodo, acoes_periodo),
                "tendencias": self._analisar_tendencias(feedbacks_periodo)
            }
            
            return relatorio
            
        except Exception as e:
            logger.error(f"[LONGTAIL-013] Erro ao gerar relatório: {str(e)}")
            return {"erro": str(e)}
    
    def _gerar_insights(self, feedbacks: List[Feedback]) -> List[str]:
        """Gera insights baseados nos feedbacks."""
        insights = []
        
        if not feedbacks:
            return ["Nenhum feedback disponível para análise"]
        
        # Análise de sentimento
        sentimentos = [f.sentimento for f in feedbacks if f.sentimento]
        if sentimentos:
            positivo_pct = len([string_data for string_data in sentimentos if string_data == Sentimento.POSITIVO]) / len(sentimentos) * 100
            if positivo_pct > 70:
                insights.append(f"Alta satisfação dos usuários: {positivo_pct:.1f}% feedbacks positivos")
            elif positivo_pct < 30:
                insights.append(f"Baixa satisfação dos usuários: {positivo_pct:.1f}% feedbacks positivos")
        
        # Análise de tipos mais comuns
        tipos = [f.tipo for f in feedbacks]
        tipo_mais_comum = max(set(tipos), key=tipos.count) if tipos else None
        if tipo_mais_comum:
            insights.append(f"Tipo de feedback mais comum: {tipo_mais_comum.value}")
        
        # Análise de notas
        notas = [f.nota for f in feedbacks if f.nota is not None]
        if notas:
            nota_media = np.mean(notas)
            if nota_media >= 8:
                insights.append("Notas altas indicam boa qualidade geral")
            elif nota_media <= 5:
                insights.append("Notas baixas indicam necessidade de melhorias")
        
        return insights
    
    def _gerar_recomendacoes(self, feedbacks: List[Feedback], acoes: List[AcaoAprendizado]) -> List[str]:
        """Gera recomendações baseadas nos dados."""
        recomendacoes = []
        
        # Análise de feedbacks negativos
        feedbacks_negativos = [f for f in feedbacks if f.sentimento == Sentimento.NEGATIVO]
        if len(feedbacks_negativos) > len(feedbacks) * 0.3:
            recomendacoes.append("Alto volume de feedbacks negativos - priorizar melhorias")
        
        # Análise de tipos de feedback
        tipos_count = defaultdict(int)
        for f in feedbacks:
            tipos_count[f.tipo] += 1
        
        tipo_mais_problema = max(tipos_count.items(), key=lambda value: value[1])[0] if tipos_count else None
        if tipo_mais_problema:
            recomendacoes.append(f"Focar melhorias em: {tipo_mais_problema.value}")
        
        # Análise de ações pendentes
        acoes_pendentes = [a for a in acoes if a.status == "pendente"]
        if len(acoes_pendentes) > 10:
            recomendacoes.append("Muitas ações pendentes - revisar prioridades")
        
        return recomendacoes
    
    def _analisar_tendencias(self, feedbacks: List[Feedback]) -> Dict[str, Any]:
        """Analisa tendências nos feedbacks."""
        if not feedbacks:
            return {}
        
        # Agrupar por dia
        feedbacks_por_dia = defaultdict(list)
        for f in feedbacks:
            dia = f.timestamp.date()
            feedbacks_por_dia[dia].append(f)
        
        # Calcular tendências
        dias = sorted(feedbacks_por_dia.keys())
        volumes = [len(feedbacks_por_dia[dia]) for dia in dias]
        
        if len(volumes) >= 2:
            tendencia_volume = "crescente" if volumes[-1] > volumes[0] else "decrescente"
        else:
            tendencia_volume = "estavel"
        
        return {
            "tendencia_volume": tendencia_volume,
            "dias_analisados": len(dias),
            "volume_medio_diario": np.mean(volumes) if volumes else 0
        }


# Função de conveniência para uso externo
def criar_sistema_feedback() -> SistemaFeedbackCaudaLonga:
    """
    Cria e configura sistema de feedback.
    
    Returns:
        Instância configurada do sistema
    """
    return SistemaFeedbackCaudaLonga()


if __name__ == "__main__":
    # Teste básico do sistema
    sistema = criar_sistema_feedback()
    
    # Registrar alguns feedbacks de teste
    sistema.registrar_feedback(
        tipo=TipoFeedback.QUALIDADE,
        usuario_id="user_001",
        titulo="Keywords muito boas",
        descricao="As keywords geradas estão muito precisas e relevantes",
        nota=9,
        sentimento=Sentimento.POSITIVO
    )
    
    sistema.registrar_feedback(
        tipo=TipoFeedback.PERFORMANCE,
        usuario_id="user_002",
        titulo="Processamento lento",
        descricao="O sistema está muito lento para processar as keywords",
        nota=3,
        sentimento=Sentimento.NEGATIVO
    )
    
    # Gerar relatório
    relatorio = sistema.gerar_relatorio_aprendizado(periodo_dias=7)
    print(f"Relatório gerado: {len(relatorio.get('insights', []))} insights")
    
    # Listar ações pendentes
    acoes = sistema.obter_acoes_pendentes()
    print(f"Ações pendentes: {len(acoes)}") 