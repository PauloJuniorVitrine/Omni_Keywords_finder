"""
Módulo de processamento ML para palavras-chave.
Responsável por aplicar machine learning adaptativo nas keywords.
"""
from typing import List, Dict, Optional, Any
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime
from infrastructure.ml.ml_adaptativo import MLAdaptativo

class MLProcessor:
    """
    Processa keywords usando machine learning adaptativo.
    
    Responsabilidades:
    - Integração com MLAdaptativo
    - Sugestão de keywords baseada em histórico
    - Bloqueio de keywords repetidas
    - Treinamento incremental com feedback
    - Processamento de contexto ML
    
    Princípios aplicados:
    - SRP: Apenas processamento ML
    - Integração: Usa MLAdaptativo existente
    - Adaptabilidade: Treinamento incremental
    - Rastreabilidade: Logging detalhado
    """
    
    def __init__(
        self,
        ml_adaptativo: Optional[MLAdaptativo] = None,
        habilitar_sugestoes: bool = True,
        habilitar_bloqueio: bool = True,
        habilitar_treinamento: bool = True
    ):
        """
        Inicializa o processador ML.
        
        Args:
            ml_adaptativo: Instância do MLAdaptativo
            habilitar_sugestoes: Se True, ativa sugestões de keywords
            habilitar_bloqueio: Se True, ativa bloqueio de repetidas
            habilitar_treinamento: Se True, ativa treinamento incremental
        """
        self.ml_adaptativo = ml_adaptativo
        self.habilitar_sugestoes = habilitar_sugestoes
        self.habilitar_bloqueio = habilitar_bloqueio
        self.habilitar_treinamento = habilitar_treinamento
        self._ultimos_resultados = {}
        
    def processar_keywords(
        self,
        keywords: List[Keyword],
        historico_feedback: Optional[List[Dict]] = None,
        contexto: Optional[Dict[str, Any]] = None
    ) -> List[Keyword]:
        """
        Processa keywords usando ML adaptativo.
        
        Args:
            keywords: Lista de keywords a processar
            historico_feedback: Histórico de feedback para treinamento
            contexto: Contexto adicional para processamento
            
        Returns:
            Lista de keywords processadas
        """
        if not self.ml_adaptativo or not keywords:
            return keywords
            
        try:
            # Converter keywords para formato do ML
            keywords_dict = [self._keyword_to_dict(kw) for kw in keywords]
            
            # Treinamento incremental se habilitado
            if self.habilitar_treinamento and historico_feedback and self.ml_adaptativo:
                self._treinar_incremental(historico_feedback)
            
            # Aplicar sugestões se habilitado
            if self.habilitar_sugestoes and self.ml_adaptativo:
                keywords_dict = self._aplicar_sugestoes(keywords_dict, contexto)
            
            # Aplicar bloqueio se habilitado
            if self.habilitar_bloqueio and self.ml_adaptativo:
                keywords_dict = self._aplicar_bloqueio(keywords_dict, historico_feedback)
            
            # Converter de volta para objetos Keyword
            keywords_processadas = [self._dict_to_keyword(kw_dict) for kw_dict in keywords_dict]
            
            # Logging
            self._log_processamento(keywords, keywords_processadas, contexto)
            
            return keywords_processadas
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_processamento_ml",
                "status": "error",
                "source": "ml_processor.processar_keywords",
                "details": {"erro": str(e), "total_keywords": len(keywords)}
            })
            return keywords
    
    def _keyword_to_dict(self, kw: Keyword) -> Dict[str, Any]:
        """
        Converte Keyword para dicionário compatível com ML.
        
        Args:
            kw: Keyword a converter
            
        Returns:
            Dicionário com dados da keyword
        """
        return {
            "termo": kw.termo,
            "volume_busca": kw.volume_busca,
            "cpc": kw.cpc,
            "concorrencia": kw.concorrencia,
            "intencao": kw.intencao.value if hasattr(kw.intencao, 'value') else str(kw.intencao),
            "score": kw.score,
            "justificativa": kw.justificativa,
            "fonte": kw.fonte,
            "data_coleta": kw.data_coleta.isoformat() if kw.data_coleta else None
        }
    
    def _dict_to_keyword(self, kw_dict: Dict[str, Any]) -> Keyword:
        """
        Converte dicionário de volta para Keyword.
        
        Args:
            kw_dict: Dicionário com dados da keyword
            
        Returns:
            Objeto Keyword
        """
        from domain.models import IntencaoBusca
        
        # Mapear intenção de volta para enum
        intencao_str = kw_dict.get("intencao", "informacional")
        intencao = IntencaoBusca.INFORMACIONAL  # default
        for int_enum in IntencaoBusca:
            if int_enum.value == intencao_str or str(int_enum) == intencao_str:
                intencao = int_enum
                break
        
        # Processar data_coleta
        data_coleta_str = kw_dict.get("data_coleta")
        data_coleta = None
        if data_coleta_str:
            try:
                data_coleta = datetime.fromisoformat(data_coleta_str)
            except (ValueError, TypeError):
                data_coleta = datetime.utcnow()
        
        return Keyword(
            termo=kw_dict.get("termo", ""),
            volume_busca=kw_dict.get("volume_busca", 0),
            cpc=kw_dict.get("cpc", 0.0),
            concorrencia=kw_dict.get("concorrencia", 0.0),
            intencao=intencao,
            score=kw_dict.get("score", 0.0),
            justificativa=kw_dict.get("justificativa", ""),
            fonte=kw_dict.get("fonte", ""),
            data_coleta=data_coleta or datetime.utcnow()
        )
    
    def _treinar_incremental(self, historico_feedback: List[Dict]) -> None:
        """
        Treina o modelo incrementalmente com feedback.
        
        Args:
            historico_feedback: Lista de feedbacks para treinamento
        """
        if not self.ml_adaptativo:
            return
            
        try:
            self.ml_adaptativo.treinar_incremental(historico_feedback)
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "treinamento_ml_incremental",
                "status": "success",
                "source": "ml_processor._treinar_incremental",
                "details": {
                    "total_feedbacks": len(historico_feedback),
                    "versao_modelo": getattr(self.ml_adaptativo, 'versao', 'N/A')
                }
            })
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_treinamento_ml",
                "status": "error",
                "source": "ml_processor._treinar_incremental",
                "details": {"erro": str(e)}
            })
    
    def _aplicar_sugestoes(
        self,
        keywords_dict: List[Dict],
        contexto: Optional[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Aplica sugestões do modelo ML.
        
        Args:
            keywords_dict: Lista de keywords em formato dicionário
            contexto: Contexto adicional
            
        Returns:
            Lista de keywords com sugestões aplicadas
        """
        if not self.ml_adaptativo:
            return keywords_dict
            
        try:
            sugeridos = self.ml_adaptativo.sugerir(keywords_dict)
            
            self._ultimos_resultados["sugeridos"] = len(sugeridos)
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "sugestoes_ml_aplicadas",
                "status": "success",
                "source": "ml_processor._aplicar_sugestoes",
                "details": {
                    "total_entrada": len(keywords_dict),
                    "total_sugeridos": len(sugeridos)
                }
            })
            
            return sugeridos
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_sugestoes_ml",
                "status": "error",
                "source": "ml_processor._aplicar_sugestoes",
                "details": {"erro": str(e)}
            })
            return keywords_dict
    
    def _aplicar_bloqueio(
        self,
        keywords_dict: List[Dict],
        historico_feedback: Optional[List[Dict]]
    ) -> List[Dict]:
        """
        Aplica bloqueio de keywords repetidas.
        
        Args:
            keywords_dict: Lista de keywords em formato dicionário
            historico_feedback: Histórico para verificação de repetidas
            
        Returns:
            Lista de keywords com bloqueio aplicado
        """
        if not self.ml_adaptativo:
            return keywords_dict
            
        try:
            historico = historico_feedback or []
            filtrados = self.ml_adaptativo.bloquear_repetidos(keywords_dict, historico)
            
            self._ultimos_resultados["filtrados"] = len(filtrados)
            self._ultimos_resultados["bloqueados"] = len(keywords_dict) - len(filtrados)
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "bloqueio_ml_aplicado",
                "status": "success",
                "source": "ml_processor._aplicar_bloqueio",
                "details": {
                    "total_entrada": len(keywords_dict),
                    "total_filtrados": len(filtrados),
                    "total_bloqueados": len(keywords_dict) - len(filtrados)
                }
            })
            
            return filtrados
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_bloqueio_ml",
                "status": "error",
                "source": "ml_processor._aplicar_bloqueio",
                "details": {"erro": str(e)}
            })
            return keywords_dict
    
    def _log_processamento(
        self,
        keywords_originais: List[Keyword],
        keywords_processadas: List[Keyword],
        contexto: Optional[Dict[str, Any]]
    ) -> None:
        """
        Registra log detalhado do processamento ML.
        
        Args:
            keywords_originais: Keywords antes do processamento
            keywords_processadas: Keywords após processamento
            contexto: Contexto do processamento
        """
        relatorio_ml = {
            "total_entrada": len(keywords_originais),
            "total_saida": len(keywords_processadas),
            "sugestoes_habilitadas": self.habilitar_sugestoes,
            "bloqueio_habilitado": self.habilitar_bloqueio,
            "treinamento_habilitado": self.habilitar_treinamento,
            "versao_ml": getattr(self.ml_adaptativo, 'versao', 'N/A') if self.ml_adaptativo else 'N/A',
            "data_treinamento": getattr(self.ml_adaptativo, 'data_treinamento', 'N/A') if self.ml_adaptativo else 'N/A'
        }
        
        # Adicionar resultados específicos se disponíveis
        if self._ultimos_resultados:
            relatorio_ml.update(self._ultimos_resultados)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "processamento_ml_completo",
            "status": "success",
            "source": "ml_processor._log_processamento",
            "details": relatorio_ml
        })
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do processamento ML.
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            "ml_adaptativo_disponivel": self.ml_adaptativo is not None,
            "sugestoes_habilitadas": self.habilitar_sugestoes,
            "bloqueio_habilitado": self.habilitar_bloqueio,
            "treinamento_habilitado": self.habilitar_treinamento,
            "ultimos_resultados": self._ultimos_resultados.copy(),
            "versao_ml": getattr(self.ml_adaptativo, 'versao', 'N/A') if self.ml_adaptativo else 'N/A'
        }
    
    def atualizar_configuracao(
        self,
        habilitar_sugestoes: Optional[bool] = None,
        habilitar_bloqueio: Optional[bool] = None,
        habilitar_treinamento: Optional[bool] = None
    ) -> bool:
        """
        Atualiza configuração do processador ML.
        
        Args:
            habilitar_sugestoes: Nova configuração para sugestões
            habilitar_bloqueio: Nova configuração para bloqueio
            habilitar_treinamento: Nova configuração para treinamento
            
        Returns:
            True se atualização bem-sucedida
        """
        try:
            if habilitar_sugestoes is not None:
                self.habilitar_sugestoes = habilitar_sugestoes
            if habilitar_bloqueio is not None:
                self.habilitar_bloqueio = habilitar_bloqueio
            if habilitar_treinamento is not None:
                self.habilitar_treinamento = habilitar_treinamento
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "configuracao_ml_atualizada",
                "status": "success",
                "source": "ml_processor.atualizar_configuracao",
                "details": {
                    "sugestoes": self.habilitar_sugestoes,
                    "bloqueio": self.habilitar_bloqueio,
                    "treinamento": self.habilitar_treinamento
                }
            })
            
            return True
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_atualizacao_configuracao_ml",
                "status": "error",
                "source": "ml_processor.atualizar_configuracao",
                "details": {"erro": str(e)}
            })
            return False 