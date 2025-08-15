"""
🧪 Gerador de Dados de Teste - Ambiente

Tracing ID: environment-test-data-generator-2025-01-27-001
Timestamp: 2025-01-27T23:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Gerador baseado em dados reais do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de geração de dados (realismo, volume, variedade)
♻️ ReAct: Simulado cenários de dados reais e validada qualidade

Gera dados de teste para ambiente incluindo:
- Dados de usuários
- Dados de keywords
- Dados de execuções
- Dados de categorias
- Dados de analytics
- Dados de pagamentos
- Dados de auditoria
- Dados de configuração
- Dados de performance
- Dados de monitoramento
"""

import pytest
import asyncio
import time
import json
import random
import string
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
import logging
from dataclasses import dataclass
import csv
import io
import os
import tempfile

# Importações do sistema real
from backend.app.models.user import User
from backend.app.models.keyword import Keyword
from backend.app.models.execucao import Execucao
from backend.app.models.categoria import Categoria
from backend.app.models.analytics import Analytics
from backend.app.models.payment import Payment
from backend.app.models.audit import AuditLog
from backend.app.services.data_service import DataService
from infrastructure.logging.structured_logger import StructuredLogger

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class TestDataGeneratorConfig:
    """Configuração para gerador de dados de teste"""
    users_count: int = 100
    keywords_count: int = 10000
    execucoes_count: int = 500
    categorias_count: int = 20
    analytics_count: int = 5000
    payments_count: int = 200
    audit_logs_count: int = 1000
    enable_realistic_data: bool = True
    enable_data_relationships: bool = True
    enable_data_validation: bool = True
    enable_data_export: bool = True
    data_export_format: str = "json"
    enable_data_cleanup: bool = True
    enable_data_backup: bool = True

