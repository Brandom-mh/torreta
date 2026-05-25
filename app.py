import cv2
import serial
import time

# --- CONFIGURACIÓN ---
PUERTO_SERIAL = '/dev/ttyUSB0'

RUTA_XML = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'

# =========================
# INICIALIZACIÓN SERIAL
# =========================
try:
    arduino = serial.Serial(PUERTO_SERIAL, 9600, timeout=1)

    # Esperar reinicio del Arduino
    time.sleep(2)

    # =========================
    # CALIBRACIÓN INICIAL
    # =========================
    # Mandar servos a posición inicial (0,0)
    arduino.write(b"S0,0\n")

    # Esperar movimiento
    time.sleep(2)

    print(f"✓ Conectado al Arduino en {PUERTO_SERIAL}")

except Exception as e:
    print(f"! Error Serial: {e}")
    arduino = None

# =========================
# CONFIGURACIÓN DE CÁMARA
# =========================
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# =========================
# CARGA DEL CLASIFICADOR
# =========================
face_cascade = cv2.CascadeClassifier(RUTA_XML)

if face_cascade.empty():
    print("! Error: No se pudo cargar el XML.")
    exit()

contador_frames = 0

print("--- Torreta Iniciada ---")

# =========================
# LOOP PRINCIPAL
# =========================
try:
    while True:

        ret, frame = cap.read()

        if not ret:
            print("! Error al capturar video")
            break

        # Procesar 1 de cada 3 frames
        if contador_frames % 3 == 0:

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(40, 40)
            )

            # Si detecta rostro
            if len(faces) > 0:

                (x, y, w, h) = faces[0]

                # Centro del rostro
                cx = x + w // 2
                cy = y + h // 2

                print(f"Rostro detectado -> X:{cx} Y:{cy}")

                # Enviar coordenadas al Arduino
                if arduino:

                    try:
                        mensaje = f"S{cx},{cy}\n"

                        arduino.write(mensaje.encode())

                        print(f"Enviado -> {mensaje.strip()}")

                    except Exception as e:
                        print(f"! Error enviando datos: {e}")

        contador_frames += 1

except KeyboardInterrupt:
    print("\nDeteniendo sistema...")

finally:

    # =========================
    # REGRESAR A POSICIÓN INICIAL
    # =========================
    if arduino:
        try:
            print("Regresando servos a posición inicial...")

            arduino.write(b"S0,0\n")

            # Esperar a que los servos se muevan
            time.sleep(2)

        except Exception as e:
            print(f"! Error al regresar servos: {e}")

    cap.release()

    if arduino:
        arduino.close()

    print("✓ Recursos liberados")
