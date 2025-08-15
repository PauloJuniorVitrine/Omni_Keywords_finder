"""
Analisador Semântico Processor - Refatoração de Complexidade Ciclomática
IMP-001: Separação de responsabilidades do IntegradorCaudaLonga

Tracing ID: IMP001_ANALISADOR_001
Data: 2024-12-27
Versão: 1.0
Status: EM IMPLEMENTAÇÃO
"""

from typing import List, Dict, Any
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime
import time

from .analisador_semantico_cauda_longa import AnalisadorSemanticoCaudaLonga

class AnalisadorSemanticoProcessor:
    """
    Responsável por aplicar análise semântica nas keywords.
    
    Responsabilidades:
    - Processar análise semântica de keywords
    - Atualizar atributos semânticos
    - Registrar métricas de análise
    - Tratar erros de processamento
    """
    
    def __init__(self):
        """Inicializa o processador de análise semântica."""
        self.analisador = AnalisadorSemanticoCaudaLonga()
        self.tempo_analise = 0.0
    
    def processar(
        self, 
        keywords: List[Keyword], 
        config: Dict[str, Any]
    ) -> List[Keyword]:
        """
        Processa análise semântica das keywords.
        
        Args:
            keywords: Lista de keywords a analisar
            config: Configuração específica do nicho
            
        Returns:
            Lista de keywords com análise semântica aplicada
        """
        tempo_inicio = time.time()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_analise_semantica",
            "status": "info",
            "source": "AnalisadorSemanticoProcessor.processar",
            "details": {
                "total_keywords": len(keywords),
                "config_keys": list(config.keys())
            }
        })
        
        try:
            keywords_analisadas = []
            
            for kw in keywords:
                try:
                    # Aplicar análise semântica
                    analise = self.analisador.analisar_keyword(kw.termo)
                    
                    # Atualizar keyword com análise semântica
                    # Como o modelo Keyword não tem esses atributos, vamos armazenar em um dict
                    if not hasattr(kw, 'analise_semantica'):
                        kw.analise_semantica = {}
                    
                    kw.analise_semantica.update({
                        "palavras_significativas": len(analise.palavras_chave_especificas),
                        "densidade_semantica": analise.similaridade_semantica,
                        "especificidade": analise.especificidade,
                        "intencao_detectada": analise.intencao_detectada,
                        "score_qualidade_semantica": analise.score_qualidade_semantica
                    })
                    
                    keywords_analisadas.append(kw)
                    
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_analise_keyword_individual",
                        "status": "warning",
                        "source": "AnalisadorSemanticoProcessor.processar",
                        "details": {
                            "keyword": kw.termo,
                            "erro": str(e)
                        }
                    })
                    # Manter keyword original em caso de erro
                    keywords_analisadas.append(kw)
            
            # Registrar tempo
            self.tempo_analise = time.time() - tempo_inicio
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_semantica_concluida",
                "status": "success",
                "source": "AnalisadorSemanticoProcessor.processar",
                "details": {
                    "keywords_processadas": len(keywords_analisadas),
                    "tempo_analise": self.tempo_analise
                }
            })
            
            return keywords_analisadas
            
        except Exception as e:
            self.tempo_analise = time.time() - tempo_inicio
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_semantica",
                "status": "error",
                "source": "AnalisadorSemanticoProcessor.processar",
                "details": {
                    "erro": str(e),
                    "tempo_analise": self.tempo_analise
                }
            })
            
            # Retornar keywords originais em caso de erro
            return keywords
    
    def obter_tempo_analise(self) -> float:
        """Obtém tempo de análise semântica."""
        return self.tempo_analise 