#!/usr/bin/env python3
"""
CDN Cache Invalidation Script
Tracing ID: IMP003_CDN_INVALIDATION_001
Data: 2025-01-27
Versão: 1.0
Status: Em Implementação

Script para invalidação inteligente de cache CDN com:
- Invalidação automática baseada em padrões
- Cache warming para URLs críticas
- Monitoramento de métricas de invalidação
- Integração com sistema de alertas
"""

import boto3
import yaml
import logging
import argparse
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import os
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data'
)
logger = logging.getLogger(__name__)

@dataclass
class InvalidationConfig:
    """Configuração para invalidação de cache"""
    distribution_id: str
    patterns: List[str]
    max_invalidations_per_month: int
    automatic_enabled: bool
    manual_enabled: bool

@dataclass
class CacheWarmingConfig:
    """Configuração para cache warming"""
    urls: List[str]
    concurrent_requests: int
    timeout: int
    retry_attempts: int

class CDNInvalidationManager:
    """Gerenciador de invalidação de cache CDN"""
    
    def __init__(self, config_path: str = "config/cdn.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.cloudfront = boto3.client('cloudfront')
        self.cloudwatch = boto3.client('cloudwatch')
        
        # Configurações de invalidação
        self.invalidation_config = InvalidationConfig(
            distribution_id=self.config['cdn']['distribution_id'],
            patterns=self.config['cdn']['invalidation']['manual']['patterns'],
            max_invalidations_per_month=self.config['cdn']['invalidation']['manual']['max_invalidations_per_month'],
            automatic_enabled=self.config['cdn']['invalidation']['automatic']['enabled'],
            manual_enabled=self.config['cdn']['invalidation']['manual']['enabled']
        )
        
        # Configurações de cache warming
        self.cache_warming_config = CacheWarmingConfig(
            urls=self.config['cdn']['cache_warming']['urls'],
            concurrent_requests=self.config['cdn']['cache_warming']['concurrent_requests'],
            timeout=self.config['cdn']['cache_warming']['timeout'],
            retry_attempts=self.config['cdn']['cache_warming']['retry_attempts']
        )
    
    def _load_config(self) -> Dict:
        """Carrega configuração do CDN"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Arquivo de configuração não encontrado: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Erro ao parsear configuração YAML: {e}")
            raise
    
    def get_invalidation_count(self) -> int:
        """Obtém número de invalidações no mês atual"""
        try:
            # Busca invalidações do mês atual
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            response = self.cloudfront.list_invalidations(
                DistributionId=self.invalidation_config.distribution_id,
                MaxItems='100'
            )
            
            count = 0
            for invalidation in response.get('InvalidationList', {}).get('Items', []):
                if invalidation['Status'] != 'Completed':
                    continue
                    
                create_time = invalidation['CreateTime']
                if create_time >= start_date:
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Erro ao obter contagem de invalidações: {e}")
            return 0
    
    def create_invalidation(self, paths: List[str], caller_reference: Optional[str] = None) -> str:
        """Cria invalidação de cache"""
        try:
            # Verifica limite de invalidações
            current_count = self.get_invalidation_count()
            if current_count >= self.invalidation_config.max_invalidations_per_month:
                raise ValueError(f"Limite de invalidações atingido: {current_count}/{self.invalidation_config.max_invalidations_per_month}")
            
            # Gera caller reference único
            if not caller_reference:
                caller_reference = f"invalidation-{int(time.time())}"
            
            # Cria invalidação
            response = self.cloudfront.create_invalidation(
                DistributionId=self.invalidation_config.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': caller_reference
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            logger.info(f"Invalidação criada: {invalidation_id} para paths: {paths}")
            
            # Registra métrica
            self._record_invalidation_metric(len(paths))
            
            return invalidation_id
            
        except Exception as e:
            logger.error(f"Erro ao criar invalidação: {e}")
            raise
    
    def wait_for_invalidation(self, invalidation_id: str, timeout: int = 300) -> bool:
        """Aguarda conclusão da invalidação"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                response = self.cloudfront.get_invalidation(
                    DistributionId=self.invalidation_config.distribution_id,
                    Id=invalidation_id
                )
                
                status = response['Invalidation']['Status']
                
                if status == 'Completed':
                    logger.info(f"Invalidação {invalidation_id} concluída com sucesso")
                    return True
                elif status == 'InProgress':
                    logger.info(f"Invalidação {invalidation_id} em progresso...")
                    time.sleep(10)
                else:
                    logger.error(f"Invalidação {invalidation_id} falhou com status: {status}")
                    return False
            
            logger.error(f"Timeout aguardando invalidação {invalidation_id}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao aguardar invalidação: {e}")
            return False
    
    def automatic_invalidation(self, deployment_type: str = "deploy") -> bool:
        """Invalidação automática baseada no tipo de deploy"""
        try:
            if not self.invalidation_config.automatic_enabled:
                logger.info("Invalidação automática desabilitada")
                return False
            
            # Padrões baseados no tipo de deploy
            patterns = {
                "deploy": [
                    "/static/css/*",
                    "/static/js/*",
                    "/static/image/*"
                ],
                "api_update": [
                    "/api/*"
                ],
                "content_update": [
                    "/content/*",
                    "/blog/*"
                ],
                "full": [
                    "/*"
                ]
            }
            
            if deployment_type not in patterns:
                logger.error(f"Tipo de deploy inválido: {deployment_type}")
                return False
            
            paths = patterns[deployment_type]
            caller_reference = f"auto-{deployment_type}-{int(time.time())}"
            
            invalidation_id = self.create_invalidation(paths, caller_reference)
            return self.wait_for_invalidation(invalidation_id)
            
        except Exception as e:
            logger.error(f"Erro na invalidação automática: {e}")
            return False
    
    def cache_warming(self) -> Dict[str, bool]:
        """Cache warming para URLs críticas"""
        import requests
        import concurrent.futures
        
        results = {}
        
        def warm_url(url: str) -> tuple:
            """Aquece uma URL específica"""
            try:
                response = requests.get(
                    url,
                    timeout=self.cache_warming_config.timeout,
                    headers={'User-Agent': 'OmniKeywords-CacheWarming/1.0'}
                )
                
                if response.status_code == 200:
                    logger.info(f"Cache warming bem-sucedido para: {url}")
                    return url, True
                else:
                    logger.warning(f"Cache warming falhou para {url}: {response.status_code}")
                    return url, False
                    
            except Exception as e:
                logger.error(f"Erro no cache warming para {url}: {e}")
                return url, False
        
        try:
            # Executa cache warming em paralelo
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.cache_warming_config.concurrent_requests
            ) as executor:
                future_to_url = {
                    executor.submit(warm_url, url): url 
                    for url in self.cache_warming_config.urls
                }
                
                for future in concurrent.futures.as_completed(future_to_url):
                    url, success = future.result()
                    results[url] = success
            
            # Registra métricas
            success_count = sum(results.values())
            total_count = len(results)
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            
            self._record_cache_warming_metric(success_rate)
            
            logger.info(f"Cache warming concluído: {success_count}/{total_count} URLs ({success_rate:.1f}%)")
            return results
            
        except Exception as e:
            logger.error(f"Erro no cache warming: {e}")
            return {}
    
    def _record_invalidation_metric(self, path_count: int):
        """Registra métrica de invalidação"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace='OmniKeywords/CDN',
                MetricData=[
                    {
                        'MetricName': 'InvalidationCount',
                        'Value': 1,
                        'Unit': 'Count',
                        'Timestamp': datetime.now()
                    },
                    {
                        'MetricName': 'InvalidatedPaths',
                        'Value': path_count,
                        'Unit': 'Count',
                        'Timestamp': datetime.now()
                    }
                ]
            )
        except Exception as e:
            logger.warning(f"Erro ao registrar métrica de invalidação: {e}")
    
    def _record_cache_warming_metric(self, success_rate: float):
        """Registra métrica de cache warming"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace='OmniKeywords/CDN',
                MetricData=[
                    {
                        'MetricName': 'CacheWarmingSuccessRate',
                        'Value': success_rate,
                        'Unit': 'Percent',
                        'Timestamp': datetime.now()
                    }
                ]
            )
        except Exception as e:
            logger.warning(f"Erro ao registrar métrica de cache warming: {e}")
    
    def get_cdn_metrics(self) -> Dict:
        """Obtém métricas do CDN"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            metrics = {}
            
            # Métricas básicas
            metric_names = [
                'Requests',
                'BytesDownloaded',
                'BytesUploaded',
                'TotalErrorRate',
                '4xxErrorRate',
                '5xxErrorRate',
                'CacheHitRate'
            ]
            
            for metric_name in metric_names:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/CloudFront',
                    MetricName=metric_name,
                    Dimensions=[
                        {
                            'Name': 'DistributionId',
                            'Value': self.invalidation_config.distribution_id
                        },
                        {
                            'Name': 'Region',
                            'Value': 'Global'
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,
                    Statistics=['Average', 'Sum', 'Maximum']
                )
                
                if response['Datapoints']:
                    latest = max(response['Datapoints'], key=lambda value: value['Timestamp'])
                    metrics[metric_name] = {
                        'average': latest.get('Average'),
                        'sum': latest.get('Sum'),
                        'maximum': latest.get('Maximum')
                    }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas do CDN: {e}")
            return {}

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='CDN Cache Invalidation Manager')
    parser.add_argument('--action', choices=['invalidate', 'warm', 'metrics', 'auto'], 
                       required=True, help='Ação a ser executada')
    parser.add_argument('--paths', nargs='+', help='Paths para invalidação')
    parser.add_argument('--deployment-type', choices=['deploy', 'api_update', 'content_update', 'full'],
                       help='Tipo de deploy para invalidação automática')
    parser.add_argument('--config', default='config/cdn.yaml', help='Caminho do arquivo de configuração')
    
    args = parser.parse_args()
    
    try:
        manager = CDNInvalidationManager(args.config)
        
        if args.action == 'invalidate':
            if not args.paths:
                logger.error("Paths devem ser especificados para invalidação")
                return 1
            
            invalidation_id = manager.create_invalidation(args.paths)
            success = manager.wait_for_invalidation(invalidation_id)
            return 0 if success else 1
            
        elif args.action == 'warm':
            results = manager.cache_warming()
            success_count = sum(results.values())
            return 0 if success_count > 0 else 1
            
        elif args.action == 'metrics':
            metrics = manager.get_cdn_metrics()
            print(json.dumps(metrics, indent=2, default=str))
            return 0
            
        elif args.action == 'auto':
            if not args.deployment_type:
                logger.error("Tipo de deploy deve ser especificado para invalidação automática")
                return 1
            
            success = manager.automatic_invalidation(args.deployment_type)
            return 0 if success else 1
    
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 