import json
from pathlib import Path


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
        if Path("src\\config.json").exists():
            with open("src\\config.json") as f:
                dicionario = json.load(f)
            dicionario[chave] = valor
        else:
            dicionario = {chave: valor}
        js = json.dumps(dicionario)
        with open("src\\config.json", "w") as f:
            f.write(js)

    def ler(self, variavel):
        """
        Recebe variável
        Retorna o valor de dicionario[variavel]
        """
        if Path('src\\config.json').exists():
            with open('src\\config.json') as f:
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
        with open('src\\config.json') as f:
            dicionario = json.load(f)
        del dicionario[chave]
        js = json.dumps(dicionario)
        with open("src\\config.json", "w") as f:
            f.write(js)
