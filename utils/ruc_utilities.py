import sqlite3


def buscar_rucs(lista_rucs, path_db, table_name="main_table"):
    """
    Recibe una lista de rucs:str, verifica si son validos y los busca en la base de datos.
    Devuelve la lista original completa, seguida de la versión limpia de cada ruc, si es que hubiera, y la información extraída de la DB
    """
    rucs_enteros = [int(ruc) for ruc in limpiar_rucs(lista_rucs)]
    CHUNK_SQL_SIZE = 900
    
    db_cache = {}
    
    con = sqlite3.connect(path_db)
    cursor = con.cursor()
    num_columnas = 0
    try:
        for i in range(0, len(rucs_enteros), CHUNK_SQL_SIZE):
            lote = rucs_enteros[i: i+CHUNK_SQL_SIZE]
            
            placeholder = ",".join("?"*len(lote))
            consulta = f"SELECT * FROM {table_name} WHERE ruc IN ({placeholder})"
            
            cursor.execute(consulta, lote)
            filas = cursor.fetchall()
            
            if num_columnas==0 and cursor.description:
                num_columnas = len(cursor.description)
            
            for fila in filas:
                db_cache[fila[0]] = fila
    
    except Exception as e:
        print(f"Error consulting DB: {e}")
        return []
    
    finally:
        con.close()
    
    resultados_finales = []
    
    for ruc_listado in lista_rucs:
        ruc_limpio = limpiar_ruc(ruc_listado)
        ruc_failed = None
        
        if not ruc_limpio:
            ruc_failed = "RUC INVÁLIDO"
        elif int(ruc_limpio) not in db_cache:
            ruc_failed = "NO SE ENCONTRÓ"
        else:
            tupla_final = (ruc_listado,) + db_cache[int(ruc_limpio)]
            resultados_finales.append(tupla_final)
        
        if ruc_failed:
            tupla_vacia = (ruc_listado, limpiar_ruc(ruc_limpio),) + (ruc_failed,) + ("-",) * (num_columnas-2)
            resultados_finales.append(tupla_vacia)
    
    return resultados_finales


def limpiar_rucs(lista_rucs):
    rucs_limpios = []
    for doc in lista_rucs:
        ruc_final = limpiar_ruc(doc)
        if ruc_final:
            rucs_limpios.append(ruc_final)

    return rucs_limpios


def limpiar_ruc(ruc):
    ruc = str(ruc).strip()
    ruc_final = ""
    
    # Lógica de conversión
    if len(ruc) == 11 and ruc.isdigit():
        digito = digito_verificador_ruc(ruc)
        
        # corrige el digito de verificación del RUC ingresado de ser necesario
        if not ruc.endswith(str(digito)):
            ruc_final = ruc.removesuffix(ruc[10]) + str(digito)
        else:
            ruc_final = ruc
    
    # para encontrar RUC 10 con solo el DNI
    elif len(ruc) == 8 and ruc.isdigit():
        base = "10" + ruc
        digito = digito_verificador_ruc(base)
        ruc_final = base + str(digito)
    
    return ruc_final if ruc_final else None


def digito_verificador_ruc(ruc_base):
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc_base[i]) * factores[i] for i in range(10))
    residuo = suma % 11
    diferencia = 11 - residuo
    return diferencia-10 if diferencia>=10 else diferencia


if __name__ == "__main__":
    print(digito_verificador_ruc(input("Ingrese ruc: ")))