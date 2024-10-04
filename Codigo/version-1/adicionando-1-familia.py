import clr
clr.AddReference('RevitAPI')  # Referência à API do Revit
clr.AddReference('RevitAPIUI')  # Referência à API da interface de usuário do Revit

from Autodesk.Revit.DB import *  # Importa todas as classes principais da DB API
from Autodesk.Revit.UI import *  # Importa todas as classes de interface de usuário


#########################################

app = __revit__.Application  # Obter a aplicação Revit ativa
doc = __revit__.ActiveUIDocument.Document  # Obter o documento ativo

#############################################

try:
    # iniciar transação
    transacao = Transaction(doc, "Carregar Família")
    transacao.Start()  # Inicia a transação

    # Carergando a familia e verificando se foi carregado com sucesso e pegando o objeto da familia
    family_path = r"C:\Users\allys\OneDrive\Área de Trabalho\Projeto Revit\familias\privada.rfa"  # Caminho do arquivo da família
    family_loaded = clr.Reference[Family]()  # Referência para armazenar a família carregada
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