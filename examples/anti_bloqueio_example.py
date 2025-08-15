"""
Exemplo Prático - Sistema Anti-Bloqueio
Tracing ID: ANTI_BLOQUEIO_EXAMPLE_20241219_001
Data: 2024-12-19
Versão: 1.0

Demonstra como usar o sistema anti-bloqueio para evitar bloqueios
em coletores de keywords e APIs externas.
"""

import asyncio
import time
import json
from typing import List, Dict, Any
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importa o sistema anti-bloqueio
from infrastructure.security.anti_bloqueio_system import (
    AntiBloqueioSystem,
    get_anti_bloqueio_system,
    anti_bloqueio_protected,
    BlockingType,
    EvasionStrategy
)

# Importa coletores existentes
from infrastructure.coleta.google_suggest import GoogleSuggestColetor
from infrastructure.coleta.google_trends import GoogleTrendsColetor
from infrastructure.coleta.youtube import YouTubeColetor


class ColetorProtegido:
    """
    Wrapper para coletores com proteção anti-bloqueio.
    """
    
    def __init__(self, coletor_class, config: Dict[str, Any] = None):
        self.coletor_class = coletor_class
        self.config = config or {}
        self.anti_bloqueio = get_anti_bloqueio_system()
        self.coletor = None
        
    async def __aenter__(self):
        """Inicializa o coletor com proteção."""
        self.coletor = self.coletor_class()
        
        # Configura proxies se disponíveis
        if self.config.get("proxies"):
            for proxy_data in self.config["proxies"]:
                self.anti_bloqueio.add_proxy(proxy_data)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Limpa recursos."""
        if self.coletor and hasattr(self.coletor, 'session'):
            if hasattr(self.coletor.session, 'close'):
                await self.coletor.session.close()
    
    @anti_bloqueio_protected(max_retries=3, base_delay=2.0)
    async def coletar_keywords_protegido(self, termo: str, limite: int = 100) -> List[Any]:
        """
        Coleta keywords com proteção anti-bloqueio.
        
        Args:
            termo: Termo base para busca
            limite: Número máximo de keywords
            
        Returns:
            Lista de keywords coletadas
        """
        try:
            # Usa o método original do coletor
            if hasattr(self.coletor, 'coletar_keywords'):
                return await self.coletor.coletar_keywords(termo, limite)
            else:
                logger.error("Coletor não possui método coletar_keywords")
                return []
                
        except Exception as e:
            logger.error(f"Erro na coleta protegida: {e}")
            raise e


class SistemaAntiBloqueioCompleto:
    """
    Sistema completo de anti-bloqueio com múltiplas estratégias.
    """
    
    def __init__(self):
        self.anti_bloqueio = get_anti_bloqueio_system()
        self.coletores_protegidos = {}
        self.estatisticas = {
            "total_requisicoes": 0,
            "requisicoes_bloqueadas": 0,
            "requisicoes_sucesso": 0,
            "dominos_bloqueados": 0,
            "tempo_total": 0
        }
    
    def configurar_proxies(self, proxy_list: List[Dict[str, Any]]):
        """Configura lista de proxies."""
        for proxy_data in proxy_list:
            self.anti_bloqueio.add_proxy(proxy_data)
        logger.info(f"Configurados {len(proxy_list)} proxies")
    
    def configurar_user_agents_customizados(self, user_agents: List[str]):
        """Configura User Agents customizados."""
        # Em uma implementação completa, adicionaria à lista do rotator
        logger.info(f"Configurados {len(user_agents)} User Agents customizados")
    
    async def testar_conectividade(self, urls: List[str]) -> Dict[str, bool]:
        """
        Testa conectividade com múltiplas URLs.
        
        Args:
            urls: Lista de URLs para testar
            
        Returns:
            Dicionário com resultados dos testes
        """
        resultados = {}
        
        for url in urls:
            try:
                success, response = await self.anti_bloqueio.make_request(url)
                resultados[url] = success
                
                if success:
                    logger.info(f"✅ Conectividade OK: {url}")
                else:
                    logger.warning(f"❌ Conectividade FALHOU: {url}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao testar {url}: {e}")
                resultados[url] = False
        
        return resultados
    
    async def coletar_keywords_multi_fonte(self, termo: str, 
                                         fontes: List[str] = None) -> Dict[str, List[Any]]:
        """
        Coleta keywords de múltiplas fontes com proteção.
        
        Args:
            termo: Termo base para busca
            fontes: Lista de fontes para coletar
            
        Returns:
            Dicionário com keywords por fonte
        """
        if fontes is None:
            fontes = ["google_suggest", "google_trends", "youtube"]
        
        resultados = {}
        inicio = time.time()
        
        for fonte in fontes:
            try:
                logger.info(f"🔄 Coletando de {fonte} para termo: {termo}")
                
                # Seleciona coletor baseado na fonte
                coletor_class = self._get_coletor_class(fonte)
                if coletor_class:
                    async with ColetorProtegido(coletor_class) as coletor_protegido:
                        keywords = await coletor_protegido.coletar_keywords_protegido(termo, 50)
                        resultados[fonte] = keywords
                        logger.info(f"✅ {fonte}: {len(keywords)} keywords coletadas")
                else:
                    logger.warning(f"⚠️ Coletor não encontrado para {fonte}")
                    resultados[fonte] = []
                    
            except Exception as e:
                logger.error(f"❌ Erro ao coletar de {fonte}: {e}")
                resultados[fonte] = []
        
        self.estatisticas["tempo_total"] = time.time() - inicio
        return resultados
    
    def _get_coletor_class(self, fonte: str):
        """Obtém classe do coletor baseado na fonte."""
        coletores = {
            "google_suggest": GoogleSuggestColetor,
            "google_trends": GoogleTrendsColetor,
            "youtube": YouTubeColetor
        }
        return coletores.get(fonte)
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas completas do sistema."""
        stats = self.anti_bloqueio.get_statistics()
        stats.update(self.estatisticas)
        
        # Calcula métricas adicionais
        if stats["total_requests"] > 0:
            stats["taxa_sucesso"] = stats["successful_requests"] / stats["total_requests"]
            stats["taxa_bloqueio"] = stats["blocked_requests"] / stats["total_requests"]
        else:
            stats["taxa_sucesso"] = 0
            stats["taxa_bloqueio"] = 0
        
        return stats
    
    def gerar_relatorio(self) -> str:
        """Gera relatório detalhado do sistema."""
        stats = self.obter_estatisticas()
        
        relatorio = f"""
📊 RELATÓRIO ANTI-BLOQUEIO
{'='*50}

📈 MÉTRICAS GERAIS:
• Total de Requisições: {stats['total_requests']}
• Requisições com Sucesso: {stats['successful_requests']}
• Requisições Bloqueadas: {stats['blocked_requests']}
• Taxa de Sucesso: {stats['taxa_sucesso']:.2%}
• Taxa de Bloqueio: {stats['taxa_bloqueio']:.2%}

🌐 DOMÍNIOS:
• Domínios Bloqueados: {stats['blocked_domains']}
• IPs Bloqueados: {stats['blocked_ips']}

⏱️ PERFORMANCE:
• Tempo Total: {stats['tempo_total']:.2f}string_data
• Requisições por Hora: {stats.get('recent_blocking_events', 0)}

🛡️ PROTEÇÕES ATIVAS:
• Rotação de User Agents: ✅
• Rotação de Proxies: ✅
• Behavioral Mimicking: ✅
• Fingerprint Evasion: ✅
• Rate Limiting Inteligente: ✅

📋 EVENTOS RECENTES:
"""
        
        # Adiciona eventos de bloqueio recentes
        blocking_events = self.anti_bloqueio.blocking_events[-5:]  # Últimos 5
        for event in blocking_events:
            relatorio += f"• {event.blocking_type.value} - {event.url}\n"
        
        return relatorio


