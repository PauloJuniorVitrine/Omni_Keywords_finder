"""
Schema de validação para execuções - Omni Keywords Finder
Validação robusta com Pydantic para todos os endpoints de execução

Prompt: Implementação de validação de entrada para execuções
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import json
from enum import Enum

class StatusExecucao(str, Enum):
    """Status possíveis para uma execução"""
    PENDENTE = "pendente"
    EM_EXECUCAO = "em_execucao"
    EXECUTADO = "executado"
    FALHOU = "falhou"
    CANCELADO = "cancelado"
    PAUSADO = "pausado"

class ExecucaoCreateRequest(BaseModel):
    """
    Schema para criação de execução individual
    """
    categoria_id: int = Field(..., gt=0, description="ID da categoria para execução")
    palavras_chave: List[str] = Field(..., min_items=1, max_items=100, description="Lista de palavras-chave")
    cluster: Optional[str] = Field(None, min_length=1, max_length=255, description="Cluster opcional")
    
    @validator('categoria_id')
    def validar_categoria_id(cls, v):
        """Valida se o ID da categoria é válido"""
        if not isinstance(v, int) or v <= 0:
            raise ValueError('categoria_id deve ser um inteiro positivo')
        return v
    
    @validator('palavras_chave')
    def validar_palavras_chave(cls, v):
        """Valida a lista de palavras-chave"""
        if not isinstance(v, list):
            raise ValueError('palavras_chave deve ser uma lista')
        
        if not v:
            raise ValueError('palavras_chave não pode estar vazia')
        
        if len(v) > 100:
            raise ValueError('máximo de 100 palavras-chave permitidas')
        
        # Validar cada palavra-chave
        for i, palavra in enumerate(v):
            if not isinstance(palavra, str):
                raise ValueError(f'palavra-chave {i+1} deve ser string')
            
            if not palavra.strip():
                raise ValueError(f'palavra-chave {i+1} não pode estar vazia')
            
            if len(palavra) > 100:
                raise ValueError(f'palavra-chave {i+1} deve ter no máximo 100 caracteres')
            
            # Validar caracteres permitidos (letras, números, espaços, hífens, underscores)
            if not re.match(r'^[a-zA-Z0-9\s\-_]+$', palavra):
                raise ValueError(f'palavra-chave {i+1} contém caracteres inválidos')
        
        return v
    
    @validator('cluster')
    def validar_cluster(cls, v):
        """Valida o cluster se fornecido"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError('cluster deve ser string')
            
            if not v.strip():
                raise ValueError('cluster não pode estar vazio')
            
            if len(v) > 255:
                raise ValueError('cluster deve ter no máximo 255 caracteres')
            
            # Validar caracteres permitidos
            if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', v):
                raise ValueError('cluster contém caracteres inválidos')
        
        return v

class ExecucaoLoteRequest(BaseModel):
    """
    Schema para execução em lote
    """
    execucoes: List[ExecucaoCreateRequest] = Field(..., min_items=1, max_items=50, description="Lista de execuções")
    max_concurrent: Optional[int] = Field(5, ge=1, le=20, description="Máximo de execuções simultâneas")
    
    @validator('execucoes')
    def validar_execucoes(cls, v):
        """Valida a lista de execuções"""
        if not isinstance(v, list):
            raise ValueError('execucoes deve ser uma lista')
        
        if not v:
            raise ValueError('execucoes não pode estar vazia')
        
        if len(v) > 50:
            raise ValueError('máximo de 50 execuções em lote permitidas')
        
        # Validar IDs únicos de categoria
        categoria_ids = [execucao.categoria_id for execucao in v]
        if len(set(categoria_ids)) != len(categoria_ids):
            raise ValueError('categorias duplicadas não são permitidas em lote')
        
        return v
    
    @validator('max_concurrent')
    def validar_max_concurrent(cls, v):
        """Valida o número máximo de execuções simultâneas"""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError('max_concurrent deve ser inteiro')
            
            if v < 1:
                raise ValueError('max_concurrent deve ser pelo menos 1')
            
            if v > 20:
                raise ValueError('max_concurrent não pode exceder 20')
        
        return v

