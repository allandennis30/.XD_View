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

### Opção 1: Script de execução (recomendado)

Na pasta do projeto, execute:

```bash
./run.sh
```

### Opção 2: Executar diretamente com Python

Na pasta do projeto, execute:

```bash
python3 main.py
```

Ou:

```bash
python main.py
```

### Opção 3: Executar de qualquer lugar

Se você estiver em outra pasta, use o caminho completo:

```bash
cd /mnt/8EB22BD6B22BC217/Projetos/VizualizadorXD
python3 main.py
```

## Funcionalidades

- **Abrir arquivos .xd**: Menu "Arquivo > Abrir arquivo .xd" ou arraste e solte o arquivo na janela
- **Drag-and-drop**: Arraste arquivos .xd diretamente para a janela de visualização
- **Zoom in/out**: Use a roda do mouse para fazer zoom (sem perder qualidade)
- **Arrastar imagem**: Clique e arraste a imagem com o mouse
- **Visualização de recursos**: Extrai e exibe recursos visuais do arquivo .xd

