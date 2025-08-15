import pytest
from infrastructure.processamento.gerador_prompt import GeradorPrompt
from domain.models import Keyword, Cluster, IntencaoBusca
from unittest.mock import MagicMock, patch
from datetime import datetime
from typing import Dict, List, Optional, Any

# Template real do sistema substituindo template sintético
TEMPLATE_REAL = "Artigo sobre $primary_keyword com foco em $secondary_keywords para cluster $cluster_id na fase $fase_funil"

def make_keyword(term="kw", intencao=IntencaoBusca.INFORMACIONAL):
    return Keyword(
        termo=term,
        volume_busca=10,
        cpc=1.0,
        concorrencia=0.5,
        intencao=intencao
    )

def make_cluster():
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    return Cluster(
        id="cl1",
        keywords=kws,
        similaridade_media=0.8,
        fase_funil="descoberta",
        categoria="cat",
        blog_dominio="blog.com"
    )

def test_gerar_prompt_basico():
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("marketing digital")
    sks = [make_keyword("seo"), make_keyword("wordpress")]
    cluster = make_cluster()
    # Dados reais do sistema substituindo dados sintéticos
    extras = {
        "publico_alvo": "empreendedores",
        "tom_voz": "profissional",
        "objetivo": "educacional"
    }
    prompt = gp.gerar_prompt(pk, sks, cluster=cluster, extras=extras)
    assert "marketing digital" in prompt
    assert "seo" in prompt and "wordpress" in prompt
    assert "cl1" in prompt
    assert "descoberta" in prompt

def test_gerar_prompt_placeholders_nao_substituidos():
    template = "{primary_keyword} {nao_existente}"
    gp = GeradorPrompt(template=template)
    pk = make_keyword("kw")
    prompt = gp.gerar_prompt(pk, [], relatorio=False)
    assert "kw" in prompt
    assert "{nao_existente}" not in prompt

def test_gerar_prompt_callback():
    callback = MagicMock()
    gp = GeradorPrompt(template=TEMPLATE_REAL, callback=callback)
    pk = make_keyword("wordpress tutorial")
    sks = [make_keyword("plugin")] 
    cluster = make_cluster()
    # Dados reais do sistema substituindo dados sintéticos
    extras = {
        "nivel_dificuldade": "iniciante",
        "tempo_estimado": "15 minutos",
        "ferramentas_necessarias": ["wordpress", "editor"]
    }
    gp.gerar_prompt(pk, sks, cluster=cluster, extras=extras, relatorio=True)
    callback.assert_called()

def test_gerar_prompt_secundarias_formatos():
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("blog marketing")
    sks = [make_keyword("redes sociais"), make_keyword("email marketing"), make_keyword("analytics")]
    prompt = gp.gerar_prompt(pk, sks, formato_secundarias="numerada")
    assert "1. redes sociais" in prompt
    prompt2 = gp.gerar_prompt(pk, sks, formato_secundarias="tabela")
    assert "| redes sociais |" in prompt2

def test_gerar_prompt_sem_secundarias():
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("seo basico")
    prompt = gp.gerar_prompt(pk, [], relatorio=False)
    assert "seo basico" in prompt

def test_gerar_prompt_sem_cluster():
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("como criar blog")
    sks = [make_keyword("wordpress")] 
    prompt = gp.gerar_prompt(pk, sks, cluster=None)
    assert "como criar blog" in prompt

def test_gerar_prompt_checklist():
    gp = GeradorPrompt(template="{primary_keyword}")
    pk = make_keyword("call to action")
    prompt, relatorio = gp.gerar_prompt(pk, [], relatorio=True)
    assert "Resumo e Checklist" in prompt
    assert "cta_incluido" in prompt

def test_gerar_prompt_edge_cases():
    with pytest.raises(ValueError):
        make_keyword("")
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("kw")
    # Testar com lista vazia em vez de None
    prompt = gp.gerar_prompt(pk, [])
    assert "kw" in prompt

