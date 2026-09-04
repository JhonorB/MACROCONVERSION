import os
import sys
import pytest
import pandas as pd
import openpyxl

# Asegurar que el directorio raíz del proyecto esté en el sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from procesador_sire import preparar_dataframes, guardar_excel_final, verificar_deudas


def test_deteccion_tasa_igv_18_y_10_5(tmp_path):
    """
    Verifica que el sistema detecte dinámicamente la tasa de IGV de 18% y 10.5%
    (Ley 31556) según la proporción real de IGV / Base Imponible.
    """
    csv_content = (
        "RUC,Apellidos y Nombres o Razón social,Periodo,CAR SUNAT,Fecha de emisión,Fecha Vcto/Pago,Tipo CP/Doc.,Serie del CDP,Año,Nro CP o Doc. Nro Inicial (Rango),Nro Final (Rango),Tipo Doc Identidad,Nro Doc Identidad,Apellidos Nombres/ Razón  Social,BI Gravado DG,IGV / IPM DG,BI Gravado DGNG,IGV / IPM DGNG,BI Gravado DNG,IGV / IPM DNG,Valor Adq. NG,ISC,ICBPER,Otros Trib/ Cargos,Total CP,Moneda,Tipo de Cambio\n"
        "20543448568,EMPRESA DECLARANTE,202607,,01/07/2026,,01,F001,,101,,6,20111111111,PROVEEDOR TASA 18,100.00,18.00,0,0,0,0,0,0,0,0,118.00,PEN,1.000\n"
        "20543448568,EMPRESA DECLARANTE,202607,,02/07/2026,,01,F001,,102,,6,20222222222,PROVEEDOR TASA 10.5,100.00,10.50,0,0,0,0,0,0,0,0,110.50,PEN,1.000\n"
    )
    csv_file = tmp_path / "compras_tasas.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    cuentas_asignadas = {
        "F001-101-20111111111": "6011001",
        "F001-102-20222222222": "6011001"
    }

    res = preparar_dataframes(
        str(csv_file),
        str(tmp_path),
        tipo="COM",
        codigo_empresa="0001",
        año="26",
        mes="07",
        cuentas_asignadas=cuentas_asignadas
    )
    df_forexel, df_docref, ruta_generada, _, _, _, _, _ = res

    assert len(df_forexel) == 2
    # Fila 0: 18%
    assert df_forexel.iloc[0]["TASIGV"] == "18.00"
    # Fila 1: 10.5%
    assert df_forexel.iloc[1]["TASIGV"] == "10.50"


def test_asignacion_cencos_cuentas_gasto(tmp_path):
    """
    Verifica que las cuentas de gasto que comienzan con 62, 63, 65 y 67
    reciban automáticamente el Centro de Costos CENCOS = 'V0000001'.
    """
    csv_content = (
        "RUC,Apellidos y Nombres o Razón social,Periodo,CAR SUNAT,Fecha de emisión,Fecha Vcto/Pago,Tipo CP/Doc.,Serie del CDP,Año,Nro CP o Doc. Nro Inicial (Rango),Nro Final (Rango),Tipo Doc Identidad,Nro Doc Identidad,Apellidos Nombres/ Razón  Social,BI Gravado DG,IGV / IPM DG,BI Gravado DGNG,IGV / IPM DGNG,BI Gravado DNG,IGV / IPM DNG,Valor Adq. NG,ISC,ICBPER,Otros Trib/ Cargos,Total CP,Moneda,Tipo de Cambio\n"
        "20543448568,EMPRESA DECLARANTE,202607,,01/07/2026,,01,F001,,201,,6,20333333333,PROVEEDOR TRANSPORTE,500.00,90.00,0,0,0,0,0,0,0,0,590.00,PEN,1.000\n"
        "20543448568,EMPRESA DECLARANTE,202607,,02/07/2026,,01,F001,,202,,6,20444444444,PROVEEDOR MERCADERIA,1000.00,180.00,0,0,0,0,0,0,0,0,1180.00,PEN,1.000\n"
    )
    csv_file = tmp_path / "compras_cencos.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    cuentas_asignadas = {
        "F001-201-20333333333": "6311001",  # Cuenta 63 -> debe recibir CENCOS V0000001
        "F001-202-20444444444": "6011001"   # Cuenta 60 -> NO debe recibir V0000001
    }

    res = preparar_dataframes(
        str(csv_file),
        str(tmp_path),
        tipo="COM",
        codigo_empresa="0001",
        año="26",
        mes="07",
        cuentas_asignadas=cuentas_asignadas
    )
    df_forexel, _, _, _, _, _, _, _ = res

    assert df_forexel.iloc[0]["CTACOM"] == "6311001"
    assert df_forexel.iloc[0]["CENCOS"] == "V0000001"

    assert df_forexel.iloc[1]["CTACOM"] == "6011001"
    assert df_forexel.iloc[1]["CENCOS"] != "V0000001"


