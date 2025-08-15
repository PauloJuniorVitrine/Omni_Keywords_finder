"""
Rotas da API para o Sistema de Preenchimento de Lacunas em Prompts
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib
import json

from ..database import get_db
from ..models.prompt_system import (
    Nicho, Categoria, PromptBase, DadosColetados, PromptPreenchido
)
from ..services.prompt_filler_service import PromptFillerService
from ..schemas.prompt_system_schemas import (
    NichoCreate, NichoResponse, CategoriaCreate, CategoriaResponse,
    DadosColetadosCreate, DadosColetadosResponse, PromptBaseCreate,
    PromptPreenchidoResponse, ProcessamentoResponse
)

router = APIRouter(prefix="/api/prompt-system", tags=["Prompt System"])


# ============================================================================
# ROTAS PARA NICHOS
# ============================================================================

@router.post("/nichos", response_model=NichoResponse)
def criar_nicho(nicho: NichoCreate, db: Session = Depends(get_db)):
    """Cria um novo nicho"""
    # Verificar se já existe nicho com o mesmo nome
    nicho_existente = db.query(Nicho).filter(Nicho.nome == nicho.nome).first()
    if nicho_existente:
        raise HTTPException(status_code=400, detail="Nicho com este nome já existe")
    
    db_nicho = Nicho(
        nome=nicho.nome,
        descricao=nicho.descricao
    )
    db.add(db_nicho)
    db.commit()
    db.refresh(db_nicho)
    
    return db_nicho


@router.get("/nichos", response_model=List[NichoResponse])
def listar_nichos(db: Session = Depends(get_db)):
    """Lista todos os nichos"""
    nichos = db.query(Nicho).all()
    return nichos


@router.get("/nichos/{nicho_id}", response_model=NichoResponse)
def obter_nicho(nicho_id: int, db: Session = Depends(get_db)):
    """Obtém um nicho específico"""
    nicho = db.query(Nicho).filter(Nicho.id == nicho_id).first()
    if not nicho:
        raise HTTPException(status_code=404, detail="Nicho não encontrado")
    return nicho


@router.put("/nichos/{nicho_id}", response_model=NichoResponse)
def atualizar_nicho(nicho_id: int, nicho: NichoCreate, db: Session = Depends(get_db)):
    """Atualiza um nicho"""
    db_nicho = db.query(Nicho).filter(Nicho.id == nicho_id).first()
    if not db_nicho:
        raise HTTPException(status_code=404, detail="Nicho não encontrado")
    
    # Verificar se o novo nome já existe em outro nicho
    if nicho.nome != db_nicho.nome:
        nicho_existente = db.query(Nicho).filter(
            Nicho.nome == nicho.nome,
            Nicho.id != nicho_id
        ).first()
        if nicho_existente:
            raise HTTPException(status_code=400, detail="Nicho com este nome já existe")
    
    db_nicho.nome = nicho.nome
    db_nicho.descricao = nicho.descricao
    db.commit()
    db.refresh(db_nicho)
    
    return db_nicho


@router.delete("/nichos/{nicho_id}")
def deletar_nicho(nicho_id: int, db: Session = Depends(get_db)):
    """Deleta um nicho"""
    nicho = db.query(Nicho).filter(Nicho.id == nicho_id).first()
    if not nicho:
        raise HTTPException(status_code=404, detail="Nicho não encontrado")
    
    db.delete(nicho)
    db.commit()
    
    return {"message": "Nicho deletado com sucesso"}


# ============================================================================
# ROTAS PARA CATEGORIAS
# ============================================================================

@router.post("/categorias", response_model=CategoriaResponse)
def criar_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    """Cria uma nova categoria"""
    # Verificar se o nicho existe
    nicho = db.query(Nicho).filter(Nicho.id == categoria.nicho_id).first()
    if not nicho:
        raise HTTPException(status_code=404, detail="Nicho não encontrado")
    
    # Verificar se já existe categoria com o mesmo nome no nicho
    categoria_existente = db.query(Categoria).filter(
        Categoria.nicho_id == categoria.nicho_id,
        Categoria.nome == categoria.nome
    ).first()
    if categoria_existente:
        raise HTTPException(status_code=400, detail="Categoria com este nome já existe neste nicho")
    
    db_categoria = Categoria(
        nicho_id=categoria.nicho_id,
        nome=categoria.nome,
        descricao=categoria.descricao
    )
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    
    return db_categoria


@router.get("/categorias", response_model=List[CategoriaResponse])
def listar_categorias(nicho_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Lista categorias, opcionalmente filtradas por nicho"""
    query = db.query(Categoria)
    if nicho_id:
        query = query.filter(Categoria.nicho_id == nicho_id)
    
    categorias = query.all()
    return categorias


