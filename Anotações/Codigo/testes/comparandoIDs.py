import clr
clr.AddReference('RevitAPI')  # Referência à API do Revit
clr.AddReference('RevitAPIUI')  # Referência à API da interface de usuário do Revit
#########################################
from Autodesk.Revit.DB import *  # Importa todas as classes principais da DB API
from Autodesk.Revit.UI import *  # Importa todas as classes de interface de usuário
#########################################
app = __revit__.Application  # Obter a aplicação Revit ativa
doc = __revit__.ActiveUIDocument.Document  # Obter o documento ativo
#############################################
try:
    transacao = Transaction(doc, "Carregar Família")
    transacao.Start()

    # Carregar o arquivo da família
    family_path = r"C:\Users\allys\OneDrive\Área de Trabalho\Projeto Revit\familias\Paisagismo_BancoDePraça_Madeira_Vitrine.rfa"
    family_loaded = clr.Reference[Family]()

    # Carregar a família
    if not doc.LoadFamily(family_path, family_loaded):
        print("Falha ao carregar a família.")
    else:
        # Obter os IDs dos FamilySymbols da nova família carregada
        new_family_symbols_ids = family_loaded.GetFamilySymbolIds()

        # Criar um conjunto para armazenar os IDs dos FamilySymbols existentes
        existing_symbols_ids = set()

        # Iterar sobre as famílias já carregadas no projeto
        for family in FilteredElementCollector(doc).OfClass(Family):
            for symbol_id in family.GetFamilySymbolIds():
                existing_symbols_ids.add(symbol_id)

        # Comparar os IDs
        for new_symbol_id in new_family_symbols_ids:
            if new_symbol_id in existing_symbols_ids:
                print("O símbolo já existe no projeto:", new_symbol_id)
            else:
                print("O símbolo é novo e pode ser adicionado:", new_symbol_id)

# Finalizar a transação
    transacao.Commit()
except Exception as e:
    print(e)
    
finally:
    if transacao.HasStarted():
        transacao.RollBack()