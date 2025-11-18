"""Interfaces abstratas para o visualizador XD (DIP + ISP)"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Optional


class IContentExtractor(ABC):
    """Interface para extração de conteúdo de arquivos .xd"""
    
    @abstractmethod
    def extract_content(self, xd_file_path: str) -> List[Union[str, Dict[str, Any]]]:
        """Extrai conteúdo visual do arquivo .xd (imagens e artboards JSON)"""
        pass


class IDisplayRenderer(ABC):
    """Interface para renderização de conteúdo visual"""
    
    @abstractmethod
    def load_content(self, content: Union[str, Dict[str, Any]], base_directory: Optional[str] = None):
        """Carrega conteúdo para visualização (imagem ou artboard JSON)"""
        pass
    
    @abstractmethod
    def render(self):
        """Renderiza o conteúdo carregado"""
        pass
    
    @abstractmethod
    def zoom(self, event, factor: float):
        """Aplica zoom no conteúdo"""
        pass
    
    @abstractmethod
    def pan(self, delta_x: int, delta_y: int):
        """Move o conteúdo"""
        pass


class IProjectParser(ABC):
    """Interface para parsing de estrutura de projetos"""
    
    @abstractmethod
    def parse_structure(self, directory: str) -> Dict[str, Any]:
        """Analisa estrutura do projeto"""
        pass

