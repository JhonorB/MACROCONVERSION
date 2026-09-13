import os
import pandas as pd
from django.conf import settings

def calcular_resumen(df_final, tipo):
    bi_total = 0.0
    igv_total = 0.0
    total_total = 0.0
    tasas_detectadas = set()
    
    for _, row in df_final.iterrows():
        tipdoc = str(row.get('TIPDOC', '')).strip().zfill(2)
        signo = -1.0 if tipdoc in ('07', '7') else 1.0
        
        try:
            bi = abs(float(str(row.get('_BI_ORIG', 0.0)).replace(',', '') or 0.0)) * signo
        except (ValueError, TypeError):
            bi = 0.0
        try:
            igv = abs(float(str(row.get('_IGV_ORIG', 0.0)).replace(',', '') or 0.0)) * signo
        except (ValueError, TypeError):
            igv = 0.0
        try:
            tot = abs(float(str(row.get('_TOTAL_ORIG', 0.0)).replace(',', '') or 0.0)) * signo
        except (ValueError, TypeError):
            tot = 0.0
        
        bi_total += bi
        igv_total += igv
        total_total += tot
        
        if abs(bi) > 0 and abs(igv) > 0:
            ratio = abs(igv) / abs(bi)
            if 0.10 <= ratio <= 0.11:
                tasas_detectadas.add("10.5 %")
            elif 0.17 <= ratio <= 0.19:
                tasas_detectadas.add("18 %")
                
    tasas_str = " y ".join(sorted(list(tasas_detectadas))) if tasas_detectadas else "18 %"
    
    return {
        'base_imponible': round(bi_total, 2),
        'igv': round(igv_total, 2),
        'total': round(total_total, 2),
        'tasa_detectada': tasas_str
    }

def guardar_excel_final(df_forexel, df_docref, indices_eliminar, tipo, nombre_archivo):
    if indices_eliminar:
        df_forexel = df_forexel.drop(index=indices_eliminar, errors='ignore')
        
    df_forexel = df_forexel.replace({r'\'': '', r'"': ''}, regex=True)
    df_docref = df_docref.replace({r'\'': '', r'"': ''}, regex=True)
    
    df_forexel["_es_nc"] = df_forexel["TIPDOC"].astype(str).str.strip() == "07"
    if tipo == "VTA":
        df_forexel = df_forexel.sort_values(by=["_es_nc", "TIPDOC"], ascending=[True, True], na_position='last')
    else:
        df_forexel = df_forexel.sort_values(by=["_es_nc"], ascending=[True])
    df_forexel = df_forexel.drop(columns=["_es_nc"], errors='ignore')
    
    df_forexel = df_forexel.drop(columns=["_BI_ORIG", "_IGV_ORIG", "_TOTAL_ORIG"], errors='ignore')

    def to_float_safe(series):
        return pd.to_numeric(
            series.astype(str).str.replace(',', '', regex=False).str.strip(),
            errors='coerce'
        ).fillna(0.0)

    for c in ["VALVTA", "IMPINF", "LIQIMP", "BASIMP", "ISC", "IGV", "ICBPER",
              "TASISC", "TASIGV", "RC", "CANT"]:
        if c in df_forexel.columns:
            df_forexel[c] = to_float_safe(df_forexel[c])

    if "TCVREF" in df_forexel.columns:
        def parse_tcvref(v):
            v_str = str(v).strip().upper()
            if v_str in ["V", "C"]:
                return v_str
            try:
                fv = float(str(v).replace(',', '').strip())
                return fv if fv != 0.0 else None
            except:
                return None
        df_forexel["TCVREF"] = df_forexel["TCVREF"].apply(parse_tcvref)

    for c in ["FECEMI", "FECVCT", "FECCONV", "FECREG"]:
        if c in df_forexel.columns:
            df_forexel[c] = pd.to_datetime(df_forexel[c], dayfirst=True, errors='coerce')

    exports_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    ruta_salida = os.path.join(exports_dir, nombre_archivo)

    with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
        df_forexel.to_excel(writer, sheet_name='FOREXEL', index=False)
        df_docref.to_excel(writer, sheet_name='DOCREF', index=False)
        
        fmt_general   = {"VALVTA", "IMPINF", "LIQIMP", "BASIMP"}
        fmt_coma      = {"ISC", "IGV", "ICBPER"}
        fmt_00        = {"TASISC", "TASIGV", "RC"}
        fmt_000       = {"CANT"}
        fmt_0000      = {"TCVREF"}
        fmt_fecha     = {"FECEMI", "FECVCT", "FECCONV", "FECREG", "FECEMIR"}
        fmt_texto     = {"TAST", "CTAXCOB", "CTAXPAG", "TIPENT", "TIPDOC", "DETRAC", "ESTD",
                         "TIPCONV", "DH", "TIPVAL", "CTAVTA", "AFECIRTA", "CENCOS",
                         "CODPROY", "CODPART", "TIPENT2", "CODENT2", "CODAGEN",
                         "INDRET", "TIH", "CODIH", "INFHT", "INFHTRB", "TIPCDI"}

        for sheet_name in ['FOREXEL', 'DOCREF']:
            if sheet_name not in writer.sheets:
                continue
            worksheet = writer.sheets[sheet_name]
            headers = {cell.column: cell.value for cell in worksheet[1]}

            for row in worksheet.iter_rows(min_row=2):
                for cell in row:
                    h = headers.get(cell.column)
                    if cell.value is None:
                        continue
                    try:
                        if h in fmt_general:
                            cell.number_format = 'General'
                        elif h in fmt_coma:
                            cell.number_format = '#,##0.00'
                        elif h in fmt_00:
                            cell.number_format = '0.00'
                        elif h in fmt_000:
                            cell.number_format = '0.000'
                        elif h in fmt_0000:
                            if isinstance(cell.value, (int, float)):
                                cell.number_format = '0.0000'
                            else:
                                cell.number_format = '@'
                        elif h in fmt_fecha:
                            import datetime as _dt
                            if hasattr(cell.value, 'date'):
                                cell.value = cell.value.date()
                            elif isinstance(cell.value, str):
                                try:
                                    cell.value = _dt.datetime.strptime(cell.value.split(' ')[0], '%Y-%m-%d').date()
                                except:
                                    pass
                            cell.number_format = 'dd/mm/yyyy'
                        elif h in fmt_texto:
                            if not isinstance(cell.value, str):
                                cell.value = str(cell.value)
                            cell.number_format = '@'
                    except:
                        pass

            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max(max_length + 3, 12), 50)
                worksheet.column_dimensions[column].width = adjusted_width

    return f'exports/{nombre_archivo}'
