#!/bin/bash
# Script de instalação das dependências

echo "Instalando dependências do Visualizador XD..."
echo ""

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then 
    echo "Instalando python3-tk..."
    apt-get update
    apt-get install -y python3-tk
    echo "✓ python3-tk instalado"
else
    echo "Para instalar python3-tk, execute:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install python3-tk"
    echo ""
fi

echo "Instalando Pillow via pip..."
pip3 install Pillow
echo "✓ Pillow instalado"
echo ""
echo "Verificando instalação..."
python3 check_dependencies.py

