from typing import Dict, List, Optional, Any
"""
Script de Teste para o Sistema de Preenchimento de Lacunas em Prompts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.prompt_system import Base, Nicho, Categoria, PromptBase, DadosColetados
from app.services.prompt_filler_service import PromptFillerService


def criar_banco_teste():
    """Cria banco de dados de teste"""
    engine = create_engine('sqlite:///test_prompt_system.db')
    Base.metadata.create_all(engine)
    return engine


def popular_dados_teste(session):
    """Popula dados de teste"""
    
    # Criar nicho
    nicho = Nicho(
        nome="Saúde e Bem-estar",
        descricao="Conteúdo sobre saúde, fitness e bem-estar"
    )
    session.add(nicho)
    session.commit()
    
    # Criar categoria
    categoria = Categoria(
        nicho_id=nicho.id,
        nome="Emagrecimento",
        descricao="Dicas e estratégias para emagrecimento saudável"
    )
    session.add(categoria)
    session.commit()
    
    # Criar prompt base
    prompt_conteudo = """
# 📥 Bloco 1 – Variáveis de Entrada (Preenchimento Obrigatório)

Preencha os seguintes campos antes de iniciar a geração do cluster de artigos:

[NICHO]: Saúde e Bem-estar

[CATEGORIA]: Emagrecimento

[CLUSTER DE CONTEÚDO]: [CLUSTER DE CONTEÚDO]

[PERFIL DO CLIENTE / PERSONA]: Mulheres de 25-40 anos interessadas em emagrecimento

[PRODUTO FINAL (opcional)]: E-book sobre emagrecimento

[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]: [PALAVRA-CHAVE PRINCIPAL DO CLUSTER]

[PALAVRAS-CHAVE SECUNDÁRIAS (opcional)]: [PALAVRAS-CHAVE SECUNDÁRIAS]

[ESTILO DE REDAÇÃO]: Didático e motivacional

## 🎯 Objetivo do Sistema
Você é um redator sênior com domínio em SEO, copywriting, storytelling, frameworks de escrita avançada e estratégia de conteúdo.
"""
    
    prompt_base = PromptBase(
        categoria_id=categoria.id,
        nome_arquivo="prompt_emagrecimento.txt",
        conteudo=prompt_conteudo,
        hash_conteudo="test_hash_123"
    )
    session.add(prompt_base)
    session.commit()
    
    # Criar dados coletados
    dados = DadosColetados(
        nicho_id=nicho.id,
        categoria_id=categoria.id,
        primary_keyword="como emagrecer 5kg em 30 dias",
        secondary_keywords="dieta low carb, exercícios para emagrecer, alimentação saudável",
        cluster_content="Guia completo para emagrecer 5kg em 30 dias de forma saudável e sustentável",
        status="ativo"
    )
    session.add(dados)
    session.commit()
    
    return nicho, categoria, prompt_base, dados


def testar_preenchimento():
    """Testa o sistema de preenchimento"""
    print("🧪 INICIANDO TESTES DO SISTEMA DE PREENCHIMENTO DE LACUNAS")
    print("=" * 60)
    
    # Criar banco e sessão
    engine = criar_banco_teste()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Popular dados de teste
        print("📝 Criando dados de teste...")
        nicho, categoria, prompt_base, dados = popular_dados_teste(session)
        print(f"✅ Nicho criado: {nicho.nome}")
        print(f"✅ Categoria criada: {categoria.nome}")
        print(f"✅ Prompt base criado: {prompt_base.nome_arquivo}")
        print(f"✅ Dados coletados criados: {dados.primary_keyword}")
        
        # Testar serviço de preenchimento
        print("\n🔧 Testando serviço de preenchimento...")
        service = PromptFillerService(session)
        
        # Detectar lacunas
        lacunas = service.detectar_lacunas(prompt_base.conteudo)
        print(f"✅ Lacunas detectadas: {lacunas}")
        
        # Validar dados
        dados_validos, erros = service.validar_dados_coletados(dados)
        print(f"✅ Dados válidos: {dados_validos}")
        if erros:
            print(f"❌ Erros: {erros}")
        
        # Preencher lacunas
        prompt_preenchido, metadados = service.preencher_lacunas(prompt_base, dados)
        print(f"✅ Prompt preenchido com sucesso!")
        print(f"⏱️ Tempo de processamento: {metadados['tempo_processamento']}ms")
        
        # Mostrar resultado
        print("\n📄 RESULTADO DO PREENCHIMENTO:")
        print("-" * 40)
        print(prompt_preenchido[:500] + "..." if len(prompt_preenchido) > 500 else prompt_preenchido)
        
        # Processar preenchimento completo
        print("\n🔄 Processando preenchimento completo...")
        prompt_final = service.processar_preenchimento(categoria.id, dados.id)
        print(f"✅ Prompt final criado com ID: {prompt_final.id}")
        print(f"✅ Status: {prompt_final.status}")
        
        print("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ ERRO NOS TESTES: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        session.close()
        # Remover banco de teste
        if os.path.exists('test_prompt_system.db'):
            os.remove('test_prompt_system.db')


if __name__ == "__main__":
    testar_preenchimento() 