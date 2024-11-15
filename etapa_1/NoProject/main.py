#########################################
# este programa pega todas as FamilySymbol e coloca em um dicicionario para facilitar a verificação
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



#PARTE FUNCOES

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
    
def criarHashGeomtry(area_total,volume_total,altura,largura,profundidade):
    return str(area_total) + str(volume_total) + str(altura)+str(largura)+str(profundidade)

def familiaInDict(nomeFamilia):
    return nomeFamilia in dict_coletor_doc

def geometriaInDictFamilia(hashGeometry,nomeFamilia):
    return hashGeometry in dict_coletor_doc[nomeFamilia]

def criarNovaInstacia(symb,altura,largura,profundidade):
    family_symbol = symb

    # Ativar o símbolo, se necessário
    if not family_symbol.IsActive:
        with Transaction(doc, "Ativar Family Symbol") as transacao:
            transacao.Start()
            family_symbol.Activate()
            transacao.Commit()
            
    # Define a localização e cria a nova instância
    try:
        localizacaoDeInsercao = uiDoc.Selection.PickPoint("Clique para selecionar o ponto de inserção da família")
    except Exception as e:
        print(e)
        return
    
    with Transaction(doc, "Criar Nova Instância") as transacao:
        transacao.Start()
        instance = doc.Create.NewFamilyInstance(localizacaoDeInsercao, family_symbol, Structure.StructuralType.NonStructural)
        
        altura_param = instance.LookupParameter("Altura")
        if altura_param:
            altura_param.Set(altura)
        
        largura_param = instance.LookupParameter("Largura")
        if largura_param:
            largura_param.Set(largura)
        
        profundidade_param = instance.LookupParameter("Profundidade")
        if profundidade_param:
            profundidade_param.Set(profundidade)
        
        transacao.Commit()
        
        return instance
    return False
       
def pegarSymbolArquivo(arquivoFamilia):
    family_symbol_ids = arquivoFamilia.GetFamilySymbolIds()  # Obtem os Ids que representa cada simbolo da familia carregada
    first_symbol_id = list(family_symbol_ids)[0]  # Cria uma lista com esses ids e acessa o primeiro símbolo
    return doc.GetElement(first_symbol_id) 
     
def colocarNovaFamilia(arquivoFamilia):
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
    return familiaInstancia

def salvarDictGeral(coletor,dict_coletor_doc):
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
       



# CLASS
class FamiliaInformacao:
    def __init__(self,symb,nomeFamilia,geometriaHash,arquivoLoad):
        self.symb=symb
        self.nomeFamilia=nomeFamilia
        self.geometriaHash=geometriaHash
        self.arquivoLoad=arquivoLoad
class Coletor:
    def __init__(self, objetoFamilia, nomeFamilia):
        self.objetoFamilia = objetoFamilia
        self.nomeFamilia = nomeFamilia
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

# Dicionario excluir
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
    salvarDictGeral(coletor,dict_coletor_doc)
    # Imprime o último valor do dicionário após a coleta
    if dict_coletor_doc:
        print(dict_coletor_doc)
    else:
        print("Dicionário está vazio.")

except Exception as e:
    print(e)


##########################################
##########################################

##PARTE DE INTERFACE 

