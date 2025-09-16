#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuración para actualizar rutas después de reorganización.
"""

import os
import shutil
from pathlib import Path

def update_paths():
    """Actualiza las rutas en los archivos de configuración."""
    
    # Crear directorios necesarios si no existen
    directories = [
        'data/audio',
        'data/transcriptions', 
        'data/models',
        'logs',
        'output'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado/verificado: {directory}")
    
    # Mover archivos de output existentes si los hay
    if Path('output').exists():
        output_files = list(Path('output').glob('*'))
        if output_files:
            for file in output_files:
                if file.is_file() and file.suffix in ['.txt', '.wav']:
                    if file.suffix == '.txt':
                        shutil.move(str(file), f"data/transcriptions/{file.name}")
                        print(f"📄 Movido: {file.name} -> data/transcriptions/")
                    elif file.suffix == '.wav':
                        shutil.move(str(file), f"data/audio/{file.name}")
                        print(f"🎵 Movido: {file.name} -> data/audio/")
    
    print("\n🎉 Reorganización completada!")
    print("\n📁 Nueva estructura:")
    print("├── config/          # Configuraciones")
    print("├── data/            # Datos del proyecto")
    print("│   ├── audio/       # Archivos de audio")
    print("│   ├── transcriptions/ # Transcripciones")
    print("│   └── models/      # Modelos de IA")
    print("├── docs/            # Documentación")
    print("├── scripts/         # Scripts auxiliares")
    print("├── tests/           # Pruebas")
    print("├── utils/           # Utilidades")
    print("├── web/             # Interfaz web")
    print("├── logs/            # Archivos de log")
    print("└── output/          # Salida temporal")

if __name__ == "__main__":
    update_paths()
