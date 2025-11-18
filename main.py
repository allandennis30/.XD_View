"""Classe principal do visualizador XD"""
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from typing import List
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None
    DND_FILES = None

# Imports dos módulos
from interfaces import IContentExtractor, IDisplayRenderer
from extraction import XDStructureAnalyzer, ArtboardExtractor, XDContentExtractor
from display import DisplayState, ImageDisplayController, CanvasRenderer
from ui import SidebarManager, DragDropHandler


class XDViewer(TkinterDnD.Tk if TkinterDnD else tk.Tk):
    """Classe principal do visualizador (Orquestração com Dependency Inversion)"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Visualizador XD")
        self.geometry("1000x700")
        
        # Injeção de dependências (DIP)
        structure_analyzer = XDStructureAnalyzer()
        artboard_extractor = ArtboardExtractor(structure_analyzer)
        self.content_extractor: IContentExtractor = XDContentExtractor(artboard_extractor)
        self.drag_handler = DragDropHandler(self)
        
        # Estado de exibição
        self.display_state = DisplayState()
        self.display_controller = ImageDisplayController(self.display_state)
        
        # Estado
        self.all_content: List[str] = []
        self.selected_content_index = -1
        self.drag_data = {"x": 0, "y": 0, "active": False}
        
        # UI Components
        self.create_menu()
        self.create_layout()
        
        # Renderizador (DIP - depende de interface)
        self.renderer: IDisplayRenderer = CanvasRenderer(
            self.canvas,
            self.display_state,
            self.display_controller
        )
        
        # Sidebar
        self.sidebar_manager = SidebarManager(self.sidebar_frame, self.on_content_selected)
        
        # Setup
        self.setup_drag_and_drop()
        self.setup_canvas_events()
        
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
    
    def create_layout(self):
        """Cria o layout principal"""
        self.main_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        self.sidebar_frame = tk.Frame(self.main_paned, bg="gray15", width=280)
        self.canvas = tk.Canvas(self.main_paned, bg="gray20", cursor="hand2")
        
        self.main_paned.add(self.sidebar_frame, width=280, minsize=200)
        self.main_paned.add(self.canvas, width=720, minsize=400)
        
        self.canvas.create_text(
            500, 350,
            text="Arquivo > Abrir arquivo .xd para começar\nou arraste e solte um arquivo .xd aqui",
            fill="white",
            font=("Arial", 14),
            justify=tk.CENTER
        )
        
        if TkinterDnD is not None:
            try:
                self.sidebar_frame.drop_target_register(DND_FILES)
                self.sidebar_frame.dnd_bind('<<Drop>>', self.on_file_drop)
            except:
                pass
    
    def setup_drag_and_drop(self):
        """Configura drag-and-drop"""
        if TkinterDnD is None:
            return
        
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_file_drop)
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.on_file_drop)
    
    def setup_canvas_events(self):
        """Configura eventos do canvas"""
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<Configure>", lambda e: self.renderer.render())
    
    def on_file_drop(self, event):
        """Handler para drag-and-drop"""
        if TkinterDnD is None:
            return
        
        files = self.drag_handler.parse_dropped_files(event.data)
        if not files:
            return
        
        file_path = files[0].strip().strip('{}')
        file_path = os.path.normpath(file_path)
        
        if not self.drag_handler.validate_xd_file(file_path):
            messagebox.showwarning(
                "Arquivo inválido",
                f"Por favor, solte um arquivo .xd\nArquivo recebido: {os.path.basename(file_path)}"
            )
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{file_path}")
            return
        
        self.process_xd_file(file_path)
    
    def open_xd_file(self):
        """Abre arquivo via dialog"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo .xd",
            filetypes=[("Adobe XD", "*.xd"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.process_xd_file(file_path)
    
    def process_xd_file(self, file_path: str):
        """Processa arquivo .xd usando extrator (DIP)"""
        try:
            # Usa interface IContentExtractor (DIP)
            self.all_content = self.content_extractor.extract_content(file_path)
            self.selected_content_index = 0
            
            # Obter diretório base temporário do extrator
            base_directory = None
            if isinstance(self.content_extractor, XDContentExtractor):
                base_directory = self.content_extractor.get_temp_dir()
            
            self.sidebar_manager.update_content(self.all_content, 0)
            if self.all_content:
                # Usa interface IDisplayRenderer (DIP)
                self.renderer.load_content(self.all_content[0], base_directory)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar arquivo .xd:\n{str(e)}")
    
    def on_content_selected(self, index: int):
        """Callback quando conteúdo é selecionado no sidebar"""
        if 0 <= index < len(self.all_content):
            self.selected_content_index = index
            self.sidebar_manager.update_content(self.all_content, index)
            
            # Obter diretório base temporário do extrator
            base_directory = None
            if isinstance(self.content_extractor, XDContentExtractor):
                base_directory = self.content_extractor.get_temp_dir()
            
            self.renderer.load_content(self.all_content[index], base_directory)
    
    def on_zoom(self, event):
        """Handle zoom"""
        self.renderer.zoom(event, event.delta)
    
    def on_drag_start(self, event):
        """Inicia arrastar"""
        if self.display_controller.original_image is None:
            return
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["active"] = True
        self.canvas.config(cursor="fleur")
    
    def on_drag(self, event):
        """Arrasta conteúdo"""
        if not self.drag_data["active"] or self.display_controller.original_image is None:
            return
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        self.renderer.pan(delta_x, delta_y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def on_drag_end(self, event):
        """Finaliza arrastar"""
        self.drag_data["active"] = False
        self.canvas.config(cursor="hand2")
    
    def on_closing(self):
        """Cleanup ao fechar"""
        if isinstance(self.content_extractor, XDContentExtractor):
            self.content_extractor.cleanup()
        self.destroy()


if __name__ == "__main__":
    app = XDViewer()
    app.mainloop()
