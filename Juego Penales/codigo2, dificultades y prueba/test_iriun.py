import cv2

# Cambiá el número si no abre (0, 1, 2...)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara de Iriun. Verificá el índice.")
    exit()

print("Cámara conectada. Presioná 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Espejar la imagen para que sea más natural (opcional)
    frame = cv2.flip(frame, 1)

    cv2.imshow('Prueba Iriun - Penal Game', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()