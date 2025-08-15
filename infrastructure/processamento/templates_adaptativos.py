"""
Sistema de Templates Adaptativos por Nicho - Omni Keywords Finder
==============================================================

Este módulo implementa templates específicos por nicho, substituindo
o template único por templates adaptados para cada categoria.

Autor: Paulo Júnior
Data: 2024-12-20
Tracing ID: LONGTAIL-018
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from domain.models import Keyword, IntencaoBusca
from shared.logger import logger
from shared.config import ProcessingConfig, FUNNEL_STAGES

class Nicho(Enum):
    """Enumeração dos nichos suportados."""
    ECOMMERCE = "ecommerce"
    SAUDE = "saude"
    TECNOLOGIA = "tecnologia"
    EDUCACAO = "educacao"
    FINANCAS = "financas"
    VIAGENS = "viagens"
    AUTOMOVEIS = "automoveis"
    CASA_JARDIM = "casa_jardim"
    ESPORTES = "esportes"
    ENTRETENIMENTO = "entretenimento"
    GENERICO = "generico"

@dataclass
class TemplateConfig:
    """Configuração de template para um nicho específico."""
    nicho: Nicho
    nome: str
    descricao: str
    template_base: str
    variaveis_obrigatorias: List[str]
    variaveis_opcionais: List[str]
    regras_especificas: Dict[str, Any]
    ativo: bool = True
    versao: str = "1.0"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class TemplateResult:
    """Resultado da aplicação de template."""
    keyword: Keyword
    template_aplicado: TemplateConfig
    prompt_gerado: str
    variaveis_utilizadas: Dict[str, str]
    score_adequacao: float
    justificativa: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class TemplatesAdaptativos:
    """
    Sistema de templates adaptativos por nicho.
    
    Características:
    - Templates específicos por categoria
    - Detecção automática de nicho
    - Personalização por fase do funil
    - Validação de adequação
    - Logs detalhados de aplicação
    """
    
    def __init__(
        self,
        enable_deteccao_automatica: bool = True,
        enable_logging: bool = True,
        fallback_template: Optional[str] = None
    ):
        """
        Inicializa o sistema de templates adaptativos.
        
        Args:
            enable_deteccao_automatica: Se True, detecta nicho automaticamente
            enable_logging: Se True, habilita logs detalhados
            fallback_template: Template de fallback para nichos não reconhecidos
        """
        self.enable_deteccao_automatica = enable_deteccao_automatica
        self.enable_logging = enable_logging
        self.fallback_template = fallback_template or self._get_template_generico()
        
        # Inicializa templates por nicho
        self.templates = self._inicializar_templates()
        
        # Palavras-chave para detecção de nicho
        self.palavras_nicho = {
            Nicho.ECOMMERCE: [
                "comprar", "produto", "loja", "preço", "oferta", "desconto",
                "marca", "modelo", "especificações", "avaliações", "entrega"
            ],
            Nicho.SAUDE: [
                "sintomas", "tratamento", "medicamento", "doença", "cura",
                "prevenção", "exame", "consulta", "médico", "hospital"
            ],
            Nicho.TECNOLOGIA: [
                "software", "hardware", "programação", "app", "sistema",
                "tecnologia", "digital", "online", "internet", "computador"
            ],
            Nicho.EDUCACAO: [
                "curso", "estudo", "aprendizado", "ensino", "educação",
                "faculdade", "universidade", "professor", "aluno", "material"
            ],
            Nicho.FINANCAS: [
                "investimento", "dinheiro", "economia", "finanças", "banco",
                "crédito", "empréstimo", "poupança", "ações", "renda"
            ],
            Nicho.VIAGENS: [
                "viagem", "turismo", "hotel", "passagem", "destino",
                "passeio", "turístico", "reserva", "hospedagem", "turismo"
            ],
            Nicho.AUTOMOVEIS: [
                "carro", "automóvel", "veículo", "marca", "modelo",
                "motor", "combustível", "manutenção", "seguro", "financiamento"
            ],
            Nicho.CASA_JARDIM: [
                "casa", "jardim", "decoração", "móveis", "construção",
                "reforma", "paisagismo", "horta", "plantas", "ferramentas"
            ],
            Nicho.ESPORTES: [
                "esporte", "atividade física", "treino", "competição",
                "equipamento", "academia", "corrida", "futebol", "basquete"
            ],
            Nicho.ENTRETENIMENTO: [
                "filme", "série", "música", "jogo", "entretenimento",
                "arte", "teatro", "cinema", "show", "evento"
            ]
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "templates_adaptativos_inicializado",
            "status": "success",
            "source": "templates_adaptativos.__init__",
            "details": {
                "total_templates": len(self.templates),
                "nichos_suportados": [n.value for n in self.templates.keys()],
                "enable_deteccao_automatica": enable_deteccao_automatica
            }
        })
    
    def _inicializar_templates(self) -> Dict[Nicho, TemplateConfig]:
        """Inicializa todos os templates por nicho."""
        templates = {}
        
        # Template E-commerce
        templates[Nicho.ECOMMERCE] = TemplateConfig(
            nicho=Nicho.ECOMMERCE,
            nome="Template E-commerce",
            descricao="Template otimizado para produtos e vendas online",
            template_base="""
