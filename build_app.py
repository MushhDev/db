import subprocess
import sys
import os
from pathlib import Path

def build_app():
    print("🔨 Compilando aplicación...")
    
    app_script = Path("app.py")
    if not app_script.exists():
        print("❌ Error: app.py no encontrado")
        return False
    
    try:
        hidden_imports = [
            "cryptography",
            "cryptography.hazmat",
            "cryptography.hazmat.primitives",
            "cryptography.hazmat.primitives.ciphers",
            "cryptography.hazmat.primitives.kdf",
            "cryptography.hazmat.backends",
            "flask",
            "flask_cors",
            "win32com.client"
        ]
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--console",
            "--name", "SecureVault",
            "--add-data", "templates;templates",
            "--add-data", "version.txt;.",
            "--hidden-import", ";".join(hidden_imports),
            "--icon", "NONE",
            str(app_script)
        ]
        
        print(f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        
        print("✅ Aplicación compilada exitosamente!")
        print(f"📦 Archivo generado: dist/SecureVault.exe")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al compilar: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SecureVault - Compilador de Aplicación")
    print("=" * 50)
    print()
    
    if build_app():
        print()
        print("✨ ¡Compilación completada!")
        print("La aplicación está en la carpeta 'dist'")
    else:
        print()
        print("❌ La compilación falló")
        sys.exit(1)

