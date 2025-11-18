# .XD_View

# Visualizador XD

Programa Python para visualização e zoom de arquivos .xd do Adobe XD.

## Requisitos

- Python 3.10 ou superior
- tkinter (interface gráfica)
- Pillow (manipulação de imagens)

## Instalação

### 1. Instalar dependências do sistema (tkinter)

No Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

No Linux (Fedora):
```bash
sudo dnf install python3-tkinter
```

No Linux (Arch):
```bash
sudo pacman -S tk
```

### 2. Instalar dependências Python

```bash
pip install -r requirements.txt
```

ou

```bash
pip install Pillow
```

## Uso

Execute o programa:

```bash
python3 main.py
```

Ou:

```bash
python main.py
```

## Funcionalidades

- Abrir arquivos .xd do Adobe XD
- Zoom in/out com scroll do mouse (sem perder qualidade)
- Arrastar imagem clicando e movendo o mouse
- Visualização de recursos visuais extraídos do arquivo .xd

