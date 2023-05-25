from datetime import datetime
from sqlalchemy import String, DateTime, insert, select, update, delete
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


Base = declarative_base()


class Prontuarios(Base):
    __tablename__ = 'prontuarios'

    id: Mapped[int] = mapped_column(primary_key=True)
    cpf: Mapped[str] = mapped_column(String(14))
    nome: Mapped[str] = mapped_column(String(100))
    telefone: Mapped[str] = mapped_column(String(15))
    nascimento: Mapped[str] = mapped_column(String(10))
    sexo: Mapped[str] = mapped_column(String(1))
    peso: Mapped[str] = mapped_column(String(5))
    sintomas: Mapped[str] = mapped_column(String(500))
    emergencia: Mapped[str] = mapped_column(String(8))
    observacoes: Mapped[str] = mapped_column(String(500))
    exames: Mapped[str] = mapped_column(String(500))
    diagnostico: Mapped[str] = mapped_column(String(500))
    receituario: Mapped[str] = mapped_column(String(500))
    prontuario_ativo: Mapped[str] = mapped_column(String(5))
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)


class Setores(Base):
    __tablename__ = 'setores'

    id: Mapped[int] = mapped_column(primary_key=True)
    setor: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)


class DbProntuarios:
    def __init__(self, engine):
        self.engine = engine
        Base.metadata.create_all(self.engine)

    def create(self, dicionario):
        stmt = insert(Prontuarios).values(
            cpf = dicionario['cpf'],
            nome = dicionario['nome'],
            telefone = dicionario['telefone'],
            nascimento = dicionario['nascimento'],
            sexo = dicionario['sexo'],
            peso = dicionario['peso'],
            sintomas = dicionario['sintomas'],
            emergencia = dicionario['emergencia'],
            observacoes = dicionario['observacoes'],
            exames = dicionario['exames'],
            diagnostico = dicionario['diagnostico'],
            receituario = dicionario['receituario'],
            prontuario_ativo = dicionario['prontuario_ativo']
        )

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def read(self, dicionario=None):
        stmt = select(Prontuarios)

        if dicionario:
            for chave, value in dicionario.items():

                match chave:
                    case 'id':
                        stmt = stmt.where(Prontuarios.id == value)
                    case 'nome':
                        stmt = stmt.where(Prontuarios.nome.contains(value))
                    case 'cpf':
                        stmt = stmt.where(Prontuarios.cpf == value)
                    case 'prontuario_ativo':
                        stmt = stmt.where(Prontuarios.prontuario_ativo == value)
                    case 'vermelho' | 'laranja' | 'amarelo' | 'verde':
                        stmt = stmt.where(Prontuarios.emergencia != value)
                    case _:
                        continue

        with self.engine.connect() as conn:
            return conn.execute(stmt)

    def update(self, indice:int, dicionario):
        stmt = update(Prontuarios).values(dicionario).where(Prontuarios.id == indice)

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, index):
        stmt = delete(Prontuarios).where(Prontuarios.id == index)

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()


class DbSetores:
    def __init__(self, engine):
        self.engine = engine
        Base.metadata.create_all(self.engine)

    def create(self, valor):
        stmt = insert(Setores).values(
            setor = valor
        )

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def read(self, valor=None):
        stmt = select(Setores)

        if valor:
            stmt = stmt.where(Setores.setor==valor)

        with self.engine.connect() as conn:
            return conn.execute(stmt)

    def update(self, indice:int, novo_valor):
        stmt = update(Setores).values({'setor': novo_valor}).where(Setores.id == indice)

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, valor):
        stmt = delete(Setores).where(Setores.setor == valor)

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
