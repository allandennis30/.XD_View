"""Estado de exibição (SRP)"""


class DisplayState:
    """Gerencia estado da visualização (Single Responsibility)"""
    
    def __init__(self):
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.min_scale = 0.1
        self.max_scale = 10.0
    
    def reset(self):
        """Reseta estado para valores padrão"""
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
    
    def apply_zoom(self, factor: float) -> float:
        """Aplica fator de zoom respeitando limites"""
        zoom_factor = 1.1 if factor > 0 else 0.9
        new_scale = self.scale * zoom_factor
        self.scale = max(self.min_scale, min(self.max_scale, new_scale))
        return self.scale
    
    def apply_pan(self, delta_x: int, delta_y: int):
        """Aplica movimento"""
        self.offset_x += delta_x
        self.offset_y += delta_y

