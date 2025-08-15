"""
Schemas Pydantic para o Sistema de Preenchimento de Lacunas em Prompts
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime


# ============================================================================
# SCHEMAS PARA NICHOS
# ============================================================================

class NichoBase(BaseModel):
    """Schema base para nichos"""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do nicho")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do nicho")


class NichoCreate(NichoBase):
    """Schema para criação de nichos"""
    pass


class NichoUpdate(NichoBase):
    """Schema para atualização de nichos"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = Field(None, max_length=1000)


class NichoResponse(NichoBase):
    """Schema para resposta de nichos"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS PARA CATEGORIAS
# ============================================================================

class CategoriaBase(BaseModel):
    """Schema base para categorias"""
    nicho_id: int = Field(..., description="ID do nicho")
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição da categoria")


class CategoriaCreate(CategoriaBase):
    """Schema para criação de categorias"""
    pass


class CategoriaUpdate(CategoriaBase):
    """Schema para atualização de categorias"""
    nicho_id: Optional[int] = None
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = Field(None, max_length=1000)


class CategoriaResponse(CategoriaBase):
    """Schema para resposta de categorias"""
    id: int
    created_at: datetime
    updated_at: datetime
    nicho: NichoResponse
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS PARA DADOS COLETADOS
# ============================================================================

class DadosColetadosBase(BaseModel):
    """Schema base para dados coletados"""
    nicho_id: int = Field(..., description="ID do nicho")
    categoria_id: int = Field(..., description="ID da categoria")
    primary_keyword: str = Field(..., min_length=1, max_length=255, description="Palavra-chave principal")
    secondary_keywords: Optional[str] = Field(None, max_length=1000, description="Palavras-chave secundárias (separadas por vírgula)")
    cluster_content: str = Field(..., min_length=1, max_length=2000, description="Conteúdo do cluster")
    
    @validator('primary_keyword')
    def validar_primary_keyword(cls, value):
        """Valida palavra-chave principal"""
        if not value or not value.strip():
            raise ValueError('Palavra-chave principal não pode estar vazia')
        return value.strip()
    
    @validator('cluster_content')
    def validar_cluster_content(cls, value):
        """Valida conteúdo do cluster"""
        if not value or not value.strip():
            raise ValueError('Conteúdo do cluster não pode estar vazio')
        return value.strip()
    
    @validator('secondary_keywords')
    def validar_secondary_keywords(cls, value):
        """Valida palavras-chave secundárias"""
        if value:
            # Remover espaços extras e normalizar
            keywords = [kw.strip() for kw in value.split(',') if kw.strip()]
            return ', '.join(keywords)
        return value


class DadosColetadosCreate(DadosColetadosBase):
    """Schema para criação de dados coletados"""
    pass


class DadosColetadosUpdate(BaseModel):
    """Schema para atualização de dados coletados"""
    primary_keyword: Optional[str] = Field(None, min_length=1, max_length=255)
    secondary_keywords: Optional[str] = Field(None, max_length=1000)
    cluster_content: Optional[str] = Field(None, min_length=1, max_length=2000)
    status: Optional[str] = Field(None, regex='^(ativo|inativo|processando)$')
    
    @validator('primary_keyword')
    def validar_primary_keyword(cls, value):
        if value is not None:
            if not value.strip():
                raise ValueError('Palavra-chave principal não pode estar vazia')
            return value.strip()
        return value
    
    @validator('cluster_content')
    def validar_cluster_content(cls, value):
        if value is not None:
            if not value.strip():
                raise ValueError('Conteúdo do cluster não pode estar vazio')
            return value.strip()
        return value
    
    @validator('secondary_keywords')
    def validar_secondary_keywords(cls, value):
        if value is not None:
            keywords = [kw.strip() for kw in value.split(',') if kw.strip()]
            return ', '.join(keywords)
        return value


class DadosColetadosResponse(DadosColetadosBase):
    """Schema para resposta de dados coletados"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    nicho: NichoResponse
    categoria: CategoriaResponse
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS PARA PROMPTS BASE
# ============================================================================

class PromptBaseCreate(BaseModel):
    """Schema para criação de prompts base"""
    categoria_id: int = Field(..., description="ID da categoria")
    nome_arquivo: str = Field(..., min_length=1, max_length=255, description="Nome do arquivo")
    conteudo: str = Field(..., min_length=1, description="Conteúdo do prompt")
    
    @validator('nome_arquivo')
    def validar_nome_arquivo(cls, value):
        """Valida nome do arquivo"""
        if not value.endswith('.txt'):
            raise ValueError('Nome do arquivo deve terminar com .txt')
        return value
    
    @validator('conteudo')
    def validar_conteudo(cls, value):
        """Valida conteúdo do prompt"""
        if not value or not value.strip():
            raise ValueError('Conteúdo do prompt não pode estar vazio')
        return value


class PromptBaseResponse(BaseModel):
    """Schema para resposta de prompts base"""
    id: int
    categoria_id: int
    nome_arquivo: str
    conteudo: str
    hash_conteudo: str
    created_at: datetime
    updated_at: datetime
    categoria: CategoriaResponse
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS PARA PROMPTS PREENCHIDOS
# ============================================================================

class PromptPreenchidoResponse(BaseModel):
    """Schema para resposta de prompts preenchidos"""
    id: int
    dados_coletados_id: int
    prompt_base_id: int
    prompt_original: str
    prompt_preenchido: str
    lacunas_detectadas: Optional[str]  # JSON string
    lacunas_preenchidas: Optional[str]  # JSON string
    status: str
    tempo_processamento: Optional[int]
    created_at: datetime
    updated_at: datetime
    dados_coletados: DadosColetadosResponse
    prompt_base: PromptBaseResponse
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS PARA PROCESSAMENTO
# ============================================================================

