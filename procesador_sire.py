import pandas as pd
import os
import json
import urllib.request
import urllib.error

def verificar_deudas(lista_rucs, token_apiperu, token_jsonpe):
    ruta_cache = os.path.join(os.path.dirname(__file__), "cache_deudas.json")
    cache = {}
    if os.path.exists(ruta_cache):
        try:
            with open(ruta_cache, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except:
            pass
            
    rucs_con_deuda = []
    rucs_a_consultar = []
    
    for ruc in lista_rucs:
        if str(ruc) in cache:
            if cache[str(ruc)]:
                rucs_con_deuda.append(ruc)
        else:
            rucs_a_consultar.append(ruc)
            
    if (not token_apiperu and not token_jsonpe) or not rucs_a_consultar:
        return rucs_con_deuda
        
    url_apiperu = "https://apiperu.dev/api/ruc_deuda_coactiva"
    url_jsonpe = "https://api.json.pe/api/ruc/deuda-coactiva"
    
    for ruc in rucs_a_consultar:
        ruc_str = str(ruc).strip()
        if len(ruc_str) != 11:
            cache[ruc_str] = False
            continue
            
        payload = json.dumps({"ruc": ruc_str}).encode('utf-8')
        
        tiene_deuda = False
        hubo_error_auth = False
        
        # 1. Intentar con apiperu.dev
        if token_apiperu:
            req = urllib.request.Request(url_apiperu, data=payload, method="POST")
            req.add_header("Accept", "application/json")
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {token_apiperu}")
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    if res_data.get("success", False):
                        if res_data.get("data"):
                            tiene_deuda = True
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    hubo_error_auth = True
            except Exception:
                pass
                
        # 2. Intentar con api.json.pe si la primera falló o dijo que no hay deuda
        if not tiene_deuda and token_jsonpe:
            req2 = urllib.request.Request(url_jsonpe, data=payload, method="POST")
            req2.add_header("Accept", "application/json")
            req2.add_header("Content-Type", "application/json")
            req2.add_header("Authorization", f"Bearer {token_jsonpe}")
            try:
                with urllib.request.urlopen(req2, timeout=5) as response:
                    hubo_error_auth = False # La segunda API funcionó correctamente
                    res_data = json.loads(response.read().decode('utf-8'))
                    if res_data.get("success", False) or "data" in res_data:
                        if res_data.get("data"):
                            tiene_deuda = True
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    hubo_error_auth = True
            except Exception:
                pass
                
        if hubo_error_auth and not tiene_deuda:
            return None # Ambos fallaron (o el único falló) por error de Auth
            
        cache[ruc_str] = tiene_deuda
        if tiene_deuda:
            rucs_con_deuda.append(ruc)
            
    try:
        with open(ruta_cache, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4)
    except:
        pass
        
    return rucs_con_deuda


def preparar_dataframes(ruta_csv, directorio_salida, tipo, codigo_empresa, año, mes, subtipo_vta="", cuentas_asignadas=None):
    """
    Lee el archivo CSV (SIRE) y genera el archivo Excel con las hojas y columnas especificadas.
    """
    try:
        # Intentar cargar con distintos encodings y separadores
        df = None
        for enc in ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']:
            for sep in ['|', '\t', ';', ',']:
                try:
                    temp = pd.read_csv(ruta_csv, sep=sep, encoding=enc, on_bad_lines='skip', dtype=str)
                    if len(temp.columns) > 1:
                        df = temp
                        break
                except Exception:
                    pass
            if df is not None:
                break
                
        if df is None:
            raise ValueError("No se pudo leer el archivo CSV con ningún separador estándar.")
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        # Rellenar nulos con string vacío
        df = df.fillna("")

        # Helper para encontrar la columna correcta
        def obtener_columna(opciones):
            for opc in opciones:
                for col in df.columns:
                    if opc.lower() in col.lower():
                        return df[col]
            return pd.Series([""] * len(df))

        # Configurar las columnas de FOREXEL según el tipo
        if tipo == "COM":
            columnas_forexel = [
                "TAST", "FECREG", "CTAXPAG", "TIPENT", "CODENT", "TIPDOC", "SERIE", "NUMERO",
                "FECEMI", "FECVCT", "MND", "TIPCONV", "FECCONV", "TCVREF", "ITEM", "CTACOM",
                "TIPVAL", "DH", "CENCOS", "VALVTA", "ISC", "IGV", "ICBPER", "DEPDTRA", "RET4TA",
                "IRENTA", "TASISC", "TASIGV", "INDRET", "NDDET", "FDDET", "CODDET", "TASDET",
                "BASDET", "TIH", "CODIH", "GLOSAD", "CODPRY", "CODPP", "LIQIMP", "INFHT",
                "CLBBSS", "MEPG", "IMPINF", "TEREF", "CODEREF", "TIPCDI"
            ]
        else: # VTA
            columnas_forexel = [
                "TAST", "CTAXCOB", "TIPENT", "CODENT", "TIPDOC", "SERIE", "NUMERO", "FECEMI",
                "FECVCT", "DETRAC", "ESTD", "TIPCONV", "FECCONV", "TCVREF", "MND", "CTAVTA",
                "DH", "TIPVAL", "TRFGRA", "VALVTA", "ISC", "IGV", "ICBPER", "GLOSAD",
                "TASISC", "TASIGV", "RC", "CANT", "AFECIRTA", "CENCOS", "CODPROY", "CODPART",
                "TIPENT2", "CODENT2", "CODAGEN", "INFHTRB", "TIPCDI"
            ]
        
        df_forexel = pd.DataFrame(columns=columnas_forexel)
        eliminados_año_pasado = 0
        eliminados_deuda = 0
        lista_detracciones = []

        # Helpers para encontrar columnas del Proveedor / Cliente (Contraparte)
        # y evitar confundirlas con la Empresa Declarante (propietaria del registro)
        def obtener_columna_contraparte_doc():
            # 1. Buscar la columna específica del proveedor/cliente
            for col in df.columns:
                cl = col.lower().replace('.', '').replace('  ', ' ').strip()
                if 'nro doc identidad' in cl or 'num doc identidad' in cl or 'nro doc ident' in cl or 'numero doc identidad' in cl:
                    return df[col]
                    
            # 2. Buscar columnas con 'doc' que NO sean tipo, cp, serie, modificado o referencia
            for col in df.columns:
                cl = col.lower()
                if 'doc' in cl and not any(x in cl for x in ['tipo', 'cp', 'serie', 'fec', 'modificado', 'ref', 'dam', 'dsi', 'inicial', 'final', 'rango']):
                    return df[col]
                    
            # 3. Si hay más de una columna con 'ruc', la primera es la empresa declarante y la segunda es el proveedor
            cols_ruc = [col for col in df.columns if 'ruc' in col.lower()]
            if len(cols_ruc) > 1:
                return df[cols_ruc[1]]
            elif len(cols_ruc) == 1:
                return df[cols_ruc[0]]
                
            return pd.Series([""] * len(df))

        def obtener_columna_contraparte_nombre():
            # 1. En SIRE el proveedor SIEMPRE tiene la barra '/' o las palabras clave 'proveedor' / 'cliente'
            # Ejemplo: 'Apellidos Nombres/ Razón  Social'
            for col in df.columns:
                cl = col.lower()
                if ('apellidos' in cl and '/' in cl) or 'proveedor' in cl or 'cliente' in cl:
                    return df[col]
                    
            # 2. Si no tiene barra '/', buscar columnas con 'razon' o 'razón' o 'apellidos'
            # En SIRE: Col 1 es la empresa declarante ('Apellidos y Nombres o Razón social')
            # y Col 13 es el proveedor ('Apellidos Nombres/ Razón Social')
            cols_razon = [col for col in df.columns if any(x in col.lower() for x in ['razon', 'razón', 'apellidos'])]
            if len(cols_razon) > 1:
                return df[cols_razon[-1]]
            elif len(cols_razon) == 1:
                return df[cols_razon[0]]
                
            return pd.Series([""] * len(df))

        # Mapeo básico de datos desde SIRE hacia FOREXEL
        df_forexel["FECEMI"] = obtener_columna(["fecha de emisi", "fec. emisi"])
        df_forexel["FECVCT"] = obtener_columna(["fecha vcto", "fecha de venci", "fecha vcto/pago"])
        df_forexel["TIPDOC"] = obtener_columna(["tipo comp", "tipo de comp", "tipo cp/doc", "tipo cp"])
        # Convertir a texto, limpiar decimales fantasma de pandas (ej. 1.0) y rellenar con 0 a la izquierda
        df_forexel["TIPDOC"] = df_forexel["TIPDOC"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(2)
        df_forexel["TIPDOC"] = df_forexel["TIPDOC"].replace(["nan", "NaN"], "")
        df_forexel["SERIE"] = obtener_columna(["serie", "serie del cdp"])
        df_forexel["NUMERO"] = obtener_columna(["nro comp", "número de comp", "nro. comp", "nro cp", "nro. cp", "numero comp", "numero cp", "nro cp o doc"])
        
        df_forexel["CODENT"] = obtener_columna_contraparte_doc()
        nombres_originales = obtener_columna_contraparte_nombre()
        
        # Limpieza de CODENT (RUC) para boletas o clientes varios
        def limpiar_codent(row):
            ruc = str(row["CODENT"]).strip().upper()
            nom = str(row["nombre"]).strip().upper()
            # Si el RUC está vacío, tiene un guión, ceros/ochos genéricos, o contiene palabras clave como 'VARIOS'
            if not ruc or ruc in ["NAN", "0", "-", "88888888", "00000000"] or "VARIOS" in ruc or "VARIOS" in nom or "VENTA DEL DIA" in ruc or "VENTA DEL DIA" in nom:
                return "20000000001"
            return ruc
            
        temp_df = pd.DataFrame({"CODENT": df_forexel["CODENT"], "nombre": nombres_originales})
        df_forexel["CODENT"] = temp_df.apply(limpiar_codent, axis=1)
        
        # Para compras (COM), la GLOSAD debe estar vacía según requerimiento.
        # En ventas (VTA), se sobrescribirá más adelante según el subtipo seleccionado.
        df_forexel["GLOSAD"] = ""
        # Valores numéricos / monetarios comunes
        df_forexel["VALVTA"] = obtener_columna(["bi gravado dg", "bi gravad", "base imponible", "base imp", "valor facturado", "valor de venta", "v. vta"])
        df_forexel["IGV"] = obtener_columna(["igv", "igv / ipm"])
        df_forexel["ISC"] = obtener_columna(["isc"])
        df_forexel["ICBPER"] = obtener_columna(["icbper"])
        
        # Lógica automática para TIPVAL y ajuste de VALVTA para Inafectos
        col_total = obtener_columna(["total cp", "importe total", "total comprobante", "total"])
        
        df_forexel["TCVREF"] = obtener_columna(["tipo de cambio", "tipo cambio"])
        df_forexel["MND"] = obtener_columna(["moneda"])
        df_forexel["MND"] = df_forexel["MND"].apply(lambda x: 'S' if 'PEN' in str(x).upper() or 'SOL' in str(x).upper() else ('D' if 'USD' in str(x).upper() else x))
        
        # --- Limpieza y Conversión de Montos Numéricos ---
        # El SIRE siempre reporta en Soles. Si la factura original es en Dólares (MND="D"), 
        # debemos dividir entre el TCVREF para devolver los valores a dólares puros, 
        # porque el sistema contable (CONCAR) los multiplicará al ingresarlos.
        col_total_num = pd.to_numeric(col_total.astype(str).str.replace('-', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0.0)
        
        tc_numeric = pd.to_numeric(df_forexel["TCVREF"], errors='coerce').fillna(1.0).replace(0, 1.0)
        is_usd = df_forexel["MND"] == "D"
        
        col_total_num = col_total_num.where(~is_usd, col_total_num / tc_numeric)
        col_total = col_total_num.round(2)
        
        cols_numericas = ["VALVTA", "IGV", "ISC", "ICBPER"]
        for c in cols_numericas:
            if c in df_forexel.columns:
                val_num = pd.to_numeric(df_forexel[c].astype(str).str.replace('-', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0.0)
                val_num = val_num.where(~is_usd, val_num / tc_numeric)
                df_forexel[c] = val_num.round(2)
        # ------------------------------------

        # Guardar valores originales del CSV (antes de transformar boletas/inafectas)
        # para usarlos en el resumen y la detección de TASIGV
        df_forexel["_BI_ORIG"] = df_forexel["VALVTA"].copy()
        df_forexel["_IGV_ORIG"] = df_forexel["IGV"].copy()
        df_forexel["_TOTAL_ORIG"] = col_total.copy()

        def determinar_tipval(row):
            igv = float(row["IGV"]) if str(row["IGV"]).strip() != "" else 0.0
            if igv > 0:
                # Si hay IGV (Gravada o Mixta), la Base Imponible Gravada se mantiene en VALVTA
                return pd.Series(["A", row["VALVTA"]])
            else:
                # Si no hay IGV (100% Inafecta), el usuario espera que VALVTA tenga el monto total
                return pd.Series(["I", row["TOTAL"]])
                
        temp_df2 = pd.DataFrame({"IGV": df_forexel["IGV"], "VALVTA": df_forexel["VALVTA"], "TOTAL": col_total})
        res_tipval = temp_df2.apply(determinar_tipval, axis=1)
        df_forexel["TIPVAL"] = res_tipval[0]
        df_forexel["VALVTA"] = res_tipval[1]
        
        # Regla especial para Boletas (03) en Ventas:
        # El IGV no se desglosa, el Total va íntegro en VALVTA y TIPVAL se mantiene en 'A'
        if tipo == "VTA":
            mask_boleta = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2) == "03"
            df_forexel.loc[mask_boleta, "IGV"] = 0.0
            df_forexel.loc[mask_boleta, "VALVTA"] = col_total.loc[mask_boleta]
            df_forexel.loc[mask_boleta, "TIPVAL"] = "A"

        # Valores por defecto y específicos según tipo
        mask_soles = df_forexel["MND"] == "S"
        df_forexel["TIPCONV"] = "V"
        mask_nc = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2) == "07"
        df_forexel.loc[mask_nc, "TIPCONV"] = "F"
        
        df_forexel["FECCONV"] = ""
        df_forexel.loc[mask_nc, "FECCONV"] = df_forexel.loc[mask_nc, "FECEMI"]
        
        # El usuario indica que TCVREF va vacío, excepto en Notas de Crédito que lleva "V"
        df_forexel["TCVREF"] = ""
        df_forexel.loc[mask_nc, "TCVREF"] = "V"
        
        if tipo == "COM":
            df_forexel["IMPINF"] = obtener_columna(["valor adq. ng", "bi no gravado", "inafecto", "exonerado", "valor adq"])
            df_forexel["TIPENT"] = "P" # Proveedor
            df_forexel["DH"] = "D" # Debe
            
            # Nuevos valores predeterminados para COM (segun formato Concar)
            df_forexel["TAST"] = "101"
            df_forexel["CTAXPAG"] = "4212001"
            # Si es dólares, la cuenta por pagar es 4212002
            df_forexel.loc[is_usd, "CTAXPAG"] = "4212002"
            df_forexel["FECREG"] = df_forexel["FECEMI"]
            df_forexel["ITEM"] = "0001"
            df_forexel["IRENTA"] = "01"
            df_forexel["TASIGV"] = "18.00"
            df_forexel["TASISC"] = "0.00"
            
            # Corrección de Fecha de Vencimiento ilógica de SUNAT
            # Si FECVCT es anterior a FECEMI, se iguala a FECEMI
            try:
                fec_emi_dt = pd.to_datetime(df_forexel["FECEMI"], format='%d/%m/%Y', errors='coerce')
                fec_vct_dt = pd.to_datetime(df_forexel["FECVCT"], format='%d/%m/%Y', errors='coerce')
                mask_vct_erronea = fec_vct_dt < fec_emi_dt
                df_forexel.loc[mask_vct_erronea, "FECVCT"] = df_forexel.loc[mask_vct_erronea, "FECEMI"]
            except Exception:
                pass
                
            # Contar Notas de Crédito procesadas tempranamente
            cantidad_nc = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2).isin(["07", "08"]).sum()
            
            # Filtro de Año Pasado (Eliminar si es año anterior y NO tiene detracción)
            try:
                año_completo = "20" + str(año)
                fechas_años = df_forexel["FECEMI"].astype(str).str.strip().str[-4:]
                mask_año_pasado = fechas_años.str.isdigit() & (fechas_años < año_completo)
                
                if mask_año_pasado.any():
                    def es_detrac_col_old(val):
                        v = str(val).strip().upper()
                        return v == 'D' or v == '1'
                    
                    mask_detraccion_prev = pd.Series([False] * len(df), index=df.index)
                    cols_detrac_prev = [col for col in df.columns if "detrac" in col.lower()]
                    for col in cols_detrac_prev:
                        mask_detraccion_prev = mask_detraccion_prev | df[col].apply(es_detrac_col_old)
                        
                    if not mask_detraccion_prev.any():
                        mask_detraccion_prev = df.apply(lambda row: row.map(lambda x: str(x).strip().upper() == 'D').any(), axis=1)

                    mask_eliminar = mask_año_pasado & (~mask_detraccion_prev)
                    eliminados_año_pasado = mask_eliminar.sum()
                    
                    if eliminados_año_pasado > 0:
                        df_forexel = df_forexel[~mask_eliminar]
                        df = df[~mask_eliminar] # Alineamos el df original
                        
                        # Re-calcular NC por si alguna fue eliminada (aunque no debería)
                        cantidad_nc = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2).isin(["07", "08"]).sum()
            except:
                pass
                
            # Filtro de Deuda Coactiva
            try:
                ruta_token = os.path.join(os.path.dirname(__file__), "api_token.txt")
                token_api = ""
                if os.path.exists(ruta_token):
                    with open(ruta_token, "r", encoding="utf-8") as f:
                        token_api = f.read().strip()
                        
                ruta_token2 = os.path.join(os.path.dirname(__file__), "api_token2.txt")
                token_jsonpe = ""
                if os.path.exists(ruta_token2):
                    with open(ruta_token2, "r", encoding="utf-8") as f:
                        token_jsonpe = f.read().strip()
                
                if token_api or token_jsonpe:
                    rucs_unicos = df_forexel["CODENT"].unique()
                    rucs_deudores = verificar_deudas(rucs_unicos, token_api, token_jsonpe)
                    
                    if rucs_deudores is None:
                        eliminados_deuda = -1
                    elif rucs_deudores:
                        mask_deuda = df_forexel["CODENT"].isin(rucs_deudores)
                        eliminados_deuda_temp = mask_deuda.sum()
                        if eliminados_deuda_temp > 0:
                            eliminados_deuda = eliminados_deuda_temp
                            df_forexel = df_forexel[~mask_deuda]
                            df = df[~mask_deuda]
                            cantidad_nc = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2).isin(["07", "08"]).sum()
                else:
                    eliminados_deuda = -1
            except Exception:
                pass
                
            # Detectar filas con detracción de la manera más sencilla posible (pedido del usuario)
            def es_detrac_columna(val):
                v = str(val).strip().upper()
                return v == 'D' or v == '1'

            def es_detrac_fila(val):
                v = str(val).strip().upper()
                return v == 'D'
                
            cols_detrac = [col for col in df.columns if "detrac" in col.lower()]
            mask_detraccion_filas = pd.Series([False] * len(df), index=df.index)
            for col in cols_detrac:
                mask_detraccion_filas = mask_detraccion_filas | df[col].apply(es_detrac_columna)
                
            # Si no se encontró en la columna específica, buscamos celda por celda en TODA la fila
            if not mask_detraccion_filas.any():
                mask_detraccion_filas = df.apply(lambda row: row.map(es_detrac_fila).any(), axis=1)
                
            if mask_detraccion_filas.any():
                df_detraccion = df_forexel[mask_detraccion_filas]
                for idx, row_elim in df_detraccion.iterrows():
                    fec_str = str(row_elim.get('FECEMI', '')).strip()
                    monto_str = str(row_elim.get('VALVTA', '')).strip()
                    mnd_sym = "$" if str(row_elim.get("MND", "")).upper() == "D" else "S/"
                    
                    texto_detrac = f"{row_elim['TIPDOC']}-{row_elim['SERIE']}-{row_elim['NUMERO']} (RUC {row_elim['CODENT']})"
                    if fec_str and fec_str.lower() != 'nan':
                        texto_detrac += f"   |   📅 Fecha: {fec_str}"
                    if monto_str and monto_str.lower() != 'nan':
                        texto_detrac += f"   |   {mnd_sym} {monto_str}"
                        
                    lista_detracciones.append({
                        "idx": idx,
                        "texto": texto_detrac,
                        "fecemi": fec_str,
                        "monto": monto_str,
                        "serie_num": f"{row_elim['SERIE']}-{row_elim['NUMERO']}",
                        "ruc": str(row_elim['CODENT'])
                    })
            
            # Si el usuario decide pasar estas facturas en Compras, el CONCAR necesita que la columna INDRET lleve la 'D'
            if tipo == "COM" and "INDRET" in df_forexel.columns:
                df_forexel.loc[mask_detraccion_filas, "INDRET"] = "D"
            
            # Lógica para extraer todas las facturas y enviarlas a la UI para revisión/asignación
            if cuentas_asignadas is None:
                col_razsoc = obtener_columna_contraparte_nombre()
                facturas = []
                for i in range(len(df_forexel)):
                    raz_val = str(col_razsoc.iloc[i]).strip()
                    if not raz_val or raz_val.upper() in ["NAN", "NONE", "", "-"]:
                        raz_val = "RAZÓN SOCIAL NO INFORMADA"
                    facturas.append({
                        "ID": f"{df_forexel['SERIE'].iloc[i]}-{df_forexel['NUMERO'].iloc[i]}-{df_forexel['CODENT'].iloc[i]}",
                        "idx_df": df_forexel.index[i],
                        "FECEMI": df_forexel['FECEMI'].iloc[i],
                        "SERIE": df_forexel['SERIE'].iloc[i],
                        "NUMERO": df_forexel['NUMERO'].iloc[i],
                        "CODENT": df_forexel['CODENT'].iloc[i],
                        "RAZSOC": raz_val,
                        "VALVTA": str(df_forexel['VALVTA'].iloc[i]),
                        "TIPDOC": str(df_forexel['TIPDOC'].iloc[i]),
                        "TIENE_D": bool(mask_detraccion_filas.iloc[i])
                    })
                return None, None, None, lista_detracciones, int(cantidad_nc), int(eliminados_año_pasado), facturas, int(eliminados_deuda)
            else:
                # Si ya vienen las cuentas asignadas desde la UI
                def aplicar_cta(row):
                    id_fact = f"{row['SERIE']}-{row['NUMERO']}-{row['CODENT']}"
                    return cuentas_asignadas.get(id_fact, "6011001")
                    
                df_forexel["CTACOM"] = df_forexel.apply(aplicar_cta, axis=1)
                    
            # Lógica para CENCOS automático
            def asignar_cencos(cta):
                cta_str = str(cta).strip()
                if cta_str.startswith(("62", "63", "65", "67")):
                    return "V0000001"
                return ""
                
            df_forexel["CENCOS"] = df_forexel["CTACOM"].apply(asignar_cencos)
            
            # Limpiar y convertir IMPINF (solo está en COM)
            if "IMPINF" in df_forexel.columns:
                val_num = pd.to_numeric(df_forexel["IMPINF"].astype(str).str.replace('-', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0.0)
                val_num = val_num.where(~is_usd, val_num / tc_numeric)
                df_forexel["IMPINF"] = val_num.round(2)
        else: # VTA
            df_forexel["TIPENT"] = "C" # Cliente
            df_forexel["DH"] = "H" # Haber
            df_forexel["ESTD"] = "V" # Vigente
            df_forexel["DETRAC"] = "N" # No sujeto por defecto
            
            if subtipo_vta == "SERVICIOS":
                df_forexel["CTAVTA"] = "7032101"
                df_forexel["GLOSAD"] = "SERVICIOS"
            elif subtipo_vta == "PRODUCTOS TERMINADOS":
                df_forexel["CTAVTA"] = "7022101"
                df_forexel["GLOSAD"] = "PRODUCTOS TERMINADOS"
            else: # "MERCADERIA" o por defecto
                df_forexel["CTAVTA"] = "7012101"
                df_forexel["GLOSAD"] = "MERCADERIA"
                
            df_forexel["TAST"] = "001" # Tipo de asiento por defecto para ventas
            df_forexel["CTAXCOB"] = "1212001" # Cuenta por cobrar por defecto para ventas
            df_forexel["TASISC"] = "0.00"
            df_forexel["TASIGV"] = "18.00"
            df_forexel["RC"] = "0.00"
            df_forexel["CANT"] = "0.000"
            df_forexel["AFECIRTA"] = "03"

        # Las listas y marcas de detracciones ya se calcularon arriba
        
        # Calcular TASIGV dinámicamente (10.50 o 18.00) usando valores ORIGINALES del CSV
        def calcular_tasigv(row):
            try:
                valvta = float(str(row.get("_BI_ORIG", "0")).replace(',', ''))
                igv = float(str(row.get("_IGV_ORIG", "0")).replace(',', ''))
                if valvta > 0 and igv > 0:
                    ratio = igv / valvta
                    if 0.10 <= ratio <= 0.11:
                        return "10.50"
            except:
                pass
            return "18.00"
            
        df_forexel["TASIGV"] = df_forexel.apply(calcular_tasigv, axis=1)

        # Invertir DH para Notas de Crédito (07)
        mask_nc = df_forexel["TIPDOC"].astype(str).str.strip() == "07"
        if tipo == "COM":
            df_forexel.loc[mask_nc, "DH"] = "H"
        else:
            df_forexel.loc[mask_nc, "DH"] = "D"
                
        # Construir hoja DOCREF (Documentos de Referencia para Notas Crédito/Débito)
        columnas_docref = ["TIPENT", "CODENT", "TIPDOC", "SERIE", "NUMERO", "TDR", "SEREF", "NUMREF", "FECEMIR", "BASIMP", "IGV"]
        df_docref = pd.DataFrame(columns=columnas_docref)
        
        df_docref["TIPENT"] = df_forexel["TIPENT"]
        df_docref["CODENT"] = df_forexel["CODENT"]
        df_docref["TIPDOC"] = df_forexel["TIPDOC"]
        df_docref["SERIE"] = df_forexel["SERIE"]
        df_docref["NUMERO"] = df_forexel["NUMERO"]
        df_docref["BASIMP"] = df_forexel["VALVTA"]
        df_docref["IGV"] = df_forexel["IGV"]
        
        df_docref["TDR"] = obtener_columna(["tipo cp modificado", "tipo doc ref"])
        df_docref["SEREF"] = obtener_columna(["serie cp modificado", "serie ref"])
        df_docref["NUMREF"] = obtener_columna(["nro cp modificado", "nro doc ref", "nro comp modificado"])
        df_docref["FECEMIR"] = obtener_columna(["fecha emisión doc modificado", "fecha emision doc modificado", "fecha emi ref"])
        
        # Filtramos solo las filas que realmente tengan datos de referencia (si el tipo de doc original es NC o ND, ej. '07' o '08')
        mask_nc_nd = df_forexel["TIPDOC"].isin(["07", "08"])
        df_docref = df_docref[mask_nc_nd]

        # Generar nombre del archivo (Aseguramos .xlsx según requerimiento final)
        nombre_archivo = f"{tipo}{codigo_empresa}{año}{mes}.xlsx"
        ruta_salida = os.path.join(directorio_salida, nombre_archivo)
        
        # Contar Notas de Crédito procesadas globales (robusto)
        cantidad_nc_global = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2).isin(["07", "08"]).sum()
        # Devolvemos 8 elementos (incluyendo una lista vacía para facturas, ya que ya fueron asignadas)
        return df_forexel, df_docref, ruta_salida, lista_detracciones, int(cantidad_nc_global), int(eliminados_año_pasado), [], int(eliminados_deuda)
    except Exception as e:
        raise Exception(f"Error al procesar el archivo: {str(e)}")

