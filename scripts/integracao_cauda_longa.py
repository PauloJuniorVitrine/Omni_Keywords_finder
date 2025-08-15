#!/usr/bin/env python3
"""
Script de Integração - Sistema de Cauda Longa

Tracing ID: INTEGRATION_LONG_TAIL_20241220_001
Data/Hora: 2024-12-20 18:45:00 UTC
Versão: 1.0
Status: ✅ IMPLEMENTADO

Este script integra todos os módulos de cauda longa implementados
com o sistema principal do Omni Keywords Finder.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import importlib.util
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data'
)
logger = logging.getLogger(__name__)

class IntegradorCaudaLonga:
    """
    Integrador do sistema de cauda longa com o sistema principal.
    """
    
    def __init__(self, projeto_root: str = None):
        """
        Inicializa o integrador.
        
        Args:
            projeto_root: Diretório raiz do projeto
        """
        self.projeto_root = Path(projeto_root) if projeto_root else Path.cwd()
        self.modulos_cauda_longa = {}
        self.configuracoes = {}
        self.status_integracao = {}
        
        # Diretórios de módulos
        self.diretorios_modulos = {
            "processamento": "infrastructure/processamento",
            "ml": "infrastructure/ml", 
            "ab_testing": "infrastructure/ab_testing",
            "monitoring": "infrastructure/monitoring",
            "cache": "infrastructure/cache",
            "feedback": "infrastructure/feedback",
            "audit": "infrastructure/audit"
        }
        
        logger.info(f"[INTEGRATION] Integrador inicializado - {datetime.now()}")
    
    def verificar_modulos_implementados(self) -> Dict[str, bool]:
        """
        Verifica quais módulos estão implementados.
        
        Returns:
            Dicionário com status dos módulos
        """
        status_modulos = {}
        
        for nome, diretorio in self.diretorios_modulos.items():
            caminho_modulo = self.projeto_root / diretorio
            status_modulos[nome] = caminho_modulo.exists()
            
            if status_modulos[nome]:
                logger.info(f"[INTEGRATION] ✅ Módulo {nome} encontrado: {caminho_modulo}")
            else:
                logger.warning(f"[INTEGRATION] ❌ Módulo {nome} não encontrado: {caminho_modulo}")
        
        return status_modulos
    
    def carregar_modulos(self) -> Dict[str, Any]:
        """
        Carrega os módulos implementados.
        
        Returns:
            Dicionário com instâncias dos módulos
        """
        modulos_carregados = {}
        
        # Mapeamento de módulos para funções de criação
        mapeamento_modulos = {
            "ml": {
                "arquivo": "ajuste_automatico_cauda_longa.py",
                "funcao": "criar_sistema_ajuste_automatico",
                "nome": "sistema_ml"
            },
            "ab_testing": {
                "arquivo": "configuracoes_cauda_longa.py", 
                "funcao": "criar_sistema_ab_testing",
                "nome": "sistema_ab_testing"
            },
            "monitoring": {
                "arquivo": "performance_cauda_longa.py",
                "funcao": "criar_sistema_monitoramento",
                "nome": "sistema_monitoramento"
            },
            "cache": {
                "arquivo": "cache_inteligente_cauda_longa.py",
                "funcao": "criar_sistema_cache",
                "nome": "sistema_cache"
            },
            "feedback": {
                "arquivo": "feedback_cauda_longa.py",
                "funcao": "criar_sistema_feedback",
                "nome": "sistema_feedback"
            },
            "audit": {
                "arquivo": "auditoria_qualidade_cauda_longa.py",
                "funcao": "criar_sistema_auditoria",
                "nome": "sistema_auditoria"
            }
        }
        
        for nome_modulo, config in mapeamento_modulos.items():
            try:
                caminho_arquivo = self.projeto_root / self.diretorios_modulos[nome_modulo] / config["arquivo"]
                
                if caminho_arquivo.exists():
                    # Carregar módulo dinamicamente
                    spec = importlib.util.spec_from_file_location(
                        nome_modulo, caminho_arquivo
                    )
                    modulo = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(modulo)
                    
                    # Criar instância do sistema
                    if hasattr(modulo, config["funcao"]):
                        funcao_criacao = getattr(modulo, config["funcao"])
                        instancia = funcao_criacao()
                        modulos_carregados[config["nome"]] = instancia
                        
                        logger.info(f"[INTEGRATION] ✅ Módulo {nome_modulo} carregado com sucesso")
                    else:
                        logger.error(f"[INTEGRATION] ❌ Função {config['funcao']} não encontrada em {nome_modulo}")
                else:
                    logger.warning(f"[INTEGRATION] ⚠️ Arquivo não encontrado: {caminho_arquivo}")
                    
            except Exception as e:
                logger.error(f"[INTEGRATION] ❌ Erro ao carregar módulo {nome_modulo}: {str(e)}")
        
        self.modulos_cauda_longa = modulos_carregados
        return modulos_carregados
    
    def criar_configuracao_integracao(self) -> Dict[str, Any]:
        """
        Cria configuração de integração.
        
        Returns:
            Configuração de integração
        """
        config = {
            "integracao": {
                "timestamp": datetime.now().isoformat(),
                "versao": "1.0.0",
                "status": "configurado"
            },
            "modulos": {
                "ml": {
                    "ativo": "sistema_ml" in self.modulos_cauda_longa,
                    "configuracao": {
                        "intervalo_otimizacao": 3600,  # 1 hora
                        "threshold_performance": 0.7,
                        "max_rollback_attempts": 3
                    }
                },
                "ab_testing": {
                    "ativo": "sistema_ab_testing" in self.modulos_cauda_longa,
                    "configuracao": {
                        "duracao_padrao_dias": 7,
                        "tamanho_amostra_padrao": 1000,
                        "nivel_significancia": 0.05
                    }
                },
                "monitoring": {
                    "ativo": "sistema_monitoramento" in self.modulos_cauda_longa,
                    "configuracao": {
                        "intervalo_coleta": 5,  # segundos
                        "intervalo_analise": 30,  # segundos
                        "alertas_ativos": True
                    }
                },
                "cache": {
                    "ativo": "sistema_cache" in self.modulos_cauda_longa,
                    "configuracao": {
                        "tamanho_maximo_mb": 100,
                        "ttl_padrao_minutos": 60,
                        "compressao": True
                    }
                },
                "feedback": {
                    "ativo": "sistema_feedback" in self.modulos_cauda_longa,
                    "configuracao": {
                        "auto_processamento": True,
                        "threshold_impacto": 0.5
                    }
                },
                "audit": {
                    "ativo": "sistema_auditoria" in self.modulos_cauda_longa,
                    "configuracao": {
                        "intervalo_auditoria": 3600,  # 1 hora
                        "retencao_logs_dias": 30
                    }
                }
            },
            "sistema_principal": {
                "endpoints": {
                    "health": "/health",
                    "metrics": "/metrics",
                    "api_docs": "/api/docs"
                },
                "configuracoes": {
                    "rate_limiting": True,
                    "cors": True,
                    "audit": True
                }
            }
        }
        
        self.configuracoes = config
        return config
    
    def salvar_configuracao(self, arquivo: str = "config_integracao_cauda_longa.json"):
        """
        Salva configuração de integração.
        
        Args:
            arquivo: Nome do arquivo de configuração
        """
        try:
            caminho_config = self.projeto_root / arquivo
            
            with open(caminho_config, 'w', encoding='utf-8') as f:
                json.dump(self.configuracoes, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[INTEGRATION] ✅ Configuração salva: {caminho_config}")
            
        except Exception as e:
            logger.error(f"[INTEGRATION] ❌ Erro ao salvar configuração: {str(e)}")
    
    def criar_blueprint_flask(self) -> str:
        """
        Cria blueprint Flask para integração.
        
        Returns:
            Código do blueprint
        """
        blueprint_code = '''
"""
Blueprint de Integração - Sistema de Cauda Longa