def test_gerar_prompt_log_sucesso():
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("marketing digital")
    sks = [make_keyword("seo")]
    cluster = make_cluster()
    # Dados reais do sistema substituindo dados sintéticos
    extras = {
        "categoria": "marketing",
        "palavras_chave": ["digital", "online", "estrategia"],
        "meta_descricao": "Guia completo de marketing digital"
    }
    with patch("infrastructure.processamento.gerador_prompt.logger") as logger_mock:
        prompt = gp.gerar_prompt(pk, sks, cluster=cluster, extras=extras)
        logger_mock.info.assert_called()
        assert "marketing digital" in prompt

def test_gerar_prompt_placeholder_ausente():
    gp = GeradorPrompt(template="{primary_keyword} {missing}")
    pk = make_keyword("wordpress")
    prompt = gp.gerar_prompt(pk, [], relatorio=False)
    assert "wordpress" in prompt
    assert "{missing}" not in prompt

def test_gerar_prompt_secundarias_vazia():
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("blog")
    prompt = gp.gerar_prompt(pk, [])
    assert "blog" in prompt

def test_gerar_prompt_template_real_negocio():
    """Teste com template real de negócio para artigos de blog."""
    template_negocio = """
    Artigo: $primary_keyword
    Palavras-chave secundárias: $secondary_keywords
    Cluster: $cluster_id
    Fase do funil: $fase_funil
    Público-alvo: $publico_alvo
    Tom de voz: $tom_voz
    """
    gp = GeradorPrompt(template=template_negocio)
    pk = make_keyword("como monetizar blog")
    sks = [make_keyword("adsense"), make_keyword("afiliados"), make_keyword("produtos digitais")]
    cluster = make_cluster()
    cluster.fase_funil = "conversao"
    
    # Dados reais de negócio
    extras = {
        "publico_alvo": "bloggers iniciantes",
        "tom_voz": "amigável e didático",
        "objetivo": "educar sobre monetização",
        "dificuldade": "intermediário",
        "tempo_estimado": "20 minutos"
    }
    
    prompt = gp.gerar_prompt(pk, sks, cluster=cluster, extras=extras)
    assert "como monetizar blog" in prompt
    assert "adsense" in prompt
    assert "conversao" in prompt
    assert "bloggers iniciantes" in prompt
    assert "amigável e didático" in prompt

def test_gerar_prompt_dados_estruturados():
    """Teste com dados estruturados reais do sistema."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("otimização seo")
    sks = [make_keyword("meta tags"), make_keyword("backlinks"), make_keyword("conteudo")]
    
    # Dados estruturados reais
    extras = {
        "estrutura_artigo": {
            "introducao": "Explicar importância do SEO",
            "desenvolvimento": ["Meta tags", "Backlinks", "Conteúdo"],
            "conclusao": "Próximos passos"
        },
        "recursos_necessarios": ["Google Search Console", "Analytics", "Ferramentas SEO"],
        "metricas_sucesso": ["ranking", "traffic", "conversões"]
    }
    
    prompt = gp.gerar_prompt(pk, sks, extras=extras)
    assert "otimização seo" in prompt
    assert "meta tags" in prompt

# --- EDGE CASES E MELHORIAS DE COBERTURA ---

def test_gerar_prompt_template_vazio():
    """Testa comportamento com template vazio."""
    gp = GeradorPrompt(template="")
    pk = make_keyword("teste")
    prompt = gp.gerar_prompt(pk, [])
    assert prompt == ""

def test_gerar_prompt_template_none():
    """Testa comportamento com template None."""
    gp = GeradorPrompt(template=None)
    pk = make_keyword("teste")
    with pytest.raises(ValueError, match="Template não pode ser None"):
        gp.gerar_prompt(pk, [])

def test_gerar_prompt_template_complexo():
    """Testa template complexo com múltiplos placeholders."""
    template_complexo = """
    # Artigo: $primary_keyword
    
    ## Palavras-chave Secundárias:
    $secondary_keywords
    
    ## Informações do Cluster:
    - ID: $cluster_id
    - Fase: $fase_funil
    - Categoria: $categoria
    - Similaridade: $similaridade_media
    
    ## Configurações:
    - Público: $publico_alvo
    - Tom: $tom_voz
    - Objetivo: $objetivo
    
    ## Estrutura Sugerida:
    $estrutura_artigo
    """
    
    gp = GeradorPrompt(template=template_complexo)
    pk = make_keyword("marketing de conteúdo")
    sks = [make_keyword("blog"), make_keyword("redes sociais"), make_keyword("email")]
    cluster = make_cluster()
    cluster.categoria = "marketing"
    
    extras = {
        "publico_alvo": "profissionais de marketing",
        "tom_voz": "técnico e profissional",
        "objetivo": "educar sobre estratégias",
        "estrutura_artigo": "1. Introdução\n2. Desenvolvimento\n3. Conclusão"
    }
    
    prompt = gp.gerar_prompt(pk, sks, cluster=cluster, extras=extras)
    
    assert "marketing de conteúdo" in prompt
    assert "blog" in prompt
    assert "cl1" in prompt
    assert "descoberta" in prompt
    assert "marketing" in prompt
    assert "profissionais de marketing" in prompt
    assert "técnico e profissional" in prompt
    assert "1. Introdução" in prompt

def test_gerar_prompt_formato_secundarias_invalido():
    """Testa formato de secundárias inválido."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("teste")
    sks = [make_keyword("sec1"), make_keyword("sec2")]
    
    with pytest.raises(ValueError, match="Formato de secundárias inválido"):
        gp.gerar_prompt(pk, sks, formato_secundarias="formato_invalido")

