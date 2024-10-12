def compararFamilias(familia1, familia2):
    # Comparar nomes das famílias
    nome_familia1 = familia1.get_Parameter(BuiltInParameter.FAMILY_NAME).AsString()
    nome_familia2 = familia2.get_Parameter(BuiltInParameter.FAMILY_NAME).AsString()

    if nome_familia1 != nome_familia2:
        print(f"Famílias diferentes: {nome_familia1} vs {nome_familia2}")
        return False
    
    # Comparar categorias das famílias
    categoria_familia1 = familia1.FamilyCategory.Name
    categoria_familia2 = familia2.FamilyCategory.Name

    if categoria_familia1 != categoria_familia2:
        print(f"Categorias diferentes: {categoria_familia1} vs {categoria_familia2}")
        return False
    
    # Comparar símbolos (FamilySymbol)
    simbolos_familia1 = list(familia1.GetFamilySymbolIds())
    simbolos_familia2 = list(familia2.GetFamilySymbolIds())

    if len(simbolos_familia1) != len(simbolos_familia2):
        print(f"Número de símbolos diferentes: {len(simbolos_familia1)} vs {len(simbolos_familia2)}")
        return False
    
    for symbol_id1, symbol_id2 in zip(simbolos_familia1, simbolos_familia2):
        simbolo1 = doc.GetElement(symbol_id1)
        simbolo2 = doc.GetElement(symbol_id2)

        nome_simbolo1 = simbolo1.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        nome_simbolo2 = simbolo2.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()

        if nome_simbolo1 != nome_simbolo2:
            print(f"Símbolos diferentes: {nome_simbolo1} vs {nome_simbolo2}")
            return False

    print("As famílias são equivalentes.")
    return True

# Exemplo de uso
familia_carregada = doc.LoadFamily(family_path)  # Família carregada, mas não instanciada
familia_no_projeto = doc.GetElement(ElementId(id_familia_no_projeto))  # Família já presente no projeto

compararFamilias(familia_carregada, familia_no_projeto)
