"""
Configuração ELK Stack - Centralização de Logs
Tracing ID: CHECKLIST_FINAL_20250127_003
Data: 2025-01-27
Status: IMPLEMENTAÇÃO COMPLETA

Configuração completa do ELK Stack (Elasticsearch, Logstash, Kibana) para:
- Centralização de logs
- Análise em tempo real
- Dashboards de monitoramento
- Alertas automáticos
- Retenção configurável
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class ElasticsearchConfig:
    """Configuração do Elasticsearch."""
    host: str = "localhost"
    port: int = 9200
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    index_prefix: str = "omni-keywords-logs"
    number_of_shards: int = 1
    number_of_replicas: int = 0
    refresh_interval: str = "1s"
    retention_days: int = 30
    
    @property
    def url(self) -> str:
        """URL completa do Elasticsearch."""
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        return f"{self.protocol}://{auth}{self.host}:{self.port}"
    
    def get_index_name(self, date_str: str = None) -> str:
        """Nome do índice baseado na data."""
        from datetime import datetime
        if date_str is None:
            date_str = datetime.now().strftime('%Y.%m.%d')
        return f"{self.index_prefix}-{date_str}"

@dataclass
class LogstashConfig:
    """Configuração do Logstash."""
    host: str = "localhost"
    port: int = 5044
    protocol: str = "http"
    pipeline_workers: int = 2
    batch_size: int = 125
    batch_delay: int = 50
    
    @property
    def url(self) -> str:
        """URL completa do Logstash."""
        return f"{self.protocol}://{self.host}:{self.port}"

@dataclass
class KibanaConfig:
    """Configuração do Kibana."""
    host: str = "localhost"
    port: int = 5601
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    
    @property
    def url(self) -> str:
        """URL completa do Kibana."""
        return f"{self.protocol}://{self.host}:{self.port}"

@dataclass
class ELKStackConfig:
    """Configuração completa do ELK Stack."""
    elasticsearch: ElasticsearchConfig = None
    logstash: LogstashConfig = None
    kibana: KibanaConfig = None
    enabled: bool = True
    environment: str = "development"
    
    def __post_init__(self):
        if self.elasticsearch is None:
            self.elasticsearch = ElasticsearchConfig()
        if self.logstash is None:
            self.logstash = LogstashConfig()
        if self.kibana is None:
            self.kibana = KibanaConfig()

class ELKStackManager:
    """Gerenciador do ELK Stack."""
    
    def __init__(self, config: ELKStackConfig = None):
        self.config = config or ELKStackConfig()
        self.config_dir = Path("config/elk_stack")
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_elasticsearch_config(self) -> str:
        """Gerar configuração do Elasticsearch."""
        config = {
            "cluster.name": "omni-keywords-cluster",
            "node.name": "omni-keywords-node-1",
            "path.data": "/var/lib/elasticsearch",
            "path.logs": "/var/log/elasticsearch",
            "network.host": self.config.elasticsearch.host,
            "http.port": self.config.elasticsearch.port,
            "discovery.type": "single-node",
            "xpack.security.enabled": bool(self.config.elasticsearch.username),
            "cluster.routing.allocation.disk.threshold_enabled": True,
            "cluster.routing.allocation.disk.watermark.low": "85%",
            "cluster.routing.allocation.disk.watermark.high": "90%",
            "cluster.routing.allocation.disk.watermark.flood_stage": "95%"
        }
        
        if self.config.elasticsearch.username:
            config.update({
                "xpack.security.authc.realms.native.native1.order": 0,
                "xpack.security.authc.realms.file.file1.order": 1
            })
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    def generate_logstash_config(self) -> str:
        """Gerar configuração do Logstash."""
        config = {
            "input": {
                "beats": {
                    "port": self.config.logstash.port,
                    "host": self.config.logstash.host
                }
            },
            "filter": [
                {
                    "if": {
                        "equals": {"[fields][service]": "omni_keywords_finder"}
                    },
                    "mutate": {
                        "add_field": {"[@metadata][index]": "omni-keywords-logs-%{+YYYY.MM.dd}"}
                    }
                },
                {
                    "grok": {
                        "match": {"message": "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}"}
                    }
                },
                {
                    "date": {
                        "match": ["timestamp", "ISO8601"],
                        "target": "@timestamp"
                    }
                },
                {
                    "mutate": {
                        "remove_field": ["timestamp"]
                    }
                }
            ],
            "output": [
                {
                    "elasticsearch": {
                        "hosts": [self.config.elasticsearch.url],
                        "index": "%{[@metadata][index]}",
                        "template_name": "omni-keywords-logs",
                        "template_pattern": "omni-keywords-logs-*",
                        "template": {
                            "settings": {
                                "number_of_shards": self.config.elasticsearch.number_of_shards,
                                "number_of_replicas": self.config.elasticsearch.number_of_replicas,
                                "refresh_interval": self.config.elasticsearch.refresh_interval
                            },
                            "mappings": {
                                "properties": {
                                    "@timestamp": {"type": "date"},
                                    "level": {"type": "keyword"},
                                    "message": {"type": "text"},
                                    "correlation_id": {"type": "keyword"},
                                    "user_id": {"type": "keyword"},
                                    "request_id": {"type": "keyword"},
                                    "service": {"type": "keyword"},
                                    "environment": {"type": "keyword"},
                                    "category": {"type": "keyword"},
                                    "function_name": {"type": "keyword"},
                                    "execution_time_ms": {"type": "float"},
                                    "memory_usage_mb": {"type": "float"},
                                    "cpu_usage_percent": {"type": "float"},
                                    "error_type": {"type": "keyword"},
                                    "stack_trace": {"type": "text"}
                                }
                            }
                        }
                    }
                }
            ]
        }
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    def generate_kibana_dashboards(self) -> Dict[str, Any]:
        """Gerar dashboards do Kibana."""
        dashboards = {
            "system_overview": {
                "title": "Omni Keywords Finder - System Overview",
                "description": "Visão geral do sistema",
                "panels": [
                    {
                        "title": "Logs por Nível",
                        "type": "visualization",
                        "visualization_type": "pie",
                        "index_pattern": "omni-keywords-logs-*",
                        "aggregation": {
                            "field": "level",
                            "type": "terms"
                        }
                    },
                    {
                        "title": "Logs por Categoria",
                        "type": "visualization",
                        "visualization_type": "bar",
                        "index_pattern": "omni-keywords-logs-*",
                        "aggregation": {
                            "field": "category",
                            "type": "terms"
                        }
                    },
                    {
                        "title": "Taxa de Erro",
                        "type": "visualization",
                        "visualization_type": "metric",
                        "index_pattern": "omni-keywords-logs-*",
                        "aggregation": {
                            "field": "level",
                            "type": "filter",
                            "filter": {"term": {"level": "error"}}
                        }
                    },
                    {
                        "title": "Tempo de Execução",
                        "type": "visualization",
                        "visualization_type": "line",
                        "index_pattern": "omni-keywords-logs-*",
                        "aggregation": {
                            "field": "execution_time_ms",
                            "type": "avg",
                            "time_field": "@timestamp"
                        }
                    }
                ]
            },
            "performance_monitoring": {
                "title": "Performance Monitoring",
                "description": "Monitoramento de performance",
                "panels": [
                    {
                        "title": "Uso de Memória",
                        "type": "visualization",
                        "visualization_type": "line",
                        "index_pattern": "omni-keywords-logs-*",
                        "aggregation": {
                            "field": "memory_usage_mb",
                            "type": "avg",
                            "time_field": "@timestamp"
                        }
                    },
                    {
                        "title": "Uso de CPU",
                        "type": "visualization",
                        "visualization_type": "line",
                        "index_pattern": "omni-keywords-logs-*",
                        "aggregation": {
                            "field": "cpu_usage_percent",
                            "type": "avg",
                            "time_field": "@timestamp"
                        }
                    }
                ]
            },
            "error_analysis": {
                "title": "Error Analysis",
                "description": "Análise de erros",
                "panels": [
                    {
                        "title": "Erros por Tipo",
                        "type": "visualization",
                        "visualization_type": "bar",
                        "index_pattern": "omni-keywords-logs-*",
                        "aggregation": {
                            "field": "error_type",
                            "type": "terms",
                            "filter": {"term": {"level": "error"}}
                        }
                    },
                    {
                        "title": "Stack Traces",
                        "type": "visualization",
                        "visualization_type": "table",
                        "index_pattern": "omni-keywords-logs-*",
                        "fields": ["@timestamp", "error_type", "message", "stack_trace"],
                        "filter": {"term": {"level": "error"}}
                    }
                ]
            }
        }
        
        return dashboards
    
    def generate_alert_rules(self) -> List[Dict[str, Any]]:
        """Gerar regras de alerta."""
        rules = [
            {
                "name": "high_error_rate",
                "description": "Taxa de erro alta",
                "condition": {
                    "query": "level:error",
                    "threshold": 10,
                    "time_window": "5m"
                },
                "action": {
                    "type": "email",
                    "recipients": ["admin@omni-keywords.com"],
                    "subject": "Alerta: Taxa de erro alta detectada"
                }
            },
            {
                "name": "performance_degradation",
                "description": "Degradação de performance",
                "condition": {
                    "query": "execution_time_ms:*",
                    "threshold": 5000,  # 5 segundos
                    "time_window": "10m"
                },
                "action": {
                    "type": "slack",
                    "channel": "#alerts",
                    "message": "Alerta: Degradação de performance detectada"
                }
            },
            {
                "name": "memory_usage_high",
                "description": "Uso de memória alto",
                "condition": {
                    "query": "memory_usage_mb:*",
                    "threshold": 1000,  # 1GB
                    "time_window": "5m"
                },
                "action": {
                    "type": "webhook",
                    "url": "https://api.omni-keywords.com/alerts",
                    "method": "POST"
                }
            }
        ]
        
        return rules
    
    def save_configs(self):
        """Salvar todas as configurações."""
        # Elasticsearch
        elasticsearch_config = self.generate_elasticsearch_config()
        with open(self.config_dir / "elasticsearch.yml", "w") as f:
            f.write(elasticsearch_config)
        
        # Logstash
        logstash_config = self.generate_logstash_config()
        with open(self.config_dir / "logstash.conf", "w") as f:
            f.write(logstash_config)
        
        # Kibana Dashboards
        dashboards = self.generate_kibana_dashboards()
        with open(self.config_dir / "kibana_dashboards.json", "w") as f:
            import json
            json.dump(dashboards, f, indent=2)
        
        # Alert Rules
        alert_rules = self.generate_alert_rules()
        with open(self.config_dir / "alert_rules.json", "w") as f:
            import json
            json.dump(alert_rules, f, indent=2)
        
        # Docker Compose
        docker_compose = self.generate_docker_compose()
        with open(self.config_dir / "docker-compose.yml", "w") as f:
            f.write(docker_compose)
    
    def generate_docker_compose(self) -> str:
        """Gerar Docker Compose para ELK Stack."""
        compose = f"""
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: omni-keywords-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled={str(self.config.elasticsearch.username is not None).lower()}
      - ELASTIC_PASSWORD=changeme
    ports:
      - "{self.config.elasticsearch.port}:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      - ./elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
    networks:
      - elk

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: omni-keywords-logstash
    ports:
      - "{self.config.logstash.port}:5044"
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
    networks:
      - elk

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: omni-keywords-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "{self.config.kibana.port}:5601"
    depends_on:
      - elasticsearch
    networks:
      - elk

