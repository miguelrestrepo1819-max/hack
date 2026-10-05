# remote_control.py

import socket
import threading
from typing import Callable

class RemoteController:
    def __init__(self, port: int = 5005):
        self.port = port
        self.socket = None
        self.running = False
        
    def start_server(self):
        """Inicia servidor UDP para control remoto"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(("127.0.0.1", self.port))
            self.running = True
            
            thread = threading.Thread(target=self._listen_for_commands)
            thread.daemon = True
            thread.start()
            
            print(f"Servidor UDP iniciado en puerto {self.port}")
            
        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
    
    def _listen_for_commands(self):
        """Escucha comandos remotos"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                command = data.decode('utf-8')
                print(f"Comando recibido desde {addr}: {command}")
                
                # Aquí podrías implementar lógica para procesar comandos
                if command.lower() == "start":
                    print("Iniciando aimbot...")
                elif command.lower() == "stop":
                    print("Deteniendo aimbot...")
                    
            except Exception as e:
                if self.running:  # Solo mostrar si no es por cierre
                    print(f"Error al recibir comando: {e}")
    
    def stop_server(self):
        """Detiene el servidor"""
        self.running = False
        if self.socket:
            self.socket.close()
