============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.1.1, pluggy-1.5.0
rootdir: D:\PROJETOS\SISTEMAS\PROGRAMAS\omni_keywords_finder
configfile: pytest.ini
plugins: anyio-4.9.0, Faker-24.14.1, asyncio-0.26.0, cov-4.1.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 0 items / 5 errors

=================================== ERRORS ====================================
______ ERROR collecting tests/integration/api/test_dashboard_metrics.py _______
ImportError while importing test module 'D:\PROJETOS\SISTEMAS\PROGRAMAS\omni_keywords_finder\tests\integration\api\test_dashboard_metrics.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Program Files\Python311\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
D:\PROJETOS\SISTEMAS\omni_keywords_finder\tests\integration\api\test_dashboard_metrics.py:5: in <module>
    ???
E   ModuleNotFoundError: No module named 'app'
____________ ERROR collecting tests/integration/api/test_export.py ____________
ImportError while importing test module 'D:\PROJETOS\SISTEMAS\PROGRAMAS\omni_keywords_finder\tests\integration\api\test_export.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Program Files\Python311\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\integration\api\test_export.py:5: in <module>
    from app.main import create_app
E   ModuleNotFoundError: No module named 'app'
___________ ERROR collecting tests/integration/api/test_externo.py ____________
ImportError while importing test module 'D:\PROJETOS\SISTEMAS\PROGRAMAS\omni_keywords_finder\tests\integration\api\test_externo.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Program Files\Python311\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\integration\api\test_externo.py:5: in <module>
    from app.main import create_app
E   ModuleNotFoundError: No module named 'app'
__________ ERROR collecting tests/integration/api/test_governanca.py __________
ImportError while importing test module 'D:\PROJETOS\SISTEMAS\PROGRAMAS\omni_keywords_finder\tests\integration\api\test_governanca.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Program Files\Python311\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\integration\api\test_governanca.py:5: in <module>
    from app.main import create_app
E   ModuleNotFoundError: No module named 'app'
___________ ERROR collecting tests/integration/api/test_keywords.py ___________
ImportError while importing test module 'D:\PROJETOS\SISTEMAS\PROGRAMAS\omni_keywords_finder\tests\integration\api\test_keywords.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Program Files\Python311\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\integration\api\test_keywords.py:5: in <module>
    from app.main import create_app
E   ModuleNotFoundError: No module named 'app'
=========================== short test summary info ===========================
ERROR tests/integration/api/test_dashboard_metrics.py
ERROR tests/integration/api/test_export.py
ERROR tests/integration/api/test_externo.py
ERROR tests/integration/api/test_governanca.py
ERROR tests/integration/api/test_keywords.py
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
======================== 1 warning, 5 errors in 0.38s =========================
