"""Handler de drag-and-drop (SRP)"""
import os
from typing import List


class DragDropHandler:
    """Responsável por gerenciar drag-and-drop (Single Responsibility)"""
    
    def __init__(self, tk_root):
        self.tk_root = tk_root
    
    def parse_dropped_files(self, event_data) -> List[str]:
        """Parse arquivos soltos no drag-and-drop"""
        if isinstance(event_data, str):
            data = event_data.strip('{}').strip()
            try:
                files = self.tk_root.tk.splitlist(data)
                return files
            except (AttributeError, Exception):
                if '}' in data:
                    return [f.strip('{}') for f in data.split('} {')]
                return [data]
        return event_data if isinstance(event_data, list) else [event_data]
    
    @staticmethod
    def validate_xd_file(file_path: str) -> bool:
        """Valida se o arquivo é .xd"""
        filename = os.path.basename(file_path)
        return filename.lower().endswith('.xd')