def inDictName(familiaNova,dict_coletor_doc,geometria):
    print("Familia no dict principal - pelo nome")
    area_Total=geometria.area
    volume_Total=geometria.volume
    altura=geometria.altura
    largura=geometria.largura
    profundidade=geometria.profundidade
    
    if geometriaInDictFamilia(familiaNova.geometriaHash,familiaNova.nomeFamilia):
    #Geometria ja no dicionario do nome da familia
        print("familia no dict secundaria - pelo hashGeometry")
        
        familiaNova.symb=dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash][0].objetoFamilia
        print(familiaNova.symb)
        try:
            print("dentro try")
            nova_instancia=criarNovaInstacia(familiaNova.symb,altura,largura,profundidade)
            if nova_instancia:
                print("POS CRIAR NOVA INSTANCIA")
                print("Nova instancia com sucesso")
                novo_coletor=Coletor(familiaNova.symb,familiaNova.nomeFamilia)
                dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(novo_coletor) #adiciona mais um item na lista de familias
                
            else:
                print("PROBLEMA NA CRIACAO DE INSTANCIA")                
        except Exception as e:
            print(e)
    
        
    elif familiaNova.geometriaHash is not None: 
        #novo dict geometria / necessario fazer a duplicada de uma familia ja existente e mudando apenas sua geomtria
        print("geometria diferente")
        #fazer loaded
        try:
            # Inicia transacao
            transacao = Transaction(doc, "Carregar Família")
            transacao.Start() 
            print("dentro try")
            primeira_chave = next(iter(dict_coletor_doc[familiaNova.nomeFamilia]))
            familiaNova.symb=dict_coletor_doc[familiaNova.nomeFamilia][primeira_chave][0].objetoFamilia
            print(familiaNova.symb)
            if familiaNova.symb is not None:
                # Duplica o símbolo
                print("ANTES DUPLICATE")
                newHash=""
                nome_unico=familiaNova.nomeFamilia
                
                    
                symb_novo = familiaNova.symb.Duplicate("base")
                print("DENTRO IF SYMB")  
                if not symb_novo.IsActive:
                    print("NAO ATIVADO")
                    symb_novo.Activate()
                
                if symb_novo is not None:
                    print("dentro if symb novo")
                    symb_novo.Name=familiaNova.nomeFamilia
                    
                    # Verificar cada parâmetro antes de tentar definir
                    altura_param = symb_novo.LookupParameter("Altura")
                    if altura_param is not None:
                        altura_param.Set(altura)
                    else:
                        print("Parâmetro 'Altura' não encontrado em symb_novo.")

                    largura_param = symb_novo.LookupParameter("Largura")
                    if largura_param is not None:
                        largura_param.Set(largura)
                    else:
                        print("Parâmetro 'Largura' não encontrado em symb_novo.")

                    profundidade_param = symb_novo.LookupParameter("Profundidade")
                    if profundidade_param is not None:
                        profundidade_param.Set(profundidade)
                    else:
                        print("Parâmetro 'Profundidade' não encontrado em symb_novo.")
                
                    if altura_param is not None:
                        newHash=criarHashGeomtry(area_Total,volume_Total,altura_param,largura_param,profundidade_param)
                    else:
                        newHash="NoGeometry"
                else:
                    print("Nenhum FamilySymbol encontrado para duplicar.")
            
            transacao.Commit()
                
            #criarNovaInstacia
            print("ANTES DE CRIAR NOVA INSTANCIA")
            if criarNovaInstacia(familiaNova.symb,altura,largura,profundidade):
                print("APOS CRIAR NOVA INSTANCIA")
                # Adiciona ao dicionário
                novo_coletor=Coletor(familiaNova.symb,familiaNova.nomeFamilia)
                dict_coletor_doc[familiaNova.nomeFamilia][newHash]=[]
                dict_coletor_doc[familiaNova.nomeFamilia][newHash].append(novo_coletor)
                print("Nova variante de FamilySymbol criada e adicionada ao dicionário.")
                print(dict_coletor_doc[familiaNova.nomeFamilia][newHash][0].nomeFamilia)
            else:
                print("ERRO FAMILIA NOVA INSTANCIA")
        except Exception as e:
            print(e)
            
        finally:
            if transacao.HasStarted():
                transacao.RollBack()
    else:
        #NoGeometry / sem geometria / necessario fazer apenas uma nova instancia
        print("NoGeometry")
        #fazer loaded
        familiaNova.symb=dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"][0].objetoFamilia
        
        try:
            if criarNovaInstacia(familiaNova.symb,altura,largura,profundidade):
                print("Nova instancia com sucesso")
                novo_coletor=Coletor(familiaNova.symb,familiaNova.nomeFamilia)
                dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"].append(novo_coletor) #adiciona mais um item na lista de familias
            else:
                print("PROBLEMA NA NOVA INSTANCIA")
        except Exception as e:
            print(e)
            
        finally:
            if transacao.HasStarted():
                transacao.RollBack()

