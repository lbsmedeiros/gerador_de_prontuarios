import os
from pathlib import Path
from string import ascii_uppercase
import subprocess


class ClearTempFiles:
    def limpar_arquivos_temporarios(self):
        """
        Identifica o nome do usuario
        Localiza o diretório temporário do usuário
        Limpa o diretório
        """
        user = os.getlogin()
        for unidade in ascii_uppercase:
            if Path(f'{unidade}:\\Users\\{user}\\AppData\\Local\\Temp').exists():
                del_dir = f'{unidade}:\\Users\\{user}\\AppData\\Local\\Temp'
                pObj = subprocess.Popen('del /S /Q /F %s\\*.*' % del_dir, shell=True, stdout = subprocess.PIPE, stderr= subprocess.PIPE)
                rTup = pObj.communicate()
                rCod = pObj.returncode
                break
