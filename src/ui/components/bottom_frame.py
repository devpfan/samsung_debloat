import customtkinter as ctk
from src.config import Config

class BottomFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        self.btn_refresh = ctk.CTkButton(self, text="Actualizar Lista", command=self.controller.refresh_list)
        self.btn_refresh.pack(side="left", padx=10, pady=10)
        
        self.btn_export = ctk.CTkButton(self, text="Exportar", width=100, fg_color=Config.COLOR_PRIMARY, hover_color=Config.COLOR_PRIMARY_HOVER, command=self.controller.export_list)
        self.btn_export.pack(side="left", padx=(0, 10), pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="Iniciando...", text_color="gray")
        self.status_label.pack(side="left", padx=20)
        
        self.btn_uninstall = ctk.CTkButton(self, text="Desinstalar (Avanzado)", width=140, fg_color=Config.COLOR_DANGER, hover_color=Config.COLOR_DANGER_HOVER, command=self.controller.uninstall_selected)
        self.btn_uninstall.pack(side="right", padx=10, pady=10)
        
        self.btn_disable = ctk.CTkButton(self, text="Desactivar", width=100, command=self.controller.disable_selected)
        self.btn_disable.pack(side="right", padx=10, pady=10)
        
        self.btn_enable = ctk.CTkButton(self, text="Activar", width=100, command=self.controller.enable_selected)
        self.btn_enable.pack(side="right", padx=10, pady=10)
        
    def update_status(self, text, color="gray"):
        self.status_label.configure(text=text, text_color=color)
        
    def set_buttons_state(self, state):
        self.btn_refresh.configure(state=state)
        self.btn_enable.configure(state=state)
        self.btn_disable.configure(state=state)
        self.btn_uninstall.configure(state=state)
        self.btn_export.configure(state=state)
