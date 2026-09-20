import customtkinter as ctk
from src.config import Config

class TopFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        
        # Contenedor para la info del dispositivo y el botón de reinicio
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.device_info_label = ctk.CTkLabel(self.header_frame, text="📱 Esperando conexión...", text_color=Config.COLOR_WARNING, font=ctk.CTkFont(size=14, weight="bold"))
        self.device_info_label.grid(row=0, column=0, sticky="w")
        
        self.btn_reboot = ctk.CTkButton(self.header_frame, text="🔄 Reiniciar Teléfono", width=140, fg_color=Config.COLOR_DANGER, hover_color=Config.COLOR_DANGER_HOVER, command=self.controller.reboot_device_prompt)
        self.btn_reboot.grid(row=0, column=1, sticky="e")
        
        # Barra de búsqueda
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Buscar paquete (ej: bixby, samsung, facebook)...")
        self.search_entry.grid(row=1, column=0, padx=(10, 10), pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.controller.on_search)
        self.search_entry.bind("<<Paste>>", self.controller.on_paste)
        
        # Filtro por Origen
        self.origin_var = ctk.StringVar(value="Sistema")
        self.origin_menu = ctk.CTkOptionMenu(self, values=["Cualquier Origen", "Sistema", "Terceros"],
                                             variable=self.origin_var, command=self.controller.on_filter)
        self.origin_menu.grid(row=1, column=1, padx=(0, 10), pady=10)
        
        # Filtro por Estado
        self.filter_var = ctk.StringVar(value="Todos")
        self.filter_menu = ctk.CTkOptionMenu(self, values=["Todos", "Activo", "Desactivado"],
                                             variable=self.filter_var, command=self.controller.on_filter)
        self.filter_menu.grid(row=1, column=2, padx=(0, 10), pady=10)

    def get_search_text(self):
        return self.search_entry.get()

    def get_origin_filter(self):
        return self.origin_var.get()

    def get_status_filter(self):
        return self.filter_var.get()

    def update_device_info(self, text, color):
        self.device_info_label.configure(text=text, text_color=color)
