"""Análise de estrutura XD (SRP)"""
import os
import json
from typing import Dict, Any, List
from interfaces import IProjectParser


class XDStructureAnalyzer(IProjectParser):
    """Analisa estrutura interna de arquivos .xd (Single Responsibility)"""
    
    def parse_structure(self, directory: str) -> Dict[str, Any]:
        """Analisa estrutura do projeto .xd"""
        structure = {
            'manifest': None,
            'artboards': [],
            'artboard_jsons': [],
            'resources': [],
            'artwork_path': None,
            'resources_path': None,
            'graphics_path': None
        }
        
        # Procurar manifest.json
        manifest_path = os.path.join(directory, 'manifest.json')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    structure['manifest'] = json.load(f)
                    # Extrair informações de artboards do manifest
                    structure['artboards'] = self._extract_artboards_from_manifest(structure['manifest'])
            except (json.JSONDecodeError, IOError):
                pass
        
        # Identificar pastas principais
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                item_lower = item.lower()
                if 'artwork' in item_lower or 'artboards' in item_lower:
                    structure['artwork_path'] = item_path
                elif 'resources' in item_lower:
                    structure['resources_path'] = item_path
                elif 'graphics' in item_lower:
                    structure['graphics_path'] = item_path
        
        # Se não encontrou pastas nomeadas, procurar por estrutura comum
        if not structure['artwork_path']:
            for root, dirs, files in os.walk(directory):
                # Procurar por arquivos que indicam artboards
                for file in files:
                    if file.endswith('.json') and ('artboard' in file.lower() or 'board' in file.lower()):
                        structure['artwork_path'] = root
                        break
                if structure['artwork_path']:
                    break
        
        # Buscar arquivos JSON de artboards
        structure['artboard_jsons'] = self._find_artboard_json_files(directory, structure)
        
        return structure
    
    def _extract_artboards_from_manifest(self, manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai informações de artboards do manifest.json"""
        artboards = []
        
        if not isinstance(manifest, dict):
            return artboards
        
        # Procurar por estruturas que podem conter artboards
        def search_for_artboards(obj, path=""):
            if isinstance(obj, dict):
                # Verificar se é um artboard
                if 'type' in obj and ('artboard' in str(obj.get('type', '')).lower() or 
                                      'board' in str(obj.get('type', '')).lower()):
                    artboards.append({
                        'path': path,
                        'data': obj,
                        'name': obj.get('name', obj.get('id', 'Unknown')),
                        'width': obj.get('width', obj.get('w', 0)),
                        'height': obj.get('height', obj.get('h', 0))
                    })
                
                # Procurar em children ou elementos
                for key, value in obj.items():
                    if key in ['children', 'elements', 'artboards', 'items', 'content']:
                        if isinstance(value, list):
                            for i, item in enumerate(value):
                                search_for_artboards(item, f"{path}.{key}[{i}]")
                        elif isinstance(value, dict):
                            search_for_artboards(value, f"{path}.{key}")
                    else:
                        search_for_artboards(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_for_artboards(item, f"{path}[{i}]")
        
        search_for_artboards(manifest)
        return artboards
    
    def _find_artboard_json_files(self, directory: str, structure: Dict[str, Any]) -> List[str]:
        """Encontra arquivos JSON que podem conter dados de artboards"""
        json_files = []
        searched_paths = []
        
        # Buscar em artwork_path
        if structure['artwork_path']:
            searched_paths.append(structure['artwork_path'])
        
        # Buscar em graphics_path
        if structure['graphics_path']:
            searched_paths.append(structure['graphics_path'])
        
        # Buscar em toda a estrutura se não encontrou paths específicos
        if not searched_paths:
            searched_paths.append(directory)
        
        for search_path in searched_paths:
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.json'):
                        json_path = os.path.join(root, file)
                        # Verificar se o JSON contém dados de artboard
                        if self._is_artboard_json(json_path):
                            json_files.append(json_path)
        
        return json_files
    
    def _is_artboard_json(self, json_path: str) -> bool:
        """Verifica se um arquivo JSON contém dados de artboard"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Verificar se contém indicadores de artboard
            if isinstance(data, dict):
                # Verificar tipo
                if 'type' in data:
                    type_str = str(data['type']).lower()
                    if 'artboard' in type_str or 'board' in type_str:
                        return True
                
                # Verificar se tem propriedades de artboard (width, height, children)
                has_dimensions = ('width' in data or 'w' in data) and ('height' in data or 'h' in data)
                has_children = 'children' in data or 'elements' in data or 'content' in data
                
                if has_dimensions and has_children:
                    return True
                
                # Verificar nome do arquivo
                filename = os.path.basename(json_path).lower()
                if 'artboard' in filename or 'board' in filename:
                    return True
            
            return False
        except (json.JSONDecodeError, IOError, UnicodeDecodeError):
            return False

