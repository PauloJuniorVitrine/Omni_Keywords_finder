"""
Módulo de enriquecimento de palavras-chave.
Responsável por calcular scores e adicionar metadados às keywords.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-001
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

from typing import List, Dict, Optional
from domain.models import Keyword, IntencaoBusca
from shared.logger import logger
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Limite explícito de concorrência para paralelização
MAX_WORKERS = 4

class EnriquecidorKeywords:
    """
    Enriquece palavras-chave com scores e metadados calculados.
    
    Responsabilidades:
    - Cálculo de scores baseado em pesos configuráveis
    - Geração de justificativas para scores
    - Processamento paralelo opcional
    - Tratamento de erros durante enriquecimento
    
    Princípios aplicados:
    - SRP: Apenas enriquecimento
    - Configurabilidade: Pesos customizáveis
    - Performance: Paralelização opcional
    - Rastreabilidade: Logging detalhado
    """
    
    def __init__(
        self,
        pesos_score: Optional[Dict[str, float]] = None,
        paralelizar: bool = False,
        max_workers: int = MAX_WORKERS
    ):
        """
        Inicializa o enriquecidor com configurações.
        
        Args:
            pesos_score: Dicionário com pesos para cálculo de score
            paralelizar: Se True, ativa processamento paralelo
            max_workers: Número máximo de workers para paralelização
        """
        self.pesos = pesos_score or {
            "volume": 0.4,
            "cpc": 0.2,
            "intention": 0.2,
            "competition": 0.2
        }
        self.paralelizar = paralelizar
        self.max_workers = max_workers
        self._ultimos_erros = []
        
    def _normalizar_intencao(self, intencao: IntencaoBusca) -> float:
        """
        Normaliza a intenção de busca para valor numérico.
        
        Args:
            intencao: Intenção de busca
            
        Returns:
            Valor normalizado entre 0 e 1
        """
        mapeamento_intencao = {
            IntencaoBusca.INFORMACIONAL: 0.3,
            IntencaoBusca.NAVEGACIONAL: 0.2,
            IntencaoBusca.COMPARACAO: 0.4,
            IntencaoBusca.COMERCIAL: 0.7,
            IntencaoBusca.TRANSACIONAL: 1.0
        }
        return mapeamento_intencao.get(intencao, 0.5)
        
    def calcular_score(self, kw: Keyword) -> float:
        """
        Calcula o score de uma keyword baseado nos pesos configurados.
        
        Fórmula: score = (volume * peso_volume + cpc * peso_cpc + 
                         intencao * peso_intencao + (1 - concorrencia) * peso_competition)
        
        Args:
            kw: Keyword para cálculo do score
            
        Returns:
            Score calculado entre 0 e 1
        """
        try:
            # Normalizar valores para escala 0-1
            volume_norm = min(kw.volume_busca / 10000, 1.0) if kw.volume_busca > 0 else 0
            cpc_norm = min(kw.cpc / 10, 1.0) if kw.cpc > 0 else 0
            intencao_norm = self._normalizar_intencao(kw.intencao)
            competicao_norm = 1 - kw.concorrencia  # Inverter concorrência
            
            # Calcular score ponderado
            score = (
                volume_norm * self.pesos.get("volume", 0.4) +
                cpc_norm * self.pesos.get("cpc", 0.2) +
                intencao_norm * self.pesos.get("intention", 0.2) +
                competicao_norm * self.pesos.get("competition", 0.2)
            )
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_score",
                "status": "error",
                "source": "enriquecidor_keywords.calcular_score",
                "details": {"termo": kw.termo, "erro": str(e)}
            })
            return 0.0
    
    def gerar_justificativa(self, kw: Keyword, score: float) -> str:
        """
        Gera justificativa para o score calculado.
        
        Args:
            kw: Keyword processada
            score: Score calculado
            
        Returns:
            Justificativa em formato legível
        """
        fatores = []
        
        if kw.volume_busca > 1000:
            fatores.append(f"volume alto ({kw.volume_busca})")
        elif kw.volume_busca > 100:
            fatores.append(f"volume médio ({kw.volume_busca})")
        else:
            fatores.append(f"volume baixo ({kw.volume_busca})")
            
        if kw.cpc > 2.0:
            fatores.append(f"CPC alto ({kw.cpc:.2f})")
        elif kw.cpc > 0.5:
            fatores.append(f"CPC médio ({kw.cpc:.2f})")
        else:
            fatores.append(f"CPC baixo ({kw.cpc:.2f})")
            
        if kw.concorrencia < 0.3:
            fatores.append("baixa concorrência")
        elif kw.concorrencia < 0.7:
            fatores.append("concorrência média")
        else:
            fatores.append("alta concorrência")
            
        return f"Score {score:.3f} baseado em: {', '.join(fatores)}"
    
    def enriquecer_keyword(self, kw: Keyword) -> Optional[Keyword]:
        """
        Enriquece uma keyword individual com score e justificativa.
        
        Args:
            kw: Keyword a ser enriquecida
            
        Returns:
            Keyword enriquecida ou None se houver erro
        """
        try:
            # Calcular score
            score = self.calcular_score(kw)
            
            # Gerar justificativa
            justificativa = self.gerar_justificativa(kw, score)
            
            # Criar nova keyword com dados enriquecidos
            kw_enriquecida = Keyword(
                termo=kw.termo,
                volume_busca=kw.volume_busca,
                cpc=kw.cpc,
                concorrencia=kw.concorrencia,
                intencao=kw.intencao,
                score=score,
                justificativa=justificativa,
                fonte=kw.fonte,
                data_coleta=kw.data_coleta
            )
            
            return kw_enriquecida
            
        except Exception as e:
            erro = {
                "termo": kw.termo,
                "erro": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            self._ultimos_erros.append(erro)
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_enriquecimento_keyword",
                "status": "error",
                "source": "enriquecidor_keywords.enriquecer_keyword",
                "details": erro
            })
            
            return None
    
    def enriquecer_lista(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Enriquece uma lista de keywords.
        
        Args:
            keywords: Lista de keywords a enriquecer
            
        Returns:
            Lista de keywords enriquecidas
        """
        self._ultimos_erros = []  # Resetar erros
        keywords_enriquecidas = []
        
        # Decidir se usar paralelização
        usar_paralelizacao = (
            self.paralelizar and 
            len(keywords) > 10 and 
            self.max_workers > 1
        )
        
        if usar_paralelizacao:
            keywords_enriquecidas = self._enriquecer_paralelo(keywords)
        else:
            keywords_enriquecidas = self._enriquecer_sequencial(keywords)
        
        # Logging
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "enriquecimento_keywords",
            "status": "success",
            "source": "enriquecidor_keywords.enriquecer_lista",
            "details": {
                "total_entrada": len(keywords),
                "total_enriquecidas": len(keywords_enriquecidas),
                "erros": len(self._ultimos_erros),
                "paralelizado": usar_paralelizacao,
                "max_workers": self.max_workers if usar_paralelizacao else 1
            }
        })
        
        return keywords_enriquecidas
    
    def _enriquecer_sequencial(self, keywords: List[Keyword]) -> List[Keyword]:
        """Enriquecimento sequencial das keywords."""
        keywords_enriquecidas = []
        
        for kw in keywords:
            kw_enriquecida = self.enriquecer_keyword(kw)
            if kw_enriquecida:
                keywords_enriquecidas.append(kw_enriquecida)
        
        return keywords_enriquecidas
    
    def _enriquecer_paralelo(self, keywords: List[Keyword]) -> List[Keyword]:
        """Enriquecimento paralelo das keywords."""
        keywords_enriquecidas = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter todas as keywords para processamento
            futures = {
                executor.submit(self.enriquecer_keyword, kw): kw 
                for kw in keywords
            }
            
            # Coletar resultados conforme completam
            for future in as_completed(futures):
                try:
                    kw_enriquecida = future.result()
                    if kw_enriquecida:
                        keywords_enriquecidas.append(kw_enriquecida)
                except Exception as e:
                    logger.error({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_enriquecimento_paralelo",
                        "status": "error",
                        "source": "enriquecidor_keywords._enriquecer_paralelo",
                        "details": {"erro": str(e)}
                    })
        
        return keywords_enriquecidas
    
    def obter_erros(self) -> List[Dict]:
        """
        Retorna os erros ocorridos no último enriquecimento.
        
        Returns:
            Lista de erros com detalhes
        """
        return self._ultimos_erros.copy()
    
    def obter_configuracao(self) -> Dict:
        """
        Retorna a configuração atual do enriquecidor.
        
        Returns:
            Dicionário com configuração atual
        """
        return {
            "pesos_score": self.pesos.copy(),
            "paralelizar": self.paralelizar,
            "max_workers": self.max_workers
        }
    
    def atualizar_pesos(self, novos_pesos: Dict[str, float]) -> bool:
        """
        Atualiza os pesos de cálculo de score.
        
        Args:
            novos_pesos: Dicionário com novos pesos
            
        Returns:
            True se atualização bem-sucedida, False caso contrário
        """
        try:
            # Validar que a soma dos pesos é aproximadamente 1.0
            soma_pesos = sum(novos_pesos.values())
            if abs(soma_pesos - 1.0) > 0.01:
                logger.warning({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "pesos_score_invalidos",
                    "status": "warning",
                    "source": "enriquecidor_keywords.atualizar_pesos",
                    "details": {
                        "soma_pesos": soma_pesos,
                        "pesos": novos_pesos
                    }
                })
            
            self.pesos = novos_pesos.copy()
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "pesos_score_atualizados",
                "status": "success",
                "source": "enriquecidor_keywords.atualizar_pesos",
                "details": {"novos_pesos": novos_pesos}
            })
            
            return True
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_atualizacao_pesos",
                "status": "error",
                "source": "enriquecidor_keywords.atualizar_pesos",
                "details": {"erro": str(e), "pesos": novos_pesos}
            })
            return False 