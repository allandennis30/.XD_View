# Como Executar o Visualizador XD

## Método Rápido (Recomendado)

1. Abra o terminal
2. Navegue até a pasta do projeto:
   ```bash
   cd /mnt/8EB22BD6B22BC217/Projetos/VizualizadorXD
   ```
3. Execute o script:
   ```bash
   ./run.sh
   ```

## Método Alternativo

1. Abra o terminal
2. Navegue até a pasta do projeto:
   ```bash
   cd /mnt/8EB22BD6B22BC217/Projetos/VizualizadorXD
   ```
3. Execute com Python:
   ```bash
   python3 main.py
   ```

## Criar Atalho no Desktop (Opcional)

Para criar um atalho no desktop:

1. Crie um arquivo `VisualizadorXD.desktop` no seu desktop:
   ```bash
   nano ~/Desktop/VisualizadorXD.desktop
   ```

2. Cole o seguinte conteúdo:
   ```ini
   [Desktop Entry]
   Version=1.0
   Type=Application
   Name=Visualizador XD
   Comment=Visualizador de arquivos .xd do Adobe XD
   Exec=/mnt/8EB22BD6B22BC217/Projetos/VizualizadorXD/run.sh
   Icon=application-x-executable
   Terminal=false
   Categories=Graphics;Viewer;
   ```

3. Torne o arquivo executável:
   ```bash
   chmod +x ~/Desktop/VisualizadorXD.desktop
   ```

Agora você pode clicar duas vezes no ícone do desktop para executar o programa!

