
def digito_verificador_ruc(ruc_base):
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc_base[i]) * factores[i] for i in range(10))
    residuo = suma % 11
    diferencia = 11 - residuo
    return diferencia-10 if diferencia>=10 else diferencia


if __name__ == "__main__":
    print(digito_verificador_ruc(input("Ingrese ruc: ")))