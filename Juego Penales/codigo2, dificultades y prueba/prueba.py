import asyncio
import websockets
import json
import random

async def send_random_hits(websocket):
    print("¡Juego conectado al detector!")
    try:
        while True:
            # Simulamos un impacto cada 3 segundos
            await asyncio.sleep(3)
            
            # Coordenadas aleatorias (x, y entre 0.0 y 1.0)
            data = {
                "x": random.uniform(0.2, 0.8), 
                "y": random.uniform(0.2, 0.6)
            }
            
            print(f"Mandando pelotazo a: {data}")
            await websocket.send(json.dumps(data))
    except websockets.exceptions.ConnectionClosed:
        print("Juego desconectado.")

async def main():
    print("Servidor activo en ws://localhost:8765")
    print("Abrí el juego.html en el navegador...")
    
    # Esta es la forma correcta en las versiones nuevas
    async with websockets.serve(send_random_hits, "localhost", 8765):
        await asyncio.Future()  # Esto mantiene el servidor corriendo para siempre

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")