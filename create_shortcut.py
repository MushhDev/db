import win32com.client
from pathlib import Path
import sys

def create_shortcut(target_path, shortcut_path, working_dir=None):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(target_path)
        if working_dir:
            shortcut.WorkingDirectory = str(working_dir)
        shortcut.IconLocation = str(target_path)
        shortcut.save()
        return True
    except Exception as e:
        print(f"Error creando acceso directo: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python create_shortcut.py <ruta_exe> <ruta_acceso_directo> [directorio_trabajo]")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    shortcut = Path(sys.argv[2])
    working_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else target.parent
    
    if create_shortcut(target, shortcut, working_dir):
        print(f"✅ Acceso directo creado: {shortcut}")
    else:
        print("❌ Error al crear acceso directo")
        sys.exit(1)