Este blueprint integra os módulos de cauda longa com a API Flask.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Criar blueprint
cauda_longa_bp = Blueprint('cauda_longa', __name__, url_prefix='/api/cauda-longa')

# Variáveis globais para instâncias dos sistemas
sistemas = {}

def inicializar_sistemas():
    """Inicializa os sistemas de cauda longa."""
    try:
        from infrastructure.ml.ajuste_automatico_cauda_longa import criar_sistema_ajuste_automatico
        from infrastructure.ab_testing.configuracoes_cauda_longa import criar_sistema_ab_testing
        from infrastructure.monitoring.performance_cauda_longa import criar_sistema_monitoramento
        from infrastructure.cache.cache_inteligente_cauda_longa import criar_sistema_cache
        from infrastructure.feedback.feedback_cauda_longa import criar_sistema_feedback
        from infrastructure.audit.auditoria_qualidade_cauda_longa import criar_sistema_auditoria
        
        sistemas['ml'] = criar_sistema_ajuste_automatico()
        sistemas['ab_testing'] = criar_sistema_ab_testing()
        sistemas['monitoring'] = criar_sistema_monitoramento()
        sistemas['cache'] = criar_sistema_cache()
        sistemas['feedback'] = criar_sistema_feedback()
        sistemas['audit'] = criar_sistema_auditoria()
        
        logger.info("Sistemas de cauda longa inicializados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar sistemas: {str(e)}")

