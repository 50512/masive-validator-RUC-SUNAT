import random
import sqlite3
import time
from os import mkdir, path

import pandas as pd

TEST_FOLDER = "./.tests_files"


def extraer_muestras(path_db, cantidad=1000, table_name="main_table"):
    con = sqlite3.connect(path_db)
    cursor = con.cursor()

    # Consultar rowid máximo
    cursor.execute(f"SELECT MAX(rowid) FROM {table_name}")
    max_id = cursor.fetchone()[0]

    import random

    muestras_unicas = set()

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_reales = cursor.fetchone()[0]
    objetivo = min(cantidad, total_reales)

    while len(muestras_unicas) < objetivo:
        random_id = random.randint(1, max_id)
        cursor.execute(f"SELECT ruc FROM {table_name} WHERE rowid = ?", (random_id,))
        res = cursor.fetchone()
        if res:
            muestras_unicas.add(res[0])

    con.close()
    return muestras_unicas


def generar_dataset_normal(path_db, cantidad, table_name):
    print("Iniciando generación...")
    start_time = time.time()
    muestras = extraer_muestras(path_db, cantidad, table_name)

    df = pd.DataFrame(muestras, columns=["Documento"], dtype=str)
    if not path.exists(TEST_FOLDER):
        mkdir(TEST_FOLDER)
    filename = path.join(TEST_FOLDER, f"test_dataset_{cantidad}.xlsx")

    df.to_excel(filename, index=False)
    print(f"Dataset generado en {round(time.time()-start_time,2)}s")
    print(f"✅ Dataset guardado en: {filename}")


def generar_dataset_stress(path_db, cantidad, table_name, ratio_error):
    print("Generando dataset con errores...")
    start_time = time.time()

    muestras = extraer_muestras(path_db, cantidad, table_name)
    num_errores = int(cantidad * ratio_error)
    dataset = []

    print(f"Inyectando {num_errores} errores...")
    for i, ruc in enumerate(muestras):
        ruc = str(ruc)

        if i < num_errores:  # Aplicar caos solo a una parte
            tipo_caos = random.choice(
                ["letra", "espacios", "corto", "formato dni", "inexistente"]
            )

            if tipo_caos == "letra":
                ruc = ruc[:-1] + "X"

            elif tipo_caos == "espacios":
                ruc = f"  {ruc}  "

            elif tipo_caos == "corto":
                ruc = ruc[:5]

            elif tipo_caos == "formato dni":
                ruc = ruc[:8]

            elif tipo_caos == "inexistente":
                ruc = "99000000000"

        dataset.append(ruc)
    random.shuffle(dataset)

    df = pd.DataFrame(dataset, columns=["Documento"])
    output_name = path.join(TEST_FOLDER, f"TEST_STRESS_{cantidad}.xlsx")
    if not path.exists(TEST_FOLDER):
        mkdir(TEST_FOLDER)
    df.to_excel(output_name, index=False)

    print(f"Dataset generado en {round(time.time()-start_time,2)}s")
    print(f"✅ ¡Dataset de estrés listo!: {output_name}")


def main():
    PATH_DB = "./.sunat-datos/padron_ruc_sunat.db"
    cantidad = int(input("Inserte cantidad de muestras: "))
    generar_dataset_normal(PATH_DB, cantidad, "padron")
    generar_dataset_stress(PATH_DB, cantidad, "padron", 0.15)


if __name__ == "__main__":
    main()