# Artigo: {titulo}

## Introdução
{keyword} é uma das principais dúvidas de quem busca {produto_categoria}. Neste artigo, vamos explorar tudo sobre {tema_principal} para ajudar você a tomar a melhor decisão.

## O que é {tema_principal}?
{tema_principal} é {definicao_basica}. É importante entender que {explicacao_importancia}.

## Principais Características
- **{caracteristica_1}**: {descricao_1}
- **{caracteristica_2}**: {descricao_2}
- **{caracteristica_3}**: {descricao_3}

## Como Escolher o Melhor {produto_categoria}
Para escolher o melhor {produto_categoria}, considere:
1. {criterio_1}
2. {criterio_2}
3. {criterio_3}

## Conclusão
{keyword} é essencial para {beneficio_principal}. Com as informações deste artigo, você estará preparado para fazer a melhor escolha.
            """,
            variaveis_obrigatorias=[
                "titulo", "keyword", "produto_categoria", "tema_principal",
                "definicao_basica", "explicacao_importancia"
            ],
            variaveis_opcionais=[
                "caracteristica_1", "caracteristica_2", "caracteristica_3",
                "descricao_1", "descricao_2", "descricao_3",
                "criterio_1", "criterio_2", "criterio_3",
                "beneficio_principal"
            ],
            regras_especificas={
                "foco_venda": True,
                "incluir_precos": True,
                "destaque_beneficios": True,
                "call_to_action": True
            }
        )
        
        # Template Saúde
        templates[Nicho.SAUDE] = TemplateConfig(
            nicho=Nicho.SAUDE,
            nome="Template Saúde",
            descricao="Template otimizado para conteúdo de saúde e bem-estar",
            template_base="""
# Guia Completo: {titulo}

## Introdução
{keyword} é uma preocupação comum entre muitas pessoas. Neste guia, vamos abordar {tema_principal} de forma clara e informativa.

## O que é {tema_principal}?
{tema_principal} é {definicao_basica}. É fundamental compreender que {explicacao_importancia}.

## Sintomas e Sinais
Os principais sintomas incluem:
- {sintoma_1}
- {sintoma_2}
- {sintoma_3}

## Causas Principais
As causas mais comuns são:
1. {causa_1}
2. {causa_2}
3. {causa_3}

## Tratamentos Disponíveis
Os tratamentos incluem:
- **{tratamento_1}**: {descricao_1}
- **{tratamento_2}**: {descricao_2}

## Prevenção
Para prevenir {tema_principal}, é importante:
- {prevencao_1}
- {prevencao_2}

## Quando Procurar um Médico
Consulte um profissional se {sinais_alerta}.

