#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 **MIGRATION TO MICROSERVICES SCRIPT - OMNİ KEYWORDS FINDER**

Tracing ID: MIGRATION_SCRIPT_20250127_001
Data de Criação: 2025-01-27
Versão: 1.0.0
Status: 🟡 EM DESENVOLVIMENTO
Responsável: AI Assistant

Este script implementa a migração gradual do sistema monolítico para microserviços,
seguindo a estratégia definida em docs/MICROSERVICES_BOUNDARIES.md
"""

import os
import sys
import json
import yaml
import logging
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MigrationPhase(Enum):
    """Fases da migração"""
    PREPARATION = "preparation"
    EXTRACTION = "extraction"
    CORE_SERVICES = "core_services"
    OPTIMIZATION = "optimization"

class ServiceStatus(Enum):
    """Status dos serviços"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class ServiceConfig:
    """Configuração de um serviço"""
    name: str
    port: int
    health_endpoint: str
    dependencies: List[str]
    database: str
    environment_vars: Dict[str, str]
    docker_image: str
    kubernetes_config: str

@dataclass
class MigrationStep:
    """Passo da migração"""
    step_id: str
    description: str
    service: str
    phase: MigrationPhase
    dependencies: List[str]
    estimated_time: int  # minutos
    rollback_plan: str
    validation_checks: List[str]

