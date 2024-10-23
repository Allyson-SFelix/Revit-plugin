#########################################
# este programa pega todas as FamilySymbol e coloca em um dicicionario para facilitar a verificação
# Lógica : DICT_COLETOR[Familia_nome] -> DICT_GEOMETRIA[concatenação da altura,volume e proporcao] -> lista_familias[objFamilia(symb,nome,categoria)]
#########################################
import clr
clr.AddReference('RevitAPI')  # Referência à API do Revit
clr.AddReference('RevitAPIUI')  # Referência à API da interface de usuário do Revit
#########################################
from Autodesk.Revit.DB import *  # Importa todas as classes principais da DB API
from Autodesk.Revit.UI import *  # Importa todas as classes de interface de usuário
#########################################
app = __revit__.Application  # Obter a aplicação Revit ativa
doc = __revit__.ActiveUIDocument.Document  # Obter o documento ativo

uiApp = __revit__  
uiDoc = uiApp.ActiveUIDocument
docs = uiDoc.Document

coletor = FilteredElementCollector(doc).OfClass(FamilySymbol)
coletor_instancias = FilteredElementCollector(doc).OfClass(FamilyInstance)
dict_coletor_doc = {}

class Coletor:
    def __init__(self, symbColetor, nomeFamilia, categoria):
        self.objetoFamilia = symbColetor
        self.nomeFamilia = nomeFamilia
        self.categoria = categoria

class Geometry:
    def __init__(self, area=None, volume=None, altura=None,largura=None,profundidade=None):
        self.area = area
        self.volume = volume
        self.altura=altura
        self.largura=largura
        self.profundidade=profundidade

    def __eq__(self, other):
        return (self.area == other.area and 
                self.volume == other.volume and
                self.altura == other.altura and
                self.largura ==other.largura and
                self.profundidade ==other.profundidade)

    def __hash__(self):
        return hash((self.area, self.volume, self.altura,self.largura,self.profundidade))


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

def pegarGeometry(geometry):

    total_area = 0
    total_volume = 0
    proporcao = 0  # Inicializa proporção
    largura = altura = profundidade = 0  # Inicializa os valores de largura, altura e profundidade

    for geo_obj in geometry:
        if isinstance(geo_obj, Solid):
            total_volume += geo_obj.Volume
            box = geo_obj.GetBoundingBox()
            altura = box.Max.Z - box.Min.Z
            largura = box.Max.X - box.Min.X
            profundidade = box.Max.Y - box.Min.Y

            for face in geo_obj.Faces:
                total_area += face.Area
        
        if largura == 0 and altura == 0 and profundidade == 0:
            return None  # Se todas as dimensões forem zero, trata como sem geometria
        
        print(largura,altura,profundidade,total_area,total_volume)
        return Geometry(total_area, total_volume, altura,largura,profundidade)
    else:
        return None
try:
    for symb in coletor:
        family_name = symb.Family.Name
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
                        dict_coletor_doc[family_name]["NoGeometria"]=[Coletor(symb, family_name, categoria)]
                    else:
                        geometry_chave = str(objGeometry.area) + str(objGeometry.volume) + str(objGeometry.altura)+str(objGeometry.largura)+str(objGeometry.profundidade)
                        dict_coletor_doc[family_name][geometry_chave] = [Coletor(symb, family_name, categoria)]
                    
            else:
                if  objGeometry is None:
                    if "NoGeometria" not in dict_coletor_doc[family_name]:
                        dict_coletor_doc[family_name]["NoGeometria"]=[Coletor(symb, family_name, categoria)]
                    else:
                        dict_coletor_doc[family_name]["NoGeometria"].append(Coletor(symb, family_name, categoria))
                
                else:
                    geometry_chave = str(objGeometry.area) + str(objGeometry.volume) + str(objGeometry.proporcao)
                    
                    if geometry_chave in dict_coletor_doc[family_name]:
                        dict_coletor_doc[family_name][geometry_chave].append(Coletor(symb, family_name, categoria))
                    else:
                        dict_coletor_doc[family_name][geometry_chave] = [Coletor(symb, family_name, categoria)]
                
                
                
                   
            
    # Imprime o último valor do dicionário após a coleta
    if dict_coletor_doc:
        print(dict_coletor_doc)
    else:
        print("Dicionário está vazio.")

except Exception as e:
    print(e)