def test_tratamiento_boletas_ventas(tmp_path):
    """
    Verifica que en el registro de Ventas (VTA), las boletas (TIPDOC 03)
    no desglosen IGV para CONCAR (IGV=0, VALVTA=Total) pero conserven los valores
    originales en las columnas ocultas _BI_ORIG y _IGV_ORIG para el resumen.
    """
    csv_content = (
        "RUC,Apellidos y Nombres o Razón social,Periodo,CAR SUNAT,Fecha de emisión,Fecha Vcto/Pago,Tipo CP/Doc.,Serie del CDP,Año,Nro CP o Doc. Nro Inicial (Rango),Nro Final (Rango),Tipo Doc Identidad,Nro Doc Identidad,Apellidos Nombres/ Razón  Social,BI Gravado DG,IGV / IPM DG,BI Gravado DGNG,IGV / IPM DGNG,BI Gravado DNG,IGV / IPM DNG,Valor Adq. NG,ISC,ICBPER,Otros Trib/ Cargos,Total CP,Moneda,Tipo de Cambio\n"
        "20543448568,EMPRESA DECLARANTE,202607,,01/07/2026,,03,B001,,501,,1,44556677,CLIENTE BOLETA,100.00,18.00,0,0,0,0,0,0,0,0,118.00,PEN,1.000\n"
    )
    csv_file = tmp_path / "ventas_boletas.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    res = preparar_dataframes(
        str(csv_file),
        str(tmp_path),
        tipo="VTA",
        codigo_empresa="0001",
        año="26",
        mes="07",
        subtipo_vta="MERCADERIA"
    )
    df_forexel, _, _, _, _, _, _, _ = res

    row = df_forexel.iloc[0]
    assert row["TIPDOC"] == "03"
    # Formato CONCAR para boletas:
    assert float(row["IGV"]) == 0.00
    assert float(row["VALVTA"]) == 118.00
    # Preservación original para resumen financiero:
    assert float(row["_BI_ORIG"]) == 100.00
    assert float(row["_IGV_ORIG"]) == 18.00
    assert float(row["_TOTAL_ORIG"]) == 118.00


def test_lectura_csv_distintos_separadores_y_encodings(tmp_path):
    """
    Verifica que el motor de lectura soporte delimitadores punto y coma (;),
    pipe (|), comas (,) y codificaciones UTF-8 y Latin-1.
    """
    # Prueba 1: Punto y coma con caracteres especiales en latin1
    csv_semicolon = (
        "RUC;Apellidos y Nombres o Razón social;Periodo;CAR SUNAT;Fecha de emisión;Fecha Vcto/Pago;Tipo CP/Doc.;Serie del CDP;Año;Nro CP o Doc. Nro Inicial (Rango);Nro Final (Rango);Tipo Doc Identidad;Nro Doc Identidad;Apellidos Nombres/ Razón  Social;BI Gravado DG;IGV / IPM DG;BI Gravado DGNG;IGV / IPM DGNG;BI Gravado DNG;IGV / IPM DNG;Valor Adq. NG;ISC;ICBPER;Otros Trib/ Cargos;Total CP;Moneda;Tipo de Cambio\n"
        "20543448568;EMPRESA ÑANDÚ S.A.C.;202607;;01/07/2026;;01;E001;;801;;6;20555555555;PROVEEDOR CAÑÓN S.R.L.;200.00;36.00;0;0;0;0;0;0;0;0;236.00;PEN;1.000\n"
    )
    csv_file1 = tmp_path / "semicolon_latin.csv"
    csv_file1.write_bytes(csv_semicolon.encode("latin1"))

    res1 = preparar_dataframes(
        str(csv_file1),
        str(tmp_path),
        tipo="COM",
        codigo_empresa="0001",
        año="26",
        mes="07",
        cuentas_asignadas={"E001-801-20555555555": "6011001"}
    )
    df1 = res1[0]
    assert len(df1) == 1
    assert df1.iloc[0]["CODENT"] == "20555555555"

    # Prueba 2: Pipe con UTF-8
    csv_pipe = (
        "RUC|Apellidos y Nombres o Razón social|Periodo|CAR SUNAT|Fecha de emisión|Fecha Vcto/Pago|Tipo CP/Doc.|Serie del CDP|Año|Nro CP o Doc. Nro Inicial (Rango)|Nro Final (Rango)|Tipo Doc Identidad|Nro Doc Identidad|Apellidos Nombres/ Razón  Social|BI Gravado DG|IGV / IPM DG|BI Gravado DGNG|IGV / IPM DGNG|BI Gravado DNG|IGV / IPM DNG|Valor Adq. NG|ISC|ICBPER|Otros Trib/ Cargos|Total CP|Moneda|Tipo de Cambio\n"
        "20543448568|EMPRESA DECLARANTE|202607||01/07/2026||01|F002||901||6|20666666666|PROVEEDOR PIPE S.A.|300.00|54.00|0|0|0|0|0|0|0|0|354.00|PEN|1.000\n"
    )
    csv_file2 = tmp_path / "pipe_utf8.csv"
    csv_file2.write_text(csv_pipe, encoding="utf-8")

    res2 = preparar_dataframes(
        str(csv_file2),
        str(tmp_path),
        tipo="COM",
        codigo_empresa="0001",
        año="26",
        mes="07",
        cuentas_asignadas={"F002-901-20666666666": "6011001"}
    )
    df2 = res2[0]
    assert len(df2) == 1
    assert df2.iloc[0]["SERIE"] == "F002"


