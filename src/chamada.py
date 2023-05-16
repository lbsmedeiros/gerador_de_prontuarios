from pathlib import Path

from src.config import ArquivoConfigNaoEncontrado, JsonFile, VariavelConfigNaoEncontrada


class Chamada:
    def inserir_nova_chamada(self, paciente):
        """
        Recebe nome do paciente
        Coleta local da lista de chamadas do config.json
        Coleta local de atendimento do config.json
        Inclui nome do paciente e local de chamada no topo da lista
        """
        jf = JsonFile()
        file = jf.ler('lista_de_chamada')
        destino = jf.ler('setor_atual')
        if Path(file).exists():
            with open(file, 'r') as f:
                content = f.read()
            with open(file, 'w') as f:
                f.write(f"{paciente}-{destino}\n{content}")
        else:
            with open(file, 'w') as f:
                f.write(paciente+'-'+destino)

    def excluir_chamada_mais_antiga(self):
        """
        Coleta local da lista de chamadas do config.json
        Verifica se existe mais de 6 linhas
        Se sim, elimina a útltima
        """
        jf = JsonFile()
        file = jf.ler('lista_de_chamada')
        with open(file, 'r') as f:
            content = f.read()
        if content.count('\n') > 5:
            referencia = content.rindex('\n')
            with open(file, 'w') as f:
                f.write(content[:referencia])

    def nova_chamada(self, paciente):
        self.inserir_nova_chamada(paciente)
        self.excluir_chamada_mais_antiga()

    def coletar_nomes_e_destinos(self):
        """
        Coleta local da lista de chamadas do config.json
        Coleta o conteúdo do arquivo
        Separa o conteúdo por linhas
        Se para cada linha por informação
        retorna lista de listas
        """
        jf = JsonFile()
        try:
            file = jf.ler('lista_de_chamada')
            if Path(file).exists():
                with open(file, 'r') as f:
                    content = f.read()

                temp_list1 = content.split('\n')
                temp_list2 = []
                for item in temp_list1:
                    temp_list2.append(item.split('-'))

                return temp_list2
            else:
                return []
        except (VariavelConfigNaoEncontrada, ArquivoConfigNaoEncontrado):
            return []
