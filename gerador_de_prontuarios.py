# flet run main.py -d
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
from time import sleep

import flet as ft
import pyttsx3

from src.banco_de_dados import DbProntuarios, DbSetores
from src.chamada import Chamada
from src.temp_files import ClearTempFiles
from src.config import ArquivoConfigNaoEncontrado, JsonFile, VariavelConfigNaoEncontrada
from src.pdf import GerarPDF


def main(page: ft.Page):
    page.title = "Prontuários"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.window_maximized = True

    # VARIAVEIS
    caminho_para_o_db = ""
    selecionar_arquivo_ou_diretorio = ft.FilePicker()
    selected_files = ft.Text()
    dlg = ft.AlertDialog(title=ft.Text("Caminho salvo com sucesso!"))

    imput_nome_atendente = ft.TextField(
        label="Nome do atendente", dense=True, hint_text="Ex.: Dr. Leonardo Medeiros"
    )
    imput_cargo_atendente = ft.TextField(
        label="Cargo do atendente", dense=True, hint_text="Ex.: Cardiologista"
    )
    imput_contato_atendente = ft.TextField(
        label="Contatos", dense=True, hint_text="Separados por vírgulas"
    )

    imput_cpf = ft.TextField(label="CPF", width=500, dense=True)
    imput_nome = ft.TextField(
        label="Nome completo", width=500, dense=True, capitalization="CHARACTERS"
    )
    imput_telefone = ft.TextField(label="Telefone", width=500, dense=True)
    imput_nascimento = ft.TextField(
        label="Data de Nascimento", width=500, dense=True, hint_text="dd/mm/aaaa"
    )
    imput_sexo = ft.TextField(
        label="Sexo",
        width=500,
        dense=True,
        capitalization="CHARACTERS",
        hint_text="M/F",
    )
    imput_peso = ft.TextField(
        label="Peso",
        width=500,
        dense=True,
        hint_text="Somente números",
        suffix_text="Kg",
    )
    imput_sintomas = ft.TextField(
        label="Sintomas",
        multiline=True,
        dense=True,
        capitalization="CHARACTERS",
    )
    imput_emergencia = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="green", fill_color=ft.colors.GREEN),
                ft.Radio(value="yellow", fill_color=ft.colors.YELLOW),
                ft.Radio(value="orange", fill_color=ft.colors.ORANGE),
                ft.Radio(value="red", fill_color=ft.colors.RED),
            ]
        )
    )

    imput_id_pesquisa = ft.TextField(label="Prontuário", dense=True)
    imput_nome_pesquisa = ft.TextField(
        label="Nome", dense=True, capitalization="CHARACTERS"
    )
    imput_cpf_pesquisa = ft.TextField(label="CPF", dense=True)
    checkbox_vermelho = ft.Checkbox(label="Vermelho")
    checkbox_laranja = ft.Checkbox(label="Laranja")
    checkbox_amarelo = ft.Checkbox(label="Amarelo")
    checkbox_verde = ft.Checkbox(label="Verde")
    filtro_emergencia = ft.Row(
        controls=(
            [checkbox_vermelho, checkbox_laranja, checkbox_amarelo, checkbox_verde]
        )
    )

    messenger = ft.SnackBar(content=ft.Text(""), bgcolor="#545756")
    page.snack_bar = messenger

    dropdown_menu_selecionar_setor = ft.Dropdown(
        width=350, dense=True, label="Selecione o setor para chamada"
    )
    switch_finalizados = ft.Switch(
        label = "Mostrar prontuários finalizados",
        value=False,
        active_color="blue",
    )
    container_de_prontuarios = ft.Container(padding=ft.padding.symmetric(vertical=10))

    imput_observacoes = ft.TextField(
        label="Observações",
        multiline=True,
        min_lines=2,
        max_lines=2,
        width=page.width - 50,
        dense=True,
        capitalization="CHARACTERS",
    )
    imput_exames = ft.TextField(
        label="Exames solicitados",
        multiline=True,
        min_lines=2,
        max_lines=2,
        width=page.width - 50,
        dense=True,
        capitalization="CHARACTERS",
    )
    imput_diagnostico = ft.TextField(
        label="Diagnóstico",
        multiline=True,
        min_lines=2,
        max_lines=2,
        width=page.width - 50,
        dense=True,
        capitalization="CHARACTERS",
    )
    imput_receita = ft.TextField(
        label="Receita",
        multiline=True,
        min_lines=2,
        max_lines=2,
        width=page.width - 50,
        dense=True,
        capitalization="CHARACTERS",
    )

    imput_inserir_local = ft.TextField(
        label="Ambiente de trabalho", dense=True, capitalization="CHARACTERS"
    )
    dropdown_menu_excluir = ft.Dropdown(
        width=350, dense=True, label="Selecione o setor para excluir"
    )
    coluna_de_locais = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END
    )

    container_numero_prontuario = ft.Container(alignment=ft.alignment.center, width=200)
    text_cor_prontuario = ft.Text(color="black")
    text_nome = ft.Text()
    text_cpf = ft.Text()
    text_data_nascimento = ft.Text()
    text_sexo = ft.Text()
    text_peso = ft.Text()
    text_chegada = ft.Text()
    text_ultimo_atendimento = ft.Text()
    text_contato = ft.Text()
    btn_gerar_receita = ft.ElevatedButton("Gerar Receita")
    btn_chamar_prontuario = ft.OutlinedButton("Chamar prontuário")

    coluna_chamada = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    container_de_chamada = ft.Container(alignment=ft.alignment.top_left)

    # FUNCOES
    def limpar_tela():
        """
        Elimina todos os controles da tela
        """
        page.clean()
        page.update()

    def open_dlg():
        """
        Abre a janela de selecao de arquivo
        """
        page.dialog = dlg
        dlg.open = True
        page.update()

    def salvar_caminhos_dbs(e):
        """
        Coleta o caminho recebido pela janela de seleção de arquivos;
        Se for diretório, cria os dbs no diretório;
        Se for arquivo, usa o arquivo informado;
            Verifica se existe o db de setores no diretorio
            Se não, cria, se sim, usa esse mesmo
        Em todo caso, salva os caminhos no config.json;
        """
        global caminho_para_o_db

        if Path(caminho_para_o_db).is_dir():
            db_prontuarios = Path(caminho_para_o_db) / "prontuarios.db"
            if not db_prontuarios.exists():
                con = sqlite3.connect(str(db_prontuarios.resolve()))
                con.commit()
                con.close()
            db_setores = Path(caminho_para_o_db) / "setores.db"
            if not db_setores.exists():
                con = sqlite3.connect(str(db_setores.resolve()))
                con.commit()
                con.close()
            lista_de_chamada = Path(caminho_para_o_db) / "chamada.txt"
        else:
            db_prontuarios = Path(caminho_para_o_db)
            db_setores = Path(caminho_para_o_db).parent / "setores.db"
            if not db_setores.exists():
                con = sqlite3.connect(str(db_setores.resolve()))
                con.commit()
                con.close()
            lista_de_chamada = Path(caminho_para_o_db).parent / "chamada.txt"

        jfile = JsonFile()
        jfile.criar_ou_atualizar("caminho_db_prontuarios", str(db_prontuarios.resolve()))
        jfile.criar_ou_atualizar("caminho_db_setores", str(db_setores.resolve()))
        jfile.criar_ou_atualizar("lista_de_chamada", str(lista_de_chamada.resolve()))

        dlg.on_dismiss = tela_inicial
        open_dlg()

    def resultado_selecao_arquivos(e):
        """
        Coleta o resultado da selecao de arquivos/diretorios
        Mostra a opcao selecionada na tela
        """
        global caminho_para_o_db
        if e.files:
            caminho_para_o_db = e.files[0].path
            selected_files.value = f"Arquivo selecionado: {e.files[0].name}"
        elif e.path:
            caminho_para_o_db = e.path
            selected_files.value = f"Caminho selecionado: {e.path}"
        else:
            caminho_para_o_db = ""
            selected_files.value = ""
        selected_files.update()

    def cpf_on_change(e):
        """
        Verifica a cada mudança se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, muda a cor da borda do campo para preto
        """
        temp_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', '-']
        variavel_de_controle = False
        if len(e.control.value) > 0:
            for l in e.control.value:
                if l not in temp_list:
                    imput_cpf.border_color = 'red'
                    variavel_de_controle = True
            if not variavel_de_controle:
                imput_cpf.border_color = 'black'
        else:
            imput_cpf.border_color = 'black'
        imput_cpf.update()

    def cpf_on_blur(e):
        """
        Verifica quando muda de foco se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, trata a informação para ser mostrada da forma correta e muda a cor da borda do campo para preto
        """
        temp = "".join(n for n in imput_cpf.value if n.isnumeric())

        if len(temp) == 0:
            imput_cpf.border_color = "black"
        elif len(temp) == 11:
            imput_cpf.value = f"{temp[:3]}.{temp[3:6]}.{temp[6:9]}-{temp[9:]}"
            imput_cpf.border_color = "black"
        else:
            imput_cpf.border_color = "red"

        imput_cpf.update()

    def cpf_pesquisa_on_change(e):
        """
        Verifica a cada mudança se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, muda a cor da borda do campo para preto
        """
        temp_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', '-']
        variavel_de_controle = False
        if len(e.control.value) > 0:
            for l in e.control.value:
                if l not in temp_list:
                    imput_cpf_pesquisa.border_color = 'red'
                    variavel_de_controle = True
            if not variavel_de_controle:
                imput_cpf_pesquisa.border_color = 'black'
        else:
            imput_cpf_pesquisa.border_color = 'black'
        imput_cpf_pesquisa.update()

    def cpf_pesquisa_on_blur(e):
        """
        Verifica quando muda de foco se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, trata a informação para ser mostrada da forma correta e muda a cor da borda do campo para preto
        """
        temp = "".join(n for n in imput_cpf_pesquisa.value if n.isnumeric())

        if len(temp) == 0:
            imput_cpf_pesquisa.value = ""
            imput_cpf_pesquisa.border_color = "black"
        elif len(temp) == 11:
            imput_cpf_pesquisa.value = f"{temp[:3]}.{temp[3:6]}.{temp[6:9]}-{temp[9:]}"
            imput_cpf_pesquisa.border_color = "black"
        else:
            imput_cpf_pesquisa.border_color = "red"

        page.update()

    def nome_on_blur(e):
        """
        Muda a cor da borda do campo para preto
        Necessário para ter certeza que estará na cor certa após uma tentativa errada de salvar informação com o campo
        """
        imput_nome.border_color = "black"
        page.update()

    def telefone_on_change(e):
        """
        Verifica a cada mudança se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, muda a cor da borda do campo para preto
        """
        temp_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '(', ')', '-', ' ']
        variavel_de_controle = False
        if len(e.control.value) > 0:
            for l in e.control.value:
                if l not in temp_list:
                    imput_telefone.border_color = 'red'
                    variavel_de_controle = True
            if not variavel_de_controle:
                imput_telefone.border_color = 'black'
        else:
            imput_telefone.border_color = 'black'
        imput_telefone.update()

    def telefone_on_blur(e):
        """
        Verifica quando muda de foco se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, trata a informação para ser mostrada da forma correta e muda a cor da borda do campo para preto
        """
        telefone_numeral = "".join(n for n in imput_telefone.value if n.isnumeric())

        while telefone_numeral.startswith("0"):
            telefone_numeral = telefone_numeral[1:]

        match len(telefone_numeral):
            case 0:
                imput_telefone.value = ""
                imput_telefone.border_color = "black"
            case (8 | 9):
                imput_telefone.value = f"(21) {telefone_numeral[:-4]}-{telefone_numeral[-4:]}"
                imput_telefone.border_color = "black"
            case (10 | 11):
                imput_telefone.value = f"({telefone_numeral[:2]}) {telefone_numeral[2:-4]}-{telefone_numeral[-4:]}"
                imput_telefone.border_color = "black"
            case _:
                imput_telefone.border_color = "red"

        page.update()

    def nascimento_on_change(e):
        """
        Verifica a cada mudança se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, muda a cor da borda do campo para preto
        """
        temp_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', r'/', '-']
        variavel_de_controle = False
        if len(e.control.value) > 0:
            for l in e.control.value:
                if l not in temp_list:
                    imput_nascimento.border_color = 'red'
                    variavel_de_controle = True
            if not variavel_de_controle:
                imput_nascimento.border_color = 'black'
        else:
            imput_nascimento.border_color = 'black'
        imput_nascimento.update()

    def nascimento_on_blur(e):
        """
        Verifica quando muda de foco se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, trata a informação para ser mostrada da forma correta e muda a cor da borda do campo para preto
        """
        temp = "".join(n for n in imput_nascimento.value if n.isnumeric())
        if len(temp) == 0:
            imput_nascimento.value = ""
            imput_nascimento.border_color = "black"
        elif len(temp) == 8:
            imput_nascimento.value = f"{temp[:2]}/{temp[2:4]}/{temp[4:]}"
            imput_nascimento.border_color = "black"
        else:
            imput_nascimento.border_color = "red"
        page.update()

    def sexo_on_change(e):
        """
        Verifica a cada mudança se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, muda a cor da borda do campo para preto
        """
        if imput_sexo.value == "M" or imput_sexo.value == "F" or imput_sexo.value == "":
            imput_sexo.border_color = "black"
        else:
            imput_sexo.border_color = "red"
        imput_sexo.update()

    def peso_on_change(e):
        """
        Verifica a cada mudança se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, muda a cor da borda do campo para preto
        """
        temp_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ',', '.']
        variavel_de_controle = False
        if len(e.control.value) > 0:
            for l in e.control.value:
                if l not in temp_list:
                    imput_peso.border_color = 'red'
                    variavel_de_controle = True
            if not variavel_de_controle:
                imput_peso.border_color = 'black'
        else:
            imput_peso.border_color = 'black'
        imput_peso.update()

    def peso_on_blur(e):
        """
        Verifica quando muda de foco se a informação imputada no campo é compatível com o esperado
        Se não, muda a cor da borda do campo para vermelho
        Se sim, trata a informação para ser mostrada da forma correta e muda a cor da borda do campo para preto
        """
        temp = "".join(n for n in imput_peso.value if not n.isalpha())

        if len([n for n in imput_peso.value if n.isnumeric()]) == 0:
            imput_peso.value = ""
            imput_peso.border_color = "black"
        elif "." in temp and "," in temp:
            imput_peso.border_color = "red"
        elif (
            len([d for d in temp if d == "."]) > 1
            or len([d for d in temp if d == ","]) > 1
        ):
            imput_peso.border_color = "red"
        elif "." in temp or "," in temp:
            if "." in temp:
                temps = temp.split(".")
            elif "," in temp:
                temps = temp.split(",")
            if len(temps[1]) > 1:
                imput_peso.value = temps[0] + "." + temps[1][0]
                imput_peso.border_color = "black"
            elif len(temps[1]) == 0:
                imput_peso.value = temps[0] + ".0"
                imput_peso.border_color = "black"
            else:
                imput_peso.value = temps[0] + "." + temps[1]
                imput_peso.border_color = "black"
        else:
            imput_peso.value = temp + ".0"
            imput_peso.border_color = "black"

        page.update()

    def sintomas_on_blur(e):
        """
        Muda a cor da borda do campo para preto
        Necessário para ter certeza que estará na cor certa após uma tentativa errada de salvar informação com o campo
        """
        imput_sintomas.border_color = "black"
        page.update()

    def validacoes_individuais():
        """
        Verifica se algum dos campos está vermelho
        Se sim, retorna True
        Também verifica se imput_nome ou imput_sintomas estão vazios
        Se sim, muda as cores das bodas para vermelho e retorna True
        """
        erro = False
        if imput_cpf.border_color == "red":
            # Pode estar vazio pois o paciente pode ter documento estrangeiro
            erro = True
        if imput_nome.value == "":
            imput_nome.border_color = "red"
            erro = True
        if imput_telefone.border_color == "red":
            # Pode estar vazio pois o paciente pode não ter telefone
            erro = True
        if imput_nascimento.border_color == "red":
            # Pode estar vazio pois o paciente pode querer não informar a data de nascimento
            erro = True
        if imput_peso.border_color == "red":
            # Pode estar vazio pois o paciente pode querer não informar ou não saber o peso
            erro = True
        if imput_sexo.border_color == "red":
            # Pode estar vazio pois o paciente pode querer não informar o sexo
            erro = True
        if imput_sintomas.value == "":
            imput_sintomas.border_color = "red"
            erro = True
        return erro

    def inserir_no_db_prontuarios(dicionario):
        """
        Recebe dicionario
        Instancia a classe DbProntuarios e insere o dicionario no db
        """
        repository = DbProntuarios()
        repository.inserir(dicionario)

    def salvar_novo_prontuario(e):
        """
        Verifica a situação dos campos
        Se estiver tudo ok, envia as informações em forma de dicionário para a função que insere no db
        Reseta a tela
        """
        if not validacoes_individuais():
            # Inserir informações no db
            inserir_no_db_prontuarios(
                {
                    "cpf": imput_cpf.value,
                    "nome": imput_nome.value,
                    "telefone": imput_telefone.value,
                    "nascimento": imput_nascimento.value,
                    "sexo": imput_sexo.value,
                    "peso": imput_peso.value,
                    "sintomas": imput_sintomas.value,
                    "emergencia": imput_emergencia.value,
                    "observacoes": "",
                    "exames": "",
                    "diagnostico": "",
                    "receituario": "",
                    "prontuario_ativo": "True",
                    "created_at": datetime.now().strftime("%d/%m/%Y - %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%d/%m/%Y - %H:%M:%S"),
                }
            )

            # Resetar a tela
            imput_cpf.border_color = "black"
            imput_cpf.value = ""
            imput_nome.border_color = "black"
            imput_nome.value = ""
            imput_telefone.border_color = "black"
            imput_telefone.value = ""
            imput_nascimento.border_color = "black"
            imput_nascimento.value = ""
            imput_sexo.border_color = "black"
            imput_sexo.value = ""
            imput_peso.border_color = "black"
            imput_peso.value = ""
            imput_sintomas.border_color = "black"
            imput_sintomas.value = ""
            imput_emergencia.value = "yellow"

            page.snack_bar.content = ft.Text(
                "Prontuário salvo com sucesso.", color="white"
            )
            page.snack_bar.open = True

        page.update()

    def atualizar_no_db_prontuarios(index, dicionario):
        """
        Recebe dicionario
        Instancia a classe DbProntuarios e atualiza o prontuario no db
        """
        repository = DbProntuarios()
        repository.atualizar(index, dicionario)

    def editar_prontuario(e):
        """
        Verifica a situação dos campos
        Se estiver tudo ok, envia as informações em forma de dicionário para a função que atualiza no db
        Retorna para  a tela de visialização do prontuário
        """
        # Verificar se está tudo preenchido corretametne
        if not validacoes_individuais():
            # Inserir informações no db
            atualizar_no_db_prontuarios(
                e.control.data,
                {
                    "cpf": imput_cpf.value,
                    "nome": imput_nome.value,
                    "telefone": imput_telefone.value,
                    "nascimento": imput_nascimento.value,
                    "sexo": imput_sexo.value,
                    "peso": imput_peso.value,
                    "sintomas": imput_sintomas.value,
                    "emergencia": imput_emergencia.value,
                    "updated_at": datetime.now().strftime("%d/%m/%Y - %H:%M:%S"),
                },
            )

            page.snack_bar.content = ft.Text(
                "Prontuário atualizado com sucesso.", color="white"
            )
            page.snack_bar.open = True

            tela_visualizar_prontuario(e)

    def update_prontuario(e):
        """
        Atualiza os itens observacoes, exames, diagnostico e receituario no db SE estiverem preenchidos
        Se houver algum valor em receituario, atualiza tbm o valor de prontuario_ativo para False
        """
        index = e.control.data

        temp_dict1 = {
            "observacoes": imput_observacoes.value,
            "exames": imput_exames.value,
            "diagnostico": imput_diagnostico.value,
            "receituario": imput_receita.value,
        }
        temp_dict2 = {}
        for chave, valor in temp_dict1.items():
            if valor != None and valor != "":
                temp_dict2[chave] = valor
                if chave == "receituario":
                    temp_dict2["prontuario_ativo"] = "False"

        temp_dict2["updated_at"] = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

        atualizar_no_db_prontuarios(index, temp_dict2)

        page.snack_bar.content = ft.Text(
            "Prontuário atualizado com sucesso.", color="white"
        )
        page.snack_bar.open = True
        page.update()

        tela_visualizar_prontuario(e)

    def pesquisar_prontuario(e):
        """
        Coleta as informações nos campos de pesquisa
        Coleta posição do switch_finalizados
        IMPORTANTE: Coleta apenas os checkbox que estão na posição FALSE
        Imputa essas informações num dicionario e usa para coletar informações do db
        Filtra resultado pela posição do switch_finalizados
        "Monta" cada resultado numa instância de ListTile
        Insere cada ListTile numa lista temporária organizando pela cor
        Insere a lista no container_de_prontuarios
        """
        temp_dict = {}

        if imput_id_pesquisa.value and not imput_id_pesquisa.value == "":
            temp_dict["id"] = imput_id_pesquisa.value

        if imput_nome_pesquisa.value and not imput_nome_pesquisa.value == "":
            temp_dict["nome"] = imput_nome_pesquisa.value

        if imput_cpf_pesquisa.value and not imput_cpf_pesquisa.value == "":
            temp_dict["cpf"] = imput_cpf_pesquisa.value

        temp_dict["prontuario_ativo"] = switch_finalizados.value

        if checkbox_vermelho.value == False:
            temp_dict["vermelho"] = "red"

        if checkbox_laranja.value == False:
            temp_dict["laranja"] = "orange"

        if checkbox_amarelo.value == False:
            temp_dict["amarelo"] = "yellow"

        if checkbox_verde.value == False:
            temp_dict["verde"] = "green"

        db = DbProntuarios()
        if temp_dict:
            res = db.coletar(temp_dict)
        else:
            res = db.coletar()

        if not switch_finalizados.value:
            res = [item for item in res if item[-3] == "True"]

        temp_list = []
        for i in range(4):
            match i:
                case 0:
                    variavel = "red"
                    cor = "vermelho"
                case 1:
                    variavel = "orange"
                    cor = "laranja"
                case 2:
                    variavel = "yellow"
                    cor = "amarelo"
                case 3:
                    variavel = "green"
                    cor = "verde"
            for resultado in res:
                if resultado[8] == variavel:
                    if resultado[-3] == "False":
                        temp_list.append(
                            ft.ListTile(
                                title=ft.Text(
                                    f"Prontuario {resultado[0]}, CPF {resultado[1]}, Nome {resultado[2]}"
                                ),
                                subtitle=ft.Row(
                                    [
                                        ft.Text(f"Atendimento {cor}", color=variavel),
                                        ft.Text("Finalizado", size=20, weight="bold"),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                dense=True,
                                on_click=tela_visualizar_prontuario,
                            )
                        )
                    else:
                        temp_list.append(
                            ft.ListTile(
                                title=ft.Text(
                                    f"Prontuario {resultado[0]}, CPF {resultado[1]}, Nome {resultado[2]}"
                                ),
                                subtitle=ft.Text(f"Atendimento {cor}", color=variavel),
                                dense=True,
                                on_click=tela_visualizar_prontuario,
                            )
                        )

        container_de_prontuarios.content = ft.Column(
            temp_list,
            spacing=0,
        )
        page.update()

    def mostrar_todos_os_prontuarios_nao_finalizado(e=None):
        """
        Reseta os valores de pesquisa, os checkboxes e o switch
        coleta todas as informações do db
        "Monta" cada resultado numa instância de ListTile
        Insere cada ListTile numa lista temporária organizando pela cor
        Insere a lista no container_de_prontuarios
        """
        imput_id_pesquisa.value = ""
        imput_nome_pesquisa.value = ""
        imput_cpf_pesquisa.value = ""
        checkbox_vermelho.value = True
        checkbox_laranja.value = True
        checkbox_amarelo.value = True
        checkbox_verde.value = True
        switch_finalizados.value = False

        db = DbProntuarios()
        res = db.coletar()
        temp_list = []

        for i in range(4):
            match i:
                case 0:
                    variavel = "red"
                    cor = "vermelho"
                case 1:
                    variavel = "orange"
                    cor = "laranja"
                case 2:
                    variavel = "yellow"
                    cor = "amarelo"
                case 3:
                    variavel = "green"
                    cor = "verde"
            for resultado in res:
                if resultado[8] == variavel:
                    temp_list.append(
                        ft.ListTile(
                            title=ft.Text(
                                f"Prontuario {resultado[0]}, CPF {resultado[1]}, Nome {resultado[2]}"
                            ),
                            subtitle=ft.Text(f"Atendimento {cor}", color=variavel),
                            dense=True,
                            on_click=tela_visualizar_prontuario,
                        )
                    )

        container_de_prontuarios.content = ft.Column(
            temp_list,
            spacing=0,
        )
        page.update()

    def preencher_identificacao():
        """
        Preenche os valores de imput_nome_atendente, imput_cargo_atendente e imput_contato_atendente
        com a informação salva no config.json.
        Se não houver config.json ou se não houver a chave 'identificacao' nele, deixa em branco
        """
        try:
            jf = JsonFile()
            temp_dict = jf.ler("identificacao")
            imput_nome_atendente.value = temp_dict["nome_medico"]
            imput_cargo_atendente.value = temp_dict["cargo_medico"]
            imput_contato_atendente.value = ", ".join(temp_dict["contatos"])
        except (ArquivoConfigNaoEncontrado, VariavelConfigNaoEncontrada):
            imput_nome_atendente.value = ""
            imput_cargo_atendente.value = ""
            imput_contato_atendente.value = ""

    def gravar_identificacao(e):
        """
        Verifica cada um dos campos de identificacao
        Se houver algum valor nele, insere num dicionario e muda a cor da borda do campo para preto
        Se não houver algum valor nele, muda a cor da borda do campo para vermelho
        Se constar "nome_medico", "cargo_medico" e "contatos" nas chaves do dicionario, insere a informação no config.json
        """
        temp_dict = {}

        if imput_nome_atendente.value and imput_nome_atendente.value != "":
            temp_dict["nome_medico"] = imput_nome_atendente.value
            imput_nome_atendente.border_color = "black"
        else:
            imput_nome_atendente.border_color = "red"

        if imput_cargo_atendente.value and imput_cargo_atendente.value != "":
            temp_dict["cargo_medico"] = imput_cargo_atendente.value
            imput_cargo_atendente.border_color = "black"
        else:
            imput_cargo_atendente.border_color = "red"

        if imput_contato_atendente.value and imput_contato_atendente.value != "":
            temp_list = imput_contato_atendente.value.split(",")
            temp_list = [contato.strip() for contato in temp_list]
            temp_dict["contatos"] = temp_list
            imput_contato_atendente.border_color = "black"
        else:
            imput_contato_atendente.border_color = "red"

        if (
            "nome_medico" in temp_dict
            and "cargo_medico" in temp_dict
            and "contatos" in temp_dict
        ):
            jf = JsonFile()
            jf.criar_ou_atualizar("identificacao", temp_dict)

            page.snack_bar.content = ft.Text(
                "Identificação gravada com sucesso.", color="white"
            )
            page.snack_bar.open = True

        page.update()

    def limpar_identificacao(e):
        """
        Limpa os campos de identificação e a informação no config.json
        """
        imput_nome_atendente.value = ""
        imput_cargo_atendente.value = ""
        imput_contato_atendente.value = ""
        page.update()
        temp_dict = {"nome_medico": "", "cargo_medico": "", "contatos": [""]}
        jf = JsonFile()
        jf.criar_ou_atualizar("identificacao", temp_dict)

    def voltar_para_chamar_pacientes(e):
        """
        Verifica se a tecla apertada é "Escape"
        Se sim, retorna para a tela_chamar_pacientes
        """
        if e.key == "Escape":
            tela_chamar_pacientes()

    def gerar_opcoes_dropdown_selecionar_setor():
        """
        Coleta setores no db
        Gera lista contendo instancia de dropdown.Option de cada setor
        Atribui lista ao dropdown_menu_selecionar.option
        """
        temp_list = []
        db = DbSetores()
        lista_de_tuplas = db.coletar_varios()
        if lista_de_tuplas:
            for tupla in lista_de_tuplas:
                temp_list.append(ft.dropdown.Option(tupla[1]))
        dropdown_menu_selecionar_setor.options = temp_list

    def salvar_setor(e):
        """
        Coleta do dropdown_menu_selecionar_setor o setor onde o programa está sendo usado
        Salva essa informacao no config.json para ser usada sempre que for chamar um paciente
        """
        jf = JsonFile()
        jf.criar_ou_atualizar("setor_atual", dropdown_menu_selecionar_setor.value)

        page.snack_bar.content = ft.Text(
            "Local de trabalho salvo com sucesso.", color="white"
        )
        page.snack_bar.open = True

        page.update()

    def limpar_setor(e):
        """
        Limpa a informação no dropdown_menu_selecionar_setor e no db
        """
        dropdown_menu_selecionar_setor.value = ""
        page.update()
        jf = JsonFile()
        jf.criar_ou_atualizar("setor_atual", '')

    def set_valor_inicial_menu_selecionar_setor():
        """
        Se existir um local salvo no config.json, e se esse local estiver no db_setores
        Esse local deverá vir selecionado
        Se não, deverá vir vazio
        """
        jf = JsonFile()
        try:
            setor_atual = jf.ler("setor_atual")
            db = DbSetores()
            if db.coletar_um(setor_atual):
                dropdown_menu_selecionar_setor.value = setor_atual
        except (VariavelConfigNaoEncontrada, ArquivoConfigNaoEncontrado):
            dropdown_menu_selecionar_setor.value = ""

    def preenche_campo_setores():
        """
        Coleta setores no db
        Gera lista contendo instancia de Text de cada setor
        Atribui lista ao coluna_de_locais.controls
        """
        db = DbSetores()
        lista_de_tuplas = db.coletar_varios()
        if lista_de_tuplas:
            temp_list = []
            for tupla in lista_de_tuplas:
                temp_list.append(ft.Text(tupla[1]))
        else:
            temp_list = [ft.Text("A lista está vazia.")]
        coluna_de_locais.controls = temp_list

    def gerar_opcoes_dropdown_excluir():
        """
        Coleta setores no db
        Gera lista contendo instancia de dropdown.Option de cada setor
        Atribui lista ao dropdown_menu_excluir.option
        """
        temp_list = []
        db = DbSetores()
        lista_de_tuplas = db.coletar_varios()
        if lista_de_tuplas:
            for tupla in lista_de_tuplas:
                temp_list.append(ft.dropdown.Option(tupla[1]))
        dropdown_menu_excluir.options = temp_list

    def inserir_novo_local(e):
        """
        Coleta texto dentro do imput_inserir_local
        Insere texto no banco de dados caminho_db_setores
        Set o valor de imput_inserir_local para uma string vazia
        """
        if imput_inserir_local.value and imput_inserir_local.value != "":
            db = DbSetores()
            db.inserir(imput_inserir_local.value)
            imput_inserir_local.value = ""
            preenche_campo_setores()
            gerar_opcoes_dropdown_excluir()
            page.snack_bar.content = ft.Text("Salvo com sucesso.", color="white")
            page.snack_bar.open = True
            page.update()

    def excluir_local(e):
        """
        Coleta texto dentro do dropdown_menu_excluir
        Insere texto no banco de dados caminho_db_setores
        Seta o valor de imput_inserir_local para uma string vazia
        """
        if dropdown_menu_excluir.value and dropdown_menu_excluir.value != "":
            db = DbSetores()
            db.excluir(dropdown_menu_excluir.value)
            preenche_campo_setores()
            gerar_opcoes_dropdown_excluir()
            dropdown_menu_excluir.value = ""
            page.snack_bar.content = ft.Text(
                "Tarefa realizada com sucesso.", color="white"
            )
            page.snack_bar.open = True
            page.update()

    def gerar_pdf_receita(e):
        """
        Coleta a identificação do atendente do config.json
        Coleta o receituário do prontuário
        Usa as informações para gerar a receita em pdf
        """
        try:
            jf = JsonFile()
            temp_dict1 = jf.ler("identificacao")

            index_cpf = text_cpf.value.index(' ')+1
            cpf = text_cpf.value[index_cpf:-1]
            db = DbProntuarios()
            res = db.coletar({'cpf': cpf})[0]
            receituario = res[-4]
            temp_dict1["receituario"] = receituario

            pdf = GerarPDF()
            pdf.gerar_receita(temp_dict1)
        except ArquivoConfigNaoEncontrado:
            page.snack_bar.content = ft.Text(
                "O arquivo de configuração do programa foi movido e não pôde ser encontrado.", color="white"
            )
            page.snack_bar.open = True
            page.update()
        except VariavelConfigNaoEncontrada:
            page.snack_bar.content = ft.Text(
                "É necessário identificar o atendente antes de solicitar a geração da receita.", color="white"
            )
            page.snack_bar.open = True
            page.update()
        except Exception:
            page.snack_bar.content = ft.Text(
                "Não foi possível gerar o arquivo.", color="white"
            )
            page.snack_bar.open = True
            page.update()

    def chamar_prontuario(e):
        """
        Coleta apenas o nome do paciente
        Envia para a função Chamada.nova_chamada
        """
        index = text_nome.value.index(" ") + 1
        nome = text_nome.value[index:]
        ch = Chamada()
        ch.nova_chamada(nome)
        page.snack_bar.content = ft.Text("Chamada realizada.", color="white")
        page.snack_bar.open = True
        page.update()

    def gerar_tela_chamada(lista_de_nomes_e_destinos=[]):
        """
        Recebe lista de nomes e setores
        Gera a formatação da tela onde de chamada de pacientes
        """
        temp_list = []
        coluna_chamada.controls = []

        if lista_de_nomes_e_destinos:
            for index, item in enumerate(lista_de_nomes_e_destinos):
                if index == 0:
                    coluna_chamada.controls.append(
                        ft.Column(
                            controls=[
                                ft.Text(item[0], color="black", size=100, weight="bold"),
                                ft.Text(item[1], color="black", size=60, weight="bold"),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    )
                else:
                    temp_list.append(
                        ft.Row(
                            controls=[
                                ft.Text(item[0], color="black", size=40, weight="bold"),
                                ft.Text(item[1], color="black", size=40, weight="bold"),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        )
                    )
        else:
            coluna_chamada.controls.append(
                ft.Column(
                    controls=[
                        ft.Text("Vazio", color="black", size=100, weight="bold"),
                        ft.Text("Vazio", color="black", size=60, weight="bold"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        container_de_chamada.content = ft.Column(
            controls=temp_list,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        coluna_chamada.controls.append(container_de_chamada)
        coluna_chamada.update()

    def tratamento_file_picker(e):
        """
        Verifica qual botão foi clicado
        Se for o botão de selecionar arquivo
            Configura o selecionar_arquivo_ou_diretorio para receber apenas arquivos .db
        Se não
            Configura o selecionar_arquivo_ou_diretorio para receber diretórios
        """
        if e.control.text == "Selecionar arquivo...":
            selecionar_arquivo_ou_diretorio.file_type = ft.FilePickerFileType.CUSTOM
            selecionar_arquivo_ou_diretorio.pick_files(allowed_extensions = ['db'], dialog_title="Selecione arquivo db")
        else:
            selecionar_arquivo_ou_diretorio.get_directory_path(dialog_title="Selecione o diretório onde o banco de dados será criado")

    def sair(e):
        """
        Limpa os arquivos temporários do Windows
        Sai da aplicacao
        """
        ctf = ClearTempFiles()
        ctf.limpar_arquivos_temporarios()
        page.window_close()

    def tela_novos_prontuarios(e=None):
        """
        Chama tela de inclusão de novos prontuários
        """
        page.on_keyboard_event = None
        page.bgcolor = None
        limpar_tela()

        # Resetar a tela
        imput_cpf.border_color = "black"
        imput_cpf.value = ""
        imput_cpf.autofocus = True
        imput_cpf.on_change = cpf_on_change
        imput_cpf.on_blur = cpf_on_blur
        imput_nome.border_color = "black"
        imput_nome.value = ""
        imput_nome.on_blur = nome_on_blur
        imput_telefone.border_color = "black"
        imput_telefone.value = ""
        imput_telefone.on_change = telefone_on_change
        imput_telefone.on_blur = telefone_on_blur
        imput_nascimento.border_color = "black"
        imput_nascimento.value = ""
        imput_nascimento.on_change = nascimento_on_change
        imput_nascimento.on_blur = nascimento_on_blur
        imput_sexo.border_color = "black"
        imput_sexo.value = ""
        imput_sexo.on_change = sexo_on_change
        imput_peso.border_color = "black"
        imput_peso.value = ""
        imput_peso.on_change = peso_on_change
        imput_peso.on_blur = peso_on_blur
        imput_sintomas.border_color = "black"
        imput_sintomas.value = ""
        imput_sintomas.width = 500
        imput_sintomas.read_only = False
        imput_sintomas.min_lines = 5
        imput_sintomas.max_lines = 5
        imput_sintomas.on_blur = sintomas_on_blur
        imput_emergencia.value = "yellow"

        coluna_a = ft.Column(
            controls=[
                imput_cpf,
                imput_nome,
                imput_telefone,
                imput_nascimento,
                imput_sexo,
                imput_peso,
                imput_sintomas,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        coluna_b = ft.Column(
            controls=[
                ft.Text("Tipo de atendimento:", size=20, weight="bold"),
                imput_emergencia,
                ft.Divider(height=450),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_main_content = ft.Row(
            [
                ft.VerticalDivider(width=9, thickness=3, color='white'),
                coluna_a,
                ft.VerticalDivider(width=9, thickness=3, color='white'),
                coluna_b,
                ft.VerticalDivider(width=9, thickness=3),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_btns = ft.Row(
            [
                ft.ElevatedButton("Sair", on_click=sair),
                ft.ElevatedButton("Voltar", on_click=tela_inicial),
                ft.ElevatedButton("Salvar", on_click=salvar_novo_prontuario),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        page.add(
            ft.Text("Novo prontuário:", size=20, weight="bold"),
            ft.Divider(height=8),
            row_main_content,
            ft.Divider(height=8),
            row_btns,
        )

    def tela_editar_prontuario(e=None):
        """
        Chama tela de edição de prontuários
        """
        page.on_keyboard_event = None
        page.bgcolor = None
        prontuario = e.control.data

        db = DbProntuarios()
        res = db.coletar({"id": prontuario})[0]

        limpar_tela()

        imput_cpf.value = res[1]
        imput_cpf.on_blur = cpf_on_blur

        imput_nome.value = res[2]
        imput_nome.on_blur = nome_on_blur

        imput_telefone.value = res[3]
        imput_telefone.on_blur = telefone_on_blur

        imput_nascimento.value = res[4]
        imput_nascimento.on_blur = nascimento_on_blur

        imput_sexo.value = res[5]
        imput_sexo.on_blur = sexo_on_change

        imput_peso.value = res[6]
        imput_peso.on_blur = peso_on_blur

        imput_sintomas.value = res[7]
        imput_sintomas.width = 500
        imput_sintomas.read_only = False
        imput_sintomas.min_lines = 5
        imput_sintomas.max_lines = 5
        imput_sintomas.on_blur = sintomas_on_blur

        imput_emergencia.value = res[8]

        coluna_a = ft.Column(
            controls=[
                imput_cpf,
                imput_nome,
                imput_telefone,
                imput_nascimento,
                imput_sexo,
                imput_peso,
                imput_sintomas,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        coluna_b = ft.Column(
            controls=[
                ft.Text("Tipo de atendimento:", size=20, weight="bold"),
                imput_emergencia,
                ft.Divider(height=450),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_main_content = ft.Row(
            [
                ft.VerticalDivider(width=9, thickness=3),
                coluna_a,
                ft.VerticalDivider(width=9, thickness=3),
                coluna_b,
                ft.VerticalDivider(width=9, thickness=3),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_btns = ft.Row(
            [
                ft.ElevatedButton("Sair", on_click=sair),
                ft.ElevatedButton(
                    "Voltar", on_click=tela_visualizar_prontuario, data=prontuario
                ),
                ft.ElevatedButton("Salvar", on_click=editar_prontuario, data=prontuario),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        page.add(
            ft.Text("Editar prontuário:", size=20, weight="bold"),
            ft.Divider(height=8),
            row_main_content,
            ft.Divider(height=8),
            row_btns,
        )

    def tela_visualizar_prontuario(e=None):
        """
        Chama tela de visualizar um prontuário
        """
        page.on_keyboard_event = None
        page.bgcolor = None
        
        try:
            inicio = e.control.title.value.index(" ") + 1
            fim = e.control.title.value.index(",")
            prontuario = int(e.control.title.value[inicio:fim])
        except AttributeError:
            prontuario = e.control.data

        db = DbProntuarios()
        res = db.coletar({"id": prontuario})[0]

        limpar_tela()

        btn_gerar_receita.on_click = gerar_pdf_receita
        btn_chamar_prontuario.on_click=chamar_prontuario
        imput_sintomas.read_only = True
        imput_sintomas.min_lines = 6
        imput_sintomas.max_lines = 6
        imput_sintomas.width = page.width - 50
        imput_sintomas.value = res[7]
        imput_observacoes.value = res[9]
        imput_exames.value = res[10]
        imput_diagnostico.value = res[11]
        imput_receita.value = res[12]

        # habilita ou não o botão de gerar a receita
        if imput_receita.value == None or imput_receita.value == "" or imput_nome_atendente.value == None or imput_nome_atendente.value == "":
            btn_gerar_receita.disabled = True
        else:
            btn_gerar_receita.disabled = False

        # habilita ou não o botão de chamada
        js = JsonFile()
        try:
            setor = js.ler('setor_atual')
            if setor == "":
                btn_chamar_prontuario.disabled = True
            else:
                btn_chamar_prontuario.disabled = False
        except (ArquivoConfigNaoEncontrado, VariavelConfigNaoEncontrada):
            btn_chamar_prontuario.disabled = True

        match res[8]:
            case "red":
                cor_de_fundo = ft.colors.RED
            case "orange":
                cor_de_fundo = ft.colors.ORANGE
            case "yellow":
                cor_de_fundo = ft.colors.YELLOW
            case "green":
                cor_de_fundo = ft.colors.GREEN

        text_cor_prontuario.value = res[8]
        container_numero_prontuario.value = text_cor_prontuario
        container_numero_prontuario.bgcolor = cor_de_fundo
        text_nome.value = f"Nome: {res[2]}"
        text_cpf.value = f"CPF: {res[1]},"
        text_data_nascimento.value = f"Data de nascimento: {res[4]}"
        text_sexo.value = f'Sexo: {"Masculino" if res[5] == "M" else "Feminino"},'
        text_peso.value = f"Peso: {res[6]}Kg"
        text_chegada.value = f"Chegada: {res[-2]}"
        text_ultimo_atendimento.value = f"Último atendimento: {res[-1]}"
        text_contato.value = f"Contato: {res[3]}"

        coluna_esquerda = ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text(f"Prontuário: "),
                        container_numero_prontuario,
                    ]
                ),
                text_nome,
                ft.Row(
                    [
                        text_cpf,
                        text_data_nascimento,
                    ]
                ),
                ft.Row(
                    [
                        text_sexo,
                        text_peso,
                    ]
                ),
                text_chegada,
                text_ultimo_atendimento,
                ft.Row(
                    [
                        text_contato,
                        btn_chamar_prontuario
                    ]
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        coluna_direita = ft.Column(
            controls=[imput_sintomas],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.END,
        )

        coluna_esquerda.expand = 3
        coluna_direita.expand = 7

        row_main = ft.Row(
            controls=[
                coluna_esquerda,
                coluna_direita,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        coluna_main = ft.Column(
            controls=[row_main],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        coluna_adicionais = ft.Column(
            controls=[
                imput_observacoes,
                imput_exames,
                imput_diagnostico,
                imput_receita,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_btns = ft.Row(
            controls=[
                ft.ElevatedButton("Sair", on_click=sair),
                ft.ElevatedButton("Voltar", on_click=tela_consultar_prontuarios),
                ft.ElevatedButton(
                    "Editar", on_click=tela_editar_prontuario, data=res[0]
                ),
                ft.ElevatedButton(
                    "Salvar", on_click=update_prontuario, data=prontuario
                ),
                btn_gerar_receita,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        page.add(
            coluna_main,
            ft.Divider(height=15),
            coluna_adicionais,
            ft.Divider(height=15),
            row_btns,
        )

    def tela_consultar_prontuarios(e=None):
        """
        Chama tela de pesquisar e filtrar prontuários
        """
        page.on_keyboard_event = None
        page.bgcolor = None
        limpar_tela()

        checkbox_vermelho.on_change = pesquisar_prontuario
        checkbox_laranja.on_change = pesquisar_prontuario
        checkbox_amarelo.on_change = pesquisar_prontuario
        checkbox_verde.on_change = pesquisar_prontuario
        imput_cpf_pesquisa.on_change = cpf_pesquisa_on_change
        imput_cpf_pesquisa.on_blur = cpf_pesquisa_on_blur
        switch_finalizados.value = False
        switch_finalizados.on_change = pesquisar_prontuario

        primeira_row = ft.Row(
            [
                ft.ElevatedButton("Sair", on_click=sair),
                ft.ElevatedButton("Voltar", on_click=tela_inicial),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        segunda_row = ft.Row(
            [ft.Text("Pesquisar prontuário")],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        terceira_row = ft.Row(
            [imput_id_pesquisa, imput_nome_pesquisa, imput_cpf_pesquisa],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        quarta_row = ft.Row(
            controls=(
                [
                    ft.ElevatedButton(
                        "Limpar pesquisa",
                        on_click=mostrar_todos_os_prontuarios_nao_finalizado,
                    ),
                    ft.VerticalDivider(width=9),
                    ft.ElevatedButton("Pesquisar", on_click=pesquisar_prontuario),
                ]
            ),
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        coluna_pesquisa = ft.Column(
            controls=[
                segunda_row,
                terceira_row,
                quarta_row,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        row_superior = ft.Row(
            controls=[
                primeira_row,
                coluna_pesquisa
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        row_filtros = ft.Row(
            controls=[
                filtro_emergencia,
                ft.VerticalDivider(width=9, thickness=3),
                switch_finalizados,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        coluna_principal = ft.Column(
            controls=[
                ft.Text("Prontuários", size=20, weight="bold"),
                ft.Divider(height=8),
                row_superior,
                ft.Divider(height=8, color='#1A1C1E'),
                row_filtros,
                ft.Divider(height=8),
                container_de_prontuarios,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        mostrar_todos_os_prontuarios_nao_finalizado()

        page.add(coluna_principal)

    def tela_chamada(e):
        """
        Chama tela de chamada
        """
        page.on_keyboard_event = voltar_para_chamar_pacientes
        page.bgcolor = "white"
        limpar_tela()
        page.add(coluna_chamada)
        jf = JsonFile()
        ch = Chamada()
        previous_mod_time = ""
        while coluna_chamada in page.controls:
            try:
                file = jf.ler("lista_de_chamada")
                if Path(file).exists():
                    current_mod_time = os.path.getmtime(file)
                    if current_mod_time != previous_mod_time:
                        previous_mod_time = current_mod_time
                        temp_list = ch.coletar_nomes_e_destinos()
                        gerar_tela_chamada(temp_list)
                        if temp_list:
                            engine = pyttsx3.init()
                            text = f"{temp_list[0][0]} compareça ao {temp_list[0][1]}"
                            engine.say(text)
                            engine.say(text)
                            engine.runAndWait()
                else:
                    gerar_tela_chamada()
            except (VariavelConfigNaoEncontrada, ArquivoConfigNaoEncontrado):
                gerar_tela_chamada()
            sleep(5)

    def tela_chamar_pacientes(e=None):
        """
        Chama tela de configurar chamada
        """
        page.on_keyboard_event = None
        page.bgcolor = None
        limpar_tela()
        preenche_campo_setores()
        gerar_opcoes_dropdown_excluir()
        imput_inserir_local.value = ""
        dropdown_menu_excluir.value = ""
        altura_divider = int(page.height*0.25)

        row_incluir_local = ft.Row(
            controls=[
                imput_inserir_local,
                ft.OutlinedButton("Inserir", on_click=inserir_novo_local),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_excluir_local = ft.Row(
            controls=[
                dropdown_menu_excluir,
                ft.OutlinedButton("Excluir", on_click=excluir_local),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        coluna_esquerda_interna = ft.Column(
            controls=[
                row_incluir_local,
                row_excluir_local,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        coluna_esquerda_externa = ft.Column(
            controls=[
                coluna_esquerda_interna,
                ft.Divider(height=15),
                ft.ElevatedButton("Abrir Tela de Chamada", on_click=tela_chamada),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        coluna_direita = ft.Column(
            controls=[
                ft.Text("Setores disponíveis", size=16, weight="bold"),
                coluna_de_locais,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_principal = ft.Row(
            controls=[coluna_esquerda_externa, coluna_direita],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_btns = ft.Row(
            controls=[
                ft.ElevatedButton("Sair", on_click=sair),
                ft.ElevatedButton("Voltar", on_click=tela_inicial),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        page.add(
            ft.Text("Chamada de prontuários", size=20, weight="bold"),
            ft.Divider(height=altura_divider),
            row_principal,
            ft.Divider(height=altura_divider),
            row_btns,
        )

    def tela_selecionar_db(e=None):
        """
        Chama tela de selecionar/criar db
        """
        page.on_keyboard_event = None
        page.bgcolor = None
        limpar_tela()

        altura_divider = int(page.height*0.28)

        selecionar_arquivo_ou_diretorio.on_result = resultado_selecao_arquivos

        page.overlay.append(selecionar_arquivo_ou_diretorio)

        page.add(
            ft.Row(
                controls=[
                    ft.Column(
                        [
                            ft.Divider(height=altura_divider),
                            ft.Text(
                                "Caso já exista um banco de dados, selecione-o no primeiro botão.",
                                size=20,
                                weight="bold",
                            ),
                            ft.ElevatedButton(
                                "Selecionar arquivo...",
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=tratamento_file_picker,
                            ),
                            ft.Divider(height=15),
                            ft.Text(
                                "Caso ainda não exista um banco de dados, selecione no segundo botão o diretório onde deseja criá-lo:",
                                size=20,
                                weight="bold",
                            ),
                            ft.ElevatedButton(
                                "Selecionar diretório...",
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=tratamento_file_picker,
                            ),
                            selected_files,
                            ft.Divider(height=altura_divider),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton("Sair", on_click=sair),
                                    ft.ElevatedButton(
                                        "Salvar", on_click=salvar_caminhos_dbs
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    def tela_inicial(e=None):
        """
        Chama tela inicial do programa
        """
        page.on_keyboard_event = None
        page.bgcolor = None
        limpar_tela()
        padding_calculado = int(page.width*0.012)
        padding_do_container = padding_calculado if padding_calculado >= 15 else 15

        preencher_identificacao()
        gerar_opcoes_dropdown_selecionar_setor()
        dropdown_menu_selecionar_setor.on_change = salvar_setor
        set_valor_inicial_menu_selecionar_setor()

        row_identificacao = ft.Row(
            controls=[
                imput_nome_atendente,
                imput_cargo_atendente,
                imput_contato_atendente,
                ft.ElevatedButton("Gravar", on_click=gravar_identificacao),
                ft.ElevatedButton("Limpar", on_click=limpar_identificacao),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        row_setor = ft.Row(
            controls=[
                dropdown_menu_selecionar_setor,
                ft.ElevatedButton('Limpar', on_click=limpar_setor)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        page.add(
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Selecione a opção desejada:", size=20, weight="bold"),
                                    ft.Divider(color='#1A1C1E'),
                                    ft.ElevatedButton(
                                        "Novos prontuários",
                                        on_click=tela_novos_prontuarios,
                                    ),
                                    ft.ElevatedButton(
                                        "Consultar prontuários",
                                        on_click=tela_consultar_prontuarios,
                                    ),
                                    ft.ElevatedButton(
                                        "Chamada de pacientes",
                                        on_click=tela_chamar_pacientes,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            border=ft.border.all(3, '#2E3136'),
                            padding=ft.padding.all(padding_do_container),
                            width=page.width,
                        ),
                        ft.Container(
                            content=ft.Column(
                            [
                                ft.Text('Identificação do atendente.', size=15, weight="bold"),
                                ft.Text('(Necessário apenas se o atendente for emitir receita.)', size=15),
                                ft.Divider(color='#1A1C1E'),
                                row_identificacao,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                            alignment=ft.alignment.center,
                            border=ft.border.all(3, '#2E3136'),
                            padding=ft.padding.all(padding_do_container),
                            width=page.width,
                        ),
                        ft.Container(
                            content=ft.Column(
                            [
                                ft.Text('Informe o setor de atendimento..', size=15, weight="bold"),
                                ft.Text('(Necessário apenas se precisar chamada o paciente ao setor informado.)', size=15),
                                ft.Divider(color='#1A1C1E'),
                                row_setor
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                            alignment=ft.alignment.center,
                            border=ft.border.all(3, '#2E3136'),
                            padding=ft.padding.all(padding_do_container),
                            width=page.width,
                        ),
                        ft.ElevatedButton("Sair", on_click=sair),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
        )

    def iniciar_programa():
        """
        Verifica se o arquivo config.json existe
        Se sim:
            Lê o arquivo em um dicionario e verifica se contém o caminho do db_prontuarios e se ele existe
            Se sim:
                Chama a tela inicial
            Se não:
                Chama a tela de selecionar/criar db
        Se não:
            Chama a tela de selecionar/criar db
        """
        caminho_executavel = Path(sys.executable).parent

        caminho_json = caminho_executavel / "config.json"
        if caminho_json.exists():
            with open(caminho_json) as f:
                dicionario = json.load(f)
            if (
                "caminho_db_prontuarios" in dicionario
                and Path(dicionario["caminho_db_prontuarios"]).exists()
            ):
                tela_inicial()
            else:
                tela_selecionar_db()
        else:
            tela_selecionar_db()

    # INICIAR
    iniciar_programa()


ft.app(target=main)
