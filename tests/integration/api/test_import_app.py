from typing import Dict, List, Optional, Any
def test_import_app_main():
    try:
        import app.main
    except Exception as e:
        assert False, f"Falha ao importar app.main: {e}" 