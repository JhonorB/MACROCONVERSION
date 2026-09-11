import os
import sys
import shutil

def obtener_directorio_base():
    """
    Retorna la carpeta donde reside la aplicación.
    Si está congelada con PyInstaller (ejecutable .exe), es la carpeta del .exe.
    Si se ejecuta como script .py, es la carpeta del proyecto.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def obtener_ruta_datos(nombre_archivo, crear_si_no_existe=True):
    """
    Retorna la ruta a un archivo dentro de la subcarpeta 'datos/'.
    Si el archivo no existe en 'datos/', busca automáticamente en:
    1. La raíz del ejecutable o proyecto
    2. Los datos internos empaquetados en PyInstaller (_MEIPASS)
    y lo copia a 'datos/' para que siempre sea editable y persistente.
    """
    base = obtener_directorio_base()
    carpeta_datos = os.path.join(base, "datos")
    if crear_si_no_existe:
        try:
            os.makedirs(carpeta_datos, exist_ok=True)
        except Exception:
            pass

    ruta_destino = os.path.join(carpeta_datos, nombre_archivo)
    if not os.path.exists(ruta_destino) and crear_si_no_existe:
        meipass = getattr(sys, '_MEIPASS', '')
        candidatos = [
            os.path.join(base, nombre_archivo),
            os.path.join(meipass, "datos", nombre_archivo) if meipass else None,
            os.path.join(meipass, nombre_archivo) if meipass else None,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", nombre_archivo),
        ]
        # También buscar archivos de ejemplo (.example.json) si el principal no existe
        base_name, ext = os.path.splitext(nombre_archivo)
        if ext.lower() == ".json":
            candidatos.append(os.path.join(base, f"{base_name}.example.json"))
            candidatos.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{base_name}.example.json"))

        for cand in candidatos:
            if cand and os.path.exists(cand) and cand != ruta_destino:
                try:
                    shutil.copy2(cand, ruta_destino)
                    break
                except Exception:
                    pass

    return ruta_destino

def obtener_ruta_asset(nombre_archivo):
    """
    Retorna la ruta a un recurso estático (imágenes, iconos).
    Busca primero en _MEIPASS (empaquetado), luego en base_dir.
    """
    meipass = getattr(sys, '_MEIPASS', '')
    if meipass:
        ruta_mei = os.path.join(meipass, nombre_archivo)
        if os.path.exists(ruta_mei):
            return ruta_mei
    base = obtener_directorio_base()
    ruta_base = os.path.join(base, nombre_archivo)
    if os.path.exists(ruta_base):
        return ruta_base
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)