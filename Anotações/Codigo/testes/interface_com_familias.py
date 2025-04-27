#########################################
# este programa pega todas as FamilySymbol e coloca em um dicicionario para facilitar a verificação
#########################################
import clr
clr.AddReference('RevitAPI')  # Referência à API do Revit
clr.AddReference('RevitAPIUI')  # Referência à API da interface de usuário do Revit

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

#########################################
from Autodesk.Revit.DB import *  # Importa todas as classes principais da DB API
from Autodesk.Revit.UI import *  # Importa todas as classes de interface de usuário
from System.Windows.Forms import Application, Form, Button, MessageBox
from System.Drawing import Point, Size
#########################################
app = __revit__.Application  # Obter a aplicação Revit ativa
doc = __revit__.ActiveUIDocument.Document  # Obter o documento ativo
##########################################
##########################################

# PARTE QUE OBTEM TODAS AS FAMILIAS DO ARQUIVO EM UM DICIONARIO
dict_coletor_doc = {}
coletor = FilteredElementCollector(doc)
symbColetor = coletor.OfClass(FamilySymbol)  

class Coletor:
    def __init__(self,symbColetor,nomeFamilia,categoria):
        self.objetoFamilia=symbColetor
        self.nomeFamilia=nomeFamilia
        self.categoria=categoria

for symb in symbColetor:
    family_name = symb.Family.Name  # Nome da Família
    symbol_name = symb.Family.FamilyCategory.Name   # Nome do símbolo
    novaInstanciaColetor=Coletor(symb,family_name,symbol_name)
    dict_coletor_doc[symb] = novaInstanciaColetor  # Adiciona o FamilySymbol ao dicionário

print(dict_coletor_doc)
##########################################
##########################################

#PARTE DE INTERFACE 
# Funções para as opções
def opcao1(sender, event):
    MessageBox.Show("Você escolheu a Opção 1", "Opção 1")

def opcao2(sender, event):
    MessageBox.Show("Você escolheu a Opção 2", "Opção 2")

def opcao3(sender, event):
    MessageBox.Show("Você escolheu a Opção 3", "Opção 3")

# Criar a janela principal
class MenuForm(Form):
    def __init__(self):
        self.Text = "Menu de Opções"
        self.Size = Size(800, 600)
        
        # Botão Opção 1
        botao1 = Button()
        botao1.Text = "Opção 1"
        botao1.Size = Size(100, 40)
        botao1.Location = Point(100, 30)
        botao1.Click += opcao1
        self.Controls.Add(botao1)

        # Botão Opção 2
        botao2 = Button()
        botao2.Text = "Opção 2"
        botao2.Size = Size(100, 40)
        botao2.Location = Point(100, 80)
        botao2.Click += opcao2
        self.Controls.Add(botao2)

        # Botão Opção 3
        botao3 = Button()
        botao3.Text = "Opção 3"
        botao3.Size = Size(100, 40)
        botao3.Location = Point(100, 130)
        botao3.Click += opcao3
        self.Controls.Add(botao3)

# Iniciar o aplicativo
form = MenuForm()
Application.Run(form)
