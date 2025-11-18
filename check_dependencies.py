#!/usr/bin/env python3
"""
Script para verificar se todas as dependências estão instaladas
"""

import sys

def check_tkinter():
    """Verifica se tkinter está disponível"""
    try:
        import tkinter
        print("✓ tkinter está instalado")
        return True
    except ImportError:
        print("✗ tkinter NÃO está instalado")
        print("  No Linux, instale com: sudo apt-get install python3-tk")
        return False

def check_pillow():
    """Verifica se Pillow está instalado"""
    try:
        from PIL import Image
        print("✓ Pillow está instalado")
        # Tentar ImageTk apenas se tkinter estiver disponível
        try:
            from PIL import ImageTk
            print("  (ImageTk também disponível)")
        except ImportError:
            pass
        return True
    except ImportError:
        print("✗ Pillow NÃO está instalado")
        print("  Instale com: pip install Pillow")
        return False

def main():
    print("Verificando dependências...\n")
    
    tkinter_ok = check_tkinter()
    pillow_ok = check_pillow()
    
    print()
    if tkinter_ok and pillow_ok:
        print("✓ Todas as dependências estão instaladas!")
        print("  Você pode executar: python3 main.py")
        return 0
    else:
        print("✗ Algumas dependências estão faltando.")
        print("  Consulte o README.md para instruções de instalação.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

