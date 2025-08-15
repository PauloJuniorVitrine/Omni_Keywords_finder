#!/usr/bin/env python3
"""
Script para gerar chave JWT segura para o OMNI KEYWORDS FINDER
Segue as melhores práticas de segurança OWASP e NIST
"""

import secrets
import string
import base64
import hashlib
import os
from typing import str

def generate_secure_jwt_secret(length: int = 64) -> str:
    """
    Gera uma chave JWT segura usando secrets.SystemRandom()
    
    Args:
        length: Comprimento da chave (padrão: 64 caracteres)
    
    Returns:
        Chave JWT segura em base64
    """
    # Usar secrets.SystemRandom() para criptografia segura
    secure_random = secrets.SystemRandom()
    
    # Gerar bytes aleatórios seguros
    random_bytes = secure_random.randbytes(length)
    
    # Codificar em base64 para string legível
    jwt_secret = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    
    # Remover padding '=' para compatibilidade
    jwt_secret = jwt_secret.rstrip('=')
    
    return jwt_secret

def validate_jwt_secret(secret: str) -> bool:
    """
    Valida se a chave JWT atende aos critérios de segurança
    
    Args:
        secret: Chave JWT para validar
    
    Returns:
        True se válida, False caso contrário
    """
    if not secret:
        return False
    
    # Verificar comprimento mínimo (32 caracteres)
    if len(secret) < 32:
        return False
    
    # Verificar entropia (pelo menos 256 bits)
    entropy = len(set(secret)) * 4  # Aproximação de entropia
    if entropy < 256:
        return False
    
    return True

def main():
    """Função principal"""
    print("🔐 GERADOR DE CHAVE JWT SEGURA - OMNI KEYWORDS FINDER")
    print("=" * 60)
    
    # Gerar chave segura
    jwt_secret = generate_secure_jwt_secret()
    
    print(f"✅ Chave JWT gerada com sucesso!")
    print(f"📏 Comprimento: {len(jwt_secret)} caracteres")
    print(f"🔒 Entropia estimada: {len(set(jwt_secret)) * 4} bits")
    
    # Validar chave
    if validate_jwt_secret(jwt_secret):
        print("✅ Chave atende aos critérios de segurança")
    else:
        print("❌ Chave não atende aos critérios de segurança")
        return 1
    
    print("\n📋 COMO USAR:")
    print("1. Adicione ao seu arquivo .env:")
    print(f"   JWT_SECRET_KEY={jwt_secret}")
    print("\n2. Ou exporte como variável de ambiente:")
    print(f"   export JWT_SECRET_KEY='{jwt_secret}'")
    
    print("\n⚠️  IMPORTANTE:")
    print("- Mantenha esta chave em segredo")
    print("- Não commite no repositório")
    print("- Use chaves diferentes para cada ambiente")
    print("- Rotacione a chave periodicamente")
    
    # Salvar em arquivo temporário (opcional)
    save_to_file = input("\n💾 Salvar em arquivo temporário? (y/N): ").lower().strip()
    if save_to_file == 'y':
        filename = f"jwt_secret_{int(os.time())}.txt"
        with open(filename, 'w') as f:
            f.write(f"JWT_SECRET_KEY={jwt_secret}\n")
        print(f"✅ Chave salva em: {filename}")
        print("⚠️  Lembre-se de deletar o arquivo após usar!")
    
    return 0

if __name__ == "__main__":
    exit(main()) 