def outDictName(caminho,familiaNova,dict_coletor_doc):
    # criar o dict prinicpal novo
    
    #carregando arquivo
    try:
        # Inicia transacao
        transacao = Transaction(doc, "Carregar Arquivo")
        transacao.Start() 
        print("NOVA TRANSACAO")
        #Carrega arquivo
        family_path = caminho
        family_loaded = clr.Reference[Family]()
        doc.LoadFamily(family_path, family_loaded)
        family_loaded=family_loaded.Value
        print("CARREGADO O ARQUIVO")
        transacao.Commit()
    except Exception as e:
        print(e)
        
    finally:
        if transacao.HasStarted():
            transacao.RollBack()

    if familiaNova.geometriaHash != None:
        #adicionar no dict principal criado o dict secundario com o hashGeometry da familia
        print("TEM GEOMETRY")
        #iniciar uma nova instancia
        try:
            # Inicia transacao
            print("DENTRO TRY")
            transacao = Transaction(doc, "Carregar Família")
            transacao.Start() 
            familiaInstancia=colocarNovaFamilia(family_loaded)
            transacao.Commit()
            if familiaInstancia:
            #inserir os valores carregados da familia
                # Obtém o elemento pelo ID
                valorId = familiaInstancia.Id
                newSymb = doc.GetElement(valorId)
                
                familiaNova.symb=newSymb.Symbol
                dict_coletor_doc[familiaNova.nomeFamilia] = {}
                print("SALVANDO NO DICT-PRINCIPAL-SECUNDARIO")
                dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]=[]
                novo_coletor=Coletor(familiaNova.symb, familiaNova.nomeFamilia)
                dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(novo_coletor)
            else:
                print("PROBELMA INSERIR NOVA FAMILIA")
            
            
        except Exception as e:
            print(e)
            
        finally:
            if transacao.HasStarted():
                transacao.RollBack() 
                    
    else:
        #adicionar no dict principal criado o dict secundario com o NoGeometry
        
        
        #iniciar uma nova instancia
        try:
            # Inicia transacao
            transacao = Transaction(doc, "Carregar Família")
            transacao.Start() 
            nova_instancia=colocarNovaFamilia(family_loaded)
            transacao.Commit()
            
            if nova_instancia:
            #inserir os valores carregados da familia
                valorId = nova_instancia.Id
                newSymb = doc.GetElement(valorId)
                
                familiaNova.symb=newSymb.Symbol
                #[Coletor(symb, family_name, categoria)]
                dict_coletor_doc[familiaNova.nomeFamilia]={}
                dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"]=[]
                novo_coletor=Coletor(familiaNova.symb, familiaNova.nomeFamilia)
                dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"].append(novo_coletor)
            else:
                print("PROBELMA INSERIR NOVA FAMILIA")
                
        except Exception as e:
            print(e)
            
        finally:
            if transacao.HasStarted():
                transacao.RollBack()    

# Funções para as opções
def opcao1(sender, event):
    print("a")
    ###############################################
    largura=0.1088928624403937
    altura=0.025860871035717992
    profundidade=0.10889286244039369
    area_Total=0.023211573706191133
    volume_Total=0.00019675464789047678
    
    caminho=r"C:\Program Files\ProjetoRevit\familias\privada_branca.rfa"
    ###############################################
    geometria=Geometry(area_Total,volume_Total,altura,largura,profundidade)
    geometry_chave = criarHashGeomtry(area_Total,volume_Total,altura,largura,profundidade)
    familiaNova=FamiliaInformacao(None,"privada_branca",geometry_chave,None)
    
    if familiaInDict(familiaNova.nomeFamilia):
        #Nome familia ja no dicionario
        inDictName(familiaNova,dict_coletor_doc,geometria)
    else:
        # nao esta no dicionario / criar uma nova posição no dict principal e do secundario / carregar arquivo
        print("NAO ESTA NO PROJETO")
        outDictName(caminho,familiaNova,dict_coletor_doc)
        
