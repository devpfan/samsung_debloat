import customtkinter as ctk
from tkinter import ttk, Menu
from src.config import Config

class MiddleFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        columns = ("Paquete", "Estado", "Origen", "Descripción")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", yscrollcommand=self.scrollbar.set, selectmode="browse")
        
        self.tree.heading("Paquete", text="Nombre del Paquete", anchor="w")
        self.tree.heading("Estado", text="Estado", anchor="center")
        self.tree.heading("Origen", text="Origen", anchor="center")
        self.tree.heading("Descripción", text="Descripción", anchor="w")
        
        self.tree.column("Paquete", width=250, anchor="w")
        self.tree.column("Estado", width=100, anchor="center")
        self.tree.column("Origen", width=100, anchor="center")
        self.tree.column("Descripción", width=350, anchor="w")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.config(command=self.tree.yview)
        
        self._build_context_menu()
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def _build_context_menu(self):
        self.context_menu = Menu(self, tearoff=0, bg=Config.COLOR_BG_DARK, fg="white", activebackground=Config.COLOR_PRIMARY)
        self.context_menu.add_command(label="🔍 Investigar paquete en la Web...", command=self.controller.search_package_on_web)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🛑 Forzar Cierre", command=self.controller.force_stop_selected)
        self.context_menu.add_command(label="☢️ Restablecer App (Borrar Todo)", command=self.controller.clear_data_selected)
        
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)
            
    def get_selected_package(self):
        selected = self.tree.selection()
        if not selected:
            return None
        return self.tree.item(selected[0], "values")[0]
        
    def get_all_items(self):
        return [self.tree.item(child, "values") for child in self.tree.get_children()]
        
    def clear_items(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
    def insert_item(self, pkg, status, origin, desc):
        self.tree.insert("", "end", values=(pkg, status, origin, desc))
