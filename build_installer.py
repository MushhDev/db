import subprocess
import sys
import os
from pathlib import Path

def build_installer():
    print("🔨 Compilando instalador...")
    
    installer_script = Path("installer_gui.py")
    if not installer_script.exists():
        print("❌ Error: installer_gui.py no encontrado")
        return False
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "SecureVault-Installer",
            "--add-data", "privacy_policy.txt;.",
            "--icon", "NONE",
            str(installer_script)
        ]
        
        print(f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        
        print("✅ Instalador compilado exitosamente!")
        print(f"📦 Archivo generado: dist/SecureVault-Installer.exe")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al compilar: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SecureVault - Compilador de Instalador")
    print("=" * 50)
    print()
    
    if build_installer():
        print()
        print("✨ ¡Compilación completada!")
        print("El instalador está en la carpeta 'dist'")
    else:
        print()
        print("❌ La compilación falló")
        sys.exit(1)

