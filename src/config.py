import json
from pathlib import Path
import sys


class ArquivoConfigNaoEncontrado(Exception):
    ...

class VariavelConfigNaoEncontrada(Exception):
    ...


class JsonFile:
    def criar_ou_atualizar(self, chave, valor):
        """
        Recebe chave e valor
        Lê arquivo json
        Atribui valor à chave
        """
        caminho_json = Path(r"C:\Users\lbsme\Documents\GitHub\prontuario_medico\src\config.json")
        # caminho_executavel = Path(sys.executable).parent
        # caminho_json = caminho_executavel / "config.json"
        if caminho_json.exists():
            with open(caminho_json) as f:
                dicionario = json.load(f)
            dicionario[chave] = valor
        else:
            dicionario = {chave: valor}
        js = json.dumps(dicionario)
        with open(caminho_json, "w") as f:
            f.write(js)

    def ler(self, variavel):
        """
        Recebe variável
        Retorna o valor de dicionario[variavel]
        """
        caminho_json = Path(r"C:\Users\lbsme\Documents\GitHub\prontuario_medico\src\config.json")
        # caminho_executavel = Path(sys.executable).parent
        # caminho_json = caminho_executavel / "config.json"
        if caminho_json.exists():
            with open(caminho_json) as f:
                dicionario = json.load(f)
            if variavel in dicionario:
                return dicionario[variavel]
            else:
                raise VariavelConfigNaoEncontrada()
        else:
            raise ArquivoConfigNaoEncontrado()

    def deletar(self, chave):
        """
        Recebe a chave do dicionario
        Exclui do dicionario o conteúdo daquela chave
        """
        caminho_json = Path(r"C:\Users\lbsme\Documents\GitHub\prontuario_medico\src\config.json")
        # caminho_executavel = Path(sys.executable).parent
        # caminho_json = caminho_executavel / "config.json"
        with open(caminho_json) as f:
            dicionario = json.load(f)
        del dicionario[chave]
        js = json.dumps(dicionario)
        with open(caminho_json, "w") as f:
            f.write(js)
