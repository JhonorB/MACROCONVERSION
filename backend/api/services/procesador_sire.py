import pandas as pd
import os
from .verificador_deudas import verificar_deudas

def preparar_dataframes(ruta_csv, tipo, codigo_empresa, año, mes, subtipo_vta="", cuentas_asignadas=None):
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
    
    df.columns = df.columns.str.strip()
    df = df.fillna("")

    def obtener_columna(opciones):
        for opc in opciones:
            for col in df.columns:
                if opc.lower() in col.lower():
                    return df[col]
        return pd.Series([""] * len(df))

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

    def obtener_columna_contraparte_doc():
        for col in df.columns:
            cl = col.lower().replace('.', '').replace('  ', ' ').strip()
            if 'nro doc identidad' in cl or 'num doc identidad' in cl or 'nro doc ident' in cl or 'numero doc identidad' in cl:
                return df[col]
        for col in df.columns:
            cl = col.lower()
            if 'doc' in cl and not any(x in cl for x in ['tipo', 'cp', 'serie', 'fec', 'modificado', 'ref', 'dam', 'dsi', 'inicial', 'final', 'rango']):
                return df[col]
        cols_ruc = [col for col in df.columns if 'ruc' in col.lower()]
        if len(cols_ruc) > 1:
            return df[cols_ruc[1]]
        elif len(cols_ruc) == 1:
            return df[cols_ruc[0]]
        return pd.Series([""] * len(df))

    def obtener_columna_contraparte_nombre():
        for col in df.columns:
            cl = col.lower()
            if ('apellidos' in cl and '/' in cl) or 'proveedor' in cl or 'cliente' in cl:
                return df[col]
        cols_razon = [col for col in df.columns if any(x in col.lower() for x in ['razon', 'razón', 'apellidos'])]
        if len(cols_razon) > 1:
            return df[cols_razon[-1]]
        elif len(cols_razon) == 1:
            return df[cols_razon[0]]
        return pd.Series([""] * len(df))

    df_forexel["FECEMI"] = obtener_columna(["fecha de emisi", "fec. emisi"])
    df_forexel["FECVCT"] = obtener_columna(["fecha vcto", "fecha de venci", "fecha vcto/pago"])
    df_forexel["TIPDOC"] = obtener_columna(["tipo comp", "tipo de comp", "tipo cp/doc", "tipo cp"])
    df_forexel["TIPDOC"] = df_forexel["TIPDOC"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(2)
    df_forexel["TIPDOC"] = df_forexel["TIPDOC"].replace(["nan", "NaN"], "")
    df_forexel["SERIE"] = obtener_columna(["serie", "serie del cdp"])
    df_forexel["NUMERO"] = obtener_columna(["nro comp", "número de comp", "nro. comp", "nro cp", "nro. cp", "numero comp", "numero cp", "nro cp o doc"])
    
    df_forexel["CODENT"] = obtener_columna_contraparte_doc()
    nombres_originales = obtener_columna_contraparte_nombre()
    
    def limpiar_codent(row):
        ruc = str(row["CODENT"]).strip().upper()
        nom = str(row["nombre"]).strip().upper()
        if not ruc or ruc in ["NAN", "0", "-", "88888888", "00000000"] or "VARIOS" in ruc or "VARIOS" in nom or "VENTA DEL DIA" in ruc or "VENTA DEL DIA" in nom:
            return "20000000001"
        return ruc
        
    temp_df = pd.DataFrame({"CODENT": df_forexel["CODENT"], "nombre": nombres_originales})
    df_forexel["CODENT"] = temp_df.apply(limpiar_codent, axis=1)
    
    df_forexel["GLOSAD"] = ""
    df_forexel["VALVTA"] = obtener_columna(["bi gravado dg", "bi gravad", "base imponible", "base imp", "valor facturado", "valor de venta", "v. vta"])
    df_forexel["IGV"] = obtener_columna(["igv", "igv / ipm"])
    df_forexel["ISC"] = obtener_columna(["isc"])
    df_forexel["ICBPER"] = obtener_columna(["icbper"])
    
    col_total = obtener_columna(["total cp", "importe total", "total comprobante", "total"])
    
    df_forexel["TCVREF"] = obtener_columna(["tipo de cambio", "tipo cambio"])
    df_forexel["MND"] = obtener_columna(["moneda"])
    df_forexel["MND"] = df_forexel["MND"].apply(lambda x: 'S' if 'PEN' in str(x).upper() or 'SOL' in str(x).upper() else ('D' if 'USD' in str(x).upper() else x))
    is_usd = df_forexel["MND"] == "D"
    
    col_total_num = pd.to_numeric(col_total.astype(str).str.replace('-', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0.0)
    col_total = col_total_num.round(2)
    
    cols_numericas = ["VALVTA", "IGV", "ISC", "ICBPER"]
    for c in cols_numericas:
        if c in df_forexel.columns:
            val_num = pd.to_numeric(df_forexel[c].astype(str).str.replace('-', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0.0)
            df_forexel[c] = val_num.round(2)

    df_forexel["_BI_ORIG"] = df_forexel["VALVTA"].copy()
    df_forexel["_IGV_ORIG"] = df_forexel["IGV"].copy()
    df_forexel["_TOTAL_ORIG"] = col_total.copy()

    def determinar_tipval(row):
        igv = float(row["IGV"]) if str(row["IGV"]).strip() != "" else 0.0
        if igv > 0:
            return pd.Series(["A", row["VALVTA"]])
        else:
            return pd.Series(["I", row["TOTAL"]])
            
    temp_df2 = pd.DataFrame({"IGV": df_forexel["IGV"], "VALVTA": df_forexel["VALVTA"], "TOTAL": col_total})
    res_tipval = temp_df2.apply(determinar_tipval, axis=1)
    df_forexel["TIPVAL"] = res_tipval[0]
    df_forexel["VALVTA"] = res_tipval[1]
    
    if tipo == "VTA":
        mask_boleta = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2) == "03"
        df_forexel.loc[mask_boleta, "IGV"] = 0.0
        df_forexel.loc[mask_boleta, "VALVTA"] = col_total.loc[mask_boleta]
        df_forexel.loc[mask_boleta, "TIPVAL"] = "A"

    tc_numeric = pd.to_numeric(
        df_forexel["TCVREF"].astype(str).str.replace(',', '', regex=False).str.strip(),
        errors='coerce'
    ).fillna(1.0).replace(0.0, 1.0)

    col_total = col_total.where(~is_usd, (col_total / tc_numeric).round(2))
    for c in cols_numericas:
        if c in df_forexel.columns:
            df_forexel[c] = df_forexel[c].where(~is_usd, (df_forexel[c] / tc_numeric).round(2))

    df_forexel["TIPCONV"] = "V"
    df_forexel["TCVREF"] = ""
    df_forexel["FECCONV"] = ""

    mask_nc = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2).isin(["07", "08"])
    col_fec_mod = obtener_columna(["fecha emisión doc modificado", "fecha emision doc modificado", "fecha emi ref", "fecha doc modificado"])
    fechas_conv_nc = col_fec_mod.where(col_fec_mod.astype(str).str.strip() != "", df_forexel["FECEMI"])

    df_forexel.loc[mask_nc, "TIPCONV"] = "F"
    df_forexel.loc[mask_nc, "TCVREF"] = "V"
    df_forexel.loc[mask_nc, "FECCONV"] = fechas_conv_nc.loc[mask_nc]

    df_forexel["TIPDOC"] = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2)

    if tipo == "COM":
        df_forexel["IMPINF"] = obtener_columna(["valor adq. ng", "bi no gravado", "inafecto", "exonerado", "valor adq"])
        df_forexel["TIPENT"] = "P"
        df_forexel["DH"] = "D"
        
        df_forexel["TAST"] = "101"
        df_forexel["CTAXPAG"] = "4212001"
        df_forexel.loc[is_usd, "CTAXPAG"] = "4212002"
        df_forexel["FECREG"] = df_forexel["FECEMI"]
        df_forexel["ITEM"] = "0001"
        df_forexel["IRENTA"] = "01"
        df_forexel["TASIGV"] = "18.00"
        df_forexel["TASISC"] = "0.00"
        
        try:
            fec_emi_dt = pd.to_datetime(df_forexel["FECEMI"], format='%d/%m/%Y', errors='coerce')
            fec_vct_dt = pd.to_datetime(df_forexel["FECVCT"], format='%d/%m/%Y', errors='coerce')
            mask_vct_erronea = fec_vct_dt < fec_emi_dt
            df_forexel.loc[mask_vct_erronea, "FECVCT"] = df_forexel.loc[mask_vct_erronea, "FECEMI"]
        except Exception:
            pass
            
        cantidad_nc = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2).isin(["07", "08"]).sum()
        
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
                    df = df[~mask_eliminar]
                    
                    cantidad_nc = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2).isin(["07", "08"]).sum()
        except:
            pass
            
        try:
            rucs_unicos = df_forexel["CODENT"].unique()
            rucs_deudores = verificar_deudas(rucs_unicos)
            
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
        except Exception:
            pass
            
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
                    "idx": int(idx),
                    "texto": texto_detrac,
                    "fecemi": fec_str,
                    "monto": monto_str,
                    "serie_num": f"{row_elim['SERIE']}-{row_elim['NUMERO']}",
                    "ruc": str(row_elim['CODENT'])
                })
        
        if "INDRET" in df_forexel.columns:
            df_forexel.loc[mask_detraccion_filas, "INDRET"] = "D"
        
        if cuentas_asignadas is None:
            col_razsoc = obtener_columna_contraparte_nombre()
            facturas = []
            for i in range(len(df_forexel)):
                raz_val = str(col_razsoc.iloc[i]).strip()
                if not raz_val or raz_val.upper() in ["NAN", "NONE", "", "-"]:
                    raz_val = "RAZÓN SOCIAL NO INFORMADA"
                facturas.append({
                    "ID": f"{df_forexel['SERIE'].iloc[i]}-{df_forexel['NUMERO'].iloc[i]}-{df_forexel['CODENT'].iloc[i]}",
                    "idx_df": int(df_forexel.index[i]),
                    "FECEMI": df_forexel['FECEMI'].iloc[i],
                    "SERIE": df_forexel['SERIE'].iloc[i],
                    "NUMERO": df_forexel['NUMERO'].iloc[i],
                    "CODENT": df_forexel['CODENT'].iloc[i],
                    "RAZSOC": raz_val,
                    "VALVTA": str(df_forexel['VALVTA'].iloc[i]),
                    "TIPDOC": str(df_forexel['TIPDOC'].iloc[i]),
                    "TIENE_D": bool(mask_detraccion_filas.iloc[i])
                })
            return None, None, lista_detracciones, int(cantidad_nc), int(eliminados_año_pasado), facturas, int(eliminados_deuda)
        else:
            def aplicar_cta(row):
                id_fact = f"{row['SERIE']}-{row['NUMERO']}-{row['CODENT']}"
                return cuentas_asignadas.get(id_fact, "6011001")
                
            df_forexel["CTACOM"] = df_forexel.apply(aplicar_cta, axis=1)
                
        def asignar_cencos(cta):
            cta_str = str(cta).strip()
            if cta_str.startswith(("62", "63", "65", "67")):
                return "V0000001"
            return ""
            
        df_forexel["CENCOS"] = df_forexel["CTACOM"].apply(asignar_cencos)
        
        if "IMPINF" in df_forexel.columns:
            val_num = pd.to_numeric(df_forexel["IMPINF"].astype(str).str.replace('-', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0.0)
            df_forexel["IMPINF"] = val_num.round(2)
    else: # VTA
        df_forexel["TIPENT"] = "C"
        df_forexel["DH"] = "H"
        df_forexel["ESTD"] = "V"
        df_forexel["DETRAC"] = "N"
        
        if subtipo_vta == "SERVICIOS":
            df_forexel["CTAVTA"] = "7032101"
            df_forexel["GLOSAD"] = "SERVICIOS"
        elif subtipo_vta == "PRODUCTOS TERMINADOS":
            df_forexel["CTAVTA"] = "7022101"
            df_forexel["GLOSAD"] = "PRODUCTOS TERMINADOS"
        else:
            df_forexel["CTAVTA"] = "7012101"
            df_forexel["GLOSAD"] = "MERCADERIA"
            
        df_forexel["TAST"] = "001"
        df_forexel["CTAXCOB"] = "1212001"
        df_forexel["TASISC"] = "0.00"
        df_forexel["TASIGV"] = "18.00"
        df_forexel["RC"] = "0.00"
        df_forexel["CANT"] = "0.000"
        df_forexel["AFECIRTA"] = "03"

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

    mask_nc = df_forexel["TIPDOC"].astype(str).str.strip() == "07"
    if tipo == "COM":
        df_forexel.loc[mask_nc, "DH"] = "H"
    else:
        df_forexel.loc[mask_nc, "DH"] = "D"
            
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
    
    mask_nc_nd = df_forexel["TIPDOC"].isin(["07", "08"])
    df_docref = df_docref[mask_nc_nd]

    cantidad_nc_global = df_forexel["TIPDOC"].astype(str).str.strip().str.zfill(2).isin(["07", "08"]).sum()
    
    return df_forexel, df_docref, lista_detracciones, int(cantidad_nc_global), int(eliminados_año_pasado), [], int(eliminados_deuda)
