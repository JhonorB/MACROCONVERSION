import os
import sys
import shutil
import subprocess
import winreg
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def get_bundle_dir():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def crear_acceso_directo(ruta_destino_lnk, ruta_target_exe, ruta_icono, working_dir, descripcion):
    vbs_content = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{ruta_destino_lnk}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{ruta_target_exe}"
oLink.WorkingDirectory = "{working_dir}"
oLink.Description = "{descripcion}"
oLink.IconLocation = "{ruta_icono}"
oLink.Save
'''
    temp_dir = os.environ.get("TEMP", ".")
    vbs_path = os.path.join(temp_dir, f"shortcut_{os.getpid()}.vbs")
    try:
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        subprocess.run(["cscript", "//Nologo", vbs_path], check=True)
    finally:
        if os.path.exists(vbs_path):
            try:
                os.remove(vbs_path)
            except Exception:
                pass

class AppInstalador(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Instalador - Conversor SIRE a Macro Excel")
        self.geometry("640x520")
        self.resizable(False, False)
        
        # Set icon if available
        bundle = get_bundle_dir()
        ico = os.path.join(bundle, "app_icon.ico")
        if os.path.exists(ico):
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

        # Carpeta destino por defecto: AppData\Local\Programs\Conversor SIRE
        default_dir = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "Programs", "Conversor SIRE")
        self.var_dir = ctk.StringVar(value=default_dir)
        self.var_desktop = ctk.BooleanVar(value=True)
        self.var_startmenu = ctk.BooleanVar(value=True)
        self.var_launch = ctk.BooleanVar(value=True)

        self.construir_ui()

    def construir_ui(self):
        # Header banner
        header = ctk.CTkFrame(self, fg_color="#1877F2", corner_radius=0, height=85)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        lbl_tit = ctk.CTkLabel(header, text="Conversor SIRE a Macro Excel", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        lbl_tit.pack(anchor="w", padx=25, pady=(15, 2))
        lbl_sub = ctk.CTkLabel(header, text="Asistente de Instalación v2.0 - Versión Multi-Empresa", font=ctk.CTkFont(size=12), text_color="#E0EDFF")
        lbl_sub.pack(anchor="w", padx=25)

        # Body container
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=25, pady=20)

        desc = ("Este asistente instalará el Conversor SIRE en su computadora.\n"
                "La aplicación incluye una carpeta dedicada 'datos/' para sus empresas y cuentas contables.")
        ctk.CTkLabel(self.body, text=desc, justify="left", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 15))

        # Directorio de instalación
        ctk.CTkLabel(self.body, text="Carpeta de Destino:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        
        frame_dir = ctk.CTkFrame(self.body, fg_color="transparent")
        frame_dir.pack(fill="x", pady=(0, 15))
        
        self.entry_dir = ctk.CTkEntry(frame_dir, textvariable=self.var_dir, font=ctk.CTkFont(size=12))
        self.entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_browse = ctk.CTkButton(frame_dir, text="Examinar...", width=100, command=self.examinar_carpeta)
        btn_browse.pack(side="right")

        # Opciones
        ctk.CTkLabel(self.body, text="Opciones de Acceso:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 5))
        
        ctk.CTkCheckBox(self.body, text="Crear acceso directo en el Escritorio", variable=self.var_desktop, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=4)
        ctk.CTkCheckBox(self.body, text="Crear acceso directo en el Menú Inicio", variable=self.var_startmenu, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=4)
        ctk.CTkCheckBox(self.body, text="Iniciar Conversor SIRE al finalizar la instalación", variable=self.var_launch, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=4)

        # Barra de progreso (oculta al inicio)
        self.lbl_progreso = ctk.CTkLabel(self.body, text="", font=ctk.CTkFont(size=12), text_color="#A0AEC0")
        self.lbl_progreso.pack(anchor="w", pady=(15, 4))
        
        self.progress = ctk.CTkProgressBar(self.body, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 10))
        self.progress.set(0)

        # Footer con botones
        footer = ctk.CTkFrame(self, fg_color="transparent", height=50)
        footer.pack(fill="x", side="bottom", padx=25, pady=(0, 15))

        self.btn_cancel = ctk.CTkButton(footer, text="Cancelar", fg_color="#4A5568", hover_color="#2D3748", width=110, command=self.destroy)
        self.btn_cancel.pack(side="right", padx=(10, 0))

        self.btn_install = ctk.CTkButton(footer, text="Instalar", fg_color="#2FA572", hover_color="#1F7A52", width=130, font=ctk.CTkFont(weight="bold"), command=self.ejecutar_instalacion)
        self.btn_install.pack(side="right")

    def examinar_carpeta(self):
        sel = filedialog.askdirectory(initialdir=self.var_dir.get(), title="Seleccionar Carpeta de Instalación")
        if sel:
            self.var_dir.set(os.path.join(sel, "Conversor SIRE"))

    def ejecutar_instalacion(self):
        dest_dir = self.var_dir.get().strip()
        if not dest_dir:
            messagebox.showerror("Error", "Por favor indique una carpeta de instalación válida.")
            return

        self.btn_install.configure(state="disabled")
        self.btn_cancel.configure(state="disabled")
        self.entry_dir.configure(state="disabled")

        self.after(100, lambda: self.instalar_pasos(dest_dir))

    def instalar_pasos(self, dest_dir):
        bundle = get_bundle_dir()

        try:
            # Paso 1: Crear carpetas
            self.lbl_progreso.configure(text="Creando carpetas de destino...")
            self.progress.set(0.15)
            self.update_idletasks()
            
            os.makedirs(dest_dir, exist_ok=True)
            datos_dir = os.path.join(dest_dir, "datos")
            os.makedirs(datos_dir, exist_ok=True)

            # Paso 2: Copiar ejecutable principal
            self.lbl_progreso.configure(text="Copiando Conversor_SIRE.exe...")
            self.progress.set(0.40)
            self.update_idletasks()

            src_exe = os.path.join(bundle, "Conversor_SIRE.exe")
            if not os.path.exists(src_exe):
                src_exe = os.path.join(bundle, "dist", "Conversor_SIRE.exe")
            
            target_exe = os.path.join(dest_dir, "Conversor_SIRE.exe")
            if os.path.exists(src_exe):
                shutil.copy2(src_exe, target_exe)
            else:
                raise FileNotFoundError("No se encontró Conversor_SIRE.exe en el instalador.")

            # Copiar icono
            src_ico = os.path.join(bundle, "app_icon.ico")
            target_ico = os.path.join(dest_dir, "app_icon.ico")
            if os.path.exists(src_ico):
                shutil.copy2(src_ico, target_ico)

            # Paso 3: Copiar archivos de la carpeta datos/
            self.lbl_progreso.configure(text="Configurando catálogo de empresas y cuentas (datos/)...")
            self.progress.set(0.65)
            self.update_idletasks()

            src_datos = os.path.join(bundle, "datos")
            if os.path.exists(src_datos):
                for item in os.listdir(src_datos):
                    s = os.path.join(src_datos, item)
                    d = os.path.join(datos_dir, item)
                    # Si ya existe en destino, preservar el del usuario (no sobreescribir empresas)
                    if not os.path.exists(d):
                        if os.path.isfile(s):
                            shutil.copy2(s, d)

            # Paso 4: Crear desinstalador
            self.crear_desinstalador(dest_dir)

            # Paso 5: Crear accesos directos
            self.lbl_progreso.configure(text="Creando accesos directos...")
            self.progress.set(0.85)
            self.update_idletasks()

            if self.var_desktop.get():
                desktop = os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Desktop")
                if os.path.exists(desktop):
                    lnk = os.path.join(desktop, "Conversor SIRE.lnk")
                    crear_acceso_directo(lnk, target_exe, target_ico, dest_dir, "Conversor SIRE a Macro Excel")

            if self.var_startmenu.get():
                appdata = os.environ.get("APPDATA", "")
                if appdata:
                    menu_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Conversor SIRE")
                    os.makedirs(menu_dir, exist_ok=True)
                    lnk_menu = os.path.join(menu_dir, "Conversor SIRE.lnk")
                    crear_acceso_directo(lnk_menu, target_exe, target_ico, dest_dir, "Conversor SIRE a Macro Excel")

            # Paso 6: Registro en Windows
            self.registrar_en_windows(dest_dir)

            self.progress.set(1.0)
            self.lbl_progreso.configure(text="¡Instalación completada con éxito!", text_color="#38A169")
            self.update_idletasks()

            # Lanzar app si se seleccionó
            if self.var_launch.get():
                try:
                    subprocess.Popen([target_exe], cwd=dest_dir)
                except Exception:
                    pass

            messagebox.showinfo("Instalación Completa", 
                                f"¡Conversor SIRE se instaló correctamente!\n\n"
                                f"Ubicación: {dest_dir}\n"
                                f"Carpeta de datos: {datos_dir}\n\n"
                                f"Ya puedes usar el acceso directo en tu Escritorio.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error durante la instalación", f"Ocurrió un error:\n\n{str(e)}")
            self.btn_install.configure(state="normal")
            self.btn_cancel.configure(state="normal")
            self.entry_dir.configure(state="normal")

    def crear_desinstalador(self, dest_dir):
        # Generar script bat de desinstalación silenciosa
        uninst_bat = os.path.join(dest_dir, "desinstalar.bat")
        content = f'''@echo off
