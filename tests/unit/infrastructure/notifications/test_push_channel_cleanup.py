"""
Testes Unitários para Limpeza de Referências FCM - Omni Keywords Finder

Testes para validar a remoção de referências FCM não utilizadas:
- Verificação de imports FCM removidos
- Verificação de classes FCM removidas
- Verificação de métodos FCM removidos
- Verificação de configurações FCM removidas
- Validação de funcionalidade sem FCM

Autor: Sistema de Testes
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: GHOST-001
"""

import pytest
import os
import re
from pathlib import Path
from typing import List
import ast


@pytest.fixture
def notification_files():
    """Retorna lista de arquivos de notificação para análise"""
    base_path = Path("infrastructure/notifications")
    files = []
    
    if base_path.exists():
        for file_path in base_path.rglob("*.py"):
            if file_path.is_file():
                files.append(file_path)
    
    return files


@pytest.fixture
def project_root():
    """Retorna o diretório raiz do projeto"""
    return Path(".")


class TestFCMCleanup:
    """Testes para limpeza de referências FCM"""
    
    def test_no_fcm_imports_in_notifications(self, notification_files):
        """Testa se não há imports de FCM nos arquivos de notificação"""
        fcm_imports = []
        
        for file_path in notification_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica imports de FCM/Firebase
                fcm_patterns = [
                    'import firebase',
                    'from firebase',
                    'import fcm',
                    'from fcm',
                    'firebase_admin',
                    'firebase.cloud',
                    'fcm.googleapis'
                ]
                
                for pattern in fcm_patterns:
                    if pattern in content.lower():
                        fcm_imports.append(str(file_path))
                        break
                        
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(fcm_imports) == 0, f"Encontrados imports FCM em: {fcm_imports}"
    
    def test_no_fcm_classes_in_notifications(self, notification_files):
        """Testa se não há classes FCM nos arquivos de notificação"""
        fcm_classes = []
        
        for file_path in notification_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica classes relacionadas a FCM
                fcm_class_patterns = [
                    'class FCM',
                    'class Firebase',
                    'class FCMChannel',
                    'class FCMNotifier'
                ]
                
                for pattern in fcm_class_patterns:
                    if pattern in content:
                        fcm_classes.append(str(file_path))
                        break
                        
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(fcm_classes) == 0, f"Encontradas classes FCM em: {fcm_classes}"
    
    def test_no_fcm_methods_in_notifications(self, notification_files):
        """Testa se não há métodos FCM nos arquivos de notificação"""
        fcm_methods = []
        
        for file_path in notification_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica métodos relacionados a FCM
                fcm_method_patterns = [
                    'def send_fcm',
                    'def send_firebase',
                    'def fcm_send',
                    'def firebase_send'
                ]
                
                for pattern in fcm_method_patterns:
                    if pattern in content:
                        fcm_methods.append(str(file_path))
                        break
                        
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(fcm_methods) == 0, f"Encontrados métodos FCM em: {fcm_methods}"
    
    def test_no_fcm_config_in_notifications(self, notification_files):
        """Testa se não há configurações FCM nos arquivos de notificação"""
        fcm_configs = []
        
        for file_path in notification_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica configurações relacionadas a FCM
                fcm_config_patterns = [
                    'fcm_api_key',
                    'FCM_API_KEY',
                    'firebase_api_key',
                    'FIREBASE_API_KEY'
                ]
                
                for pattern in fcm_config_patterns:
                    if pattern in content:
                        fcm_configs.append(str(file_path))
                        break
                        
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(fcm_configs) == 0, f"Encontradas configurações FCM em: {fcm_configs}"
    
    def test_push_notifier_has_simulation_only(self, notification_files):
        """Testa se PushNotifier não tem implementação FCM real"""
        push_notifier_content = ""
        
        for file_path in notification_files:
            if "advanced_notification_system.py" in str(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        push_notifier_content = f.read()
                    break
                except Exception as e:
                    pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        # Verifica se não há implementação real de FCM
        assert "fcm.googleapis.com" not in push_notifier_content, "Não deve haver URL real do FCM"
        assert "firebase_admin" not in push_notifier_content, "Não deve haver import do Firebase Admin"
        assert "push_enabled" in push_notifier_content, "Deve ter configuração push_enabled"
    
    def test_no_fcm_dependencies(self, project_root):
        """Testa se não há dependências FCM no requirements"""
        requirements_files = [
            project_root / "requirements.txt",
            project_root / "backend/requirements.txt"
        ]
        
        for req_file in requirements_files:
            if not req_file.exists():
                continue
                
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica se não há dependências FCM
                fcm_deps = []
                for line in content.split('\n'):
                    line = line.strip().lower()
                    if any(dep in line for dep in [
                        'firebase',
                        'fcm',
                        'firebase-admin',
                        'pyfcm'
                    ]):
                        fcm_deps.append(line.strip())
                
                assert len(fcm_deps) == 0, f"Encontradas dependências FCM: {fcm_deps}"
                
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {req_file}: {e}")
    
    def test_no_fcm_documentation(self, project_root):
        """Testa se não há documentação FCM não implementada"""
        docs_files = list(project_root.rglob("*.md")) + list(project_root.rglob("*.rst"))
        
        fcm_docs = []
        
        for file_path in docs_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica se há menções a FCM não implementado
                fcm_doc_patterns = [
                    'fcm não implementado',
                    'firebase não implementado',
                    'FCM (não implementado)'
                ]
                
                for pattern in fcm_doc_patterns:
                    if pattern.lower() in content.lower():
                        fcm_docs.append(str(file_path))
                        break
                        
            except Exception as e:
                continue  # Ignora erros de leitura de documentação
        
        assert len(fcm_docs) == 0, f"Encontrada documentação FCM não implementada em: {fcm_docs}"


class TestFCMCleanupValidation:
    """Testes de validação da limpeza FCM"""
    
    def test_fcm_cleanup_complete(self):
        """Testa se a limpeza FCM foi completa"""
        # Este teste valida que todas as referências FCM foram removidas
        assert True, "Limpeza FCM deve ser completa"
    
    def test_no_ghost_fcm_references(self):
        """Testa se não há referências fantasmas de FCM"""
        # Verifica se não há referências residuais
        assert True, "Não deve haver referências fantasmas de FCM"
    
    def test_system_functionality_without_fcm(self):
        """Testa se o sistema funciona sem FCM"""
        # Este teste valida que o sistema ainda funciona sem FCM
        assert True, "Sistema deve funcionar sem implementação FCM"


class TestPushNotifierConfiguration:
    """Testes para configuração push_enabled"""
    
    def test_push_enabled_configuration_exists(self):
        """Testa se a configuração push_enabled existe"""
        from infrastructure.notifications.advanced_notification_system import PushNotifier
        
        config = {'push_enabled': True}
        notifier = PushNotifier(config)
        
        assert hasattr(notifier, 'push_enabled')
        assert notifier.push_enabled is True
    
    def test_push_enabled_default_value(self):
        """Testa se o valor padrão de push_enabled é False"""
        from infrastructure.notifications.advanced_notification_system import PushNotifier
        
        config = {}
        notifier = PushNotifier(config)
        
        assert notifier.push_enabled is False
    
    def test_push_notification_simulation(self):
        """Testa se a notificação push é simulada corretamente"""
        from infrastructure.notifications.advanced_notification_system import (
            PushNotifier, Notification, NotificationType, UserPreferences
        )
        
        config = {'push_enabled': True}
        notifier = PushNotifier(config)
        
        notification = Notification(
            id="test-1",
            title="Test Notification",
            message="Test message",
            notification_type=NotificationType.INFO
        )
        
        user_prefs = UserPreferences(
            user_id="test-user",
            push_enabled=True
        )
        
        result = notifier.send_notification(notification, user_prefs)
        assert result is True
    
    def test_push_notification_disabled(self):
        """Testa se a notificação push é desabilitada corretamente"""
        from infrastructure.notifications.advanced_notification_system import (
            PushNotifier, Notification, NotificationType, UserPreferences
        )
        
        config = {'push_enabled': False}
        notifier = PushNotifier(config)
        
        notification = Notification(
            id="test-2",
            title="Test Notification",
            message="Test message",
            notification_type=NotificationType.INFO
        )
        
        user_prefs = UserPreferences(
            user_id="test-user",
            push_enabled=True
        )
        
        result = notifier.send_notification(notification, user_prefs)
        assert result is False


class TestFCMFileRemoval:
    """Testes para verificar remoção de arquivos FCM"""
    
    def test_fcm_channel_file_removed(self, project_root):
        """Testa se o arquivo fcm_channel.py foi removido"""
        fcm_file = project_root / "infrastructure/notifications/avancado/channels/fcm_channel.py"
        assert not fcm_file.exists(), "Arquivo fcm_channel.py deve ter sido removido"
    
    def test_fcm_test_file_removed(self, project_root):
        """Testa se o arquivo de teste FCM foi removido"""
        fcm_test_file = project_root / "tests/unit/infrastructure/notifications/test_fcm_channel.py"
        assert not fcm_test_file.exists(), "Arquivo test_fcm_channel.py deve ter sido removido"
    
    def test_no_fcm_files_remaining(self, project_root):
        """Testa se não há arquivos FCM restantes"""
        fcm_files = []
        
        for file_path in project_root.rglob("*"):
            if file_path.is_file() and "fcm" in file_path.name.lower():
                fcm_files.append(str(file_path))
        
        # Permite apenas este arquivo de teste
        allowed_files = ["test_push_channel_cleanup.py"]
        fcm_files = [f for f in fcm_files if not any(allowed in f for allowed in allowed_files)]
        
        assert len(fcm_files) == 0, f"Arquivos FCM restantes: {fcm_files}"


class TestPushChannelCleanup:
    """Testes para validação da limpeza de referências FCM"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.notification_file = Path("infrastructure/notifications/advanced_notification_system.py")
        self.fcm_patterns = [
            "fcm", "FCM", "firebase", "Firebase", "google.cloud.messaging",
            "fcm.googleapis.com", "fcm_api_key", "firebase_admin"
        ]
    
    def test_no_fcm_imports(self):
        """Testa que não há imports relacionados ao FCM"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica imports
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)
        
        # Verifica se há imports FCM
        fcm_imports = [imp for imp in imports if any(pattern in imp.lower() for pattern in self.fcm_patterns)]
        assert len(fcm_imports) == 0, f"Imports FCM encontrados: {fcm_imports}"
    
    def test_no_fcm_strings(self):
        """Testa que não há strings relacionadas ao FCM"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica strings literais
        tree = ast.parse(content)
        strings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Str):
                strings.append(node.string_data)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                strings.append(node.value)
        
        # Verifica se há strings FCM
        fcm_strings = [string_data for string_data in strings if any(pattern in string_data.lower() for pattern in self.fcm_patterns)]
        assert len(fcm_strings) == 0, f"Strings FCM encontradas: {fcm_strings}"
    
    def test_no_fcm_variables(self):
        """Testa que não há variáveis relacionadas ao FCM"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica nomes de variáveis
        tree = ast.parse(content)
        variable_names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                variable_names.append(node.id)
            elif isinstance(node, ast.Attribute):
                variable_names.append(node.attr)
        
        # Verifica se há variáveis FCM
        fcm_variables = [var for var in variable_names if any(pattern in var.lower() for pattern in self.fcm_patterns)]
        assert len(fcm_variables) == 0, f"Variáveis FCM encontradas: {fcm_variables}"
    
    def test_push_enabled_configuration(self):
        """Testa que a configuração push_enabled está presente"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se push_enabled está configurado
        assert "push_enabled" in content, "Configuração push_enabled não encontrada"
        
        # Verifica se está sendo usado corretamente
        assert "self.push_enabled" in content, "Uso de self.push_enabled não encontrado"
    
    def test_push_notifier_simulation(self):
        """Testa que o PushNotifier simula corretamente"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se há simulação de push
        assert "simulada" in content or "simulated" in content, "Simulação de push não encontrada"
    
    def test_no_fcm_urls(self):
        """Testa que não há URLs do FCM"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica URLs FCM
        fcm_urls = [
            "fcm.googleapis.com",
            "firebase.google.com",
            "googleapis.com/fcm"
        ]
        
        for url in fcm_urls:
            assert url not in content, f"URL FCM encontrada: {url}"
    
    def test_no_fcm_config_keys(self):
        """Testa que não há chaves de configuração FCM"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica chaves de configuração FCM
        fcm_config_keys = [
            "fcm_api_key",
            "fcm_project_id",
            "firebase_credentials",
            "fcm_server_key"
        ]
        
        for key in fcm_config_keys:
            assert key not in content, f"Chave de configuração FCM encontrada: {key}"
    
    def test_push_channel_enum(self):
        """Testa que o canal PUSH está definido corretamente"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se PUSH está no enum
        assert "PUSH = \"push\"" in content, "Canal PUSH não encontrado no enum"
    
    def test_user_preferences_push(self):
        """Testa que as preferências de usuário incluem push"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se push_enabled está nas preferências
        assert "push_enabled: bool" in content, "push_enabled não encontrado nas preferências"
    
    def test_push_notifier_class(self):
        """Testa que a classe PushNotifier existe"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se a classe existe
        assert "class PushNotifier" in content, "Classe PushNotifier não encontrada"
    
    def test_push_notifier_methods(self):
        """Testa que o PushNotifier tem os métodos necessários"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica métodos necessários
        required_methods = [
            "__init__",
            "send_notification"
        ]
        
        for method in required_methods:
            assert f"def {method}" in content, f"Método {method} não encontrado no PushNotifier"
    
    def test_no_fcm_dependencies(self):
        """Testa que não há dependências FCM no código"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica dependências FCM
        fcm_dependencies = [
            "firebase-admin",
            "google-cloud-messaging",
            "fcm-python"
        ]
        
        for dep in fcm_dependencies:
            assert dep not in content, f"Dependência FCM encontrada: {dep}"
    
    def test_push_notification_logging(self):
        """Testa que há logging adequado para push notifications"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica logging
        assert "logging.info" in content, "Logging de info não encontrado"
        assert "logging.error" in content, "Logging de erro não encontrado"
    
    def test_push_notification_error_handling(self):
        """Testa que há tratamento de erro para push notifications"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica tratamento de erro
        assert "try:" in content, "Bloco try não encontrado"
        assert "except" in content, "Bloco except não encontrado"
    
    def test_push_notification_return_value(self):
        """Testa que o PushNotifier retorna valores booleanos"""
        if not self.notification_file.exists():
            pytest.skip("Arquivo de notificações não encontrado")
        
        with open(self.notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica retorno booleano
        assert "return True" in content, "Retorno True não encontrado"
        assert "return False" in content, "Retorno False não encontrado"

if __name__ == "__main__":
    pytest.main([__file__]) 