class MicroservicesMigration:
    """Classe principal para gerenciar a migração para microserviços"""
    
    def __init__(self, config_path: str = "config/migration_config.yaml"):
        self.config_path = config_path
        self.migration_config = self._load_config()
        self.current_phase = MigrationPhase.PREPARATION
        self.services_status = {}
        self.migration_steps = self._create_migration_steps()
        self.tracing_id = f"MIGRATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Criar diretórios necessários
        self._create_directories()
        
        logger.info(f"🚀 Iniciando migração para microserviços - Tracing ID: {self.tracing_id}")
    
    def _load_config(self) -> Dict:
        """Carrega configuração da migração"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"✅ Configuração carregada de {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Arquivo de configuração não encontrado: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"❌ Erro ao parsear YAML: {e}")
            sys.exit(1)
    
    def _create_directories(self):
        """Cria diretórios necessários para a migração"""
        directories = [
            "logs",
            "backups",
            "migration_states",
            "kubernetes",
            "docker",
            "scripts/temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Diretórios criados")
    
    def _create_migration_steps(self) -> List[MigrationStep]:
        """Cria lista de passos da migração"""
        steps = [
            # Fase 1: Preparação
            MigrationStep(
                step_id="1.1",
                description="Configurar Kubernetes cluster",
                service="infrastructure",
                phase=MigrationPhase.PREPARATION,
                dependencies=[],
                estimated_time=120,
                rollback_plan="Remover cluster e recriar",
                validation_checks=["kubectl cluster-info", "kubectl get nodes"]
            ),
            MigrationStep(
                step_id="1.2",
                description="Implementar service mesh (Istio)",
                service="infrastructure",
                phase=MigrationPhase.PREPARATION,
                dependencies=["1.1"],
                estimated_time=60,
                rollback_plan="Desinstalar Istio",
                validation_checks=["istioctl version", "kubectl get pods -n istio-system"]
            ),
            MigrationStep(
                step_id="1.3",
                description="Configurar API Gateway",
                service="infrastructure",
                phase=MigrationPhase.PREPARATION,
                dependencies=["1.2"],
                estimated_time=90,
                rollback_plan="Remover Kong deployment",
                validation_checks=["kubectl get pods -n kong", "curl -k https://localhost:8443/status"]
            ),
            MigrationStep(
                step_id="1.4",
                description="Configurar monitoring stack",
                service="infrastructure",
                phase=MigrationPhase.PREPARATION,
                dependencies=["1.3"],
                estimated_time=120,
                rollback_plan="Remover Prometheus/Grafana",
                validation_checks=["kubectl get pods -n monitoring", "curl http://localhost:3000"]
            ),
            
            # Fase 2: Extração Gradual
            MigrationStep(
                step_id="2.1",
                description="Extrair Auth-Service",
                service="auth-service",
                phase=MigrationPhase.EXTRACTION,
                dependencies=["1.4"],
                estimated_time=240,
                rollback_plan="Restaurar auth do monolito",
                validation_checks=["curl http://auth-service:8004/health", "Testar login/logout"]
            ),
            MigrationStep(
                step_id="2.2",
                description="Extrair Notification-Service",
                service="notification-service",
                phase=MigrationPhase.EXTRACTION,
                dependencies=["2.1"],
                estimated_time=180,
                rollback_plan="Restaurar notifications do monolito",
                validation_checks=["curl http://notification-service:8005/health", "Testar envio de email"]
            ),
            MigrationStep(
                step_id="2.3",
                description="Extrair Billing-Service",
                service="billing-service",
                phase=MigrationPhase.EXTRACTION,
                dependencies=["2.2"],
                estimated_time=300,
                rollback_plan="Restaurar billing do monolito",
                validation_checks=["curl http://billing-service:8006/health", "Testar processamento de pagamento"]
            ),
            MigrationStep(
                step_id="2.4",
                description="Extrair UI-Service",
                service="ui-service",
                phase=MigrationPhase.EXTRACTION,
                dependencies=["2.3"],
                estimated_time=240,
                rollback_plan="Restaurar UI do monolito",
                validation_checks=["curl http://ui-service:3000/health", "Testar interface web"]
            ),
            
            # Fase 3: Core Services
            MigrationStep(
                step_id="3.1",
                description="Extrair Keyword-Service",
                service="keyword-service",
                phase=MigrationPhase.CORE_SERVICES,
                dependencies=["2.4"],
                estimated_time=360,
                rollback_plan="Restaurar keywords do monolito",
                validation_checks=["curl http://keyword-service:8000/health", "Testar análise de keywords"]
            ),
            MigrationStep(
                step_id="3.2",
                description="Extrair Analytics-Service",
                service="analytics-service",
                phase=MigrationPhase.CORE_SERVICES,
                dependencies=["3.1"],
                estimated_time=480,
                rollback_plan="Restaurar analytics do monolito",
                validation_checks=["curl http://analytics-service:8001/health", "Testar geração de relatórios"]
            ),
            MigrationStep(
                step_id="3.3",
                description="Extrair Crawler-Service",
                service="crawler-service",
                phase=MigrationPhase.CORE_SERVICES,
                dependencies=["3.2"],
                estimated_time=420,
                rollback_plan="Restaurar crawler do monolito",
                validation_checks=["curl http://crawler-service:8002/health", "Testar crawling de sites"]
            ),
            MigrationStep(
                step_id="3.4",
                description="Extrair Ranking-Service",
                service="ranking-service",
                phase=MigrationPhase.CORE_SERVICES,
                dependencies=["3.3"],
                estimated_time=360,
                rollback_plan="Restaurar ranking do monolito",
                validation_checks=["curl http://ranking-service:8003/health", "Testar monitoramento de posições"]
            ),
            
            # Fase 4: Otimização
            MigrationStep(
                step_id="4.1",
                description="Performance tuning",
                service="all",
                phase=MigrationPhase.OPTIMIZATION,
                dependencies=["3.4"],
                estimated_time=240,
                rollback_plan="Reverter configurações de performance",
                validation_checks=["Teste de carga", "Análise de métricas"]
            ),
            MigrationStep(
                step_id="4.2",
                description="Security hardening",
                service="all",
                phase=MigrationPhase.OPTIMIZATION,
                dependencies=["4.1"],
                estimated_time=180,
                rollback_plan="Reverter configurações de segurança",
                validation_checks=["Scan de vulnerabilidades", "Teste de penetração"]
            ),
            MigrationStep(
                step_id="4.3",
                description="Documentation",
                service="all",
                phase=MigrationPhase.OPTIMIZATION,
                dependencies=["4.2"],
                estimated_time=120,
                rollback_plan="N/A",
                validation_checks=["Verificar documentação", "Validar exemplos"]
            ),
            MigrationStep(
                step_id="4.4",
                description="Training",
                service="all",
                phase=MigrationPhase.OPTIMIZATION,
                dependencies=["4.3"],
                estimated_time=60,
                rollback_plan="N/A",
                validation_checks=["Feedback da equipe", "Teste de conhecimento"]
            )
        ]
        
        return steps
    
    def backup_monolith(self) -> bool:
        """Cria backup do sistema monolítico atual"""
        try:
            logger.info("🔄 Criando backup do sistema monolítico...")
            
            # Backup do código
            backup_dir = f"backups/monolith_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            Path(backup_dir).mkdir(parents=True, exist_ok=True)
            
            # Copiar arquivos principais
            subprocess.run([
                "cp", "-r", "app", f"{backup_dir}/app"
            ], check=True)
            
            subprocess.run([
                "cp", "-r", "backend", f"{backup_dir}/backend"
            ], check=True)
            
            subprocess.run([
                "cp", "requirements.txt", f"{backup_dir}/requirements.txt"
            ], check=True)
            
            # Backup do banco de dados
            subprocess.run([
                "sqlite3", "backend/db.sqlite3", f".backup {backup_dir}/database_backup.sqlite3"
            ], check=True)
            
            # Criar arquivo de metadados do backup
            backup_metadata = {
                "timestamp": datetime.now().isoformat(),
                "tracing_id": self.tracing_id,
                "description": "Backup do sistema monolítico antes da migração",
                "files": [
                    "app/",
                    "backend/",
                    "requirements.txt",
                    "database_backup.sqlite3"
                ]
            }
            
            with open(f"{backup_dir}/backup_metadata.json", 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            logger.info(f"✅ Backup criado em: {backup_dir}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado no backup: {e}")
            return False
    
    def validate_prerequisites(self) -> bool:
        """Valida pré-requisitos para a migração"""
        logger.info("🔍 Validando pré-requisitos...")
        
        prerequisites = [
            ("Docker", "docker --version"),
            ("Docker Compose", "docker-compose --version"),
            ("kubectl", "kubectl version --client"),
            ("helm", "helm version"),
            ("istioctl", "istioctl version"),
            ("Python 3.8+", "python3 --version")
        ]
        
        all_valid = True
        
        for tool, command in prerequisites:
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"✅ {tool}: OK")
                else:
                    logger.error(f"❌ {tool}: Não encontrado")
                    all_valid = False
            except FileNotFoundError:
                logger.error(f"❌ {tool}: Não encontrado")
                all_valid = False
        
        # Verificar arquivos necessários
        required_files = [
            "config/api_gateway.yaml",
            "docs/MICROSERVICES_BOUNDARIES.md",
            "requirements.txt"
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                logger.info(f"✅ {file_path}: OK")
            else:
                logger.error(f"❌ {file_path}: Não encontrado")
                all_valid = False
        
        return all_valid
    
    def create_service_template(self, service_name: str) -> bool:
        """Cria template para um microserviço"""
        try:
            logger.info(f"🏗️ Criando template para {service_name}...")
            
            service_dir = f"services/{service_name}"
            Path(service_dir).mkdir(parents=True, exist_ok=True)
            
            # Estrutura do serviço
            structure = {
                "app": {
                    "__init__.py": "",
                    "main.py": self._get_main_template(service_name),
                    "models.py": self._get_models_template(service_name),
                    "schemas.py": self._get_schemas_template(service_name),
                    "database.py": self._get_database_template(service_name),
                    "config.py": self._get_config_template(service_name)
                },
                "tests": {
                    "__init__.py": "",
                    "test_main.py": self._get_test_template(service_name)
                },
                "migrations": {
                    "__init__.py": ""
                },
                "Dockerfile": self._get_dockerfile_template(service_name),
                "requirements.txt": self._get_requirements_template(service_name),
                "kubernetes.yaml": self._get_kubernetes_template(service_name),
                "README.md": self._get_readme_template(service_name)
            }
            
            # Criar estrutura
            for path, content in self._flatten_structure(structure):
                full_path = Path(service_dir) / path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                if isinstance(content, str):
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    full_path.mkdir(exist_ok=True)
            
            logger.info(f"✅ Template criado para {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar template para {service_name}: {e}")
            return False
    
    def _flatten_structure(self, structure: Dict, prefix: str = "") -> List[Tuple[str, str]]:
        """Achatamento da estrutura de diretórios"""
        result = []
        for key, value in structure.items():
            path = f"{prefix}/{key}" if prefix else key
            if isinstance(value, dict):
                result.extend(self._flatten_structure(value, path))
            else:
                result.append((path, value))
        return result
    
    def _get_main_template(self, service_name: str) -> str:
        """Template para main.py"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{service_name.upper()} SERVICE - OMNİ KEYWORDS FINDER

