"""
Módulo de normalização de palavras-chave.
Responsável por normalizar termos, remover duplicatas e aplicar regras de formatação.
"""
from typing import List, Set, Optional
from domain.models import Keyword
from shared.logger import logger
import re
import unicodedata
from datetime import datetime

class NormalizadorKeywords:
    """
    Normaliza palavras-chave aplicando regras de formatação e deduplicação.
    
    Responsabilidades:
    - Normalização de termos (case, espaços, acentos)
    - Remoção de duplicatas
    - Validação de caracteres permitidos
    - Logging estruturado
    
    Princípios aplicados:
    - SRP: Apenas normalização
    - Imutabilidade: Não altera objetos originais
    - Configurabilidade: Opções de normalização
    """
    
    def __init__(
        self,
        remover_acentos: bool = False,
        case_sensitive: bool = False,
        caracteres_permitidos: str = r'^[\w\string_data\-.,?!]+$'
    ):
        """
        Inicializa o normalizador com configurações.
        
        Args:
            remover_acentos: Se True, remove acentos dos termos
            case_sensitive: Se True, não converte para lowercase
            caracteres_permitidos: Regex para caracteres válidos
        """
        self.remover_acentos = remover_acentos
        self.case_sensitive = case_sensitive
        self.caracteres_permitidos = caracteres_permitidos
        
    def normalizar_termo(self, termo: str) -> str:
        """
        Normaliza um termo aplicando as regras configuradas.
        
        Aplicações:
        - Strip de espaços
        - Normalização de espaços internos
        - Conversão case (se configurado)
        - Remoção de acentos (se configurado)
        - Validação de caracteres permitidos
        
        Args:
            termo: Termo a ser normalizado
            
        Returns:
            Termo normalizado ou string vazia se inválido
        """
        if not termo:
            return ""
            
        # Aplicar normalizações básicas
        termo = termo.strip()
        termo = re.sub(r'\string_data+', ' ', termo)
        
        # Conversão de case
        if not self.case_sensitive:
            termo = termo.lower()
            
        # Remoção de acentos
        if self.remover_acentos:
            termo = unicodedata.normalize('NFKD', termo).encode('ASCII', 'ignore').decode('ASCII')
            
        # Validação de caracteres permitidos
        if not re.fullmatch(self.caracteres_permitidos, termo):
            return ""
            
        return termo
    
    def normalizar_lista(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Normaliza uma lista de keywords removendo duplicatas.
        
        Processo:
        1. Normaliza cada termo individualmente
        2. Remove termos vazios/inválidos
        3. Deduplica por termo normalizado
        4. Preserva metadados originais
        5. Valida campos numéricos
        
        Args:
            keywords: Lista de Keyword a normalizar
            
        Returns:
            Lista de Keyword normalizada e sem duplicatas
        """
        termos_vistos: Set[str] = set()
        keywords_normalizadas: List[Keyword] = []
        
        for kw in keywords:
            if not kw.termo:
                continue
                
            termo_norm = self.normalizar_termo(kw.termo)
            if not termo_norm:
                continue
                
            # Deduplicação
            if termo_norm not in termos_vistos:
                termos_vistos.add(termo_norm)
                
                # Criar nova keyword com dados normalizados
                nova_kw = Keyword(
                    termo=termo_norm,
                    volume_busca=max(0, kw.volume_busca),
                    cpc=max(0, kw.cpc),
                    concorrencia=max(0, min(1, kw.concorrencia)),
                    intencao=kw.intencao,
                    score=kw.score,
                    justificativa=kw.justificativa,
                    fonte=kw.fonte,
                    data_coleta=kw.data_coleta
                )
                keywords_normalizadas.append(nova_kw)
        
        # Logging estruturado
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "normalizacao_keywords",
            "status": "success",
            "source": "normalizador_keywords.normalizar_lista",
            "details": {
                "total_entrada": len(keywords),
                "total_normalizadas": len(keywords_normalizadas),
                "remover_acentos": self.remover_acentos,
                "case_sensitive": self.case_sensitive
            }
        })
        
        return keywords_normalizadas
    
    def validar_configuracao(self) -> bool:
        """
        Valida se a configuração do normalizador é válida.
        
        Returns:
            True se configuração válida, False caso contrário
        """
        try:
            # Testar regex de caracteres permitidos
            re.compile(self.caracteres_permitidos)
            return True
        except re.error:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_configuracao_normalizador",
                "status": "error",
                "source": "normalizador_keywords.validar_configuracao",
                "details": {"regex_invalido": self.caracteres_permitidos}
            })
            return False 