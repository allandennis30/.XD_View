"""Extrator de conteúdo XD (SRP + DIP)"""
import os
import zipfile
import tempfile
import shutil
from typing import List, Optional
from interfaces import IContentExtractor
from .artboard_extractor import ArtboardExtractor


class XDContentExtractor(IContentExtractor):
    """Coordena extração completa de conteúdo .xd (Single Responsibility)"""
    
    def __init__(self, artboard_extractor: ArtboardExtractor):
        self.artboard_extractor = artboard_extractor
        self.temp_dir: Optional[str] = None
    
    def extract_content(self, xd_file_path: str) -> List[str]:
        """Extrai todo o conteúdo visual do arquivo .xd"""
        self.cleanup()
        
        # Criar diretório temporário
        self.temp_dir = tempfile.mkdtemp(prefix="xd_viewer_")
        
        # Extrair arquivo .xd (ZIP)
        try:
            with zipfile.ZipFile(xd_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
        except zipfile.BadZipFile:
            raise ValueError("O arquivo não é um arquivo .xd válido")
        
        # Extrair artboards e conteúdo visual
        content_paths = self.artboard_extractor.extract_artboards(self.temp_dir)
        
        if not content_paths:
            raise ValueError("Nenhum conteúdo visual encontrado no arquivo .xd")
        
        return content_paths
    
    def get_temp_dir(self) -> Optional[str]:
        """Retorna diretório temporário atual"""
        return self.temp_dir
    
    def cleanup(self):
        """Limpa recursos temporários"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except OSError:
                pass
        self.temp_dir = None

