#include <Servo.h>

Servo servoX;
Servo servoY;

// Guardamos la última posición para evitar movimientos bruscos
int lastX = 90;
int lastY = 90;

void setup() {
  Serial.begin(9600);
  servoX.attach(9); 
  servoY.attach(10);
  
  // Posición inicial centrada
  servoX.write(lastX);
  servoY.write(lastY);
}

void loop() {
  if (Serial.available() > 0) {
    // Buscamos el caracter de inicio 'S' para ignorar basura serial
    if (Serial.read() == 'S') {
      String data = Serial.readStringUntil('\n');
      
      int commaIndex = data.indexOf(',');
      if (commaIndex != -1) {
        int xVal = data.substring(0, commaIndex).toInt();
        int yVal = data.substring(commaIndex + 1).toInt();
        
        // Validación: Solo mover si los valores están en el rango de la cámara (320x240)
        // Y si no son 0 (que suele ser error de lectura)
        if (xVal > 0 && yVal > 0 && xVal <= 320 && yVal <= 240) {
          
          int angleX = map(xVal, 0, 320, 180, 0); 
          int angleY = map(yVal, 0, 240, 0, 180);
          
          servoX.write(angleX);
          servoY.write(angleY);
          
          lastX = angleX;
          lastY = angleY;
        }
      }
    }
  }
}
