import os
import sys
import shutil
import json
import urllib.request
import webbrowser
from pathlib import Path

APP_NAME = "SecureVault"
VERSION_URL = "https://raw.githubusercontent.com/MushhDev/db/main/version.txt"
INSTALL_DIR = Path.home() / "Documents" / APP_NAME
CONFIG_FILE = INSTALL_DIR / "config.json"

def get_current_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except:
        return "1.0.0"

def check_updates():
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
            latest_version = response.read().decode().strip()
            current_version = get_current_version()
            return latest_version, latest_version != current_version
    except:
        return get_current_version(), False

def install_app():
    print(f"Instalando {APP_NAME}...")
    
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    
    files_to_copy = [
        "app.py",
        "requirements.txt",
        "version.txt",
        "templates"
    ]
    
    for item in files_to_copy:
        src = Path(item)
        dst = INSTALL_DIR / item
        
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        elif src.exists():
            shutil.copy2(src, dst)
    
    config = {
        "installed": True,
        "version": get_current_version(),
        "install_path": str(INSTALL_DIR)
    }
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ {APP_NAME} instalado en: {INSTALL_DIR}")
    return True

def is_installed():
    return CONFIG_FILE.exists()

def get_install_path():
    if is_installed():
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("install_path", str(INSTALL_DIR))
    return str(INSTALL_DIR)

if __name__ == "__main__":
    latest_version, has_update = check_updates()
    current_version = get_current_version()
    
    print(f"\n{'='*50}")
    print(f"  {APP_NAME} v{current_version}")
    print(f"{'='*50}\n")
    
    if has_update:
        print(f"⚠ Actualización disponible: v{latest_version}")
        print(f"  Versión actual: v{current_version}\n")
    
    if not is_installed():
        print("Primera instalación detectada...")
        if install_app():
            print("\n✓ Instalación completada exitosamente!")
            print(f"\nIniciando {APP_NAME}...\n")
            
            install_path = get_install_path()
            os.chdir(install_path)
            os.system(f'python "{install_path}/app.py"')
    else:
        print(f"✓ {APP_NAME} ya está instalado")
        print(f"  Ubicación: {get_install_path()}\n")
        
        install_path = get_install_path()
        if os.path.exists(install_path):
            os.chdir(install_path)
            os.system(f'python "{install_path}/app.py"')
        else:
            print("⚠ Directorio de instalación no encontrado. Reinstalando...")
            install_app()
            os.chdir(get_install_path())
            os.system(f'python "{get_install_path()}/app.py"')

