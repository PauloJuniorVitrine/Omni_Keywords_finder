"""
Normalizador centralizado para palavras-chave e termos.
Consolida todas as funções de normalização duplicadas entre coletores.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-003
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from shared.logger import logger


class NormalizadorCentral:
    """
    Normalizador centralizado para palavras-chave e termos.
    
    Responsabilidades:
    - Normalização de termos (case, espaços, acentos)
    - Validação de caracteres permitidos
    - Deduplicação de listas
    - Normalização de keywords completas
    - Logging estruturado
    
    Princípios aplicados:
    - DRY: Elimina duplicação entre coletores
    - SRP: Apenas normalização
    - Configurabilidade: Opções flexíveis
    - Rastreabilidade: Logging detalhado
    """
    
    def __init__(
        self,
        remover_acentos: bool = False,
        case_sensitive: bool = False,
        caracteres_permitidos: str = r'^[\w\string_data\-.,?!]+$',
        min_caracteres: int = 2,
        max_caracteres: int = 100
    ):
        """
        Inicializa o normalizador central.
        
        Args:
            remover_acentos: Se True, remove acentos dos termos
            case_sensitive: Se True, não converte para lowercase
            caracteres_permitidos: Regex para caracteres válidos
            min_caracteres: Tamanho mínimo do termo
            max_caracteres: Tamanho máximo do termo
        """
        self.remover_acentos = remover_acentos
        self.case_sensitive = case_sensitive
        self.caracteres_permitidos = caracteres_permitidos
        self.min_caracteres = min_caracteres
        self.max_caracteres = max_caracteres
    
    def normalizar_termo(self, termo: str) -> str:
        """
        Normaliza um termo individual.
        
        Processo:
        1. Remove espaços extras
        2. Normaliza espaços internos
        3. Converte para lowercase (se configurado)
        4. Remove acentos (se configurado)
        5. Valida caracteres permitidos
        
        Args:
            termo: Termo a ser normalizado
            
        Returns:
            Termo normalizado ou string vazia se inválido
        """
        if not termo:
            return ""
        
        try:
            # Remove espaços extras
            termo_norm = termo.strip()
            
            # Normaliza espaços internos
            termo_norm = re.sub(r'\string_data+', ' ', termo_norm)
            
            # Converte para lowercase (se não case sensitive)
            if not self.case_sensitive:
                termo_norm = termo_norm.lower()
            
            # Remove acentos (se configurado)
            if self.remover_acentos:
                termo_norm = unicodedata.normalize('NFKD', termo_norm).encode('ASCII', 'ignore').decode('ASCII')
            
            # Valida tamanho
            if not (self.min_caracteres <= len(termo_norm) <= self.max_caracteres):
                return ""
            
            # Valida caracteres permitidos
            if not re.match(self.caracteres_permitidos, termo_norm):
                return ""
            
            return termo_norm
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_normalizacao_termo",
                "status": "error",
                "source": "normalizador_central.normalizar_termo",
                "details": {
                    "termo_original": termo,
                    "erro": str(e)
                }
            })
            return ""
    
    def validar_termo(self, termo: str) -> bool:
        """
        Valida se um termo é válido para normalização.
        
        Args:
            termo: Termo a ser validado
            
        Returns:
            True se válido, False caso contrário
        """
        if not termo:
            return False
        
        termo_norm = self.normalizar_termo(termo)
        return bool(termo_norm)
    
    def normalizar_lista_termos(self, termos: List[str]) -> List[str]:
        """
        Normaliza uma lista de termos removendo duplicatas.
        
        Args:
            termos: Lista de termos a normalizar
            
        Returns:
            Lista de termos normalizados e únicos
        """
        termos_vistos: Set[str] = set()
        termos_normalizados: List[str] = []
        
        for termo in termos:
            termo_norm = self.normalizar_termo(termo)
            if termo_norm and termo_norm not in termos_vistos:
                termos_vistos.add(termo_norm)
                termos_normalizados.append(termo_norm)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "normalizacao_lista_termos",
            "status": "success",
            "source": "normalizador_central.normalizar_lista_termos",
            "details": {
                "total_original": len(termos),
                "total_normalizados": len(termos_normalizados),
                "duplicatas_removidas": len(termos) - len(termos_normalizados)
            }
        })
        
        return termos_normalizados
    
    def normalizar_keywords(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza uma lista de keywords (dicionários).
        
        Args:
            keywords: Lista de keywords como dicionários
            
        Returns:
            Lista de keywords normalizadas e únicas
        """
        termos_vistos: Set[str] = set()
        keywords_normalizadas: List[Dict[str, Any]] = []
        
        for kw in keywords:
            termo = kw.get('termo', '')
            termo_norm = self.normalizar_termo(termo)
            
            if termo_norm and termo_norm not in termos_vistos:
                termos_vistos.add(termo_norm)
                
                # Cria nova keyword com termo normalizado
                kw_normalizada = kw.copy()
                kw_normalizada['termo'] = termo_norm
                
                # Valida campos numéricos
                kw_normalizada['volume_busca'] = max(0, kw_normalizada.get('volume_busca', 0))
                kw_normalizada['cpc'] = max(0, kw_normalizada.get('cpc', 0))
                kw_normalizada['concorrencia'] = max(0, min(1, kw_normalizada.get('concorrencia', 0)))
                
                keywords_normalizadas.append(kw_normalizada)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "normalizacao_keywords",
            "status": "success",
            "source": "normalizador_central.normalizar_keywords",
            "details": {
                "total_original": len(keywords),
                "total_normalizadas": len(keywords_normalizadas),
                "duplicatas_removidas": len(keywords) - len(keywords_normalizadas)
            }
        })
        
        return keywords_normalizadas
    
    def normalizar_keywords_objects(self, keywords: List[Any]) -> List[Any]:
        """
        Normaliza uma lista de objetos Keyword.
        
        Args:
            keywords: Lista de objetos Keyword
            
        Returns:
            Lista de objetos Keyword normalizados e únicos
        """
        termos_vistos: Set[str] = set()
        keywords_normalizadas: List[Any] = []
        
        for kw in keywords:
            if not hasattr(kw, 'termo'):
                continue
                
            termo_norm = self.normalizar_termo(kw.termo)
            
            if termo_norm and termo_norm not in termos_vistos:
                termos_vistos.add(termo_norm)
                
                # Cria nova keyword com termo normalizado
                nova_kw = type(kw)(
                    termo=termo_norm,
                    volume_busca=max(0, getattr(kw, 'volume_busca', 0)),
                    cpc=max(0, getattr(kw, 'cpc', 0)),
                    concorrencia=max(0, min(1, getattr(kw, 'concorrencia', 0))),
                    intencao=getattr(kw, 'intencao', None),
                    score=getattr(kw, 'score', 0),
                    justificativa=getattr(kw, 'justificativa', ''),
                    fonte=getattr(kw, 'fonte', ''),
                    data_coleta=getattr(kw, 'data_coleta', datetime.utcnow())
                )
                
                keywords_normalizadas.append(nova_kw)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "normalizacao_keywords_objects",
            "status": "success",
            "source": "normalizador_central.normalizar_keywords_objects",
            "details": {
                "total_original": len(keywords),
                "total_normalizadas": len(keywords_normalizadas),
                "duplicatas_removidas": len(keywords) - len(keywords_normalizadas)
            }
        })
        
        return keywords_normalizadas
    
    def limpar_termo_especial(self, termo: str, remover_especiais: bool = True) -> str:
        """
        Limpeza especial de termos (remove caracteres especiais).
        
        Args:
            termo: Termo a ser limpo
            remover_especiais: Se True, remove caracteres especiais
            
        Returns:
            Termo limpo
        """
        if not termo:
            return ""
        
        termo_limpo = termo.strip()
        
        if remover_especiais:
            # Remove caracteres especiais mantendo letras, números e espaços
            termo_limpo = re.sub(r'[^\w\string_data]', '', termo_limpo)
            # Normaliza espaços
            termo_limpo = re.sub(r'\string_data+', ' ', termo_limpo)
        
        return termo_limpo.strip()
    
    def normalizar_para_busca(self, termo: str) -> str:
        """
        Normaliza termo para uso em buscas (mais permissivo).
        
        Args:
            termo: Termo a ser normalizado
            
        Returns:
            Termo normalizado para busca
        """
        if not termo:
            return ""
        
        # Remove espaços extras
        termo_norm = termo.strip()
        
        # Normaliza espaços internos
        termo_norm = re.sub(r'\string_data+', ' ', termo_norm)
        
        # Converte para lowercase
        termo_norm = termo_norm.lower()
        
        # Remove acentos
        termo_norm = unicodedata.normalize('NFKD', termo_norm).encode('ASCII', 'ignore').decode('ASCII')
        
        return termo_norm
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do normalizador.
        
        Returns:
            Estatísticas de configuração
        """
        return {
            "remover_acentos": self.remover_acentos,
            "case_sensitive": self.case_sensitive,
            "caracteres_permitidos": self.caracteres_permitidos,
            "min_caracteres": self.min_caracteres,
            "max_caracteres": self.max_caracteres,
            "timestamp": datetime.utcnow().isoformat()
        }


# Instância global para uso direto
normalizador_global = NormalizadorCentral()

# Funções de conveniência para compatibilidade
def normalizar_termo(termo: str, remover_acentos: bool = False, case_sensitive: bool = False) -> str:
    """
    Função de conveniência para normalização de termos.
    
    Args:
        termo: Termo a ser normalizado
        remover_acentos: Se True, remove acentos
        case_sensitive: Se True, não converte para lowercase
        
    Returns:
        Termo normalizado
    """
    normalizador = NormalizadorCentral(
        remover_acentos=remover_acentos,
        case_sensitive=case_sensitive
    )
    return normalizador.normalizar_termo(termo)


def validar_termo(termo: str, min_caracteres: int = 2, max_caracteres: int = 100) -> bool:
    """
    Função de conveniência para validação de termos.
    
    Args:
        termo: Termo a ser validado
        min_caracteres: Tamanho mínimo
        max_caracteres: Tamanho máximo
        
    Returns:
        True se válido, False caso contrário
    """
    normalizador = NormalizadorCentral(
        min_caracteres=min_caracteres,
        max_caracteres=max_caracteres
    )
    return normalizador.validar_termo(termo)


def normalizar_lista_termos(termos: List[str]) -> List[str]:
    """
    Função de conveniência para normalização de lista de termos.
    
    Args:
        termos: Lista de termos a normalizar
        
    Returns:
        Lista de termos normalizados e únicos
    """
    return normalizador_global.normalizar_lista_termos(termos) 