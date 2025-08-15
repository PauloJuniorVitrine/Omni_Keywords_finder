#!/usr/bin/env python3
"""
Script de Análise de Anomalias
Criado em: 2025-01-27
Tracing ID: COMPLETUDE_CHECKLIST_20250127_001
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path
import tempfile
import yaml
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Tipos de anomalias"""
    SPIKE = "spike"
    DROP = "drop"
    TREND = "trend"
    SEASONAL = "seasonal"
    OUTLIER = "outlier"

@dataclass
class AnomalyDetectionConfig:
    """Configuração para detecção de anomalias"""
    window_size: int = 60  # Janela em minutos
    threshold_multiplier: float = 2.0  # Multiplicador do desvio padrão
    min_data_points: int = 10  # Mínimo de pontos para análise
    confidence_level: float = 0.95  # Nível de confiança
    seasonality_period: int = 1440  # Período sazonal em minutos (24h)
    trend_sensitivity: float = 0.1  # Sensibilidade para detecção de tendências

class AnomalyDetector:
    """Detector de anomalias"""
    
    def __init__(self, config: AnomalyDetectionConfig):
        self.config = config
        self.anomalies = []
        self.metrics_history = {}
    
    def detect_spike_anomaly(self, data: List[float], timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detecta anomalias do tipo spike"""
        anomalies = []
        
        if len(data) < self.config.min_data_points:
            return anomalies
        
        # Calcula estatísticas da janela móvel
        window_data = data[-self.config.window_size:]
        mean_val = np.mean(window_data)
        std_val = np.std(window_data)
        
        if std_val == 0:
            return anomalies
        
        threshold = mean_val + (self.config.threshold_multiplier * std_val)
        
        # Verifica valores que excedem o threshold
        for i, value in enumerate(data):
            if value > threshold:
                anomaly = {
                    'type': AnomalyType.SPIKE.value,
                    'timestamp': timestamps[i].isoformat(),
                    'value': value,
                    'threshold': threshold,
                    'mean': mean_val,
                    'std': std_val,
                    'severity': self._calculate_severity(value, threshold, mean_val)
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def detect_drop_anomaly(self, data: List[float], timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detecta anomalias do tipo drop"""
        anomalies = []
        
        if len(data) < self.config.min_data_points:
            return anomalies
        
        # Calcula estatísticas da janela móvel
        window_data = data[-self.config.window_size:]
        mean_val = np.mean(window_data)
        std_val = np.std(window_data)
        
        if std_val == 0:
            return anomalies
        
        threshold = mean_val - (self.config.threshold_multiplier * std_val)
        
        # Verifica valores que ficam abaixo do threshold
        for i, value in enumerate(data):
            if value < threshold:
                anomaly = {
                    'type': AnomalyType.DROP.value,
                    'timestamp': timestamps[i].isoformat(),
                    'value': value,
                    'threshold': threshold,
                    'mean': mean_val,
                    'std': std_val,
                    'severity': self._calculate_severity(threshold, value, mean_val)
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def detect_trend_anomaly(self, data: List[float], timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detecta anomalias de tendência"""
        anomalies = []
        
        if len(data) < self.config.min_data_points:
            return anomalies
        
        # Calcula tendência usando regressão linear
        x = np.arange(len(data))
        slope, intercept = np.polyfit(x, data, 1)
        
        # Calcula R² para verificar qualidade da tendência
        y_pred = slope * x + intercept
        r_squared = 1 - (np.sum((data - y_pred) ** 2) / np.sum((data - np.mean(data)) ** 2))
        
        # Se R² é alto e slope é significativo, pode ser uma tendência
        if r_squared > 0.7 and abs(slope) > self.config.trend_sensitivity:
            # Verifica se a tendência é anômala comparando com histórico
            if len(self.metrics_history.get('trends', [])) > 0:
                historical_slopes = [t['slope'] for t in self.metrics_history['trends']]
                mean_slope = np.mean(historical_slopes)
                std_slope = np.std(historical_slopes)
                
                if std_slope > 0 and abs(slope - mean_slope) > (self.config.threshold_multiplier * std_slope):
                    anomaly = {
                        'type': AnomalyType.TREND.value,
                        'timestamp': timestamps[-1].isoformat(),
                        'slope': slope,
                        'r_squared': r_squared,
                        'mean_slope': mean_slope,
                        'std_slope': std_slope,
                        'severity': self._calculate_severity(abs(slope), abs(mean_slope), std_slope)
                    }
                    anomalies.append(anomaly)
            
            # Armazena tendência atual no histórico
            if 'trends' not in self.metrics_history:
                self.metrics_history['trends'] = []
            
            self.metrics_history['trends'].append({
                'timestamp': timestamps[-1].isoformat(),
                'slope': slope,
                'r_squared': r_squared
            })
        
        return anomalies
    
    def detect_seasonal_anomaly(self, data: List[float], timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detecta anomalias sazonais"""
        anomalies = []
        
        if len(data) < self.config.seasonality_period:
            return anomalies
        
        # Calcula padrão sazonal
        seasonal_pattern = self._calculate_seasonal_pattern(data, self.config.seasonality_period)
        
        if seasonal_pattern is None:
            return anomalies
        
        # Compara valores atuais com o padrão sazonal
        for i, (value, timestamp) in enumerate(zip(data, timestamps)):
            if i < len(seasonal_pattern):
                expected_value = seasonal_pattern[i % self.config.seasonality_period]
                deviation = abs(value - expected_value)
                
                # Calcula threshold baseado na variabilidade do padrão
                pattern_std = np.std(seasonal_pattern)
                threshold = self.config.threshold_multiplier * pattern_std
                
                if deviation > threshold:
                    anomaly = {
                        'type': AnomalyType.SEASONAL.value,
                        'timestamp': timestamp.isoformat(),
                        'value': value,
                        'expected_value': expected_value,
                        'deviation': deviation,
                        'threshold': threshold,
                        'severity': self._calculate_severity(deviation, 0, pattern_std)
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def detect_outlier_anomaly(self, data: List[float], timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detecta outliers usando IQR"""
        anomalies = []
        
        if len(data) < self.config.min_data_points:
            return anomalies
        
        # Calcula quartis
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        # Define limites para outliers
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        
        # Identifica outliers
        for i, value in enumerate(data):
            if value < lower_bound or value > upper_bound:
                anomaly = {
                    'type': AnomalyType.OUTLIER.value,
                    'timestamp': timestamps[i].isoformat(),
                    'value': value,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'q1': q1,
                    'q3': q3,
                    'iqr': iqr,
                    'severity': self._calculate_severity(value, (lower_bound + upper_bound) / 2, iqr)
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_seasonal_pattern(self, data: List[float], period: int) -> Optional[List[float]]:
        """Calcula padrão sazonal"""
        if len(data) < period * 2:
            return None
        
        # Agrupa dados por posição no período
        seasonal_groups = [[] for _ in range(period)]
        
        for i, value in enumerate(data):
            seasonal_groups[i % period].append(value)
        
        # Calcula média para cada posição
        pattern = [np.mean(group) if group else 0 for group in seasonal_groups]
        
        return pattern
    
    def _calculate_severity(self, value: float, baseline: float, std: float) -> str:
        """Calcula severidade da anomalia"""
        if std == 0:
            return "low"
        
        deviation = abs(value - baseline) / std
        
        if deviation > 3:
            return "critical"
        elif deviation > 2:
            return "high"
        elif deviation > 1.5:
            return "medium"
        else:
            return "low"
    
    def detect_all_anomalies(self, data: List[float], timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Executa todas as detecções de anomalias"""
        all_anomalies = []
        
        # Detecta diferentes tipos de anomalias
        all_anomalies.extend(self.detect_spike_anomaly(data, timestamps))
        all_anomalies.extend(self.detect_drop_anomaly(data, timestamps))
        all_anomalies.extend(self.detect_trend_anomaly(data, timestamps))
        all_anomalies.extend(self.detect_seasonal_anomaly(data, timestamps))
        all_anomalies.extend(self.detect_outlier_anomaly(data, timestamps))
        
        # Remove duplicatas baseado em timestamp
        unique_anomalies = {}
        for anomaly in all_anomalies:
            timestamp = anomaly['timestamp']
            if timestamp not in unique_anomalies:
                unique_anomalies[timestamp] = anomaly
            else:
                # Mantém a anomalia com maior severidade
                current_severity = self._severity_to_numeric(unique_anomalies[timestamp]['severity'])
                new_severity = self._severity_to_numeric(anomaly['severity'])
                if new_severity > current_severity:
                    unique_anomalies[timestamp] = anomaly
        
        return list(unique_anomalies.values())
    
    def _severity_to_numeric(self, severity: str) -> int:
        """Converte severidade para valor numérico"""
        severity_map = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return severity_map.get(severity, 0)

class MetricsCollector:
    """Coletor de métricas"""
    
    def __init__(self, data_source: str = 'prometheus'):
        self.data_source = data_source
        self.metrics_cache = {}
    
    def collect_metrics(self, metric_name: str, start_time: datetime, end_time: datetime) -> Tuple[List[float], List[datetime]]:
        """Coleta métricas do sistema"""
        # Simula coleta de métricas (em produção, conectaria com Prometheus/InfluxDB)
        logger.info(f"Coletando métricas para {metric_name} de {start_time} até {end_time}")
        
        # Gera dados simulados
        time_delta = end_time - start_time
        num_points = int(time_delta.total_seconds() / 60)  # 1 ponto por minuto
        
        timestamps = [start_time + timedelta(minutes=i) for i in range(num_points)]
        
        # Simula diferentes padrões de métricas
        if 'cpu' in metric_name.lower():
            data = self._generate_cpu_data(num_points)
        elif 'memory' in metric_name.lower():
            data = self._generate_memory_data(num_points)
        elif 'response_time' in metric_name.lower():
            data = self._generate_response_time_data(num_points)
        elif 'error_rate' in metric_name.lower():
            data = self._generate_error_rate_data(num_points)
        else:
            data = self._generate_generic_data(num_points)
        
        return data, timestamps
    
    def _generate_cpu_data(self, num_points: int) -> List[float]:
        """Gera dados simulados de CPU"""
        base_cpu = 30.0
        noise = np.random.normal(0, 5, num_points)
        trend = np.linspace(0, 10, num_points)  # Tendência crescente
        seasonal = 5 * np.sin(np.linspace(0, 4*np.pi, num_points))  # Padrão sazonal
        
        # Adiciona algumas anomalias
        data = base_cpu + noise + trend + seasonal
        
        # Adiciona spikes aleatórios
        spike_indices = np.random.choice(num_points, size=num_points//20, replace=False)
        data[spike_indices] += np.random.uniform(20, 40, len(spike_indices))
        
        return data.tolist()
    
    def _generate_memory_data(self, num_points: int) -> List[float]:
        """Gera dados simulados de memória"""
        base_memory = 60.0
        noise = np.random.normal(0, 3, num_points)
        trend = np.linspace(0, 5, num_points)  # Tendência crescente suave
        
        data = base_memory + noise + trend
        
        # Adiciona algumas quedas
        drop_indices = np.random.choice(num_points, size=num_points//30, replace=False)
        data[drop_indices] -= np.random.uniform(10, 20, len(drop_indices))
        
        return data.tolist()
    
    def _generate_response_time_data(self, num_points: int) -> List[float]:
        """Gera dados simulados de tempo de resposta"""
        base_response_time = 0.2
        noise = np.random.normal(0, 0.05, num_points)
        
        data = base_response_time + noise
        
        # Adiciona alguns picos de latência
        spike_indices = np.random.choice(num_points, size=num_points//25, replace=False)
        data[spike_indices] += np.random.uniform(0.5, 2.0, len(spike_indices))
        
        return data.tolist()
    
    def _generate_error_rate_data(self, num_points: int) -> List[float]:
        """Gera dados simulados de taxa de erro"""
        base_error_rate = 0.01
        noise = np.random.normal(0, 0.005, num_points)
        
        data = base_error_rate + noise
        
        # Adiciona alguns picos de erro
        spike_indices = np.random.choice(num_points, size=num_points//40, replace=False)
        data[spike_indices] += np.random.uniform(0.05, 0.15, len(spike_indices))
        
        return data.tolist()
    
    def _generate_generic_data(self, num_points: int) -> List[float]:
        """Gera dados genéricos"""
        base_value = 50.0
        noise = np.random.normal(0, 10, num_points)
        trend = np.linspace(0, 5, num_points)
        
        data = base_value + noise + trend
        
        return data.tolist()

class AnomalyReporter:
    """Relator de anomalias"""
    
    def __init__(self, output_format: str = 'json'):
        self.output_format = output_format
    
    def generate_report(self, anomalies: List[Dict[str, Any]], metric_name: str) -> str:
        """Gera relatório de anomalias"""
        if not anomalies:
            return "Nenhuma anomalia detectada."
        
        # Agrupa anomalias por tipo
        anomalies_by_type = {}
        for anomaly in anomalies:
            anomaly_type = anomaly['type']
            if anomaly_type not in anomalies_by_type:
                anomalies_by_type[anomaly_type] = []
            anomalies_by_type[anomaly_type].append(anomaly)
        
        # Gera relatório
        report = []
        report.append(f"# Relatório de Anomalias - {metric_name}")
        report.append(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total de Anomalias**: {len(anomalies)}")
        report.append("")
        
        # Resumo por tipo
        report.append("## Resumo por Tipo")
        for anomaly_type, type_anomalies in anomalies_by_type.items():
            report.append(f"- **{anomaly_type.title()}**: {len(type_anomalies)} anomalias")
        report.append("")
        
        # Detalhes por tipo
        for anomaly_type, type_anomalies in anomalies_by_type.items():
            report.append(f"## Anomalias {anomaly_type.title()}")
            
            # Ordena por severidade
            type_anomalies.sort(key=lambda x: self._severity_to_numeric(x['severity']), reverse=True)
            
            for i, anomaly in enumerate(type_anomalies[:10], 1):  # Top 10
                report.append(f"### {i}. Anomalia {anomaly['severity'].title()}")
                report.append(f"- **Timestamp**: {anomaly['timestamp']}")
                report.append(f"- **Valor**: {anomaly.get('value', 'N/A')}")
                report.append(f"- **Severidade**: {anomaly['severity']}")
                
                # Adiciona detalhes específicos do tipo
                if anomaly_type == 'spike':
                    report.append(f"- **Threshold**: {anomaly.get('threshold', 'N/A')}")
                elif anomaly_type == 'trend':
                    report.append(f"- **Slope**: {anomaly.get('slope', 'N/A')}")
                elif anomaly_type == 'outlier':
                    report.append(f"- **IQR**: {anomaly.get('iqr', 'N/A')}")
                
                report.append("")
        
        return "\n".join(report)
    
    def _severity_to_numeric(self, severity: str) -> int:
        """Converte severidade para valor numérico"""
        severity_map = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return severity_map.get(severity, 0)
    
    def save_report(self, report: str, filename: str = None) -> str:
        """Salva relatório em arquivo"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"anomaly_report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Detector de Anomalias')
    parser.add_argument('--metric', required=True, help='Nome da métrica para analisar')
    parser.add_argument('--start-time', required=True, help='Hora de início (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-time', required=True, help='Hora de fim (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--config', default=None, help='Arquivo de configuração YAML')
    parser.add_argument('--output', default=None, help='Arquivo de saída')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown', help='Formato de saída')
    
    args = parser.parse_args()
    
    # Parse timestamps
    start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')
    
    # Carrega configuração
    config = AnomalyDetectionConfig()
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config_data = yaml.safe_load(f)
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    # Inicializa componentes
    detector = AnomalyDetector(config)
    collector = MetricsCollector()
    reporter = AnomalyReporter(args.format)
    
    # Coleta métricas
    logger.info("Coletando métricas...")
    data, timestamps = collector.collect_metrics(args.metric, start_time, end_time)
    
    # Detecta anomalias
    logger.info("Detectando anomalias...")
    anomalies = detector.detect_all_anomalies(data, timestamps)
    
    # Gera relatório
    logger.info("Gerando relatório...")
    if args.format == 'json':
        report = json.dumps(anomalies, indent=2, default=str)
    else:
        report = reporter.generate_report(anomalies, args.metric)
    
    # Salva relatório
    output_file = reporter.save_report(report, args.output)
    
    logger.info(f"Relatório salvo em: {output_file}")
    logger.info(f"Detectadas {len(anomalies)} anomalias")
    
    # Exibe resumo
    if anomalies:
        print(f"\n📊 Resumo de Anomalias:")
        print(f"   Total: {len(anomalies)}")
        
        by_type = {}
        by_severity = {}
        
        for anomaly in anomalies:
            anomaly_type = anomaly['type']
            severity = anomaly['severity']
            
            by_type[anomaly_type] = by_type.get(anomaly_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        print(f"   Por tipo: {by_type}")
        print(f"   Por severidade: {by_severity}")
    else:
        print("\n✅ Nenhuma anomalia detectada")

if __name__ == "__main__":
    main() 