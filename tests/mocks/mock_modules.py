"""
Mocks para módulos externos - Omni Keywords Finder

Baseado no código real do sistema para garantir
que os testes sejam representativos.
"""

import time
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, MagicMock


class MockPyTrends:
    """Mock para pytrends.request.TrendReq"""
    
    def __init__(self, hl='pt-BR', tz=360, timeout=(10, 25), retries=2, backoff_factor=0.1):
        self.hl = hl
        self.tz = tz
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.build_payload_called = False
        self.interest_over_time_called = False
        self.related_queries_called = False
    
    def build_payload(self, kw_list, cat=0, timeframe='today 12-m', geo=''):
        """Mock para build_payload"""
        self.build_payload_called = True
        self.kw_list = kw_list
        self.cat = cat
        self.timeframe = timeframe
        self.geo = geo
        return True
    
    def interest_over_time(self):
        """Mock para interest_over_time"""
        self.interest_over_time_called = True
        return MockDataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'teste': [50, 75]
        })
    
    def related_queries(self):
        """Mock para related_queries"""
        self.related_queries_called = True
        return {
            'teste': {
                'top': MockDataFrame({
                    'query': ['teste1', 'teste2'],
                    'value': [100, 80]
                }),
                'rising': MockDataFrame({
                    'query': ['teste3', 'teste4'],
                    'value': [200, 150]
                })
            }
        }


class MockDataFrame:
    """Mock para pandas.DataFrame"""
    
    def __init__(self, data: Dict[str, List]):
        self.data = data
        self.columns = list(data.keys())
    
    def to_dict(self, orient='records'):
        """Mock para to_dict"""
        records = []
        for i in range(len(next(iter(self.data.values())))):
            record = {}
            for col in self.columns:
                record[col] = self.data[col][i]
            records.append(record)
        return records
    
    def __len__(self):
        """Mock para len"""
        return len(next(iter(self.data.values())))
    
    def empty(self):
        """Mock para empty"""
        return len(self) == 0


class MockGoogleKeywordPlanner:
    """Mock para GoogleKeywordPlannerColetor"""
    
    def __init__(self):
        self.nome = "google_keyword_planner"
        self.config = {"limite_padrao": 100}
    
    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[str]:
        """Mock para coletar_keywords"""
        return [f"keyword_{termo}_1", f"keyword_{termo}_2"]
    
    async def coletar(self, termo: str, session=None) -> List[str]:
        """Mock para coletar"""
        return await self.coletar_keywords(termo)


class MockGoogleSuggest:
    """Mock para GoogleSuggestColetor"""
    
    def __init__(self):
        self.nome = "google_suggest"
        self.config = {"limite_padrao": 100}
    
    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[str]:
        """Mock para coletar_keywords"""
        return [f"suggest_{termo}_1", f"suggest_{termo}_2"]
    
    async def coletar(self, termo: str, session=None) -> List[str]:
        """Mock para coletar"""
        return await self.coletar_keywords(termo)


class MockGoogleTrends:
    """Mock para GoogleTrendsColetor"""
    
    def __init__(self):
        self.nome = "google_trends"
        self.config = {"janela_analise": 90, "pais": "BR"}
    
    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[str]:
        """Mock para coletar_keywords"""
        return [f"trend_{termo}_1", f"trend_{termo}_2"]
    
    async def coletar(self, termo: str, session=None) -> List[str]:
        """Mock para coletar"""
        return await self.coletar_keywords(termo)


class MockProcessadorOrquestrador:
    """Mock para ProcessadorOrquestrador"""
    
    def __init__(self):
        self.nome = "processador_orquestrador"
    
    async def processar_keywords(self, keywords: List[str], nicho: str) -> Dict[str, Any]:
        """Mock para processar_keywords"""
        return {
            "keywords": [f"processed_{kw}" for kw in keywords],
            "nicho": nicho,
            "total_processadas": len(keywords)
        }


class MockExportadorKeywords:
    """Mock para ExportadorKeywords"""
    
    def __init__(self):
        self.nome = "exportador_keywords"
    
    async def exportar_keywords(self, keywords: List[str], nicho: str, formatos: List[str]) -> Dict[str, Any]:
        """Mock para exportar_keywords"""
        return {
            "arquivos": {fmt: f"file1.{fmt}" for fmt in formatos},
            "nicho": nicho,
            "total_exportado": len(keywords)
        }


class MockAnomalyDetector:
    """Mock para AnomalyDetector"""
    
    def __init__(self):
        self.nome = "anomaly_detector"
    
    def detect_anomaly(self, value: float, metric_name: str = "unknown"):
        """Mock para detect_anomaly"""
        return MockAnomalyResult(
            is_anomaly=False,
            confidence=0.95,
            score=0.1
        )


class MockAnomalyResult:
    """Mock para AnomalyResult"""
    
    def __init__(self, is_anomaly: bool, confidence: float, score: float):
        self.is_anomaly = is_anomaly
        self.confidence = confidence
        self.score = score


class MockPredictiveMonitor:
    """Mock para PredictiveMonitor"""
    
    def __init__(self):
        self.nome = "predictive_monitor"
    
    def predict_metric(self, metric_name: str, horizon_hours: Optional[int] = None):
        """Mock para predict_metric"""
        return MockPredictionResult(
            metric_name=metric_name,
            predicted_value=100.0,
            confidence="high"
        )


class MockPredictionResult:
    """Mock para PredictionResult"""
    
    def __init__(self, metric_name: str, predicted_value: float, confidence: str):
        self.metric_name = metric_name
        self.predicted_value = predicted_value
        self.confidence = confidence
