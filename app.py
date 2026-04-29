import cv2
import serial
import time

# 1. Configuración de la comunicación Serial
# El puerto suele ser /dev/ttyACM0 o /dev/ttyUSB0 en Raspberry
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2) # Espera a que el Arduino se reinicie
except:
    print("No se encontró el Arduino en /dev/ttyACM0, intentando otro...")
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# 2. Configuración de Cámara (Resolución reducida para Pi 3B)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # [cite: 147]
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) # [cite: 147]

ruta_xml = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(ruta_xml)

contador_frames = 0

while True:
    ret, frame = cap.read()
    if not ret: break

    # Procesar solo cada 3 frames para agilidad [cite: 150, 161]
    if contador_frames % 3 == 0:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # scaleFactor alto para detección rápida [cite: 148, 160]
        faces = face_cascade.detectMultiScale(gray, 1.5, 5, minSize=(30, 30))

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            cx = x + w // 2
            cy = y + h // 2
            
            # Enviar coordenadas al Arduino en formato "X,Y\n"
            cadena_datos = f"{cx},{cy}\n"
            arduino.write(cadena_datos.encode()) # [cite: 26, 105]
            print(f"Enviado a Arduino: {cadena_datos.strip()}") # [cite: 104]

    contador_frames += 1
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
arduino.close()