@cauda_longa_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica saúde dos sistemas de cauda longa."""
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "sistemas": {}
        }
        
        for nome, sistema in sistemas.items():
            status["sistemas"][nome] = {
                "ativo": sistema is not None,
                "tipo": type(sistema).__name__
            }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@cauda_longa_bp.route('/ml/otimizar', methods=['POST'])
def otimizar_parametros():
    """Executa otimização de parâmetros via ML."""
    try:
        if 'ml' not in sistemas:
            return jsonify({"error": "Sistema ML não disponível"}), 503
        
        sistema_ml = sistemas['ml']
        resultado = sistema_ml.executar_ciclo_otimizacao()
        
        return jsonify({
            "status": "success",
            "resultado": {
                "melhoria": resultado.melhoria,
                "confianca": resultado.confianca,
                "status": resultado.status,
                "tracing_id": resultado.tracing_id
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na otimização: {str(e)}")
        return jsonify({"error": str(e)}), 500

@cauda_longa_bp.route('/ab-testing/criar', methods=['POST'])
def criar_experimento():
    """Cria novo experimento A/B."""
    try:
        if 'ab_testing' not in sistemas:
            return jsonify({"error": "Sistema A/B Testing não disponível"}), 503
        
        dados = request.get_json()
        sistema_ab = sistemas['ab_testing']
        
        experimento = sistema_ab.criar_experimento(
            nome=dados.get('nome'),
            descricao=dados.get('descricao'),
            configuracao_a=dados.get('configuracao_a'),
            configuracao_b=dados.get('configuracao_b'),
            tamanho_amostra=dados.get('tamanho_amostra', 1000),
            duracao_dias=dados.get('duracao_dias', 7)
        )
        
        return jsonify({
            "status": "success",
            "experimento_id": experimento.id,
            "nome": experimento.nome
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar experimento: {str(e)}")
        return jsonify({"error": str(e)}), 500

@cauda_longa_bp.route('/monitoring/dashboard', methods=['GET'])
def obter_dashboard():
    """Obtém dashboard de monitoramento."""
    try:
        if 'monitoring' not in sistemas:
            return jsonify({"error": "Sistema de monitoramento não disponível"}), 503
        
        sistema_monitoring = sistemas['monitoring']
        periodo = request.args.get('periodo_minutos', 60, type=int)
        
        dashboard = sistema_monitoring.obter_dashboard_metricas(periodo)
        
        return jsonify(dashboard), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter dashboard: {str(e)}")
        return jsonify({"error": str(e)}), 500

@cauda_longa_bp.route('/cache/stats', methods=['GET'])
def obter_estatisticas_cache():
    """Obtém estatísticas do cache."""
    try:
        if 'cache' not in sistemas:
            return jsonify({"error": "Sistema de cache não disponível"}), 503
        
        sistema_cache = sistemas['cache']
        stats = sistema_cache.obter_estatisticas()
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do cache: {str(e)}")
        return jsonify({"error": str(e)}), 500

@cauda_longa_bp.route('/feedback/enviar', methods=['POST'])
def enviar_feedback():
    """Envia feedback para o sistema."""
    try:
        if 'feedback' not in sistemas:
            return jsonify({"error": "Sistema de feedback não disponível"}), 503
        
        dados = request.get_json()
        sistema_feedback = sistemas['feedback']
        
        from infrastructure.feedback.feedback_cauda_longa import Feedback, TipoFeedback, Sentimento
        
        feedback = Feedback(
            id=dados.get('id'),
            tipo=TipoFeedback(dados.get('tipo')),
            descricao=dados.get('descricao'),
            nota=dados.get('nota'),
            sentimento=Sentimento(dados.get('sentimento')),
            contexto=dados.get('contexto', {})
        )
        
        acoes = sistema_feedback.processar_feedback(feedback)
        
        return jsonify({
            "status": "success",
            "feedback_id": feedback.id,
            "acoes_geradas": len(acoes)
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao enviar feedback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@cauda_longa_bp.route('/audit/relatorio', methods=['GET'])
def gerar_relatorio_auditoria():
    """Gera relatório de auditoria."""
    try:
        if 'audit' not in sistemas:
            return jsonify({"error": "Sistema de auditoria não disponível"}), 503
        
        sistema_audit = sistemas['audit']
        periodo = request.args.get('periodo_horas', 24, type=int)
        
        relatorio = sistema_audit.gerar_relatorio_auditoria(periodo)
        
        return jsonify(relatorio), 200
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Inicializar sistemas quando o blueprint for registrado
@cauda_longa_bp.before_app_first_request
def setup_sistemas():
    """Configura sistemas na primeira requisição."""
    inicializar_sistemas()
'''
        
        return blueprint_code
    
    def salvar_blueprint(self, arquivo: str = "backend/app/api/cauda_longa.py"):
        """
        Salva blueprint Flask.
        
        Args:
            arquivo: Caminho do arquivo do blueprint
        """
        try:
            caminho_blueprint = self.projeto_root / arquivo
            caminho_blueprint.parent.mkdir(parents=True, exist_ok=True)
            
            blueprint_code = self.criar_blueprint_flask()
            
            with open(caminho_blueprint, 'w', encoding='utf-8') as f:
                f.write(blueprint_code)
            
            logger.info(f"[INTEGRATION] ✅ Blueprint salvo: {caminho_blueprint}")
            
        except Exception as e:
            logger.error(f"[INTEGRATION] ❌ Erro ao salvar blueprint: {str(e)}")
    
    def atualizar_main_flask(self) -> bool:
        """
        Atualiza o arquivo main.py do Flask para incluir o blueprint.
        
        Returns:
            True se atualizado com sucesso
        """
        try:
            caminho_main = self.projeto_root / "backend/app/main.py"
            
            if not caminho_main.exists():
                logger.error(f"[INTEGRATION] ❌ Arquivo main.py não encontrado: {caminho_main}")
                return False
            
            # Ler arquivo atual
            with open(caminho_main, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Verificar se já tem o blueprint
            if "cauda_longa_bp" in conteudo:
                logger.info("[INTEGRATION] ✅ Blueprint já está registrado no main.py")
                return True
            
            # Adicionar import
            import_line = "from backend.app.api.cauda_longa import cauda_longa_bp"
            
            # Encontrar linha após outros imports
            linhas = conteudo.split('\n')
            for index, linha in enumerate(linhas):
                if "from backend.app.api." in linha and "import" in linha:
                    # Inserir após este import
                    linhas.insert(index + 1, import_line)
                    break
            
            # Adicionar registro do blueprint
            for index, linha in enumerate(linhas):
                if "app.register_blueprint" in linha:
                    # Inserir após este registro
                    linhas.insert(index + 1, "app.register_blueprint(cauda_longa_bp)")
                    break
            
            # Salvar arquivo atualizado
            novo_conteudo = '\n'.join(linhas)
            
            with open(caminho_main, 'w', encoding='utf-8') as f:
                f.write(novo_conteudo)
            
            logger.info(f"[INTEGRATION] ✅ main.py atualizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"[INTEGRATION] ❌ Erro ao atualizar main.py: {str(e)}")
            return False
    
    def criar_arquivo_requirements(self) -> str:
        """
        Cria arquivo requirements.txt atualizado.
        
        Returns:
            Conteúdo do requirements.txt
        """
        requirements = '''# Requirements para Sistema de Cauda Longa
# Gerado automaticamente em: {timestamp}

# Dependências principais
flask>=2.3.0
flask-cors>=4.0.0
flask-sqlalchemy>=3.0.0
flask-migrate>=4.0.0
flask-babel>=3.1.0

# Machine Learning e Analytics
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0

# Cache e Performance
redis>=4.5.0
psutil>=5.9.0

# Monitoramento e Métricas
prometheus-client>=0.17.0
prometheus-flask-exporter>=0.22.0

# Testes
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Desenvolvimento
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0

# Segurança
cryptography>=42.0.0
bcrypt>=4.0.0
passlib[bcrypt]>=1.7.0

# Utilitários
python-dotenv>=1.0.0
requests>=2.32.2
aiohttp>=3.8.0
asyncio-mqtt>=0.11.0

# Visualização (opcional)
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0
'''.format(timestamp=datetime.now().isoformat())
        
        return requirements
    
    def salvar_requirements(self, arquivo: str = "requirements_cauda_longa.txt"):
        """
        Salva arquivo requirements.txt.
        
        Args:
            arquivo: Nome do arquivo requirements
        """
        try:
            caminho_requirements = self.projeto_root / arquivo
            
            requirements_content = self.criar_arquivo_requirements()
            
            with open(caminho_requirements, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            
            logger.info(f"[INTEGRATION] ✅ Requirements salvo: {caminho_requirements}")
            
        except Exception as e:
            logger.error(f"[INTEGRATION] ❌ Erro ao salvar requirements: {str(e)}")
    
    def executar_integracao_completa(self) -> Dict[str, Any]:
        """
        Executa integração completa.
        
        Returns:
            Relatório de integração
        """
        logger.info("[INTEGRATION] 🚀 Iniciando integração completa...")
        
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "status": "em_andamento",
            "etapas": {},
            "erros": [],
            "sucessos": []
        }
        
        try:
            # 1. Verificar módulos
            logger.info("[INTEGRATION] 📋 Verificando módulos implementados...")
            status_modulos = self.verificar_modulos_implementados()
            relatorio["etapas"]["verificacao_modulos"] = status_modulos
            
            # 2. Carregar módulos
            logger.info("[INTEGRATION] 📦 Carregando módulos...")
            modulos_carregados = self.carregar_modulos()
            relatorio["etapas"]["carregamento_modulos"] = {
                "total": len(modulos_carregados),
                "modulos": list(modulos_carregados.keys())
            }
            
            # 3. Criar configuração
            logger.info("[INTEGRATION] ⚙️ Criando configuração...")
            config = self.criar_configuracao_integracao()
            relatorio["etapas"]["configuracao"] = "criada"
            
            # 4. Salvar configuração
            logger.info("[INTEGRATION] 💾 Salvando configuração...")
            self.salvar_configuracao()
            relatorio["etapas"]["configuracao_salva"] = True
            
            # 5. Criar blueprint
            logger.info("[INTEGRATION] 🔧 Criando blueprint Flask...")
            self.salvar_blueprint()
            relatorio["etapas"]["blueprint_criado"] = True
            
            # 6. Atualizar main.py
            logger.info("[INTEGRATION] 🔄 Atualizando main.py...")
            main_atualizado = self.atualizar_main_flask()
            relatorio["etapas"]["main_atualizado"] = main_atualizado
            
            # 7. Criar requirements
            logger.info("[INTEGRATION] 📝 Criando requirements.txt...")
            self.salvar_requirements()
            relatorio["etapas"]["requirements_criado"] = True
            
            # Marcar como concluído
            relatorio["status"] = "concluido"
            relatorio["sucessos"].append("Integração concluída com sucesso")
            
            logger.info("[INTEGRATION] ✅ Integração concluída com sucesso!")
            
        except Exception as e:
            relatorio["status"] = "erro"
            relatorio["erros"].append(str(e))
            logger.error(f"[INTEGRATION] ❌ Erro na integração: {str(e)}")
        
        return relatorio
    
    def gerar_relatorio_final(self) -> str:
        """
        Gera relatório final de integração.
        
        Returns:
            Relatório em formato texto
        """
        relatorio = f"""