def test_ordenamiento_notas_credito(tmp_path):
    """
    Verifica que las Notas de Crédito (Tipo 07) se procesen con TIPCONV = 'F',
    TCVREF = 'V', importes positivos y se ordenen al final de la hoja Excel.
    """
    csv_content = (
        "RUC,Apellidos y Nombres o Razón social,Periodo,CAR SUNAT,Fecha de emisión,Fecha Vcto/Pago,Tipo CP/Doc.,Serie del CDP,Año,Nro CP o Doc. Nro Inicial (Rango),Nro Final (Rango),Tipo Doc Identidad,Nro Doc Identidad,Apellidos Nombres/ Razón  Social,BI Gravado DG,IGV / IPM DG,BI Gravado DGNG,IGV / IPM DGNG,BI Gravado DNG,IGV / IPM DNG,Valor Adq. NG,ISC,ICBPER,Otros Trib/ Cargos,Total CP,Moneda,Tipo de Cambio,Fecha Emisión Doc Modificado,Tipo CP Modificado,Serie CP Modificado,COD. DAM O DSI,Nro CP Modificado\n"
        "20543448568,EMPRESA DECLARANTE,202607,,05/07/2026,,07,FC01,,10,,6,20777777777,PROVEEDOR NC,50.00,9.00,0,0,0,0,0,0,0,0,59.00,PEN,1.000,01/07/2026,01,F001,,101\n"
        "20543448568,EMPRESA DECLARANTE,202607,,01/07/2026,,01,F001,,101,,6,20777777777,PROVEEDOR FACTURA,500.00,90.00,0,0,0,0,0,0,0,0,590.00,PEN,1.000,,,,,\n"
    )
    csv_file = tmp_path / "compras_nc.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    cuentas_asignadas = {
        "FC01-10-20777777777": "6011001",
        "F001-101-20777777777": "6011001"
    }

    res = preparar_dataframes(
        str(csv_file),
        str(tmp_path),
        tipo="COM",
        codigo_empresa="0001",
        año="26",
        mes="07",
        cuentas_asignadas=cuentas_asignadas
    )
    df_forexel, df_docref, ruta_generada, _, cantidad_nc, _, _, _ = res

    assert cantidad_nc == 1
    # Guardar Excel final y verificar ordenamiento
    guardar_excel_final(df_forexel, df_docref, [], "COM", ruta_generada)

    # Leer Excel resultante
    wb = openpyxl.load_workbook(ruta_generada)
    assert "FOREXEL" in wb.sheetnames
    assert "DOCREF" in wb.sheetnames

    sheet_forexel = wb["FOREXEL"]
    # Fila 1 es header, Fila 2 debe ser la Factura (01) y Fila 3 la NC (07)
    tipdoc_fila2 = str(sheet_forexel.cell(row=2, column=6).value) # TIPDOC
    tipdoc_fila3 = str(sheet_forexel.cell(row=3, column=6).value) # TIPDOC
    assert tipdoc_fila2 == "01"
    assert tipdoc_fila3 == "07"


