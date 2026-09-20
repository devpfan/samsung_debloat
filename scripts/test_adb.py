import sys
import os

# Agregamos la ruta principal del proyecto al path para poder importar src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.adb_client import ADBClient

def main():
    print("⏳ Iniciando prueba de conexión ADB con el dispositivo...")
    client = ADBClient()
    
    # Intentamos listar todos los paquetes del user 0
    success, output = client.list_packages()
    
    if not success:
        print("\n❌ Error al conectar o ejecutar el comando:")
        print(output)
        print("\nRevisa lo siguiente:")
        print("1. Que el celular esté bien conectado por USB.")
        print("2. Que la depuración USB esté activada en opciones de desarrollador.")
        print("3. Que hayas aceptado la huella digital (RSA) de esta computadora en la pantalla del celular.")
        return

    # Si hay éxito, el output es un string largo separado por saltos de línea
    paquetes = output.split('\n')
    
    # Filtramos líneas vacías por si acaso
    paquetes = [p.replace('package:', '').strip() for p in paquetes if p.strip()]
    
    print(f"\n✅ ¡Conexión exitosa! Se detectaron {len(paquetes)} paquetes en el usuario actual.")
    print("\nAquí tienes una muestra de los primeros 15 paquetes encontrados:")
    print("-" * 50)
    
    for i, pkg in enumerate(paquetes[:15]):
        print(f"  {i+1:02d}. {pkg}")
        
    print("-" * 50)
    print("La prueba de adb_client.py es funcional.")

if __name__ == "__main__":
    main()
