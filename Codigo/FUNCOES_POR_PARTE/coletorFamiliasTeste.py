import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

uiApp = __revit__  
uiDoc = uiApp.ActiveUIDocument
docs = uiDoc.Document

coletor = FilteredElementCollector(doc).OfClass(FamilySymbol)
dict_coletor_doc = {}

class Coletor:
    def __init__(self, symbColetor, nomeFamilia, categoria):
        self.objetoFamilia = symbColetor
        self.nomeFamilia = nomeFamilia
        self.categoria = categoria

class Geometry:
    def __init__(self, area=None, volume=None, proporcao=None):
        self.area = area
        self.volume = volume
        self.proporcao = proporcao

    def __eq__(self, other):
        return (self.volume == other.volume and
                self.proporcao == other.proporcao)

    def __hash__(self):
        return hash((self.area, self.volume, self.proporcao))


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

    for geo_obj in geometry:
        if isinstance(geo_obj, Solid):
            total_volume += geo_obj.Volume
            box = geo_obj.GetBoundingBox()
            altura = box.Max.Z - box.Min.Z
            largura = box.Max.X - box.Min.X
            profundidade = box.Max.Y - box.Min.Y
            
            if largura > 0 and profundidade > 0:
                proporcao = altura / max(largura, profundidade)

            for face in geo_obj.Faces:
                total_area += face.Area
        elif isinstance(geo_obj, Curve):
            comprimentoCurva = geo_obj.Length

    return Geometry(total_area, total_volume, proporcao)

try:
    for symb in coletor:
        family_name = symb.Family.Name
        categoria = symb.Category
        
        if categoria.Id.IntegerValue not in categorias_excluir_dic_ids:
            geometry_options = Options()
            geometry = symb.get_Geometry(geometry_options)

            if geometry:
                objGeometry = pegarGeometry(geometry)
            else:
                objGeometry=Geometry()

            if family_name not in dict_coletor_doc:
                dict_coletor_doc[family_name] = {}
            else:
                if objGeometry in dict_coletor_doc[family_name]:
                    dict_coletor_doc[family_name][objGeometry].append(Coletor(symb, family_name, categoria))
                else:
                    dict_coletor_doc[family_name][objGeometry] = [Coletor(symb, family_name, categoria)]

    # Imprime o último valor do dicionário após a coleta
    if dict_coletor_doc:
        print(dict_coletor_doc)
    else:
        print("Dicionário está vazio.")

except Exception as e:
    print(e)