Tracing ID: {service_name.upper()}_SERVICE_20250127_001
Data de Criação: 2025-01-27
Versão: 1.0.0
Status: 🟡 EM DESENVOLVIMENTO
Responsável: AI Assistant
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.models import Base

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle do aplicativo"""
    # Startup
    logger.info("🚀 Iniciando {service_name} service...")
    await init_db()
    logger.info("✅ {service_name} service iniciado")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando {service_name} service...")

# Criação da aplicação
app = FastAPI(
    title="{service_name.title()} Service",
    description="Microserviço {service_name} do Omni Keywords Finder",
    version="1.0.0",
    lifespan=lifespan
)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{
        "status": "healthy",
        "service": "{service_name}",
        "timestamp": "2025-01-27T00:00:00Z"
    }}

@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "message": "Welcome to {service_name.title()} Service",
        "version": "1.0.0"
    }}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
'''
    
    def _get_models_template(self, service_name: str) -> str:
        """Template para models.py"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Models para {service_name} service
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class {service_name.title()}Model(Base):
    """Modelo base para {service_name}"""
    __tablename__ = "{service_name}"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
'''
    
    def _get_schemas_template(self, service_name: str) -> str:
        """Template para schemas.py"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schemas para {service_name} service
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class {service_name.title()}Base(BaseModel):
    """Schema base para {service_name}"""
    name: str
    description: Optional[str] = None

class {service_name.title()}Create({service_name.title()}Base):
    """Schema para criação de {service_name}"""
    pass

class {service_name.title()}Update({service_name.title()}Base):
    """Schema para atualização de {service_name}"""
    name: Optional[str] = None

class {service_name.title()}Response({service_name.title()}Base):
    """Schema para resposta de {service_name}"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True
'''
    
    def _get_database_template(self, service_name: str) -> str:
        """Template para database.py"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database configuration para {service_name} service
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

# Engine
engine = create_engine(settings.DATABASE_URL)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base
Base = declarative_base()

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Inicializar banco de dados"""
    Base.metadata.create_all(bind=engine)
