import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import *

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

# Criar o coletor de símbolos de famílias (FamilySymbol)
coletor = FilteredElementCollector(doc).OfClass(FamilySymbol)

'''Dicionario com as categorias que quero excluir e encontrar seus IDS'''
categorias_excluir = {
    BuiltInCategory.OST_CableTray :None,
    BuiltInCategory.OST_Conduit:None,
    BuiltInCategory.OST_DuctSystem:None,
    BuiltInCategory.OST_FlexDuctCurves:None,
    BuiltInCategory.OST_Ceilings:None,
    BuiltInCategory.OST_StructuralFoundation:None,
    BuiltInCategory.OST_CurtainWallMullions:None,
    BuiltInCategory.OST_Walls:None,
    BuiltInCategory.OST_CurtainWallPanels:None,
    BuiltInCategory.OST_StructuralFraming:None,
    BuiltInCategory.OST_DuctSystem:None,
    BuiltInCategory.OST_PipingSystem:None,
    BuiltInCategory.OST_GenericAnnotation:None,
    BuiltInCategory.OST_Roofs:None,
    BuiltInCategory.OST_Topography:None,
    BuiltInCategory.OST_PipeCurves:None,
    BuiltInCategory.OST_FlexPipeCurves:None
}

categorias_excluir_dic_ids = {int(excluir) for excluir in categorias_excluir} 
'''Dicionario com as categorias que quero excluir com as chaves sendos seus IDS'''

# Dicionário para armazenar as famílias que são consideradas "blocks"
dict_familias_blocks = {}

# Filtrar e remover famílias de categorias indesejadas
for symb in coletor:
    family_name = symb.Family.Name  # Nome da família
    categoria = symb.Category
    
    # Verificar se a categoria da família não está no dicionário de exclusão
    if categoria.Id.IntegerValue not in categorias_excluir_dic_ids:
        # Se a família não estiver no dicionário, adicionar
        if family_name not in dict_familias_blocks:
            dict_familias_blocks[family_name] = [symb]
        else:
            dict_familias_blocks[family_name].append(symb)

# Exibir o dicionário filtrado
for nome_familia, coletores in dict_familias_blocks.items():
    print(nome_familia,len(coletores))
