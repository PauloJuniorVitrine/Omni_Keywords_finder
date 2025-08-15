import pytest
from infrastructure.monitoramento import observabilidade
from typing import Dict, List, Optional, Any
import re
import uuid

def test_generate_trace_uuid():
    uuid1 = observabilidade.generate_trace_uuid()
    uuid2 = observabilidade.generate_trace_uuid()
    # Validação de tipo e formato UUID v4
    assert isinstance(uuid1, str)
    assert uuid1 != uuid2
    assert len(uuid1) == 36
    # Regex de UUID v4
    uuid_regex = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$", re.I)
    assert uuid_regex.match(uuid1), f"UUID inválido: {uuid1}"
    # Validação usando módulo uuid
    parsed = uuid.UUID(uuid1)
    assert parsed.version == 4

def test_log_structured(capsys):
    observabilidade.log_structured("mensagem de teste", extra={"foo": "bar"}, level="info")
    captured = capsys.readouterr()
    # Não há garantia de saída no stdout, mas não deve lançar exceção 