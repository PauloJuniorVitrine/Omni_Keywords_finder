import pytest
from domain.models import Blog, Categoria
from typing import Dict, List, Optional, Any

def make_categoria(nome, descricao="desc"):
    return Categoria(nome=nome, descricao=descricao)

def test_blog_nao_permite_categorias_duplicadas():
    blog = Blog(dominio="meublog.com", nome="Meu Blog", descricao="desc", publico_alvo="público", tom_voz="voz")
    cat1 = make_categoria("Tecnologia")
    blog.adicionar_categoria(cat1)
    # Duplicata exata
    cat2 = make_categoria("Tecnologia")
    with pytest.raises(ValueError, match="Categoria já existe"):
        blog.adicionar_categoria(cat2)
    # Duplicata case-insensitive
    cat3 = make_categoria("tecnologia")
    with pytest.raises(ValueError, match="Categoria já existe"):
        blog.adicionar_categoria(cat3)
    # Duplicata com espaços
    cat4 = make_categoria("  tecnologia  ")
    with pytest.raises(ValueError, match="Categoria já existe"):
        blog.adicionar_categoria(cat4)
    # Duplicata com acento
    cat5 = make_categoria("tecnológia")
    blog.adicionar_categoria(cat5)  # Não deve ser considerado duplicata se acento for diferente
    # Duplicata com nome diferente
    cat6 = make_categoria("Negócios")
    blog.adicionar_categoria(cat6)
    assert len(blog.categorias) == 3 