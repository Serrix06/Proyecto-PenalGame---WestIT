import cv2
import asyncio
import websockets
import json
import numpy as np

# --- CONFIGURACIÓN ---
UMBRAL_MOVIMIENTO = 2000  # Píxeles mínimos que deben cambiar para considerar un golpe
CAM_INDEX = 0            # El índice que te funcionó antes

async def detector(websocket):
    print("¡Juego conectado al detector!")
    cap = cv2.VideoCapture(CAM_INDEX)
    
    # Usamos un sustractor de fondo para detectar movimiento
    fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 1. Pre-procesamiento
            frame = cv2.flip(frame, 1) # Espejar para que coincida con el arco
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 2. Aplicar sustracción de fondo
            fgmask = fgbg.apply(gray)
            
            # Limpiar ruido (puntos chiquitos que no son la pelota)
            kernel = np.ones((5,5), np.uint8)
            fgmask = cv2.erode(fgmask, kernel, iterations=1)
            fgmask = cv2.dilate(fgmask, kernel, iterations=2)

            # 3. Buscar contornos (donde hubo golpe)
            contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > UMBRAL_MOVIMIENTO:
                    # Obtenemos las coordenadas del golpe en píxeles
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])

                        # 4. NORMALIZACIÓN (Convertir píxeles a valores entre 0.0 y 1.0)
                        # Esto es lo que el juego.html necesita
                        relX = round(cX / frame.shape[1], 3)
                        relY = round(cY / frame.shape[0], 3)

                        data = {"x": relX, "y": relY}
                        
                        print(f"¡IMPACTO DETECTADO! Enviando: {data}")
                        await websocket.send(json.dumps(data))
                        
                        # Dibujamos un círculo en el monitor para ver dónde pegó
                        cv2.circle(frame, (cX, cY), 20, (0, 255, 0), -1)
                        
                        # Pequeña pausa para no mandar 1000 señales por un solo golpe
                        await asyncio.sleep(3) 

            # Mostrar el monitor de la cámara
            cv2.imshow('Monitor de Deteccion', frame)
            # cv2.imshow('Mascara de Movimiento', fgmask) # Descomentá para ver qué detecta el "ojo" de la PC

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            await asyncio.sleep(0.01)

    except websockets.exceptions.ConnectionClosed:
        print("Juego desconectado.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

async def main():
    print(f"Servidor activo en ws://localhost:8765")
    async with websockets.serve(detector, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSistema detenido.")