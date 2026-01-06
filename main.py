import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import requests
import zipfile
import os
import threading

# --- CONFIGURACIÓN ---
URL_PADRON = "https://www.sunat.gob.pe/descargaPRR/padron_reducido_ruc.zip"
ARCHIVO_ZIP = "padron_reducido_ruc.zip"
NOMBRE_PADRON_TXT = "padron_reducido_ruc.txt"

class SunatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Validador Masivo SUNAT - Modo Gratuito")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("Green.Horizontal.TProgressbar", foreground='green', background='green')

        # Variables
        self.archivo_seleccionado = tk.StringVar()
        self.estado_padron = tk.StringVar(value="Verificando padrón...")
        
        # --- INTERFAZ ---
        
        # 1. Sección Padrón
        frame_padron = tk.LabelFrame(root, text="1. Base de Datos SUNAT", padx=10, pady=10)
        frame_padron.pack(fill="x", padx=10, pady=5)
        
        self.lbl_padron = tk.Label(frame_padron, textvariable=self.estado_padron, fg="blue", font=("Arial", 9, "bold"))
        self.lbl_padron.pack(side="left")
        
        self.btn_descargar = tk.Button(frame_padron, text="Descargar/Actualizar Padrón", command=self.iniciar_descarga_thread, bg="#f0f0f0")
        self.btn_descargar.pack(side="right")

        # 2. Sección Archivo Excel
        frame_file = tk.LabelFrame(root, text="2. Archivo de Clientes", padx=10, pady=10)
        frame_file.pack(fill="x", padx=10, pady=5)
        
        tk.Entry(frame_file, textvariable=self.archivo_seleccionado, state="readonly", width=50).pack(side="left", padx=5)
        tk.Button(frame_file, text="📂 Seleccionar Excel", command=self.seleccionar_excel, bg="#2196F3", fg="white").pack(side="right")

        # 3. Sección Procesar
        frame_action = tk.Frame(root, padx=10, pady=10)
        frame_action.pack(fill="x", padx=10, pady=5)
        
        self.btn_procesar = tk.Button(frame_action, text="🚀 PROCESAR LISTA", command=self.iniciar_procesamiento_thread, 
                                      bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), state="disabled", width=30)
        self.btn_procesar.pack(pady=5)

        # Barra de Progreso
        self.progress = ttk.Progressbar(root, orient="horizontal", length=550, mode="determinate", style="Green.Horizontal.TProgressbar")
        self.progress.pack(pady=5)
        
        # Consola de Log
        self.log_area = scrolledtext.ScrolledText(root, width=70, height=12, state='disabled', font=("Consolas", 9))
        self.log_area.pack(padx=10, pady=5)

        # Verificar estado inicial
        self.verificar_padron_local()

    # --- LÓGICA DE UTILIDAD ---
    def log(self, mensaje, color="black"):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f">> {mensaje}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        self.root.update_idletasks()

    def verificar_padron_local(self):
        if os.path.exists(NOMBRE_PADRON_TXT):
            self.estado_padron.set("✅ Padrón SUNAT Listo")
            self.lbl_padron.config(fg="green")
            self.btn_descargar.config(state="normal")
        else:
            self.estado_padron.set("❌ Padrón NO encontrado")
            self.lbl_padron.config(fg="red")

    def calcular_digito_ruc(self, ruc_base):
        factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc_base[i]) * factores[i] for i in range(10))
        residuo = suma % 11
        diferencia = 11 - residuo
        return 0 if diferencia == 10 else (1 if diferencia == 11 else diferencia)

    # --- HILOS (THREADS) ---
    def iniciar_descarga_thread(self):
        threading.Thread(target=self.descargar_logica, daemon=True).start()

    def iniciar_procesamiento_thread(self):
        threading.Thread(target=self.procesar_logica, daemon=True).start()

    # --- LÓGICA PRINCIPAL ---
    def descargar_logica(self):
        self.btn_descargar.config(state="disabled")
        self.btn_procesar.config(state="disabled")
        self.log("Iniciando descarga del Padrón SUNAT (300MB+)...")
        
        try:
            response = requests.get(URL_PADRON, stream=True)
            total_length = int(response.headers.get('content-length', 0))
            dl = 0
            
            with open(ARCHIVO_ZIP, 'wb') as f:
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    if total_length:
                        porcentaje = (dl / total_length) * 100
                        self.progress['value'] = porcentaje
                        self.root.update_idletasks()
            
            self.log("Descarga completa. Descomprimiendo ZIP...")
            with zipfile.ZipFile(ARCHIVO_ZIP, 'r') as z:
                z.extractall()
                
            self.log("✅ Padrón actualizado correctamente.", "green")
            self.root.after(0, self.verificar_padron_local)
            
        except Exception as e:
            self.log(f"❌ Error en descarga: {str(e)}", "red")
            messagebox.showerror("Error", f"Fallo en la descarga: {e}")
            
        finally:
            self.btn_descargar.config(state="normal")
            if self.archivo_seleccionado.get():
                self.btn_procesar.config(state="normal")
            self.progress['value'] = 0

    def seleccionar_excel(self):
        archivo = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if archivo:
            self.archivo_seleccionado.set(archivo)
            self.log(f"Archivo seleccionado: {os.path.basename(archivo)}")
            if os.path.exists(NOMBRE_PADRON_TXT):
                self.btn_procesar.config(state="normal")
            else:
                self.log("⚠️ Primero debes descargar el padrón SUNAT.")

    def procesar_logica(self):
        self.btn_procesar.config(state="disabled")
        self.progress['value'] = 0
        archivo_input = self.archivo_seleccionado.get()
        
        try:
            # 1. Cargar Padrón
            self.log("⏳ Cargando Padrón SUNAT en memoria (esto toma unos segundos)...")
            
            # Leemos por chunks o optimizado
            df_padron = pd.read_csv(
                NOMBRE_PADRON_TXT, sep='|', encoding='latin-1',
                usecols=[0, 1, 2, 3], names=['RUC', 'NOMBRE', 'ESTADO', 'CONDICION'],
                dtype={'RUC': str}, engine='c'
            )
            
            self.log("⚙️ Indexando base de datos...")
            bd_sunat = df_padron.set_index('RUC').to_dict('index')
            del df_padron # Liberar memoria
            
            # 2. Cargar Excel
            self.log(f"Leyendo Excel: {os.path.basename(archivo_input)}")
            df_user = pd.read_excel(archivo_input, dtype=str)
            
            # Buscar columna
            col_doc = next((c for c in df_user.columns if str(c).strip().lower() == 'documento'), None)
            if not col_doc:
                raise Exception("No se encontró columna 'Documento' en el Excel.")

            # 3. Procesar
            resultados = []
            total_filas = len(df_user)
            self.log(f"Analizando {total_filas} registros...")
            
            for i, doc in enumerate(df_user[col_doc]):
                doc = str(doc).strip()
                ruc_final = ""
                
                if len(doc) == 11 and doc.isdigit():
                    ruc_final = doc
                elif len(doc) == 8 and doc.isdigit():
                    base = "10" + doc
                    digito = self.calcular_digito_ruc(base)
                    ruc_final = base + str(digito)
                
                info = bd_sunat.get(ruc_final)
                
                res = {
                    "Documento Input": doc,
                    "RUC Validado": ruc_final if ruc_final else "-",
                    "Razon Social": info['NOMBRE'] if info else "-",
                    "Estado": info['ESTADO'] if info else "NO HALLADO",
                    "Condicion": info['CONDICION'] if info else "-"
                }
                resultados.append(res)
                
                # Actualizar barra cada 50 items para no alentar la GUI
                if i % 50 == 0:
                    progreso = (i / total_filas) * 100
                    self.progress['value'] = progreso
                    self.root.update_idletasks()

            # 4. Guardar
            self.progress['value'] = 100
            nombre_salida = os.path.splitext(archivo_input)[0] + "_PROCESADO.xlsx"
            pd.DataFrame(resultados).to_excel(nombre_salida, index=False)
            
            self.log(f"✅ ¡ÉXITO! Archivo guardado:\n{os.path.basename(nombre_salida)}")
            messagebox.showinfo("Proceso Terminado", f"Se generó el archivo:\n{nombre_salida}")
            os.startfile(os.path.dirname(nombre_salida)) # Abrir carpeta

        except Exception as e:
            self.log(f"❌ ERROR CRÍTICO: {str(e)}", "red")
            messagebox.showerror("Error", str(e))
        
        finally:
            self.btn_procesar.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = SunatApp(root)
    root.mainloop()
