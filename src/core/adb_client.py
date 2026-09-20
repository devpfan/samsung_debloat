import subprocess
import json
import os
from typing import Tuple, List

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
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            output = result.stdout.strip()
            error_output = result.stderr.strip()
            
            # ADB a veces da código 0 (éxito) pero el comando falló internamente
            if result.returncode == 0 and not ("Failure" in output or "Exception" in output):
                return True, output
            else:
                # Si falló, priorizamos mostrar el texto de salida (donde ADB suele escupir el "Failure")
                return False, error_output if error_output else output
        except FileNotFoundError:
            return False, "Error: El comando ADB no se encontró en el sistema."
        except Exception as e:
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
        return self._run_command(["shell", "pm", "uninstall", "-k", "--user", "0", package_name])
