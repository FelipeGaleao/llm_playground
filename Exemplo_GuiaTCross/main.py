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


def inject_ga():
    # replace G-XXXXXXXXXX to your web app's ID
    analytics_js = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-TF6PYQCV15"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-TF6PYQCV15');
    </script>
    <div id="G-TF6PYQCV15"></div>
    """
    analytics_id = "G-TF6PYQCV15"

    
    # Identify html path of streamlit
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=analytics_id): # if id not found within html file
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # backup recovery
        else:
            shutil.copy(index_path, bck_index)  # save backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + analytics_js) 
        index_path.write_text(new_html) # insert analytics tag at top of head
if __name__ == "__main__":
    inject_ga()
    main()