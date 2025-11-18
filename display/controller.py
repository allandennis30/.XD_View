"""Controlador de exibição (SRP)"""
import os
from typing import Optional, Tuple, Dict, Any, Union
from PIL import Image
from .state import DisplayState
from .artboard_renderer import ArtboardRenderer


class ImageDisplayController:
    """Controla zoom, pan e interações com imagem e artboards (Single Responsibility)"""
    
    def __init__(self, display_state: DisplayState):
        self.display_state = display_state
        self.original_image: Optional[Image.Image] = None
        self.content_type: str = 'image'  # 'image' ou 'artboard'
        self.artboard_renderer: Optional[ArtboardRenderer] = None
        self.base_directory: Optional[str] = None
    
    def load_image(self, image_path: str):
        """Carrega uma nova imagem"""
        try:
            self.original_image = Image.open(image_path)
            self.content_type = 'image'
            self.display_state.reset()
        except Exception as e:
            raise ValueError(f"Erro ao carregar imagem: {str(e)}")
    
    def load_artboard(self, artboard_data: Union[Dict[str, Any], str], base_directory: str):
        """Carrega um artboard a partir de dados JSON"""
        try:
            self.base_directory = base_directory
            
            # Se artboard_data é um dicionário, usar diretamente
            if isinstance(artboard_data, dict):
                artboard_dict = artboard_data
            else:
                # Se é string (caminho), tentar carregar do arquivo
                import json
                with open(artboard_data, 'r', encoding='utf-8') as f:
                    artboard_dict = json.load(f)
            
            # Criar renderizador se necessário
            if self.artboard_renderer is None or self.artboard_renderer.base_directory != base_directory:
                self.artboard_renderer = ArtboardRenderer(base_directory)
            
            # Renderizar artboard
            width = artboard_dict.get('width', artboard_dict.get('w', 800))
            height = artboard_dict.get('height', artboard_dict.get('h', 600))
            self.original_image = self.artboard_renderer.render_artboard(artboard_dict, width, height)
            self.content_type = 'artboard'
            self.display_state.reset()
        except Exception as e:
            raise ValueError(f"Erro ao carregar artboard: {str(e)}")
    
    def load_content(self, content: Union[str, Dict[str, Any]], base_directory: Optional[str] = None):
        """Carrega conteúdo (imagem ou artboard) baseado no tipo"""
        if isinstance(content, dict):
            # É um artboard JSON
            if content.get('type') in ['artboard_json', 'artboard_manifest']:
                artboard_data = content.get('data', content)
                base_dir = base_directory or os.path.dirname(content.get('path', ''))
                self.load_artboard(artboard_data, base_dir)
            else:
                raise ValueError("Formato de conteúdo desconhecido")
        elif isinstance(content, str):
            # Verificar se é um arquivo JSON ou imagem
            if content.endswith('.json'):
                # Tentar carregar como artboard
                base_dir = base_directory or os.path.dirname(content)
                self.load_artboard(content, base_dir)
            else:
                # Carregar como imagem
                self.load_image(content)
        else:
            raise ValueError("Tipo de conteúdo não suportado")
    
    def calculate_zoom(self, event, canvas_width: int, canvas_height: int) -> Tuple[Optional[float], Optional[Tuple[int, int]]]:
        """Calcula novo zoom e offset baseado no evento do mouse"""
        if self.original_image is None:
            return None, None
        
        old_scale = self.display_state.scale
        new_scale = self.display_state.apply_zoom(event.delta)
        
        width, height = self.original_image.size
        old_width = int(width * old_scale)
        old_height = int(height * old_scale)
        
        img_x = (canvas_width - old_width) // 2 + self.display_state.offset_x
        img_y = (canvas_height - old_height) // 2 + self.display_state.offset_y
        
        mouse_x_rel = event.x - img_x
        mouse_y_rel = event.y - img_y
        
        new_width = int(width * new_scale)
        new_height = int(height * new_scale)
        new_img_x = (canvas_width - new_width) // 2 + self.display_state.offset_x
        new_img_y = (canvas_height - new_height) // 2 + self.display_state.offset_y
        
        offset_x = self.display_state.offset_x + (event.x - new_img_x) - mouse_x_rel
        offset_y = self.display_state.offset_y + (event.y - new_img_y) - mouse_y_rel
        
        return new_scale, (offset_x, offset_y)

