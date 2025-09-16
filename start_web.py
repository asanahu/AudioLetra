#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio rapido para el servidor web de dictado inteligente.
"""

import sys
from pathlib import Path

# Agregar directorios al path
sys.path.append(str(Path(__file__).parent))

try:
    from web_server import WebDictationServer

    print("Iniciando servidor web de dictado inteligente...")
    print("=" * 60)

    server = WebDictationServer()
    server.run(host='127.0.0.1', port=5000, debug=False)

except KeyboardInterrupt:
    print("\nServidor detenido por el usuario")
except Exception as e:
    print(f"Error al iniciar servidor: {e}")
    print("\nAsegurate de que todas las dependencias esten instaladas:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

