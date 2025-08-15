import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

BLOGS_PATH = Path("blogs/blogs.json")
BLOGS_PATH.parent.mkdir(exist_ok=True)

AUDIT_PATH = Path("blogs/audit.jsonl")
AUDIT_PATH.parent.mkdir(exist_ok=True)

def carregar_blogs() -> List[Dict]:
    if BLOGS_PATH.exists():
        try:
            with open(BLOGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_blog(blog: Dict, ip: str = None, user_agent: str = None) -> None:
    blogs = carregar_blogs()
    # Validação de unicidade de domínio
    if any(b.get("dominio", "").lower() == blog.get("dominio", "").lower() for b in blogs):
        raise ValueError("Domínio já cadastrado.")
    blogs.append(blog)
    try:
        with open(BLOGS_PATH, "w", encoding="utf-8") as f:
            json.dump(blogs, f, ensure_ascii=False, indent=2)
        # Log de auditoria
        audit = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "dominio": blog.get("dominio"),
            "ip": ip,
            "user_agent": user_agent
        }
        with open(AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit, ensure_ascii=False) + "\n")
    except Exception as e:
        raise IOError(f"Erro ao salvar blog: {e}") 