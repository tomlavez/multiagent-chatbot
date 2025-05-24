#!/usr/bin/env python3
"""
Script para executar a aplicação web Streamlit
"""
import subprocess
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/web/app.py"]) 