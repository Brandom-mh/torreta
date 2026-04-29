#include <Servo.h>

Servo servoX;
Servo servoY;

void setup() {
  Serial.begin(9600);
  servoX.attach(9); // Pin del servo horizontal
  servoY.attach(10); // Pin del servo vertical
}

void loop() {
  if (Serial.available() > 0) {
    // Lee la cadena hasta el salto de línea
    String data = Serial.readStringUntil('\n');
    
    // Divide la cadena en X y Y
    int逗号Index = data.indexOf(',');
    if (逗号Index != -1) {
      int xVal = data.substring(0, 逗号Index).toInt();
      int yVal = data.substring(逗号Index + 1).toInt();
      
      // Aquí mapeas la resolución 320x240 a los grados del servo (0-180)
      int angleX = map(xVal, 0, 320, 180, 0); 
      int angleY = map(yVal, 0, 240, 0, 180);
      
      servoX.write(angleX);
      servoY.write(angleY);
    }
  }
}