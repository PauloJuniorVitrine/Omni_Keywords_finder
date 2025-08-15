"""
Configurador de Nicho - Refatoração de Complexidade Ciclomática
IMP-001: Separação de responsabilidades do IntegradorCaudaLonga

Tracing ID: IMP001_CONFIGURADOR_001
Data: 2024-12-27
Versão: 1.0
Status: EM IMPLEMENTAÇÃO
"""

from typing import Dict, Any, Optional
from shared.logger import logger
from datetime import datetime
import time

from .configuracao_adaptativa import ConfiguracaoAdaptativa

class ConfiguradorNicho:
    """
    Responsável por configurar parâmetros específicos do nicho.
    
    Responsabilidades:
    - Obter configurações adaptativas por nicho
    - Aplicar configurações específicas de idioma
    - Validar configurações obtidas
    - Registrar métricas de configuração
    """
    
    def __init__(self):
        """Inicializa o configurador de nicho."""
        self.configuracao_adaptativa = ConfiguracaoAdaptativa()
        self.tempo_configuracao = 0.0
    
    def configurar(
        self, 
        nicho: Optional[str], 
        idioma: str = "pt"
    ) -> Dict[str, Any]:
        """
        Configura parâmetros específicos do nicho.
        
        Args:
            nicho: Nicho específico para configuração
            idioma: Idioma para processamento
            
        Returns:
            Configuração específica do nicho
        """
        tempo_inicio = time.time()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_configuracao_nicho",
            "status": "info",
            "source": "ConfiguradorNicho.configurar",
            "details": {
                "nicho": nicho,
                "idioma": idioma
            }
        })
        
        try:
            # Obter configuração adaptativa
            if nicho:
                config_obj = self.configuracao_adaptativa.obter_configuracao(nicho)
                config = self._converter_configuracao_para_dict(config_obj)
            else:
                config = {}
            
            # Validar configuração
            config_validada = self._validar_configuracao(config)
            
            # Registrar tempo
            self.tempo_configuracao = time.time() - tempo_inicio
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "configuracao_nicho_concluida",
                "status": "success",
                "source": "ConfiguradorNicho.configurar",
                "details": {
                    "nicho": nicho,
                    "tempo_configuracao": self.tempo_configuracao,
                    "config_keys": list(config_validada.keys())
                }
            })
            
            return config_validada
            
        except Exception as e:
            self.tempo_configuracao = time.time() - tempo_inicio
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_configuracao_nicho",
                "status": "error",
                "source": "ConfiguradorNicho.configurar",
                "details": {
                    "nicho": nicho,
                    "erro": str(e),
                    "tempo_configuracao": self.tempo_configuracao
                }
            })
            
            # Retornar configuração padrão em caso de erro
            return self._obter_configuracao_padrao(idioma)
    
    def _validar_configuracao(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida configuração obtida.
        
        Args:
            config: Configuração a validar
            
        Returns:
            Configuração validada
        """
        # Configuração mínima obrigatória
        config_padrao = self._obter_configuracao_padrao("pt")
        
        # Mesclar com configuração obtida
        config_validada = config_padrao.copy()
        config_validada.update(config)
        
        # Validar campos obrigatórios
        campos_obrigatorios = [
            "volume_minimo",
            "cpc_minimo", 
            "score_minimo",
            "complexidade_maxima"
        ]
        
        for campo in campos_obrigatorios:
            if campo not in config_validada:
                logger.warning({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "campo_configuracao_ausente",
                    "status": "warning",
                    "source": "ConfiguradorNicho._validar_configuracao",
                    "details": {
                        "campo": campo,
                        "valor_padrao": config_padrao.get(campo)
                    }
                })
                config_validada[campo] = config_padrao.get(campo)
        
        return config_validada
    
    def _obter_configuracao_padrao(self, idioma: str) -> Dict[str, Any]:
        """
        Obtém configuração padrão para o idioma.
        
        Args:
            idioma: Idioma para configuração
            
        Returns:
            Configuração padrão
        """
        return {
            "volume_minimo": 10,
            "cpc_minimo": 0.01,
            "score_minimo": 0.3,
            "complexidade_maxima": 0.8,
            "competitividade_maxima": 0.7,
            "idioma": idioma,
            "ativar_cache": True,
            "ativar_ml": True,
            "max_workers": 4,
            "timeout_segundos": 300
        }
    
    def obter_tempo_configuracao(self) -> float:
        """Obtém tempo de configuração."""
        return self.tempo_configuracao
    
    def _converter_configuracao_para_dict(self, config_obj) -> Dict[str, Any]:
        """
        Converte objeto ConfiguracaoNicho para dicionário.
        
        Args:
            config_obj: Objeto ConfiguracaoNicho
            
        Returns:
            Dicionário com configuração
        """
        if hasattr(config_obj, '__dict__'):
            return config_obj.__dict__.copy()
        elif hasattr(config_obj, '_asdict'):
            return config_obj._asdict()
        else:
            return {} 