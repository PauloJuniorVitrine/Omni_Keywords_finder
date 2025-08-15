import sys
from backend.app.models import db
from backend.app.models.role import Role
from backend.app.models.permission import Permission
from backend.app.models.user import User
from backend.app.models.associations import role_permissions, user_roles
from datetime import datetime
from typing import Dict, List, Optional, Any

# Papéis padrão
ROLES = [
    {"nome": "admin", "descricao": "Administrador do sistema"},
    {"nome": "gestor", "descricao": "Gestor de operações"},
    {"nome": "operador", "descricao": "Operador de tarefas"},
    {"nome": "visualizador", "descricao": "Acesso somente leitura"},
]

# Permissões padrão (exemplo, ajustar conforme endpoints reais)
PERMISSIONS = [
    {"nome": "ver_dashboard", "descricao": "Acessar dashboard"},
    {"nome": "gerenciar_usuarios", "descricao": "CRUD de usuários"},
    {"nome": "gerenciar_papeis", "descricao": "CRUD de papéis"},
    {"nome": "gerenciar_permissoes", "descricao": "CRUD de permissões"},
    {"nome": "executar_prompts", "descricao": "Executar prompts"},
]

# Mapeamento papel-permissão (exemplo)
ROLE_PERMISSIONS = {
    "admin": [p["nome"] for p in PERMISSIONS],
    "gestor": ["ver_dashboard", "executar_prompts"],
    "operador": ["executar_prompts"],
    "visualizador": ["ver_dashboard"],
}

def log(msg):
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(f"[SEED][{timestamp}] {msg}")

def seed_roles_permissions():
    # Papéis
    for role_data in ROLES:
        role = Role.query.filter_by(nome=role_data["nome"]).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
            log(f"Criado papel: {role_data['nome']}")
        else:
            log(f"Papel já existe: {role_data['nome']}")
    db.session.commit()

    # Permissões
    for perm_data in PERMISSIONS:
        perm = Permission.query.filter_by(nome=perm_data["nome"]).first()
        if not perm:
            perm = Permission(**perm_data)
            db.session.add(perm)
            log(f"Criada permissão: {perm_data['nome']}")
        else:
            log(f"Permissão já existe: {perm_data['nome']}")
    db.session.commit()

    # Associação papel-permissão
    for role_name, perms in ROLE_PERMISSIONS.items():
        role = Role.query.filter_by(nome=role_name).first()
        if not role:
            log(f"Papel não encontrado para associação: {role_name}")
            continue
        for perm_name in perms:
            perm = Permission.query.filter_by(nome=perm_name).first()
            if perm and perm not in role.permissions:
                role.permissions.append(perm)
                log(f"Associada permissão {perm_name} ao papel {role_name}")
        db.session.commit()

if __name__ == "__main__":
    try:
        seed_roles_permissions()
        log("Seed concluído com sucesso.")
    except Exception as e:
        log(f"Erro ao executar seed: {e}")
        sys.exit(1) 