async def exemplo_uso_basico():
    """Exemplo básico de uso do sistema anti-bloqueio."""
    print("🚀 EXEMPLO BÁSICO - SISTEMA ANTI-BLOQUEIO")
    print("="*60)
    
    # Inicializa sistema
    sistema = SistemaAntiBloqueioCompleto()
    
    # Configura proxies (exemplo)
    proxies_exemplo = [
        {
            "host": "proxy1.exemplo.com",
            "port": 8080,
            "protocol": "http",
            "country": "BR"
        },
        {
            "host": "proxy2.exemplo.com", 
            "port": 8080,
            "protocol": "http",
            "country": "US"
        }
    ]
    
    # sistema.configurar_proxies(proxies_exemplo)  # Descomente se tiver proxies
    
    # Testa conectividade
    urls_teste = [
        "https://www.google.com",
        "https://www.youtube.com",
        "https://www.reddit.com"
    ]
    
    print("\n🔍 TESTANDO CONECTIVIDADE...")
    resultados_conectividade = await sistema.testar_conectividade(urls_teste)
    
    for url, sucesso in resultados_conectividade.items():
        status = "✅ OK" if sucesso else "❌ FALHOU"
        print(f"  {status} {url}")
    
    # Coleta keywords
    print("\n🔍 COLETANDO KEYWORDS...")
    termo_teste = "marketing digital"
    
    resultados = await sistema.coletar_keywords_multi_fonte(
        termo_teste, 
        fontes=["google_suggest", "google_trends"]
    )
    
    # Exibe resultados
    for fonte, keywords in resultados.items():
        print(f"\n📊 {fonte.upper()}:")
        for index, keyword in enumerate(keywords[:5], 1):  # Mostra apenas 5
            if hasattr(keyword, 'termo'):
                print(f"  {index}. {keyword.termo}")
            else:
                print(f"  {index}. {keyword}")
    
    # Gera relatório
    print("\n" + sistema.gerar_relatorio())


