from pathlib import Path
from subprocess import Popen
import sys
from tempfile import NamedTemporaryFile

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class GerarPDF:
    # imagem = r"C:\Users\lbsme\Documents\GitHub\prontuario_medico\bastao_de_asclepio.bmp"
    caminho_executavel = Path(sys.executable).parent
    imagem = str(caminho_executavel / "bastao_de_asclepio.bmp")
    altura_máxima_A4 = 842
    largura_máxima_A4 = 595
    altura_imagem = 278
    largura_imagem = 80

    def gerar_receita(self, dicionario):
        """
        Recebe dicionario
        Instancia arquivo temporário com sufixo .pdf
        Gera pdf contendo informações no dicionario
        Salva e abre o pdf
        """
        with NamedTemporaryFile(suffix='.pdf', delete=False) as tf:
            cnv = canvas.Canvas(tf.name, pagesize=A4)

            cnv.drawInlineImage(self.imagem, 0, self.altura_máxima_A4-self.altura_imagem)

            meio_da_imagem = self.altura_máxima_A4-(self.altura_imagem/2)
            cnv.drawString(self.largura_imagem+20, meio_da_imagem+10, dicionario["nome_medico"])
            cnv.drawString(self.largura_imagem+20, meio_da_imagem-10, dicionario["cargo_medico"])

            posicao_texto = self.altura_máxima_A4-self.altura_imagem-20
            for texto in dicionario["receituario"].split('\n'):
                cnv.drawCentredString(
                    self.largura_máxima_A4/2,
                    posicao_texto,
                    texto
                )
                posicao_texto -= 20

            temp_list = dicionario["contatos"]
            temp_list.reverse()
            base = 15
            for contato in dicionario["contatos"]:
                cnv.drawString(40, base, contato)
                base += 15
            cnv.drawString(20, base, 'Contato:')

            cnv.save()
        Popen(["start", "/MAX", tf.name], shell=True)
