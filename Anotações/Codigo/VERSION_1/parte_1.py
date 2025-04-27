import clr
clr.AddReference('RevitAPI')  # Referência à API do Revit
clr.AddReference('RevitAPIUI')  # Referência à API da interface de usuário do Revit
#########################################
from Autodesk.Revit.DB import *  # Importa todas as classes principais da DB API
from Autodesk.Revit.UI import *  # Importa todas as classes de interface de usuário
#########################################
app = __revit__.Application  # Obter a aplicação Revit ativa
doc = __revit__.ActiveUIDocument.Document  # Obter o documento ativo
##########################################
#OBJETOS
class Coletor:
    def __init__(self,symbColetor,nomeFamilia,categoria):
        self.objetoFamilia=symbColetor
        self.nomeFamilia=nomeFamilia
        self.categoria=categoria
##########################################
#VARIAVEIS GLOBAIS
dict_coletor_doc = {}
coletor = FilteredElementCollector(doc)
symbColetor = coletor.OfClass(FamilySymbol)  
##########################################
#FUNÇÕES
def preencherColetor(symbColetor,dict_coletor_doc):
    for symb in symbColetor:
        family_name = symb.Family.Name  # Nome da Família
        symbol_name = symb.Family.FamilyCategory.Name   # Nome do símbolo
        novaInstanciaColetor=Coletor(symb,family_name,symbol_name)
        symbHash=symb.GetHashCode()
        if dict_coletor_doc[symbHash] is 
        dict_coletor_doc[symbHash] = novaInstanciaColetor  # Adiciona o FamilySymbol ao dicionário

    return dict_coletor_doc
##########################################
#LINHAS EXECUTAVEIS
dict_coletor_doc=preencherColetor(symbColetor,dict_coletor_doc)
print(dict_coletor_doc)
    