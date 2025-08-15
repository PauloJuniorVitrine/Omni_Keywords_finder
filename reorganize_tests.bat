@echo off
echo Reorganizando estrutura de testes...
echo.

REM Tentar diferentes caminhos do Python
set PYTHON_PATHS=python.exe python3.exe py.exe

for %%p in (%PYTHON_PATHS%) do (
    %%p --version >nul 2>&1
    if not errorlevel 1 (
        echo Usando: %%p
        %%p reorganize_tests_structure.py
        goto :end
    )
)

echo Python nao encontrado. Tentando caminhos alternativos...

REM Tentar caminhos específicos
set PYTHON_SPECIFIC_PATHS="C:\Python311\python.exe" "C:\Python310\python.exe" "C:\Python39\python.exe" "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"

for %%p in (%PYTHON_SPECIFIC_PATHS%) do (
    if exist %%p (
        echo Usando: %%p
        %%p reorganize_tests_structure.py
        goto :end
    )
)

echo Erro: Python nao encontrado no sistema.
echo Por favor, instale o Python ou configure o PATH.
pause

:end
echo.
echo Reorganizacao concluida!
pause 