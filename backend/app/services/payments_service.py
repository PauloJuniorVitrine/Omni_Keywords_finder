import logging, os
from typing import Dict, List, Optional, Any

def process_payment(valor: float, metodo: str = 'stripe') -> dict:
    """Processa pagamento simulado, logando operação."""
    logging.info(f'Processando pagamento: valor={valor}, metodo={metodo}')
    # Simulação: sempre retorna sucesso
    return {'status': 'success', 'metodo': metodo, 'valor': valor} 