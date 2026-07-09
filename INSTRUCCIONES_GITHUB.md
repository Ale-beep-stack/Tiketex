# 📘 Instrucciones para GitHub y Releases

## 🚀 Configuración Inicial (Solo una vez)

### 1. Instalar Git
Si no tienes Git instalado:
- Descarga desde: https://git-scm.com/download/win
- Instala con las opciones por defecto

### 2. Instalar GitHub CLI (Recomendado)
Para subir releases fácilmente:
- Descarga desde: https://cli.github.com/
- Instala y ejecuta en CMD: `gh auth login`
- Sigue las instrucciones para autenticarte

### 3. Instalar Inno Setup
Para crear el instalador:
- Descarga desde: https://jrsoftware.org/isdl.php
- Instala con las opciones por defecto

---

## 📦 Primer Subida a GitHub

### Paso 1: Inicializar el repositorio local
```bash
cd "C:\Users\Alejandro\Documents\Ticket Facturacion Completo"
git init
git add .
git commit -m "Primera versión del Generador de Tickets"
```

### Paso 2: Conectar con GitHub
```bash
git remote add origin https://github.com/Ale-beep-stack/Tiketex.git
git branch -M main
git push -u origin main
```

---

## 🔄 Proceso para Actualizar y Crear Release

### Cada vez que hagas cambios:

#### 1. Actualiza la versión en `version.json`
```json
{
  "version": "1.0.1",  ← Cambia esto
  "fecha": "2026-07-08",
  "cambios": [
    "Corrección de bugs",
    "Mejora en la interfaz"
  ]
}
```

#### 2. Compila y crea el instalador
```bash
COMPILAR_Y_CREAR_INSTALADOR.bat
```

Esto generará:
- `dist\GeneradorTickets.exe`
- `dist\GeneradorTickets_Instalador_v1.0.1.exe`

#### 3. Sube los cambios a GitHub
```bash
git add .
git commit -m "Versión 1.0.1 - Descripción de cambios"
git push
```

#### 4. Crea el Release con los archivos compilados

**Opción A - Con GitHub CLI (Automático):**
```bash
SUBIR_RELEASE_GITHUB.bat
```

**Opción B - Manual (en el navegador):**
1. Ve a: https://github.com/Ale-beep-stack/Tiketex/releases/new
2. Tag: `v1.0.1`
3. Title: `Versión 1.0.1`
4. Description: Describe los cambios
5. Arrastra los archivos:
   - `GeneradorTickets.exe`
   - `GeneradorTickets_Instalador_v1.0.1.exe`
6. Click en "Publish release"

---

## 🎯 Para el Usuario Final

### Primera instalación:
1. Ir a: https://github.com/Ale-beep-stack/Tiketex/releases/latest
2. Descargar: `GeneradorTickets_Instalador_v1.0.0.exe`
3. Ejecutar el instalador (doble clic)
4. ¡Listo!

### Actualizaciones posteriores:
- **¡NO HACE NADA!** El programa se actualiza automáticamente

---

## 📝 Comandos Git Útiles

### Ver estado de cambios:
```bash
git status
```

### Ver historial de commits:
```bash
git log --oneline
```

### Deshacer cambios no guardados:
```bash
git restore .
```

### Ver archivos que se subirán:
```bash
git diff
```

---

## ⚠️ Solución de Problemas

### Si el instalador no se genera:
- Verifica que Inno Setup esté instalado
- Ruta común: `C:\Program Files (x86)\Inno Setup 6\`

### Si no puedes subir a GitHub:
- Verifica tu autenticación: `gh auth status`
- Re-autentícate: `gh auth login`

### Si el auto-actualizador no funciona:
- Verifica que el archivo `version.json` tenga la versión correcta
- Verifica que el release tenga el tag correcto (ej: `v1.0.1`)
- Verifica que el archivo `GeneradorTickets.exe` esté en el release

---

## 📞 Ayuda

Si tienes problemas:
1. Revisa los logs en la consola
2. Verifica que todos los archivos estén presentes
3. Consulta la documentación de Git: https://git-scm.com/doc
