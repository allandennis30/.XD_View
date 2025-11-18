import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import zipfile
import json
import os
import tempfile
import shutil
from pathlib import Path
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    # Fallback se tkinterdnd2 não estiver disponível
    TkinterDnD = None
    DND_FILES = None


class XDViewer(TkinterDnD.Tk if TkinterDnD else tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Visualizador XD")
        self.geometry("1000x700")
        
        # Variáveis de estado
        self.original_image = None
        self.display_image = None
        self.photo = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_data = {"x": 0, "y": 0, "active": False}
        self.temp_dir = None
        self.current_image_path = None
        
        # Criar interface
        self.create_menu()
        self.create_canvas()
        
        # Configurar drag-and-drop
        self.setup_drag_and_drop()
        
        # Bind events
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Cleanup ao fechar
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
        """Cria o menu da aplicação"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir arquivo .xd", command=self.open_xd_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_closing)
    
    def create_canvas(self):
        """Cria o canvas para exibição"""
        self.canvas = tk.Canvas(self, bg="gray20", cursor="hand2")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mensagem inicial
        self.canvas.create_text(
            self.winfo_width() // 2 if self.winfo_width() > 1 else 500,
            self.winfo_height() // 2 if self.winfo_height() > 1 else 350,
            text="Arquivo > Abrir arquivo .xd para começar\nou arraste e solte um arquivo .xd aqui",
            fill="white",
            font=("Arial", 14),
            justify=tk.CENTER
        )
    
    def setup_drag_and_drop(self):
        """Configura drag-and-drop para a janela e canvas"""
        if TkinterDnD is None:
            return  # Drag-and-drop não disponível
        
        # Tornar a janela um drop target
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_file_drop)
        
        # Tornar o canvas um drop target também
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.on_file_drop)
    
    def on_file_drop(self, event):
        """Handler para quando um arquivo é solto"""
        if TkinterDnD is None:
            return
        
        # Obter lista de arquivos soltos
        # event.data pode ser uma string ou uma lista
        data = event.data
        
        # Se for string, processar
        if isinstance(data, str):
            # Remover chaves {} se presentes (formato do tkinterdnd2)
            data = data.strip('{}')
            # Usar splitlist do tkinter para lidar com espaços em nomes de arquivo
            try:
                files = self.tk.splitlist(data)
            except:
                # Fallback: dividir por espaço (pode quebrar com espaços no nome)
                files = data.split()
        else:
            files = data if isinstance(data, list) else [data]
        
        if not files:
            return
        
        # Pegar o primeiro arquivo
        file_path = files[0]
        
        # Verificar se é um arquivo .xd
        if not file_path.lower().endswith('.xd'):
            messagebox.showwarning(
                "Arquivo inválido",
                "Por favor, solte um arquivo .xd"
            )
            return
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            messagebox.showerror(
                "Erro",
                f"Arquivo não encontrado:\n{file_path}"
            )
            return
        
        # Processar o arquivo
        try:
            self.process_xd_file(file_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar arquivo .xd:\n{str(e)}")
    
    def open_xd_file(self):
        """Abre e processa arquivo .xd"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo .xd",
            filetypes=[("Adobe XD", "*.xd"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.process_xd_file(file_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar arquivo .xd:\n{str(e)}")
    
    def process_xd_file(self, file_path):
        """Extrai e processa o arquivo .xd"""
        # Limpar diretório temporário anterior se existir
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Criar diretório temporário
        self.temp_dir = tempfile.mkdtemp(prefix="xd_viewer_")
        
        # Extrair arquivo .xd (é um ZIP)
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
        except zipfile.BadZipFile:
            raise Exception("O arquivo não é um arquivo .xd válido")
        
        # Procurar por imagens e recursos visuais
        image_paths = self.find_images(self.temp_dir)
        
        if not image_paths:
            # Tentar encontrar artboards ou outros recursos
            image_paths = self.find_resources(self.temp_dir)
        
        if not image_paths:
            raise Exception("Nenhuma imagem ou recurso visual encontrado no arquivo .xd")
        
        # Carregar a primeira imagem encontrada
        # Se houver múltiplas, podemos melhorar isso depois
        self.current_image_path = image_paths[0]
        self.load_image(self.current_image_path)
    
    def find_images(self, directory):
        """Encontra imagens (PNG, JPG, etc.) no diretório"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        image_paths = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    image_paths.append(os.path.join(root, file))
        
        return sorted(image_paths)
    
    def find_resources(self, directory):
        """Tenta encontrar recursos analisando JSON"""
        image_paths = []
        
        # Procurar por arquivos JSON que podem conter referências a recursos
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    json_path = os.path.join(root, file)
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Procurar por caminhos de imagens no JSON
                            image_paths.extend(self.extract_image_paths_from_json(data, directory))
                    except:
                        pass
        
        return list(set(image_paths))  # Remover duplicatas
    
    def extract_image_paths_from_json(self, data, base_dir):
        """Extrai caminhos de imagens de estruturas JSON"""
        image_paths = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Verificar se é um caminho de imagem
                    if any(value.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                        full_path = os.path.join(base_dir, value)
                        if os.path.exists(full_path):
                            image_paths.append(full_path)
                else:
                    image_paths.extend(self.extract_image_paths_from_json(value, base_dir))
        elif isinstance(data, list):
            for item in data:
                image_paths.extend(self.extract_image_paths_from_json(item, base_dir))
        
        return image_paths
    
    def load_image(self, image_path):
        """Carrega imagem e atualiza exibição"""
        try:
            self.original_image = Image.open(image_path)
            self.scale = 1.0
            self.offset_x = 0
            self.offset_y = 0
            self.update_display()
        except Exception as e:
            raise Exception(f"Erro ao carregar imagem: {str(e)}")
    
    def update_display(self):
        """Atualiza a exibição da imagem no canvas"""
        if self.original_image is None:
            return
        
        # Calcular novo tamanho
        width, height = self.original_image.size
        new_width = int(width * self.scale)
        new_height = int(height * self.scale)
        
        # Redimensionar mantendo qualidade
        self.display_image = self.original_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
        
        # Converter para PhotoImage
        self.photo = ImageTk.PhotoImage(self.display_image)
        
        # Limpar canvas e desenhar imagem
        self.canvas.delete("all")
        
        # Calcular posição centralizada se necessário
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 1000
            canvas_height = 700
        
        # Posição inicial (centralizada) + offset
        x = (canvas_width - new_width) // 2 + self.offset_x
        y = (canvas_height - new_height) // 2 + self.offset_y
        
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
    
    def on_zoom(self, event):
        """Handle zoom com scroll do mouse"""
        if self.original_image is None:
            return
        
        # Fator de zoom
        zoom_factor = 1.1 if event.delta > 0 else 0.9
        
        # Limitar zoom
        min_scale = 0.1
        max_scale = 10.0
        
        new_scale = self.scale * zoom_factor
        if new_scale < min_scale:
            new_scale = min_scale
        elif new_scale > max_scale:
            new_scale = max_scale
        
        # Calcular posição do mouse relativa à imagem
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 1000
            canvas_height = 700
        
        # Posição atual da imagem
        width, height = self.original_image.size
        old_width = int(width * self.scale)
        old_height = int(height * self.scale)
        
        img_x = (canvas_width - old_width) // 2 + self.offset_x
        img_y = (canvas_height - old_height) // 2 + self.offset_y
        
        # Posição do mouse relativa à imagem
        mouse_x_rel = event.x - img_x
        mouse_y_rel = event.y - img_y
        
        # Aplicar novo zoom
        self.scale = new_scale
        
        # Ajustar offset para manter o ponto sob o mouse fixo
        new_width = int(width * self.scale)
        new_height = int(height * self.scale)
        
        new_img_x = (canvas_width - new_width) // 2 + self.offset_x
        new_img_y = (canvas_height - new_height) // 2 + self.offset_y
        
        # Calcular novo offset
        self.offset_x += (event.x - new_img_x) - mouse_x_rel
        self.offset_y += (event.y - new_img_y) - mouse_y_rel
        
        self.update_display()
    
    def on_drag_start(self, event):
        """Inicia arrastar"""
        if self.original_image is None:
            return
        
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["active"] = True
        self.canvas.config(cursor="fleur")
    
    def on_drag(self, event):
        """Arrasta a imagem"""
        if not self.drag_data["active"] or self.original_image is None:
            return
        
        # Calcular delta
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        
        # Atualizar offset
        self.offset_x += delta_x
        self.offset_y += delta_y
        
        # Atualizar posição de referência
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        self.update_display()
    
    def on_drag_end(self, event):
        """Finaliza arrastar"""
        self.drag_data["active"] = False
        self.canvas.config(cursor="hand2")
    
    def on_canvas_resize(self, event):
        """Atualiza display quando canvas é redimensionado"""
        if self.original_image is not None:
            self.update_display()
    
    def on_closing(self):
        """Limpa recursos ao fechar"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
        self.destroy()


if __name__ == "__main__":
    app = XDViewer()
    app.mainloop()

