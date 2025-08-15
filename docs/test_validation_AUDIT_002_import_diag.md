============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.1.1, pluggy-1.5.0
rootdir: D:\PROJETOS\SISTEMAS\PROGRAMAS\omni_keywords_finder
configfile: pytest.ini
plugins: anyio-4.9.0, Faker-24.14.1, asyncio-0.26.0, cov-4.1.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 1 item

tests\integration\api\test_import_app.py F                               [100%]

================================== FAILURES ===================================
____________________________ test_import_app_main _____________________________
tests\integration\api\test_import_app.py:3: in test_import_app_main
    import app.main
E   ModuleNotFoundError: No module named 'app'

During handling of the above exception, another exception occurred:
tests\integration\api\test_import_app.py:5: in test_import_app_main
    assert False, f"Falha ao importar app.main: {e}"
E   AssertionError: Falha ao importar app.main: No module named 'app'
E   assert False
---------------------------- Captured stdout setup ----------------------------
[RESET PRE-TEST] Falha: HTTPConnectionPool(host='localhost', port=5000): Max retries exceeded with url: /api/test/reset (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001FEC4B81E50>: Failed to establish a new connection: [WinError 10061] Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente'))
-------------------------- Captured stdout teardown ---------------------------
[RESET POST-TEST] Falha: HTTPConnectionPool(host='localhost', port=5000): Max retries exceeded with url: /api/test/reset (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001FEC4B815D0>: Failed to establish a new connection: [WinError 10061] Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente'))
============================== warnings summary ===============================
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\_pytest\config\__init__.py:1439
  C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\_pytest\config\__init__.py:1439: PytestConfigWarning: Unknown config option: timeout
  
    self._warn_or_fail_if_strict(f"Unknown config option: {key}\n")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/integration/api/test_import_app.py::test_import_app_main - Asser...
======================== 1 failed, 1 warning in 9.78s =========================