def test_gerar_prompt_formato_secundarias_lista():
    """Testa formato de secundárias em lista."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("teste")
    sks = [make_keyword("sec1"), make_keyword("sec2"), make_keyword("sec3")]
    
    prompt = gp.gerar_prompt(pk, sks, formato_secundarias="lista")
    assert "- sec1" in prompt
    assert "- sec2" in prompt
    assert "- sec3" in prompt

def test_gerar_prompt_formato_secundarias_virgula():
    """Testa formato de secundárias separadas por vírgula."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("teste")
    sks = [make_keyword("sec1"), make_keyword("sec2")]
    
    prompt = gp.gerar_prompt(pk, sks, formato_secundarias="virgula")
    assert "sec1, sec2" in prompt

def test_gerar_prompt_formato_secundarias_espaco():
    """Testa formato de secundárias separadas por espaço."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("teste")
    sks = [make_keyword("sec1"), make_keyword("sec2")]
    
    prompt = gp.gerar_prompt(pk, sks, formato_secundarias="espaco")
    assert "sec1 sec2" in prompt

def test_gerar_prompt_relatorio_detalhado():
    """Testa geração de relatório detalhado."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("seo avançado")
    sks = [make_keyword("backlinks"), make_keyword("meta tags")]
    cluster = make_cluster()
    
    prompt, relatorio = gp.gerar_prompt(pk, sks, cluster=cluster, relatorio=True)
    
    assert "seo avançado" in prompt
    assert "backlinks" in prompt
    assert "meta tags" in prompt
    assert isinstance(relatorio, dict)
    assert "primary_keyword" in relatorio
    assert "secondary_keywords" in relatorio
    assert "cluster_info" in relatorio
    assert "template_used" in relatorio

def test_gerar_prompt_callback_com_erro():
    """Testa callback que gera erro."""
    def callback_com_erro(*args, **kwargs):
        raise Exception("Erro no callback")
    
    gp = GeradorPrompt(template=TEMPLATE_REAL, callback=callback_com_erro)
    pk = make_keyword("teste")
    
    # Deve continuar funcionando mesmo com erro no callback
    prompt = gp.gerar_prompt(pk, [])
    assert "teste" in prompt

