#########################################
# este programa pega todas as FamilySymbol e coloca em um dicicionario para facilitar a verificação
# NAO ESTA CERTO A LOGICA
# FUNCOES REDUNDANTES DEVIDO A VERIFICAÇÃO SE EXISTE SENDO QUE LOADED JA RETORNA TRUE SENDO EXATAMENTE ESSA VERIFICACAO
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
##########################################
dict_coletor_doc = {}
coletor = FilteredElementCollector(doc)
symbColetor = coletor.OfClass(FamilySymbol)  


def pegarParametros(arquivo,arquivoLoaded):## recebo a lista de SymbolID´s
    if arquivo is None:
        print("Arquivo está None")
        return None
    
    #variaveis que irei guardar:nome,categoria,lista de simbolos
    categoriaArquivo=arquivo.Name
    nomeArquivo=arquivo.FamilyCategory.Name
    listaSimboloArquivo = [doc.GetElement(symbol_id) for symbol_id in arquivo.GetFamilySymbolIds()]
    parametro = Parametro(nomeArquivo,categoriaArquivo,listaSimboloArquivo,arquivoLoaded)
    return parametro

class Parametro:
        def __init__(self,nomes,categorias,listaSimbolos,loadArquivo):
            self.nome=nomes
            self.categoria=categorias
            self.listaSimb=listaSimbolos
            self.arquivoLoad=loadArquivo

class Coletor:
    def __init__(self,symbColetor,nomeFamilia,categoria):
        self.objetoFamilia=symbColetor
        self.nomeFamilia=nomeFamilia
        self.categoria=categoria

for symb in symbColetor:
    family_name = symb.Family.Name  # Nome da Família
    symbol_name = symb.Family.FamilyCategory.Name   # Nome do símbolo
    novaInstanciaColetor=Coletor(symb,family_name,symbol_name)
    dict_coletor_doc[symb] = novaInstanciaColetor  # Adiciona o FamilySymbol ao dicionário

print(dict_coletor_doc)

def compararFamilias(arquivo, dicionario):
    # pegando nomes e categorias
    nome_familiaArquivo = arquivo.categoria
    nome_familiaDicionario = [familia.nomeFamilia for familia in dicionario.values()] #em cada local do dicionario quero .Name
    
    
    simbolos_arquivo = arquivo.nome
    simbolos_dicionario = [categorias.categoria for categorias in dicionario.values()] #em cada local do dicionario quero categoria    
    
    if compararNomes(nome_familiaDicionario,nome_familiaArquivo) and compararCategorias(simbolos_dicionario,simbolos_arquivo):
            print("iguais")
            return True
    print("diferentes")
    return False
    
    # Comparar categorias das famílias
    # Comparar símbolos (FamilySymbol)

def compararCategorias(listCategoria,categoriaArquivo):
    for categoria in listCategoria:
        if categoria == categoriaArquivo:
            return False

def compararNomes(listDic,arquivoNome):
    for nomeDic in listDic:
        if nomeDic == arquivoNome:
            print(nomeDic+""+arquivoNome)
            return True
    return False

def colocarFamilia(arquivoFamilia):
    family_symbol_ids = arquivoFamilia.GetFamilySymbolIds()  # Obtem os Ids que representa cada simbolo da familia carregada
    first_symbol_id = list(family_symbol_ids)[0]  # Cria uma lista com esses ids e acessa o primeiro símbolo
    symbolFamilia = doc.GetElement(first_symbol_id)  # Pego esse primeiro simbolo e transformo em familia
        
    # verifico se a familia que gerei está ativada e o ativo
    if not symbolFamilia.IsActive:
            symbolFamilia.Activate()  # Ativa o símbolo se estiver desativado

    # Crio uma localizacao e inicializo uma instancia para essa familia
    try:
        localizacaoDeInsercao = uiDoc.Selection.PickPoint("Clique para selecionar o ponto de inserção da família")
    except Exception as e:
        print(e)
        return

    familiaInstancia = doc.Create.NewFamilyInstance(
    localizacaoDeInsercao, symbolFamilia, Structure.StructuralType.NonStructural) #inicializa a instancia (posicao,familia,...)


try:
    # Inicia transacao
    transacao = Transaction(doc, "Carregar Família")
    transacao.Start() 

    #Carrega arquivo
    family_path = r"C:\Program Files\Projeto Revit\familias\Mobiliario_Aparador_Azul_Vitrine.rfa"
    family_loaded = clr.Reference[Family]()  
    arquivoFamilia_loaded=family_loaded
    #verifica carregamento de arquivo (True ou False)
    if doc.LoadFamily(family_path, family_loaded):
        #pego o objeto do arquivo
        family_loaded = family_loaded.Value  
        
        #carrego em um objeto os parametros
        parametros = pegarParametros(family_loaded,arquivoFamilia_loaded)
        
        #mostro a categoria e nome no terminal
        print(parametros.categoria)
        print(parametros.nome)
        print(parametros.listaSimb)

        if not compararFamilias(parametros,dict_coletor_doc):
            colocarFamilia(parametros.arquivoLoad)
    else:
        family_symbol_ids = family_loaded.GetFamilySymbolIds()  # Obtem os Ids que representa cada simbolo da familia carregada
        first_symbol_id = list(family_symbol_ids)[0]  # Cria uma lista com esses ids e acessa o primeiro símbolo
        symbolFamilia = doc.GetElement(first_symbol_id)  # Pego esse primeiro simbolo e transformo em familia
     
        symbolFamilia=list(dict_coletor_doc)[0]
        localizacaoDeInsercao = XYZ(0, 0, 0)  # Define o ponto de inserção
        familiaInstancia = doc.Create.NewFamilyInstance(
        localizacaoDeInsercao, symbolFamilia, Structure.StructuralType.NonStructural) #inicializa a instancia (posicao,familia,...)

    transacao.Commit()
    
except Exception as e:
    print(e)
    
finally:
    if transacao.HasStarted():
        transacao.RollBack()