def guardar_excel_final(df_forexel, df_docref, indices_eliminar, tipo, ruta_salida):
    if indices_eliminar:
        df_forexel = df_forexel.drop(index=indices_eliminar, errors='ignore')
        
    # Limpieza final sugerida (sin comillas, sin apóstrofes)
    df_forexel = df_forexel.replace({'\'': '', '"': ''}, regex=True)
    df_docref = df_docref.replace({'\'': '', '"': ''}, regex=True)
    
    # Mover Notas de Crédito (TIPDOC = 07) al final de la hoja
    df_forexel["_es_nc"] = df_forexel["TIPDOC"].astype(str).str.strip() == "07"
    if tipo == "VTA":
        df_forexel = df_forexel.sort_values(by=["_es_nc", "TIPDOC"], ascending=[True, True], na_position='last')
    else:
        df_forexel = df_forexel.sort_values(by=["_es_nc"], ascending=[True])
    df_forexel = df_forexel.drop(columns=["_es_nc"], errors='ignore')
    
    # Eliminar columnas internas antes de escribir al Excel
    df_forexel = df_forexel.drop(columns=["_BI_ORIG", "_IGV_ORIG", "_TOTAL_ORIG"], errors='ignore')

    with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
        df_forexel.to_excel(writer, sheet_name='FOREXEL', index=False)
        df_docref.to_excel(writer, sheet_name='DOCREF', index=False)
        
        # Auto-ajustar el ancho de las columnas en FOREXEL
        worksheet = writer.sheets['FOREXEL']
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter # Ej: 'A', 'X', 'AA'
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max(max_length + 3, 12), 50)
            worksheet.column_dimensions[column].width = adjusted_width
