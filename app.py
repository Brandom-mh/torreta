import cv2          # Librería OpenCV para captura y procesamiento de imágenes
import serial       # Librería para comunicación serial con Arduino
import time         # Librería para manejar tiempos y retardos

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================

# Puerto serial donde se encuentra conectado el Arduino
PUERTO_SERIAL = '/dev/ttyUSB0'

# Ruta del clasificador Haar Cascade para detección de rostros
RUTA_XML = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'

# Resolución de captura de video
ANCHO = 320
ALTO = 240

# Factor de suavizado para evitar movimientos bruscos en los servomotores
SUAVIZADO = 0.30

# Intervalo mínimo de tiempo entre envíos de datos al Arduino
INTERVALO_ENVIO = 0.05

# Parámetros para mejorar la imagen
ALPHA = 1.5   # Controla el contraste de la imagen
BETA = 25     # Controla el brillo de la imagen

# Variables iniciales para controlar el tiempo de envío y posición de los servos
ultimo_envio = 0
servo_x_actual = 160
servo_y_actual = 120

# ==============================
# CONEXIÓN SERIAL CON ARDUINO
# ==============================

try:
    # Se establece comunicación serial con el Arduino a 9600 baudios
    arduino = serial.Serial(PUERTO_SERIAL, 9600, timeout=1)

    # Se espera a que el Arduino inicialice correctamente
    time.sleep(2)

    # Se manda la torreta a su posición inicial
    arduino.write(b"S0,0\n")
    time.sleep(2)

    print(f"Conectado al Arduino en {PUERTO_SERIAL}")

except Exception as e:
    # Si ocurre un error de conexión, se muestra el mensaje
    print(f"Error Serial: {e}")
    arduino = None

# ==============================
# CONFIGURACIÓN DE LA CÁMARA
# ==============================

# Se inicializa la cámara conectada a la Raspberry Pi
cap = cv2.VideoCapture(0)

# Se define la resolución de captura
cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)

# Se carga el clasificador Haar Cascade para detectar rostros
face_cascade = cv2.CascadeClassifier(RUTA_XML)

# Se verifica que el archivo XML haya sido cargado correctamente
if face_cascade.empty():
    print("Error: No se pudo cargar el XML.")
    exit()

# Contador de frames para no procesar todos los cuadros y reducir carga
contador_frames = 0

# Variable que almacena el frame anterior en escala de grises
prev_gray = None

print("--- Torreta Iniciada---")

# ==============================
# CICLO PRINCIPAL DEL SISTEMA
# ==============================

try:
    while True:

        # Se captura un frame de la cámara
        ret, frame = cap.read()

        # Si no se pudo capturar el frame, se detiene el ciclo
        if not ret:
            print("Error al capturar video")
            break

        # Se procesa un frame cada 3 capturas para mejorar el rendimiento
        if contador_frames % 3 == 0:

            # ==============================
            # Fórmula: pixel_nuevo = ALPHA * pixel_original + BETA
            # ==============================

            # Se ajusta el brillo y contraste del frame
            frame = cv2.convertScaleAbs(frame, alpha=ALPHA, beta=BETA)

            # Se convierte la imagen a escala de grises para facilitar el análisis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Se aplica ecualización de histograma para mejorar el contraste
            gray = cv2.equalizeHist(gray)

            # ==============================
            # DETECCIÓN DE ROSTROS
            # ==============================

            # Se detectan rostros dentro del frame procesado
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,    # Escala de búsqueda del rostro
                minNeighbors=4,     # Filtros para reducir falsos positivos
                minSize=(30, 30)    # Tamaño mínimo del rostro a detectar
            )

            # Si se detectó al menos un rostro
            if len(faces) > 0:

                # Variable para almacenar el rostro con mayor movimiento
                rostro_movil = None

                # Variable para almacenar la cantidad de movimiento detectado
                mayor_movimiento = 0

                # Se compara el frame actual con el anterior
                if prev_gray is not None:

                    # Se calcula la diferencia entre el frame anterior y el actual
                    diff = cv2.absdiff(prev_gray, gray)

                    # Se analiza cada rostro detectado
                    for (x, y, w, h) in faces:

                        # Se recorta la zona del rostro para analizar solo esa región
                        zona_movimiento = diff[y:y+h, x:x+w]

                        # Se convierte la diferencia a una imagen binaria
                        _, zona_binaria = cv2.threshold(
                            zona_movimiento,
                            25,
                            255,
                            cv2.THRESH_BINARY
                        )

                        # Se cuenta la cantidad de píxeles que cambiaron
                        movimiento = cv2.countNonZero(zona_binaria)

                        # Se selecciona el rostro con mayor movimiento
                        if movimiento > mayor_movimiento:
                            mayor_movimiento = movimiento
                            rostro_movil = (x, y, w, h)

                # Solo se continúa si se detectó un rostro con movimiento suficiente
                if rostro_movil is not None and mayor_movimiento > 100:

                    # Se obtienen las coordenadas del rostro seleccionado
                    x, y, w, h = rostro_movil

                    # Se calcula el centro del rostro
                    cx = x + w // 2
                    cy = y + h // 2

                    # ==============================
                    # SUAVIZADO DE MOVIMIENTO
                    # ==============================

                    # Se actualiza gradualmente la posición horizontal del servo
                    servo_x_actual = int(
                        servo_x_actual + (cx - servo_x_actual) * SUAVIZADO
                    )

                    # Se actualiza gradualmente la posición vertical del servo
                    servo_y_actual = int(
                        servo_y_actual + (cy - servo_y_actual) * SUAVIZADO
                    )

                    # Se obtiene el tiempo actual
                    ahora = time.time()

                    # Se verifica que exista conexión con Arduino y que ya haya pasado
                    # el intervalo mínimo para enviar nuevas coordenadas
                    if arduino and (ahora - ultimo_envio) >= INTERVALO_ENVIO:

                        try:
                            # Se genera el mensaje con el formato esperado por Arduino
                            mensaje = f"S{servo_x_actual},{servo_y_actual}\n"

                            # Se envía el mensaje por comunicación serial
                            arduino.write(mensaje.encode())

                            # Se actualiza el tiempo del último envío
                            ultimo_envio = ahora

                            # Se imprime el mensaje enviado y el movimiento detectado
                            print(
                                f"Enviado -> {mensaje.strip()} | "
                                f"Movimiento:{mayor_movimiento}"
                            )

                        except Exception as e:
                            print(f"Error enviando datos: {e}")

            # Se guarda el frame actual como referencia para la siguiente comparación
            prev_gray = gray.copy()

        # Se incrementa el contador de frames
        contador_frames += 1

# Si el usuario detiene el programa con Ctrl + C
except KeyboardInterrupt:
    print("\nDeteniendo sistema...")

# ==============================
# LIBERACIÓN DE RECURSOS
# ==============================

finally:

    # Si existe conexión con Arduino, se regresan los servos a la posición inicial
    if arduino:
        try:
            print("Regresando servos a posición inicial...")
            arduino.write(b"S0,0\n")
            time.sleep(2)
        except Exception as e:
            print(f"! Error al regresar servos: {e}")

    # Se libera la cámara
    cap.release()

    # Se cierra la comunicación serial
    if arduino:
        arduino.close()

    print("Recursos liberados")
