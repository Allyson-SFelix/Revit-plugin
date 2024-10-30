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

def criarNovaInstacia(symb):
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
        transacao.Commit()
        return True
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



# PARTE QUE OBTEM TODAS AS FAMILIAS DO ARQUIVO EM UM DICIONARIO

coletor = FilteredElementCollector(doc).OfClass(FamilySymbol)
coletor_instancias = FilteredElementCollector(doc).OfClass(FamilyInstance)
dict_coletor_doc = {}
contadorDuplicates=1 
''"PARA POSSIBILITAR A DUPLICACAO DURANTE A EXECUCAO DO APLICATIVO"''
# CLASS
class FamiliaInformacao:
    def __init__(self,symb,nomeFamilia,geometriaHash,arquivoLoad):
        self.symb=symb
        self.nomeFamilia=nomeFamilia
        self.geometriaHash=geometriaHash
        self.arquivoLoad=arquivoLoad
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
#53.10120235190.7316359454125.090535670074.790026246720.404168452992
#53.10120235190.7316359454125.090535670074.790026246720.404168452992'
#53.10120235190.7316359454125.090535670074.790026246720.404168452992
categorias_excluir_dic_ids = {int(excluir) for excluir in categorias_excluir}



    
    
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
                    geometry_chave = str(objGeometry.area) + str(objGeometry.volume) + str(objGeometry.altura)+str(objGeometry.largura)+str(objGeometry.profundidade)
                    
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

##########################################
##########################################

##PARTE DE INTERFACE 

#erro -> System.MissingMemberException: 'FamilySymbol' object has no attribute 'objetoFamilia'

# Funções para as opções
def opcao1(sender, event):
    print("a")
    largura=0.1088928624403937
    altura=0.025860871035717992
    profundidade=0.10889286244039369
    area_Total=0.023211573706191133
    volume_Total=0.00019675464789047678
    geometry_chave = criarHashGeomtry(area_Total,volume_Total,altura,largura,profundidade)
    familiaNova=FamiliaInformacao(None,"privada_branca",geometry_chave,None)
    
    if familiaInDict(familiaNova.nomeFamilia):
    #Nome familia ja no dicionario
        print("Familia no dict principal - pelo nome")
    
        if geometriaInDictFamilia(familiaNova.geometriaHash,familiaNova.nomeFamilia):
        #Geometria ja no dicionario do nome da familia
            print("familia no dict secundaria - pelo hashGeometry")
            
            familiaNova.symb=dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash][0].objetoFamilia
            
            try:
                if criarNovaInstacia(familiaNova.symb):
                    print("Nova instancia com sucesso")
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(symb) #adiciona mais um item na lista de familias
                    for i in dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]:
                        print(i)
                else:
                    print("PROBLEMA NA CRIACAO DE INSTANCIA")                
            except Exception as e:
                print(e)
            
        
        elif familiaNova.geometriaHash != None: #PROVAVEL ERRO
            #novo dict geometria / necessario fazer o loaded do arquivo pois é uma familia diferente
            print("geometria diferente")
            #fazer loaded
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 

                #Carrega arquivo
                family_path = r"C:\Program Files\ProjetoRevit\familias\privada_branca.rfa"
                family_loaded = clr.Reference[Family]()
                if colocarNovaFamilia(family_loaded):
                    newSymb=pegarSymbolArquivo(family_loaded)
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]=[]
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                transacao.Commit()
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack()
        else:
            #NoGeometry / sem geometria / necessario fazer o loaded do arquivo pois é uma fmailia diferente
            print("NoGeometry")
            #fazer loaded
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 

                #Carrega arquivo
                family_path = r"C:\Program Files\ProjetoRevit\familias\privada_branca.rfa"
                family_loaded = clr.Reference[Family]()
                if colocarNovaFamilia(family_loaded):
                    newSymb=pegarSymbolArquivo(family_loaded)
                    dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                transacao.Commit()
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack()

    else:
        print("NAO ESTA NO PROJETO")
        # nao esta no dicionario / criar uma nova posição no dict principal e do secundario / carregar arquivo
        
        # criar o dict prinicpal novo
        
        #carregando arquivo
        try:
            # Inicia transacao
            transacao = Transaction(doc, "Carregar Arquivo")
            transacao.Start() 
            print("NOVA TRANSACAO")
            #Carrega arquivo
            family_path = r"C:\Program Files\ProjetoRevit\familias\privada_branca.rfa"
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
            print("CRIAR COM GEOMETRIA")
            #iniciar uma nova instancia
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 
                valorAdd=colocarNovaFamilia(family_loaded)
                transacao.Commit()
                if valorAdd:
                #inserir os valores carregados da familia
                    print("POS FUNCAO COLOCAR NOVA FAMILIA")
                    newSymb=pegarSymbolArquivo(family_loaded)
                    print("POS PEGAR SIMBOLO")
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]=[]
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(newSymb)
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
                valorAdd=colocarNovaFamilia(family_loaded)
                transacao.Commit()
                if valorAdd:
                #inserir os valores carregados da familia
                    newSymb=pegarSymbolArquivo(family_loaded)
                    dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack()    
            
