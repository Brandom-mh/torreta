#include <Servo.h>   // Librería para controlar servomotores

// ==============================
// DECLARACIÓN DE SERVOMOTORES
// ==============================

// Servo encargado del movimiento horizontal
Servo servoX;

// Servo encargado del movimiento vertical
Servo servoY;

// ==============================
// VARIABLES GLOBALES
// ==============================

// Variables que almacenan la última posición de los servos
// Esto ayuda a evitar movimientos bruscos al iniciar
int lastX = 90;
int lastY = 90;

// ==============================
// FUNCIÓN SETUP
// ==============================

void setup() {

  // Inicializa la comunicación serial a 9600 baudios
  // para recibir datos desde la Raspberry Pi
  Serial.begin(9600);

  // Se asignan los pines PWM donde están conectados los servos
  servoX.attach(9);
  servoY.attach(10);

  // ==============================
  // POSICIÓN INICIAL
  // ==============================

  // Se posicionan ambos servos al centro
  servoX.write(lastX);
  servoY.write(lastY);
}

// ==============================
// FUNCIÓN PRINCIPAL
// ==============================

void loop() {

  // Verifica si existen datos disponibles en el puerto serial
  if (Serial.available() > 0) {

    // ==============================
    // VALIDACIÓN DE INICIO DE TRAMA
    // ==============================

    // Se busca el carácter 'S' para asegurarse
    // de que el mensaje recibido es válido
    if (Serial.read() == 'S') {

      // Se lee el resto del mensaje hasta encontrar salto de línea
      String data = Serial.readStringUntil('\n');

      // ==============================
      // SEPARACIÓN DE COORDENADAS
      // ==============================

      // Busca la posición de la coma que separa X,Y
      int commaIndex = data.indexOf(',');

      // Si la coma existe, el formato es correcto
      if (commaIndex != -1) {

        // Obtiene el valor X antes de la coma
        int xVal = data.substring(0, commaIndex).toInt();

        // Obtiene el valor Y después de la coma
        int yVal = data.substring(commaIndex + 1).toInt();

        // ==============================
        // VALIDACIÓN DE DATOS
        // ==============================

        // Se verifica que:
        // - Los valores no sean negativos
        // - No sean cero
        // - Estén dentro del rango de resolución de la cámara
        // Resolución utilizada: 320x240
        if (xVal > 0 && yVal > 0 && xVal <= 320 && yVal <= 240) {

          // ==============================
          // CONVERSIÓN DE COORDENADAS
          // ==============================

          // Convierte coordenadas de la cámara
          // a ángulos para el servo horizontal
          int angleX = map(xVal, 0, 320, 180, 0);

          // Convierte coordenadas de la cámara
          // a ángulos para el servo vertical
          int angleY = map(yVal, 0, 240, 0, 180);

          // ==============================
          // MOVIMIENTO DE SERVOS
          // ==============================

          // Mueve el servo horizontal
          servoX.write(angleX);

          // Mueve el servo vertical
          servoY.write(angleY);

          // ==============================
          // ACTUALIZACIÓN DE POSICIÓN
          // ==============================

          // Guarda la última posición enviada
          lastX = angleX;
          lastY = angleY;
        }
      }
    }
  }
}
