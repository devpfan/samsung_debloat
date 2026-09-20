import subprocess
import json
import os
from typing import List, Tuple, Dict, Set
from src.core.logger import get_logger

logger = get_logger(__name__)

class ADBClientError(Exception):
    pass

class ADBClient:
    def __init__(self):
        # Asumimos que ADB está disponible en el PATH del sistema
        self.adb_cmd = "adb"
        self.descriptions = {}
        self._load_dictionary()

    def _load_dictionary(self):
        dict_path = os.path.join(os.path.dirname(__file__), "bloatware_dict.json")
        try:
            with open(dict_path, "r", encoding="utf-8") as f:
                self.descriptions = json.load(f)
        except Exception:
            self.descriptions = {}

    def get_description(self, pkg_name: str) -> str:
        return self.descriptions.get(pkg_name, "Desconocido")

    def _run_command(self, args: List[str]) -> Tuple[bool, str]:
        cmd = [self.adb_cmd] + args
        logger.debug(f"Ejecutando comando ADB: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            output = result.stdout.strip()
            error_output = result.stderr.strip()
            
            # ADB a veces da código 0 (éxito) pero el comando falló internamente
            if result.returncode == 0 and not ("Failure" in output or "Exception" in output):
                logger.debug(f"Éxito: {' '.join(cmd)}")
                return True, output
            else:
                # Si falló, priorizamos mostrar el texto de salida
                err_msg = error_output if error_output else output
                logger.error(f"Fallo ADB [{' '.join(cmd)}]: {err_msg}")
                return False, err_msg
        except FileNotFoundError:
            logger.error("Error crítico: El comando ADB no se encontró en el PATH.")
            return False, "Error: El comando ADB no se encontró en el sistema."
        except Exception as e:
            logger.exception(f"Excepción inesperada al ejecutar {' '.join(cmd)}")
            return False, str(e)

    def list_packages(self, uninstalled: bool = False, disabled: bool = False, system: bool = False, third_party: bool = False) -> Tuple[bool, str]:
        args = ["shell", "pm", "list", "packages"]
        if uninstalled:
            args.append("-u")
        if disabled:
            args.append("-d")
        if system:
            args.append("-s")
        if third_party:
            args.append("-3")
        return self._run_command(args)

    def disable_package(self, package_name: str) -> Tuple[bool, str]:
        return self._run_command(["shell", "pm", "disable-user", "--user", "0", package_name])

    def enable_package(self, package_name: str) -> Tuple[bool, str]:
        success, output = self._run_command(["shell", "pm", "enable", package_name])
        if success:
            # Reinstalamos el paquete en el espacio del usuario por si había sido desinstalado previamente
            self._run_command(["shell", "cmd", "package", "install-existing", package_name])
        return success, output

    def uninstall_package(self, package_name: str) -> Tuple[bool, str]:
        # -k mantiene los datos y el caché. --user 0 lo desinstala solo para el usuario actual.
        return self._run_command(["shell", "pm", "uninstall", "-k", "--user", "0", package_name])

    def force_stop_package(self, package_name: str) -> Tuple[bool, str]:
        """Fuerza el cierre de la aplicación matando todos sus procesos."""
        return self._run_command(["shell", "am", "force-stop", package_name])

    def clear_package_data(self, package_name: str) -> Tuple[bool, str]:
        """Borra todos los datos de usuario y caché de la aplicación (Equivalente a Borrar Datos)."""
        return self._run_command(["shell", "pm", "clear", package_name])

    def get_device_info(self) -> dict:
        """Extrae información básica del dispositivo conectado (Modelo, Android y Batería)."""
        info = {
            "model": "Desconocido",
            "android": "Desconocido",
            "battery": "Desconocido"
        }
        
        succ, out = self._run_command(["shell", "getprop", "ro.product.model"])
        if succ and out and not "error" in out.lower(): 
            info["model"] = out.strip()
            
        succ, out = self._run_command(["shell", "getprop", "ro.build.version.release"])
        if succ and out and not "error" in out.lower(): 
            info["android"] = out.strip()
            
        succ, out = self._run_command(["shell", "dumpsys", "battery"])
        if succ and out and not "error" in out.lower():
            for line in out.split('\n'):
                if "level:" in line:
                    info["battery"] = line.split(":")[1].strip() + "%"
                    break
                    
        return info

    def reboot_device(self) -> Tuple[bool, str]:
        """Envía el comando para reiniciar el dispositivo."""
        return self._run_command(["reboot"])