def opcao2(sender, event):
    largura=0.34380099892333349
    altura=0.049212598425196763
    profundidade=0.34380099885387738
    area_Total=0.23487576549786049
    volume_Total=0.0038537725583392543
    geometry_chave = criarHashGeomtry(area_Total,volume_Total,altura,largura,profundidade)
    familiaNova=FamiliaInformacao(None,"SegurançaEControle_OrganizadorDeFilas_Vitrine",geometry_chave,None)
    
    if familiaInDict(familiaNova.nomeFamilia):
    #Nome familia ja no dicionario
        print("Familia no dict principal - pelo nome")
        
        if geometriaInDictFamilia(familiaNova.geometriaHash,familiaNova.nomeFamilia):
        #Geometria ja no dicionario do nome da familia
            print("familia no dict secundaria - pelo hashGeometry")
            
            familiaNova.symb=dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash][0].objetoFamilia
            
            try:
                if criarNovaInstacia(familiaNova.symb):
                    print("Nova instancia com sucesso")
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(symb) #adiciona mais um item na lista de familias
                    for i in dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]:
                        print(i)
                else:
                    print("PROBLEMA NA CRIACAO DE INSTANCIA")                
            except Exception as e:
                print(e)
            
        
        elif familiaNova.geometriaHash != None: #PROVAVEL ERRO
            #novo dict geometria / necessario fazer o loaded do arquivo pois é uma familia diferente
            print("geometria diferente")
            #fazer loaded
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 

                #Carrega arquivo
                family_path = r"C:\Program Files\ProjetoRevit\familias\SegurançaEControle_OrganizadorDeFilas_Vitrine.rfa"
                family_loaded = clr.Reference[Family]()
                
                if colocarNovaFamilia(family_loaded):
                    
                    newSymb=pegarSymbolArquivo(family_loaded)
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]=[]
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                transacao.Commit()  
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack()
        else:
            #NoGeometry / sem geometria / necessario fazer o loaded do arquivo pois é uma fmailia diferente
            print("NoGeometry")
            #fazer loaded
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 

                #Carrega arquivo
                family_path = r"C:\Program Files\ProjetoRevit\familias\SegurançaEControle_OrganizadorDeFilas_Vitrine.rfa"
                family_loaded = clr.Reference[Family]()
                doc.LoadFamily(family_path, family_loaded)
                if colocarNovaFamilia(family_loaded):
                    newSymb=pegarSymbolArquivo(family_loaded)
                    dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                
                transacao.Commit()
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack()

    else:
        # nao esta no dicionario / criar uma nova posição no dict principal e do secundario / carregar arquivo
        
        # criar o dict prinicpal novo
        
        #carregando arquivo
        try:
            # Inicia transacao
            transacao = Transaction(doc, "Carregar Arquivo")
            transacao.Start() 

            #Carrega arquivo
            family_path = r"C:\Program Files\ProjetoRevit\familias\SegurançaEControle_OrganizadorDeFilas_Vitrine.rfa"
            family_loaded = clr.Reference[Family]()
            doc.LoadFamily(family_path, family_loaded)
            print(family_loaded)
            
            transacao.Commit()
        except Exception as e:
            print(e)
                
        finally:
            if transacao.HasStarted():
                transacao.RollBack()

        if familiaNova.geometriaHash != None:
            #adicionar no dict principal criado o dict secundario com o hashGeometry da familia
            
            #iniciar uma nova instancia
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 

                if colocarNovaFamilia(family_loaded):
                #inserir os valores carregados da familia
                    newSymb=pegarSymbolArquivo(family_loaded)
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]=[]
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                
                
                transacao.Commit()    
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack() 
                        
        else:
            pass
            #adicionar no dict principal criado o dict secundario com o NoGeometry
            dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"]=None
            
            #iniciar uma nova instancia
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 

                if colocarNovaFamilia(family_loaded):
                #inserir os valores carregados da familia
                    newSymb=pegarSymbolArquivo(family_loaded)
                    dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                 
                
                transacao.Commit()   
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack()    

