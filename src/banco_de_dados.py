import sqlite3

from src.config import JsonFile


class DbSetores:

    def inserir(self, setor):
        """
        Cria a tabela se ela ainda não existir
        Insere na tabela os valores recebidos no dicionario
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_setores'))
        cur = con.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS setores (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, setor TEXT UNIQUE)")
        con.commit()

        try:
            cur.execute("INSERT INTO setores (setor) VALUES (?)", (setor, ))
            con.commit()
        except sqlite3.IntegrityError:
            pass

        con.close()

    def coletar_um(self, setor):
        """
        Receber setor
        Coleta informações de uma entrada do db
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_setores'))
        cur = con.cursor()

        try:
            res = cur.execute('SELECT * FROM setores WHERE setor=?', (setor,)).fetchall()
        except sqlite3.OperationalError:
            res = None

        con.close()

        if res:
            return res[0]
        else:
            return None

    def coletar_varios(self, setor=None):
        """
        Pode receber setor
        Coleta informações de todas as entradas do db
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_setores'))
        cur = con.cursor()

        try:
            if setor:
                res = cur.execute('SELECT * FROM setores WHERE setor=?', (setor,)).fetchall()
            else:
                res = cur.execute(f"SELECT * FROM setores").fetchall()
        except sqlite3.OperationalError:
            res = None

        con.close()

        if res:
            return res
        else:
            return None

    def atualizar(self, indice, novo_valor):
        """
        Recebe indice e novo valor
        Atualiza informações do db
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_setores'))
        cur = con.cursor()

        cur.execute(f"UPDATE setores SET setor=? WHERE id=?", (novo_valor, indice))

        con.commit()
        con.close()

    def excluir(self, setor):
        """
        Recebe setor
        Exclui setor do dicionario
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_setores'))
        cur = con.cursor()

        cur.execute("DELETE FROM setores WHERE setor=?", (setor,))

        con.commit()
        con.close()


class DbProntuarios:

    def inserir(self, dicionario):
        """
        Cria a tabela se ela ainda não existir
        Insere na tabela os valores recebidos no dicionario
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_prontuarios'))
        cur = con.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS prontuarios (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, cpf TEXT, nome TEXT, telefone TEXT, nascimento TEXT, sexo TEXT, peso TEXT, sintomas TEXT, emergencia TEXT, observacoes TEXT, exames TEXT, diagnostico TEXT, receituario TEXT, prontuario_ativo TEXT, created_at TEXT, updated_at TEXT)")
        con.commit()

        cur.execute("INSERT INTO prontuarios (cpf, nome, telefone, nascimento, sexo, peso, sintomas, emergencia, observacoes, exames, diagnostico, receituario, prontuario_ativo, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                dicionario['cpf'],
                dicionario['nome'],
                dicionario['telefone'],
                dicionario['nascimento'],
                dicionario['sexo'],
                dicionario['peso'],
                dicionario['sintomas'],
                dicionario['emergencia'],
                dicionario['observacoes'],
                dicionario['exames'],
                dicionario['diagnostico'],
                dicionario['receituario'],
                dicionario['prontuario_ativo'],
                dicionario['created_at'],
                dicionario['updated_at']
            ]
        )
        con.commit()

        con.close()

    def gerar_query_coletar(self, dicionario):
        """
        Gera a query que será usada para coletar informações do db com base no dicionario recebido
        """
        query = "SELECT * FROM prontuarios WHERE "
        valores = []

        if 'id' in dicionario:
            query += 'id=? AND '
            valores.append(dicionario['id'])

        if 'nome' in dicionario:
            query += f'nome LIKE "%{dicionario["nome"]}%" AND '

        if 'cpf' in dicionario:
            query += 'cpf=? AND '
            valores.append(dicionario['cpf'])

        # Somente as cores que serão REMOVIDAS da query
        if 'vermelho' in dicionario:
            query += 'emergencia!=? AND '
            valores.append(dicionario['vermelho'])

        if 'laranja' in dicionario:
            query += 'emergencia!=? AND '
            valores.append(dicionario['laranja'])

        if 'amarelo' in dicionario:
            query += 'emergencia!=? AND '
            valores.append(dicionario['amarelo'])

        if 'verde' in dicionario:
            query += 'emergencia!=? AND '
            valores.append(dicionario['verde'])
        
        query = query[:-5]

        return query, valores

    def coletar(self, condicao=None):
        """
        Pode receber condição de pesquisa na forma de dicionario
        Coleta informações do db
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_prontuarios'))
        cur = con.cursor()

        try:
            if condicao:
                query, valores = self.gerar_query_coletar(condicao)
                res = cur.execute(query, valores).fetchall()
            else:
                res = cur.execute("SELECT * FROM prontuarios WHERE prontuario_ativo=?", ('True', )).fetchall()
        except sqlite3.OperationalError:
            res = []

        con.close()
        return res

    def gerar_query_atualizar(self, dicionario):
        """
        Recebe dicionario contendo novas informações para o db
        Gera a query para atualizar informações no db
        """
        campos = ['cpf', 'nome', 'telefone', 'nascimento', 'sexo', 'peso', 'sintomas', 'emergencia', 'observacoes', 'exames', 'diagnostico', 'receituario', 'prontuario_ativo', 'created_at', 'updated_at']
        query = 'UPDATE prontuarios SET '
        valores = []

        for campo in campos:
            if campo in dicionario:
                query += f'{campo}=?, '
                valores.append(dicionario[campo])

        query = query[:-2]

        query += ' WHERE id = ?'

        return query, valores

    def atualizar(self, indice, dicionario):
        """
        Recebe indice e dicionario
        Atualiza informações do prontuário do db
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_prontuarios'))
        cur = con.cursor()

        query, valores = self.gerar_query_atualizar(dicionario)
        valores.append(indice)
        cur.execute(query, valores)

        con.commit()
        con.close()

    def excluir(self, index:str):
        """
        Exclui um prontuário do db
        """
        jf = JsonFile()

        con = sqlite3.connect(jf.ler('caminho_db_prontuarios'))
        cur = con.cursor()

        cur.execute("DELETE FROM prontuarios WHERE id=?", index)

        con.commit()
        con.close()
