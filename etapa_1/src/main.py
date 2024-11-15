#########################################
from classes import *
from utils.helpers import *
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
uiApp = __revit__  
uiDoc = uiApp.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document  # Obter o documento ativo
##########################################
##########################################

#VARIAVEIS GLOBAIS
# PARTE QUE OBTEM TODAS AS FAMILIAS DO ARQUIVO EM UM DICIONARIO
coletor = FilteredElementCollector(doc).OfClass(FamilySymbol)
coletor_instancias = FilteredElementCollector(doc).OfClass(FamilyInstance)
dict_coletor_doc = {}

contadorDuplicates=1 
''"PARA POSSIBILITAR A DUPLICACAO DURANTE A EXECUCAO DO APLICATIVO"''

categorias_excluir = {
    BuiltInCategory.OST_CableTray: None,
    BuiltInCategory.OST_Conduit: None,
    BuiltInCategory.OST_DuctSystem: None,
    BuiltInCategory.OST_FlexDuctCurves: None,
    BuiltInCategory.OST_Ceilings: None,
    BuiltInCategory.OST_StructuralFoundation: None,
    BuiltInCategory.OST_CurtainWallMullions: None,
    BuiltInCategory.OST_Walls: None,
    BuiltInCategory.OST_CurtainWallPanels: None,
    BuiltInCategory.OST_StructuralFraming: None,
    BuiltInCategory.OST_PipingSystem: None,
    BuiltInCategory.OST_GenericAnnotation: None,
    BuiltInCategory.OST_Roofs: None,
    BuiltInCategory.OST_Topography: None,
    BuiltInCategory.OST_PipeCurves: None,
    BuiltInCategory.OST_FlexPipeCurves: None
}

categorias_excluir_dic_ids = {int(excluir) for excluir in categorias_excluir}




try:
    for symb in coletor:
        family_name = symb.Family.Name
        print(family_name) 
        categoria = symb.Category
        objGeometry=None
        if categoria.Id.IntegerValue not in categorias_excluir_dic_ids:
            
                # Usa a primeira instância para coletar a geometria
            geometry_options = Options()
            geometry = symb.get_Geometry(geometry_options)
            print(family_name)    
            if geometry:
                objGeometry = pegarGeometry(geometry)        
            
            if family_name not in dict_coletor_doc:
                    dict_coletor_doc[family_name] = {}
                    if  objGeometry is None:
                        dict_coletor_doc[family_name]["NoGeometria"]=[Coletor(symb, family_name)]
                    else:
                        geometry_chave = str(objGeometry.area) + str(objGeometry.volume) + str(objGeometry.altura)+str(objGeometry.largura)+str(objGeometry.profundidade)
                        dict_coletor_doc[family_name][geometry_chave] = [Coletor(symb, family_name)]
                    
            else:
                if  objGeometry is None:
                    if "NoGeometria" not in dict_coletor_doc[family_name]:
                        dict_coletor_doc[family_name]["NoGeometria"]=[Coletor(symb, family_name)]
                    else:
                        dict_coletor_doc[family_name]["NoGeometria"].append(Coletor(symb, family_name))
                
                else:
                    geometry_chave = str(objGeometry.area) + str(objGeometry.volume) + str(objGeometry.altura)+str(objGeometry.largura)+str(objGeometry.profundidade)
                    
                    if geometry_chave in dict_coletor_doc[family_name]:
                        dict_coletor_doc[family_name][geometry_chave].append(Coletor(symb, family_name))
                    else:
                        dict_coletor_doc[family_name][geometry_chave] = [Coletor(symb, family_name)]
                
                
                
                   
            
    # Imprime o último valor do dicionário após a coleta
    if dict_coletor_doc:
        print(dict_coletor_doc)
    else:
        print("Dicionário está vazio.")

except Exception as e:
    print(e)
    
    
form = MenuForm()
Application.Run(form)
