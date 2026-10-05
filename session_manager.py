# session_manager.py

import atexit
import time

class SessionManager:
    def __init__(self, aimbot_instance):
        self.aimbot = aimbot_instance
        self.running = True

    def start(self):
        print("Sesión iniciada...")
        while self.running:
            try:
                # Simulación de loop continuo (puede ser reemplazado por funciones realistas)
                time.sleep(1)

                # Ejemplo: ejecutar aimbot si está activo
                if hasattr(self.aimbot, 'aim_at_target'):
                    self.aimbot.aim_at_target()

            except KeyboardInterrupt:
                break

        print("Sesión terminada.")

    def stop(self):
        self.running = False
