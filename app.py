import cv2
import serial
import time

# --- CONFIGURACIÓN ---
PUERTO_SERIAL = 'COM3' 
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

try:
    arduino = serial.Serial(PUERTO_SERIAL, 9600, timeout=0.1)
    time.sleep(2)
    print("✓ Conectado al Arduino")
except:
    arduino = None

cap = cv2.VideoCapture(0)
# Resolución de referencia
WIDTH, HEIGHT = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

print("--- Ejecutando con Ejes Corregidos ---")

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. Efecto Espejo: Esto ayuda a que "izquierda" sea "izquierda" en pantalla
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(50, 50))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        cx = x + w // 2
        cy = y + h // 2
        
        if arduino:
           
            env_x = WIDTH - cx  
            env_y = HEIGHT - cy 

        
            env_x = int(env_x * (320 / WIDTH))
            env_y = int(env_y * (240 / HEIGHT))
            
            mensaje = f"S{env_x},{env_y}\n"
            arduino.write(mensaje.encode())

    cv2.imshow('Torreta - Ejes Corregidos', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if arduino: arduino.close()
