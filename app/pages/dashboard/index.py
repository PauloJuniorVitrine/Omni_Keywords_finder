from flask import Blueprint, render_template_string
from prometheus_client import REGISTRY
from typing import Dict, List, Optional, Any

dashboard_bp = Blueprint('dashboard', __name__)

def get_metric_value(name):
    for metric in REGISTRY.collect():
        if metric.name == name:
            for sample in metric.samples:
                return int(sample.value)
    return 0

@dashboard_bp.route('/dashboard')
def dashboard():
    keywords = get_metric_value('keywords_processadas_total')
    exportacoes = get_metric_value('exportacoes_realizadas_total')
    erros = get_metric_value('erros_processamento_total')
    # Mock de clusters e tendências
    clusters = keywords // 20 if keywords else 0
    tendencias = [
        {'nome': 'Cluster A', 'volume': clusters//2},
        {'nome': 'Cluster B', 'volume': clusters//3},
        {'nome': 'Cluster C', 'volume': clusters//4},
    ]
    html = '''
    <h1>Dashboard Omni Keywords Finder</h1>
    <ul>
      <li><b>Keywords processadas:</b> {{keywords}}</li>
      <li><b>Exportações realizadas:</b> {{exportacoes}}</li>
      <li><b>Clusters gerados (mock):</b> {{clusters}}</li>
      <li><b>Rejeições/Erros:</b> {{erros}}</li>
    </ul>
    <h2>Tendências (mock)</h2>
    <ul>
      {% for t in tendencias %}
        <li>{{t.nome}}: {{t.volume}}</li>
      {% endfor %}
    </ul>
    <p><a href="/metrics">Ver métricas Prometheus</a></p>
    '''
    return render_template_string(html, keywords=keywords, exportacoes=exportacoes, clusters=clusters, erros=erros, tendencias=tendencias) 