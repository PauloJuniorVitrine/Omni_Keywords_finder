import datetime
from prometheus_client import REGISTRY
from typing import Dict, List, Optional, Any

ARQUIVO = 'docs/relatorio_negocio.html'

def get_metric_value(name):
    for metric in REGISTRY.collect():
        if metric.name == name:
            for sample in metric.samples:
                return int(sample.value)
    return 0

def gerar_relatorio():
    keywords = get_metric_value('keywords_processadas_total')
    exportacoes = get_metric_value('exportacoes_realizadas_total')
    erros = get_metric_value('erros_processamento_total')
    clusters = keywords // 20 if keywords else 0
    top_clusters = [
        {'nome': 'Cluster A', 'volume': clusters//2},
        {'nome': 'Cluster B', 'volume': clusters//3},
        {'nome': 'Cluster C', 'volume': clusters//4},
    ]
    html = f'''
    <html><head><title>Relatório de Negócio - Omni Keywords Finder</title></head><body>
    <h1>Relatório Semanal - {datetime.datetime.utcnow().strftime('%Y-%m-%data')}</h1>
    <ul>
      <li><b>Keywords processadas:</b> {keywords}</li>
      <li><b>Exportações realizadas:</b> {exportacoes}</li>
      <li><b>Clusters gerados (mock):</b> {clusters}</li>
      <li><b>Rejeições/Erros:</b> {erros}</li>
    </ul>
    <h2>Top Clusters (mock)</h2>
    <ul>
      {''.join([f"<li>{c['nome']}: {c['volume']}</li>" for c in top_clusters])}
    </ul>
    <p>Relatório gerado automaticamente.</p>
    </body></html>
    '''
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] Relatório salvo em {ARQUIVO}")

if __name__ == "__main__":
    gerar_relatorio() 