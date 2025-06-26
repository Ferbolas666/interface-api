@echo off
setlocal

REM Caminho para o arquivo original
set INPUT=dump_local.sql

REM Caminho para o novo arquivo convertido
set OUTPUT=dump_utf8.sql

REM Nome do banco de dados local
set DATABASE=bd_sup

REM Nome do usuário PostgreSQL
set USER=postgres

REM Converte UTF-16 para UTF-8 usando PowerShell
powershell -Command "Get-Content '%INPUT%' | Set-Content -Encoding UTF8 '%OUTPUT%'"

REM Importa para o PostgreSQL
echo Importando para o banco %DATABASE%...
psql -U %USER% -d %DATABASE% -f %OUTPUT%

pause