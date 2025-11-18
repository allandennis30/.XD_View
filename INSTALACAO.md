# Instruções de Instalação

## Problema Identificado

O programa não consegue abrir porque o **tkinter** não está instalado no sistema.

## Solução

Execute os seguintes comandos para instalar as dependências:

### 1. Instalar tkinter (requer sudo)

```bash
sudo apt-get update
sudo apt-get install python3-tk
```

### 2. Verificar instalação

```bash
python3 check_dependencies.py
```

### 3. Executar o programa

```bash
python3 main.py
```

## Status Atual

- ✓ Pillow: **Instalado**
- ✗ tkinter: **Precisa instalação** (execute o comando acima)

## Alternativa: Script de Instalação

Você também pode executar:

```bash
./install.sh
```

Mas ainda precisará executar manualmente o comando `sudo apt-get install python3-tk` se não tiver permissões de root.