## Conclusão
{keyword} requer atenção e conhecimento adequado. Sempre consulte um profissional de saúde para orientações específicas.
            """,
            variaveis_obrigatorias=[
                "titulo", "keyword", "tema_principal", "definicao_basica",
                "explicacao_importancia", "sinais_alerta"
            ],
            variaveis_opcionais=[
                "sintoma_1", "sintoma_2", "sintoma_3",
                "causa_1", "causa_2", "causa_3",
                "tratamento_1", "tratamento_2", "descricao_1", "descricao_2",
                "prevencao_1", "prevencao_2"
            ],
            regras_especificas={
                "foco_informacao": True,
                "incluir_sintomas": True,
                "destaque_prevencao": True,
                "disclaimer_medico": True
            }
        )
        
        # Template Tecnologia
        templates[Nicho.TECNOLOGIA] = TemplateConfig(
            nicho=Nicho.TECNOLOGIA,
            nome="Template Tecnologia",
            descricao="Template otimizado para conteúdo de tecnologia e inovação",
            template_base="""
# {titulo} - Guia Definitivo

## Introdução
{keyword} é um tema fundamental no mundo da tecnologia atual. Vamos explorar {tema_principal} e suas implicações.

## O que é {tema_principal}?
{tema_principal} é {definicao_basica}. Esta tecnologia {explicacao_importancia}.

## Como Funciona
O funcionamento envolve:
1. {processo_1}
2. {processo_2}
3. {processo_3}

## Vantagens e Benefícios
As principais vantagens incluem:
- **{vantagem_1}**: {descricao_1}
- **{vantagem_2}**: {descricao_2}
- **{vantagem_3}**: {descricao_3}

## Aplicações Práticas
Esta tecnologia pode ser aplicada em:
- {aplicacao_1}
- {aplicacao_2}
- {aplicacao_3}

## Tendências Futuras
O futuro de {tema_principal} inclui:
- {tendencia_1}
- {tendencia_2}

## Conclusão
{keyword} representa uma evolução importante na tecnologia. Entender {tema_principal} é essencial para se manter atualizado.
            """,
            variaveis_obrigatorias=[
                "titulo", "keyword", "tema_principal", "definicao_basica",
                "explicacao_importancia"
            ],
            variaveis_opcionais=[
                "processo_1", "processo_2", "processo_3",
                "vantagem_1", "vantagem_2", "vantagem_3",
                "descricao_1", "descricao_2", "descricao_3",
                "aplicacao_1", "aplicacao_2", "aplicacao_3",
                "tendencia_1", "tendencia_2"
            ],
            regras_especificas={
                "foco_inovacao": True,
                "incluir_tendencias": True,
                "destaque_aplicacoes": True,
                "linguagem_tecnica": True
            }
        )
        
        # Template Educação
        templates[Nicho.EDUCACAO] = TemplateConfig(
            nicho=Nicho.EDUCACAO,
            nome="Template Educação",
            descricao="Template otimizado para conteúdo educacional e didático",
            template_base="""
# Aprenda sobre {titulo}

## Introdução
{keyword} é um conhecimento essencial para {publico_alvo}. Neste artigo, vamos aprender {tema_principal} de forma didática.

## Conceito Básico
{tema_principal} é {definicao_basica}. É importante entender que {explicacao_importancia}.

## Fundamentos
Os fundamentos incluem:
- **{fundamento_1}**: {explicacao_1}
- **{fundamento_2}**: {explicacao_2}
- **{fundamento_3}**: {explicacao_3}

## Passo a Passo
Para aprender {tema_principal}, siga estes passos:
1. {passo_1}
2. {passo_2}
3. {passo_3}

## Exemplos Práticos
Veja alguns exemplos:
- {exemplo_1}
- {exemplo_2}

## Dicas Importantes
Algumas dicas para dominar {tema_principal}:
- {dica_1}
- {dica_2}

