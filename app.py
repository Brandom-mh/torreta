import cv2
import serial
import time

PUERTO_SERIAL = '/dev/ttyUSB0'
RUTA_XML = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'

ANCHO = 320
ALTO = 240

SUAVIZADO = 0.30
INTERVALO_ENVIO = 0.05

# Contraste
ALPHA = 1.5   # contraste: 1.0 normal, 1.5 más contraste
BETA = 25     # brillo: 0 normal, 20-40 más brillo

ultimo_envio = 0
servo_x_actual = 160
servo_y_actual = 120

try:
    arduino = serial.Serial(PUERTO_SERIAL, 9600, timeout=1)
    time.sleep(2)

    # Posición inicial
    arduino.write(b"S0,0\n")
    time.sleep(2)

    print(f"✓ Conectado al Arduino en {PUERTO_SERIAL}")

except Exception as e:
    print(f"! Error Serial: {e}")
    arduino = None

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)

face_cascade = cv2.CascadeClassifier(RUTA_XML)

if face_cascade.empty():
    print("! Error: No se pudo cargar el XML.")
    exit()

contador_frames = 0
prev_gray = None

print("--- Torreta Iniciada: tracking continuo con contraste ---")

try:
    while True:

        ret, frame = cap.read()

        if not ret:
            print("! Error al capturar video")
            break

        if contador_frames % 3 == 0:

            # ==============================
            # MEJORA DE CONTRASTE Y BRILLO
            # Fórmula: pixel_nuevo = ALPHA * pixel_original + BETA
            # ==============================
            frame = cv2.convertScaleAbs(frame, alpha=ALPHA, beta=BETA)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Ecualización de histograma para mejorar contraste
            gray = cv2.equalizeHist(gray)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(30, 30)
            )

            if len(faces) > 0:

                rostro_movil = None
                mayor_movimiento = 0

                if prev_gray is not None:

                    diff = cv2.absdiff(prev_gray, gray)

                    for (x, y, w, h) in faces:

                        zona_movimiento = diff[y:y+h, x:x+w]

                        _, zona_binaria = cv2.threshold(
                            zona_movimiento,
                            25,
                            255,
                            cv2.THRESH_BINARY
                        )

                        movimiento = cv2.countNonZero(zona_binaria)

                        if movimiento > mayor_movimiento:
                            mayor_movimiento = movimiento
                            rostro_movil = (x, y, w, h)

                if rostro_movil is not None and mayor_movimiento > 100:

                    x, y, w, h = rostro_movil

                    cx = x + w // 2
                    cy = y + h // 2

                    # Suavizado continuo
                    servo_x_actual = int(
                        servo_x_actual + (cx - servo_x_actual) * SUAVIZADO
                    )

                    servo_y_actual = int(
                        servo_y_actual + (cy - servo_y_actual) * SUAVIZADO
                    )

                    ahora = time.time()

                    if arduino and (ahora - ultimo_envio) >= INTERVALO_ENVIO:

                        try:
                            mensaje = f"S{servo_x_actual},{servo_y_actual}\n"
                            arduino.write(mensaje.encode())

                            ultimo_envio = ahora

                            print(
                                f"Enviado -> {mensaje.strip()} | "
                                f"Movimiento:{mayor_movimiento}"
                            )

                        except Exception as e:
                            print(f"! Error enviando datos: {e}")

            prev_gray = gray.copy()

        contador_frames += 1

except KeyboardInterrupt:
    print("\nDeteniendo sistema...")

finally:

    if arduino:
        try:
            print("Regresando servos a posición inicial...")
            arduino.write(b"S0,0\n")
            time.sleep(2)
        except Exception as e:
            print(f"! Error al regresar servos: {e}")

    cap.release()

    if arduino:
        arduino.close()

    print("✓ Recursos liberados")

