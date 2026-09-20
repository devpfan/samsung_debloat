import customtkinter as ctk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Asegurar que importamos la lógica del core correctamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core.adb_client import ADBClient

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Samsung Debloat Tool")
        self.geometry("1000x700")
        self.minsize(900, 600)
        
        self.client = ADBClient()
        self.paquetes_cache = [] # Lista de tuplas: (pkg, status, origen)
        
        # Configurar la cuadrícula principal (3 filas: Top, Middle, Bottom)
        self.grid_rowconfigure(0, weight=0) # Barra superior (tamaño fijo)
        self.grid_rowconfigure(1, weight=1) # Lista central (expansible)
        self.grid_rowconfigure(2, weight=0) # Botones inferiores (tamaño fijo)
        self.grid_columnconfigure(0, weight=1)
        
        self._build_top_frame()
        self._build_middle_frame()
        self._build_bottom_frame()
        
        # Cargar lista automáticamente al iniciar (en hilo separado)
        self.refresh_list()

    def _build_top_frame(self):
        """Construye la barra superior con el buscador y filtros."""
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        
        # Barra de búsqueda
        self.search_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Buscar paquete (ej: bixby, samsung, facebook)...")
        self.search_entry.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search) # Filtrar en tiempo real mientras el usuario escribe
        
        # Filtro por Origen
        self.origin_var = ctk.StringVar(value="Sistema") # Por defecto solo mostramos los del sistema
        self.origin_menu = ctk.CTkOptionMenu(self.top_frame, values=["Cualquier Origen", "Sistema", "Terceros"],
                                             variable=self.origin_var, command=self.on_filter)
        self.origin_menu.grid(row=0, column=1, padx=(0, 10), pady=10)
        
        # Filtro por Estado
        self.filter_var = ctk.StringVar(value="Todos")
        self.filter_menu = ctk.CTkOptionMenu(self.top_frame, values=["Todos", "Activo", "Desactivado"],
                                             variable=self.filter_var, command=self.on_filter)
        self.filter_menu.grid(row=0, column=2, padx=(0, 10), pady=10)

    def _build_middle_frame(self):
        """Construye la sección central donde va la lista (Treeview)."""
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.middle_frame.grid_rowconfigure(0, weight=1)
        self.middle_frame.grid_columnconfigure(0, weight=1)
        
        # Estilo para el Treeview (adaptado al modo oscuro de CustomTkinter)
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=30,
                        fieldbackground="#2b2b2b",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#333333", foreground="white", font=('Helvetica', 11, 'bold'), borderwidth=0)
        
        # Componente Treeview (Ahora con 3 columnas)
        columns = ("Paquete", "Estado", "Origen")
        self.tree = ttk.Treeview(self.middle_frame, columns=columns, show="headings", style="Treeview")
        self.tree.heading("Paquete", text="Nombre del Paquete", anchor="w")
        self.tree.heading("Estado", text="Estado", anchor="center")
        self.tree.heading("Origen", text="Origen", anchor="center")
        
        self.tree.column("Paquete", width=600, anchor="w")
        self.tree.column("Estado", width=150, anchor="center")
        self.tree.column("Origen", width=150, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar vertical nativo de tkinter (ttk)
        scrollbar = ttk.Scrollbar(self.middle_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_bottom_frame(self):
        """Construye los botones de acción de la parte inferior."""
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.btn_refresh = ctk.CTkButton(self.bottom_frame, text="Actualizar Lista", command=self.refresh_list)
        self.btn_refresh.pack(side="left", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Iniciando...", text_color="gray")
        self.status_label.pack(side="left", padx=20)
        
        # Botones de acción alineados a la derecha
        self.btn_uninstall = ctk.CTkButton(self.bottom_frame, text="Desinstalar (Avanzado)", fg_color="#d32f2f", hover_color="#9a0007", command=self.uninstall_selected)
        self.btn_uninstall.pack(side="right", padx=10, pady=10)
        
        self.btn_disable = ctk.CTkButton(self.bottom_frame, text="Desactivar", fg_color="#f57c00", hover_color="#b26a00", command=self.disable_selected)
        self.btn_disable.pack(side="right", padx=10, pady=10)
        
        self.btn_enable = ctk.CTkButton(self.bottom_frame, text="Activar / Restaurar", fg_color="#388e3c", hover_color="#00600f", command=self.enable_selected)
        self.btn_enable.pack(side="right", padx=10, pady=10)

    # ---- Lógica de ADB y Asincronismo ----
    
    def refresh_list(self):
        """Pide los datos de ADB en un hilo separado para no congelar la UI."""
        self.status_label.configure(text="Obteniendo y clasificando paquetes...", text_color="#f57c00")
        self.tree.delete(*self.tree.get_children()) # Limpiar lista actual
        self.btn_refresh.configure(state="disabled")
        
        # Lanzar hilo en background (daemon=True para que muera al cerrar la app)
        threading.Thread(target=self._load_packages_thread, daemon=True).start()

    def _load_packages_thread(self):
        """Se ejecuta fuera del hilo principal."""
        # 1. Obtenemos listas base por estado
        s_act, o_act = self.client.list_packages(disabled=False, uninstalled=False)
        s_dis, o_dis = self.client.list_packages(disabled=True, uninstalled=False)
        
        # 2. Obtenemos listas de clasificación por origen
        s_sys, o_sys = self.client.list_packages(system=True)
        s_3rd, o_3rd = self.client.list_packages(third_party=True)
        
        if not s_act:
            # Hubo error de ADB
            self.after(0, lambda: self.status_label.configure(text="Error de conexión ADB. ¿Está el celular conectado?", text_color="#d32f2f"))
            self.after(0, lambda: self.btn_refresh.configure(state="normal"))
            return
            
        activos = [p.replace('package:', '').strip() for p in o_act.split('\n') if p.strip()]
        desactivados = [p.replace('package:', '').strip() for p in o_dis.split('\n') if p.strip()]
        
        # Sets para búsqueda súper rápida
        sys_pkgs = set([p.replace('package:', '').strip() for p in o_sys.split('\n') if p.strip()])
        usr_pkgs = set([p.replace('package:', '').strip() for p in o_3rd.split('\n') if p.strip()])
        
        def determinar_origen(pkg):
            if pkg in usr_pkgs: return "Terceros"
            if pkg in sys_pkgs: return "Sistema"
            return "Desconocido"
        
        # Guardar todo en caché para filtrado instantáneo
        self.paquetes_cache = []
        for pkg in activos:
            self.paquetes_cache.append((pkg, "Activo", determinar_origen(pkg)))
        for pkg in desactivados:
            self.paquetes_cache.append((pkg, "Desactivado", determinar_origen(pkg)))
            
        # Actualizar interfaz en el hilo principal (usar after(0, ...))
        self.after(0, lambda: self._render_list(self.search_entry.get(), self.filter_var.get(), self.origin_var.get()))
        self.after(0, lambda: self.status_label.configure(text=f"Carga completa: {len(self.paquetes_cache)} paquetes encontrados.", text_color="#388e3c"))
        self.after(0, lambda: self.btn_refresh.configure(state="normal"))

    def _render_list(self, filter_text="", filter_status="Todos", filter_origin="Sistema"):
        """Dibuja los elementos en el Treeview aplicando los filtros de estado y origen."""
        self.tree.delete(*self.tree.get_children())
        filter_text = filter_text.lower()
        
        for pkg, status, origen in self.paquetes_cache:
            if filter_text in pkg.lower():
                match_status = (filter_status == "Todos" or filter_status == status)
                match_origin = (filter_origin == "Cualquier Origen" or filter_origin == origen)
                
                if match_status and match_origin:
                    self.tree.insert("", "end", values=(pkg, status, origen))
                    
    def on_search(self, event):
        """Se lanza al soltar una tecla en el buscador."""
        self._render_list(self.search_entry.get(), self.filter_var.get(), self.origin_var.get())
        
    def on_filter(self, choice):
        """Se lanza al cambiar cualquiera de los menús desplegables."""
        self._render_list(self.search_entry.get(), self.filter_var.get(), self.origin_var.get())

    # ---- Acciones ----
    
    def _get_selected_package(self):
        """Devuelve el paquete seleccionado en la lista o muestra una advertencia."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un paquete de la lista primero.")
            return None
        item_values = self.tree.item(selected_item[0], "values")
        return item_values[0] # Retorna solo el nombre del paquete (columna 0)

    def disable_selected(self):
        pkg = self._get_selected_package()
        if not pkg: return
        
        self.status_label.configure(text=f"Desactivando {pkg}...", text_color="#f57c00")
        
        def run():
            success, out = self.client.disable_package(pkg)
            self.after(0, lambda: self._handle_action_result(success, f"Paquete desactivado: {pkg}", out))
            self.after(0, self.refresh_list)
            
        threading.Thread(target=run, daemon=True).start()

    def enable_selected(self):
        pkg = self._get_selected_package()
        if not pkg: return
        
        self.status_label.configure(text=f"Activando/Restaurando {pkg}...", text_color="#f57c00")
        
        def run():
            success, out = self.client.enable_package(pkg)
            self.after(0, lambda: self._handle_action_result(success, f"Paquete activado: {pkg}", out))
            self.after(0, self.refresh_list)
            
        threading.Thread(target=run, daemon=True).start()

    def uninstall_selected(self):
        pkg = self._get_selected_package()
        if not pkg: return
        
        confirm = messagebox.askyesno("Confirmar Desinstalación", 
                                      f"¿Estás seguro que deseas desinstalar '{pkg}' del usuario?\n\n"
                                      "Esto es útil para apps rebeldes. Si te equivocas, podrás intentar recuperarla con el botón 'Activar / Restaurar'.", 
                                      icon="warning")
        if not confirm:
            return
            
        self.status_label.configure(text=f"Desinstalando {pkg}...", text_color="#f57c00")
        
        def run():
            success, out = self.client.uninstall_package(pkg)
            self.after(0, lambda: self._handle_action_result(success, f"Paquete desinstalado: {pkg}", out))
            self.after(0, self.refresh_list)
            
        threading.Thread(target=run, daemon=True).start()
        
    def _handle_action_result(self, success, success_msg, error_msg):
        """Procesa el resultado de un comando ADB mostrando éxito o el mensaje de error."""
        if success:
            self.status_label.configure(text=success_msg, text_color="#388e3c")
        else:
            self.status_label.configure(text="Error al procesar el paquete.", text_color="#d32f2f")
            messagebox.showerror("Error ADB", f"Ocurrió un error:\n{error_msg}")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