## Conclusão
{keyword} é fundamental para {beneficio_aprendizado}. Continue praticando para aprimorar seus conhecimentos.
            """,
            variaveis_obrigatorias=[
                "titulo", "keyword", "publico_alvo", "tema_principal",
                "definicao_basica", "explicacao_importancia", "beneficio_aprendizado"
            ],
            variaveis_opcionais=[
                "fundamento_1", "fundamento_2", "fundamento_3",
                "explicacao_1", "explicacao_2", "explicacao_3",
                "passo_1", "passo_2", "passo_3",
                "exemplo_1", "exemplo_2",
                "dica_1", "dica_2"
            ],
            regras_especificas={
                "foco_aprendizado": True,
                "incluir_exemplos": True,
                "destaque_dicas": True,
                "linguagem_didatica": True
            }
        )
        
        # Template Genérico (fallback)
        templates[Nicho.GENERICO] = TemplateConfig(
            nicho=Nicho.GENERICO,
            nome="Template Genérico",
            descricao="Template padrão para nichos não específicos",
            template_base="""
# {titulo}

## Introdução
{keyword} é um tema relevante que merece nossa atenção. Vamos explorar {tema_principal} em detalhes.

## O que é {tema_principal}?
{tema_principal} é {definicao_basica}. É importante compreender que {explicacao_importancia}.

## Aspectos Principais
Os principais aspectos incluem:
- {aspecto_1}
- {aspecto_2}
- {aspecto_3}

## Considerações Importantes
Algumas considerações importantes:
1. {consideracao_1}
2. {consideracao_2}
3. {consideracao_3}

## Conclusão
{keyword} é fundamental para {beneficio_principal}. Compreender {tema_principal} traz diversos benefícios.
            """,
            variaveis_obrigatorias=[
                "titulo", "keyword", "tema_principal", "definicao_basica",
                "explicacao_importancia", "beneficio_principal"
            ],
            variaveis_opcionais=[
                "aspecto_1", "aspecto_2", "aspecto_3",
                "consideracao_1", "consideracao_2", "consideracao_3"
            ],
            regras_especificas={
                "foco_geral": True,
                "linguagem_neutra": True,
                "estrutura_simples": True
            }
        )
        
        return templates
    
    def _get_template_generico(self) -> str:
        """Retorna template genérico de fallback."""
        return """
# {titulo}

## Introdução
{keyword} é um tema importante que vamos explorar neste artigo.

## Desenvolvimento
{tema_principal} é {definicao_basica}. {explicacao_importancia}.

