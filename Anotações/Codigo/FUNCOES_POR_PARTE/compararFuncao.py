def compararFamilias(arquivo, dicionario):
    # pegando nomes e categorias
    nome_familiaArquivo = arquivo.categoria
    nome_familiaDicionario = [familia.nome for familia in dicionario.values()] #em cada local do dicionario quero .Name
    
    
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