class ExecucaoFilterRequest(BaseModel):
    """
    Schema para filtros de listagem de execuções
    """
    categoria_id: Optional[int] = Field(None, gt=0, description="Filtrar por ID da categoria")
    nicho_id: Optional[int] = Field(None, gt=0, description="Filtrar por ID do nicho")
    status: Optional[StatusExecucao] = Field(None, description="Filtrar por status")
    data_inicio: Optional[datetime] = Field(None, description="Data de início para filtro")
    data_fim: Optional[datetime] = Field(None, description="Data de fim para filtro")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Limite de resultados")
    offset: Optional[int] = Field(0, ge=0, description="Offset para paginação")
    
    @validator('categoria_id', 'nicho_id')
    def validar_ids(cls, v):
        """Valida IDs de categoria e nicho"""
        if v is not None:
            if not isinstance(v, int) or v <= 0:
                raise ValueError('ID deve ser um inteiro positivo')
        return v
    
    @validator('limit')
    def validar_limit(cls, v):
        """Valida o limite de resultados"""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError('limit deve ser inteiro')
            
            if v < 1:
                raise ValueError('limit deve ser pelo menos 1')
            
            if v > 1000:
                raise ValueError('limit não pode exceder 1000')
        
        return v
    
    @validator('offset')
    def validar_offset(cls, v):
        """Valida o offset para paginação"""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError('offset deve ser inteiro')
            
            if v < 0:
                raise ValueError('offset deve ser não negativo')
        
        return v
    
    @root_validator
    def validar_datas(cls, values):
        """Valida se data_inicio é anterior a data_fim"""
        data_inicio = values.get('data_inicio')
        data_fim = values.get('data_fim')
        
        if data_inicio and data_fim and data_inicio > data_fim:
            raise ValueError('data_inicio deve ser anterior a data_fim')
        
        return values