def opcao3(sender, event):
    largura=0.34380099892333349
    altura=0.049212598425196763
    profundidade=0.34380099885387738
    area_Total=0.23487576549786049
    volume_Total=0.0038537725583392543
    hashGeo="0.2348757654980.003853772558340.04921259842520.3438009989230.343800998854"
    #geometry_chave = criarHashGeomtry(area_Total,volume_Total,altura,largura,profundidade)
    familiaNova=FamiliaInformacao(None,"Paisagismo_BancoDePraca_Madeira_Vitrine",hashGeo,None)
    
    if familiaInDict(familiaNova.nomeFamilia):
    #Nome familia ja no dicionario
        print("Familia no dict principal - pelo nome")
        
        if geometriaInDictFamilia(familiaNova.geometriaHash,familiaNova.nomeFamilia):
        #Geometria ja no dicionario do nome da familia
            print("familia no dict secundaria - pelo hashGeometry")
            
            familiaNova.symb=dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash][0].objetoFamilia
            print(familiaNova.symb)
            try:
                print("dentro try")
                if criarNovaInstacia(familiaNova.symb):
                    print("POS CRIAR NOVA INSTANCIA")
                    print("Nova instancia com sucesso")
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(symb) #adiciona mais um item na lista de familias
                    for i in dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]:
                        print(i)
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
                    nome_unico=familiaNova.nomeFamilia
                    
                    while nome_unico not in dict_coletor_doc:
                        nome_unico=nome_unico+contadorDuplicates
                        contadorDuplicates=contadorDuplicates+1
                        
                    symb_novo = familiaNova.symb.Duplicate(nome_unico)
                    print("DENTRO IF SYMB")      
                    if symb_novo is not None:
                        print("dentro if symb novo")              
                    # Configura os parâmetros da nova geometria (se aplicável)
                    if symb_novo is not None:
                        print("dentro if symb novo")
                        
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
                    

                        transacao.Commit()
                    
                else:
                    print("Nenhum FamilySymbol encontrado para duplicar.")
            
                #criarNovaInstacia
                print("ANTES DE CRIAR NOVA INSTANCIA")
                if criarNovaInstacia(familiaNova.symb):
                    print("APOS CRIAR NOVA INSTANCIA")
                    # Adiciona ao dicionário
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]=[]
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(symb_novo)
                    print("Nova variante de FamilySymbol criada e adicionada ao dicionário.")
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
                if criarNovaInstacia(familiaNova.symb):
                    print("Nova instancia com sucesso")
                    dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"].append(familiaNova.symb) #adiciona mais um item na lista de familias
                else:
                    print("PROBLEMA NA NOVA INSTANCIA")
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack()

    else:
        # nao esta no dicionario / criar uma nova posição no dict principal e do secundario / carregar arquivo
        print("NAO ESTA NO PROJETO")
        # criar o dict prinicpal novo
        
        #carregando arquivo
        try:
            # Inicia transacao
            transacao = Transaction(doc, "Carregar Arquivo")
            transacao.Start() 
            print("NOVA TRANSACAO")
            #Carrega arquivo
            family_path = r"C:\Program Files\ProjetoRevit\familias\Paisagismo_BancoDePraca_Madeira_Vitrine.rfa"
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
            
            #iniciar uma nova instancia
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 
                familiaInstancia=colocarNovaFamilia(family_loaded)
                transacao.Commit()
                if familiaInstancia:
                #inserir os valores carregados da familia
                    # Obtém o elemento pelo ID
                    valorId = familiaInstancia.Id
                    newSymb = doc.GetElement(valorId)
                    
                    familiaNova.symb=newSymb
                    dict_coletor_doc[familiaNova.nomeFamilia] = {}
                    
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash]=[]
                    dict_coletor_doc[familiaNova.nomeFamilia][familiaNova.geometriaHash].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                
                
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack() 
                        
        else:
            #adicionar no dict principal criado o dict secundario com o NoGeometry
            dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"]=None
            
            #iniciar uma nova instancia
            try:
                # Inicia transacao
                transacao = Transaction(doc, "Carregar Família")
                transacao.Start() 
                nova_instancia=colocarNovaFamilia(family_loaded)
                transacao.Commit()
                
                if nova_instancia:
                #inserir os valores carregados da familia
                    newSymb=pegarSymbolArquivo(family_loaded)
                    dict_coletor_doc[familiaNova.nomeFamilia]["NoGeometry"].append(newSymb)
                else:
                    print("PROBELMA INSERIR NOVA FAMILIA")
                    
            except Exception as e:
                print(e)
                
            finally:
                if transacao.HasStarted():
                    transacao.RollBack()    


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
