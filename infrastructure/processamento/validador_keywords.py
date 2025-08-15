"""
Módulo de validação de palavras-chave.
Responsável por validar keywords conforme regras configuráveis.

Tracing ID: IMP002_VALIDADOR_INTEGRADO_001
Data/Hora: 2024-12-27 22:40:00 UTC
Versão: 2.0
Prompt: Integração IMP-002 - Validação Semântica Anti-Falsos Positivos
Ruleset: enterprise_control_layer.yaml
"""

from typing import List, Dict, Optional, Tuple, Set
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime
from infrastructure.processamento.validador_semantico_avancado import ValidadorSemanticoAvancado
import re

class ValidadorKeywords:
    """
    Valida palavras-chave conforme regras configuráveis.
    
    Responsabilidades:
    - Validação de termos individuais
    - Validação de listas de keywords
    - Aplicação de regras customizáveis
    - Geração de relatórios de validação
    - Suporte a blacklist/whitelist
    
    Princípios aplicados:
    - SRP: Apenas validação
    - Configurabilidade: Regras flexíveis
    - Rastreabilidade: Relatórios detalhados
    """
    
    def __init__(
        self,
        min_palavras: int = 3,
        tamanho_min: int = 15,
        tamanho_max: int = 100,
        concorrencia_max: float = 0.5,
        score_minimo: float = 0.0,
        volume_min: int = 0,
        cpc_min: float = 0.0,
        regex_termo: Optional[str] = None,
        palavras_obrigatorias: Optional[List[str]] = None,
        blacklist: Optional[Set[str]] = None,
        whitelist: Optional[Set[str]] = None,
        enable_semantic_validation: bool = True
    ):
        """
        Inicializa o validador com regras configuráveis.
        
        Args:
            min_palavras: Número mínimo de palavras no termo
            tamanho_min: Tamanho mínimo do termo (caracteres)
            tamanho_max: Tamanho máximo do termo (caracteres)
            concorrencia_max: Concorrência máxima permitida
            score_minimo: Score mínimo para aprovação
            volume_min: Volume mínimo de busca
            cpc_min: CPC mínimo
            regex_termo: Regex para validação do termo
            palavras_obrigatorias: Lista de palavras que devem estar presentes
            blacklist: Conjunto de termos proibidos
            whitelist: Conjunto de termos obrigatórios
        """
        self.min_palavras = min_palavras
        self.tamanho_min = tamanho_min
        self.tamanho_max = tamanho_max
        self.concorrencia_max = concorrencia_max
        self.score_minimo = score_minimo
        self.volume_min = volume_min
        self.cpc_min = cpc_min
        self.regex_termo = regex_termo
        self.palavras_obrigatorias = palavras_obrigatorias or []
        self.blacklist = blacklist or set()
        self.whitelist = whitelist or set()
        self.enable_semantic_validation = enable_semantic_validation
        
        # Inicializar validador semântico se habilitado
        self.validador_semantico = None
        if self.enable_semantic_validation:
            try:
                self.validador_semantico = ValidadorSemanticoAvancado()
            except ImportError:
                logger.warning("Validador semântico não disponível. Validação semântica desabilitada.")
                self.enable_semantic_validation = False
        
    def validar_keyword(self, kw: Keyword) -> Tuple[bool, Dict]:
        """
        Valida uma keyword individual conforme as regras configuradas.
        
        Args:
            kw: Keyword a ser validada
            
        Returns:
            Tupla (é_válida, detalhes_validação)
        """
        detalhes = {
            "termo": kw.termo,
            "regras_verificadas": [],
            "violacoes": []
        }
        
        # Validação básica do termo
        if not kw.termo or not kw.termo.strip():
            detalhes["violacoes"].append("termo_vazio")
            return False, detalhes
            
        # Validação de tamanho
        if len(kw.termo) < self.tamanho_min:
            detalhes["violacoes"].append(f"tamanho_minimo_{self.tamanho_min}")
        elif len(kw.termo) > self.tamanho_max:
            detalhes["violacoes"].append(f"tamanho_maximo_{self.tamanho_max}")
        else:
            detalhes["regras_verificadas"].append("tamanho")
            
        # Validação de número de palavras
        num_palavras = len(kw.termo.split())
        if num_palavras < self.min_palavras:
            detalhes["violacoes"].append(f"min_palavras_{self.min_palavras}")
        else:
            detalhes["regras_verificadas"].append("num_palavras")
            
        # Validação de regex
        if self.regex_termo and not re.search(self.regex_termo, kw.termo):
            detalhes["violacoes"].append("regex_termo")
        elif self.regex_termo:
            detalhes["regras_verificadas"].append("regex")
            
        # Validação de palavras obrigatórias
        if self.palavras_obrigatorias:
            termo_lower = kw.termo.lower()
            palavras_faltantes = [
                palavra for palavra in self.palavras_obrigatorias 
                if palavra.lower() not in termo_lower
            ]
            if palavras_faltantes:
                detalhes["violacoes"].append(f"palavras_obrigatorias_faltantes_{palavras_faltantes}")
            else:
                detalhes["regras_verificadas"].append("palavras_obrigatorias")
                
        # Validação de blacklist
        if kw.termo.lower() in {termo.lower() for termo in self.blacklist}:
            detalhes["violacoes"].append("blacklist")
        else:
            detalhes["regras_verificadas"].append("blacklist")
            
        # Validação de whitelist (se configurada)
        if self.whitelist:
            if kw.termo.lower() not in {termo.lower() for termo in self.whitelist}:
                detalhes["violacoes"].append("whitelist")
            else:
                detalhes["regras_verificadas"].append("whitelist")
                
        # Validação de campos numéricos
        if kw.volume_busca < self.volume_min:
            detalhes["violacoes"].append(f"volume_min_{self.volume_min}")
        else:
            detalhes["regras_verificadas"].append("volume")
            
        if kw.cpc < self.cpc_min:
            detalhes["violacoes"].append(f"cpc_min_{self.cpc_min}")
        else:
            detalhes["regras_verificadas"].append("cpc")
            
        if kw.concorrencia > self.concorrencia_max:
            detalhes["violacoes"].append(f"concorrencia_max_{self.concorrencia_max}")
        else:
            detalhes["regras_verificadas"].append("concorrencia")
            
        if kw.score < self.score_minimo:
            detalhes["violacoes"].append(f"score_min_{self.score_minimo}")
        else:
            detalhes["regras_verificadas"].append("score")
            
        # Determinar se é válida
        is_valida = len(detalhes["violacoes"]) == 0
        
        return is_valida, detalhes
        
    def validar_keyword_com_semantica(self, kw: Keyword) -> Tuple[bool, Dict]:
        """
        Valida uma keyword com análise semântica integrada.
        
        Args:
            kw: Keyword a ser validada
            
        Returns:
            Tupla (é_válida, detalhes_validação_completa)
        """
        # Validação básica primeiro
        is_valida_basica, detalhes_basicos = self.validar_keyword(kw)
        
        detalhes_completos = {
            **detalhes_basicos,
            "validacao_semantica": None,
            "recomendacao_final": "aprovada" if is_valida_basica else "rejeitar",
            "justificativa_semantica": []
        }
        
        # Se passou na validação básica, aplicar validação semântica
        if is_valida_basica and self.enable_semantic_validation and self.validador_semantico:
            try:
                analise_semantica = self.validador_semantico.analisar_semantica_keyword(kw)
                detalhes_completos["validacao_semantica"] = analise_semantica
                
                # Determinar recomendação final baseada em ambas as validações
                if analise_semantica["recomendacao"] == "rejeitar":
                    detalhes_completos["recomendacao_final"] = "rejeitar"
                    detalhes_completos["justificativa_semantica"] = analise_semantica["justificativa"]
                elif analise_semantica["recomendacao"] == "revisar":
                    detalhes_completos["recomendacao_final"] = "revisar"
                    detalhes_completos["justificativa_semantica"] = analise_semantica["justificativa"]
                else:
                    detalhes_completos["recomendacao_final"] = "aprovada"
                    
            except Exception as e:
                logger.error(f"Erro na validação semântica: {e}")
                detalhes_completos["validacao_semantica"] = {"erro": str(e)}
                
        # Determinar resultado final
        is_valida_final = detalhes_completos["recomendacao_final"] == "aprovada"
        
        return is_valida_final, detalhes_completos
        
    def validar_lista(
        self, 
        keywords: List[Keyword], 
        relatorio: bool = False
    ) -> Tuple[List[Keyword], List[Keyword], Optional[Dict]]:
        """
        Valida uma lista de keywords.
        
        Args:
            keywords: Lista de keywords a validar
            relatorio: Se True, gera relatório detalhado
            
        Returns:
            Tupla (keywords_aprovadas, keywords_rejeitadas, relatorio)
        """
        keywords_aprovadas = []
        keywords_rejeitadas = []
        estatisticas = {
            "total": len(keywords),
            "aprovadas": 0,
            "rejeitadas": 0,
            "violacoes_por_tipo": {},
            "regras_mais_violadas": {}
        }
        
        for kw in keywords:
            is_valida, detalhes = self.validar_keyword(kw)
            
            if is_valida:
                keywords_aprovadas.append(kw)
                estatisticas["aprovadas"] += 1
            else:
                keywords_rejeitadas.append(kw)
                estatisticas["rejeitadas"] += 1
                
                # Contar violações por tipo
                for violacao in detalhes["violacoes"]:
                    estatisticas["violacoes_por_tipo"][violacao] = \
                        estatisticas["violacoes_por_tipo"].get(violacao, 0) + 1
                        
        # Calcular regras mais violadas
        if estatisticas["violacoes_por_tipo"]:
            estatisticas["regras_mais_violadas"] = dict(
                sorted(
                    estatisticas["violacoes_por_tipo"].items(),
                    key=lambda value: value[1],
                    reverse=True
                )[:5]
            )
            
        # Logging
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "validacao_keywords",
            "status": "success",
            "source": "validador_keywords.validar_lista",
            "details": {
                "total": estatisticas["total"],
                "aprovadas": estatisticas["aprovadas"],
                "rejeitadas": estatisticas["rejeitadas"],
                "taxa_aprovacao": estatisticas["aprovadas"] / estatisticas["total"] if estatisticas["total"] > 0 else 0
            }
        })
        
        relatorio_final = estatisticas if relatorio else None
        
        return keywords_aprovadas, keywords_rejeitadas, relatorio_final
        
    def validar_avancado(
        self,
        keywords: List[Keyword],
        regras: Optional[Dict] = None,
        relatorio: bool = False,
        blacklist: Optional[List[str]] = None,
        whitelist: Optional[List[str]] = None
    ) -> Tuple[List[Keyword], List[Keyword], Optional[Dict]]:
        """
        Validação avançada com regras customizáveis.
        
        Args:
            keywords: Lista de keywords a validar
            regras: Dicionário com regras customizadas
            relatorio: Se True, gera relatório detalhado
            blacklist: Lista de termos proibidos
            whitelist: Lista de termos obrigatórios
            
        Returns:
            Tupla (keywords_aprovadas, keywords_rejeitadas, relatorio)
        """
        # Criar validador temporário com regras customizadas
        validador_temp = ValidadorKeywords(
            min_palavras=regras.get("min_palavras", self.min_palavras) if regras else self.min_palavras,
            tamanho_min=regras.get("tamanho_min", self.tamanho_min) if regras else self.tamanho_min,
            tamanho_max=regras.get("tamanho_max", self.tamanho_max) if regras else self.tamanho_max,
            concorrencia_max=regras.get("concorrencia_max", self.concorrencia_max) if regras else self.concorrencia_max,
            score_minimo=regras.get("score_min", self.score_minimo) if regras else self.score_minimo,
            volume_min=regras.get("volume_min", self.volume_min) if regras else self.volume_min,
            cpc_min=regras.get("cpc_min", self.cpc_min) if regras else self.cpc_min,
            regex_termo=regras.get("regex_termo", self.regex_termo) if regras else self.regex_termo,
            palavras_obrigatorias=regras.get("palavras_obrigatorias", self.palavras_obrigatorias) if regras else self.palavras_obrigatorias,
            blacklist=set(blacklist) if blacklist else self.blacklist,
            whitelist=set(whitelist) if whitelist else self.whitelist
        )
        
        return validador_temp.validar_lista(keywords, relatorio)
        
    def obter_configuracao(self) -> Dict:
        """
        Retorna a configuração atual do validador.
        
        Returns:
            Dicionário com configuração atual
        """
        return {
            "min_palavras": self.min_palavras,
            "tamanho_min": self.tamanho_min,
            "tamanho_max": self.tamanho_max,
            "concorrencia_max": self.concorrencia_max,
            "score_minimo": self.score_minimo,
            "volume_min": self.volume_min,
            "cpc_min": self.cpc_min,
            "regex_termo": self.regex_termo,
            "palavras_obrigatorias": self.palavras_obrigatorias,
            "blacklist": list(self.blacklist),
            "whitelist": list(self.whitelist)
        } 