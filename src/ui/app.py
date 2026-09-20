import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import csv
import json
import sys
import os

# Asegurar que importamos la lógica del core correctamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.adb_client import ADBClient
from src.config import Config
from src.core.logger import get_logger
from src.ui.components.top_frame import TopFrame
from src.ui.components.middle_frame import MiddleFrame
from src.ui.components.bottom_frame import BottomFrame

logger = get_logger(__name__)

# Configuración global del tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DebloatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        logger.info("Iniciando Samsung Debloat Tool UI")
        
        self.title(Config.APP_TITLE)
        self.geometry(Config.WINDOW_SIZE)
        self.minsize(800, 500)
        
        # Inyección de dependencias
        self.client = ADBClient()
        self.paquetes_cache = []
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._apply_treeview_styles()
        
        # Instanciación de componentes modulares
        self.top_frame = TopFrame(self, controller=self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.middle_frame = MiddleFrame(self, controller=self)
        self.middle_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
        
        self.bottom_frame = BottomFrame(self, controller=self)
        self.bottom_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.refresh_list()

    def _apply_treeview_styles(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", 
                        background=Config.COLOR_BG_DARK, 
                        foreground="white", 
                        rowheight=25, 
                        fieldbackground=Config.COLOR_BG_DARK)
        style.map('Treeview', background=[('selected', Config.COLOR_PRIMARY)])

    # --- Callbacks de UI (Delegados desde los frames) ---
    def on_search(self, event=None):
        self._render_list()
        
    def on_paste(self, event):
        try:
            self.top_frame.search_entry.delete("sel.first", "sel.last")
        except Exception:
            pass
        self.after(50, lambda: self.on_search(None))
        
    def on_filter(self, choice):
        self._render_list()

    def _render_list(self):
        s_text = self.top_frame.get_search_text().lower()
        filter_s = self.top_frame.get_status_filter()
        filter_o = self.top_frame.get_origin_filter()
        
        self.middle_frame.clear_items()
        
        for pkg, status, origen, descripcion in self.paquetes_cache:
            match_search = s_text in pkg.lower() or s_text in descripcion.lower()
            match_status = (filter_s == "Todos") or (filter_s == "Activo" and status == "Activo") or (filter_s == "Desactivado" and status == "Desactivado")
            match_origin = (filter_o == "Cualquier Origen") or (filter_o == origen)
            
            if match_search and match_status and match_origin:
                self.middle_frame.insert_item(pkg, status, origen, descripcion)

    # --- Acciones Menú Contextual y Exportación ---
    def search_package_on_web(self):
        pkg = self.middle_frame.get_selected_package()
        if pkg:
            url = f"https://www.google.com/search?q=android+package+{pkg}"
            webbrowser.open(url)

    def force_stop_selected(self):
        pkg = self.middle_frame.get_selected_package()
        if not pkg: return
        self.bottom_frame.update_status(f"Forzando cierre de {pkg}...", Config.COLOR_WARNING)
        def run():
            success, out = self.client.force_stop_package(pkg)
            self.after(0, lambda: self._handle_action_result(success, f"Proceso detenido: {pkg}", out))
        threading.Thread(target=run, daemon=True).start()

    def clear_data_selected(self):
        pkg = self.middle_frame.get_selected_package()
        if not pkg: return
        
        confirm = messagebox.askyesno(
            "⚠️ ADVERTENCIA CRÍTICA", 
            f"¿Estás seguro que deseas BORRAR TODOS LOS DATOS de '{pkg}'?\n\n"
            "Esto dejará la aplicación como recién instalada. Perderás tus cuentas iniciadas.", 
            icon="warning"
        )
        if not confirm:
            return
            
        self.bottom_frame.update_status(f"Restableciendo {pkg}...", Config.COLOR_WARNING)
        def run():
            success, out = self.client.clear_package_data(pkg)
            self.after(0, lambda: self._handle_action_result(success, f"App restablecida: {pkg}", out))
            self.after(0, self.refresh_list)
        threading.Thread(target=run, daemon=True).start()

    def reboot_device_prompt(self):
        confirm = messagebox.askyesno(
            "Confirmar Reinicio", 
            "¿Estás seguro que deseas reiniciar el dispositivo conectado?\n\nEl teléfono se apagará y volverá a encender.", 
            icon="warning"
        )
        if confirm:
            self.bottom_frame.update_status("Enviando orden de reinicio...", Config.COLOR_WARNING)
            def run():
                success, out = self.client.reboot_device()
                self.after(0, lambda: self._handle_action_result(success, "Dispositivo reiniciándose...", out))
            threading.Thread(target=run, daemon=True).start()

    def export_list(self):
        items = self.middle_frame.get_all_items()
        if not items:
            messagebox.showinfo("Exportar", "No hay paquetes para exportar.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv"), ("Archivo JSON", "*.json")],
            title="Guardar lista..."
        )
        if not file_path:
            return
            
        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Paquete", "Estado", "Origen", "Descripción"])
                    writer.writerows(items)
            elif file_path.endswith('.json'):
                json_data = [{"paquete": r[0], "estado": r[1], "origen": r[2], "descripcion": r[3]} for r in items]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", "Lista exportada exitosamente.")
            logger.info(f"Lista exportada a {file_path}")
        except Exception as e:
            logger.error(f"Error exportando: {e}")
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")

    # --- Acciones ADB Principales ---
    def refresh_list(self):
        self.bottom_frame.set_buttons_state("disabled")
        self.bottom_frame.update_status("Cargando paquetes de ADB...", "white")
        self.middle_frame.clear_items()
        self.paquetes_cache.clear()
        
        threading.Thread(target=self._load_packages_thread, daemon=True).start()

    def _load_packages_thread(self):
        device_info = self.client.get_device_info()
        def update_device_label():
            if device_info["model"] == "Desconocido":
                self.top_frame.update_device_info("❌ No se detectó dispositivo por ADB", Config.COLOR_DANGER)
            else:
                self.top_frame.update_device_info(f"📱 {device_info['model']}  |  🤖 Android {device_info['android']}  |  🔋 {device_info['battery']}", Config.COLOR_SUCCESS)
        self.after(0, update_device_label)
        
        s_act, o_act = self.client.list_packages(disabled=False, uninstalled=False)
        s_dis, o_dis = self.client.list_packages(disabled=True, uninstalled=False)
        
        s_sys, o_sys = self.client.list_packages(system=True)
        s_3rd, o_3rd = self.client.list_packages(third_party=True)
        
        if not s_act and not s_dis:
            logger.error("No se detectó el comando ADB o falló list_packages")
            self.after(0, lambda: self._handle_action_result(False, "No se detectó dispositivo o ADB", o_act))
            return
            
        todos = [p.replace('package:', '').strip() for p in o_act.split('\n') if p.strip()]
        desactivados = [p.replace('package:', '').strip() for p in o_dis.split('\n') if p.strip()]
        
        desactivados_set = set(desactivados)
        activos = [p for p in todos if p not in desactivados_set]
        
        sys_pkgs = set([p.replace('package:', '').strip() for p in o_sys.split('\n') if p.strip()])
        usr_pkgs = set([p.replace('package:', '').strip() for p in o_3rd.split('\n') if p.strip()])
        
        cache = []
        for p in activos:
            origen = "Sistema" if p in sys_pkgs else "Terceros" if p in usr_pkgs else "Cualquier Origen"
            desc = self.client.get_description(p)
            cache.append((p, "Activo", origen, desc))
            
        for p in desactivados:
            origen = "Sistema" if p in sys_pkgs else "Terceros" if p in usr_pkgs else "Cualquier Origen"
            desc = self.client.get_description(p)
            cache.append((p, "Desactivado", origen, desc))
            
        self.paquetes_cache = sorted(cache, key=lambda x: x[0])
        
        self.after(0, self._render_list)
        self.after(0, lambda: self.bottom_frame.update_status(f"Se cargaron {len(self.paquetes_cache)} paquetes.", Config.COLOR_SUCCESS))
        self.after(0, lambda: self.bottom_frame.set_buttons_state("normal"))
        logger.info(f"Refresco de lista completado: {len(self.paquetes_cache)} paquetes")

    def _handle_action_result(self, success: bool, success_msg: str, output: str):
        self.bottom_frame.set_buttons_state("normal")
        if success:
            self.bottom_frame.update_status(success_msg, Config.COLOR_SUCCESS)
            logger.info(success_msg)
        else:
            self.bottom_frame.update_status("Error en la operación", Config.COLOR_DANGER)
            messagebox.showerror("Error de ADB", output)
            logger.error(f"Error UI: {output}")

    def disable_selected(self):
        pkg = self.middle_frame.get_selected_package()
        if not pkg: return
        self.bottom_frame.update_status(f"Desactivando {pkg}...", "white")
        self.bottom_frame.set_buttons_state("disabled")
        threading.Thread(target=lambda: self._run_adb_action(self.client.disable_package, pkg, f"Desactivado: {pkg}"), daemon=True).start()

    def enable_selected(self):
        pkg = self.middle_frame.get_selected_package()
        if not pkg: return
        self.bottom_frame.update_status(f"Activando {pkg}...", "white")
        self.bottom_frame.set_buttons_state("disabled")
        threading.Thread(target=lambda: self._run_adb_action(self.client.enable_package, pkg, f"Activado: {pkg}"), daemon=True).start()

    def uninstall_selected(self):
        pkg = self.middle_frame.get_selected_package()
        if not pkg: return
        
        confirm = messagebox.askyesno("Confirmar Desinstalación", f"¿Estás seguro que deseas DESINSTALAR '{pkg}'?\nEsto lo removerá para el usuario actual.", icon="warning")
        if confirm:
            self.bottom_frame.update_status(f"Desinstalando {pkg}...", Config.COLOR_WARNING)
            self.bottom_frame.set_buttons_state("disabled")
            threading.Thread(target=lambda: self._run_adb_action(self.client.uninstall_package, pkg, f"Desinstalado: {pkg}"), daemon=True).start()

    def _run_adb_action(self, func, pkg, success_msg):
        success, out = func(pkg)
        self.after(0, lambda: self._handle_action_result(success, success_msg, out))
        if success:
            self.after(0, self.refresh_list)

if __name__ == "__main__":
    app = DebloatApp()
    try:
        app.mainloop()
    except Exception as e:
        logger.critical(f"La aplicación crasheó: {e}", exc_info=True)