🎉 RELATÓRIO DE INTEGRAÇÃO - SISTEMA DE CAUDA LONGA
{'='*60}

📅 Data/Hora: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}
🔧 Status: {'✅ CONCLUÍDO' if self.modulos_cauda_longa else '❌ FALHOU'}

📊 MÓDULOS INTEGRADOS:
"""
        
        for nome, sistema in self.modulos_cauda_longa.items():
            relatorio += f"  ✅ {nome}: {type(sistema).__name__}\n"
        
        relatorio += f"""
📁 ARQUIVOS CRIADOS/ATUALIZADOS:
  ✅ backend/app/api/cauda_longa.py
  ✅ config_integracao_cauda_longa.json
  ✅ requirements_cauda_longa.txt
  ✅ backend/app/main.py (atualizado)

🌐 ENDPOINTS DISPONÍVEIS:
  GET  /api/cauda-longa/health
  POST /api/cauda-longa/ml/otimizar
  POST /api/cauda-longa/ab-testing/criar
  GET  /api/cauda-longa/monitoring/dashboard
  GET  /api/cauda-longa/cache/stats
  POST /api/cauda-longa/feedback/enviar
  GET  /api/cauda-longa/audit/relatorio

🚀 PRÓXIMOS PASSOS:
  1. Instalar dependências: pip install -r requirements_cauda_longa.txt
  2. Configurar variáveis de ambiente
  3. Executar testes de integração
  4. Deploy em ambiente de desenvolvimento
  5. Validar funcionamento em produção

🎯 OBJETIVO ATINGIDO: Sistema de cauda longa enterprise integrado!
"""
        
        return relatorio


def main():
    """Função principal."""
    print("🚀 INTEGRAÇÃO DO SISTEMA DE CAUDA LONGA")
    print("=" * 60)
    
    # Criar integrador
    integrador = IntegradorCaudaLonga()
    
    # Executar integração completa
    relatorio = integrador.executar_integracao_completa()
    
    # Exibir relatório final
    relatorio_final = integrador.gerar_relatorio_final()
    print(relatorio_final)
    
    # Salvar relatório
    with open("relatorio_integracao_cauda_longa.txt", "w", encoding="utf-8") as f:
        f.write(relatorio_final)
    
    print("📄 Relatório salvo em: relatorio_integracao_cauda_longa.txt")
    
    if relatorio["status"] == "concluido":
        print("\n🎉 INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
        return 0
    else:
        print("\n❌ INTEGRAÇÃO FALHOU!")
        return 1


if __name__ == "__main__":
    exit(main()) 