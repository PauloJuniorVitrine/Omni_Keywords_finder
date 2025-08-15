# Guia de Logs

Este documento detalha as estratégias de logging do Omni Keywords Finder.

## Configuração

### 1. Logger

```python
# src/logging/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
import json
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """Formatador customizado para logs"""
    
    def format(self, record):
        """Formata log"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Configura logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # Handler para arquivo
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(CustomFormatter())
        logger.addHandler(file_handler)
        
    return logger
```

### 2. Handlers

```python
# src/logging/handlers.py
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
import os
from datetime import datetime

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Handler com rotação por tempo"""
    
    def __init__(
        self,
        filename: str,
        when: str = "midnight",
        interval: int = 1,
        backup_count: int = 30,
        encoding: Optional[str] = None
    ):
        super().__init__(
            filename,
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding=encoding
        )
        
    def getFilesToDelete(self):
        """Lista arquivos para deletar"""
        result = super().getFilesToDelete()
        return [f for f in result if os.path.exists(f)]

class CustomRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Handler com rotação por tamanho"""
    
    def __init__(
        self,
        filename: str,
        mode: str = "a",
        max_bytes: int = 0,
        backup_count: int = 0,
        encoding: Optional[str] = None
    ):
        super().__init__(
            filename,
            mode=mode,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding
        )
        
    def doRollover(self):
        """Faz rotação do arquivo"""
        if self.stream:
            self.stream.close()
            self.stream = None
            
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename(
                    self.baseFilename + "." + str(i)
                )
                dfn = self.rotation_filename(
                    self.baseFilename + "." + str(i + 1)
                )
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
                    
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
            
        if not self.delay:
            self.stream = self._open()
```

## Logs de Aplicação

### 1. API

```python
# src/logging/api.py
import logging
from fastapi import Request, Response
from typing import Callable
import time
from datetime import datetime

class APILogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    async def log_request(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Loga requisição"""
        start_time = time.time()
        
        # Log da requisição
        self.logger.info(
            "Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host,
                "headers": dict(request.headers)
            }
        )
        
        try:
            # Processa requisição
            response = await call_next(request)
            
            # Log da resposta
            process_time = time.time() - start_time
            self.logger.info(
                "Request completed",
                extra={
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            )
            
            return response
            
        except Exception as e:
            # Log do erro
            self.logger.error(
                "Request failed",
                extra={
                    "error": str(e),
                    "process_time": time.time() - start_time
                }
            )
            raise
```

### 2. ML

```python
# src/logging/ml.py
import logging
from typing import List, Dict, Any
import time
from datetime import datetime

class MLLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_extraction(
        self,
        text: str,
        keywords: List[str],
        scores: List[float],
        process_time: float
    ):
        """Loga extração de keywords"""
        self.logger.info(
            "Keywords extracted",
            extra={
                "text_length": len(text),
                "keywords_count": len(keywords),
                "keywords": keywords,
                "scores": scores,
                "process_time": process_time
            }
        )
        
    def log_training(
        self,
        model_name: str,
        metrics: Dict[str, float],
        process_time: float
    ):
        """Loga treinamento"""
        self.logger.info(
            "Model trained",
            extra={
                "model": model_name,
                "metrics": metrics,
                "process_time": process_time
            }
        )
        
    def log_prediction(
        self,
        model_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        process_time: float
    ):
        """Loga predição"""
        self.logger.info(
            "Prediction made",
            extra={
                "model": model_name,
                "input": input_data,
                "output": output_data,
                "process_time": process_time
            }
        )
```

## Logs de Sistema

### 1. Performance

```python
# src/logging/performance.py
import logging
from typing import Dict, Any
import time
from datetime import datetime
import psutil

class PerformanceLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_system_metrics(self):
        """Loga métricas do sistema"""
        metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "network_io": psutil.net_io_counters()._asdict()
        }
        
        self.logger.info(
            "System metrics",
            extra={"metrics": metrics}
        )
        
    def log_process_metrics(self, process_name: str):
        """Loga métricas do processo"""
        for proc in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
            if proc.info["name"] == process_name:
                self.logger.info(
                    "Process metrics",
                    extra={
                        "process": process_name,
                        "metrics": proc.info
                    }
                )
```

### 2. Erros

```python
# src/logging/errors.py
import logging
from typing import Optional, Dict, Any
import traceback
from datetime import datetime

class ErrorLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ):
        """Loga erro"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        
        if context:
            error_data["context"] = context
            
        self.logger.error(
            "Error occurred",
            extra=error_data
        )
        
    def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Loga warning"""
        warning_data = {
            "message": message
        }
        
        if context:
            warning_data["context"] = context
            
        self.logger.warning(
            "Warning occurred",
            extra=warning_data
        )
```

## Logs de Banco

### 1. MongoDB

```python
# src/logging/mongodb.py
import logging
from typing import Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDBLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_query(
        self,
        collection: str,
        operation: str,
        query: Dict[str, Any],
        process_time: float
    ):
        """Loga query"""
        self.logger.info(
            "MongoDB query",
            extra={
                "collection": collection,
                "operation": operation,
                "query": query,
                "process_time": process_time
            }
        )
        
    def log_error(
        self,
        collection: str,
        operation: str,
        error: Exception
    ):
        """Loga erro do MongoDB"""
        self.logger.error(
            "MongoDB error",
            extra={
                "collection": collection,
                "operation": operation,
                "error": str(error)
            }
        )
```

### 2. Redis

```python
# src/logging/redis.py
import logging
from typing import Dict, Any
from datetime import datetime
from redis import Redis

class RedisLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_operation(
        self,
        operation: str,
        key: str,
        value: Any,
        process_time: float
    ):
        """Loga operação"""
        self.logger.info(
            "Redis operation",
            extra={
                "operation": operation,
                "key": key,
                "value": value,
                "process_time": process_time
            }
        )
        
    def log_error(
        self,
        operation: str,
        key: str,
        error: Exception
    ):
        """Loga erro do Redis"""
        self.logger.error(
            "Redis error",
            extra={
                "operation": operation,
                "key": key,
                "error": str(error)
            }
        )
```

## Observações

- Usar níveis adequados
- Incluir contexto
- Rotacionar arquivos
- Monitorar tamanho
- Filtrar dados sensíveis
- Estruturar logs
- Manter histórico
- Analisar padrões
- Correlacionar eventos
- Documentar mudanças 