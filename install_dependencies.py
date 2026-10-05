# install_dependencies.py

import subprocess
import sys
from importlib.metadata import PackageNotFoundError, distribution

def check_and_install_package(package_name, pip_name=None):
    """Verifica e instala un paquete si es necesario"""
    if pip_name is None:
        pip_name = package_name
    
    try:
        distribution(package_name)
        print(f"OK: {package_name} ya está instalado")
        return True
    except PackageNotFoundError:
        print(f"Installing {pip_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        print(f"OK: {pip_name} instalado correctamente")
        return True

def install_packages():
    """Instala todas las dependencias necesarias"""
    packages = [
        ("opencv-python", "opencv-python"),
        ("numpy", "numpy"), 
        ("pyautogui", "pyautogui"),
        ("pynput", "pynput"),
        ("pywin32", "pywin32"),
        ("psutil", "psutil")
    ]
    
    for pkg_name, pip_name in packages:
        check_and_install_package(pkg_name, pip_name)

if __name__ == "__main__":
    install_packages()