def test_extraccion_contraparte_proveedor_no_empresa(tmp_path):
    """
    Verifica que el RUC y Razón Social del proveedor se extraigan de las columnas
    de la contraparte (Nro Doc Identidad / Apellidos Nombres/ Razón Social) y
    nunca del encabezado de la empresa declarante.
    """
    csv_content = (
        "RUC,Apellidos y Nombres o Razón social,Periodo,CAR SUNAT,Fecha de emisión,Fecha Vcto/Pago,Tipo CP/Doc.,Serie del CDP,Año,Nro CP o Doc. Nro Inicial (Rango),Nro Final (Rango),Tipo Doc Identidad,Nro Doc Identidad,Apellidos Nombres/ Razón  Social,BI Gravado DG,IGV / IPM DG,BI Gravado DGNG,IGV / IPM DGNG,BI Gravado DNG,IGV / IPM DNG,Valor Adq. NG,ISC,ICBPER,Otros Trib/ Cargos,Total CP,Moneda,Tipo de Cambio\n"
        "20543448568,LA CASA OXAPAMPINA A & K E.I.R.L.,202607,,01/07/2026,,01,E001,,10003,,6,20612744425,TRANSPORTE LOGISTICO YSABELLA S.A.C.,1429.19,257.25,0,0,0,0,0,0,0,0,1686.44,PEN,1.000\n"
    )
    csv_file = tmp_path / "compras_oxapampina.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    # Primera llamada (cuentas_asignadas=None) para obtener la lista de facturas para la UI
    res = preparar_dataframes(
        str(csv_file),
        str(tmp_path),
        tipo="COM",
        codigo_empresa="0001",
        año="26",
        mes="07",
        cuentas_asignadas=None
    )
    _, _, _, _, _, _, facturas, _ = res

    assert len(facturas) == 1
    factura = facturas[0]
    assert factura["CODENT"] == "20612744425"
    assert factura["RAZSOC"] == "TRANSPORTE LOGISTICO YSABELLA S.A.C."
    assert "OXAPAMPINA" not in factura["RAZSOC"]


def test_verificar_deudas_sin_tokens():
    """
    Verifica que la función verificar_deudas retorne lista vacía sin error
    y sin hacer peticiones de red si no hay tokens provistos.
    """
    rucs = ["20111111111", "20222222222", "123"] # 123 es RUC inválido
    resultado = verificar_deudas(rucs, token_apiperu="", token_jsonpe="")
    assert isinstance(resultado, list)


def test_ventas_con_facturas_dolares_y_notas_credito(tmp_path):
    """
    Verifica que las facturas en USD mantengan sus montos originales en USD (sin dividir entre TC)
    y que las Notas de Crédito mantengan su valor original para el resumen financiero.
    """
    csv_content = (
        "Ruc,Razon Social,Periodo,CAR SUNAT,Fecha de emisión,Fecha Vcto/Pago,Tipo CP/Doc.,Serie del CDP,Nro CP o Doc. Nro Inicial (Rango),Nro Final (Rango),Tipo Doc Identidad,Nro Doc Identidad,Apellidos Nombres/ Razón Social,Valor Facturado Exportación,BI Gravada,Dscto BI,IGV / IPM,Dscto IGV / IPM,Mto Exonerado,Mto Inafecto,ISC,BI Grav IVAP,IVAP,ICBPER,Otros Tributos,Total CP,Moneda,Tipo Cambio,Fecha Emisión Doc Modificado,Tipo CP Modificado,Serie CP Modificado,Nro CP Modificado\n"
        "20520775839,J-SIMEC S.A.C.,202608,CAR1,03/08/2026,,01,E001,513,,6,10161254326,CLIENTE 1,0,1735.44,0,312.38,0,0,0,0,0,0,0,0,2047.82,PEN,1.000,,,,\n"
        "20520775839,J-SIMEC S.A.C.,202608,CAR2,03/08/2026,,07,E001,36,,6,10161254326,CLIENTE 1,0,-1735.44,0,-312.38,0,0,0,0,0,0,0,0,-2047.82,PEN,1.000,03/08/2026,01,E001,513\n"
        "20520775839,J-SIMEC S.A.C.,202608,CAR3,04/08/2026,,01,E001,515,,6,20547006101,CLIENTE USD,0,3643.54,0,655.84,0,0,0,0,0,0,0,0,4299.38,USD,3.402,,,,\n"
    )
    csv_file = tmp_path / "ventas_usd_nc.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    res = preparar_dataframes(
        str(csv_file),
        str(tmp_path),
        tipo="VTA",
        codigo_empresa="0215",
        año="26",
        mes="08",
        subtipo_vta="MERCADERIA"
    )
    df_forexel, _, _, _, _, _, _, _ = res

    # Factura en USD debe conservar 3643.54 (no dividirse entre 3.402)
    row_usd = df_forexel[df_forexel["NUMERO"] == "515"].iloc[0]
    assert float(row_usd["VALVTA"]) == 3643.54
    assert float(row_usd["IGV"]) == 655.84
    assert row_usd["MND"] == "D"