def opcao2(sender, event):
    print("aa")
    ###############################################
    largura=0.34380099892333349
    altura=0.049212598425196763
    profundidade=0.34380099885387738
    area_Total=0.23487576549786049
    volume_Total=0.0038537725583392543
    
    caminho=r"C:\Program Files\ProjetoRevit\familias\SegurançaEControle_OrganizadorDeFilas_Vitrine.rfa"
    ###############################################
    geometria=Geometry(area_Total,volume_Total,altura,largura,profundidade)
    geometry_chave = criarHashGeomtry(area_Total,volume_Total,altura,largura,profundidade)
    familiaNova=FamiliaInformacao(None,"SegurançaEControle_OrganizadorDeFilas_Vitrine",geometry_chave,None)
        
    if familiaInDict(familiaNova.nomeFamilia):
        print("bb")
        inDictName(familiaNova,dict_coletor_doc,geometria)

    else:
        # nao esta no dicionario / criar uma nova posição no dict principal e do secundario / carregar arquivo
        print("NAO ESTA NO PROJETO")
        # criar o dict prinicpal novo
        outDictName(caminho,familiaNova,dict_coletor_doc)

def opcao3(sender, event):
    print("aaa")
    ###############################################
    largura=0.34380099892333349
    altura=0.049212598425196763
    profundidade=0.34380099885387738
    area_Total=0.23487576549786049
    volume_Total=0.0038537725583392543
    
    caminho=r"C:\Program Files\ProjetoRevit\familias\Paisagismo_BancoDePraca_Madeira_Vitrine.rfa"
    ###############################################
    geometria=Geometry(area_Total,volume_Total,altura,largura,profundidade)
    geometry_chave = criarHashGeomtry(area_Total,volume_Total,altura,largura,profundidade)
    familiaNova=FamiliaInformacao(None,"Paisagismo_BancoDePraca_Madeira_Vitrine",geometry_chave,None)
    
    if familiaInDict(familiaNova.nomeFamilia):
    #Nome familia ja no dicionario
        print("Familia no dict principal - pelo nome")
        inDictName(familiaNova,dict_coletor_doc,geometria)

    else:
        # nao esta no dicionario / criar uma nova posição no dict principal e do secundario / carregar arquivo
        print("NAO ESTA NO PROJETO")
        # criar o dict prinicpal novo
        outDictName(caminho,familiaNova,dict_coletor_doc)

# Criar a janela principal
class MenuForm(Form):
    def __init__(self):
        self.Text = "Menu de Opções"
        self.Size = Size(800, 600)
        
        # Botão Opção 1
        botao1 = Button()
        botao1.Text = "PRIVADA BRANCA"
        botao1.Size = Size(100, 40)
        botao1.Location = Point(100, 30)
        botao1.Click += opcao1
        self.Controls.Add(botao1)

        # Botão Opção 2
        botao2 = Button()
        botao2.Text = "Opção 2"
        botao2.Size = Size(100, 40)
        botao2.Location = Point(100, 80)
        botao2.Click += opcao2
        self.Controls.Add(botao2)

        # Botão Opção 3
        botao3 = Button()
        botao3.Text = "Banco de Praça Madeira"
        botao3.Size = Size(100, 40)
        botao3.Location = Point(100, 130)
        botao3.Click += opcao3
        self.Controls.Add(botao3)

# Iniciar o aplicativo
form = MenuForm()
Application.Run(form)
