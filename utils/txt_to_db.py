import sqlite3
import time
from os import path, remove

import pandas as pd


def count_lines(file_path):
    with open(file_path, "rb") as file:
        lines = 0
        buf_size = 1024 * 1024
        read_f = file.raw.read

        buf = read_f(buf_size)
        while buf:
            lines += buf.count(b"\n")
            buf = read_f(buf_size)
        return lines


def sanitize_csv(input_file, output_file, expected_fields=4, separator="|"):
    clean_lines = []

    # open file on latin-1 for correct reading
    with open(input_file, "r", encoding="latin-1") as file:
        for i, line in enumerate(file):
            line = line.strip()

            fields = line.split(separator, expected_fields)[:expected_fields]

            if len(fields) == expected_fields:
                clean_lines.append("|".join(fields))
            else:
                print(f"Error en linea {i}")

    # export file in utf-8 for most compatibility
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(clean_lines))


def convert_txt_to_sql(
    input_txt,
    output_db,
    table_name="main_table",
    separator="|",
    chunk_size=5000,
    progress_callback=None,
):
    """Convierte una entrada en txt o csv a una base de datos sql"""

    connection = sqlite3.connect(output_db)
    cursor = connection.cursor()
    print("Iniciando conversión...")

    # Deshabilita seguridad para aumentar velocidad (solo en la conversión)
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.close()

    start_time = time.time()
    rows_processed = 0
    total_lines = count_lines(input_txt)
    try:
        chunks = pd.read_csv(
            input_txt,
            sep=separator,
            chunksize=chunk_size,
            encoding="utf-8",
            on_bad_lines="warn",
            engine="c",
            low_memory=False,
            quoting=3,
            dtype="str",
        )

        for i, chunk in enumerate(chunks):
            chunk.columns = chunk.columns.str.strip().str.lower().str.replace(" ", "_")

            if "ruc" in chunk.columns:
                # 'coerce' convierte cualquier error a NaN
                chunk["ruc"] = (
                    pd.to_numeric(chunk["ruc"], errors="coerce")
                    .fillna(0)
                    .astype("int64")
                )

            chunk.to_sql(table_name, connection, if_exists="append", index=False)

            rows_in_chunk = len(chunk)
            rows_processed += rows_in_chunk

            if progress_callback:
                progress_callback(min(rows_processed / total_lines, 1.0))
            else:
                print(f"Chunk {i+1} procesado")

        print("Indexando la tabla")
        index_time = time.time()

        cursor_idx = connection.cursor()
        cursor_idx.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_ruc ON {table_name}(ruc)"
        )
        cursor_idx.close()

        connection.commit()
        print(f"Índice creado en {round(time.time() - index_time, 2)}s")
        print(f"Conversion completada en {round(time.time() - start_time, 2)}s")
    except Exception as e:
        connection.close()
        remove(output_db)
        print(f"Error: {e}")
    finally:
        cursor = connection.cursor()
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.execute("PRAGMA journal_mode = DELETE")
        connection.close()


def main():
    """runs in a main execution"""
    input_file = input("TO SANITIZE: ")
    output_db = path.splitext(input_file)[0] + ".db"
    TEMP_FILE = ".temp_sanitize.txt"

    sanitize_csv(input_file, TEMP_FILE)
    convert_txt_to_sql(TEMP_FILE, output_db)
    remove(TEMP_FILE)
    # convert_txt_to_sql(input_file, output_db, "padron", chunk_size=50000)


if __name__ == "__main__":
    main()
