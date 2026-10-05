import tkinter as tk
from tkinter import ttk, messagebox
import sys
import threading
import time
import pyautogui
import cv2
import numpy as np
import psutil
import socket
import struct
import json
import os
import logging
from datetime import datetime
from collections import deque
from pynput import keyboard

# Configuración del log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("aimbot.log"),
        logging.StreamHandler()
    ]
)

class AimbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aimbot para Warzone")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Variables de configuración
        self.is_running = False
        self.aimbot_thread = None
        self.debug_mode = tk.BooleanVar()
        self.debug_mode.set(False)
        self.current_mode = "aimbot"
        self.sensitivity = 50
        self.aim_speed = 30
        
        # Configuración de red
        self.udp_port = 8080
        self.tcp_port = 8081
        
        # Variables para la memoria compartida
        self.memory_data = {}
        
        # Inicializar interfaz
        self.create_widgets()
        
        # Verificar y instalar dependencias
        self.install_dependencies()

        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_global_key_press)
        self.keyboard_listener.start()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuración de grilla
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Aimbot para Warzone", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # Configuración de modo
        mode_frame = ttk.LabelFrame(main_frame, text="Modo de Operación", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.mode_var = tk.StringVar(value="aimbot")
        modes = ["aimbot", "espionaje", "inactividad"]
        for i, mode in enumerate(modes):
            ttk.Radiobutton(mode_frame, text=mode.capitalize(), variable=self.mode_var, 
                          value=mode, command=self.on_mode_change).grid(row=0, column=i, padx=10)
        
        # Configuración de sensibilidad
        sensitivity_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        sensitivity_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(sensitivity_frame, text="Sensibilidad:").grid(row=0, column=0, sticky=tk.W)
        self.sensitivity_slider = ttk.Scale(sensitivity_frame, from_=1, to=100, orient="horizontal", 
                                           command=lambda x: setattr(self, 'sensitivity', int(x)))
        self.sensitivity_slider.set(50)
        self.sensitivity_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Label(sensitivity_frame, text="Velocidad del Aimbot:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.speed_slider = ttk.Scale(sensitivity_frame, from_=1, to=100, orient="horizontal",
                                     command=lambda x: setattr(self, 'aim_speed', int(x)))
        self.speed_slider.set(30)
        self.speed_slider.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
        
        # Control de UDP/TCP
        network_frame = ttk.LabelFrame(main_frame, text="Red", padding="10")
        network_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.udp_port_var = tk.StringVar(value=str(self.udp_port))
        ttk.Label(network_frame, text="Puerto UDP:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(network_frame, textvariable=self.udp_port_var).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        self.tcp_port_var = tk.StringVar(value=str(self.tcp_port))
        ttk.Label(network_frame, text="Puerto TCP:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Entry(network_frame, textvariable=self.tcp_port_var).grid(row=1, column=1, padx=(10, 0), sticky=tk.W, pady=(5, 0))
        
        # Configuración de debug
        self.debug_check = ttk.Checkbutton(main_frame, text="Modo Debug", variable=self.debug_mode)
        self.debug_check.grid(row=4, column=0, sticky=tk.W, pady=(0, 20))
        
        # Botones de control
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="Iniciar", command=self.start_aimbot)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Detener", command=self.stop_aimbot, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Estado del sistema
        status_frame = ttk.LabelFrame(main_frame, text="Estado del Sistema", padding="10")
        status_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, text="Listo para iniciar...", foreground='gray')
        self.status_label.pack()
        ttk.Label(status_frame, text="Presiona K para cerrar el programa").pack()
        
        # Registro de datos
        log_frame = ttk.LabelFrame(main_frame, text="Registro", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.log_text = tk.Text(log_frame, height=8, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def on_mode_change(self):
        self.current_mode = self.mode_var.get()
        logging.info(f"Modo cambiado a: {self.current_mode}")
    
    def install_dependencies(self):
        from install_dependencies import install_packages

        install_packages()
                
    def start_aimbot(self):
        if self.is_running:
            return
            
        # Obtener los puertos
        try:
            udp_port = int(self.udp_port_var.get())
            tcp_port = int(self.tcp_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Puerto inválido")
            return
        
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Iniciando aimbot...", foreground='green')
        
        # Iniciar el hilo de aimbot en segundo plano
        self.aimbot_thread = threading.Thread(target=self.run_aimbot, args=(udp_port, tcp_port))
        self.aimbot_thread.daemon = True
        self.aimbot_thread.start()
        
    def stop_aimbot(self):
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Aimbot detenido", foreground='red')

    def on_global_key_press(self, key):
        pressed_key = getattr(key, "char", None)
        if isinstance(pressed_key, str) and pressed_key.lower() == "k":
            self.root.after(0, self.close_application)
            return False

    def close_application(self):
        self.stop_aimbot()
        self.keyboard_listener.stop()
        self.root.destroy()
        
    def run_aimbot(self, udp_port, tcp_port):
        # Configurar pyautogui para evitar el fail-safe
        pyautogui.FAILSAFE = False
        
        logging.info("Iniciando aimbot...")
        self.status_label.config(text="Ejecutando...", foreground='orange')
        
        try:
            # Iniciar servidor UDP
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.bind(('localhost', udp_port))
            
            # Iniciar servidor TCP
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_socket.bind(('localhost', tcp_port))
            tcp_socket.listen(5)
            
            logging.info(f"Servidores iniciados: UDP:{udp_port}, TCP:{tcp_port}")
            
            # Bucle principal
            while self.is_running:
                if self.current_mode == "aimbot":
                    # Simular lectura de memoria compartida (en un sistema real, se usaría shared_memory)
                    self.memory_data = {
                        'player_position': [100, 200],
                        'enemy_positions': [[350, 400], [800, 700]],
                        'weapon_info': {'type': 'rifle', 'ammo': 30},
                        'game_state': {
                            'health': 100,
                            'armor': 50,
                            'is_in_combat': True
                        }
                    }
                    
                    # Procesar aimbot
                    self.process_aimbot()
                
                elif self.current_mode == "espionaje":
                    # Simular espionaje de enemigos
                    self.process_spying()
                
                elif self.current_mode == "inactividad":
                    # Simular detección de inactividad
                    self.process_inactivity_detection()
                
                time.sleep(0.05)  # 20 FPS
                
        except Exception as e:
            logging.error(f"Error en el aimbot: {str(e)}")
            messagebox.showerror("Error", f"Error al ejecutar aimbot: {str(e)}")
        
        finally:
            try:
                udp_socket.close()
                tcp_socket.close()
            except:
                pass
            self.status_label.config(text="Aimbot detenido", foreground='red')
    
    def process_aimbot(self):
        # Simular el proceso de aimbot con movimiento natural
        if not self.memory_data.get('enemy_positions'):
            return
            
        # Encontrar enemigo más cercano (simplificado)
        player_pos = self.memory_data['player_position']
        enemy_positions = self.memory_data['enemy_positions']
        
        if len(enemy_positions) == 0:
            return
        
        closest_enemy = min(enemy_positions, key=lambda pos: 
                          (pos[0] - player_pos[0])**2 + (pos[1] - player_pos[1])**2)
        
        # Calcular movimiento con sensibilidad
        dx = (closest_enemy[0] - player_pos[0]) * self.sensitivity / 50.0
        dy = (closest_enemy[1] - player_pos[1]) * self.sensitivity / 50.0
        
        # Simular movimiento suave con variación natural
        target_x = pyautogui.position()[0] + dx
        target_y = pyautogui.position()[1] + dy
        
        # Ajustar velocidad de movimiento
        steps = max(1, int(self.aim_speed / 5))
        
        # Mover el mouse con movimientos naturales (evitando fail-safe)
        current_x, current_y = pyautogui.position()
        
        for i in range(steps):
            progress = float(i) / (steps - 1) if steps > 1 else 1.0
            new_x = int(current_x + (target_x - current_x) * progress)
            new_y = int(current_y + (target_y - current_y) * progress)
            
            # Evitar que el mouse salga de la pantalla
            screen_width, screen_height = pyautogui.size()
            new_x = max(0, min(new_x, screen_width))
            new_y = max(0, min(new_y, screen_height))
            
            pyautogui.moveTo(new_x, new_y, duration=0.01)
            
        if self.debug_mode.get():
            logging.info(f"Aimbot moviendo a: ({new_x}, {new_y})")
    
    def process_spying(self):
        # Simular detección de enemigos
        if not self.memory_data:
            return
            
        enemies = self.memory_data.get('enemy_positions', [])
        
        for i, enemy_pos in enumerate(enemies):
            logging.info(f"Enemigo {i+1} detectado en: ({enemy_pos[0]}, {enemy_pos[1]})")
    
    def process_inactivity_detection(self):
        # Simular detección de inactividad
        pass
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
        # Limitar el tamaño del registro a 500 líneas
        if int(self.log_text.index('end-1c').split('.')[0]) > 500:
            self.log_text.delete(1.0, 2.0)

def main():
    root = tk.Tk()
    app = AimbotApp(root)
    
    # Establecer el tamaño mínimo de la ventana
    root.minsize(600, 700)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Saliendo...")
        sys.exit(0)

if __name__ == "__main__":
    main()
