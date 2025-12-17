# 📦 Guía de Instalación - SecureVault

## Para Usuarios Finales

### Instalación con .exe (Más Fácil)

1. **Descarga** `SecureVault-Installer.exe`
2. **Ejecuta** el instalador haciendo doble clic
3. **Sigue el asistente**:
   - Selecciona dónde instalar (por defecto: `Documentos\SecureVault`)
   - Lee la Política de Privacidad en la pestaña correspondiente
   - Marca "Acepto los términos y condiciones"
   - Elige crear acceso directo en el escritorio
4. **Haz clic en "Instalar"**
5. **¡Listo!** El instalador:
   - Copia todos los archivos necesarios
   - Crea un `.exe` ejecutable
   - Crea un acceso directo en el escritorio (si lo elegiste)

### Ejecutar la Aplicación

- **Opción 1**: Doble clic en el acceso directo del escritorio
- **Opción 2**: Doble clic en `SecureVault.exe` en la carpeta de instalación
- **Opción 3**: Ejecutar `app.py` con Python (si tienes Python instalado)

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:5000`

## Para Desarrolladores

### Compilar los .exe

#### Requisitos
```bash
pip install -r requirements.txt
```

#### Compilar Todo
```bash
# Windows
build_all.bat

# O manualmente:
python build_installer.py  # Crea el instalador
python build_app.py        # Crea la aplicación
```

#### Compilar Solo el Instalador
```bash
python build_installer.py
```
Genera: `dist/SecureVault-Installer.exe`

#### Compilar Solo la Aplicación
```bash
python build_app.py
```
Genera: `dist/SecureVault.exe`

### Estructura de Archivos Generados

```
dist/
├── SecureVault-Installer.exe  # Instalador con GUI
└── SecureVault.exe            # Aplicación ejecutable
```

### Notas de Compilación

- **PyInstaller** se usa para crear los .exe
- Los archivos se compilan como "onefile" (un solo archivo)
- El instalador incluye la política de privacidad
- La aplicación incluye las plantillas HTML

### Solución de Problemas

**Error: PyInstaller no encontrado**
```bash
pip install pyinstaller
```

**Error: win32com no encontrado**
```bash
pip install pywin32
```

**El .exe no se crea correctamente**
- Verifica que todas las dependencias estén instaladas
- Revisa que los archivos fuente existan
- Ejecuta como administrador si hay problemas de permisos

**El instalador no funciona**
- Asegúrate de tener Python 3.8+ instalado
- Verifica que tkinter esté disponible (viene con Python)
- Revisa los permisos de escritura en la carpeta de destino

## Personalización

### Cambiar la Ubicación por Defecto

Edita `installer_gui.py`:
```python
self.install_path = Path.home() / "Documents" / APP_NAME
```

### Cambiar el Nombre de la Aplicación

Edita `installer_gui.py` y `app.py`:
```python
APP_NAME = "TuNombreAqui"
```

### Agregar un Icono

1. Crea un archivo `.ico`
2. En `build_installer.py` y `build_app.py`, cambia:
```python
"--icon", "tu_icono.ico",
```

## Distribución

Para distribuir SecureVault:

1. Compila ambos .exe usando `build_all.bat`
2. Distribuye solo `SecureVault-Installer.exe`
3. Los usuarios ejecutarán el instalador y obtendrán todo lo necesario

**No necesitas distribuir:**
- Los archivos fuente (.py)
- Las dependencias
- Python (si compilas correctamente)

**Sí necesitas distribuir:**
- `SecureVault-Installer.exe` (el instalador)
- `privacy_policy.txt` (opcional, ya está incluido)

