"""Gerenciador de sidebar (SRP)"""
import tkinter as tk
import os
from typing import List, Optional, Union, Dict, Any
from PIL import Image, ImageTk


class SidebarManager:
    """Responsável por gerenciar o painel lateral (Single Responsibility)"""
    
    def __init__(self, parent_frame: tk.Frame, on_content_selected):
        self.parent_frame = parent_frame
        self.on_content_selected = on_content_selected
        self.scrollable_frame: Optional[tk.Frame] = None
        self.sidebar_canvas: Optional[tk.Canvas] = None
        self.selected_index = -1
        self.items = []
        self._create_ui()
    
    def _create_ui(self):
        """Cria a interface do sidebar"""
        title_label = tk.Label(
            self.parent_frame,
            text="Projetos",
            bg="gray15",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10
        )
        title_label.pack(fill=tk.X)
        
        scroll_frame = tk.Frame(self.parent_frame, bg="gray15")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.sidebar_canvas = tk.Canvas(scroll_frame, bg="gray15", highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=self.sidebar_canvas.yview)
        self.scrollable_frame = tk.Frame(self.sidebar_canvas, bg="gray15")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))
        )
        
        self.sidebar_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.sidebar_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar_canvas.bind("<MouseWheel>", self._on_scroll)
        
        self._show_empty_message()
    
    def _on_scroll(self, event):
        """Handle scroll no painel lateral"""
        self.sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _show_empty_message(self):
        """Mostra mensagem quando não há conteúdo"""
        label = tk.Label(
            self.scrollable_frame,
            text="Nenhum projeto carregado",
            bg="gray15",
            fg="gray60",
            font=("Arial", 10),
            pady=20
        )
        label.pack()
    
    def update_content(self, content_items: List[Union[str, Dict[str, Any]]], selected_index: int = 0):
        """Atualiza a lista de conteúdo no sidebar"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.items = []
        
        if not content_items:
            self._show_empty_message()
            return
        
        self.selected_index = selected_index
        
        for idx, content_item in enumerate(content_items):
            self._create_item(idx, content_item)
    
    def _create_item(self, index: int, content_item: Union[str, Dict[str, Any]]):
        """Cria um item no sidebar"""
        is_selected = index == self.selected_index
        item_frame = tk.Frame(
            self.scrollable_frame,
            bg="gray20" if is_selected else "gray15",
            relief=tk.RAISED,
            borderwidth=1
        )
        item_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Determinar nome e tipo do conteúdo
        if isinstance(content_item, dict):
            # É um artboard JSON
            content_name = content_item.get('name', 'Artboard')
            content_type = 'artboard'
            content_path = content_item.get('path', '')
        else:
            # É uma imagem
            content_name = os.path.basename(content_item)
            content_type = 'image'
            content_path = content_item
        
        # Truncar nome se muito longo
        if len(content_name) > 25:
            content_name = content_name[:22] + "..."
        
        try:
            # Tentar carregar thumbnail
            if isinstance(content_item, dict):
                # Para artboards, criar uma imagem placeholder ou tentar renderizar
                # Por enquanto, usar um placeholder
                img = Image.new('RGB', (150, 150), color=(50, 50, 50))
                # Adicionar texto indicando que é um artboard
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                except:
                    font = ImageFont.load_default()
                draw.text((10, 60), "ARTBOARD", fill=(200, 200, 200), font=font)
                draw.text((10, 80), content_name[:15], fill=(150, 150, 150), font=font)
            else:
                img = Image.open(content_item)
            
            img.thumbnail((150, 150), Image.Resampling.LANCZOS)
            thumbnail = ImageTk.PhotoImage(img)
            
            thumb_label = tk.Label(
                item_frame,
                image=thumbnail,
                bg=item_frame.cget("bg"),
                cursor="hand2"
            )
            thumb_label.image = thumbnail
            thumb_label.pack(pady=5)
            
            # Adicionar indicador de tipo
            type_label = tk.Label(
                item_frame,
                text="[Artboard]" if content_type == 'artboard' else "[Imagem]",
                bg=item_frame.cget("bg"),
                fg="cyan" if content_type == 'artboard' else "yellow",
                font=("Arial", 7),
                cursor="hand2"
            )
            type_label.pack()
            
            name_label = tk.Label(
                item_frame,
                text=content_name,
                bg=item_frame.cget("bg"),
                fg="white",
                font=("Arial", 9),
                cursor="hand2",
                wraplength=250
            )
            name_label.pack(pady=(0, 5))
            
            def on_click(event, idx=index):
                self.on_content_selected(idx)
            
            for widget in [item_frame, thumb_label, type_label, name_label]:
                widget.bind("<Button-1>", on_click)
                if not is_selected:
                    widget.bind("<Enter>", lambda e, f=item_frame: self._on_enter(e, f))
                    widget.bind("<Leave>", lambda e, f=item_frame: self._on_leave(e, f))
        
        except Exception as e:
            error_label = tk.Label(
                item_frame,
                text=f"Erro: {content_name}",
                bg=item_frame.cget("bg"),
                fg="red",
                font=("Arial", 9),
                cursor="hand2"
            )
            error_label.pack(pady=5)
            error_label.bind("<Button-1>", lambda e, idx=index: self.on_content_selected(idx))
        
        self.items.append(item_frame)
    
    def _on_enter(self, event, frame: tk.Frame):
        """Hover effect - entrar"""
        frame.config(bg="gray25")
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg="gray25")
    
    def _on_leave(self, event, frame: tk.Frame):
        """Hover effect - sair"""
        frame.config(bg="gray15")
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg="gray15")

