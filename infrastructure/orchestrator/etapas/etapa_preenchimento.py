"""
Etapa de Preenchimento - Omni Keywords Finder

Responsável pela geração de prompts e conteúdo usando IA:
- Integração com sistema de prompts
- Geração de conteúdo com IA
- Validação de qualidade
- Templates personalizados

Tracing ID: ETAPA_PREENCHIMENTO_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import sys

# Adicionar caminho para importar módulos do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

# Cache removido temporariamente - será implementado posteriormente
# from infrastructure.cache.cache_inteligente_cauda_longa import CacheInteligenteCaudaLonga
from domain.models import Keyword

logger = logging.getLogger(__name__)


@dataclass
class PromptGerado:
    """Estrutura para prompt gerado."""
    keyword: str
    tipo_prompt: str
    conteudo: str
    score_qualidade: float
    metadados: Dict[str, Any]


@dataclass
class PreenchimentoResult:
    """Resultado da etapa de preenchimento."""
    prompts_gerados: List[PromptGerado]
    total_prompts: int
    tempo_execucao: float
    templates_utilizados: List[str]
    metadados: Dict[str, Any]


class EtapaPreenchimento:
    """
    Etapa responsável pela geração de prompts e conteúdo.
    
    Integra com sistema de prompts existente e gera conteúdo
    personalizado para cada keyword.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a etapa de preenchimento.
        
        Args:
            config: Configurações da etapa de preenchimento
        """
        self.config = config
        # self.cache = CacheInteligenteCaudaLonga()  # Cache removido temporariamente
        
        # Templates disponíveis
        self.templates = self._carregar_templates()
        
        logger.info("Etapa de preenchimento inicializada")
    
    def _carregar_templates(self) -> Dict[str, str]:
        """Carrega templates de prompts disponíveis."""
        templates = {
            'blog_post': """
            Escreva um artigo de blog sobre "{keyword}" que seja:
            - Informativo e detalhado
            - Otimizado para SEO
            - Com pelo menos 1500 palavras
            - Incluindo subtítulos e estrutura clara
            - Com conclusão prática
            """,
            
            'social_media': """
            Crie 3 posts para redes sociais sobre "{keyword}":
            - Um post informativo
            - Um post com dica prática
            - Um post com curiosidade
            Cada post deve ter até 280 caracteres
            """,
            
            'email': """
            Escreva um email marketing sobre "{keyword}" que:
            - Tenha assunto atrativo
            - Seja persuasivo mas não agressivo
            - Inclua call-to-action claro
            - Seja personalizado para o público-alvo
            """,
            
            'landing_page': """
            Crie uma landing page sobre "{keyword}" com:
            - Headline principal atrativa
            - Benefícios claros
            - Prova social
            - Call-to-action destacado
            - Formulário de conversão
            """
        }
        
        # Carregar templates customizados se existirem
        templates_custom = self.config.get('templates_custom', {})
        templates.update(templates_custom)
        
        return templates
    
    async def executar(self, keywords: List[Keyword], nicho: str) -> PreenchimentoResult:
        """
        Executa a etapa de preenchimento para as keywords.
        
        Args:
            keywords: Lista de keywords para gerar prompts
            nicho: Nome do nicho
            
        Returns:
            PreenchimentoResult com os prompts gerados
        """
        inicio_tempo = time.time()
        logger.info(f"Iniciando preenchimento para nicho: {nicho} - {len(keywords)} keywords")
        
        try:
            # Executar preenchimento real (cache removido temporariamente)
            prompts_gerados = []
            templates_utilizados = []
            
            # Tipos de prompt a gerar
            tipos_prompt = self.config.get('tipos_prompt', ['blog_post', 'social_media'])
            max_prompts_por_keyword = self.config.get('max_prompts_por_keyword', 3)
            
            for keyword in keywords:
                if not hasattr(keyword, 'termo'):
                    continue
                
                termo = keyword.termo
                prompts_keyword = []
                
                # Gerar prompts para cada tipo solicitado
                for tipo_prompt in tipos_prompt[:max_prompts_por_keyword]:
                    try:
                        prompt = await self._gerar_prompt(termo, tipo_prompt, nicho)
                        if prompt:
                            prompts_keyword.append(prompt)
                            if tipo_prompt not in templates_utilizados:
                                templates_utilizados.append(tipo_prompt)
                    except Exception as e:
                        logger.error(f"Erro ao gerar prompt {tipo_prompt} para {termo}: {e}")
                        continue
                
                prompts_gerados.extend(prompts_keyword)
                
                # Aplicar rate limiting
                if self.config.get('delay_entre_prompts', 0.5) > 0:
                    time.sleep(self.config.get('delay_entre_prompts', 0.5))
            
            # Aplicar filtros de qualidade
            prompts_gerados = self._aplicar_filtros_qualidade(prompts_gerados)
            
            # Cache removido temporariamente
            
            tempo_execucao = time.time() - inicio_tempo
            
            resultado = PreenchimentoResult(
                prompts_gerados=prompts_gerados,
                total_prompts=len(prompts_gerados),
                tempo_execucao=tempo_execucao,
                templates_utilizados=templates_utilizados,
                metadados={
                    'nicho': nicho,
                    'keywords_originais': len(keywords),
                    'config_utilizada': self.config
                }
            )
            
            logger.info(f"Preenchimento concluído para nicho: {nicho} - {len(prompts_gerados)} prompts em {tempo_execucao:.2f}string_data")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na etapa de preenchimento para nicho {nicho}: {e}")
            raise
    
    async def _gerar_prompt(self, keyword: str, tipo_prompt: str, nicho: str) -> Optional[PromptGerado]:
        """Gera um prompt específico para uma keyword."""
        try:
            # Verificar se template existe
            if tipo_prompt not in self.templates:
                logger.warning(f"Template {tipo_prompt} não encontrado")
                return None
            
            # Obter template
            template = self.templates[tipo_prompt]
            
            # Preparar contexto
            contexto = {
                'keyword': keyword,
                'nicho': nicho,
                'idioma': self.config.get('idioma', 'pt-BR'),
                'tom': self.config.get('tom', 'profissional'),
                'publico_alvo': self.config.get('publico_alvo', 'geral')
            }
            
            # Preencher template com contexto (sem geração de conteúdo)
            conteudo = template.format(**contexto)
            
            if not conteudo:
                return None
            
            # Calcular score de qualidade básico
            score_qualidade = await self._calcular_score_qualidade(conteudo, keyword, tipo_prompt)
            
            # Criar prompt gerado
            prompt = PromptGerado(
                keyword=keyword,
                tipo_prompt=tipo_prompt,
                conteudo=conteudo,
                score_qualidade=score_qualidade,
                metadados={
                    'nicho': nicho,
                    'template_utilizado': tipo_prompt,
                    'timestamp': time.time()
                }
            )
            
            return prompt
            
        except Exception as e:
            logger.error(f"Erro ao gerar prompt: {e}")
            return None
    

    
    async def _calcular_score_qualidade(self, conteudo: str, keyword: str, tipo_prompt: str) -> float:
        """Calcula score de qualidade básico do prompt preenchido."""
        try:
            score = 0.0
            
            # Critérios básicos de qualidade
            criterios = {
                'comprimento': min(1.0, len(conteudo) / 500),  # Normalizar por 500 chars
                'relevancia_keyword': 1.0 if keyword.lower() in conteudo.lower() else 0.3,
                'estrutura_basica': 0.7 if any(marker in conteudo for marker in ['{', '}', 'keyword', 'nicho']) else 0.4
            }
            
            # Calcular score médio
            score = sum(criterios.values()) / len(criterios)
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de qualidade: {e}")
            return 0.5
    
    def _aplicar_filtros_qualidade(self, prompts: List[PromptGerado]) -> List[PromptGerado]:
        """Aplica filtros de qualidade nos prompts gerados."""
        prompts_filtrados = []
        
        score_minimo = self.config.get('min_qualidade_prompt', 0.8)
        
        for prompt in prompts:
            # Filtro de score mínimo
            if prompt.score_qualidade < score_minimo:
                continue
            
            # Filtro de comprimento mínimo
            comprimento_minimo = self.config.get('comprimento_minimo', 50)
            if len(prompt.conteudo) < comprimento_minimo:
                continue
            
            # Filtro de relevância da keyword
            if prompt.keyword.lower() not in prompt.conteudo.lower():
                continue
            
            prompts_filtrados.append(prompt)
        
        logger.info(f"Filtros aplicados: {len(prompts)} -> {len(prompts_filtrados)} prompts")
        return prompts_filtrados
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna status atual da etapa de preenchimento."""
        return {
            'templates_disponiveis': list(self.templates.keys()),
            'config': self.config,
            'cache_ativo': False  # Cache removido temporariamente
        } 