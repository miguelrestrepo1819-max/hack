# main.py

from install_dependencies import install_packages

def main():
    # Instalar dependencias si es necesario
    print("Instalando dependencias...")
    install_packages()

    try:
        from aimbot import AimbotApp
        import tkinter as tk
        
        root = tk.Tk()
        app = AimbotApp(root)
        
        # Ejecutar el loop de tkinter
        root.mainloop()
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()
