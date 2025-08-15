"""
Módulo: security_utils_v1
Funções de segurança: sanitização, controle de acesso, logging de tentativas suspeitas.
"""
import re
from typing import Any, List, Dict
from backend.app.services.auditoria_v1 import registrar_log

def sanitizar_entrada(valor: Any) -> Any:
    """
    Sanitiza strings removendo scripts, SQL injection e caracteres perigosos.
    - Remove tags HTML potencialmente perigosas
    - Remove comandos SQL e padrões de ataque comuns
    - Retorna o valor original se não for string
    Args:
        valor (Any): Valor a ser sanitizado
    Returns:
        Any: Valor sanitizado ou original
    Raises:
        TypeError: Se valor for de tipo não suportado
    """
    if valor is None:
        return None
    if not isinstance(valor, (str, int, float, bool, list, dict)):
        raise TypeError(f"Tipo de valor não suportado: {type(valor)}")
    if not isinstance(valor, str):
        return valor
    # Remove tags HTML
    valor = re.sub(r'<.*?>', '', valor)
    # Remove comandos SQL e padrões de ataque
    valor = re.sub(r'(--|;|/\*|\*/|xp_|exec|drop|select|insert|delete|update)', '', valor, flags=re.IGNORECASE)
    return valor

def checar_permissao(usuario: str, permissoes: List[str], permissao_necessaria: str, logger=None) -> bool:
    """
    Verifica se o usuário possui a permissão necessária.
    - Loga tentativa negada caso não possua
    Args:
        usuario (str): Identificador do usuário
        permissoes (List[str]): Permissões do usuário
        permissao_necessaria (str): Permissão requerida
        logger (callable, opcional): Função de log customizada
    Returns:
        bool: True se permitido, False caso contrário
    Raises:
        TypeError: Se permissoes não for lista ou permissao_necessaria não for string
    """
    log_fn = logger if logger is not None else registrar_log
    if not isinstance(permissoes, list):
        raise TypeError("permissoes deve ser uma lista de strings")
    if not isinstance(permissao_necessaria, str):
        raise TypeError("permissao_necessaria deve ser string")
    if permissao_necessaria not in permissoes:
        # Loga tentativa negada de acesso
        log_fn('tentativa_negada', 'Seguranca', usuario, f'Permissão negada: {permissao_necessaria}')
        return False
    return True

def logar_tentativa_suspeita(usuario: str, acao: str, detalhes: str, logger=None):
    """
    Loga tentativa suspeita de acesso ou manipulação.
    - Registra log detalhado da ação suspeita
    Args:
        usuario (str): Identificador do usuário
        acao (str): Ação suspeita
        detalhes (str): Descrição detalhada
        logger (callable, opcional): Função de log customizada
    Returns:
        None
    Raises:
        TypeError: Se argumentos não forem string/int/float
    """
    log_fn = logger if logger is not None else registrar_log
    if not all(isinstance(arg, (str, int, float, bool)) for arg in [usuario, acao, detalhes]):
        raise TypeError("Argumentos usuario, acao e detalhes devem ser string, int, float ou bool")
    log_fn('tentativa_suspeita', 'Seguranca', usuario, str(detalhes) + f' (ação: {acao})') 