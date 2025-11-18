"""Renderizador (SRP + ISP)"""
import tkinter as tk
import os
from typing import Optional, Union, Dict, Any
from PIL import Image, ImageTk
from interfaces import IDisplayRenderer
from .state import DisplayState
from .controller import ImageDisplayController


class CanvasRenderer(IDisplayRenderer):
    """Renderiza conteúdo em Canvas tkinter (Single Responsibility)"""
    
    def __init__(self, canvas: tk.Canvas, display_state: DisplayState, controller: ImageDisplayController):
        self.canvas = canvas
        self.display_state = display_state
        self.controller = controller
        self.display_image: Optional[Image.Image] = None
        self.photo: Optional[ImageTk.PhotoImage] = None
        self.base_directory: Optional[str] = None
    
    def load_content(self, content: Union[str, Dict[str, Any]], base_directory: Optional[str] = None):
        """Carrega conteúdo para visualização (imagem ou artboard)"""
        self.base_directory = base_directory
        self.controller.load_content(content, base_directory)
        self.render()
    
    def render(self):
        """Renderiza o conteúdo carregado no canvas"""
        if self.controller.original_image is None:
            return
        
        width, height = self.controller.original_image.size
        new_width = int(width * self.display_state.scale)
        new_height = int(height * self.display_state.scale)
        
        self.display_image = self.controller.original_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
        
        self.photo = ImageTk.PhotoImage(self.display_image)
        self.canvas.delete("all")
        
        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)
        
        x = (canvas_width - new_width) // 2 + self.display_state.offset_x
        y = (canvas_height - new_height) // 2 + self.display_state.offset_y
        
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
    
    def zoom(self, event, factor: float):
        """Aplica zoom no conteúdo"""
        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)
        
        result = self.controller.calculate_zoom(event, canvas_width, canvas_height)
        if result[0] is not None:
            new_scale, (offset_x, offset_y) = result
            self.display_state.scale = new_scale
            self.display_state.offset_x = offset_x
            self.display_state.offset_y = offset_y
            self.render()
    
    def pan(self, delta_x: int, delta_y: int):
        """Move o conteúdo"""
        self.display_state.apply_pan(delta_x, delta_y)
        self.render()

