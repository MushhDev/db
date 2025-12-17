# 🔐 SecureVault

Sistema de gestión de datos con encriptación avanzada de 5 niveles. Aplicación de escritorio segura para almacenar contraseñas, notas, archivos y datos sensibles.

## 🚀 Instalación Rápida

### Opción 1: Instalador .exe (Recomendado)

1. **Descarga el instalador**: `SecureVault-Installer.exe`
2. **Ejecuta el instalador** haciendo doble clic
3. **Sigue el asistente**:
   - Selecciona la ubicación de instalación (por defecto: `Documentos\SecureVault`)
   - Lee y acepta la Política de Privacidad
   - Elige crear acceso directo en el escritorio
4. **¡Listo!** El instalador creará:
   - El programa en la ubicación seleccionada
   - Un archivo `.exe` ejecutable
   - Un acceso directo en el escritorio (opcional)

### Opción 2: Instalación Manual

```
# 1. Instala las dependencias
pip install -r requirements.txt

# 2. Ejecuta el instalador GUI
python installer_gui.py

# O ejecuta directamente la aplicación
python app.py
```

## 📦 Compilar a .exe

Si quieres crear tus propios ejecutables:

### Requisitos previos
```
pip install -r requirements.txt
```

### Compilar todo (Instalador + Aplicación)
```
# Windows
build_all.bat

# O manualmente:
python build_installer.py  # Crea SecureVault-Installer.exe
python build_app.py         # Crea SecureVault.exe
```

### Archivos generados
- `dist/SecureVault-Installer.exe` - Instalador con interfaz gráfica
- `dist/SecureVault.exe` - Aplicación ejecutable

## 🎯 Uso

### Primera vez

1. **Ejecuta** `SecureVault.exe` (o el acceso directo del escritorio)
2. **Abre tu navegador** en: `http://localhost:5000`
3. **Regístrate** creando tu primera cuenta
4. **¡Comienza a usar SecureVault!**

### Características Principales

#### 🔐 Sistema de Autenticación
- Login y registro de usuarios
- Sesiones seguras
- Contraseñas hasheadas con PBKDF2

#### 🔍 Búsqueda y Filtros
- Búsqueda en tiempo real
- Filtro por categoría
- Filtro por tipo (texto, contraseña, nota, archivo)
- Filtro de items encriptados

#### 📁 Gestión de Items
- Agregar texto, contraseñas, notas y archivos
- Editar items existentes
- Vista detallada de items
- Eliminar items
- Organización por categorías

#### 🔒 Encriptación de 5 Niveles

1. **Nivel 1**: Base64 simple
2. **Nivel 2**: AES-128
3. **Nivel 3**: AES-256
4. **Nivel 4**: AES-256 + PBKDF2 (100,000 iteraciones)
5. **Nivel 5**: AES-256 + PBKDF2 (200,000 iteraciones) + HMAC ⭐ Máxima seguridad

#### 🔑 Generador de Contraseñas
- Longitud configurable (8-64 caracteres)
- Opciones: mayúsculas, minúsculas, números, especiales
- Indicador de fuerza en tiempo real
- Copiar al portapapeles

#### 📊 Estadísticas
- Total de items
- Items encriptados
- Distribución por tipo
- Distribución por nivel de encriptación
- Estadísticas por categoría

#### 💾 Exportación/Importación
- **Exportar a**: `.encript`, `.json`, `.csv`, `.txt`
- **Importar desde**: `.encript`, `.json`
- Encriptación opcional en exportación

#### 🌙 Modo Oscuro
- Tema oscuro para privacidad visual
- Persistencia de preferencias

## 📋 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.8+ (solo para desarrollo/compilación)
- **Espacio en disco**: ~50 MB
- **Memoria RAM**: 100 MB mínimo

## 🔧 Estructura del Proyecto

```
SecureVault/
├── app.py                 # Aplicación principal Flask
├── installer_gui.py        # Instalador con interfaz gráfica
├── main.py                # Punto de entrada alternativo
├── build_installer.py     # Script para compilar instalador
├── build_app.py           # Script para compilar aplicación
├── build_all.bat          # Compilar todo (Windows)
├── create_shortcut.py     # Crear acceso directo
├── privacy_policy.txt     # Política de privacidad
├── requirements.txt       # Dependencias Python
├── version.txt           # Versión actual
└── templates/            # Plantillas HTML
    ├── index.html        # Panel principal
    ├── login.html        # Login
    ├── register.html     # Registro
    └── installer.html    # Instalador web
```

## 🔒 Seguridad

- **Encriptación**: Múltiples niveles de encriptación AES-256
- **Autenticación**: Sesiones seguras con tokens aleatorios
- **Almacenamiento**: Todos los datos se guardan localmente
- **Sin conexión**: Funciona completamente offline
- **Privacidad**: No se envían datos a servidores externos

## 📝 Política de Privacidad

SecureVault es una aplicación **100% offline**. 
- No recopilamos datos personales
- No enviamos información a servidores
- Todos los datos se almacenan localmente
- Solo verificamos actualizaciones (opcional) desde GitHub

Lee la política completa en `privacy_policy.txt` o en el instalador.

## 🐛 Solución de Problemas

### El instalador no se ejecuta
- Asegúrate de tener Python 3.8+ instalado
- Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`

### Error al crear acceso directo
- Ejecuta el programa como administrador
- Verifica permisos de escritura en el escritorio

### La aplicación no inicia
- Verifica que el puerto 5000 no esté en uso
- Revisa los logs en la consola
- Asegúrate de que todos los archivos estén en la carpeta de instalación

### Error de importación
- Reinstala las dependencias: `pip install -r requirements.txt --force-reinstall`

## 🔄 Actualizaciones

SecureVault verifica automáticamente actualizaciones desde:

```
https://raw.githubusercontent.com/MushhDev/db/main/version.txt
```

Las actualizaciones son opcionales y no se envían datos personales.

## 📄 Licencia

Este proyecto es de código abierto. Consulta el repositorio para más información.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para problemas, preguntas o sugerencias:
- Abre un issue en el repositorio
- Consulta la documentación
- Revisa los logs de la aplicación

## ✨ Características Avanzadas

- **Búsqueda inteligente**: Busca en nombres y contenidos
- **Filtros múltiples**: Combina búsqueda, categoría, tipo y estado de encriptación
- **Vista previa**: Ve detalles completos de cada item
- **Edición rápida**: Modifica items sin desencriptar
- **Exportación flexible**: Múltiples formatos según tus necesidades
- **Estadísticas detalladas**: Analiza tu vault completo


**SecureVault** - Tu bóveda digital segura 🔐
