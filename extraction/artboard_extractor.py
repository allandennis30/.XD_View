"""Extrator de artboards (SRP)"""
import os
import json
from pathlib import Path
from typing import List, Set, Any, Dict, Union
from .analyzer import XDStructureAnalyzer


class ArtboardExtractor:
    """Extrai artboards do projeto .xd (Single Responsibility)"""
    
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
    
    def __init__(self, structure_analyzer: XDStructureAnalyzer):
        self.structure_analyzer = structure_analyzer
    
    def extract_artboards(self, directory: str) -> List[Union[str, Dict[str, Any]]]:
        """Extrai todos os artboards encontrados (imagens e JSONs)"""
        structure = self.structure_analyzer.parse_structure(directory)
        content_items = []
        
        # Primeiro, adicionar artboards JSON (prioridade)
        for json_path in structure.get('artboard_jsons', []):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    artboard_data = json.load(f)
                    # Criar entrada de artboard com metadados
                    artboard_entry = {
                        'type': 'artboard_json',
                        'path': json_path,
                        'data': artboard_data,
                        'name': self._extract_artboard_name(artboard_data, json_path),
                        'width': artboard_data.get('width', artboard_data.get('w', 0)),
                        'height': artboard_data.get('height', artboard_data.get('h', 0))
                    }
                    content_items.append(artboard_entry)
            except (json.JSONDecodeError, IOError, UnicodeDecodeError):
                continue
        
        # Adicionar artboards do manifest
        for artboard_info in structure.get('artboards', []):
            if artboard_info.get('data'):
                artboard_entry = {
                    'type': 'artboard_manifest',
                    'path': artboard_info.get('path', ''),
                    'data': artboard_info.get('data'),
                    'name': artboard_info.get('name', 'Unknown'),
                    'width': artboard_info.get('width', 0),
                    'height': artboard_info.get('height', 0)
                }
                content_items.append(artboard_entry)
        
        # Buscar imagens (fallback e recursos)
        image_paths = set()
        
        # Buscar em artwork/artboards
        if structure['artwork_path']:
            image_paths.update(self._find_in_directory(structure['artwork_path']))
        
        # Buscar em resources (pode conter artboards exportados)
        if structure['resources_path']:
            image_paths.update(self._find_in_directory(structure['resources_path']))
        
        # Buscar em toda a estrutura (fallback)
        image_paths.update(self._find_in_directory(directory))
        
        # Buscar referências em JSON
        image_paths.update(self._find_in_json_files(directory, structure))
        
        # Adicionar imagens como entradas simples (strings)
        for img_path in sorted(image_paths):
            # Verificar se não é uma imagem já referenciada por um artboard JSON
            if not self._is_image_in_artboard(img_path, content_items):
                content_items.append(img_path)
        
        return content_items
    
    def _extract_artboard_name(self, artboard_data: Dict[str, Any], json_path: str) -> str:
        """Extrai nome do artboard dos dados JSON"""
        if isinstance(artboard_data, dict):
            # Tentar vários campos possíveis
            name = (artboard_data.get('name') or 
                   artboard_data.get('id') or 
                   artboard_data.get('title') or
                   artboard_data.get('label'))
            if name:
                return str(name)
        
        # Fallback: usar nome do arquivo
        filename = os.path.basename(json_path)
        return os.path.splitext(filename)[0]
    
    def _is_image_in_artboard(self, image_path: str, content_items: List[Union[str, Dict[str, Any]]]) -> bool:
        """Verifica se uma imagem já está referenciada em um artboard JSON"""
        image_name = os.path.basename(image_path)
        for item in content_items:
            if isinstance(item, dict) and item.get('type') in ['artboard_json', 'artboard_manifest']:
                # Verificar se a imagem está referenciada nos dados do artboard
                data = item.get('data', {})
                if self._image_referenced_in_data(data, image_name, image_path):
                    return True
        return False
    
    def _image_referenced_in_data(self, data: Any, image_name: str, image_path: str) -> bool:
        """Verifica recursivamente se uma imagem está referenciada nos dados"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    if image_name in value or image_path in value:
                        return True
                elif isinstance(value, (dict, list)):
                    if self._image_referenced_in_data(value, image_name, image_path):
                        return True
        elif isinstance(data, list):
            for item in data:
                if self._image_referenced_in_data(item, image_name, image_path):
                    return True
        return False
    
    def _find_in_directory(self, directory: str) -> Set[str]:
        """Encontra imagens em um diretório"""
        image_paths = set()
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = Path(file)
                if file_path.suffix.lower() in self.IMAGE_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    normalized_path = os.path.normpath(full_path)
                    image_paths.add(normalized_path)
        
        return image_paths
    
    def _find_in_json_files(self, directory: str, structure: Dict) -> Set[str]:
        """Encontra referências a imagens em arquivos JSON"""
        image_paths = set()
        
        # Buscar em todos os JSONs
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    json_path = os.path.join(root, file)
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            found_paths = self._extract_paths_from_json(data, directory)
                            normalized_paths = {os.path.normpath(p) for p in found_paths if os.path.exists(p)}
                            image_paths.update(normalized_paths)
                    except (json.JSONDecodeError, IOError, UnicodeDecodeError):
                        continue
        
        return image_paths
    
    def _extract_paths_from_json(self, data: Any, base_dir: str) -> List[str]:
        """Extrai caminhos de imagens de estruturas JSON recursivamente"""
        image_paths = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Verificar se é caminho de imagem
                    if any(value.lower().endswith(ext) for ext in self.IMAGE_EXTENSIONS):
                        full_path = os.path.join(base_dir, value)
                        if os.path.exists(full_path):
                            image_paths.append(full_path)
                    # Verificar se é referência relativa
                    elif '/' in value or '\\' in value:
                        # Tentar construir caminho
                        possible_path = os.path.join(base_dir, value)
                        if os.path.exists(possible_path):
                            image_paths.append(possible_path)
                else:
                    image_paths.extend(self._extract_paths_from_json(value, base_dir))
        elif isinstance(data, list):
            for item in data:
                image_paths.extend(self._extract_paths_from_json(item, base_dir))
        
        return image_paths