class ExecucaoUpdateRequest(BaseModel):
    """
    Schema para atualização de execução
    """
    status: Optional[StatusExecucao] = Field(None, description="Novo status da execução")
    tempo_estimado: Optional[float] = Field(None, ge=0, description="Tempo estimado em segundos")
    tempo_real: Optional[float] = Field(None, ge=0, description="Tempo real em segundos")
    log_path: Optional[str] = Field(None, max_length=255, description="Caminho do arquivo de log")
    
    @validator('tempo_estimado', 'tempo_real')
    def validar_tempos(cls, v):
        """Valida tempos de execução"""
        if v is not None:
            if not isinstance(v, (int, float)):
                raise ValueError('tempo deve ser número')
            
            if v < 0:
                raise ValueError('tempo não pode ser negativo')
            
            if v > 86400:  # 24 horas em segundos
                raise ValueError('tempo não pode exceder 24 horas')
        
        return v
    
    @validator('log_path')
    def validar_log_path(cls, v):
        """Valida o caminho do arquivo de log"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError('log_path deve ser string')
            
            if not v.strip():
                raise ValueError('log_path não pode estar vazio')
            
            if len(v) > 255:
                raise ValueError('log_path deve ter no máximo 255 caracteres')
            
            # Validar caracteres permitidos em caminhos
            if not re.match(r'^[a-zA-Z0-9\/\-_\.]+$', v):
                raise ValueError('log_path contém caracteres inválidos')
        
        return v

class ExecucaoResponse(BaseModel):
    """
    Schema de resposta para execução
    """
    id: int
    id_categoria: int
    palavras_chave: List[str]
    cluster_usado: str
    prompt_usado: str
    status: str
    data_execucao: datetime
    tempo_estimado: Optional[float]
    tempo_real: Optional[float]
    log_path: Optional[str]
    
    class Config:
        from_attributes = True

class ExecucaoCreateResponse(BaseModel):
    """
    Schema de resposta para criação de execução
    """
    execucao_id: int
    prompt_preenchido: str
    categoria_id: int
    palavras_chave: List[str]
    cluster: str

class ExecucaoLoteResponse(BaseModel):
    """
    Schema de resposta para execução em lote
    """
    lote_id: str
    total_execucoes: int
    execucoes_criadas: List[int]
    status: str
    mensagem: str

class ExecucaoLoteStatusResponse(BaseModel):
    """
    Schema de resposta para status de lote
    """
    lote_id: str
    total_execucoes: int
    execucoes_concluidas: int
    execucoes_falharam: int
    execucoes_pendentes: int
    progresso_percentual: float
    status: str
    tempo_estimado_restante: Optional[float]

class ExecucaoErrorResponse(BaseModel):
    """
    Schema de resposta de erro
    """
    erro: str
    codigo: Optional[str] = None
    detalhes: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Funções utilitárias de validação
def validar_json_palavras_chave(palavras_json: str) -> List[str]:
    """
    Valida e converte JSON de palavras-chave para lista
    """
    try:
        palavras = json.loads(palavras_json)
        
        if not isinstance(palavras, list):
            raise ValueError("palavras_chave deve ser uma lista JSON")
        
        if not palavras:
            raise ValueError("palavras_chave não pode estar vazia")
        
        # Validar cada palavra
        for i, palavra in enumerate(palavras):
            if not isinstance(palavra, str):
                raise ValueError(f"palavra-chave {i+1} deve ser string")
            
            if not palavra.strip():
                raise ValueError(f"palavra-chave {i+1} não pode estar vazia")
            
            if len(palavra) > 100:
                raise ValueError(f"palavra-chave {i+1} deve ter no máximo 100 caracteres")
        
        return palavras
    
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido para palavras_chave: {str(e)}")

def validar_status_transicao(status_atual: str, novo_status: str) -> bool:
    """
    Valida se a transição de status é permitida
    """
    transicoes_permitidas = {
        'pendente': ['em_execucao', 'cancelado'],
        'em_execucao': ['executado', 'falhou', 'pausado'],
        'pausado': ['em_execucao', 'cancelado'],
        'executado': [],  # Status final
        'falhou': [],     # Status final
        'cancelado': []   # Status final
    }
    
    return novo_status in transicoes_permitidas.get(status_atual, [])

def sanitizar_palavra_chave(palavra: str) -> str:
    """
    Sanitiza uma palavra-chave removendo caracteres perigosos
    """
    # Remover caracteres de controle
    palavra = ''.join(char for char in palavra if ord(char) >= 32)
    
    # Remover caracteres especiais perigosos
    palavra = re.sub(r'[<>"\']', '', palavra)
    
    # Normalizar espaços
    palavra = ' '.join(palavra.split())
    
    return palavra.strip()

def sanitizar_cluster(cluster: str) -> str:
    """
    Sanitiza o campo cluster removendo caracteres perigosos e normalizando espaços
    """
    if not isinstance(cluster, str):
        return ""
    # Remover caracteres de controle
    cluster = ''.join(char for char in cluster if ord(char) >= 32)
    # Remover caracteres especiais perigosos
    cluster = re.sub(r'[<>"\']', '', cluster)
    # Normalizar espaços
    cluster = ' '.join(cluster.split())
    return cluster.strip()

def validar_limites_execucao(categoria_id: int, palavras_chave: List[str]) -> Dict[str, Any]:
    """
    Valida limites de execução (rate limiting, quotas, etc.)
    """
    # Aqui você pode implementar validações específicas
    # como verificar se o usuário não excedeu o limite diário
    # ou se a categoria está ativa
    
    return {
        'valido': True,
        'limite_diario_restante': 100,  # Exemplo
        'categoria_ativa': True,
        'mensagem': 'Limites OK'
    } 