import pytest
import json
from infrastructure.persistencia.blogs import carregar_blogs, salvar_blog
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from typing import Dict, List, Optional, Any

def test_carregar_blogs_existente():
    data = [{"dominio": "meublog.com"}]
    m = mock_open(read_data=json.dumps(data))
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", m):
        out = carregar_blogs()
        assert out == data

def test_carregar_blogs_inexistente():
    with patch("pathlib.Path.exists", return_value=False):
        out = carregar_blogs()
        assert out == []

def test_carregar_blogs_erro_json():
    m = mock_open(read_data="{corrompido}")
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", m):
        out = carregar_blogs()
        assert out == []

def test_salvar_blog_sucesso():
    blog = {"dominio": "meublog.com"}
    m = mock_open()
    with patch("infrastructure.persistencia.blogs.carregar_blogs", return_value=[]), \
         patch("builtins.open", m) as open_mock:
        salvar_blog(blog, ip="1.2.3.4", user_agent="ua")
        assert open_mock.call_count == 2  # blogs.json + audit.jsonl

def test_salvar_blog_duplicado():
    blog = {"dominio": "meublog.com"}
    with patch("infrastructure.persistencia.blogs.carregar_blogs", return_value=[{"dominio": "meublog.com"}]):
        with pytest.raises(ValueError):
            salvar_blog(blog)

def test_salvar_blog_erro_io():
    blog = {"dominio": "meublog.com"}
    with patch("infrastructure.persistencia.blogs.carregar_blogs", return_value=[]), \
         patch("builtins.open", side_effect=IOError("erro")):
        with pytest.raises(IOError):
            salvar_blog(blog)

def test_salvar_blog_unicidade(tmp_path):
    path = tmp_path / "blogs.json"
    path.write_text(json.dumps([{"dominio": "blog.com"}]), encoding="utf-8")
    with patch("infrastructure.persistencia.blogs.BLOGS_PATH", path):
        with pytest.raises(ValueError):
            salvar_blog({"dominio": "blog.com"})

def test_salvar_blog_unicidade_case_insensitive(tmp_path):
    path = tmp_path / "blogs.json"
    path.write_text(json.dumps([{"dominio": "BLOG.com"}]), encoding="utf-8")
    with patch("infrastructure.persistencia.blogs.BLOGS_PATH", path):
        with pytest.raises(ValueError):
            salvar_blog({"dominio": "blog.com"})

def test_salvar_blog_dominio_com_espacos(tmp_path):
    path = tmp_path / "blogs.json"
    with patch("infrastructure.persistencia.blogs.BLOGS_PATH", path):
        salvar_blog({"dominio": "  novo.com  "})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert any(b["dominio"].strip() == "novo.com" for b in data)

def test_salvar_blog_multiplos(tmp_path):
    path = tmp_path / "blogs.json"
    with patch("infrastructure.persistencia.blogs.BLOGS_PATH", path):
        salvar_blog({"dominio": "a.com"})
        salvar_blog({"dominio": "b.com"})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert any(b["dominio"] == "a.com" for b in data)
        assert any(b["dominio"] == "b.com" for b in data)

def test_salvar_blog_dados_incompletos(tmp_path):
    path = tmp_path / "blogs.json"
    audit_path = tmp_path / "audit.jsonl"
    with patch("infrastructure.persistencia.blogs.BLOGS_PATH", path), \
         patch("infrastructure.persistencia.blogs.AUDIT_PATH", audit_path):
        salvar_blog({"dominio": "value.com"})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert any(b["dominio"] == "value.com" for b in data)

def test_salvar_blog_dominio_vazio(tmp_path):
    path = tmp_path / "blogs.json"
    with patch("infrastructure.persistencia.blogs.BLOGS_PATH", path):
        salvar_blog({"dominio": ""})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert any(b["dominio"] == "" for b in data)

def test_salvar_blog_audit_erro_leitura(tmp_path, monkeypatch):
    path = tmp_path / "blogs.json"
    audit_path = tmp_path / "audit.jsonl"
    path.write_text("[]", encoding="utf-8")  # Garante que o arquivo existe
    real_open = open
    def open_side_effect(file, *args, **kwargs):
        if str(file).endswith("audit.jsonl"):
            return mock_open(read_data="{corrompido}")().return_value
        return real_open(file, *args, **kwargs)
    monkeypatch.setattr("builtins.open", open_side_effect)
    with patch("infrastructure.persistencia.blogs.BLOGS_PATH", path), \
         patch("infrastructure.persistencia.blogs.AUDIT_PATH", audit_path):
        salvar_blog({"dominio": "result.com"})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert any(b["dominio"] == "result.com" for b in data)

def test_salvar_blog_audit_dados_ausentes(tmp_path):
    path = tmp_path / "blogs.json"
    audit_path = tmp_path / "audit.jsonl"
    with patch("infrastructure.persistencia.blogs.BLOGS_PATH", path), \
         patch("infrastructure.persistencia.blogs.AUDIT_PATH", audit_path):
        salvar_blog({"dominio": "data.com"})
        audit_lines = audit_path.read_text(encoding="utf-8").splitlines()
        assert any("data.com" in list_data for list_data in audit_lines) 