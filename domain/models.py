"""
Modelos de domínio do sistema de geração de clusters e conteúdo SEO.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Literal
from enum import Enum
import re
from shared.config import FUNNEL_STAGES
from shared.logger import logger

class IntencaoBusca(Enum):
    """Enum para classificação da intenção de busca."""
    INFORMACIONAL = "informacional"
    COMERCIAL = "comercial"
    NAVEGACIONAL = "navegacional"
    TRANSACIONAL = "transacional"
    COMPARACAO = "comparacao"

    def __str__(self) -> str:
        """Retorna o valor do enum como string."""
        return self.value

    def lower(self) -> str:
        """Retorna o valor do enum em lowercase."""
        return self.value.lower()

@dataclass
class Keyword:
    """Representa uma palavra-chave com suas métricas e classificações."""
    termo: str
    volume_busca: int
    cpc: float
    concorrencia: float
    intencao: IntencaoBusca
    score: float = 0.0
    justificativa: str = ""
    fonte: str = ""
    data_coleta: datetime = field(default_factory=datetime.utcnow)
    ordem_no_cluster: int = -1  # Posição no cluster, default -1 se não atribuído
    fase_funil: str = ""      # Fase do funil, default vazio
    nome_artigo: str = ""  # Nome do artigo, ex: Artigo1, Artigo2

    def __post_init__(self):
        """Validações pós-inicialização."""
        # Validação explícita para None
        if self.termo is None:
            raise ValueError("Termo não pode ser vazio")
        # Normaliza o termo primeiro
        self.termo = self.termo.strip()
        
        # Validações básicas
        if not self.termo:
            raise ValueError("Termo não pode ser vazio")
        if len(self.termo) > 100:
            raise ValueError("Termo não pode ter mais de 100 caracteres")
        if self.volume_busca < 0:
            raise ValueError("Volume de busca não pode ser negativo")
        if not 0 <= self.concorrencia <= 1:
            raise ValueError("Concorrência deve estar entre 0 e 1")
        if self.cpc < 0:
            raise ValueError("CPC não pode ser negativo")
        if not isinstance(self.intencao, IntencaoBusca):
            raise ValueError("Intenção de busca inválida")
        
        # Validação de caracteres especiais mais restritiva
        if not re.fullmatch(r'^[\w\string_data\-.,?!]+$', self.termo):
            raise ValueError("Termo contém caracteres especiais não permitidos")

    def __eq__(self, other: object) -> bool:
        """Compara keywords pelo termo (case insensitive)."""
        if not isinstance(other, Keyword):
            return NotImplemented
        return self.termo.lower() == other.termo.lower()

    def __hash__(self) -> int:
        """Hash baseado no termo para permitir uso em sets."""
        return hash(self.termo.lower())

    def calcular_score(self, weights: Dict[str, float]) -> float:
        """Calcula o score da palavra-chave conforme fórmula do prompt."""
        try:
            intencao_val = 1.0 if self.intencao in [IntencaoBusca.COMERCIAL, IntencaoBusca.TRANSACIONAL] else 0.5
            self.score = (
                weights.get("volume", 0.4) * (self.volume_busca / 100) +
                weights.get("cpc", 0.3) * self.cpc +
                weights.get("intencao", 0.2) * intencao_val +
                weights.get("concorrencia", 0.1) * self.concorrencia
            )
            self.justificativa = (
                f"Score = {weights.get('volume', 0.4)}*volume({self.volume_busca}) + "
                f"{weights.get('cpc', 0.3)}*cpc({self.cpc}) + "
                f"{weights.get('intencao', 0.2)}*intencao({intencao_val}) + "
                f"{weights.get('concorrencia', 0.1)}*concorrencia({self.concorrencia}) = {self.score:.4f}"
            )
            return self.score
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_score",
                "status": "error",
                "source": "keyword.calcular_score",
                "details": {
                    "erro": str(e),
                    "termo": self.termo,
                    "volume": self.volume_busca,
                    "cpc": self.cpc,
                    "concorrencia": self.concorrencia,
                    "intencao": self.intencao.value
                }
            })
            raise

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa a instância para dicionário, padronizando campos opcionais.
        """
        data = {
            "termo": self.termo,
            "volume_busca": self.volume_busca,
            "cpc": self.cpc,
            "concorrencia": self.concorrencia,
            "intencao": self.intencao.value,
            "score": self.score,
            "justificativa": self.justificativa,
            "fonte": self.fonte,
            "data_coleta": self.data_coleta.isoformat() if self.data_coleta else None
        }
        # Adiciona ordem, fase_funil e nome_artigo se definidos
        if hasattr(self, "ordem_no_cluster") and self.ordem_no_cluster >= 0:
            data["ordem_no_cluster"] = self.ordem_no_cluster
            data["nome_artigo"] = f"Artigo{self.ordem_no_cluster+1}"
        if hasattr(self, "fase_funil") and self.fase_funil:
            data["fase_funil"] = self.fase_funil
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Keyword':
        """
        Cria uma instância de Keyword a partir de um dicionário padronizado.
        """
        raw_intencao = data.get("intencao", IntencaoBusca.INFORMACIONAL)
        if isinstance(raw_intencao, str):
            try:
                intencao = IntencaoBusca(raw_intencao)
            except ValueError:
                intencao = IntencaoBusca.INFORMACIONAL
        else:
            intencao = raw_intencao if raw_intencao is not None else IntencaoBusca.INFORMACIONAL
        return cls(
            termo=data.get("termo", ""),
            volume_busca=int(data.get("volume_busca", 0)),
            cpc=float(data.get("cpc", 0)),
            concorrencia=float(data.get("concorrencia", 0)),
            intencao=intencao,
            score=float(data.get("score", 0)),
            justificativa=data.get("justificativa", ""),
            fonte=data.get("fonte", ""),
            data_coleta=datetime.fromisoformat(data["data_coleta"]) if data.get("data_coleta") else datetime.utcnow(),
            ordem_no_cluster=data.get("ordem_no_cluster", -1),
            fase_funil=data.get("fase_funil", ""),
            nome_artigo=data.get("nome_artigo", "")
        )

    @staticmethod
    def normalizar_termo(termo: str) -> str:
        """Normaliza um termo (strip e lower)."""
        return termo.strip().lower() if termo else ""