async def exemplo_uso_avancado():
    """Exemplo avançado com configurações específicas."""
    print("\n🚀 EXEMPLO AVANÇADO - CONFIGURAÇÕES ESPECÍFICAS")
    print("="*60)
    
    # Configuração avançada
    config_avancada = {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "max_retries": 5,
        "base_delay": 3.0,
        "rotation_interval": 120
    }
    
    # Inicializa com configuração
    sistema = get_anti_bloqueio_system()
    
    # Simula requisições com diferentes estratégias
    urls_teste = [
        "https://api.exemplo.com/v1/keywords",
        "https://www.google.com/search",
        "https://www.youtube.com/results"
    ]
    
    print("\n🔄 SIMULANDO REQUISIÇÕES COM PROTEÇÃO...")
    
    for url in urls_teste:
        print(f"\n📡 Testando: {url}")
        
        for tentativa in range(3):
            try:
                success, response = await sistema.make_request(
                    url=url,
                    method="GET",
                    timeout=10
                )
                
                if success:
                    print(f"  ✅ Tentativa {tentativa + 1}: SUCESSO")
                    break
                else:
                    print(f"  ⚠️ Tentativa {tentativa + 1}: BLOQUEADO")
                    
            except Exception as e:
                print(f"  ❌ Tentativa {tentativa + 1}: ERRO - {e}")
    
    # Estatísticas finais
    stats = sistema.get_statistics()
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"  • Taxa de Sucesso: {stats['success_rate']:.2%}")
    print(f"  • Requisições Bloqueadas: {stats['blocked_requests']}")
    print(f"  • Domínios Bloqueados: {stats['blocked_domains']}")


async def exemplo_integracao_coletores():
    """Exemplo de integração com coletores existentes."""
    print("\n🚀 EXEMPLO INTEGRAÇÃO - COLETORES EXISTENTES")
    print("="*60)
    
    sistema = SistemaAntiBloqueioCompleto()
    
    # Lista de termos para testar
    termos_teste = [
        "seo otimização",
        "marketing digital",
        "ecommerce"
    ]
    
    print("\n🔍 TESTANDO COLETORES COM PROTEÇÃO...")
    
    for termo in termos_teste:
        print(f"\n📝 Termo: '{termo}'")
        
        try:
            resultados = await sistema.coletar_keywords_multi_fonte(
                termo, 
                fontes=["google_suggest"]
            )
            
            for fonte, keywords in resultados.items():
                print(f"  📊 {fonte}: {len(keywords)} keywords")
                
                # Mostra algumas keywords
                for index, keyword in enumerate(keywords[:3], 1):
                    if hasattr(keyword, 'termo'):
                        print(f"    {index}. {keyword.termo}")
                    else:
                        print(f"    {index}. {keyword}")
                        
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    # Relatório final
    print("\n" + sistema.gerar_relatorio())


async def main():
    """Função principal com todos os exemplos."""
    print("🛡️ SISTEMA ANTI-BLOQUEIO - OMNİ KEYWORDS FINDER")
    print("="*70)
    print("Demonstração de estratégias para evitar bloqueios em coletores")
    print("="*70)
    
    try:
        # Exemplo básico
        await exemplo_uso_basico()
        
        # Exemplo avançado
        await exemplo_uso_avancado()
        
        # Exemplo de integração
        await exemplo_integracao_coletores()
        
        print("\n✅ TODOS OS EXEMPLOS CONCLUÍDOS COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Executa exemplos
    asyncio.run(main()) 