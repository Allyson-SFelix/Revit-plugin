#########################################
#este código está carregando o arquivo da familia que está no PC e depois guardando em um objeto (nome,categoria,lista de symbols)
#com esse código vou conseguir obter os itens necessários para fazer as verificações e saber se há ou não essa familia no projeto
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
#############################################
def pegarParametros(arquivo):## recebo a lista de SymbolID´s
    #variaveis que irei guardar:nome,categoria,lista de simbolos
    categoriaArquivo=arquivo.Name
    nomeArquivo=arquivo.FamilyCategory.Name
    listaSimboloArquivo = [doc.GetElement(symbol_id) for symbol_id in arquivo.GetFamilySymbolIds()]
    parametro = Parametro(nomeArquivo,categoriaArquivo,listaSimboloArquivo)
    return parametro

class Parametro:
        def __init__(self,nome,categoria,listaSimbolos):
            self.nome=nome
            self.categoria=categoria
            self.listaSimbolos=listaSimbolos

try:
    # Inicia transacao
    transacao = Transaction(doc, "Carregar Família")
    transacao.Start() 

    #Carrega arquivo
    family_path = r"C:\Users\allys\OneDrive\Área de Trabalho\Projeto Revit\familias\Paisagismo_BancoDePraça_Madeira_Vitrine.rfa" 
    family_loaded = clr.Reference[Family]()  
    
    #verifica carregamento de arquivo (True ou False)
    if doc.LoadFamily(family_path, family_loaded):
        #pego o objeto do arquivo
        family_loaded = family_loaded.Value  
        
        #carrego em um objeto os parametros
        parametros = pegarParametros(family_loaded)
        
        #mostro a categoria e nome no terminal
        print(parametros.categoria)
        print(parametros.nome)
        for simb in parametros.listaSimbolos:
            print(simb)
    
    else:
        print("Erro ao carregar a família.")

    transacao.Commit()
    
except Exception as e:
    print(e)
    
finally:
    if transacao.HasStarted():
        transacao.RollBack()