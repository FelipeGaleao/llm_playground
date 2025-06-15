"""
Ponto de entrada principal para o Guia VW T-Cross
Seguindo princípios de Clean Architecture
"""
import sys
import os
import subprocess
import pathlib
import shutil
import logging
from bs4 import BeautifulSoup
import streamlit as st



def main():
    """Função principal que executa a aplicação Streamlit"""
    print("🚗 Iniciando Guia VW T-Cross...")
    
    # Caminho para o arquivo Streamlit
    current_dir = Path(__file__).parent
    streamlit_file = current_dir / 'ui' / 'streamlit.py'
    
    # Adiciona o diretório atual ao PYTHONPATH
    env = os.environ.copy()
    pythonpath = str(current_dir) + os.pathsep + env.get('PYTHONPATH', '')
    env['PYTHONPATH'] = pythonpath
    
    try:
        print(f"📁 Executando: {streamlit_file}")
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', str(streamlit_file)
        ], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar Streamlit: {e}")
        print("💡 Certifique-se de que o Streamlit está instalado:")
        print("   pip install streamlit")
    except FileNotFoundError:
        print("❌ Streamlit não encontrado!")
        print("💡 Instale com: pip install streamlit")
    except KeyboardInterrupt:
        print("\n🛑 Aplicação interrompida pelo usuário")

if __name__ == "__main__":
    main()