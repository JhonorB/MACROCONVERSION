import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
import datetime
from procesador_sire import preparar_dataframes, guardar_excel_final

# Configuración básica del tema (puedes cambiar "Dark" a "Light" o "System")
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Conversor SIRE a Macro Excel")
        self.update_idletasks()
        
        # Centrado matemático robusto (compatible con escalado de Windows)
        width = 750
        height = 680
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # Parche para pantallas ultra-anchas o multi-monitor
        if screen_w > 2560:
            screen_w = 1920
            
        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))
        
        # Evitar que se oculte debajo de la barra de tareas
        x = max(10, x)
        y = max(10, y - 40)
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.ruta_json = os.path.join(os.path.dirname(__file__), "empresas.json")
        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                self.empresas = json.load(f)
        except Exception as e:
            messagebox.showwarning("Advertencia", f"No se pudo cargar empresas.json: {e}")
            self.empresas = {}
            
        self.nombres_empresas = list(self.empresas.keys())
        self.ruta_csv = ""
        
        # Configuración extra (Ruta PDFs)
        self.ruta_config = os.path.join(os.path.dirname(__file__), "config_sire.json")
        self.config = {}
        if os.path.exists(self.ruta_config):
            try:
                with open(self.ruta_config, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except:
                pass
        self.ruta_pdfs = self.config.get("ruta_pdfs", "")
        
        self.construir_ui()

    def construir_ui(self):
        # Título principal
        self.lbl_titulo = ctk.CTkLabel(self, text="Conversor SIRE SUNAT", font=ctk.CTkFont(size=26, weight="bold"))
        self.lbl_titulo.pack(pady=(10, 5))

        # Contenedor principal con bordes curvos (sin scroll global)
        self.frame_main = ctk.CTkFrame(self, corner_radius=15)
        self.frame_main.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Paddings internos
        inner_padx = 25
        
        # ----------------------------------------------------
        # 1. Selección de CSV
        # ----------------------------------------------------
        ctk.CTkLabel(self.frame_main, text="1. Seleccione el archivo CSV:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=inner_padx, pady=(10, 2))
        
        frame_csv = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        frame_csv.pack(fill="x", padx=inner_padx, pady=(0, 5))
        
        self.lbl_csv = ctk.CTkLabel(frame_csv, text="Ningún archivo seleccionado...", text_color="gray", anchor="w")
        self.lbl_csv.pack(side="left", fill="x", expand=True)
        
        self.btn_csv = ctk.CTkButton(frame_csv, text="Buscar CSV", command=self.seleccionar_csv, width=120)
        self.btn_csv.pack(side="right", padx=(10, 0))

        # ----------------------------------------------------
        # 2. Selección de Empresa (con filtro)
        # ----------------------------------------------------
        frame_lbl2 = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        frame_lbl2.pack(fill="x", padx=inner_padx, pady=(0, 2))
        ctk.CTkLabel(frame_lbl2, text="2. Busque y seleccione la Empresa:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(frame_lbl2, text="➕ Nueva Empresa", width=120, height=24, command=self.agregar_empresa, fg_color="#2FA572", hover_color="#1F7A52").pack(side="right")

        
        self.var_empresa = ctk.StringVar()
        self.var_empresa.trace("w", self.filtrar_empresas)
        
        self.entry_empresa = ctk.CTkEntry(self.frame_main, textvariable=self.var_empresa, placeholder_text="Escriba aquí para buscar una empresa...")
        self.entry_empresa.pack(fill="x", padx=inner_padx, pady=(0, 5))
        
        # Lista scrolleable de empresas más pequeña
        self.scroll_empresas = ctk.CTkScrollableFrame(self.frame_main, height=75, corner_radius=8)
        self.scroll_empresas.pack(fill="x", padx=inner_padx, pady=(0, 5))
        
        self.botones_empresa = []
        self.actualizar_lista(self.nombres_empresas)

        # ----------------------------------------------------
        # 3. Tipo (Compra / Venta)
        # ----------------------------------------------------
        ctk.CTkLabel(self.frame_main, text="3. Tipo de Registro:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=inner_padx, pady=(0, 2))
        self.var_tipo = ctk.StringVar(value="COM")
        
        self.frame_tipo = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_tipo.pack(fill="x", padx=inner_padx, pady=(0, 5))
        
        ctk.CTkRadioButton(self.frame_tipo, text="Compras (COM)", variable=self.var_tipo, value="COM", command=self.toggle_subtipo).pack(side="left", padx=(0, 30))
        ctk.CTkRadioButton(self.frame_tipo, text="Ventas (VTA)", variable=self.var_tipo, value="VTA", command=self.toggle_subtipo).pack(side="left")

        # Subtipo Venta (Oculto por defecto)
        self.frame_subtipo = ctk.CTkFrame(self.frame_tipo, fg_color="transparent")
        
        self.lbl_subtipo_vta = ctk.CTkLabel(self.frame_subtipo, text="↳ Detalle:", font=ctk.CTkFont(size=14, slant="italic"))
        self.lbl_subtipo_vta.pack(side="left", padx=(15, 5))
        
        self.var_subtipo_vta = ctk.StringVar(value="MERCADERIA")
        self.combo_subtipo_vta = ctk.CTkComboBox(
            self.frame_subtipo,
            variable=self.var_subtipo_vta,
            values=["MERCADERIA", "PRODUCTOS TERMINADOS", "SERVICIOS"],
            state="readonly",
            width=200
        )
        self.combo_subtipo_vta.pack(side="left")

        # ----------------------------------------------------
        # 4. Año y Mes
        # ----------------------------------------------------
        ctk.CTkLabel(self.frame_main, text="4. Periodo:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=inner_padx, pady=(0, 2))
        
        frame_fecha = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        frame_fecha.pack(fill="x", padx=inner_padx, pady=(0, 5))
        
        now = datetime.datetime.now()
        if now.month == 1:
            prev_m = 12
            prev_y = now.year - 1
        else:
            prev_m = now.month - 1
            prev_y = now.year
            
        def_ano = str(prev_y)[-2:]
        def_mes = f"{prev_m:02d}"
        
        ctk.CTkLabel(frame_fecha, text="Año (2 dígitos):").pack(side="left")
        self.var_ano = ctk.StringVar(value=def_ano)
        ctk.CTkEntry(frame_fecha, textvariable=self.var_ano, width=60, justify="center").pack(side="left", padx=(10, 30))
        
        ctk.CTkLabel(frame_fecha, text="Mes (2 dígitos):").pack(side="left")
        self.var_mes = ctk.StringVar(value=def_mes)
        ctk.CTkEntry(frame_fecha, textvariable=self.var_mes, width=60, justify="center").pack(side="left", padx=(10, 0))

        # ----------------------------------------------------
        # 4.5. Directorio de PDFs (Opcional)
        # ----------------------------------------------------
        frame_pdf = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        frame_pdf.pack(fill="x", padx=inner_padx, pady=(15, 5))
        
        ctk.CTkLabel(frame_pdf, text="📁 Carpeta de Comprobantes Locales (Opcional):", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        self.lbl_pdf = ctk.CTkLabel(frame_pdf, text=self.ruta_pdfs if self.ruta_pdfs else "Ninguna carpeta seleccionada...", text_color=("gray10", "gray90") if self.ruta_pdfs else "gray", anchor="w")
        self.lbl_pdf.pack(side="left", fill="x", expand=True, padx=10)
        
        ctk.CTkButton(frame_pdf, text="Elegir Carpeta", command=self.seleccionar_carpeta_pdfs, width=120).pack(side="right")

        # ----------------------------------------------------
        # 5. Botón Generar
        # ----------------------------------------------------
        self.btn_generar = ctk.CTkButton(
            self, 
            text="GENERAR MACRO EXCEL", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            height=50, 
            command=self.generar_excel, 
            fg_color="#2FA572", 
            hover_color="#1F7A52",
            corner_radius=10
        )
        self.btn_generar.place(relx=0.5, rely=0.94, anchor="center", relwidth=0.9)

    def toggle_subtipo(self):
        if self.var_tipo.get() == "VTA":
            self.frame_subtipo.pack(side="left")
        else:
            self.frame_subtipo.pack_forget()

    def agregar_empresa(self):
        # Paso 1: Pedir RUC
        dialog_ruc = ctk.CTkInputDialog(text="Paso 1 de 2:\n\nIngrese el RUC de la nueva empresa:", title="Nueva Empresa - RUC")
        ruc_empresa = dialog_ruc.get_input()
        
        if not ruc_empresa or not ruc_empresa.strip():
            return # Canceló o dejó vacío
            
        # Paso 2: Pedir Razón Social
        dialog_nombre = ctk.CTkInputDialog(text="Paso 2 de 2:\n\nIngrese la Razón Social (Nombre) de la empresa:", title="Nueva Empresa - Nombre")
        nombre_empresa = dialog_nombre.get_input()
        
        if not nombre_empresa or not nombre_empresa.strip():
            return # Canceló o dejó vacío
            
        ruc_empresa = ruc_empresa.strip()
        nombre_empresa = nombre_empresa.strip().upper()
        
        # Combinar RUC y Nombre
        texto_completo = f"{ruc_empresa} - {nombre_empresa}"
        
        # Encontrar el código más alto
        max_codigo = 0
        for emp_name in self.empresas.keys():
            partes = emp_name.split("-", 1)
            if len(partes) > 1:
                cod_str = partes[0].strip()
                if cod_str.isdigit():
                    max_codigo = max(max_codigo, int(cod_str))
                    
        nuevo_codigo_int = max_codigo + 1
        nuevo_codigo_str = f"{nuevo_codigo_int:04d}"
        nuevo_nombre = f"{nuevo_codigo_str} - {texto_completo}"
        
        # Guardar en base de datos
        self.empresas[nuevo_nombre] = nuevo_codigo_str
        self.nombres_empresas = list(self.empresas.keys())
        self.nombres_empresas.sort()
        
        try:
            with open(self.ruta_json, "w", encoding="utf-8") as f:
                json.dump(self.empresas, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la empresa: {e}")
            
        # Seleccionar automáticamente y actualizar UI
        self.var_empresa.set(nuevo_nombre)
        self.filtrar_empresas()
        messagebox.showinfo("Éxito", f"Empresa agregada exitosamente:\n\n{nuevo_nombre}")

    def filtrar_empresas(self, *args):
        busqueda = self.var_empresa.get().lower()
        if busqueda == "":
            self.actualizar_lista(self.nombres_empresas) 
        else:
            filtradas = [emp for emp in self.nombres_empresas if busqueda in emp.lower()]
            self.actualizar_lista(filtradas)

    def actualizar_lista(self, items):
        # Limpiar botones anteriores
        for btn in self.botones_empresa:
            btn.destroy()
        self.botones_empresa.clear()
        
        # Limitar para evitar lag extremo si hay miles de empresas (aquí hay ~100, así que no hay problema)
        items_a_mostrar = items[:150]
        
        for item in items_a_mostrar:
            btn = ctk.CTkButton(
                self.scroll_empresas, 
                text=item, 
                anchor="w", 
                fg_color="transparent", 
                text_color=("gray10", "gray90"), 
                hover_color=("gray70", "gray30"), 
                command=lambda emp=item: self.seleccionar_empresa_lista(emp)
            )
            btn.pack(fill="x", pady=1)
            self.botones_empresa.append(btn)

    def seleccionar_empresa_lista(self, empresa_seleccionada):
        self.var_empresa.set(empresa_seleccionada)

    def seleccionar_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if ruta:
            self.ruta_csv = ruta
            self.lbl_csv.configure(text=os.path.basename(ruta), text_color=("black", "white"))

    def seleccionar_carpeta_pdfs(self):
        carpeta = filedialog.askdirectory(title="Seleccionar Carpeta de PDFs")
        if carpeta:
            self.ruta_pdfs = carpeta
            self.lbl_pdf.configure(text=carpeta, text_color=("gray10", "gray90"))
            self.config["ruta_pdfs"] = carpeta
            try:
                with open(self.ruta_config, "w", encoding="utf-8") as f:
                    json.dump(self.config, f)
            except: pass

    def generar_excel(self, silent_alerts=False):
        if not self.ruta_csv:
            messagebox.showerror("Error", "Por favor seleccione un archivo CSV primero.")
            return
            
        nombre_emp = self.var_empresa.get()
        if nombre_emp not in self.empresas:
            messagebox.showerror("Error", "Por favor seleccione una empresa válida de la lista.")
            return
            
        codigo_empresa = self.empresas[nombre_emp]
        tipo = self.var_tipo.get()
        ano = self.var_ano.get()
        mes = self.var_mes.get()
        
        if len(ano) != 2 or len(mes) != 2:
            messagebox.showerror("Error", "El año y mes deben tener 2 dígitos (ej. 26 y 05).")
            return
                
        # Obtener la ruta de la carpeta "Descargas" o "Downloads" del usuario
        directorio_salida = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Por seguridad, si por alguna razón no existe, usar la carpeta del CSV
        if not os.path.exists(directorio_salida):
            directorio_salida = os.path.dirname(self.ruta_csv)
        
        try:
            res = preparar_dataframes(
                self.ruta_csv, 
                directorio_salida, 
                tipo, 
                codigo_empresa, 
                ano, 
                mes,
                self.var_subtipo_vta.get() if tipo == "VTA" else ""
            )
            
            df_forexel, df_docref, ruta_generada, lista_detracciones, cantidad_nc, eliminados_año_pasado, facturas, eliminados_deuda = res
            
            # Alertas Inmediatas de Deuda Coactiva
            if eliminados_deuda == -1:
                messagebox.showerror("Error de Conexión: API SUNAT", "No se pudo consultar las Deudas Coactivas.\n\nFaltan los archivos de token o han expirado.\n\nPor favor, cree un archivo llamado 'api_token.txt' (para apiperu.dev) o 'api_token2.txt' (para api.json.pe) en la carpeta del programa y pegue su token dentro.")
            elif eliminados_deuda > 0:
                messagebox.showwarning("⚠️ Filtro API: Deuda Coactiva", f"¡Alerta de SUNAT!\nEl sistema acaba de detectar y ELIMINAR automáticamente {eliminados_deuda} comprobante(s) de proveedores que registran DEUDA COACTIVA.")
            elif tipo == "COM" and not silent_alerts:
                messagebox.showinfo("Análisis SUNAT", "Análisis de Deudas Completo:\n\nNo se detectó ninguna empresa con deuda coactiva en este archivo.")
                
            
            # Primero: Si hay detracciones, mostrar popup interactivo y pausar el flujo
            if lista_detracciones:
                self.mostrar_popup_detracciones(df_forexel, df_docref, lista_detracciones, tipo, ruta_generada, cantidad_nc, eliminados_año_pasado, eliminados_deuda, silent_alerts, facturas_pendientes=facturas)
                return  # El flujo continúa dentro del callback del popup

            # Segundo: Si se requieren asignar cuentas (Compras), mostramos el popup
            if facturas:
                self.mostrar_popup_facturas(facturas, indices_a_eliminar_detrac=[])
                return
                
            # Si no hay detracciones, guardamos directamente
            guardar_excel_final(df_forexel, df_docref, [], tipo, ruta_generada)
            self.mostrar_alertas_post_guardado(ruta_generada, [], cantidad_nc, eliminados_año_pasado, eliminados_deuda, silent_alerts, tipo, df_forexel, nombre_emp, ano, mes)
                
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar el archivo:\n{e}")

    def mostrar_popup_detracciones(self, df_forexel, df_docref, lista_detracciones, tipo, ruta_generada, cantidad_nc, eliminados_año_pasado, eliminados_deuda, silent_alerts, facturas_pendientes=None):
        popup = ctk.CTkToplevel(self)
        popup.title("⚠️ ¡Detracciones Detectadas!")
        popup.geometry("780x520")
        popup.minsize(680, 420)
        popup.transient(self)
        popup.grab_set()  # Hacerla modal
        
        # Centrar ventana
        p_w, p_h = 780, 520
        x = max(10, (self.winfo_screenwidth() // 2) - (p_w // 2))
        y = max(10, (self.winfo_screenheight() // 2) - (p_h // 2))
        popup.geometry(f"{p_w}x{p_h}+{x}+{y}")
        
        lbl_info = ctk.CTkLabel(popup, text="Se han detectado comprobantes con Detracción (letra 'D').\nDecida si desea que PASEN al Excel o si se EXCLUYEN del reporte final.", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_info.pack(pady=(18, 6), padx=20)
        
        # Frame scrolleable para la lista
        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color="#1E222B", corner_radius=10)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Diccionario para guardar el estado de los switches {idx_fila: variable_booleana}
        switches_vars = {}
        
        for det in lista_detracciones:
            idx = det["idx"]
            texto = det["texto"]
            
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="#262C36", corner_radius=8, border_width=1, border_color="#334155")
            row_frame.pack(fill="x", pady=5, padx=4)
            
            lbl_doc = ctk.CTkLabel(row_frame, text=texto, font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
            lbl_doc.pack(side="left", padx=(14, 10), pady=10, fill="x", expand=True)
            
            # Botón para copiar el texto individualmente
            def hacer_copia(t=texto):
                try:
                    self.clipboard_clear()
                    self.clipboard_append(t)
                    self.update()
                    self.mostrar_toast("✔️ Copiado al portapapeles")
                except Exception as e:
                    print("Error al copiar:", e)
                    
            btn_copiar = ctk.CTkButton(row_frame, text="📋 Copiar", width=70, height=28, font=ctk.CTkFont(size=12), fg_color="#F39C12", hover_color="#D68910", cursor="hand2", command=hacer_copia)
            btn_copiar.pack(side="left", padx=(0, 14), pady=10)
            
            var = ctk.BooleanVar(value=False) # False = Excluir (Rojo), True = Pasar (Verde)
            switches_vars[idx] = var
            
            switch = ctk.CTkSwitch(
                row_frame, 
                text="🔴 EXCLUIDO", 
                variable=var, 
                onvalue=True, 
                offvalue=False,
                fg_color="#E74C3C", # ROJO por defecto cuando no se selecciona
                progress_color="#2FA572", # VERDE cuando se activa para pasar
                button_color="#FFFFFF",
                button_hover_color="#E2E8F0",
                text_color="#E74C3C",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            
            def on_switch_toggle(sw=switch, v=var):
                if v.get():
                    sw.configure(text="🟢 PASAR", text_color="#2FA572")
                else:
                    sw.configure(text="🔴 EXCLUIDO", text_color="#E74C3C")
                    
            switch.configure(command=on_switch_toggle)
            switch.pack(side="right", padx=14, pady=10)
            
        def on_aceptar():
            indices_a_eliminar = []
            for idx, var in switches_vars.items():
                if not var.get(): # Si está en False (Rojo/Apagado) -> Eliminar
                    indices_a_eliminar.append(idx)
            
            popup.destroy()
            
            if tipo == "COM" and facturas_pendientes:
                # Filtrar las facturas que el usuario decidió eliminar
                facturas_filtradas = [f for f in facturas_pendientes if f.get("idx_df") not in indices_a_eliminar]
                if facturas_filtradas:
                    self.mostrar_popup_facturas(facturas_filtradas, indices_a_eliminar_detrac=indices_a_eliminar)
                    return
            
            # Guardamos el Excel con los excluidos
            try:
                df_final = df_forexel.drop(index=indices_a_eliminar, errors='ignore') if indices_a_eliminar else df_forexel
                guardar_excel_final(df_forexel, df_docref, indices_a_eliminar, tipo, ruta_generada)
                self.mostrar_alertas_post_guardado(ruta_generada, indices_a_eliminar, cantidad_nc, eliminados_año_pasado, eliminados_deuda, silent_alerts, tipo, df_final, self.var_empresa.get(), self.var_ano.get(), self.var_mes.get())
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar el Excel:\n{e}")
                
        btn_aceptar = ctk.CTkButton(popup, text="Aceptar y Generar", fg_color="#0056b3", hover_color="#004494", font=ctk.CTkFont(weight="bold", size=14), height=40, command=on_aceptar)
        btn_aceptar.pack(pady=(5, 18))
        
    def mostrar_alertas_post_guardado(self, ruta_generada, indices_eliminados, cantidad_nc, eliminados_año_pasado, eliminados_deuda, silent_alerts, tipo, df_final=None, nombre_emp="", ano="", mes=""):
        if not silent_alerts:
            if cantidad_nc > 0:
                messagebox.showwarning("Atención Contador: Notas de Crédito", f"¡OJO!\nSe han detectado {cantidad_nc} Nota(s) de Crédito/Débito en este registro.\n\nRecuerde validar manualmente el 'Documento de Referencia' (Columnas del 27 al 30 en el Excel final) para estas notas de crédito.")
            
            if indices_eliminados:
                messagebox.showwarning("Aviso Importante: Detracciones Excluidas", f"El sistema ha EXCLUIDO {len(indices_eliminados)} comprobante(s) por detracción, tal como lo indicó en la ventana de opciones.")
                
            # Alerta de año pasado
            if eliminados_año_pasado > 0:
                messagebox.showwarning("Purga Automática: Fechas Anteriores", f"¡Atención!\nEl sistema ha eliminado automáticamente {eliminados_año_pasado} comprobante(s) del año pasado porque no tenían detracción.")

        messagebox.showinfo("Éxito", f"¡Macro generada con éxito!\n\nSe guardó en:\n{ruta_generada}")
        
        if df_final is not None:
            self.mostrar_resumen(df_final, tipo, nombre_emp, ano, mes, ruta_generada)

    def mostrar_resumen(self, df_final, tipo, nombre_emp, ano, mes, ruta_generada):
        popup = ctk.CTkToplevel(self)
        titulo = "RESUMEN DE VENTAS" if tipo == "VTA" else "RESUMEN DE COMPRAS"
        popup.title(titulo)
        popup.geometry("500x520")
        popup.grab_set()
        popup.transient(self)
        
        # Centrar popup
        p_width = 500
        p_height = 520
        x = (self.winfo_screenwidth() // 2) - (p_width // 2)
        y = (self.winfo_screenheight() // 2) - (p_height // 2)
        popup.geometry(f'{p_width}x{p_height}+{x}+{y}')
        
        # Usar columnas originales del CSV (_BI_ORIG, _IGV_ORIG, _TOTAL_ORIG)
        # que conservan los valores reales de BI Gravada, IGV/IPM y Total CP
        # incluso para boletas (cuyo IGV fue puesto en 0 solo para el formato CONCAR)
        bi_total = 0.0
        igv_total = 0.0
        total_total = 0.0
        tasas_detectadas = set()
        
        for _, row in df_final.iterrows():
            try:
                bi = float(str(row.get('_BI_ORIG', 0.0)).replace(',', '') or 0.0)
            except (ValueError, TypeError):
                bi = 0.0
            try:
                igv = float(str(row.get('_IGV_ORIG', 0.0)).replace(',', '') or 0.0)
            except (ValueError, TypeError):
                igv = 0.0
            try:
                tot = float(str(row.get('_TOTAL_ORIG', 0.0)).replace(',', '') or 0.0)
            except (ValueError, TypeError):
                tot = 0.0
            
            bi_total += bi
            igv_total += igv
            total_total += tot
            
            # Detectar tasa usando la proporción real IGV/BI del CSV
            if bi > 0 and igv > 0:
                ratio = igv / bi
                if 0.10 <= ratio <= 0.11:
                    tasas_detectadas.add("10.5 %")
                elif 0.17 <= ratio <= 0.19:
                    tasas_detectadas.add("18 %")
                
        tasas_str = " y ".join(sorted(list(tasas_detectadas))) if tasas_detectadas else "18 %"
        
        bi_total = round(bi_total, 2)
        igv_total = round(igv_total, 2)
        total_total = round(total_total, 2)
        
        bi_str = f"S/ {bi_total:,.2f}"
        igv_str = f"S/ {igv_total:,.2f}"
        tot_str = f"S/ {total_total:,.2f}"
        
        lbl_tit = ctk.CTkLabel(popup, text="Conversión completada\n\n" + titulo, font=ctk.CTkFont(size=18, weight="bold"))
        lbl_tit.pack(pady=(20, 15))
        
        frame_info = ctk.CTkFrame(popup, fg_color="transparent")
        frame_info.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame_info, text=f"Empresa: {nombre_emp}", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x")
        ctk.CTkLabel(frame_info, text=f"Periodo: 20{ano}-{mes}", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x")
        ctk.CTkLabel(frame_info, text=f"Comprobantes procesados: {len(df_final)}", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x")
        ctk.CTkLabel(frame_info, text=f"Tasa detectada: {tasas_str}", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x")
        
        frame_tot = ctk.CTkFrame(popup, fg_color="#2B2B2B", corner_radius=10)
        frame_tot.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(frame_tot, text="Base imponible:", font=ctk.CTkFont(weight="bold", size=15)).grid(row=0, column=0, padx=20, pady=(20,5), sticky="w")
        ctk.CTkLabel(frame_tot, text=bi_str, font=ctk.CTkFont(weight="bold", size=15)).grid(row=0, column=1, padx=20, pady=(20,5), sticky="e")
        
        ctk.CTkLabel(frame_tot, text="IGV / IPM:", font=ctk.CTkFont(weight="bold", size=15)).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkLabel(frame_tot, text=igv_str, font=ctk.CTkFont(weight="bold", size=15)).grid(row=1, column=1, padx=20, pady=5, sticky="e")
        
        ctk.CTkLabel(frame_tot, text="Total:", font=ctk.CTkFont(weight="bold", size=15)).grid(row=2, column=0, padx=20, pady=(5,20), sticky="w")
        ctk.CTkLabel(frame_tot, text=tot_str, font=ctk.CTkFont(weight="bold", size=15)).grid(row=2, column=1, padx=20, pady=(5,20), sticky="e")
        
        frame_tot.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(popup, text="Archivo generado correctamente.", font=ctk.CTkFont(slant="italic")).pack(pady=5)
        
        btn_cerrar = ctk.CTkButton(popup, text="Cerrar", font=ctk.CTkFont(weight="bold"), command=popup.destroy, fg_color="#E74C3C", hover_color="#C0392B", height=40)
        btn_cerrar.pack(pady=(10, 20))

    def mostrar_popup_facturas(self, facturas, indices_a_eliminar_detrac=None):
        if indices_a_eliminar_detrac is None:
            indices_a_eliminar_detrac = []
            
        popup = ctk.CTkToplevel(self)
        popup.title("Asistente de Cuentas: Facturas de Compras")
        popup.transient(self)
        
        # Dimensiones responsivas (90-94% del espacio disponible, centrado)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        if screen_w > 2560:
            screen_w = 1920
        p_width = max(980, min(int(screen_w * 0.92), 1700))
        p_height = max(620, min(int(screen_h * 0.90), 960))
        x = max(10, (screen_w - p_width) // 2)
        y = max(10, (screen_h - p_height) // 2 - 25)
        popup.geometry(f"{p_width}x{p_height}+{x}+{y}")
        popup.minsize(940, 580)
        
        self.after(200, popup.focus)
        popup.grab_set()
        
        # Cargar icono del ojo
        eye_icon_img = None
        try:
            from PIL import Image as PILImage
            icon_path = os.path.join(os.path.dirname(__file__), "icon_eye.png")
            if os.path.exists(icon_path):
                pil_img = PILImage.open(icon_path)
                eye_icon_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(24, 24))
        except Exception:
            pass
        
        def normalizar_cuenta_str(cta_str):
            if not cta_str:
                return ""
            partes = str(cta_str).strip().split(" - ")
            if len(partes) >= 2 and partes[0].strip() == partes[1].strip():
                return " - ".join([partes[0].strip()] + [p.strip() for p in partes[2:]])
            return str(cta_str).strip()

        # Load Cuentas
        ruta_cuentas = os.path.join(os.path.dirname(__file__), "cuentas_compras.json")
        todas_cuentas = []
        if os.path.exists(ruta_cuentas):
            try:
                with open(ruta_cuentas, "r", encoding="utf-8") as f:
                    db_c = json.load(f)
                    todas_cuentas = []
                    for k, v in db_c.items():
                        v_str = str(v).strip()
                        if v_str.startswith(f"{k} - ") or v_str.startswith(f"{k} "):
                            todas_cuentas.append(v_str)
                        else:
                            todas_cuentas.append(f"{k} - {v_str}")
            except:
                pass
        if not todas_cuentas:
            todas_cuentas = ["6011001 - MERCADERIAS", "6311001 - TRANSPORTE", "6561001 - SUMINISTROS", "6391001 - OTROS SERVICIOS", "3361001 - EQUIPOS"]

        # Load Historial
        ruta_cta = os.path.join(os.path.dirname(__file__), "ctacom.json")
        cta_db = {}
        if os.path.exists(ruta_cta):
            try:
                with open(ruta_cta, "r", encoding="utf-8") as f:
                    cta_db = json.load(f)
            except:
                pass
        for ruc, data in cta_db.items():
            if isinstance(data, str):
                cta_db[ruc] = {data: 1}

        # Inicializar estado de autosave y asignaciones
        self.ruta_autosave = os.path.join(os.path.dirname(__file__), "autosave_sesion.json")
        self.autosave_db = {}
        if os.path.exists(self.ruta_autosave):
            try:
                with open(self.ruta_autosave, "r", encoding="utf-8") as f:
                    self.autosave_db = json.load(f)
            except:
                pass

        self.fact_assignments = {}
        for fact in facturas:
            fid = fact["ID"]
            ruc = fact["CODENT"]
            unique_key = f"{ruc}_{fact.get('SERIE', '')}_{fact.get('NUMERO', '')}"
            
            if unique_key in self.autosave_db:
                self.fact_assignments[fid] = normalizar_cuenta_str(self.autosave_db[unique_key])
            else:
                frecuencias = cta_db.get(ruc, {})
                if frecuencias:
                    top = max(frecuencias.items(), key=lambda x: x[1])[0]
                    match = next((x for x in todas_cuentas if x.startswith(top)), f"{top} - (Historial)")
                    self.fact_assignments[fid] = normalizar_cuenta_str(match)
                else:
                    self.fact_assignments[fid] = ""
                
        self.fact_actual = ctk.StringVar(value=facturas[0]["ID"])

        # ============================================================
        # ESTRUCTURA GRID RESPONSIVA
        # ============================================================
        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1)

        # --- ENCABEZADO SUPERIOR ---
        frame_header = ctk.CTkFrame(popup, fg_color="transparent")
        frame_header.grid(row=0, column=0, sticky="ew", padx=28, pady=(16, 6))
        
        ctk.CTkLabel(frame_header, text="Asistente de Asignación de Cuentas Contables", 
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(frame_header, text="Selecciona una factura en el panel izquierdo y busca su cuenta contable en el panel derecho.", 
                     font=ctk.CTkFont(size=13), text_color="#94A3B8").pack(anchor="w", pady=(2, 0))

        # --- CONTENEDOR DE PANELES ---
        frame_paneles = ctk.CTkFrame(popup, fg_color="transparent")
        frame_paneles.grid(row=1, column=0, sticky="nsew", padx=28, pady=(6, 12))
        frame_paneles.grid_rowconfigure(0, weight=1)
        frame_paneles.grid_columnconfigure(0, weight=42)  # Panel izquierdo 42%
        frame_paneles.grid_columnconfigure(1, weight=58)  # Panel derecho 58%

        # ============================================================
        # PANEL IZQUIERDO: COMPROBANTES
        # ============================================================
        frame_izq = ctk.CTkFrame(frame_paneles, corner_radius=12, fg_color="#1E222B")
        frame_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        frame_izq.grid_rowconfigure(3, weight=1)
        frame_izq.grid_columnconfigure(0, weight=1)
        
        # Contadores
        num_facturas = sum(1 for f in facturas if f.get("TIPDOC") == "01")
        num_boletas = sum(1 for f in facturas if f.get("TIPDOC") == "03")
        num_ncs = sum(1 for f in facturas if f.get("TIPDOC") in ["07", "08"])
        num_detrac = sum(1 for f in facturas if f.get("TIENE_D"))
        
        mes_num = self.var_mes.get().strip()
        año_num = "20" + self.var_ano.get().strip()
        meses = {"01": "ENERO", "02": "FEBRERO", "03": "MARZO", "04": "ABRIL", "05": "MAYO", "06": "JUNIO", "07": "JULIO", "08": "AGOSTO", "09": "SEPTIEMBRE", "10": "OCTUBRE", "11": "NOVIEMBRE", "12": "DICIEMBRE"}
        mes_nombre = meses.get(mes_num, mes_num)
        
        # Header Periodo Linea 1: PERIODO Grande y claro
        ctk.CTkLabel(frame_izq, text=f"PERIODO: {mes_nombre} {año_num}", 
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#5D9CEC",
                     anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 2))
        
        # Header Periodo Linea 2: Contadores
        texto_contadores = f"Facturas: {num_facturas}   |   Boletas: {num_boletas}   |   NC/ND: {num_ncs}   |   Detracciones: {num_detrac}"
        ctk.CTkLabel(frame_izq, text=texto_contadores, 
                     font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8",
                     anchor="w").grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Separador visual
        ctk.CTkFrame(frame_izq, height=1, fg_color="#334155").grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))
        
        # Lista scrolleable de facturas
        scroll_facts = ctk.CTkScrollableFrame(frame_izq, corner_radius=10, fg_color="transparent")
        scroll_facts.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        self.botones_fact = {}
        self.fact_actual_previa = None
        
        def seleccionar_fact(fid):
            prev_fid = self.fact_actual.get()
            self.fact_actual.set(fid)
            
            if prev_fid and prev_fid in self.botones_fact:
                if self.fact_assignments.get(prev_fid):
                    self.botones_fact[prev_fid].configure(fg_color="#2FA572", border_width=0)
                else:
                    self.botones_fact[prev_fid].configure(fg_color="#262C36", border_width=0)
                    
            if fid in self.botones_fact:
                if self.fact_assignments.get(fid):
                    self.botones_fact[fid].configure(fg_color="#2FA572", border_width=2, border_color="#FFFFFF")
                else:
                    self.botones_fact[fid].configure(fg_color="#262C36", border_width=2, border_color="#3B8ED0")
        
        for fact in facturas:
            fid = fact["ID"]
            
            # Tarjeta de factura con diseño uniforme
            card_frame = ctk.CTkFrame(scroll_facts, corner_radius=10, fg_color="#262C36", border_width=1, border_color="#334155")
            card_frame.pack(fill="x", pady=5, padx=2)
            card_frame.grid_columnconfigure(0, weight=1)
            
            color_ini = "#2FA572" if self.fact_assignments.get(fid) else "#262C36"
            btn = ctk.CTkButton(card_frame, text="", anchor="w", fg_color=color_ini, 
                                text_color=("gray10", "gray90"), border_width=0,
                                corner_radius=8, height=76,
                                command=lambda f=fid: seleccionar_fact(f))
            btn.grid(row=0, column=0, sticky="nsew", padx=(6, 8), pady=6)
            self.botones_fact[fid] = btn
            
            # Botones de accion a la derecha
            button_group = ctk.CTkFrame(card_frame, fg_color="transparent")
            button_group.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=6)
            
            def copiar_info(f_info):
                self.clipboard_clear()
                texto_copiar = f"{f_info['CODENT']}\t{f_info['SERIE']}-{f_info['NUMERO']}\t{f_info['RAZSOC']}"
                self.clipboard_append(texto_copiar)
                self.mostrar_toast("📋 ¡Datos copiados al portapapeles!")
            
            def eliminar_factura_manual(f_info):
                if messagebox.askyesno("Confirmar Eliminación", f"¿Eliminar factura {f_info['SERIE']}-{f_info['NUMERO']}?\n\nAl eliminarla manualmente, NO aparecerá en la Macro Excel final.\n(Útil para deudas coactivas si te quedaste sin tokens de API)"):
                    indices_a_eliminar_detrac.append(f_info["idx_df"])
                    fid_del = f_info["ID"]
                    if fid_del in self.botones_fact:
                        self.botones_fact[fid_del].master.destroy()
                        del self.botones_fact[fid_del]
                    if f_info in facturas:
                        facturas.remove(f_info)
                    
                    if self.fact_actual.get() == fid_del:
                        if facturas:
                            seleccionar_fact(facturas[0]["ID"])
                        else:
                            self.lbl_fact_seleccionada.configure(text="No hay facturas pendientes.")
                    
                    if not facturas:
                        self.btn_guardar.configure(state="normal", fg_color="#2FA572")
                    else:
                        if all(self.fact_assignments.get(f["ID"]) for f in facturas):
                            self.btn_guardar.configure(state="normal", fg_color="#2FA572")
                        else:
                            self.btn_guardar.configure(state="disabled", fg_color="#4B5563")
            
            def ver_factura_local(f_info):
                if not getattr(self, "ruta_pdfs", "") or not os.path.isdir(self.ruta_pdfs):
                    respuesta = messagebox.askyesno(
                        "Carpeta no configurada", 
                        "Para ver el comprobante, primero debes indicarme en qué carpeta de tu computadora guardas los PDFs de tus facturas.\n\n¿Deseas seleccionar la carpeta ahora mismo?"
                    )
                    if respuesta:
                        self.seleccionar_carpeta_pdfs()
                    if not getattr(self, "ruta_pdfs", "") or not os.path.isdir(self.ruta_pdfs):
                        return
                    
                buscado = f"{f_info['SERIE']}-{f_info['NUMERO']}"
                ruc_buscado = str(f_info['CODENT']).strip()
                encontrado = None
                
                archivos_pdf = []
                for root, dirs, files in os.walk(self.ruta_pdfs):
                    for file in files:
                        if file.lower().endswith(('.pdf', '.xml')):
                            ruta_completa = os.path.join(root, file)
                            archivos_pdf.append(ruta_completa)
                            if buscado.lower() in file.lower():
                                encontrado = ruta_completa
                                break
                    if encontrado: break
                    
                if not encontrado:
                    self.mostrar_toast(f"🔍 Escaneando el interior de {len(archivos_pdf)} archivos...")
                    self.update()
                    try:
                        import fitz
                        for ruta in archivos_pdf:
                            if ruta.lower().endswith('.pdf'):
                                try:
                                    doc = fitz.open(ruta)
                                    texto = ""
                                    if len(doc) > 0:
                                        texto = doc[0].get_text().upper()
                                    doc.close()
                                    buscado_norm = buscado.upper().replace("-", "")
                                    texto_norm = texto.replace("-", "").replace(" ", "")
                                    if ruc_buscado in texto and (buscado.upper() in texto or buscado_norm in texto_norm):
                                        encontrado = ruta
                                        break
                                except:
                                    continue
                    except ImportError:
                        pass
                
                if encontrado:
                    try:
                        os.startfile(encontrado)
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
                else:
                    messagebox.showinfo("No Encontrado", f"No se encontró ningún comprobante para la factura {buscado} ni por nombre ni escaneando su contenido.\n\nAsegúrate de haberlo descargado en la carpeta seleccionada.")
            
            # Boton Ojo / Ver (con CTkImage PNG de alta calidad)
            if eye_icon_img:
                btn_ver = ctk.CTkButton(button_group, image=eye_icon_img, text="", width=46, height=44,
                                         fg_color="#3498DB", hover_color="#2980B9", corner_radius=8,
                                         cursor="hand2", command=lambda f=fact: ver_factura_local(f))
            else:
                btn_ver = ctk.CTkButton(button_group, text="Ver", width=46, height=44,
                                         fg_color="#3498DB", hover_color="#2980B9", corner_radius=8,
                                         font=ctk.CTkFont(size=12, weight="bold"), cursor="hand2",
                                         command=lambda f=fact: ver_factura_local(f))
            btn_ver.pack(pady=(0, 3))
            
            # Boton Eliminar
            btn_del = ctk.CTkButton(button_group, text="🗑️", width=46, height=26,
                                     fg_color="#E74C3C", hover_color="#C0392B", corner_radius=6,
                                     font=ctk.CTkFont(size=13), cursor="hand2",
                                     command=lambda f=fact: eliminar_factura_manual(f))
            btn_del.pack(pady=(0, 3))
            
            # Boton Copiar
            btn_copy = ctk.CTkButton(button_group, text="📋", width=46, height=26,
                                      fg_color="#F39C12", hover_color="#D68910", corner_radius=6,
                                      font=ctk.CTkFont(size=13), cursor="hand2",
                                      command=lambda f=fact: copiar_info(f))
            btn_copy.pack()
        
        def actualizar_textos_botones(fids_especificos=None):
            lista_fids = fids_especificos if fids_especificos is not None else [f["ID"] for f in facturas]
            for fid in lista_fids:
                fact = next((f for f in facturas if f["ID"] == fid), None)
                if not fact: continue
                
                simbolo = "$" if fact.get("MND") == "D" else "S/"
                detrac_tag = "   [⚠️ DETRACCIÓN]" if fact.get("TIENE_D") else ""
                texto_l1 = f"{fact['SERIE']}-{fact['NUMERO']}       {simbolo} {fact['VALVTA']}{detrac_tag}"
                
                razsoc_str = str(fact.get("RAZSOC", "")).strip()
                if not razsoc_str or razsoc_str.upper() in ["NAN", "NONE", "", "-"]:
                    razsoc_str = "RAZÓN SOCIAL NO INFORMADA"
                if len(razsoc_str) > 34:
                    razsoc_str = razsoc_str[:31] + "..."
                texto_l2 = f"{fact['CODENT']} - {razsoc_str}"
                
                asig = self.fact_assignments[fid]
                txt_asig = asig if asig else "⚠️ SIN CUENTA ASIGNADA"
                texto = f"{texto_l1}\n{texto_l2}\n↳ {txt_asig}"
                
                if fid in self.botones_fact:
                    self.botones_fact[fid].configure(text=texto)
                
        actualizar_textos_botones()

        # ============================================================
        # PANEL DERECHO: BUSCADOR DE CUENTAS
        # ============================================================
        frame_der = ctk.CTkFrame(frame_paneles, corner_radius=12, fg_color="#1E222B")
        frame_der.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        frame_der.grid_rowconfigure(4, weight=1)
        frame_der.grid_columnconfigure(0, weight=1)
        
        # Tarjeta de factura seleccionada
        frame_sel_info = ctk.CTkFrame(frame_der, fg_color="#262C36", corner_radius=10)
        frame_sel_info.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        frame_sel_info.grid_columnconfigure(0, weight=1)
        
        self.lbl_fact_seleccionada = ctk.CTkLabel(frame_sel_info, text="Seleccionando cuenta para: ...", 
                                                   font=ctk.CTkFont(size=14, weight="bold"), 
                                                   text_color="#F39C12", justify="center")
        self.lbl_fact_seleccionada.grid(row=0, column=0, padx=16, pady=12, sticky="ew")
        
        def on_fact_change(*args):
            fid = self.fact_actual.get()
            fact = next((f for f in facturas if f["ID"] == fid), None)
            if fact:
                doc = f"{fact['SERIE']}-{fact['NUMERO']}"
                razsoc_str = str(fact.get("RAZSOC", "")).strip()
                if not razsoc_str or razsoc_str.upper() in ["NAN", "NONE", "", "-"]:
                    razsoc_str = "RAZÓN SOCIAL NO INFORMADA"
                prov = f"{fact['CODENT']} - {razsoc_str}"
                asignado = self.fact_assignments.get(fid, "")
                txt = f"Asignando a: {doc}\n{prov}"
                if asignado:
                    txt += f"\n(Cuenta actual: {asignado})"
                self.lbl_fact_seleccionada.configure(text=txt)
                filtrar_cuentas()
            
        self.fact_actual.trace("w", on_fact_change)
        
        # Buscador
        frame_buscador = ctk.CTkFrame(frame_der, fg_color="transparent")
        frame_buscador.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
        frame_buscador.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_buscador, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, padx=(0, 10))
        self.var_buscar_cta = ctk.StringVar()
        entry_buscar = ctk.CTkEntry(frame_buscador, textvariable=self.var_buscar_cta, 
                                     placeholder_text="Ej. transporte, 63100, materia prima...",
                                     height=38, font=ctk.CTkFont(size=13))
        entry_buscar.grid(row=0, column=1, sticky="ew")
        
        # Checkbox RUC
        self.var_aplicar_todos = ctk.BooleanVar(value=False)
        chk_aplicar = ctk.CTkCheckBox(frame_der, text="Aplicar cuenta a TODAS las facturas de este mismo RUC", 
                                      variable=self.var_aplicar_todos, text_color="#F39C12", 
                                      font=ctk.CTkFont(weight="bold", size=13))
        chk_aplicar.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))
        
        # Separador visual
        ctk.CTkFrame(frame_der, height=1, fg_color="#334155").grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 8))
        
        # Lista scrolleable de cuentas
        scroll_ctas = ctk.CTkScrollableFrame(frame_der, corner_radius=8, fg_color="transparent")
        scroll_ctas.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        self.botones_cta = []
        
        def asignar_cta(cta_text):
            fid = self.fact_actual.get()
            
            fact_actual_dict = next((f for f in facturas if f["ID"] == fid), None)
            ruc_actual = fact_actual_dict["CODENT"] if fact_actual_dict else None
            
            fids_a_actualizar = [fid]
            if self.var_aplicar_todos.get() and ruc_actual:
                fids_a_actualizar = [f["ID"] for f in facturas if f["CODENT"] == ruc_actual]
            
            for id_fact in fids_a_actualizar:
                self.fact_assignments[id_fact] = normalizar_cuenta_str(cta_text)
                
                if id_fact in self.botones_fact:
                    if id_fact == self.fact_actual.get():
                        self.botones_fact[id_fact].configure(fg_color="#2FA572", border_width=2, border_color="#FFFFFF")
                    else:
                        self.botones_fact[id_fact].configure(fg_color="#2FA572", border_width=0)
                    
                try:
                    f_info = next((f for f in facturas if f["ID"] == id_fact), None)
                    if f_info:
                        unique_key = f"{f_info['CODENT']}_{f_info.get('SERIE', '')}_{f_info.get('NUMERO', '')}"
                        self.autosave_db[unique_key] = normalizar_cuenta_str(cta_text)
                except:
                    pass
            
            try:
                with open(self.ruta_autosave, "w", encoding="utf-8") as f:
                    json.dump(self.autosave_db, f, indent=4, ensure_ascii=False)
            except:
                pass
                
            actualizar_textos_botones(fids_a_actualizar)
            seleccionar_fact(fid)
            on_fact_change()
            
            siguiente = next((f for f in facturas if not self.fact_assignments[f["ID"]]), None)
            if siguiente:
                seleccionar_fact(siguiente["ID"])
                self.var_buscar_cta.set("")
            else:
                idx = next((i for i, f in enumerate(facturas) if f["ID"] == fid), -1)
                next_idx = idx + 1
                if next_idx < len(facturas):
                    seleccionar_fact(facturas[next_idx]["ID"])
                    self.var_buscar_cta.set("")
                
            if all(self.fact_assignments.get(f["ID"]) for f in facturas):
                self.btn_guardar.configure(state="normal", fg_color="#2FA572")
        
        self.ultima_busqueda_q = None
        self.ultimo_busqueda_ruc = None
        
        def filtrar_cuentas(*args):
            q = self.var_buscar_cta.get().lower()
            fid = self.fact_actual.get()
            fact = next((f for f in facturas if f["ID"] == fid), None)
            ruc = fact["CODENT"] if fact else None
            
            if self.ultima_busqueda_q == q and self.ultimo_busqueda_ruc == ruc:
                return
                
            self.ultima_busqueda_q = q
            self.ultimo_busqueda_ruc = ruc
            
            for b in self.botones_cta:
                b.destroy()
            self.botones_cta.clear()
            
            ctas_mostrar = todas_cuentas
            if not q:
                fid = self.fact_actual.get()
                fact = next((f for f in facturas if f["ID"] == fid), None)
                if fact:
                    ruc = fact["CODENT"]
                    frecuencias = cta_db.get(ruc, {})
                    if frecuencias:
                        top_5 = sorted(frecuencias.items(), key=lambda x: x[1], reverse=True)[:5]
                        top_5_codes = [c[0] for c in top_5]
                        ctas_mostrar = []
                        for code in top_5_codes:
                            match = next((x for x in todas_cuentas if x.startswith(code)), f"{code} - (Historial)")
                            ctas_mostrar.append(match)
                        for c in todas_cuentas:
                            if c not in ctas_mostrar:
                                ctas_mostrar.append(c)
            
            for c in ctas_mostrar:
                if q in c.lower():
                    b = ctk.CTkButton(scroll_ctas, text=c, anchor="w", fg_color="#262C36", 
                                      text_color=("gray10", "gray90"), hover_color="#3B8ED0",
                                      height=36, corner_radius=6, font=ctk.CTkFont(size=13),
                                      command=lambda cta=c: asignar_cta(cta))
                    b.pack(fill="x", pady=2, padx=4)
                    self.botones_cta.append(b)
                    if len(self.botones_cta) > 100:
                        break
                        
        self.var_buscar_cta.trace("w", filtrar_cuentas)
        
        # Trigger initial selection
        seleccionar_fact(facturas[0]["ID"])
        filtrar_cuentas() 
        
        # ============================================================
        # BOTÓN INFERIOR GUARDAR
        # ============================================================
        def guardar_y_continuar():
            if not all(self.fact_assignments.get(f["ID"]) for f in facturas):
                messagebox.showerror("Faltan Cuentas", "Por favor asigne una cuenta contable a todas las facturas antes de continuar.")
                return
                
            cuentas_asignadas = {}
            for fact in facturas:
                fid = fact["ID"]
                ruc = fact["CODENT"]
                seleccion = self.fact_assignments[fid]
                cuenta_ingresada = seleccion.split(" ")[0]
                cuentas_asignadas[fid] = cuenta_ingresada
                
                if ruc not in cta_db:
                    cta_db[ruc] = {}
                if cuenta_ingresada not in cta_db[ruc]:
                    cta_db[ruc][cuenta_ingresada] = 0
                cta_db[ruc][cuenta_ingresada] += 1
                
            try:
                with open(ruta_cta, "w", encoding="utf-8") as f:
                    json.dump(cta_db, f, indent=4, ensure_ascii=False)
            except:
                pass
                
            popup.destroy()
            
            try:
                ruta_csv = self.ruta_csv
                nombre_emp = self.var_empresa.get()
                empresa = self.empresas[nombre_emp]
                tipo = self.var_tipo.get()
                año = self.var_ano.get()
                mes = self.var_mes.get()
                subtipo_vta = self.var_subtipo_vta.get() if tipo == "VTA" else ""
                
                res = preparar_dataframes(ruta_csv, os.path.join(os.path.expanduser("~"), "Downloads"), tipo, empresa, año, mes, subtipo_vta, cuentas_asignadas)
                df_forexel, df_docref, ruta_generada, _, cantidad_nc, eliminados_año_pasado, _, eliminados_deuda = res
                
                df_final = df_forexel.drop(index=indices_a_eliminar_detrac, errors='ignore') if indices_a_eliminar_detrac else df_forexel
                guardar_excel_final(df_forexel, df_docref, indices_a_eliminar_detrac, tipo, ruta_generada)
                self.mostrar_alertas_post_guardado(ruta_generada, indices_a_eliminar_detrac, cantidad_nc, eliminados_año_pasado, eliminados_deuda, False, tipo, df_final, nombre_emp, año, mes)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar la macro post-asignación:\n{str(e)}")
                
        estado = "normal" if all(self.fact_assignments.values()) else "disabled"
        color = "#2FA572" if all(self.fact_assignments.values()) else "#4B5563"

        frame_bottom = ctk.CTkFrame(popup, fg_color="transparent")
        frame_bottom.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 16))
        
        self.btn_guardar = ctk.CTkButton(frame_bottom, text="💾  GUARDAR Y GENERAR MACRO", 
                                         font=ctk.CTkFont(weight="bold", size=15), 
                                         command=guardar_y_continuar, fg_color=color, state=estado, 
                                         height=48, corner_radius=10)
        self.btn_guardar.pack(fill="x", padx=40)


    def mostrar_toast(self, mensaje):
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(fg_color="#2FA572") # Verde estilo éxito
        
        lbl = ctk.CTkLabel(toast, text=mensaje, text_color="white", font=ctk.CTkFont(weight="bold", size=14))
        lbl.pack(padx=20, pady=15, fill="both", expand=True)
        
        # Darle dimensiones pequeñas fijas para evitar que se estire por toda la pantalla
        w = 550
        h = 50
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2) + 200 # Más abajo del centro
        toast.geometry(f"{w}x{h}+{x}+{y}")
        
        self.after(2000, toast.destroy)
    
if __name__ == "__main__":
    app = App()
    app.mainloop()