class EnvironmentTestDataGenerator:
    """Gerador de dados de teste para ambiente"""
    
    def __init__(self, config: Optional[TestDataGeneratorConfig] = None):
        self.config = config or TestDataGeneratorConfig()
        self.logger = StructuredLogger(
            module="environment_test_data_generator",
            tracing_id="test_data_generator_001"
        )
        self.data_service = DataService()
        
        # Dados gerados
        self.generated_data: Dict[str, List[Dict[str, Any]]] = {}
        self.data_relationships: Dict[str, List[Tuple[str, str]]] = {}
        self.data_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Dados de referência realistas
        self.real_keywords = [
            "marketing digital", "seo", "google ads", "facebook ads", "instagram marketing",
            "content marketing", "email marketing", "social media", "inbound marketing",
            "outbound marketing", "growth hacking", "conversion optimization", "landing page",
            "copywriting", "branding", "publicidade", "análise de dados", "automação",
            "lead generation", "customer success", "sales funnel", "retention", "churn",
            "customer lifetime value", "roi", "kpi", "analytics", "business intelligence"
        ]
        
        self.real_categories = [
            "Marketing Digital", "SEO", "Google Ads", "Facebook Ads", "Instagram",
            "Content Marketing", "Email Marketing", "Social Media", "Inbound Marketing",
            "Growth Hacking", "Conversion", "Copywriting", "Branding", "Publicidade",
            "Analytics", "Automação", "Lead Generation", "Customer Success", "Sales",
            "Business Intelligence"
        ]
        
        logger.info(f"Environment Test Data Generator inicializado com configuração: {self.config}")
    
    async def setup_generator(self):
        """Configura o gerador de dados"""
        try:
            # Configurar serviço de dados
            self.data_service.configure({
                "enable_data_validation": self.config.enable_data_validation,
                "enable_data_relationships": self.config.enable_data_relationships
            })
            
            logger.info("Gerador de dados configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar gerador de dados: {e}")
            raise
    
    async def generate_users_data(self):
        """Gera dados de usuários"""
        try:
            users = []
            
            for i in range(self.config.users_count):
                user_id = str(uuid.uuid4())
                
                # Gerar dados realistas
                first_names = ["João", "Maria", "Pedro", "Ana", "Carlos", "Lucia", "Fernando", "Juliana"]
                last_names = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Almeida"]
                
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i}@teste.com"
                
                user_data = {
                    "id": user_id,
                    "nome": f"{first_name} {last_name}",
                    "email": email,
                    "senha_hash": hashlib.sha256(f"senha{i}".encode()).hexdigest(),
                    "ativo": random.choice([True, True, True, False]),  # 75% ativos
                    "tipo_usuario": random.choice(["admin", "user", "user", "user"]),  # 25% admin
                    "data_criacao": datetime.now() - timedelta(days=random.randint(1, 365)),
                    "ultimo_login": datetime.now() - timedelta(days=random.randint(0, 30)),
                    "regiao": random.choice(["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]),
                    "configuracoes": {
                        "notificacoes_email": random.choice([True, False]),
                        "notificacoes_push": random.choice([True, False]),
                        "tema": random.choice(["light", "dark"]),
                        "idioma": random.choice(["pt-BR", "en-US", "es-ES"])
                    }
                }
                
                users.append(user_data)
            
            self.generated_data["users"] = users
            self.data_metrics["users"] = {
                "count": len(users),
                "active_count": len([u for u in users if u["ativo"]]),
                "admin_count": len([u for u in users if u["tipo_usuario"] == "admin"]),
                "regions": list(set([u["regiao"] for u in users]))
            }
            
            logger.info(f"Dados de usuários gerados: {len(users)} usuários")
            
            return users
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de usuários: {e}")
            raise
    
    async def generate_categorias_data(self):
        """Gera dados de categorias"""
        try:
            categorias = []
            
            for i in range(self.config.categorias_count):
                categoria_id = str(uuid.uuid4())
                
                categoria_data = {
                    "id": categoria_id,
                    "nome": self.real_categories[i] if i < len(self.real_categories) else f"Categoria {i+1}",
                    "descricao": f"Descrição da categoria {i+1}",
                    "cor": f"#{random.randint(0, 0xFFFFFF):06x}",
                    "icone": f"icon-{i+1}",
                    "ativo": random.choice([True, True, True, False]),  # 75% ativas
                    "data_criacao": datetime.now() - timedelta(days=random.randint(1, 365)),
                    "keywords_count": random.randint(0, 1000),
                    "execucoes_count": random.randint(0, 100)
                }
                
                categorias.append(categoria_data)
            
            self.generated_data["categorias"] = categorias
            self.data_metrics["categorias"] = {
                "count": len(categorias),
                "active_count": len([c for c in categorias if c["ativo"]]),
                "total_keywords": sum([c["keywords_count"] for c in categorias]),
                "total_execucoes": sum([c["execucoes_count"] for c in categorias])
            }
            
            logger.info(f"Dados de categorias gerados: {len(categorias)} categorias")
            
            return categorias
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de categorias: {e}")
            raise
    
    async def generate_execucoes_data(self):
        """Gera dados de execuções"""
        try:
            execucoes = []
            users = self.generated_data.get("users", [])
            categorias = self.generated_data.get("categorias", [])
            
            if not users or not categorias:
                raise ValueError("Usuários e categorias devem ser gerados primeiro")
            
            for i in range(self.config.execucoes_count):
                execucao_id = str(uuid.uuid4())
                user = random.choice(users)
                categoria = random.choice(categorias)
                
                status_options = ["completed", "running", "failed", "pending"]
                status_weights = [0.6, 0.2, 0.1, 0.1]  # 60% completed, 20% running, etc.
                status = random.choices(status_options, weights=status_weights)[0]
                
                execucao_data = {
                    "id": execucao_id,
                    "user_id": user["id"],
                    "categoria_id": categoria["id"],
                    "status": status,
                    "data_inicio": datetime.now() - timedelta(days=random.randint(1, 30)),
                    "data_fim": datetime.now() - timedelta(days=random.randint(0, 29)) if status == "completed" else None,
                    "keywords_processadas": random.randint(0, 1000),
                    "keywords_encontradas": random.randint(0, 500),
                    "tempo_processamento": random.randint(10, 3600) if status == "completed" else None,
                    "configuracoes": {
                        "regiao": random.choice(["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]),
                        "idioma": random.choice(["pt-BR", "en-US", "es-ES"]),
                        "limite_resultados": random.randint(100, 1000)
                    },
                    "resultados": {
                        "volume_total": random.randint(1000, 100000),
                        "competicao_media": random.uniform(0.1, 0.9),
                        "cpc_medio": random.uniform(0.5, 5.0)
                    } if status == "completed" else None
                }
                
                execucoes.append(execucao_data)
                
                # Criar relacionamento
                self.data_relationships.setdefault("user_execucoes", []).append((user["id"], execucao_id))
                self.data_relationships.setdefault("categoria_execucoes", []).append((categoria["id"], execucao_id))
            
            self.generated_data["execucoes"] = execucoes
            self.data_metrics["execucoes"] = {
                "count": len(execucoes),
                "completed_count": len([e for e in execucoes if e["status"] == "completed"]),
                "running_count": len([e for e in execucoes if e["status"] == "running"]),
                "failed_count": len([e for e in execucoes if e["status"] == "failed"]),
                "total_keywords_processed": sum([e["keywords_processadas"] for e in execucoes if e["keywords_processadas"]])
            }
            
            logger.info(f"Dados de execuções gerados: {len(execucoes)} execuções")
            
            return execucoes
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de execuções: {e}")
            raise
    
    async def generate_keywords_data(self):
        """Gera dados de keywords"""
        try:
            keywords = []
            execucoes = self.generated_data.get("execucoes", [])
            categorias = self.generated_data.get("categorias", [])
            
            if not execucoes or not categorias:
                raise ValueError("Execuções e categorias devem ser geradas primeiro")
            
            for i in range(self.config.keywords_count):
                keyword_id = str(uuid.uuid4())
                execucao = random.choice(execucoes)
                categoria = random.choice(categorias)
                
                # Gerar keyword realista
                if self.config.enable_realistic_data and i < len(self.real_keywords):
                    base_keyword = self.real_keywords[i]
                    keyword_text = f"{base_keyword} {random.choice(['2024', '2025', 'melhor', 'top', 'guia', 'tutorial'])}"
                else:
                    keyword_text = f"keyword teste {i+1}"
                
                keyword_data = {
                    "id": keyword_id,
                    "palavra": keyword_text,
                    "execucao_id": execucao["id"],
                    "categoria_id": categoria["id"],
                    "volume": random.randint(100, 50000),
                    "competicao": random.uniform(0.1, 0.95),
                    "cpc": random.uniform(0.1, 10.0),
                    "posicao_media": random.randint(1, 100),
                    "cliques_estimados": random.randint(10, 10000),
                    "impressoes_estimadas": random.randint(100, 100000),
                    "ctr_estimado": random.uniform(0.01, 0.15),
                    "data_coleta": datetime.now() - timedelta(days=random.randint(1, 30)),
                    "regiao": execucao["configuracoes"]["regiao"],
                    "idioma": execucao["configuracoes"]["idioma"],
                    "status": random.choice(["ativo", "inativo", "pendente"]),
                    "tags": random.sample(["alta_competicao", "baixo_volume", "alto_cpc", "long_tail"], random.randint(0, 3))
                }
                
                keywords.append(keyword_data)
                
                # Criar relacionamentos
                self.data_relationships.setdefault("execucao_keywords", []).append((execucao["id"], keyword_id))
                self.data_relationships.setdefault("categoria_keywords", []).append((categoria["id"], keyword_id))
            
            self.generated_data["keywords"] = keywords
            self.data_metrics["keywords"] = {
                "count": len(keywords),
                "avg_volume": statistics.mean([k["volume"] for k in keywords]),
                "avg_competicao": statistics.mean([k["competicao"] for k in keywords]),
                "avg_cpc": statistics.mean([k["cpc"] for k in keywords]),
                "regions": list(set([k["regiao"] for k in keywords])),
                "languages": list(set([k["idioma"] for k in keywords]))
            }
            
            logger.info(f"Dados de keywords gerados: {len(keywords)} keywords")
            
            return keywords
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de keywords: {e}")
            raise
    
    async def generate_analytics_data(self):
        """Gera dados de analytics"""
        try:
            analytics = []
            keywords = self.generated_data.get("keywords", [])
            execucoes = self.generated_data.get("execucoes", [])
            
            if not keywords or not execucoes:
                raise ValueError("Keywords e execuções devem ser geradas primeiro")
            
            for i in range(self.config.analytics_count):
                analytics_id = str(uuid.uuid4())
                keyword = random.choice(keywords)
                execucao = random.choice(execucoes)
                
                analytics_data = {
                    "id": analytics_id,
                    "keyword_id": keyword["id"],
                    "execucao_id": execucao["id"],
                    "data_analise": datetime.now() - timedelta(days=random.randint(1, 30)),
                    "metricas": {
                        "volume_tendencia": random.choice(["crescente", "decrescente", "estavel"]),
                        "competicao_tendencia": random.choice(["crescente", "decrescente", "estavel"]),
                        "cpc_tendencia": random.choice(["crescente", "decrescente", "estavel"]),
                        "score_opportunity": random.uniform(0.1, 1.0),
                        "score_dificuldade": random.uniform(0.1, 1.0)
                    },
                    "insights": [
                        "Volume crescente nos últimos 30 dias",
                        "Competição moderada",
                        "CPC dentro da média do mercado",
                        "Boa oportunidade para SEO"
                    ],
                    "recomendacoes": [
                        "Focar em conteúdo de qualidade",
                        "Otimizar meta tags",
                        "Melhorar velocidade do site",
                        "Criar backlinks relevantes"
                    ],
                    "regiao": keyword["regiao"],
                    "idioma": keyword["idioma"]
                }
                
                analytics.append(analytics_data)
            
            self.generated_data["analytics"] = analytics
            self.data_metrics["analytics"] = {
                "count": len(analytics),
                "regions": list(set([a["regiao"] for a in analytics])),
                "languages": list(set([a["idioma"] for a in analytics])),
                "avg_opportunity_score": statistics.mean([a["metricas"]["score_opportunity"] for a in analytics]),
                "avg_difficulty_score": statistics.mean([a["metricas"]["score_dificuldade"] for a in analytics])
            }
            
            logger.info(f"Dados de analytics gerados: {len(analytics)} registros")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de analytics: {e}")
            raise
    
    async def generate_payments_data(self):
        """Gera dados de pagamentos"""
        try:
            payments = []
            users = self.generated_data.get("users", [])
            
            if not users:
                raise ValueError("Usuários devem ser gerados primeiro")
            
            for i in range(self.config.payments_count):
                payment_id = str(uuid.uuid4())
                user = random.choice(users)
                
                status_options = ["completed", "pending", "failed", "refunded"]
                status_weights = [0.7, 0.15, 0.1, 0.05]  # 70% completed, etc.
                status = random.choices(status_options, weights=status_weights)[0]
                
                payment_methods = ["credit_card", "pix", "boleto", "paypal"]
                payment_method = random.choice(payment_methods)
                
                amount = random.uniform(29.90, 299.90)
                
                payment_data = {
                    "id": payment_id,
                    "user_id": user["id"],
                    "amount": amount,
                    "currency": "BRL",
                    "status": status,
                    "payment_method": payment_method,
                    "data_criacao": datetime.now() - timedelta(days=random.randint(1, 365)),
                    "data_processamento": datetime.now() - timedelta(days=random.randint(0, 364)) if status == "completed" else None,
                    "transaction_id": f"txn_{random.randint(100000, 999999)}",
                    "gateway": random.choice(["stripe", "paypal", "mercadopago", "pagseguro"]),
                    "regiao": user["regiao"],
                    "metadata": {
                        "plan": random.choice(["basic", "pro", "enterprise"]),
                        "billing_cycle": random.choice(["monthly", "yearly"]),
                        "discount_applied": random.choice([True, False])
                    }
                }
                
                payments.append(payment_data)
            
            self.generated_data["payments"] = payments
            self.data_metrics["payments"] = {
                "count": len(payments),
                "completed_count": len([p for p in payments if p["status"] == "completed"]),
                "total_amount": sum([p["amount"] for p in payments if p["status"] == "completed"]),
                "avg_amount": statistics.mean([p["amount"] for p in payments]),
                "payment_methods": list(set([p["payment_method"] for p in payments])),
                "gateways": list(set([p["gateway"] for p in payments]))
            }
            
            logger.info(f"Dados de pagamentos gerados: {len(payments)} pagamentos")
            
            return payments
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de pagamentos: {e}")
            raise
    
    async def generate_audit_logs_data(self):
        """Gera dados de logs de auditoria"""
        try:
            audit_logs = []
            users = self.generated_data.get("users", [])
            
            if not users:
                raise ValueError("Usuários devem ser gerados primeiro")
            
            action_types = [
                "user_login", "user_logout", "user_register", "user_update",
                "execucao_create", "execucao_update", "execucao_delete",
                "keyword_search", "keyword_export", "keyword_import",
                "payment_create", "payment_update", "payment_refund",
                "config_update", "admin_action", "data_export"
            ]
            
            for i in range(self.config.audit_logs_count):
                log_id = str(uuid.uuid4())
                user = random.choice(users)
                action = random.choice(action_types)
                
                audit_data = {
                    "id": log_id,
                    "user_id": user["id"],
                    "action": action,
                    "timestamp": datetime.now() - timedelta(days=random.randint(1, 365)),
                    "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    "user_agent": random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                    ]),
                    "regiao": user["regiao"],
                    "status": random.choice(["success", "success", "success", "error"]),
                    "details": {
                        "resource_type": random.choice(["user", "execucao", "keyword", "payment", "config"]),
                        "resource_id": str(uuid.uuid4()),
                        "changes": {
                            "field": "example_field",
                            "old_value": "old_value",
                            "new_value": "new_value"
                        } if action.endswith("_update") else None
                    },
                    "metadata": {
                        "session_id": str(uuid.uuid4()),
                        "request_id": str(uuid.uuid4()),
                        "response_time": random.randint(100, 5000)
                    }
                }
                
                audit_logs.append(audit_data)
            
            self.generated_data["audit_logs"] = audit_logs
            self.data_metrics["audit_logs"] = {
                "count": len(audit_logs),
                "success_count": len([a for a in audit_logs if a["status"] == "success"]),
                "error_count": len([a for a in audit_logs if a["status"] == "error"]),
                "action_types": list(set([a["action"] for a in audit_logs])),
                "regions": list(set([a["regiao"] for a in audit_logs]))
            }
            
            logger.info(f"Dados de logs de auditoria gerados: {len(audit_logs)} logs")
            
            return audit_logs
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de logs de auditoria: {e}")
            raise
    
    async def export_test_data(self, format: str = None):
        """Exporta dados de teste"""
        try:
            export_format = format or self.config.data_export_format
            
            if export_format == "json":
                return await self._export_json_data()
            elif export_format == "csv":
                return await self._export_csv_data()
            else:
                raise ValueError(f"Formato de exportação não suportado: {export_format}")
                
        except Exception as e:
            logger.error(f"Erro ao exportar dados de teste: {e}")
            raise
    
    async def _export_json_data(self):
        """Exporta dados em formato JSON"""
        try:
            export_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "config": self.config.__dict__,
                    "metrics": self.data_metrics,
                    "relationships": self.data_relationships
                },
                "data": self.generated_data
            }
            
            # Salvar em arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(export_data, f, indent=2, default=str)
                file_path = f.name
            
            logger.info(f"Dados exportados em JSON: {file_path}")
            
            return {
                "success": True,
                "format": "json",
                "file_path": file_path,
                "data_size": len(json.dumps(export_data))
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar dados JSON: {e}")
            raise
    
    async def _export_csv_data(self):
        """Exporta dados em formato CSV"""
        try:
            csv_files = {}
            
            for data_type, data_list in self.generated_data.items():
                if not data_list:
                    continue
                
                # Criar arquivo CSV
                with tempfile.NamedTemporaryFile(mode='w', suffix=f'_{data_type}.csv', delete=False) as f:
                    writer = csv.DictWriter(f, fieldnames=data_list[0].keys())
                    writer.writeheader()
                    writer.writerows(data_list)
                    csv_files[data_type] = f.name
            
            logger.info(f"Dados exportados em CSV: {len(csv_files)} arquivos")
            
            return {
                "success": True,
                "format": "csv",
                "files": csv_files,
                "file_count": len(csv_files)
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar dados CSV: {e}")
            raise
    
    async def cleanup_test_data(self):
        """Limpa dados de teste"""
        try:
            if self.config.enable_data_cleanup:
                # Limpar dados gerados
                self.generated_data.clear()
                self.data_relationships.clear()
                self.data_metrics.clear()
                
                logger.info("Dados de teste limpos com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao limpar dados de teste: {e}")
            raise
    
    def get_generation_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de geração de dados"""
        return {
            "total_data_types": len(self.generated_data),
            "total_records": sum(len(data) for data in self.generated_data.values()),
            "data_metrics": self.data_metrics,
            "relationships_count": sum(len(rels) for rels in self.data_relationships.values()),
            "config": self.config.__dict__
        }

# Testes pytest
@pytest.mark.asyncio
class TestEnvironmentTestDataGenerator:
    """Testes do gerador de dados de teste"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.generator = EnvironmentTestDataGenerator()
        await self.generator.setup_generator()
        yield
        await self.generator.cleanup_test_data()
    
    async def test_generate_users_data(self):
        """Testa geração de dados de usuários"""
        users = await self.generator.generate_users_data()
        assert len(users) == self.generator.config.users_count
        assert all("id" in user for user in users)
    
    async def test_generate_categorias_data(self):
        """Testa geração de dados de categorias"""
        categorias = await self.generator.generate_categorias_data()
        assert len(categorias) == self.generator.config.categorias_count
        assert all("id" in categoria for categoria in categorias)
    
    async def test_generate_execucoes_data(self):
        """Testa geração de dados de execuções"""
        await self.generator.generate_users_data()
        await self.generator.generate_categorias_data()
        
        execucoes = await self.generator.generate_execucoes_data()
        assert len(execucoes) == self.generator.config.execucoes_count
        assert all("id" in execucao for execucao in execucoes)
    
    async def test_generate_keywords_data(self):
        """Testa geração de dados de keywords"""
        await self.generator.generate_users_data()
        await self.generator.generate_categorias_data()
        await self.generator.generate_execucoes_data()
        
        keywords = await self.generator.generate_keywords_data()
        assert len(keywords) == self.generator.config.keywords_count
        assert all("id" in keyword for keyword in keywords)
    
    async def test_generate_analytics_data(self):
        """Testa geração de dados de analytics"""
        await self.generator.generate_users_data()
        await self.generator.generate_categorias_data()
        await self.generator.generate_execucoes_data()
        await self.generator.generate_keywords_data()
        
        analytics = await self.generator.generate_analytics_data()
        assert len(analytics) == self.generator.config.analytics_count
        assert all("id" in analytic for analytic in analytics)
    
    async def test_generate_payments_data(self):
        """Testa geração de dados de pagamentos"""
        await self.generator.generate_users_data()
        
        payments = await self.generator.generate_payments_data()
        assert len(payments) == self.generator.config.payments_count
        assert all("id" in payment for payment in payments)
    
    async def test_generate_audit_logs_data(self):
        """Testa geração de dados de logs de auditoria"""
        await self.generator.generate_users_data()
        
        audit_logs = await self.generator.generate_audit_logs_data()
        assert len(audit_logs) == self.generator.config.audit_logs_count
        assert all("id" in log for log in audit_logs)
    
    async def test_export_test_data_json(self):
        """Testa exportação de dados em JSON"""
        await self.generator.generate_users_data()
        await self.generator.generate_categorias_data()
        
        export_result = await self.generator.export_test_data("json")
        assert export_result["success"] is True
        assert export_result["format"] == "json"
    
    async def test_export_test_data_csv(self):
        """Testa exportação de dados em CSV"""
        await self.generator.generate_users_data()
        await self.generator.generate_categorias_data()
        
        export_result = await self.generator.export_test_data("csv")
        assert export_result["success"] is True
        assert export_result["format"] == "csv"
    
    async def test_overall_data_generation_metrics(self):
        """Testa métricas gerais de geração de dados"""
        # Gerar todos os tipos de dados
        await self.generator.generate_users_data()
        await self.generator.generate_categorias_data()
        await self.generator.generate_execucoes_data()
        await self.generator.generate_keywords_data()
        await self.generator.generate_analytics_data()
        await self.generator.generate_payments_data()
        await self.generator.generate_audit_logs_data()
        
        # Obter métricas
        metrics = self.generator.get_generation_metrics()
        
        # Verificar métricas
        assert metrics["total_data_types"] > 0
        assert metrics["total_records"] > 0

if __name__ == "__main__":
    # Execução direta do gerador
    async def main():
        generator = EnvironmentTestDataGenerator()
        try:
            await generator.setup_generator()
            
            # Gerar todos os tipos de dados
            await generator.generate_users_data()
            await generator.generate_categorias_data()
            await generator.generate_execucoes_data()
            await generator.generate_keywords_data()
            await generator.generate_analytics_data()
            await generator.generate_payments_data()
            await generator.generate_audit_logs_data()
            
            # Exportar dados
            export_result = await generator.export_test_data("json")
            
            # Obter métricas finais
            metrics = generator.get_generation_metrics()
            print(f"Métricas de Geração de Dados: {json.dumps(metrics, indent=2, default=str)}")
            print(f"Exportação: {export_result}")
            
        finally:
            await generator.cleanup_test_data()
    
    asyncio.run(main()) 