class ProcessamentoRequest(BaseModel):
    """Schema para requisição de processamento"""
    categoria_id: int = Field(..., description="ID da categoria")
    dados_id: int = Field(..., description="ID dos dados coletados")


class ProcessamentoResponse(BaseModel):
    """Schema para resposta de processamento"""
    nicho_id: Optional[int] = None
    categoria_id: Optional[int] = None
    dados_id: Optional[int] = None
    total_processados: int
    sucessos: int = 0
    erros: int = 0
    resultados: List[dict]
    tempo_total: Optional[int] = None  # em milissegundos


# ============================================================================
# SCHEMAS PARA DETECÇÃO DE LACUNAS
# ============================================================================

class LacunaDetectada(BaseModel):
    """Schema para lacuna detectada"""
    tipo: str  # primary_keyword, secondary_keywords, cluster_content
    original: str
    quantidade: int
    posicoes: List[int] = []  # posições no texto


class DeteccaoLacunasResponse(BaseModel):
    """Schema para resposta de detecção de lacunas"""
    categoria_id: int
    total_lacunas: int
    lacunas: List[LacunaDetectada]
    conteudo_preview: str  # primeiros 500 caracteres


# ============================================================================
# SCHEMAS PARA ESTATÍSTICAS
# ============================================================================

class EstatisticasNicho(BaseModel):
    """Schema para estatísticas por nicho"""
    nicho_id: int
    nome_nicho: str
    total_categorias: int
    categorias_com_prompt: int
    categorias_com_dados: int
    prompts_preenchidos: int
    tempo_medio_processamento: Optional[float] = None


class EstatisticasGerais(BaseModel):
    """Schema para estatísticas gerais"""
    total_nichos: int
    total_categorias: int
    total_prompts_base: int
    total_dados_coletados: int
    total_prompts_preenchidos: int
    tempo_medio_processamento: Optional[float] = None
    taxa_sucesso: Optional[float] = None  # porcentagem
    estatisticas_por_nicho: List[EstatisticasNicho]


# ============================================================================
# SCHEMAS PARA LOGS
# ============================================================================

class LogOperacaoResponse(BaseModel):
    """Schema para resposta de logs de operação"""
    id: int
    tipo_operacao: str
    entidade: str
    entidade_id: Optional[int]
    detalhes: Optional[str]  # JSON string
    status: str
    tempo_execucao: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS PARA VALIDAÇÃO
# ============================================================================

class ValidacaoPromptRequest(BaseModel):
    """Schema para requisição de validação de prompt"""
    categoria_id: int
    conteudo: str


class ValidacaoPromptResponse(BaseModel):
    """Schema para resposta de validação de prompt"""
    valido: bool
    lacunas_detectadas: List[str]
    lacunas_obrigatorias: List[str]
    lacunas_opcionais: List[str]
    erros: List[str] = []
    avisos: List[str] = []


# ============================================================================
# SCHEMAS PARA INTEGRAÇÃO COM IA GENERATIVA
# ============================================================================

class AIGenerationRequest(BaseModel):
    """Schema para requisição de geração de conteúdo"""
    prompt_id: int = Field(..., description="ID do prompt preenchido")
    provider: Optional[str] = Field("openai", description="Provedor de IA (openai, claude, deepseek)")
    model: Optional[str] = Field("default", description="Modelo específico do provedor")
    max_tokens: Optional[int] = Field(2000, description="Máximo de tokens na resposta")
    temperature: Optional[float] = Field(0.7, description="Temperatura da geração (0-1)")


class AIGenerationResponse(BaseModel):
    """Schema para resposta de geração de conteúdo"""
    generation_id: str
    content: str
    provider: str
    model: str
    tokens_used: int
    cost_estimate: float
    quality_score: float
    generation_time: float
    status: str
    error: Optional[str] = None
    
    class Config:
        from_attributes = True


class AIGenerationStats(BaseModel):
    """Schema para estatísticas de geração"""
    total_generations: int
    completed: int
    failed: int
    success_rate: float
    total_tokens: int
    total_cost: float
    average_quality: float
    providers_used: List[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS PARA TEMPLATES AVANÇADOS
# ============================================================================

class TemplateCreate(BaseModel):
    """Schema para criação de template"""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do template")
    content: str = Field(..., min_length=1, description="Conteúdo do template")
    autor: str = Field(..., min_length=1, max_length=100, description="Autor do template")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do template")
    tags: List[str] = Field(default_factory=list, description="Tags do template")


class TemplateResponse(BaseModel):
    """Schema para resposta de template"""
    template_id: str
    nome: str
    tipo: str
    versao: str
    autor: str
    descricao: str
    tags: List[str]
    variaveis: List[str]
    performance_score: float
    uso_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateVersion(BaseModel):
    """Schema para versão de template"""
    version_id: str
    template_id: str
    content: str
    changes: str
    author: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ABTestResult(BaseModel):
    """Schema para resultado de teste A/B"""
    test_id: str
    template_a_id: str
    template_b_id: str
    template_a_metrics: Dict[str, float]
    template_b_metrics: Dict[str, float]
    winner: str
    confidence_level: float
    test_duration_days: int
    total_participants: int
    
    class Config:
        from_attributes = True 