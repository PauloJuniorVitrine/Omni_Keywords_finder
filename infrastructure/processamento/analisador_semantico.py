"""
Analisador Semântico para Contagem de Palavras Significativas
LONGTAIL-001: Sistema completo de análise de palavras significativas

Tracing ID: LONGTAIL-001
Data/Hora: 2024-12-20 16:30:00 UTC
Versão: 1.0
Status: EM IMPLEMENTAÇÃO

Responsável: Sistema de Cauda Longa
"""

import re
import unicodedata
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from shared.logger import logger


@dataclass
class AnalisePalavras:
    """Resultado da análise de palavras significativas."""
    palavras_significativas: List[str]
    total_palavras: int
    palavras_unicas: int
    palavras_significativas_unicas: int
    score_significancia: float
    palavras_removidas: List[str]
    metadados: Dict[str, any]


class AnalisadorSemantico:
    """
    Sistema completo de análise de palavras significativas para cauda longa.
    
    Funcionalidades:
    - Lista de stop words em português
    - Filtro de palavras com menos de 3 caracteres
    - Análise de palavras-chave específicas
    - Contagem de palavras únicas
    - Normalização de contagem
    - Logs de análise de palavras
    - Integração com validador existente
    - Testes de edge cases
    - Performance otimizada
    - Configuração flexível
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o analisador semântico.
        
        Args:
            config: Configuração opcional do analisador
        """
        self.config = config or {}
        self._stop_words = self._carregar_stop_words()
        self._palavras_chave_especificas = self._carregar_palavras_chave()
        self._min_caracteres = self.config.get("min_caracteres", 3)
        self._case_sensitive = self.config.get("case_sensitive", False)
        self._remover_acentos = self.config.get("remover_acentos", False)
        
        # Métricas de performance
        self.metricas = {
            "total_analises": 0,
            "total_palavras_processadas": 0,
            "tempo_total_analise": 0.0,
            "ultima_analise": None
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "analisador_semantico_inicializado",
            "status": "success",
            "source": "AnalisadorSemantico.__init__",
            "details": {
                "min_caracteres": self._min_caracteres,
                "case_sensitive": self._case_sensitive,
                "remover_acentos": self._remover_acentos,
                "total_stop_words": len(self._stop_words),
                "total_palavras_chave": len(self._palavras_chave_especificas)
            }
        })
    
    def _carregar_stop_words(self) -> Set[str]:
        """
        Carrega lista de stop words em português.
        
        Returns:
            Conjunto de stop words
        """
        stop_words = {
            # Artigos
            "o", "a", "os", "as", "um", "uma", "uns", "umas",
            
            # Preposições
            "de", "da", "do", "das", "dos", "em", "na", "no", "nas", "nos",
            "por", "para", "com", "sem", "sob", "sobre", "entre", "contra",
            "desde", "até", "perante", "segundo", "conforme", "mediante",
            
            # Conjunções
            "e", "ou", "mas", "porém", "contudo", "todavia", "entretanto",
            "logo", "portanto", "assim", "pois", "que", "se", "como",
            "quando", "onde", "porque", "já", "ainda", "também", "nem",
            
            # Pronomes
            "eu", "tu", "ele", "ela", "nós", "vós", "eles", "elas",
            "me", "te", "se", "nos", "vos", "lhe", "lhes",
            "meu", "minha", "meus", "minhas", "teu", "tua", "teus", "tuas",
            "seu", "sua", "seus", "suas", "nosso", "nossa", "nossos", "nossas",
            "este", "esta", "estes", "estas", "esse", "essa", "esses", "essas",
            "aquele", "aquela", "aqueles", "aquelas", "isto", "isso", "aquilo",
            
            # Advérbios comuns
            "muito", "pouco", "mais", "menos", "bem", "mal", "melhor", "pior",
            "hoje", "ontem", "amanhã", "agora", "depois", "antes", "sempre",
            "nunca", "jamais", "talvez", "quiçá", "certamente", "realmente",
            "verdadeiramente", "efetivamente", "deveras", "indubitavelmente",
            
            # Verbos auxiliares e comuns
            "ser", "estar", "ter", "haver", "ir", "vir", "fazer", "dizer",
            "ver", "dar", "saber", "querer", "poder", "dever", "precisar",
            
            # Números
            "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito",
            "nove", "dez", "primeiro", "segundo", "terceiro", "quarto", "quinto",
            
            # Outros
            "sim", "não", "nada", "tudo", "algo", "ninguém", "alguém",
            "qualquer", "qualquer", "certo", "certa", "certos", "certas",
            "outro", "outra", "outros", "outras", "mesmo", "mesma", "mesmos", "mesmas",
            "próprio", "própria", "próprios", "próprias", "tal", "tais"
        }
        
        return stop_words
    
    def _carregar_palavras_chave(self) -> Set[str]:
        """
        Carrega palavras-chave específicas de cauda longa.
        
        Returns:
            Conjunto de palavras-chave específicas
        """
        palavras_chave = {
            # Palavras de intenção
            "como", "qual", "quando", "onde", "porque", "quanto", "quais",
            "melhor", "pior", "maior", "menor", "mais", "menos",
            "diferença", "comparação", "vantagem", "desvantagem",
            
            # Palavras de especificidade
            "específico", "específica", "específicos", "específicas",
            "detalhado", "detalhada", "detalhados", "detalhadas",
            "completo", "completa", "completos", "completas",
            "abrangente", "abrangentes", "extenso", "extensa", "extensos", "extensas",
            
            # Palavras de nicho
            "guia", "tutorial", "manual", "passo", "passos", "dica", "dicas",
            "recomendação", "recomendações", "sugestão", "sugestões",
            "opinião", "opiniões", "experiência", "experiências",
            
            # Palavras de tempo
            "atual", "atuais", "recente", "recentes", "novo", "nova", "novos", "novas",
            "antigo", "antiga", "antigos", "antigas", "clássico", "clássica", "clássicos", "clássicas",
            
            # Palavras de localização
            "brasil", "brasileiro", "brasileira", "brasileiros", "brasileiras",
            "local", "locais", "regional", "regionais", "nacional", "nacionais",
            
            # Palavras de qualidade
            "premium", "profissional", "profissionais", "especializado", "especializada",
            "especializados", "especializadas", "avançado", "avançada", "avançados", "avançadas"
        }
        
        return palavras_chave
    
    def normalizar_texto(self, texto: str) -> str:
        """
        Normaliza texto para análise.
        
        Args:
            texto: Texto a ser normalizado
            
        Returns:
            Texto normalizado
        """
        if not texto:
            return ""
        
        # Normalização básica
        texto = texto.strip()
        texto = re.sub(r'\string_data+', ' ', texto)
        
        # Case sensitivity
        if not self._case_sensitive:
            texto = texto.lower()
        
        # Remoção de acentos
        if self._remover_acentos:
            texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        
        return texto
    
    def extrair_palavras(self, texto: str) -> List[str]:
        """
        Extrai palavras do texto.
        
        Args:
            texto: Texto para extração
            
        Returns:
            Lista de palavras extraídas
        """
        texto_normalizado = self.normalizar_texto(texto)
        
        # Extração de palavras usando regex
        palavras = re.findall(r'\b\w+\b', texto_normalizado)
        
        return palavras
    
    def filtrar_palavras_significativas(self, palavras: List[str]) -> Tuple[List[str], List[str]]:
        """
        Filtra palavras significativas removendo stop words e palavras irrelevantes.
        
        Args:
            palavras: Lista de palavras para filtrar
            
        Returns:
            Tupla com (palavras_significativas, palavras_removidas)
        """
        palavras_significativas = []
        palavras_removidas = []
        
        for palavra in palavras:
            # Filtro de tamanho mínimo
            if len(palavra) < self._min_caracteres:
                palavras_removidas.append(f"{palavra} (muito curta)")
                continue
            
            # Filtro de stop words
            if palavra in self._stop_words:
                palavras_removidas.append(f"{palavra} (stop word)")
                continue
            
            # Filtro de números isolados
            if palavra.isdigit():
                palavras_removidas.append(f"{palavra} (número)")
                continue
            
            # Filtro de palavras com apenas caracteres especiais
            if not re.match(r'^[a-zA-ZÀ-ÿ]+$', palavra):
                palavras_removidas.append(f"{palavra} (caracteres especiais)")
                continue
            
            palavras_significativas.append(palavra)
        
        return palavras_significativas, palavras_removidas
    
    def calcular_score_significancia(self, palavras_significativas: List[str]) -> float:
        """
        Calcula score de significância baseado em palavras-chave específicas.
        
        Args:
            palavras_significativas: Lista de palavras significativas
            
        Returns:
            Score de significância entre 0 e 1
        """
        if not palavras_significativas:
            return 0.0
        
        # Contagem de palavras-chave específicas
        palavras_chave_encontradas = sum(
            1 for palavra in palavras_significativas 
            if palavra in self._palavras_chave_especificas
        )
        
        # Cálculo do score
        score_base = len(palavras_significativas) / max(len(palavras_significativas), 1)
        bonus_palavras_chave = palavras_chave_encontradas / max(len(palavras_significativas), 1)
        
        score_final = (score_base * 0.7) + (bonus_palavras_chave * 0.3)
        
        return min(1.0, max(0.0, score_final))
    
    def analisar_palavras(self, texto: str) -> AnalisePalavras:
        """
        Analisa palavras significativas em um texto.
        
        Args:
            texto: Texto para análise
            
        Returns:
            Resultado da análise
        """
        inicio_analise = datetime.utcnow()
        
        try:
            # Extração de palavras
            todas_palavras = self.extrair_palavras(texto)
            
            # Filtragem de palavras significativas
            palavras_significativas, palavras_removidas = self.filtrar_palavras_significativas(todas_palavras)
            
            # Cálculo de métricas
            total_palavras = len(todas_palavras)
            palavras_unicas = len(set(todas_palavras))
            palavras_significativas_unicas = len(set(palavras_significativas))
            
            # Cálculo do score de significância
            score_significancia = self.calcular_score_significancia(palavras_significativas)
            
            # Metadados da análise
            metadados = {
                "texto_original": texto,
                "texto_normalizado": self.normalizar_texto(texto),
                "configuracao": {
                    "min_caracteres": self._min_caracteres,
                    "case_sensitive": self._case_sensitive,
                    "remover_acentos": self._remover_acentos
                },
                "palavras_chave_encontradas": [
                    palavra for palavra in palavras_significativas 
                    if palavra in self._palavras_chave_especificas
                ]
            }
            
            # Criação do resultado
            resultado = AnalisePalavras(
                palavras_significativas=palavras_significativas,
                total_palavras=total_palavras,
                palavras_unicas=palavras_unicas,
                palavras_significativas_unicas=palavras_significativas_unicas,
                score_significancia=score_significancia,
                palavras_removidas=palavras_removidas,
                metadados=metadados
            )
            
            # Atualização de métricas
            tempo_analise = (datetime.utcnow() - inicio_analise).total_seconds()
            self.metricas["total_analises"] += 1
            self.metricas["total_palavras_processadas"] += total_palavras
            self.metricas["tempo_total_analise"] += tempo_analise
            self.metricas["ultima_analise"] = datetime.utcnow().isoformat()
            
            # Log da análise
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_palavras_significativas",
                "status": "success",
                "source": "AnalisadorSemantico.analisar_palavras",
                "details": {
                    "texto_tamanho": len(texto),
                    "total_palavras": total_palavras,
                    "palavras_significativas": len(palavras_significativas),
                    "score_significancia": score_significancia,
                    "tempo_analise": tempo_analise,
                    "palavras_removidas": len(palavras_removidas)
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_palavras",
                "status": "error",
                "source": "AnalisadorSemantico.analisar_palavras",
                "details": {
                    "texto": texto[:100] + "..." if len(texto) > 100 else texto,
                    "erro": str(e)
                }
            })
            
            # Retorno de erro
            return AnalisePalavras(
                palavras_significativas=[],
                total_palavras=0,
                palavras_unicas=0,
                palavras_significativas_unicas=0,
                score_significancia=0.0,
                palavras_removidas=[],
                metadados={"erro": str(e)}
            )
    
    def obter_metricas(self) -> Dict:
        """
        Obtém métricas de performance do analisador.
        
        Returns:
            Dicionário com métricas
        """
        return {
            **self.metricas,
            "tempo_medio_analise": (
                self.metricas["tempo_total_analise"] / max(self.metricas["total_analises"], 1)
            ),
            "palavras_por_analise": (
                self.metricas["total_palavras_processadas"] / max(self.metricas["total_analises"], 1)
            )
        }
    
    def resetar_metricas(self):
        """Reseta métricas de performance."""
        self.metricas = {
            "total_analises": 0,
            "total_palavras_processadas": 0,
            "tempo_total_analise": 0.0,
            "ultima_analise": None
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "metricas_resetadas",
            "status": "info",
            "source": "AnalisadorSemantico.resetar_metricas",
            "details": {"acao": "reset_metricas"}
        })


# Instância global para uso em outros módulos
analisador_semantico = AnalisadorSemantico() 