@router.get("/categorias/{categoria_id}", response_model=CategoriaResponse)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Obtém uma categoria específica"""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@router.put("/categorias/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(categoria_id: int, categoria: CategoriaCreate, db: Session = Depends(get_db)):
    """Atualiza uma categoria"""
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Verificar se o nicho existe
    nicho = db.query(Nicho).filter(Nicho.id == categoria.nicho_id).first()
    if not nicho:
        raise HTTPException(status_code=404, detail="Nicho não encontrado")
    
    # Verificar se o novo nome já existe no mesmo nicho
    if categoria.nome != db_categoria.nome or categoria.nicho_id != db_categoria.nicho_id:
        categoria_existente = db.query(Categoria).filter(
            Categoria.nicho_id == categoria.nicho_id,
            Categoria.nome == categoria.nome,
            Categoria.id != categoria_id
        ).first()
        if categoria_existente:
            raise HTTPException(status_code=400, detail="Categoria com este nome já existe neste nicho")
    
    db_categoria.nicho_id = categoria.nicho_id
    db_categoria.nome = categoria.nome
    db_categoria.descricao = categoria.descricao
    db.commit()
    db.refresh(db_categoria)
    
    return db_categoria


@router.delete("/categorias/{categoria_id}")
def deletar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Deleta uma categoria"""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    db.delete(categoria)
    db.commit()
    
    return {"message": "Categoria deletada com sucesso"}


# ============================================================================
# ROTAS PARA PROMPTS BASE
# ============================================================================

