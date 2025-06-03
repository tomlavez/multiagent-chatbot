#!/usr/bin/env python3
"""
Script to run the Streamlit web application
"""
import subprocess
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/web/app.py"]) 