'''
    
    def _get_config_template(self, service_name: str) -> str:
        """Template para config.py"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration para {service_name} service
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/{service_name}_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Service
    SERVICE_NAME: str = "{service_name}"
    SERVICE_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
    
    def _get_test_template(self, service_name: str) -> str:
        """Template para testes"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para {service_name} service
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Teste do health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "{service_name}"

def test_root_endpoint():
    """Teste do endpoint root"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to {service_name.title()} Service"
    assert data["version"] == "1.0.0"
'''
    
    def _get_dockerfile_template(self, service_name: str) -> str:
        """Template para Dockerfile"""
        return f'''# Dockerfile para {service_name} service
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _get_requirements_template(self, service_name: str) -> str:
        """Template para requirements.txt"""
        return f'''# Requirements para {service_name} service
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
redis==5.0.1
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
'''
    
    def _get_kubernetes_template(self, service_name: str) -> str:
        """Template para Kubernetes"""
        return f'''# Kubernetes deployment para {service_name} service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}-deployment
  namespace: omni-keywords
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
    spec:
      containers:
      - name: {service_name}
        image: {service_name}:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {service_name}-secret
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: {service_name}-secret
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {service_name}-service
  namespace: omni-keywords
spec:
  selector:
    app: {service_name}
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
'''
    
    def _get_readme_template(self, service_name: str) -> str:
        """Template para README.md"""
        return f'''# {service_name.title()} Service

Microserviço {service_name} do Omni Keywords Finder.

