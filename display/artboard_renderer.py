"""Renderizador de artboards XD (SRP)"""
import os
import json
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk


class ArtboardRenderer:
    """Renderiza artboards XD a partir de dados JSON (Single Responsibility)"""
    
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.default_font = None
        self._try_load_font()
    
    def _try_load_font(self):
        """Tenta carregar uma fonte padrão"""
        try:
            # Tentar carregar fonte do sistema
            self.default_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            try:
                self.default_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 12)
            except:
                # Fonte padrão do PIL
                self.default_font = ImageFont.load_default()
    
    def render_artboard(self, artboard_data: Dict[str, Any], width: Optional[int] = None, height: Optional[int] = None) -> Image.Image:
        """Renderiza um artboard completo a partir de dados JSON"""
        # Obter dimensões do artboard
        artboard_width = width or artboard_data.get('width', artboard_data.get('w', 800))
        artboard_height = height or artboard_data.get('height', artboard_data.get('h', 600))
        
        # Criar imagem base
        image = Image.new('RGBA', (int(artboard_width), int(artboard_height)), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Renderizar background do artboard
        bg_color = self._parse_color(artboard_data.get('backgroundColor', artboard_data.get('bgColor', '#FFFFFF')))
        if bg_color:
            draw.rectangle([(0, 0), (artboard_width, artboard_height)], fill=bg_color)
        
        # Renderizar elementos filhos
        children = artboard_data.get('children', artboard_data.get('elements', artboard_data.get('content', [])))
        if isinstance(children, list):
            for child in children:
                self._render_element(draw, child, image)
        
        return image
    
    def _render_element(self, draw: ImageDraw.Draw, element: Dict[str, Any], canvas_image: Image.Image):
        """Renderiza um elemento individual"""
        if not isinstance(element, dict):
            return
        
        element_type = str(element.get('type', '')).lower()
        
        # Aplicar transformações (posição, rotação, escala, opacidade)
        x = element.get('x', element.get('left', 0))
        y = element.get('y', element.get('top', 0))
        width = element.get('width', element.get('w', 0))
        height = element.get('height', element.get('h', 0))
        rotation = element.get('rotation', element.get('r', 0))
        opacity = element.get('opacity', element.get('alpha', 1.0))
        
        # Renderizar baseado no tipo
        if 'rectangle' in element_type or 'rect' in element_type:
            self._render_rectangle(draw, x, y, width, height, element, opacity)
        elif 'circle' in element_type or 'ellipse' in element_type:
            self._render_circle(draw, x, y, width, height, element, opacity)
        elif 'line' in element_type or 'path' in element_type:
            self._render_line(draw, x, y, width, height, element, opacity)
        elif 'text' in element_type or 'string' in element_type:
            self._render_text(draw, x, y, width, height, element, opacity)
        elif 'image' in element_type or 'bitmap' in element_type or 'picture' in element_type:
            self._render_image(draw, x, y, width, height, element, canvas_image, opacity)
        elif 'group' in element_type or 'container' in element_type:
            # Renderizar grupo recursivamente
            children = element.get('children', element.get('elements', element.get('content', [])))
            if isinstance(children, list):
                for child in children:
                    # Ajustar posição relativa ao grupo
                    child_x = child.get('x', child.get('left', 0)) + x
                    child_y = child.get('y', child.get('top', 0)) + y
                    child_copy = child.copy()
                    child_copy['x'] = child_x
                    child_copy['y'] = child_y
                    self._render_element(draw, child_copy, canvas_image)
    
    def _render_rectangle(self, draw: ImageDraw.Draw, x: float, y: float, width: float, height: float, 
                         element: Dict[str, Any], opacity: float):
        """Renderiza um retângulo"""
        fill_color = self._parse_color(element.get('fill', element.get('color', '#000000')))
        stroke_color = self._parse_color(element.get('stroke', element.get('borderColor')))
        stroke_width = element.get('strokeWidth', element.get('borderWidth', 0))
        
        if fill_color:
            fill_color = self._apply_opacity(fill_color, opacity)
            draw.rectangle([(x, y), (x + width, y + height)], fill=fill_color)
        
        if stroke_color and stroke_width > 0:
            stroke_color = self._apply_opacity(stroke_color, opacity)
            for i in range(int(stroke_width)):
                draw.rectangle([(x + i, y + i), (x + width - i, y + height - i)], outline=stroke_color)
    
    def _render_circle(self, draw: ImageDraw.Draw, x: float, y: float, width: float, height: float,
                      element: Dict[str, Any], opacity: float):
        """Renderiza um círculo/elipse"""
        fill_color = self._parse_color(element.get('fill', element.get('color', '#000000')))
        stroke_color = self._parse_color(element.get('stroke', element.get('borderColor')))
        stroke_width = element.get('strokeWidth', element.get('borderWidth', 0))
        
        # Calcular centro e raios
        center_x = x + width / 2
        center_y = y + height / 2
        radius_x = width / 2
        radius_y = height / 2
        
        # PIL não tem elipse direta, usar aproximação com polígono
        bbox = [(x, y), (x + width, y + height)]
        
        if fill_color:
            fill_color = self._apply_opacity(fill_color, opacity)
            draw.ellipse(bbox, fill=fill_color)
        
        if stroke_color and stroke_width > 0:
            stroke_color = self._apply_opacity(stroke_color, opacity)
            draw.ellipse(bbox, outline=stroke_color, width=int(stroke_width))
    
    def _render_line(self, draw: ImageDraw.Draw, x: float, y: float, width: float, height: float,
                    element: Dict[str, Any], opacity: float):
        """Renderiza uma linha"""
        stroke_color = self._parse_color(element.get('stroke', element.get('color', '#000000')))
        stroke_width = element.get('strokeWidth', element.get('width', 1))
        
        if stroke_color:
            stroke_color = self._apply_opacity(stroke_color, opacity)
            # Se tem path, renderizar path
            path = element.get('path', element.get('d', []))
            if path and isinstance(path, list) and len(path) >= 2:
                points = [(p.get('x', 0) + x, p.get('y', 0) + y) if isinstance(p, dict) else (p[0] + x, p[1] + y) if isinstance(p, (list, tuple)) else (x, y) for p in path]
                if len(points) >= 2:
                    draw.line(points, fill=stroke_color, width=int(stroke_width))
            else:
                # Linha simples
                end_x = element.get('x2', x + width)
                end_y = element.get('y2', y + height)
                draw.line([(x, y), (end_x, end_y)], fill=stroke_color, width=int(stroke_width))
    
    def _render_text(self, draw: ImageDraw.Draw, x: float, y: float, width: float, height: float,
                    element: Dict[str, Any], opacity: float):
        """Renderiza texto"""
        text = element.get('text', element.get('content', element.get('string', '')))
        if not text:
            return
        
        text_color = self._parse_color(element.get('fill', element.get('color', '#000000')))
        font_size = element.get('fontSize', element.get('size', 12))
        
        # Tentar carregar fonte
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(font_size))
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", int(font_size))
            except:
                font = self.default_font
        
        if text_color:
            text_color = self._apply_opacity(text_color, opacity)
            # Renderizar texto (multiline se necessário)
            lines = str(text).split('\n')
            current_y = y
            for line in lines:
                draw.text((x, current_y), line, fill=text_color, font=font)
                # Aproximar altura da linha
                current_y += font_size * 1.2
    
    def _render_image(self, draw: ImageDraw.Draw, x: float, y: float, width: float, height: float,
                     element: Dict[str, Any], canvas_image: Image.Image, opacity: float):
        """Renderiza uma imagem"""
        # Procurar referência à imagem
        image_path = element.get('href', element.get('src', element.get('path', element.get('file', ''))))
        if not image_path:
            return
        
        # Tentar encontrar o arquivo de imagem
        full_path = os.path.join(self.base_directory, image_path)
        if not os.path.exists(full_path):
            # Tentar caminho relativo
            full_path = os.path.normpath(os.path.join(self.base_directory, image_path.lstrip('/')))
        
        if os.path.exists(full_path):
            try:
                img = Image.open(full_path)
                # Redimensionar se necessário
                if width > 0 and height > 0:
                    img = img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                
                # Aplicar opacidade
                if opacity < 1.0:
                    alpha = img.split()[3] if img.mode == 'RGBA' else None
                    if alpha:
                        alpha = alpha.point(lambda p: int(p * opacity))
                        img.putalpha(alpha)
                    else:
                        img = img.convert('RGBA')
                        alpha = img.split()[3]
                        alpha = alpha.point(lambda p: int(p * opacity))
                        img.putalpha(alpha)
                
                # Colar na imagem do canvas
                canvas_image.paste(img, (int(x), int(y)), img if img.mode == 'RGBA' else None)
            except Exception:
                pass  # Ignorar erros ao carregar imagem
    
    def _parse_color(self, color_value: Any) -> Optional[Tuple[int, int, int, int]]:
        """Converte valor de cor para RGBA tuple"""
        if color_value is None:
            return None
        
        if isinstance(color_value, str):
            # Hex color (#RRGGBB ou #RRGGBBAA)
            if color_value.startswith('#'):
                hex_color = color_value[1:]
                if len(hex_color) == 6:
                    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), 255)
                elif len(hex_color) == 8:
                    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), int(hex_color[6:8], 16))
            # RGB/RGBA string
            elif color_value.startswith('rgb'):
                # Simplificado - retornar preto
                return (0, 0, 0, 255)
        
        elif isinstance(color_value, dict):
            # Objeto de cor {r, g, b, a}
            r = int(color_value.get('r', color_value.get('red', 0)) * 255) if isinstance(color_value.get('r', 0), float) else color_value.get('r', 0)
            g = int(color_value.get('g', color_value.get('green', 0)) * 255) if isinstance(color_value.get('g', 0), float) else color_value.get('g', 0)
            b = int(color_value.get('b', color_value.get('blue', 0)) * 255) if isinstance(color_value.get('b', 0), float) else color_value.get('b', 0)
            a = int(color_value.get('a', color_value.get('alpha', 1.0)) * 255) if isinstance(color_value.get('a', 1.0), float) else color_value.get('a', 255)
            return (r, g, b, a)
        
        elif isinstance(color_value, (list, tuple)):
            # Lista/tupla [r, g, b] ou [r, g, b, a]
            if len(color_value) >= 3:
                r = int(color_value[0] * 255) if isinstance(color_value[0], float) else color_value[0]
                g = int(color_value[1] * 255) if isinstance(color_value[1], float) else color_value[1]
                b = int(color_value[2] * 255) if isinstance(color_value[2], float) else color_value[2]
                a = int(color_value[3] * 255) if len(color_value) > 3 and isinstance(color_value[3], float) else (color_value[3] if len(color_value) > 3 else 255)
                return (r, g, b, a)
        
        # Fallback: preto
        return (0, 0, 0, 255)
    
    def _apply_opacity(self, color: Tuple[int, int, int, int], opacity: float) -> Tuple[int, int, int, int]:
        """Aplica opacidade a uma cor"""
        if len(color) == 4:
            return (color[0], color[1], color[2], int(color[3] * opacity))
        return color + (int(255 * opacity),)

