import clr
clr.AddReference('RevitAPI')  # Referência à API do Revit
clr.AddReference('RevitAPIUI')  # Referência à API da interface de usuário do Revit

from Autodesk.Revit.DB import *  # Importa todas as classes principais da DB API
from Autodesk.Revit.UI import *  # Importa todas as classes de interface de usuário

# Inicializando o dicionário que armazenará os FamilySymbols
dict_coletor_doc = {}

app = __revit__.Application  
doc = __revit__.ActiveUIDocument.Document  

coletor = FilteredElementCollector(doc)
symbColetor = coletor.OfClass(FamilySymbol)  

for symb in symbColetor:
    family_name = symb.Family.Name  # Nome da Família
    symbol_name = symb.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()  # Nome do símbolo
    
    dict_coletor_doc[family_name+"-"+symbol_name] = symb  # Adiciona o FamilySymbol ao dicionário

print(dict_coletor_doc)
