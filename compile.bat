@echo off
echo Compilando modulo C...
set PATH=C:\Users\joao.guimaraes\Desktop\msys2\ucrt64\bin;%PATH%
gcc main.c -o academic_module.exe -lsqlite3
if %ERRORLEVEL% EQU 0 (
    echo Compilacao bem-sucedida! Executavel criado: academic_module.exe
) else (
    echo ERRO: Falha na compilacao. Certifique-se de ter o GCC e SQLite3 instalados.
    echo.
    echo Para instalar no Windows:
    echo 1. Instale MinGW-w64 com GCC
    echo 2. Baixe SQLite3 DLL e arquivo de desenvolvimento
    echo.
)
pause