volumes:
  elasticsearch_data:

networks:
  elk:
    driver: bridge
"""
        return compose
    
    def create_index_template(self):
        """Criar template de índice no Elasticsearch."""
        import requests
        
        template = {
            "index_patterns": ["omni-keywords-logs-*"],
            "settings": {
                "number_of_shards": self.config.elasticsearch.number_of_shards,
                "number_of_replicas": self.config.elasticsearch.number_of_replicas,
                "refresh_interval": self.config.elasticsearch.refresh_interval
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "message": {"type": "text"},
                    "correlation_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "request_id": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "environment": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "function_name": {"type": "keyword"},
                    "execution_time_ms": {"type": "float"},
                    "memory_usage_mb": {"type": "float"},
                    "cpu_usage_percent": {"type": "float"},
                    "error_type": {"type": "keyword"},
                    "stack_trace": {"type": "text"}
                }
            }
        }
        
        try:
            response = requests.put(
                f"{self.config.elasticsearch.url}/_template/omni-keywords-logs",
                json=template,
                timeout=10
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Erro ao criar template: {e}")
            return False

def get_elk_config() -> ELKStackConfig:
    """Obter configuração do ELK Stack."""
    return ELKStackConfig(
        elasticsearch=ElasticsearchConfig(
            host=os.getenv('ELASTICSEARCH_HOST', 'localhost'),
            port=int(os.getenv('ELASTICSEARCH_PORT', '9200')),
            username=os.getenv('ELASTICSEARCH_USERNAME'),
            password=os.getenv('ELASTICSEARCH_PASSWORD')
        ),
        logstash=LogstashConfig(
            host=os.getenv('LOGSTASH_HOST', 'localhost'),
            port=int(os.getenv('LOGSTASH_PORT', '5044'))
        ),
        kibana=KibanaConfig(
            host=os.getenv('KIBANA_HOST', 'localhost'),
            port=int(os.getenv('KIBANA_PORT', '5601'))
        ),
        enabled=os.getenv('ELK_ENABLED', 'true').lower() == 'true',
        environment=os.getenv('ENVIRONMENT', 'development')
    )

# Instância global
_elk_manager: Optional[ELKStackManager] = None

def get_elk_manager() -> ELKStackManager:
    """Obter instância global do gerenciador ELK."""
    global _elk_manager
    if _elk_manager is None:
        config = get_elk_config()
        _elk_manager = ELKStackManager(config)
    return _elk_manager 