## Conclusão
{keyword} é essencial para {beneficio_principal}.
        """
    
    def detectar_nicho_automatico(self, keyword: Keyword) -> Nicho:
        """
        Detecta automaticamente o nicho da keyword.
        
        Args:
            keyword: Keyword para análise
            
        Returns:
            Nicho detectado
        """
        if not self.enable_deteccao_automatica:
            return Nicho.GENERICO
        
        termo = keyword.termo.lower()
        scores_nicho = {}
        
        # Calcula score para cada nicho
        for nicho, palavras in self.palavras_nicho.items():
            score = 0
            for palavra in palavras:
                if palavra in termo:
                    score += 1
            
            if score > 0:
                scores_nicho[nicho] = score
        
        # Retorna nicho com maior score
        if scores_nicho:
            return max(scores_nicho, key=scores_nicho.get)
        else:
            return Nicho.GENERICO
    
    def aplicar_template_adaptativo(
        self,
        keyword: Keyword,
        nicho_especifico: Optional[Nicho] = None,
        fase_funil: Optional[str] = None
    ) -> TemplateResult:
        """
        Aplica template adaptativo para uma keyword.
        
        Args:
            keyword: Keyword para processar
            nicho_especifico: Nicho específico (opcional)
            fase_funil: Fase do funil (opcional)
            
        Returns:
            TemplateResult com resultado da aplicação
        """
        # Detecta nicho se não especificado
        if nicho_especifico is None:
            nicho_especifico = self.detectar_nicho_automatico(keyword)
        
        # Obtém template para o nicho
        template_config = self.templates.get(nicho_especifico, self.templates[Nicho.GENERICO])
        
        # Gera variáveis para o template
        variaveis = self._gerar_variaveis_template(keyword, template_config, fase_funil)
        
        # Aplica template
        prompt_gerado = template_config.template_base.format(**variaveis)
        
        # Calcula score de adequação
        score_adequacao = self._calcular_score_adequacao(keyword, template_config, variaveis)
        
        # Gera justificativa
        justificativa = self._gerar_justificativa_template(
            keyword, template_config, nicho_especifico, score_adequacao
        )
        
        resultado = TemplateResult(
            keyword=keyword,
            template_aplicado=template_config,
            prompt_gerado=prompt_gerado,
            variaveis_utilizadas=variaveis,
            score_adequacao=score_adequacao,
            justificativa=justificativa
        )
        
        # Log do resultado
        if self.enable_logging:
            self._log_aplicacao_template(resultado)
        
        return resultado
    
    def _gerar_variaveis_template(
        self,
        keyword: Keyword,
        template_config: TemplateConfig,
        fase_funil: Optional[str]
    ) -> Dict[str, str]:
        """
        Gera variáveis para preenchimento do template.
        
        Args:
            keyword: Keyword para processar
            template_config: Configuração do template
            fase_funil: Fase do funil
            
        Returns:
            Dicionário com variáveis preenchidas
        """
        termo = keyword.termo
        palavras = termo.split()
        
        # Variáveis básicas
        variaveis = {
            "titulo": termo.title(),
            "keyword": termo,
            "tema_principal": palavras[0] if palavras else "tema",
            "definicao_basica": f"um conceito relacionado a {termo}",
            "explicacao_importancia": f"é fundamental para compreender {termo}",
            "beneficio_principal": f"entender melhor {termo}"
        }
        
        # Adiciona variáveis específicas por nicho
        if template_config.nicho == Nicho.ECOMMERCE:
            variaveis.update({
                "produto_categoria": palavras[-1] if len(palavras) > 1 else "produto",
                "caracteristica_1": "Qualidade",
                "caracteristica_2": "Preço",
                "caracteristica_3": "Durabilidade",
                "descricao_1": "aspecto fundamental para qualquer compra",
                "descricao_2": "fator determinante na decisão",
                "descricao_3": "garantia de longevidade do produto"
            })
        
        elif template_config.nicho == Nicho.SAUDE:
            variaveis.update({
                "sintoma_1": "alterações no comportamento",
                "sintoma_2": "mudanças físicas",
                "sintoma_3": "disconforto persistente",
                "causa_1": "fatores genéticos",
                "causa_2": "condições ambientais",
                "causa_3": "estilo de vida",
                "sinais_alerta": "os sintomas persistirem por mais de uma semana"
            })
        
        elif template_config.nicho == Nicho.TECNOLOGIA:
            variaveis.update({
                "processo_1": "análise inicial",
                "processo_2": "implementação",
                "processo_3": "otimização",
                "vantagem_1": "Eficiência",
                "vantagem_2": "Inovação",
                "vantagem_3": "Escalabilidade",
                "descricao_1": "melhora significativa no desempenho",
                "descricao_2": "soluções inovadoras para problemas complexos",
                "descricao_3": "crescimento sustentável do sistema"
            })
        
        elif template_config.nicho == Nicho.EDUCACAO:
            variaveis.update({
                "publico_alvo": "estudantes e profissionais",
                "fundamento_1": "Teoria Básica",
                "fundamento_2": "Aplicação Prática",
                "fundamento_3": "Desenvolvimento Avançado",
                "explicacao_1": "base teórica essencial",
                "explicacao_2": "implementação real dos conceitos",
                "explicacao_3": "domínio completo da técnica",
                "beneficio_aprendizado": "desenvolver habilidades práticas"
            })
        
        # Adiciona variáveis específicas por fase do funil
        if fase_funil:
            variaveis.update(self._adicionar_variaveis_fase_funil(fase_funil, termo))
        
        return variaveis
    
    def _adicionar_variaveis_fase_funil(self, fase_funil: str, termo: str) -> Dict[str, str]:
        """Adiciona variáveis específicas por fase do funil."""
        variaveis = {}
        
        if fase_funil == "descoberta":
            variaveis.update({
                "abordagem": "introdutória",
                "profundidade": "básica",
                "objetivo": "apresentar o conceito"
            })
        elif fase_funil == "curiosidade":
            variaveis.update({
                "abordagem": "exploratória",
                "profundidade": "intermediária",
                "objetivo": "despertar interesse"
            })
        elif fase_funil == "consideracao":
            variaveis.update({
                "abordagem": "analítica",
                "profundidade": "detalhada",
                "objetivo": "fornecer informações completas"
            })
        elif fase_funil == "comparacao":
            variaveis.update({
                "abordagem": "comparativa",
                "profundidade": "crítica",
                "objetivo": "ajudar na decisão"
            })
        elif fase_funil == "decisao":
            variaveis.update({
                "abordagem": "persuasiva",
                "profundidade": "focada",
                "objetivo": "facilitar a escolha"
            })
        elif fase_funil == "autoridade":
            variaveis.update({
                "abordagem": "especializada",
                "profundidade": "avançada",
                "objetivo": "estabelecer credibilidade"
            })
        
        return variaveis
    
    def _calcular_score_adequacao(
        self,
        keyword: Keyword,
        template_config: TemplateConfig,
        variaveis: Dict[str, str]
    ) -> float:
        """
        Calcula score de adequação do template.
        
        Args:
            keyword: Keyword processada
            template_config: Configuração do template
            variaveis: Variáveis utilizadas
            
        Returns:
            Score de adequação (0-1)
        """
        score = 0.5  # Score base
        
        # Verifica se variáveis obrigatórias foram preenchidas
        variaveis_obrigatorias = template_config.variaveis_obrigatorias
        variaveis_preenchidas = sum(1 for var in variaveis_obrigatorias if var in variaveis)
        
        if variaveis_preenchidas == len(variaveis_obrigatorias):
            score += 0.3
        
        # Verifica adequação do nicho
        nicho_detectado = self.detectar_nicho_automatico(keyword)
        if nicho_detectado == template_config.nicho:
            score += 0.2
        
        # Verifica qualidade das variáveis
        variaveis_qualidade = sum(1 for var in variaveis.values() if len(var) > 10)
        if variaveis_qualidade >= len(variaveis) * 0.7:
            score += 0.1
        
        return min(1.0, score)
    
    def _gerar_justificativa_template(
        self,
        keyword: Keyword,
        template_config: TemplateConfig,
        nicho_detectado: Nicho,
        score_adequacao: float
    ) -> str:
        """Gera justificativa da aplicação do template."""
        if score_adequacao >= 0.8:
            nivel = "excelente"
        elif score_adequacao >= 0.6:
            nivel = "boa"
        else:
            nivel = "adequada"
        
        return f"Template {template_config.nome} aplicado com adequação {nivel} ({score_adequacao:.1%}) para nicho {nicho_detectado.value}"
    
    def _log_aplicacao_template(self, resultado: TemplateResult) -> None:
        """Registra log da aplicação do template."""
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "template_adaptativo_aplicado",
            "status": "success",
            "source": "templates_adaptativos._log_aplicacao_template",
            "details": {
                "keyword": resultado.keyword.termo,
                "template": resultado.template_aplicado.nome,
                "nicho": resultado.template_aplicado.nicho.value,
                "score_adequacao": resultado.score_adequacao,
                "variaveis_utilizadas": len(resultado.variaveis_utilizadas),
                "tamanho_prompt": len(resultado.prompt_gerado)
            }
        })
    
    def aplicar_templates_lote(
        self,
        keywords: List[Keyword],
        nicho_especifico: Optional[Nicho] = None
    ) -> List[TemplateResult]:
        """
        Aplica templates adaptativos para uma lista de keywords.
        
        Args:
            keywords: Lista de keywords para processar
            nicho_especifico: Nicho específico (opcional)
            
        Returns:
            Lista de TemplateResult
        """
        resultados = []
        
        for keyword in keywords:
            resultado = self.aplicar_template_adaptativo(
                keyword, nicho_especifico, keyword.fase_funil
            )
            resultados.append(resultado)
        
        # Log do lote
        if self.enable_logging:
            self._log_lote_templates(resultados)
        
        return resultados
    
    def _log_lote_templates(self, resultados: List[TemplateResult]) -> None:
        """Registra log do processamento em lote."""
        if not resultados:
            return
        
        # Estatísticas do lote
        nichos_utilizados = {}
        scores_adequacao = [r.score_adequacao for r in resultados]
        
        for resultado in resultados:
            nicho = resultado.template_aplicado.nicho.value
            if nicho not in nichos_utilizados:
                nichos_utilizados[nicho] = 0
            nichos_utilizados[nicho] += 1
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "lote_templates_processado",
            "status": "success",
            "source": "templates_adaptativos._log_lote_templates",
            "details": {
                "total_keywords": len(resultados),
                "nichos_utilizados": nichos_utilizados,
                "score_adequacao_medio": round(sum(scores_adequacao) / len(scores_adequacao), 3),
                "score_adequacao_min": round(min(scores_adequacao), 3),
                "score_adequacao_max": round(max(scores_adequacao), 3)
            }
        })
    
    def validar_qualidade_templates(
        self,
        resultados: List[TemplateResult]
    ) -> Dict[str, Any]:
        """
        Valida a qualidade dos templates aplicados.
        
        Args:
            resultados: Lista de resultados para validar
            
        Returns:
            Dicionário com métricas de qualidade
        """
        if not resultados:
            return {"status": "empty", "message": "Nenhum resultado para validar"}
        
        scores = [r.score_adequacao for r in resultados]
        
        # Calcula métricas de qualidade
        qualidade = {
            "total_keywords": len(resultados),
            "score_adequacao_medio": round(sum(scores) / len(scores), 3),
            "score_adequacao_mediana": round(sorted(scores)[len(scores)//2], 3),
            "score_adequacao_min": round(min(scores), 3),
            "score_adequacao_max": round(max(scores), 3),
            "distribuicao_adequacao": {
                "excelente": len([string_data for string_data in scores if string_data >= 0.8]),
                "boa": len([string_data for string_data in scores if 0.6 <= string_data < 0.8]),
                "adequada": len([string_data for string_data in scores if string_data < 0.6])
            },
            "nichos_utilizados": {}
        }
        
        # Estatísticas por nicho
        for resultado in resultados:
            nicho = resultado.template_aplicado.nicho.value
            if nicho not in qualidade["nichos_utilizados"]:
                qualidade["nichos_utilizados"][nicho] = 0
            qualidade["nichos_utilizados"][nicho] += 1
        
        # Determina status geral
        if qualidade["score_adequacao_medio"] >= 0.7:
            qualidade["status"] = "excelente"
        elif qualidade["score_adequacao_medio"] >= 0.5:
            qualidade["status"] = "bom"
        else:
            qualidade["status"] = "precisa_melhoria"
        
        return qualidade

# Função de conveniência para uso direto
def aplicar_templates_adaptativos(
    keywords: List[Keyword],
    nicho_especifico: Optional[Nicho] = None,
    enable_deteccao_automatica: bool = True
) -> List[TemplateResult]:
    """
    Função de conveniência para aplicação de templates adaptativos.
    
    Args:
        keywords: Lista de keywords para processar
        nicho_especifico: Nicho específico (opcional)
        enable_deteccao_automatica: Se True, detecta nicho automaticamente
        
    Returns:
        Lista de TemplateResult
    """
    adaptador = TemplatesAdaptativos(enable_deteccao_automatica=enable_deteccao_automatica)
    return adaptador.aplicar_templates_lote(keywords, nicho_especifico) 