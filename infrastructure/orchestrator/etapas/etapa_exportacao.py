"""
Etapa de Exportação - Omni Keywords Finder

Responsável pela exportação dos resultados:
- Geração de arquivos ZIP
- Organização por nicho/categoria
- Metadados de exportação
- Limpeza automática

Tracing ID: ETAPA_EXPORTACAO_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import time
import logging
import zipfile
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import sys

# Adicionar caminho para importar módulos do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

from infrastructure.cache.cache_inteligente_cauda_longa import CacheInteligenteCaudaLonga
from domain.models import Keyword

logger = logging.getLogger(__name__)


@dataclass
class ArquivoExportado:
    """Estrutura para arquivo exportado."""
    nome_arquivo: str
    caminho_completo: str
    tamanho_bytes: int
    tipo_conteudo: str
    metadados: Dict[str, Any]


@dataclass
class ExportacaoResult:
    """Resultado da etapa de exportação."""
    arquivos_gerados: List[ArquivoExportado]
    total_arquivos: int
    tamanho_total_bytes: int
    tempo_execucao: float
    metadados: Dict[str, Any]


class EtapaExportacao:
    """
    Etapa responsável pela exportação dos resultados.
    
    Gera arquivos ZIP organizados com todos os dados processados
    e metadados de exportação.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a etapa de exportação.
        
        Args:
            config: Configurações da etapa de exportação
        """
        self.config = config
        self.cache = CacheInteligenteCaudaLonga()
        
        # Diretório de exportação
        self.diretorio_exportacao = Path(self.config.get('diretorio_exportacao', 'blogs/saida_zip'))
        self.diretorio_exportacao.mkdir(parents=True, exist_ok=True)
        
        logger.info("Etapa de exportação inicializada")
    
    async def executar(
        self, 
        keywords: List[Keyword], 
        prompts: List[Any], 
        nicho: str,
        metadados_processamento: Dict[str, Any]
    ) -> ExportacaoResult:
        """
        Executa a etapa de exportação.
        
        Args:
            keywords: Lista de keywords processadas
            prompts: Lista de prompts gerados
            nicho: Nome do nicho
            metadados_processamento: Metadados do processamento
            
        Returns:
            ExportacaoResult com os arquivos gerados
        """
        inicio_tempo = time.time()
        logger.info(f"Iniciando exportação para nicho: {nicho}")
        
        try:
            # Verificar cache primeiro
            cache_key = f"exportacao_{nicho}_{int(time.time())}"
            resultado_cache = self.cache.obter(cache_key)
            
            if resultado_cache and self.config.get('use_cache', True):
                logger.info(f"Usando dados do cache para exportação do nicho: {nicho}")
                return ExportacaoResult(
                    arquivos_gerados=resultado_cache['arquivos'],
                    total_arquivos=len(resultado_cache['arquivos']),
                    tamanho_total_bytes=resultado_cache.get('tamanho_total', 0),
                    tempo_execucao=time.time() - inicio_tempo,
                    metadados=resultado_cache.get('metadados', {})
                )
            
            # Executar exportação real
            arquivos_gerados = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1. Gerar arquivo ZIP principal
            arquivo_zip = await self._gerar_arquivo_zip(
                keywords, prompts, nicho, timestamp, metadados_processamento
            )
            if arquivo_zip:
                arquivos_gerados.append(arquivo_zip)
            
            # 2. Gerar arquivo JSON com metadados
            arquivo_json = await self._gerar_arquivo_json(
                keywords, prompts, nicho, timestamp, metadados_processamento
            )
            if arquivo_json:
                arquivos_gerados.append(arquivo_json)
            
            # 3. Gerar arquivo CSV com keywords
            arquivo_csv = await self._gerar_arquivo_csv(keywords, nicho, timestamp)
            if arquivo_csv:
                arquivos_gerados.append(arquivo_csv)
            
            # 4. Gerar arquivo de prompts
            arquivo_prompts = await self._gerar_arquivo_prompts(prompts, nicho, timestamp)
            if arquivo_prompts:
                arquivos_gerados.append(arquivo_prompts)
            
            # 5. Executar limpeza se configurado
            if self.config.get('cleanup_arquivos_antigos', True):
                await self._executar_limpeza()
            
            # Calcular tamanho total
            tamanho_total = sum(arquivo.tamanho_bytes for arquivo in arquivos_gerados)
            
            # Salvar no cache
            if self.config.get('use_cache', True):
                self.cache.inserir(cache_key, {
                    'arquivos': arquivos_gerados,
                    'tamanho_total': tamanho_total,
                    'metadados': {
                        'nicho': nicho,
                        'timestamp': time.time(),
                        'total_arquivos': len(arquivos_gerados)
                    }
                }, ttl_minutos=self.config.get('cache_ttl_horas', 24) * 60)
            
            tempo_execucao = time.time() - inicio_tempo
            
            resultado = ExportacaoResult(
                arquivos_gerados=arquivos_gerados,
                total_arquivos=len(arquivos_gerados),
                tamanho_total_bytes=tamanho_total,
                tempo_execucao=tempo_execucao,
                metadados={
                    'nicho': nicho,
                    'timestamp_exportacao': timestamp,
                    'config_utilizada': self.config
                }
            )
            
            logger.info(f"Exportação concluída para nicho: {nicho} - {len(arquivos_gerados)} arquivos em {tempo_execucao:.2f}string_data")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na etapa de exportação para nicho {nicho}: {e}")
            raise
    
    async def _gerar_arquivo_zip(
        self, 
        keywords: List[Keyword], 
        prompts: List[Any], 
        nicho: str, 
        timestamp: str,
        metadados: Dict[str, Any]
    ) -> Optional[ArquivoExportado]:
        """Gera arquivo ZIP com todos os dados."""
        try:
            nome_arquivo = f"{nicho}_keywords_{timestamp}.zip"
            caminho_arquivo = self.diretorio_exportacao / nome_arquivo
            
            with zipfile.ZipFile(caminho_arquivo, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Adicionar keywords
                keywords_data = []
                for kw in keywords:
                    kw_dict = {
                        'termo': getattr(kw, 'termo', ''),
                        'volume_busca': getattr(kw, 'volume_busca', 0),
                        'cpc': getattr(kw, 'cpc', 0.0),
                        'concorrencia': getattr(kw, 'concorrencia', 0.0),
                        'score': getattr(kw, 'score', 0.0),
                        'intencao': str(getattr(kw, 'intencao', '')),
                        'fonte': getattr(kw, 'fonte', ''),
                        'metadados': getattr(kw, 'metadados', {})
                    }
                    keywords_data.append(kw_dict)
                
                zip_file.writestr('keywords.json', json.dumps(keywords_data, indent=2, ensure_ascii=False))
                
                # Adicionar prompts
                prompts_data = []
                for prompt in prompts:
                    if hasattr(prompt, 'keyword') and hasattr(prompt, 'conteudo'):
                        prompt_dict = {
                            'keyword': prompt.keyword,
                            'tipo_prompt': getattr(prompt, 'tipo_prompt', ''),
                            'conteudo': prompt.conteudo,
                            'score_qualidade': getattr(prompt, 'score_qualidade', 0.0),
                            'metadados': getattr(prompt, 'metadados', {})
                        }
                        prompts_data.append(prompt_dict)
                
                zip_file.writestr('prompts.json', json.dumps(prompts_data, indent=2, ensure_ascii=False))
                
                # Adicionar metadados
                metadados_exportacao = {
                    'nicho': nicho,
                    'timestamp_exportacao': timestamp,
                    'total_keywords': len(keywords),
                    'total_prompts': len(prompts),
                    'metadados_processamento': metadados,
                    'config_exportacao': self.config
                }
                
                zip_file.writestr('metadados.json', json.dumps(metadados_exportacao, indent=2, ensure_ascii=False))
            
            tamanho_bytes = caminho_arquivo.stat().st_size
            
            return ArquivoExportado(
                nome_arquivo=nome_arquivo,
                caminho_completo=str(caminho_arquivo),
                tamanho_bytes=tamanho_bytes,
                tipo_conteudo='application/zip',
                metadados={'tipo': 'zip_completo'}
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo ZIP: {e}")
            return None
    
    async def _gerar_arquivo_json(
        self, 
        keywords: List[Keyword], 
        prompts: List[Any], 
        nicho: str, 
        timestamp: str,
        metadados: Dict[str, Any]
    ) -> Optional[ArquivoExportado]:
        """Gera arquivo JSON com metadados."""
        try:
            nome_arquivo = f"{nicho}_metadados_{timestamp}.json"
            caminho_arquivo = self.diretorio_exportacao / nome_arquivo
            
            dados_json = {
                'nicho': nicho,
                'timestamp_exportacao': timestamp,
                'estatisticas': {
                    'total_keywords': len(keywords),
                    'total_prompts': len(prompts),
                    'keywords_com_volume': len([kw for kw in keywords if getattr(kw, 'volume_busca', 0) > 0]),
                    'keywords_com_score': len([kw for kw in keywords if getattr(kw, 'score', 0) > 0])
                },
                'metadados_processamento': metadados,
                'config_exportacao': self.config
            }
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_json, f, indent=2, ensure_ascii=False)
            
            tamanho_bytes = caminho_arquivo.stat().st_size
            
            return ArquivoExportado(
                nome_arquivo=nome_arquivo,
                caminho_completo=str(caminho_arquivo),
                tamanho_bytes=tamanho_bytes,
                tipo_conteudo='application/json',
                metadados={'tipo': 'metadados'}
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo JSON: {e}")
            return None
    
    async def _gerar_arquivo_csv(self, keywords: List[Keyword], nicho: str, timestamp: str) -> Optional[ArquivoExportado]:
        """Gera arquivo CSV com keywords."""
        try:
            nome_arquivo = f"{nicho}_keywords_{timestamp}.csv"
            caminho_arquivo = self.diretorio_exportacao / nome_arquivo
            
            import csv
            
            with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Cabeçalho
                writer.writerow([
                    'termo', 'volume_busca', 'cpc', 'concorrencia', 
                    'score', 'intencao', 'fonte'
                ])
                
                # Dados
                for kw in keywords:
                    writer.writerow([
                        getattr(kw, 'termo', ''),
                        getattr(kw, 'volume_busca', 0),
                        getattr(kw, 'cpc', 0.0),
                        getattr(kw, 'concorrencia', 0.0),
                        getattr(kw, 'score', 0.0),
                        str(getattr(kw, 'intencao', '')),
                        getattr(kw, 'fonte', '')
                    ])
            
            tamanho_bytes = caminho_arquivo.stat().st_size
            
            return ArquivoExportado(
                nome_arquivo=nome_arquivo,
                caminho_completo=str(caminho_arquivo),
                tamanho_bytes=tamanho_bytes,
                tipo_conteudo='text/csv',
                metadados={'tipo': 'keywords_csv'}
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo CSV: {e}")
            return None
    
    async def _gerar_arquivo_prompts(self, prompts: List[Any], nicho: str, timestamp: str) -> Optional[ArquivoExportado]:
        """Gera arquivo com prompts."""
        try:
            nome_arquivo = f"{nicho}_prompts_{timestamp}.txt"
            caminho_arquivo = self.diretorio_exportacao / nome_arquivo
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(f"PROMPTS GERADOS - NICHO: {nicho}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write("=" * 80 + "\n\n")
                
                for index, prompt in enumerate(prompts, 1):
                    if hasattr(prompt, 'keyword') and hasattr(prompt, 'conteudo'):
                        f.write(f"PROMPT {index}\n")
                        f.write(f"Keyword: {prompt.keyword}\n")
                        f.write(f"Tipo: {getattr(prompt, 'tipo_prompt', 'N/A')}\n")
                        f.write(f"Score: {getattr(prompt, 'score_qualidade', 0.0):.2f}\n")
                        f.write("-" * 40 + "\n")
                        f.write(prompt.conteudo)
                        f.write("\n\n" + "=" * 80 + "\n\n")
            
            tamanho_bytes = caminho_arquivo.stat().st_size
            
            return ArquivoExportado(
                nome_arquivo=nome_arquivo,
                caminho_completo=str(caminho_arquivo),
                tamanho_bytes=tamanho_bytes,
                tipo_conteudo='text/plain',
                metadados={'tipo': 'prompts_texto'}
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo de prompts: {e}")
            return None
    
    async def _executar_limpeza(self):
        """Executa limpeza de arquivos antigos."""
        try:
            dias_para_cleanup = self.config.get('dias_para_cleanup', 30)
            limite_tamanho_mb = self.config.get('max_tamanho_arquivo_mb', 100)
            
            # Calcular data limite
            from datetime import timedelta
            data_limite = datetime.now() - timedelta(days=dias_para_cleanup)
            
            # Listar arquivos antigos
            arquivos_antigos = []
            for arquivo in self.diretorio_exportacao.glob('*'):
                if arquivo.is_file():
                    stat = arquivo.stat()
                    data_modificacao = datetime.fromtimestamp(stat.st_mtime)
                    
                    if data_modificacao < data_limite:
                        arquivos_antigos.append(arquivo)
            
            # Remover arquivos antigos
            for arquivo in arquivos_antigos:
                try:
                    arquivo.unlink()
                    logger.info(f"Arquivo antigo removido: {arquivo.name}")
                except Exception as e:
                    logger.warning(f"Erro ao remover arquivo {arquivo.name}: {e}")
            
            logger.info(f"Limpeza concluída: {len(arquivos_antigos)} arquivos removidos")
            
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna status atual da etapa de exportação."""
        try:
            arquivos_existentes = list(self.diretorio_exportacao.glob('*'))
            tamanho_total = sum(arquivo.stat().st_size for arquivo in arquivos_existentes if arquivo.is_file())
            
            return {
                'diretorio_exportacao': str(self.diretorio_exportacao),
                'arquivos_existentes': len(arquivos_existentes),
                'tamanho_total_mb': tamanho_total / (1024 * 1024),
                'config': self.config,
                'cache_ativo': self.config.get('use_cache', True)
            }
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {'erro': str(e)} 