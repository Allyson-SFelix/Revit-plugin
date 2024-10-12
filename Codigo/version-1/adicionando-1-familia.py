import clr
clr.AddReference('RevitAPI')  # Referência à API do Revit
clr.AddReference('RevitAPIUI')  # Referência à API da interface de usuário do Revit

from Autodesk.Revit.DB import *  # Importa todas as classes principais da DB API
from Autodesk.Revit.UI import *  # Importa todas as classes de interface de usuário


#########################################

app = __revit__.Application  # Obter a aplicação Revit ativa
doc = __revit__.ActiveUIDocument.Document  # Obter o documento ativo

#############################################
class Parametro:
        def __init__(self,listTextura,listaCores):
            self.texturas=listTextura
            self.cores=listaCores

       
def pegarParametros(family_symbols):
    listTextura=[]
    listColors=[]
    for symbol_id in family_symbols:
        symbol = doc.GetElement(symbol_id)  # Obter o FamilySymbol
        symbol_name = symbol.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()

        material_param = symbol.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM)
            
        if material_param:
            material_id = material_param.AsElementId()
            material = doc.GetElement(material_id)  # Obter o material associado
                
            if isinstance(material, Material):
                listColors.append(material.Color)
                asset = material.AppearanceAssetId
                if asset != ElementId.InvalidElementId:
                    appearance_asset = doc.GetElement(asset)
                    
                    if isinstance(appearance_asset, AppearanceAssetElement):
                        texture_property = appearance_asset.GetRenderingAsset().FindByName("generic_diffuse")
                        if texture_property and texture_property.IsValid:
                            listTextura.append(texture_property.Value)

    parametro=Parametro(listTextura,listColors)
    return parametro

try:
    # iniciar transação
    transacao = Transaction(doc, "Carregar Família")
    transacao.Start()  # Inicia a transação

    # Carergando a familia e verificando se foi carregado com sucesso e pegando o objeto da familia
    family_path = r"C:\Users\allys\OneDrive\Área de Trabalho\Projeto Revit\familias\privada.rfa"  # Caminho do arquivo da família
    family_loaded = clr.Reference[Family]()  # Referência para armazenar a família carregada
    family_symbols = list(family_loaded.GetFamilySymbolIds())
    parametros=Parametro(None,None)
    parametros=pegarParametros(family_symbols)
    print(parametros.texturas+"\n"+parametros.cores)
    
    
    verifica = doc.LoadFamily(family_path, family_loaded)  #Carrega a família
    
    
    if verifica:
        family_loaded = family_loaded.Value  # Acessa o objeto da família carregada
       
        # Obtem os Ids que representa cada simbolo da familia carregada, tranformo em lista e gero a familia que quero
        family_symbol_ids = family_loaded.GetFamilySymbolIds()  # Obtem os Ids que representa cada simbolo da familia carregada
        first_symbol_id = list(family_symbol_ids)[0]  # Cria uma lista com esses ids e acessa o primeiro símbolo
        symbolFamilia = doc.GetElement(first_symbol_id)  # Pego esse primeiro simbolo e transformo em familia
        
        # verifico se a familia que gerei está ativada e o ativo
        if not symbolFamilia.IsActive:
            symbolFamilia.Activate()  # Ativa o símbolo se estiver desativado

        # Crio uma localizacao e inicializo uma instancia para essa familia
        localizacaoDeInsercao = XYZ(0, 0, 0)  # Define o ponto de inserção
        familiaInstancia = doc.Create.NewFamilyInstance(
        localizacaoDeInsercao, symbolFamilia, Structure.StructuralType.NonStructural) #inicializa a instancia (posicao,familia,...)

        
    else:
        print("erro ao carregar familia")
    
    #
    
    transacao.Commit()
    
except Exception as e:
    print(e)
    
finally:
    if transacao.HasStarted():
        transacao.RollBack()
        
        
        
 