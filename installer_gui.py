import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import shutil
import json
import sys
from pathlib import Path
import subprocess
import urllib.request

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

APP_NAME = "SecureVault"
VERSION = "1.0.0"

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - Instalador")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        self.install_path = Path.home() / "Documents" / APP_NAME
        self.create_shortcut = tk.BooleanVar(value=True)
        self.accept_terms = tk.BooleanVar(value=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header = ttk.Label(main_frame, text=f"🔐 {APP_NAME}", font=("Arial", 24, "bold"))
        header.pack(pady=(0, 10))
        
        subtitle = ttk.Label(main_frame, text=f"Versión {VERSION}", font=("Arial", 10))
        subtitle.pack(pady=(0, 20))
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        install_frame = ttk.Frame(notebook, padding="20")
        notebook.add(install_frame, text="Instalación")
        
        privacy_frame = ttk.Frame(notebook, padding="20")
        notebook.add(privacy_frame, text="Política de Privacidad")
        
        self.setup_install_tab(install_frame)
        self.setup_privacy_tab(privacy_frame)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancelar", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        self.install_btn = ttk.Button(button_frame, text="Instalar", command=self.install, state=tk.DISABLED)
        self.install_btn.pack(side=tk.RIGHT, padx=5)
        
    def setup_install_tab(self, parent):
        ttk.Label(parent, text="Selecciona la ubicación de instalación:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        path_frame = ttk.Frame(parent)
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.path_var = tk.StringVar(value=str(self.install_path))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(path_frame, text="Examinar...", command=self.browse_path).pack(side=tk.LEFT)
        
        ttk.Label(parent, text="Opciones de instalación:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(20, 10))
        
        ttk.Checkbutton(parent, text="Crear acceso directo en el escritorio", variable=self.create_shortcut).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(parent, text="Crear .exe para ejecutar la aplicación", variable=tk.BooleanVar(value=True), state=tk.DISABLED).pack(anchor=tk.W, pady=5)
        
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        terms_frame = ttk.Frame(parent)
        terms_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Checkbutton(terms_frame, text="Acepto los términos y condiciones de la Política de Privacidad", 
                       variable=self.accept_terms, command=self.update_install_button).pack(anchor=tk.W, pady=10)
        
        info_label = ttk.Label(terms_frame, text="Espacio requerido: ~50 MB\nPython 3.8+ requerido", 
                               font=("Arial", 9), foreground="gray")
        info_label.pack(anchor=tk.W, pady=10)
        
    def setup_privacy_tab(self, parent):
        ttk.Label(parent, text="Política de Privacidad", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        text_widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20, width=60)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        try:
            with open("privacy_policy.txt", "r", encoding="utf-8") as f:
                text_widget.insert(tk.END, f.read())
        except:
            text_widget.insert(tk.END, self.get_default_privacy_policy())
        
        text_widget.config(state=tk.DISABLED)
        
    def get_default_privacy_policy(self):
        return f"""
{APP_NAME} - Política de Privacidad

Última actualización: {VERSION}

1. RECOPILACIÓN DE INFORMACIÓN
{APP_NAME} es una aplicación de escritorio que funciona completamente offline. 
No recopilamos, almacenamos ni transmitimos ningún dato personal a servidores externos.

2. ALMACENAMIENTO LOCAL
Todos los datos que almacenas en {APP_NAME} se guardan localmente en tu ordenador.
Los archivos se almacenan en: {self.install_path}

3. ENCRIPTACIÓN
{APP_NAME} utiliza encriptación de nivel militar para proteger tus datos:
- Nivel 1: Base64
- Nivel 2: AES-128
- Nivel 3: AES-256
- Nivel 4: AES-256 + PBKDF2
- Nivel 5: AES-256 + PBKDF2 + HMAC (Máxima seguridad)

4. VERIFICACIÓN DE ACTUALIZACIONES
La aplicación puede verificar actualizaciones desde GitHub de forma opcional.
Esta verificación solo consulta la versión disponible, sin enviar datos personales.

5. DATOS DE USUARIO
- Las contraseñas de usuario se almacenan con hash PBKDF2
- Los datos encriptados solo pueden ser desencriptados con tu contraseña
- No tenemos acceso a tus datos encriptados

6. SEGURIDAD
- Todos los datos sensibles se encriptan antes de almacenarse
- Las sesiones utilizan tokens seguros
- No se almacenan contraseñas en texto plano

7. RESPONSABILIDAD
El usuario es responsable de:
- Mantener sus contraseñas seguras
- Realizar backups regulares de sus datos
- No compartir sus credenciales de acceso

8. CAMBIOS EN LA POLÍTICA
Nos reservamos el derecho de actualizar esta política. 
Los cambios se reflejarán en futuras versiones de la aplicación.

9. CONTACTO
Para preguntas sobre privacidad, consulta el repositorio del proyecto.

Al instalar {APP_NAME}, aceptas esta política de privacidad.
"""
        
    def browse_path(self):
        path = filedialog.askdirectory(initialdir=str(self.install_path.parent))
        if path:
            self.path_var.set(path)
            self.install_path = Path(path) / APP_NAME
            
    def update_install_button(self):
        if self.accept_terms.get():
            self.install_btn.config(state=tk.NORMAL)
        else:
            self.install_btn.config(state=tk.DISABLED)
            
    def install(self):
        if not self.accept_terms.get():
            messagebox.showerror("Error", "Debes aceptar los términos y condiciones")
            return
            
        self.install_path = Path(self.path_var.get())
        
        if not self.install_path.parent.exists():
            messagebox.showerror("Error", "La ruta seleccionada no existe")
            return
            
        try:
            self.install_btn.config(state=tk.DISABLED, text="Instalando...")
            self.root.update()
            
            self.install_path.mkdir(parents=True, exist_ok=True)
            
            current_dir = Path(__file__).parent
            
            files_to_copy = ["app.py", "requirements.txt", "version.txt"]
            dirs_to_copy = ["templates"]
            
            for file_name in files_to_copy:
                src_file = current_dir / file_name
                if src_file.exists():
                    shutil.copy2(src_file, self.install_path / file_name)
            
            for dir_name in dirs_to_copy:
                src_dir = current_dir / dir_name
                if src_dir.exists() and src_dir.is_dir():
                    dst_dir = self.install_path / dir_name
                    if dst_dir.exists():
                        shutil.rmtree(dst_dir)
                    shutil.copytree(src_dir, dst_dir)
            
            config = {
                "installed": True,
                "version": VERSION,
                "install_path": str(self.install_path)
            }
            
            with open(self.install_path / "config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            if self.create_shortcut.get():
                self.create_desktop_shortcut()
            
            self.create_launcher_exe()
            
            messagebox.showinfo("Instalación Completada", 
                              f"{APP_NAME} se ha instalado correctamente en:\n{self.install_path}\n\n"
                              f"Se ha creado un acceso directo en el escritorio.\n"
                              f"Puedes ejecutar la aplicación desde el .exe generado.")
            
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Error de Instalación", f"Ocurrió un error durante la instalación:\n{str(e)}")
            self.install_btn.config(state=tk.NORMAL, text="Instalar")
            
    def create_desktop_shortcut(self):
        if not HAS_WIN32:
            return
            
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / f"{APP_NAME}.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            exe_path = self.install_path / f"{APP_NAME}.exe"
            if not exe_path.exists():
                exe_path = self.install_path / "app.py"
            shortcut.Targetpath = str(exe_path)
            shortcut.WorkingDirectory = str(self.install_path)
            shortcut.IconLocation = str(exe_path)
            shortcut.save()
        except Exception as e:
            print(f"Error creando acceso directo: {e}")
            
    def create_launcher_exe(self):
        launcher_script = self.install_path / "launcher.py"
        with open(launcher_script, "w", encoding="utf-8") as f:
            f.write(f'''import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time

APP_NAME = "{APP_NAME}"
INSTALL_DIR = Path(r"{self.install_path}")

if __name__ == "__main__":
    os.chdir(INSTALL_DIR)
    app_file = INSTALL_DIR / "app.py"
    
    if app_file.exists():
        print(f"Iniciando {{APP_NAME}}...")
        print(f"El navegador se abrirá automáticamente en http://localhost:5000")
        print("Cierra esta ventana para detener la aplicación\\n")
        
        process = subprocess.Popen([sys.executable, str(app_file)], 
                                 creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        
        time.sleep(2)
        try:
            webbrowser.open("http://localhost:5000")
        except:
            pass
        
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
    else:
        print(f"Error: No se encontró app.py en {{INSTALL_DIR}}")
        input("Presiona Enter para salir...")
''')
        
        try:
            spec_file = self.install_path / f"{APP_NAME}.spec"
            if spec_file.exists():
                spec_file.unlink()
            
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--console",
                "--name", APP_NAME,
                "--clean",
                str(launcher_script)
            ]
            
            result = subprocess.run(cmd, cwd=str(self.install_path), 
                                  capture_output=True, text=True)
            
            dist_exe = self.install_path / "dist" / f"{APP_NAME}.exe"
            if dist_exe.exists():
                final_exe = self.install_path / f"{APP_NAME}.exe"
                if final_exe.exists():
                    final_exe.unlink()
                shutil.move(str(dist_exe), str(final_exe))
                
            for item in ['build', 'dist']:
                path = self.install_path / item
                if path.exists():
                    shutil.rmtree(path, ignore_errors=True)
                    
            for spec in self.install_path.glob("*.spec"):
                spec.unlink()
                
            launcher_script.unlink()
            
        except ImportError:
            messagebox.showwarning("PyInstaller no encontrado", 
                                  "PyInstaller no está instalado. El .exe no se creará.\n"
                                  "Instala con: pip install pyinstaller")
        except Exception as e:
            print(f"Error creando .exe: {e}")
            messagebox.showwarning("Error", f"No se pudo crear el .exe:\n{str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = InstallerGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar el instalador:\n{str(e)}")

