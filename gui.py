# gui.py

import tkinter as tk
from tkinter import ttk
import threading
from aimbot import Aimbot

class WarzoneAimbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Warzone Aimbot")
        self.root.geometry("500x600")

        # Instancia del aimbot
        self.aimbot = None
        
        # Configuración de widgets
        self.create_widgets()
        
    def create_widgets(self):
        tk.Label(self.root, text="Warzone Aimbot", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Modo de operación (Radio buttons)
        mode_frame = ttk.Frame(self.root)
        mode_frame.pack(pady=5)
        self.mode_var = tk.StringVar(value="aimbot")
        modes = [("Aimbot", "aimbot"), ("Espionaje", "spy"), ("Inactividad", "idle")]
        for text, value in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=value).pack(anchor='w')

        # Velocidad del aimbot
        tk.Label(self.root, text="Velocidad Aimbot (0-1):").pack(pady=5)
        self.speed = tk.Scale(self.root, from_=0.0, to=1.0, resolution=0.01, orient='horizontal')
        self.speed.set(0.5)  # Valor por defecto
        self.speed.pack(pady=5)

        # Puerto UDP
        tk.Label(self.root, text="Puerto UDP (ej: 5005):").pack(pady=5)
        self.port_entry = ttk.Entry(self.root)
        self.port_entry.insert(0, "5005")
        self.port_entry.pack(pady=5)

        # Botones de control
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Iniciar", command=self.start).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Detener", command=self.stop).pack(side=tk.LEFT, padx=10)
        
        # Debug Mode Toggle
        self.debug_var = tk.BooleanVar()
        ttk.Checkbutton(self.root, text="Modo Debug", variable=self.debug_var).pack(pady=5)

        # Estado del aimbot
        self.status_label = tk.Label(self.root, text="Estado: Detenido")
        self.status_label.pack(pady=10)
        
    def start(self):
        """Inicia el aimbot"""
        try:
            speed = float(self.speed.get())
            
            if not self.aimbot:
                self.aimbot = Aimbot(speed=speed)
                self.aimbot.set_debug(self.debug_var.get())
                
            # Iniciar en hilo separado
            thread = threading.Thread(target=self.run_aimbot)
            thread.daemon = True
            thread.start()
            
            self.status_label.config(text=f"Estado: Ejecutando (Velocidad: {speed})")
            print("Aimbot iniciado...")
            
        except Exception as e:
            print(f"Error al iniciar aimbot: {e}")
            
    def stop(self):
        """Detiene el aimbot"""
        if self.aimbot:
            self.aimbot.stop_aimbot()
            self.status_label.config(text="Estado: Detenido")
            print("Aimbot detenido...")
        
    def run_aimbot(self):
        """Ejecuta el aimbot en segundo plano"""
        try:
            if self.aimbot:
                self.aimbot.start_aimbot()
        except Exception as e:
            print(f"Error al ejecutar aimbot: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WarzoneAimbotGUI(root)
    root.mainloop()
