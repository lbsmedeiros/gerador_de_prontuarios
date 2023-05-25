import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from src.banco_de_dados import DbProntuarios, DbSetores

# testes
def teste_remover_arquivo_prontuarios():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\prontuarios.db"
    try:
        os.remove(caminho_db)
    except Exception:
        pass
    assert not Path(caminho_db).exists()

def teste_remover_arquivo_setores():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\setores.db"
    try:
        os.remove(caminho_db)
    except Exception:
        pass
    assert not Path(caminho_db).exists()

def teste_criar_db_prontuarios():
    Base = declarative_base()
    caminho_db = "C:\\Users\\lbsme\\Desktop\\prontuarios.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)
    Base.metadata.create_all(engine)
    assert Path(caminho_db).exists()
    
def teste_criar_db_setores():
    Base = declarative_base()
    caminho_db = "C:\\Users\\lbsme\\Desktop\\setores.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)
    Base.metadata.create_all(engine)
    assert Path(caminho_db).exists()

def teste_novos_prontuarios():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\prontuarios.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbProntuarios(engine)

    db.create({
        "cpf": "111.111.111-11",
        "nome": "JOÃO DAS NEVES",
        "telefone": "(11) 11111-1111",
        "nascimento": "01/01/2001",
        "sexo": "M",
        "peso": "101.0",
        "sintomas": "DOR DE CABEÇA\nFEBRE\nENJÔO",
        "emergencia": "amarelo",
        "observacoes": "",
        "exames": "",
        "diagnostico": "",
        "receituario": "",
        "prontuario_ativo": "True",
    })

    db.create({
        "cpf": "222.222.222-22",
        "nome": "MARIA DAS COUVES",
        "telefone": "(22) 2222-2222",
        "nascimento": "02/02/2002",
        "sexo": "F",
        "peso": "102.0",
        "sintomas": "AVC",
        "emergencia": "vermelho",
        "observacoes": "",
        "exames": "",
        "diagnostico": "",
        "receituario": "",
        "prontuario_ativo": "True",
    })

    assert len([resultado for resultado in db.read()]) > 0

def teste_novos_setores():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\setores.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbSetores(engine)
    db.create("CONSULTÓRIO 1")
    db.create("CONSULTÓRIO 2")

    assert len([resultado for resultado in db.read()]) > 0

def teste_ler_prontuarios_com_filtros_1():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\prontuarios.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    dict_filtros = {
        'id': 1,
        'nome': 'JOÃO DAS NEVES',
        'cpf': '111.111.111-11',
        'vermelho': 'vermelho',
        'laranja': 'laranja',
        'verde': 'verde',
    }

    db = DbProntuarios(engine)
    res = db.read(dict_filtros)

    assert len([i for i in res]) == 1

def teste_ler_prontuarios_com_filtros_2():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\prontuarios.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    dict_filtros = {
        'nome': 'MARIA',
    }

    db = DbProntuarios(engine)
    res = db.read(dict_filtros)

    assert len([i for i in res]) == 1

def teste_prontuarios_sem_filtros():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\prontuarios.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbProntuarios(engine)
    res = db.read()

    assert len([i for i in res]) == 2

def teste_ler_setores_com_filtro():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\setores.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbSetores(engine)
    res = db.read('CONSULTÓRIO 1')

    assert len([i for i in res]) == 1

def teste_ler_setores_sem_filtro():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\setores.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbSetores(engine)
    res = db.read()

    assert len([i for i in res]) == 2

def teste_update_prontuarios():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\prontuarios.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbProntuarios(engine)
    db.update(1, {'nome': 'ROSEMBRILDO DA SILVA'})

    res = [i for i in db.read({'id': 1})]

    assert res[0][2] == 'ROSEMBRILDO DA SILVA'

def teste_update_seletores():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\setores.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbSetores(engine)
    db.update(1, 'CONSULTÓRIO 3')

    res = [i for i in db.read('CONSULTÓRIO 3')]

    assert res[0][1] == 'CONSULTÓRIO 3'

def teste_deletar_do_db_prontuarios():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\prontuarios.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbProntuarios(engine)
    db.delete(1)

    res = [i for i in db.read({'id': 1})]

    assert len(res) == 0

def teste_deletar_do_db_setores():
    caminho_db = "C:\\Users\\lbsme\\Desktop\\setores.db"
    engine = create_engine(f"sqlite:///{caminho_db}", future=True)

    db = DbSetores(engine)
    db.delete('CONSULTÓRIO 3')

    res = [i for i in db.read('CONSULTÓRIO 3')]

    assert len(res) == 0