@router.post("/prompts-base")
def upload_prompt_base(
    categoria_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload de arquivo TXT para prompt base"""
    # Verificar se a categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Verificar se é um arquivo TXT
    if not arquivo.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Apenas arquivos TXT são permitidos")
    
    # Ler conteúdo do arquivo
    conteudo = arquivo.file.read().decode('utf-8')
    
    # Calcular hash do conteúdo
    hash_conteudo = hashlib.sha256(conteudo.encode()).hexdigest()
    
    # Verificar se já existe prompt base para esta categoria
    prompt_existente = db.query(PromptBase).filter(
        PromptBase.categoria_id == categoria_id
    ).first()
    
    if prompt_existente:
        # Atualizar prompt existente
        prompt_existente.nome_arquivo = arquivo.filename
        prompt_existente.conteudo = conteudo
        prompt_existente.hash_conteudo = hash_conteudo
        db.commit()
        db.refresh(prompt_existente)
        return {"message": "Prompt base atualizado com sucesso", "id": prompt_existente.id}
    else:
        # Criar novo prompt base
        prompt_base = PromptBase(
            categoria_id=categoria_id,
            nome_arquivo=arquivo.filename,
            conteudo=conteudo,
            hash_conteudo=hash_conteudo
        )
        db.add(prompt_base)
        db.commit()
        db.refresh(prompt_base)
        return {"message": "Prompt base criado com sucesso", "id": prompt_base.id}


@router.get("/prompts-base/{categoria_id}")
def obter_prompt_base(categoria_id: int, db: Session = Depends(get_db)):
    """Obtém o prompt base de uma categoria"""
    prompt_base = db.query(PromptBase).filter(
        PromptBase.categoria_id == categoria_id
    ).first()
    
    if not prompt_base:
        raise HTTPException(status_code=404, detail="Prompt base não encontrado")
    
    return {
        "id": prompt_base.id,
        "categoria_id": prompt_base.categoria_id,
        "nome_arquivo": prompt_base.nome_arquivo,
        "conteudo": prompt_base.conteudo,
        "hash_conteudo": prompt_base.hash_conteudo,
        "created_at": prompt_base.created_at
    }


# ============================================================================
# ROTAS PARA DADOS COLETADOS
# ============================================================================

@router.post("/dados-coletados", response_model=DadosColetadosResponse)
def criar_dados_coletados(dados: DadosColetadosCreate, db: Session = Depends(get_db)):
    """Cria novos dados coletados"""
    # Verificar se o nicho existe
    nicho = db.query(Nicho).filter(Nicho.id == dados.nicho_id).first()
    if not nicho:
        raise HTTPException(status_code=404, detail="Nicho não encontrado")
    
    # Verificar se a categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == dados.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Verificar se a categoria pertence ao nicho
    if categoria.nicho_id != dados.nicho_id:
        raise HTTPException(status_code=400, detail="Categoria não pertence ao nicho especificado")
    
    # Verificar se já existem dados para esta categoria
    dados_existente = db.query(DadosColetados).filter(
        DadosColetados.categoria_id == dados.categoria_id,
        DadosColetados.status == 'ativo'
    ).first()
    
    if dados_existente:
        # Atualizar dados existentes
        dados_existente.primary_keyword = dados.primary_keyword
        dados_existente.secondary_keywords = dados.secondary_keywords
        dados_existente.cluster_content = dados.cluster_content
        db.commit()
        db.refresh(dados_existente)
        return dados_existente
    
    # Criar novos dados
    db_dados = DadosColetados(
        nicho_id=dados.nicho_id,
        categoria_id=dados.categoria_id,
        primary_keyword=dados.primary_keyword,
        secondary_keywords=dados.secondary_keywords,
        cluster_content=dados.cluster_content
    )
    db.add(db_dados)
    db.commit()
    db.refresh(db_dados)
    
    return db_dados


@router.get("/dados-coletados", response_model=List[DadosColetadosResponse])
def listar_dados_coletados(
    nicho_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista dados coletados, opcionalmente filtrados"""
    query = db.query(DadosColetados)
    
    if nicho_id:
        query = query.filter(DadosColetados.nicho_id == nicho_id)
    if categoria_id:
        query = query.filter(DadosColetados.categoria_id == categoria_id)
    
    dados = query.all()
    return dados


# ============================================================================
# ROTAS PARA PROCESSAMENTO
# ============================================================================

@router.post("/processar/{categoria_id}/{dados_id}", response_model=PromptPreenchidoResponse)
def processar_preenchimento(categoria_id: int, dados_id: int, db: Session = Depends(get_db)):
    """Processa preenchimento de lacunas para uma categoria específica"""
    service = PromptFillerService(db)
    
    try:
        prompt_preenchido = service.processar_preenchimento(categoria_id, dados_id)
        return prompt_preenchido
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")


@router.post("/processar-lote/{nicho_id}", response_model=ProcessamentoResponse)
def processar_lote(nicho_id: int, db: Session = Depends(get_db)):
    """Processa preenchimento em lote para um nicho"""
    service = PromptFillerService(db)
    
    try:
        resultados = service.processar_lote(nicho_id)
        return {
            "nicho_id": nicho_id,
            "total_processados": len(resultados),
            "resultados": [{"id": r.id, "status": r.status} for r in resultados]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento em lote: {str(e)}")


@router.get("/prompts-preenchidos", response_model=List[PromptPreenchidoResponse])
def listar_prompts_preenchidos(
    nicho_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista prompts preenchidos, opcionalmente filtrados"""
    query = db.query(PromptPreenchido)
    
    if nicho_id:
        query = query.join(DadosColetados).filter(DadosColetados.nicho_id == nicho_id)
    if categoria_id:
        query = query.join(DadosColetados).filter(DadosColetados.categoria_id == categoria_id)
    if status:
        query = query.filter(PromptPreenchido.status == status)
    
    prompts = query.all()
    return prompts


@router.get("/prompts-preenchidos/{prompt_id}", response_model=PromptPreenchidoResponse)
def obter_prompt_preenchido(prompt_id: int, db: Session = Depends(get_db)):
    """Obtém um prompt preenchido específico"""
    prompt = db.query(PromptPreenchido).filter(PromptPreenchido.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt preenchido não encontrado")
    return prompt


@router.get("/prompts-preenchidos/{prompt_id}/download")
def download_prompt_preenchido(prompt_id: int, db: Session = Depends(get_db)):
    """Download do prompt preenchido"""
    prompt = db.query(PromptPreenchido).filter(PromptPreenchido.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt preenchido não encontrado")
    
    return {
        "id": prompt.id,
        "conteudo": prompt.prompt_preenchido,
        "nome_arquivo": f"prompt_preenchido_{prompt_id}.txt",
        "created_at": prompt.created_at
    } 