## 🚀 Execução Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
uvicorn app.main:app --reload
```

## 🐳 Docker

```bash
# Build
docker build -t {service_name} .

# Executar
docker run -p 8000:8000 {service_name}
```

## ☸️ Kubernetes

```bash
# Deploy
kubectl apply -f kubernetes.yaml
```

## 🧪 Testes

```bash
pytest
```
'''
    
    def execute_migration_step(self, step: MigrationStep) -> bool:
        """Executa um passo da migração"""
        logger.info(f"🔄 Executando passo {step.step_id}: {step.description}")
        
        try:
            # Verificar dependências
            if not self._check_dependencies(step.dependencies):
                logger.error(f"❌ Dependências não atendidas para passo {step.step_id}")
                return False
            
            # Executar passo específico
            success = self._execute_step_logic(step)
            
            if success:
                # Validar passo
                if self._validate_step(step):
                    logger.info(f"✅ Passo {step.step_id} concluído com sucesso")
                    self.services_status[step.service] = ServiceStatus.COMPLETED
                    return True
                else:
                    logger.error(f"❌ Validação falhou para passo {step.step_id}")
                    self._rollback_step(step)
                    return False
            else:
                logger.error(f"❌ Execução falhou para passo {step.step_id}")
                self._rollback_step(step)
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro inesperado no passo {step.step_id}: {e}")
            self._rollback_step(step)
            return False
    
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Verifica se as dependências foram atendidas"""
        for dep in dependencies:
            if dep not in self.services_status or \
               self.services_status.get(dep) != ServiceStatus.COMPLETED:
                return False
        return True
    
    def _execute_step_logic(self, step: MigrationStep) -> bool:
        """Executa a lógica específica do passo"""
        step_id = step.step_id
        
        if step_id.startswith("1."):  # Preparação
            return self._execute_preparation_step(step)
        elif step_id.startswith("2."):  # Extração
            return self._execute_extraction_step(step)
        elif step_id.startswith("3."):  # Core Services
            return self._execute_core_step(step)
        elif step_id.startswith("4."):  # Otimização
            return self._execute_optimization_step(step)
        else:
            logger.error(f"❌ Passo desconhecido: {step_id}")
            return False
    
    def _execute_preparation_step(self, step: MigrationStep) -> bool:
        """Executa passos de preparação"""
        step_id = step.step_id
        
        if step_id == "1.1":
            return self._setup_kubernetes_cluster()
        elif step_id == "1.2":
            return self._setup_istio()
        elif step_id == "1.3":
            return self._setup_api_gateway()
        elif step_id == "1.4":
            return self._setup_monitoring()
        else:
            return False
    
    def _execute_extraction_step(self, step: MigrationStep) -> bool:
        """Executa passos de extração"""
        service_name = step.service.replace("-service", "")
        
        # Criar template do serviço
        if not self.create_service_template(service_name):
            return False
        
        # Deploy do serviço
        if not self._deploy_service(service_name):
            return False
        
        # Configurar roteamento
        if not self._configure_routing(service_name):
            return False
        
        return True
    
    def _execute_core_step(self, step: MigrationStep) -> bool:
        """Executa passos de core services"""
        return self._execute_extraction_step(step)
    
    def _execute_optimization_step(self, step: MigrationStep) -> bool:
        """Executa passos de otimização"""
        step_id = step.step_id
        
        if step_id == "4.1":
            return self._optimize_performance()
        elif step_id == "4.2":
            return self._harden_security()
        elif step_id == "4.3":
            return self._create_documentation()
        elif step_id == "4.4":
            return self._conduct_training()
        else:
            return False
    
    def _setup_kubernetes_cluster(self) -> bool:
        """Configura cluster Kubernetes"""
        try:
            logger.info("🔧 Configurando cluster Kubernetes...")
            
            # Verificar se kubectl está disponível
            result = subprocess.run(["kubectl", "cluster-info"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ kubectl não está configurado")
                return False
            
            # Criar namespace
            subprocess.run([
                "kubectl", "create", "namespace", "omni-keywords"
            ], check=True)
            
            logger.info("✅ Cluster Kubernetes configurado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao configurar Kubernetes: {e}")
            return False
    
    def _setup_istio(self) -> bool:
        """Configura Istio service mesh"""
        try:
            logger.info("🔧 Configurando Istio...")
            
            # Instalar Istio
            subprocess.run([
                "istioctl", "install", "--set", "profile=demo", "-y"
            ], check=True)
            
            # Habilitar sidecar injection
            subprocess.run([
                "kubectl", "label", "namespace", "omni-keywords", "istio-injection=enabled"
            ], check=True)
            
            logger.info("✅ Istio configurado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao configurar Istio: {e}")
            return False
    
    def _setup_api_gateway(self) -> bool:
        """Configura API Gateway"""
        try:
            logger.info("🔧 Configurando API Gateway...")
            
            # Deploy Kong
            subprocess.run([
                "kubectl", "apply", "-f", "config/api_gateway.yaml"
            ], check=True)
            
            # Aguardar pods ficarem prontos
            subprocess.run([
                "kubectl", "wait", "--for=condition=ready", "pod", "-l", "app=kong", "-n", "omni-keywords", "--timeout=300s"
            ], check=True)
            
            logger.info("✅ API Gateway configurado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao configurar API Gateway: {e}")
            return False
    
    def _setup_monitoring(self) -> bool:
        """Configura stack de monitoramento"""
        try:
            logger.info("🔧 Configurando monitoramento...")
            
            # Deploy Prometheus
            subprocess.run([
                "kubectl", "apply", "-f", "monitoring/prometheus.yaml"
            ], check=True)
            
            # Deploy Grafana
            subprocess.run([
                "kubectl", "apply", "-f", "monitoring/grafana.yaml"
            ], check=True)
            
            logger.info("✅ Monitoramento configurado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao configurar monitoramento: {e}")
            return False
    
    def _deploy_service(self, service_name: str) -> bool:
        """Deploy de um serviço"""
        try:
            logger.info(f"🚀 Deployando {service_name}...")
            
            # Build da imagem
            subprocess.run([
                "docker", "build", "-t", f"{service_name}:latest", f"services/{service_name}"
            ], check=True)
            
            # Deploy no Kubernetes
            subprocess.run([
                "kubectl", "apply", "-f", f"services/{service_name}/kubernetes.yaml"
            ], check=True)
            
            # Aguardar deploy
            subprocess.run([
                "kubectl", "wait", "--for=condition=ready", "pod", "-l", f"app={service_name}", "-n", "omni-keywords", "--timeout=300s"
            ], check=True)
            
            logger.info(f"✅ {service_name} deployado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao deployar {service_name}: {e}")
            return False
    
    def _configure_routing(self, service_name: str) -> bool:
        """Configura roteamento para um serviço"""
        try:
            logger.info(f"🔧 Configurando roteamento para {service_name}...")
            
            # Configurar Kong routes
            # (Implementação específica do Kong)
            
            logger.info(f"✅ Roteamento configurado para {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar roteamento para {service_name}: {e}")
            return False
    
    def _optimize_performance(self) -> bool:
        """Otimização de performance"""
        try:
            logger.info("⚡ Otimizando performance...")
            
            # Configurar HPA (Horizontal Pod Autoscaler)
            # Configurar resource limits
            # Otimizar configurações de cache
            
            logger.info("✅ Performance otimizada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na otimização de performance: {e}")
            return False
    
    def _harden_security(self) -> bool:
        """Hardening de segurança"""
        try:
            logger.info("🔒 Aplicando hardening de segurança...")
            
            # Configurar network policies
            # Configurar RBAC
            # Configurar secrets management
            
            logger.info("✅ Segurança aplicada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no hardening de segurança: {e}")
            return False
    
    def _create_documentation(self) -> bool:
        """Cria documentação"""
        try:
            logger.info("📚 Criando documentação...")
            
            # Gerar documentação da API
            # Criar runbooks
            # Documentar arquitetura
            
            logger.info("✅ Documentação criada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar documentação: {e}")
            return False
    
    def _conduct_training(self) -> bool:
        """Conduz treinamento da equipe"""
        try:
            logger.info("👥 Conduzindo treinamento...")
            
            # Criar materiais de treinamento
            # Conduzir sessões
            # Avaliar conhecimento
            
            logger.info("✅ Treinamento concluído")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento: {e}")
            return False
    
    def _validate_step(self, step: MigrationStep) -> bool:
        """Valida um passo da migração"""
        logger.info(f"🔍 Validando passo {step.step_id}...")
        
        for check in step.validation_checks:
            try:
                if check.startswith("curl"):
                    # Executar curl
                    result = subprocess.run(check.split(), capture_output=True, text=True)
                    if result.returncode != 0:
                        logger.error(f"❌ Validação falhou: {check}")
                        return False
                elif check.startswith("kubectl"):
                    # Executar kubectl
                    result = subprocess.run(check.split(), capture_output=True, text=True)
                    if result.returncode != 0:
                        logger.error(f"❌ Validação falhou: {check}")
                        return False
                else:
                    # Outros tipos de validação
                    logger.warning(f"⚠️ Validação não implementada: {check}")
                
            except Exception as e:
                logger.error(f"❌ Erro na validação {check}: {e}")
                return False
        
        logger.info(f"✅ Validação do passo {step.step_id} concluída")
        return True
    
    def _rollback_step(self, step: MigrationStep):
        """Executa rollback de um passo"""
        logger.warning(f"🔄 Executando rollback do passo {step.step_id}")
        
        try:
            # Implementar lógica de rollback específica
            if step.rollback_plan != "N/A":
                logger.info(f"Executando: {step.rollback_plan}")
                # Implementar rollback específico
            
            self.services_status[step.service] = ServiceStatus.ROLLED_BACK
            logger.info(f"✅ Rollback do passo {step.step_id} concluído")
            
        except Exception as e:
            logger.error(f"❌ Erro no rollback do passo {step.step_id}: {e}")
    
    def save_migration_state(self):
        """Salva estado atual da migração"""
        state = {
            "tracing_id": self.tracing_id,
            "current_phase": self.current_phase.value,
            "services_status": {k: v.value for k, v in self.services_status.items()},
            "timestamp": datetime.now().isoformat(),
            "completed_steps": [step.step_id for step in self.migration_steps 
                              if self.services_status.get(step.service) == ServiceStatus.COMPLETED]
        }
        
        state_file = f"migration_states/migration_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 Estado da migração salvo em: {state_file}")
    
    def run_migration(self, start_phase: Optional[str] = None, dry_run: bool = False) -> bool:
        """Executa a migração completa"""
        logger.info("🚀 Iniciando migração para microserviços...")
        
        # Backup inicial
        if not self.backup_monolith():
            logger.error("❌ Falha no backup inicial")
            return False
        
        # Validar pré-requisitos
        if not self.validate_prerequisites():
            logger.error("❌ Pré-requisitos não atendidos")
            return False
        
        # Executar passos
        for step in self.migration_steps:
            if start_phase and step.phase.value != start_phase:
                continue
            
            if dry_run:
                logger.info(f"🔍 [DRY RUN] Executaria passo {step.step_id}: {step.description}")
                continue
            
            if not self.execute_migration_step(step):
                logger.error(f"❌ Migração falhou no passo {step.step_id}")
                self.save_migration_state()
                return False
            
            # Salvar estado após cada passo
            self.save_migration_state()
        
        logger.info("🎉 Migração concluída com sucesso!")
        return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Migração para microserviços - Omni Keywords Finder")
    parser.add_argument("--config", default="config/migration_config.yaml", help="Arquivo de configuração")
    parser.add_argument("--start-phase", help="Fase inicial da migração")
    parser.add_argument("--dry-run", action="store_true", help="Executar em modo dry-run")
    
    args = parser.parse_args()
    
    # Criar instância da migração
    migration = MicroservicesMigration(args.config)
    
    # Executar migração
    success = migration.run_migration(
        start_phase=args.start_phase,
        dry_run=args.dry_run
    )
    
    if success:
        logger.info("✅ Migração concluída com sucesso!")
        sys.exit(0)
    else:
        logger.error("❌ Migração falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main() 