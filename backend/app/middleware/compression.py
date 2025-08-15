"""
Response Compression Middleware - Gzip/Brotli Implementation

Prompt: CHECKLIST_RESOLUCAO_GARGALOS.md - Fase 3.2.1
Ruleset: enterprise_control_layer.yaml
Date: 2025-01-27
Tracing ID: CHECKLIST_RESOLUCAO_GARGALOS_20250127_001
"""

import gzip
import brotli
import json
import logging
from typing import Dict, List, Optional, Union, Any
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import hashlib

logger = logging.getLogger(__name__)

class CompressionConfig:
    """Configuração para compressão de responses"""
    
    def __init__(
        self,
        min_size: int = 1024,  # Tamanho mínimo para compressão
        gzip_level: int = 6,   # Nível de compressão Gzip (1-9)
        brotli_quality: int = 11,  # Qualidade Brotli (0-11)
        content_types: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        enable_gzip: bool = True,
        enable_brotli: bool = True,
        cache_compressed: bool = True
    ):
        self.min_size = min_size
        self.gzip_level = max(1, min(9, gzip_level))
        self.brotli_quality = max(0, min(11, brotli_quality))
        self.content_types = content_types or [
            'text/plain',
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'application/xml',
            'application/xml+rss',
            'text/xml'
        ]
        self.exclude_paths = exclude_paths or [
            '/health',
            '/metrics',
            '/favicon.ico'
        ]
        self.enable_gzip = enable_gzip
        self.enable_brotli = enable_brotli
        self.cache_compressed = cache_compressed

class CompressionCache:
    """Cache para responses comprimidos"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, bytes]] = {}
        self.access_count: Dict[str, int] = {}
    
    def _generate_key(self, content: bytes, content_type: str, encoding: str) -> str:
        """Gera chave única para o cache"""
        content_hash = hashlib.md5(content).hexdigest()
        return f"{content_hash}:{content_type}:{encoding}"
    
    def get(self, content: bytes, content_type: str, encoding: str) -> Optional[bytes]:
        """Recupera conteúdo comprimido do cache"""
        key = self._generate_key(content, content_type, encoding)
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key][encoding]
        return None
    
    def set(self, content: bytes, content_type: str, encoding: str, compressed: bytes) -> None:
        """Armazena conteúdo comprimido no cache"""
        key = self._generate_key(content, content_type, encoding)
        
        # Remove item menos acessado se cache cheio
        if len(self.cache) >= self.max_size:
            least_accessed = min(self.access_count.items(), key=lambda x: x[1])
            del self.cache[least_accessed[0]]
            del self.access_count[least_accessed[0]]
        
        self.cache[key] = {encoding: compressed}
        self.access_count[key] = 1
    
    def clear(self) -> None:
        """Limpa o cache"""
        self.cache.clear()
        self.access_count.clear()

class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware para compressão de responses"""
    
    def __init__(
        self,
        app: ASGIApp,
        config: Optional[CompressionConfig] = None
    ):
        super().__init__(app)
        self.config = config or CompressionConfig()
        self.cache = CompressionCache() if self.config.cache_compressed else None
        
        # Headers de compressão suportados
        self.compression_headers = []
        if self.config.enable_gzip:
            self.compression_headers.append('gzip')
        if self.config.enable_brotli:
            self.compression_headers.append('br')
    
    def _should_compress(self, request: Request, content_type: str, content_length: int) -> bool:
        """Verifica se o response deve ser comprimido"""
        # Verifica tamanho mínimo
        if content_length < self.config.min_size:
            return False
        
        # Verifica tipo de conteúdo
        if not any(ct in content_type for ct in self.config.content_types):
            return False
        
        # Verifica paths excluídos
        path = request.url.path
        if any(excluded in path for excluded in self.config.exclude_paths):
            return False
        
        return True
    
    def _get_best_encoding(self, request: Request) -> Optional[str]:
        """Determina o melhor encoding baseado no Accept-Encoding"""
        accept_encoding = request.headers.get('accept-encoding', '').lower()
        
        # Prioriza Brotli se suportado
        if self.config.enable_brotli and 'br' in accept_encoding:
            return 'br'
        
        # Fallback para Gzip
        if self.config.enable_gzip and 'gzip' in accept_encoding:
            return 'gzip'
        
        return None
    
    def _compress_gzip(self, content: bytes) -> bytes:
        """Comprime conteúdo usando Gzip"""
        try:
            return gzip.compress(content, compresslevel=self.config.gzip_level)
        except Exception as e:
            logger.error(f"Erro na compressão Gzip: {e}")
            return content
    
    def _compress_brotli(self, content: bytes) -> bytes:
        """Comprime conteúdo usando Brotli"""
        try:
            return brotli.compress(content, quality=self.config.brotli_quality)
        except Exception as e:
            logger.error(f"Erro na compressão Brotli: {e}")
            return content
    
    def _compress_content(self, content: bytes, encoding: str) -> bytes:
        """Comprime conteúdo usando o encoding especificado"""
        if encoding == 'gzip':
            return self._compress_gzip(content)
        elif encoding == 'br':
            return self._compress_brotli(content)
        else:
            return content
    
    async def dispatch(self, request: Request, call_next):
        """Processa o request e aplica compressão se necessário"""
        start_time = time.time()
        
        # Processa o request
        response = await call_next(request)
        
        # Verifica se deve comprimir
        content_type = response.headers.get('content-type', '')
        content_length = response.headers.get('content-length')
        
        if not content_length:
            # Se não há content-length, não pode comprimir
            return response
        
        content_length = int(content_length)
        
        if not self._should_compress(request, content_type, content_length):
            return response
        
        # Determina encoding
        encoding = self._get_best_encoding(request)
        if not encoding:
            return response
        
        # Lê o conteúdo da response
        try:
            content = b''
            async for chunk in response.body_iterator:
                content += chunk
        except Exception as e:
            logger.error(f"Erro ao ler conteúdo da response: {e}")
            return response
        
        # Verifica cache
        compressed_content = None
        if self.cache:
            compressed_content = self.cache.get(content, content_type, encoding)
        
        # Comprime se não está em cache
        if compressed_content is None:
            compressed_content = self._compress_content(content, encoding)
            
            # Armazena no cache
            if self.cache and len(compressed_content) < len(content):
                self.cache.set(content, content_type, encoding, compressed_content)
        
        # Só usa compressão se realmente comprimiu
        if len(compressed_content) >= len(content):
            return response
        
        # Cria nova response comprimida
        headers = dict(response.headers)
        headers['content-encoding'] = encoding
        headers['content-length'] = str(len(compressed_content))
        headers['vary'] = 'Accept-Encoding'
        
        # Remove headers que podem causar problemas
        headers.pop('content-range', None)
        
        # Log de métricas
        compression_ratio = (1 - len(compressed_content) / len(content)) * 100
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(
            f"Compression applied: {encoding}, "
            f"Original: {len(content)}B, "
            f"Compressed: {len(compressed_content)}B, "
            f"Ratio: {compression_ratio:.1f}%, "
            f"Time: {processing_time:.2f}ms"
        )
        
        return Response(
            content=compressed_content,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )

