import sys
import os
from typing import Dict, List, Optional, Any
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

import pytest
from app.api.usuarios import deletar_usuario
from unittest.mock import patch, MagicMock

@pytest.mark.parametrize("user_id,exists,perm,expected", [
    (1, True, True, True),    # Sucesso
    (999, False, True, False),# Usuário inexistente
    (2, True, False, False),  # Permissão negada
])
def test_deletar_usuario(user_id, exists, perm, expected):
    with patch("app.api.usuarios.get_user_by_id", return_value=MagicMock() if exists else None), \
         patch("app.api.usuarios.current_user_can", return_value=perm):
        if not perm:
            with pytest.raises(PermissionError):
                deletar_usuario(user_id)
        elif not exists:
            with pytest.raises(ValueError):
                deletar_usuario(user_id)
        else:
            assert deletar_usuario(user_id) is True

def test_deletar_usuario_rollback_visual():
    with patch("app.api.usuarios.get_user_by_id", return_value=MagicMock()), \
         patch("app.api.usuarios.current_user_can", return_value=True), \
         patch("app.api.usuarios.delete_user", side_effect=Exception("DB error")):
        with pytest.raises(Exception):
            deletar_usuario(1)
        # Aqui você pode validar se o feedback visual de erro foi disparado (mock de logger ou feedback) 