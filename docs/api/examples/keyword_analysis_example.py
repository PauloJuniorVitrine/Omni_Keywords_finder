#!/usr/bin/env python3
"""
Exemplo de uso da API Omni Keywords Finder - Análise de Palavras-chave
Tracing ID: API_EXAMPLE_KEYWORD_ANALYSIS_001
Data: 2025-01-27
"""

import requests
import json
import time
from typing import Dict, List, Optional

class OmniKeywordsFinderAPI:
    """Cliente para a API Omni Keywords Finder"""
    
    def __init__(self, base_url: str = "https://api.omnikeywords.com/v2"):
        self.base_url = base_url
        self.access_token = None
        self.session = requests.Session()
    
    def login(self, email: str, password: str) -> bool:
        """Realizar login na API"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                print("✅ Login realizado com sucesso")
                return True
            else:
                print(f"❌ Erro no login: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro durante login: {e}")
            return False
    
    def analyze_keyword(self, keyword: str, language: str = "pt-BR", 
                       market: str = "BR", include_competitors: bool = True,
                       include_trends: bool = True) -> Optional[Dict]:
        """Analisar uma palavra-chave específica"""
        try:
            payload = {
                "keyword": keyword,
                "language": language,
                "market": market,
                "include_competitors": include_competitors,
                "include_trends": include_trends
            }
            
            response = self.session.post(
                f"{self.base_url}/keywords/analyze",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro na análise: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro durante análise: {e}")
            return None
    
    def discover_keywords(self, seed_keywords: List[str], max_results: int = 20) -> Optional[Dict]:
        """Descobrir novas palavras-chave relacionadas"""
        try:
            payload = {
                "seed_keywords": seed_keywords,
                "language": "pt-BR",
                "market": "BR",
                "max_results": max_results
            }
            
            response = self.session.post(
                f"{self.base_url}/keywords/discover",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro na descoberta: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro durante descoberta: {e}")
            return None
    
    def optimize_content(self, content: str, target_keywords: List[str]) -> Optional[Dict]:
        """Otimizar conteúdo para SEO"""
        try:
            payload = {
                "content": content,
                "target_keywords": target_keywords,
                "content_type": "blog",
                "language": "pt-BR"
            }
            
            response = self.session.post(
                f"{self.base_url}/content/optimize",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro na otimização: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro durante otimização: {e}")
            return None

def print_keyword_analysis(analysis: Dict):
    """Exibir resultados da análise de palavra-chave"""
    print("\n" + "="*60)
    print("📊 ANÁLISE DE PALAVRA-CHAVE")
    print("="*60)
    
    keyword = analysis.get("keyword", "N/A")
    analysis_data = analysis.get("analysis", {})
    
    print(f"🔍 Palavra-chave: {keyword}")
    print(f"📈 Volume de busca: {analysis_data.get('search_volume', 'N/A'):,}")
    print(f"🎯 Dificuldade: {analysis_data.get('difficulty', 'N/A')}/100")
    print(f"💰 CPC médio: R$ {analysis_data.get('cpc', 'N/A')}")
    print(f"🏆 Competição: {analysis_data.get('competition', 'N/A')*100:.1f}%")
    print(f"🎯 Intenção: {analysis_data.get('intent', 'N/A')}")
    
    # Competidores
    competitors = analysis.get("competitors", [])
    if competitors:
        print(f"\n🏢 TOP COMPETIDORES ({len(competitors)}):")
        for i, comp in enumerate(competitors[:5], 1):
            print(f"  {i}. {comp.get('domain', 'N/A')} (Rank: {comp.get('rank', 'N/A')})")
    
    # Tendências
    trends = analysis.get("trends", {})
    if trends:
        print(f"\n📈 TENDÊNCIAS:")
        print(f"  Padrão sazonal: {trends.get('seasonal_pattern', 'N/A')}")
        print(f"  Taxa de crescimento: {trends.get('growth_rate', 'N/A')}%")
    
    # Recomendações
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        print(f"\n💡 RECOMENDAÇÕES:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

def print_discovery_results(discovery: Dict):
    """Exibir resultados da descoberta de palavras-chave"""
    print("\n" + "="*60)
    print("🔍 DESCOBERTA DE PALAVRAS-CHAVE")
    print("="*60)
    
    discovered = discovery.get("discovered_keywords", [])
    print(f"📊 Total descoberto: {len(discovered)} palavras-chave")
    
    if discovered:
        print(f"\n🏆 TOP 10 OPORTUNIDADES:")
        for i, kw in enumerate(discovered[:10], 1):
            print(f"  {i}. {kw.get('keyword', 'N/A')}")
            print(f"     Volume: {kw.get('search_volume', 'N/A'):,} | "
                  f"Dificuldade: {kw.get('difficulty', 'N/A')}/100 | "
                  f"Relevância: {kw.get('relevance_score', 'N/A')*100:.1f}%")
    
    # Clusters
    clusters = discovery.get("clusters", [])
    if clusters:
        print(f"\n📦 CLUSTERS IDENTIFICADOS ({len(clusters)}):")
        for i, cluster in enumerate(clusters, 1):
            print(f"  {i}. {cluster.get('name', 'N/A')}")
            print(f"     Média volume: {cluster.get('avg_volume', 'N/A'):,}")
            print(f"     Média dificuldade: {cluster.get('avg_difficulty', 'N/A')}/100")

def print_optimization_results(optimization: Dict):
    """Exibir resultados da otimização de conteúdo"""
    print("\n" + "="*60)
    print("✏️ OTIMIZAÇÃO DE CONTEÚDO")
    print("="*60)
    
    seo_score = optimization.get("seo_score", 0)
    print(f"📊 Score SEO: {seo_score}/100")
    
    suggestions = optimization.get("suggestions", [])
    if suggestions:
        print(f"\n💡 SUGESTÕES DE MELHORIA ({len(suggestions)}):")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. [{suggestion.get('type', 'N/A').upper()}] "
                  f"[{suggestion.get('priority', 'N/A').upper()}]")
            print(f"     {suggestion.get('description', 'N/A')}")
            if suggestion.get('suggested_value'):
                print(f"     Sugestão: {suggestion.get('suggested_value', 'N/A')}")

def main():
    """Função principal com exemplos de uso"""
    print("🚀 EXEMPLO DE USO - API OMNİ KEYWORDS FINDER")
    print("="*60)
    
    # Inicializar cliente
    api = OmniKeywordsFinderAPI()
    
    # Credenciais (substitua pelas suas)
    email = "seu_email@exemplo.com"
    password = "sua_senha"
    
    # Login
    if not api.login(email, password):
        print("❌ Não foi possível fazer login. Verifique as credenciais.")
        return
    
    # Exemplo 1: Análise de palavra-chave
    print("\n🔍 EXEMPLO 1: Análise de palavra-chave")
    keyword_analysis = api.analyze_keyword("marketing digital")
    if keyword_analysis:
        print_keyword_analysis(keyword_analysis)
    
    # Exemplo 2: Descoberta de palavras-chave
    print("\n🔍 EXEMPLO 2: Descoberta de palavras-chave")
    discovery = api.discover_keywords(["marketing digital", "seo"], max_results=15)
    if discovery:
        print_discovery_results(discovery)
    
    # Exemplo 3: Otimização de conteúdo
    print("\n✏️ EXEMPLO 3: Otimização de conteúdo")
    content = """
    Marketing digital é uma estratégia essencial para empresas modernas. 
    Com o crescimento da internet, as empresas precisam se adaptar e 
    usar ferramentas digitais para alcançar seus clientes.
    """
    optimization = api.optimize_content(content, ["marketing digital", "estratégia"])
    if optimization:
        print_optimization_results(optimization)
    
    print("\n✅ Exemplos concluídos com sucesso!")

if __name__ == "__main__":
    main() 