class CompressionMetrics:
    """Métricas de compressão"""
    
    def __init__(self):
        self.total_requests = 0
        self.compressed_requests = 0
        self.total_original_size = 0
        self.total_compressed_size = 0
        self.compression_times = []
    
    def record_compression(
        self,
        original_size: int,
        compressed_size: int,
        processing_time: float
    ) -> None:
        """Registra métrica de compressão"""
        self.total_requests += 1
        self.compressed_requests += 1
        self.total_original_size += original_size
        self.total_compressed_size += compressed_size
        self.compression_times.append(processing_time)
    
    def record_no_compression(self) -> None:
        """Registra request sem compressão"""
        self.total_requests += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de compressão"""
        if self.compressed_requests == 0:
            return {
                'total_requests': self.total_requests,
                'compressed_requests': 0,
                'compression_ratio': 0.0,
                'avg_processing_time': 0.0,
                'bytes_saved': 0
            }
        
        compression_ratio = (
            (self.total_original_size - self.total_compressed_size) / 
            self.total_original_size * 100
        )
        
        avg_processing_time = sum(self.compression_times) / len(self.compression_times)
        bytes_saved = self.total_original_size - self.total_compressed_size
        
        return {
            'total_requests': self.total_requests,
            'compressed_requests': self.compressed_requests,
            'compression_ratio': round(compression_ratio, 2),
            'avg_processing_time': round(avg_processing_time, 2),
            'bytes_saved': bytes_saved,
            'total_original_size': self.total_original_size,
            'total_compressed_size': self.total_compressed_size
        }

# Instância global de métricas
compression_metrics = CompressionMetrics()

def get_compression_stats() -> Dict[str, Any]:
    """Retorna estatísticas de compressão"""
    return compression_metrics.get_stats()

def clear_compression_cache() -> None:
    """Limpa o cache de compressão"""
    if hasattr(compression_metrics, 'cache'):
        compression_metrics.cache.clear()

# Configurações predefinidas
COMPRESSION_CONFIGS = {
    'development': CompressionConfig(
        min_size=512,
        gzip_level=1,
        brotli_quality=5,
        cache_compressed=False
    ),
    'production': CompressionConfig(
        min_size=1024,
        gzip_level=6,
        brotli_quality=11,
        cache_compressed=True
    ),
    'high_compression': CompressionConfig(
        min_size=512,
        gzip_level=9,
        brotli_quality=11,
        cache_compressed=True
    )
} 