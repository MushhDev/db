import os
import sys
import json
import subprocess
from pathlib import Path

APP_NAME = "SecureVault"
INSTALL_DIR = Path.home() / "Documents" / APP_NAME
CONFIG_FILE = INSTALL_DIR / "config.json"

def is_installed():
    return CONFIG_FILE.exists()

def get_install_path():
    if is_installed():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                install_path = config.get("install_path", str(INSTALL_DIR))
                if os.path.exists(install_path):
                    return install_path
        except:
            pass
    return str(INSTALL_DIR)

if __name__ == "__main__":
    if is_installed():
        install_path = get_install_path()
        app_file = Path(install_path) / "app.py"
        if app_file.exists():
            os.chdir(install_path)
            subprocess.run([sys.executable, str(app_file)])
        else:
            print(f"Error: No se encontró app.py en {install_path}")
            print("Por favor, ejecuta el instalador desde el navegador: http://localhost:5000/installer")
            current_dir = Path(__file__).parent
            app_file = current_dir / "app.py"
            if app_file.exists():
                subprocess.run([sys.executable, str(app_file)])
    else:
        current_dir = Path(__file__).parent
        app_file = current_dir / "app.py"
        if app_file.exists():
            print(f"\n{'='*60}")
            print(f"  Bienvenido a {APP_NAME}")
            print(f"{'='*60}\n")
            print("Primera ejecución detectada.")
            print("Abre http://localhost:5000/installer en tu navegador para completar la instalación.\n")
            subprocess.run([sys.executable, str(app_file)])
        else:
            print("Error: No se encontró app.py")

