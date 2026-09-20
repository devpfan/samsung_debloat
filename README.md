# Samsung Debloat Tool

Una herramienta gráfica, rápida y segura para limpiar el bloatware (aplicaciones preinstaladas basura) de los dispositivos Samsung Galaxy utilizando ADB. Diseñada para operar sin necesidad de acceso Root, manteniendo tu estado de Knox seguro (0x0).

## Características Principales

- **Interfaz Moderna y Asíncrona:** Construida con `CustomTkinter`. La carga de cientos de paquetes nunca congelará la aplicación gracias a su manejo avanzado de hilos (threading).
- **Monitor de Sistema:** Reconoce automáticamente tu dispositivo conectado mostrando el Modelo, Versión de Android y nivel de Batería actual en la barra superior.
- **Detección de Origen Segura:** Clasifica los paquetes entre aplicaciones del "Sistema" y de "Terceros" leyendo las particiones nativas por ADB.
- **Diccionario de Bloatware Integrado:** Traduce los códigos de paquetes ininteligibles a nombres legibles (ej: `com.samsung.android.bixby.agent` -> "Asistente de Voz Bixby"). El diccionario en `bloatware_dict.json` es 100% personalizable.
- **Acciones Rápidas (Clic Derecho):** 
  - 🔍 **Investigar en la Web:** Busca automáticamente el nombre del paquete en tu navegador si no sabes qué hace.
  - 🛑 **Forzar Cierre:** Mata todos los procesos de una app conflictiva.
  - ☢️ **Restablecer App:** Borra todos los datos y caché de la app (como recién instalada).
- **Operaciones de Limpieza:** Activa, Desactiva o Desinstala paquetes ocultos únicamente para el Usuario 0, previniendo daños irreparables.
- **Exportación de Listas:** Exporta lo que estás viendo en la tabla directamente a formato `.csv` (Excel) o `.json` para llevar un respaldo de qué desactivaste.

## Requisitos Previos

- Python 3.10 o superior.
- [Poetry](https://python-poetry.org/) instalado en el sistema.
- Un dispositivo Android/Samsung con la **Depuración por USB** activada en las *Opciones de Desarrollador*.
- Los controladores de [Platform-Tools (ADB)](https://developer.android.com/studio/command-line/adb) instalados y disponibles en el PATH del sistema.

## Instalación y Ejecución

1. Clona este repositorio y entra en la carpeta:
   ```bash
   git clone https://github.com/devpfan/samsung_debloat.git
   cd samsung_debloat
   ```
2. Instala las dependencias gráficas usando Poetry:
   ```bash
   poetry install
   ```
3. Conecta tu teléfono mediante un cable de datos, asegúrate de haberle dado en "Permitir" a la alerta en tu pantalla, y ejecuta la interfaz:
   ```bash
   poetry run python src/ui/app.py
   ```

## Estructura de Carpetas

- `src/core/adb_client.py`: Motor base que ejecuta y parsea todos los subprocesos de ADB con control de errores.
- `src/core/bloatware_dict.json`: Base de datos local para descripciones de paquetes sospechosos habituales (Meta, Microsoft, Bixby).
- `src/ui/app.py`: Archivo de control principal de la interfaz visual y la lógica asíncrona.
- `scripts/test_adb.py`: Herramienta CLI de diagnóstico rápido para validar si los drivers ADB y el teléfono se comunican correctamente.

## Aviso de Seguridad
Desinstalar componentes críticos de Samsung (como `com.samsung.android.lool` o los frameworks de telefonía) puede causar inestabilidad. Al utilizar esta herramienta, el dispositivo siempre puede ser recuperado realizando un restablecimiento de fábrica (Hard Reset), ya que los `.apk` originales de `/system` no son destruidos. Úsala con precaución y siempre utiliza el botón de "Investigar" ante la duda.
