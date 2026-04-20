from flask import Flask, render_template, Response
import cv2
import time

app = Flask(__name__)

# Configuración inicial (tu lógica original) 
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def gen_frames():
    frame_anterior = None
    faces = []
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # --- Tu lógica de detección actual ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if frame_anterior is None:
            frame_anterior = gray_blur
            continue

        delta = cv2.absdiff(frame_anterior, gray_blur)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        movimiento = any(cv2.contourArea(c) > 100 for c in contornos)
        frame_anterior = gray_blur

        if movimiento:
            faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))

        if len(faces) > 0:
            x, y, w, h = faces[0]
            cx, cy = x + w // 2, y + h // 2
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            # Aquí puedes seguir usando tu print o enviar a Serial 
        
        # --- Codificación para Streaming Web --- [cite: 23]
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)