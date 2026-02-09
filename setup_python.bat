@echo off
echo [Lumina] Configurando o Motor Python...

cd src/Lumina.Engine

if not exist "venv" (
    echo [Lumina] Criando ambiente virtual (venv)...
    python -m venv venv
)

echo [Lumina] Instalando dependencias...
.\venv\Scripts\pip install -r requirements.txt

echo [Lumina] Configuracao do Motor Python concluida!
pause