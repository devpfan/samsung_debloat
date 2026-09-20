# Samsung Android Debloat Tool

Herramienta gráfica (GUI) en Python para la auditoría, desinstalación y gestión de paquetes preinstalados (bloatware) en dispositivos Samsung Galaxy. Utiliza **Android Debug Bridge (ADB)** para realizar las operaciones de manera segura, sin necesidad de acceso Root ni alterar el estado de seguridad de Samsung Knox.

## Características Principales

* **No requiere Root**: Realiza operaciones a nivel de usuario (`--user 0`), manteniendo intacta la partición de solo lectura `/system`.
* **100% Seguro y Reversible**: No afecta el estado de Samsung Knox (`0x0`), conserva la certificación Widevine L1 y permite deshacer cualquier cambio restaurando el dispositivo de fábrica.
* **Interfaz Fluida (GUI)**: Desarrollada con `CustomTkinter` y diseñada con concurrencia (`threading`) para asegurar que la aplicación no se congele durante la ejecución de los comandos ADB.
* **Gestión Avanzada**: Permite listar paquetes activos o desactivados, realizar búsquedas con filtros en tiempo real y ejecutar acciones en lote (desactivar, activar o desinstalar) fácilmente.

## Requisitos del Entorno

### Computadora (Host)

* **Python**: Versión `>= 3.10`
* **Tkinter**: Interfaz gráfica nativa de Python (en sistemas Linux puede requerir el paquete `python3-tk`).
* **ADB**: Herramienta `adb` instalada y disponible en las variables de entorno (`PATH`).

### Dispositivo Móvil

* Dispositivo Samsung Galaxy con **Android 8.0** o superior (validado con One UI 2.5 / Android 10).
* **Opciones de desarrollador** y **Depuración por USB** activadas y autorizadas con la PC.

## Instalación y Uso (En Desarrollo)

El proyecto utiliza **Poetry** para la gestión de dependencias y el entorno virtual.

1. Clona el repositorio e ingresa a la carpeta:

   ```bash
   git clone <URL_DEL_REPO>
   cd Samsung_debloat
   ```

2. Inicializa el entorno (opcional si no tienes librerías externas por ahora):

   ```bash
   poetry install
   ```

3. Ejecuta la herramienta gráfica:

   ```bash
   poetry run python src/ui/app.py
   ```

*(Nota: Los comandos de ejecución pueden variar conforme avance el desarrollo de la estructura del proyecto).*

## Advertencias

Deshabilitar ciertos paquetes críticos del sistema podría ocasionar comportamientos inesperados, pérdida de funcionalidades del proveedor o *bootloops* temporales. Utiliza la herramienta bajo tu propia responsabilidad y audita correctamente el bloatware antes de congelarlo.