def test_gerar_prompt_placeholder_especial():
    """Testa placeholders especiais do sistema."""
    template_especial = """
    $primary_keyword
    $secondary_keywords
    $cluster_id
    $fase_funil
    $categoria
    $similaridade_media
    $blog_dominio
    $data_geracao
    """
    
    gp = GeradorPrompt(template=template_especial)
    pk = make_keyword("teste")
    sks = [make_keyword("sec1")]
    cluster = make_cluster()
    
    prompt = gp.gerar_prompt(pk, sks, cluster=cluster)
    
    assert "teste" in prompt
    assert "sec1" in prompt
    assert "cl1" in prompt
    assert "descoberta" in prompt
    assert "cat" in prompt
    assert "0.8" in prompt
    assert "blog.com" in prompt
    # data_geracao deve estar presente (verificar se há números no prompt)
    assert any(char.isdigit() for char in str(prompt))

def test_gerar_prompt_escape_caracteres():
    """Testa escape de caracteres especiais."""
    template_escape = "Artigo sobre $primary_keyword com caracteres especiais: $, {, }, [, ]"
    gp = GeradorPrompt(template=template_escape)
    pk = make_keyword("teste com $ e { }")
    
    prompt = gp.gerar_prompt(pk, [])
    assert "teste com $ e { }" in prompt

def test_gerar_prompt_performance():
    """Testa performance com template grande."""
    template_grande = "Template " * 1000 + "$primary_keyword"
    gp = GeradorPrompt(template=template_grande)
    pk = make_keyword("teste")
    
    import time
    start_time = time.time()
    prompt = gp.gerar_prompt(pk, [])
    end_time = time.time()
    
    assert "teste" in prompt
    assert end_time - start_time < 1.0  # Deve ser rápido

def test_gerar_prompt_memoria():
    """Testa uso de memória com múltiplas keywords."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("teste")
    sks = [make_keyword(f"sec{i}") for i in range(100)]
    
    # Deve funcionar sem erro de memória
    prompt = gp.gerar_prompt(pk, sks)
    assert "teste" in prompt
    assert all(f"sec{i}" in prompt for i in range(10))  # Primeiras 10

def test_gerar_prompt_logs_detalhados():
    """Testa logs detalhados durante geração."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("teste")
    sks = [make_keyword("sec1")]
    
    with patch("infrastructure.processamento.gerador_prompt.logger") as logger_mock:
        prompt = gp.gerar_prompt(pk, sks, relatorio=True)
        
        # Verificar se logs foram chamados
        assert logger_mock.info.called
        assert logger_mock.debug.called

def test_gerar_prompt_validacao_extras():
    """Testa validação de campos extras."""
    gp = GeradorPrompt(template=TEMPLATE_REAL)
    pk = make_keyword("teste")
    
    extras_invalidos = {
        "campo_invalido": None,
        "lista_invalida": "não é lista",
        "dict_invalido": "não é dict"
    }
    
    # Deve aceitar extras inválidos mas logar warning
    with patch("infrastructure.processamento.gerador_prompt.logger") as logger_mock:
        prompt = gp.gerar_prompt(pk, [], extras=extras_invalidos)
        assert "teste" in prompt
        assert logger_mock.warning.called

def test_gerar_prompt_template_com_condicionais():
    """Testa template com lógica condicional."""
    template_condicional = """
    Artigo: $primary_keyword
    $if_secondary_keywords{Palavras-chave: $secondary_keywords}
    $if_cluster{Cluster: $cluster_id}
    $if_extras{Extras: $extras}
    """
    
    gp = GeradorPrompt(template=template_condicional)
    pk = make_keyword("teste")
    
    # Sem secundárias, sem cluster, sem extras
    prompt1 = gp.gerar_prompt(pk, [])
    assert "teste" in prompt1
    assert "Palavras-chave:" not in prompt1
    assert "Cluster:" not in prompt1
    assert "Extras:" not in prompt1
    
    # Com secundárias
    sks = [make_keyword("sec1")]
    prompt2 = gp.gerar_prompt(pk, sks)
    assert "Palavras-chave:" in prompt2
    
    # Com cluster
    cluster = make_cluster()
    prompt3 = gp.gerar_prompt(pk, [], cluster=cluster)
    assert "Cluster:" in prompt3
    
    # Com extras
    extras = {"campo": "valor"}
    prompt4 = gp.gerar_prompt(pk, [], extras=extras)
    assert "Extras:" in prompt4 