@dataclass
class Categoria:
    """Representa uma categoria de blog com suas configurações."""
    nome: str
    descricao: str
    palavras_chave: List[str] = field(default_factory=list)
    clusters_gerados: List['Cluster'] = field(default_factory=list)
    status_execucao: str = "pendente"
    ultima_execucao: Optional[datetime] = None

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.nome or len(self.nome.strip()) == 0:
            raise ValueError("Nome da categoria não pode ser vazio")
        if not self.descricao:
            self.descricao = self.nome
        if len(self.nome) > 50:
            raise ValueError("Nome da categoria não pode ter mais de 50 caracteres")
        if len(self.descricao) > 200:
            raise ValueError("Descrição não pode ter mais de 200 caracteres")
        
        # Normaliza campos
        self.nome = self.nome.strip()
        self.descricao = self.descricao.strip()
        
        # Validação de caracteres especiais
        if not re.match(r'^[\w\string_data\-]+$', self.nome):
            raise ValueError("Nome da categoria contém caracteres especiais não permitidos")
        
        # Remove palavras-chave duplicadas e valida
        palavras_chave_set = set()
        palavras_chave_normalizadas = []
        for kw in self.palavras_chave:
            kw_norm = kw.strip().lower()
            if kw_norm and kw_norm not in palavras_chave_set:
                if len(kw_norm) > 100:
                    raise ValueError("Palavra-chave não pode ter mais de 100 caracteres")
                if not re.match(r'^[\w\string_data\-.,?!]+$', kw_norm):
                    raise ValueError(f"Palavra-chave '{kw}' contém caracteres especiais não permitidos")
                palavras_chave_set.add(kw_norm)
                palavras_chave_normalizadas.append(kw_norm)
        self.palavras_chave = palavras_chave_normalizadas

    def atualizar_status(self, novo_status: str) -> None:
        """Atualiza o status de execução e timestamp."""
        self.status_execucao = novo_status
        self.ultima_execucao = datetime.utcnow()
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "atualizacao_status_categoria",
            "status": "success",
            "source": "categoria.atualizar_status",
            "details": {
                "categoria": self.nome,
                "novo_status": novo_status,
                "timestamp_execucao": self.ultima_execucao.isoformat()
            }
        })

    def adicionar_cluster(self, cluster: 'Cluster') -> None:
        """Adiciona um novo cluster à categoria."""
        if cluster.categoria != self.nome:
            raise ValueError("Cluster não pertence a esta categoria")
        self.clusters_gerados.append(cluster)
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "cluster_adicionado",
            "status": "success",
            "source": "categoria.adicionar_cluster",
            "details": {
                "categoria": self.nome,
                "cluster_id": cluster.id,
                "total_clusters": len(self.clusters_gerados)
            }
        })

    def to_dict(self) -> Dict[str, Any]:
        """Converte a categoria para dicionário."""
        return {
            "nome": self.nome,
            "descricao": self.descricao,
            "palavras_chave": self.palavras_chave,
            "status_execucao": self.status_execucao,
            "ultima_execucao": self.ultima_execucao.isoformat() if self.ultima_execucao else None,
            "total_clusters": len(self.clusters_gerados)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Categoria':
        """Cria uma instância de Categoria a partir de um dicionário."""
        return cls(
            nome=data.get("nome", ""),
            descricao=data.get("descricao", ""),
            palavras_chave=data.get("palavras_chave", []),
            clusters_gerados=[Cluster.from_dict(c) for c in data.get("clusters_gerados", [])],
            status_execucao=data.get("status_execucao", "pendente"),
            ultima_execucao=datetime.fromisoformat(data["ultima_execucao"]) if data.get("ultima_execucao") else None
        )

@dataclass
class Blog:
    """Representa um blog com suas configurações e categorias."""
    dominio: str
    nome: str
    descricao: str
    publico_alvo: str
    tom_voz: str
    categorias: List[Categoria] = field(default_factory=list)
    prompt_base: str = ""
    data_cadastro: datetime = field(default_factory=datetime.utcnow)
    ultima_atualizacao: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.dominio or len(self.dominio.strip()) == 0:
            raise ValueError("Domínio não pode ser vazio")
        if not self.nome:
            self.nome = self.dominio
        if len(self.nome) > 100:
            raise ValueError("Nome do blog não pode ter mais de 100 caracteres")
        if len(self.descricao) > 500:
            raise ValueError("Descrição não pode ter mais de 500 caracteres")
        if len(self.publico_alvo) > 200:
            raise ValueError("Público-alvo não pode ter mais de 200 caracteres")
        if len(self.tom_voz) > 50:
            raise ValueError("Tom de voz não pode ter mais de 50 caracteres")
        
        # Validação de domínio
        if not re.match(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$', self.dominio.lower()):
            raise ValueError("Domínio inválido")
        
        # Normaliza campos
        self.dominio = self.dominio.strip().lower()
        self.nome = self.nome.strip()
        self.descricao = self.descricao.strip()
        self.publico_alvo = self.publico_alvo.strip()
        self.tom_voz = self.tom_voz.strip()
        
        # Validar unicidade de categorias
        categorias_nomes: Set[str] = set()
        for categoria in self.categorias:
            if categoria.nome.lower() in categorias_nomes:
                raise ValueError(f"Categoria duplicada: {categoria.nome}")
            categorias_nomes.add(categoria.nome.lower())

    def adicionar_categoria(self, categoria: Categoria) -> None:
        """Adiciona uma nova categoria ao blog."""
        if any(c.nome.lower() == categoria.nome.lower() for c in self.categorias):
            raise ValueError(f"Categoria já existe: {categoria.nome}")
        
        self.categorias.append(categoria)
        self.ultima_atualizacao = datetime.utcnow()
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "categoria_adicionada",
            "status": "success",
            "source": "blog.adicionar_categoria",
            "details": {
                "blog": self.dominio,
                "categoria": categoria.nome,
                "total_categorias": len(self.categorias)
            }
        })

    def remover_categoria(self, nome_categoria: str) -> None:
        """Remove uma categoria do blog."""
        categoria_anterior = len(self.categorias)
        self.categorias = [c for c in self.categorias if c.nome.lower() != nome_categoria.lower()]
        
        if len(self.categorias) == categoria_anterior:
            raise ValueError(f"Categoria não encontrada: {nome_categoria}")
        
        self.ultima_atualizacao = datetime.utcnow()
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "categoria_removida",
            "status": "success",
            "source": "blog.remover_categoria",
            "details": {
                "blog": self.dominio,
                "categoria": nome_categoria,
                "categorias_restantes": len(self.categorias)
            }
        })

    def to_dict(self) -> Dict[str, Any]:
        """Converte o blog para dicionário."""
        return {
            "dominio": self.dominio,
            "nome": self.nome,
            "descricao": self.descricao,
            "publico_alvo": self.publico_alvo,
            "tom_voz": self.tom_voz,
            "categorias": [cat.to_dict() for cat in self.categorias],
            "total_categorias": len(self.categorias),
            "data_cadastro": self.data_cadastro.isoformat(),
            "ultima_atualizacao": self.ultima_atualizacao.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Blog':
        """Cria uma instância de Blog a partir de um dicionário."""
        return cls(
            dominio=data.get("dominio", ""),
            nome=data.get("nome", ""),
            descricao=data.get("descricao", ""),
            publico_alvo=data.get("publico_alvo", ""),
            tom_voz=data.get("tom_voz", ""),
            categorias=[Categoria.from_dict(c) for c in data.get("categorias", [])],
            prompt_base=data.get("prompt_base", ""),
            data_cadastro=datetime.fromisoformat(data["data_cadastro"]) if data.get("data_cadastro") else datetime.utcnow(),
            ultima_atualizacao=datetime.fromisoformat(data["ultima_atualizacao"]) if data.get("ultima_atualizacao") else datetime.utcnow()
        )

@dataclass
class Cluster:
    """Representa um cluster de palavras-chave relacionadas."""
    id: str
    keywords: List[Keyword]
    similaridade_media: float
    fase_funil: str
    categoria: str
    blog_dominio: str
    data_criacao: datetime = field(default_factory=datetime.utcnow)
    status_geracao: str = "pendente"
    prompt_gerado: Optional[str] = None

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.id or len(self.id.strip()) == 0:
            raise ValueError("ID do cluster não pode ser vazio")
        
        if not 4 <= len(self.keywords) <= 8:
            raise ValueError("Cluster deve conter entre 4 e 8 keywords")
        
        if self.fase_funil not in FUNNEL_STAGES:
            raise ValueError(f"Fase do funil inválida: {self.fase_funil}")
        
        if not 0 <= self.similaridade_media <= 1:
            raise ValueError("Similaridade média deve estar entre 0 e 1")
        
        if len(self.id) > 50:
            raise ValueError("ID do cluster não pode ter mais de 50 caracteres")
        
        # Validação de ID
        if not re.match(r'^[a-zA-Z0-9\-_]+$', self.id):
            raise ValueError("ID do cluster contém caracteres inválidos")
        
        # Validar keywords únicas
        keywords_set = set()
        for keyword in self.keywords:
            if keyword.termo.lower() in keywords_set:
                raise ValueError(f"Keyword duplicada no cluster: {keyword.termo}")
            keywords_set.add(keyword.termo.lower())
        
        # Normaliza campos
        self.id = self.id.strip()
        self.categoria = self.categoria.strip()
        self.blog_dominio = self.blog_dominio.strip().lower()
        
        # Validação de domínio mais permissiva
        if not re.match(r'^[a-z0-9][a-z0-9\-_.]+[a-z0-9]$', self.blog_dominio):
            raise ValueError("Domínio do blog inválido")

    def atualizar_status(self, novo_status: str) -> None:
        """Atualiza o status de geração do cluster."""
        self.status_geracao = novo_status
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "atualizacao_status_cluster",
            "status": "success",
            "source": "cluster.atualizar_status",
            "details": {
                "cluster_id": self.id,
                "novo_status": novo_status,
                "categoria": self.categoria,
                "blog": self.blog_dominio
            }
        })

    def to_dict(self) -> Dict[str, Any]:
        """Converte o cluster para dicionário."""
        return {
            "id": self.id,
            "keywords": [key.to_dict() for key in self.keywords],
            "similaridade_media": self.similaridade_media,
            "fase_funil": self.fase_funil,
            "categoria": self.categoria,
            "blog_dominio": self.blog_dominio,
            "data_criacao": self.data_criacao.isoformat(),
            "status_geracao": self.status_geracao,
            "tem_prompt": bool(self.prompt_gerado)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cluster':
        """Cria uma instância de Cluster a partir de um dicionário."""
        return cls(
            id=data.get("id", ""),
            keywords=[Keyword.from_dict(key) for key in data.get("keywords", [])],
            similaridade_media=float(data.get("similaridade_media", 0)),
            fase_funil=data.get("fase_funil", "descoberta"),
            categoria=data.get("categoria", ""),
            blog_dominio=data.get("blog_dominio", ""),
            data_criacao=datetime.fromisoformat(data["data_criacao"]) if data.get("data_criacao") else datetime.utcnow(),
            status_geracao=data.get("status_geracao", "pendente"),
            prompt_gerado=data.get("prompt_gerado")
        )

@dataclass
class Execucao:
    """Representa uma execução de geração de conteúdo."""
    id: str
    blog_dominio: str
    categoria: str
    tipo_execucao: str  # "individual" ou "lote"
    modelo_ia: str
    inicio_execucao: datetime = field(default_factory=datetime.utcnow)
    fim_execucao: Optional[datetime] = None
    status: str = "iniciada"
    clusters_gerados: List[str] = field(default_factory=list)
    erros: List[str] = field(default_factory=list)
    metricas: Dict = field(default_factory=dict)

    # Constantes
    TIPOS_EXECUCAO = ["individual", "lote"]
    STATUS_VALIDOS = ["iniciada", "processando", "concluida", "erro"]
    MAX_ERROS = 3

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.id or len(self.id.strip()) == 0:
            raise ValueError("ID da execução não pode ser vazio")
        
        if self.tipo_execucao not in self.TIPOS_EXECUCAO:
            raise ValueError(f"Tipo de execução inválido: {self.tipo_execucao}")
        
        if not self.modelo_ia or len(self.modelo_ia.strip()) == 0:
            raise ValueError("Modelo de IA não pode ser vazio")
        
        if len(self.id) > 50:
            raise ValueError("ID da execução não pode ter mais de 50 caracteres")
        
        if len(self.modelo_ia) > 50:
            raise ValueError("Nome do modelo de IA não pode ter mais de 50 caracteres")
        
        # Validação de ID
        if not re.match(r'^[a-zA-Z0-9\-_]+$', self.id):
            raise ValueError("ID da execução contém caracteres inválidos")
        
        # Normaliza campos
        self.id = self.id.strip()
        self.blog_dominio = self.blog_dominio.strip().lower()
        self.categoria = self.categoria.strip()
        self.modelo_ia = self.modelo_ia.strip().lower()
        
        # Validação de domínio
        if not re.match(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$', self.blog_dominio):
            raise ValueError("Domínio do blog inválido")

    def adicionar_erro(self, erro: str) -> None:
        """Adiciona um erro à execução e verifica limite."""
        self.erros.append(erro)
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "erro_execucao",
            "status": "error",
            "source": "execucao.adicionar_erro",
            "details": {
                "execucao_id": self.id,
                "erro": erro,
                "total_erros": len(self.erros),
                "tipo_execucao": self.tipo_execucao
            }
        })
        
        if len(self.erros) >= self.MAX_ERROS:
            self.finalizar(sucesso=False)

    def adicionar_cluster(self, cluster_id: str) -> None:
        """Adiciona um cluster gerado à execução."""
        self.clusters_gerados.append(cluster_id)
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "cluster_gerado",
            "status": "success",
            "source": "execucao.adicionar_cluster",
            "details": {
                "execucao_id": self.id,
                "cluster_id": cluster_id,
                "total_clusters": len(self.clusters_gerados),
                "tipo_execucao": self.tipo_execucao
            }
        })

    def atualizar_status(self, novo_status: str) -> None:
        """Atualiza o status da execução."""
        if novo_status not in self.STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {novo_status}")
        
        self.status = novo_status
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "atualizacao_status_execucao",
            "status": "success",
            "source": "execucao.atualizar_status",
            "details": {
                "execucao_id": self.id,
                "novo_status": novo_status,
                "tipo_execucao": self.tipo_execucao,
                "total_clusters": len(self.clusters_gerados)
            }
        })

    def finalizar(self, sucesso: bool = True) -> None:
        """Finaliza a execução com status e métricas."""
        self.fim_execucao = datetime.utcnow()
        self.status = "concluida" if sucesso else "erro"
        
        duracao = (self.fim_execucao - self.inicio_execucao).total_seconds()
        
        self.metricas.update({
            "duracao_segundos": duracao,
            "total_clusters": len(self.clusters_gerados),
            "total_erros": len(self.erros),
            "media_tempo_cluster": duracao / len(self.clusters_gerados) if self.clusters_gerados else 0
        })
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execucao_finalizada",
            "status": "success" if sucesso else "error",
            "source": "execucao.finalizar",
            "details": {
                "execucao_id": self.id,
                "sucesso": sucesso,
                "metricas": self.metricas,
                "tipo_execucao": self.tipo_execucao,
                "duracao_total": duracao
            }
        })

    def to_dict(self) -> Dict[str, Any]:
        """Converte a execução para dicionário."""
        return {
            "id": self.id,
            "blog_dominio": self.blog_dominio,
            "categoria": self.categoria,
            "tipo_execucao": self.tipo_execucao,
            "modelo_ia": self.modelo_ia,
            "inicio_execucao": self.inicio_execucao.isoformat(),
            "fim_execucao": self.fim_execucao.isoformat() if self.fim_execucao else None,
            "status": self.status,
            "clusters_gerados": self.clusters_gerados,
            "total_clusters": len(self.clusters_gerados),
            "erros": self.erros,
            "total_erros": len(self.erros),
            "metricas": self.metricas
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Execucao':
        """Cria uma instância de Execucao a partir de um dicionário."""
        return cls(
            id=data.get("id", ""),
            blog_dominio=data.get("blog_dominio", ""),
            categoria=data.get("categoria", ""),
            tipo_execucao=data.get("tipo_execucao", "individual"),
            modelo_ia=data.get("modelo_ia", ""),
            inicio_execucao=datetime.fromisoformat(data["inicio_execucao"]) if data.get("inicio_execucao") else datetime.utcnow(),
            fim_execucao=datetime.fromisoformat(data["fim_execucao"]) if data.get("fim_execucao") else None,
            status=data.get("status", "iniciada"),
            clusters_gerados=data.get("clusters_gerados", []),
            erros=data.get("erros", []),
            metricas=data.get("metricas", {})
        ) 