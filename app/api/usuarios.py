from typing import Any

def get_user_by_id(user_id: int) -> Any:
    # Stub para mock nos testes
    pass

def current_user_can(user_id: int) -> bool:
    # Stub para mock nos testes
    pass

def delete_user(user_id: int) -> bool:
    # Stub para mock nos testes
    pass

def deletar_usuario(user_id: int) -> bool:
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Usuário não encontrado")
    if not current_user_can(user_id):
        raise PermissionError("Permissão negada")
    delete_user(user_id)
    return True 