title Desinstalador - Conversor SIRE
echo ==============================================
echo       Desinstalador de Conversor SIRE
echo ==============================================
echo.
set /p resp="Desea desinstalar Conversor SIRE? (S/N): "
if /i not "%resp%"=="S" goto cancelar

echo Cerrando procesos activos...
taskkill /f /im Conversor_SIRE.exe >nul 2>&1

echo Eliminando accesos directos...
del /q "%USERPROFILE%\\Desktop\\Conversor SIRE.lnk" >nul 2>&1
rd /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Conversor SIRE" >nul 2>&1

echo Limpiando registro de Windows...
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ConversorSIRE" /f >nul 2>&1

echo Desea conservar su carpeta de empresas y cuentas (datos)?
set /p kdata="Presione S para conservar sus datos o N para borrar todo: "
if /i "%kdata%"=="S" (
    echo Conservando datos...
    del /q "{dest_dir}\\Conversor_SIRE.exe" >nul 2>&1
    del /q "{dest_dir}\\app_icon.ico" >nul 2>&1
) else (
    cd ..
    rd /s /q "{dest_dir}" >nul 2>&1
)

echo.
echo Desinstalacion completada.
pause
exit

:cancelar
echo Desinstalacion cancelada.
pause
exit
'''
        with open(uninst_bat, "w", encoding="latin1") as f:
            f.write(content)

    def registrar_en_windows(self, dest_dir):
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ConversorSIRE"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Conversor SIRE a Macro Excel")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "2.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "JhonorB")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, dest_dir)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, os.path.join(dest_dir, "app_icon.ico"))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'cmd.exe /c "{os.path.join(dest_dir, "desinstalar.bat")}"')
            winreg.CloseKey(key)
        except Exception:
            pass

if __name__ == "__main__":
    app = AppInstalador()
    app.mainloop()