import os
import tensorflow as tf
import cv2
import numpy as np
from flask import Flask, render_template, Response, redirect
import time

model_path = '/Users/monicagullapalli/Downloads/Neural-networks-assignments/Neural-Networks-project/final_model.h5'
model = tf.keras.models.load_model(model_path)

app = Flask(__name__)
predicted_emotion = None  # Global variable to store the predicted emotion

@app.route('/')
def index():
    return render_template('index.html')

def detect_emotion(frame):
    # Preprocess the frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (64, 64))
    frame = frame / 255.0
    frame = np.expand_dims(frame, axis=0)

    # Make the prediction
    predictions = model.predict(frame)
    emotion_index = tf.argmax(predictions, axis=1).numpy()[0]
    emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
    predicted_emotion = emotions[emotion_index]
    return predicted_emotion

def generate_frames():
    global predicted_emotion  # Access the global variable
    camera = cv2.VideoCapture(0)
    countdown = 10  # Countdown in seconds

    while countdown > 0:
        ret, frame = camera.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, f"Emotion will be captured in {countdown}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(1)
        countdown -= 1

    success, frame = camera.read()
    if success:
        frame = cv2.flip(frame, 1)
        predicted_emotion = detect_emotion(frame)
        cv2.putText(frame, predicted_emotion, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/redirect_playlist/<emotion>')
def redirect_playlist(emotion):
    global predicted_emotion  # Access the global variable

    # Define the Spotify playlist URLs for different emotions
    playlist_urls = {
        'Angry': 'https://open.spotify.com/playlist/6uyLtbq9zvZqHCyDbGpuzD',
        'Happy': 'https://open.spotify.com/playlist/049OGKQgNXgRRJh91zNwi7',
        'Sad': 'https://open.spotify.com/playlist/723NngXppAcYXXlYokFGVH',
        'Neutral': 'https://open.spotify.com/playlist/4vMpOTgv5vekgBoSJ5Fwdo',
        'Surprise': 'https://example.com/surprise',
        'Fear': 'https://example.com/fear',
        'Disgust': 'https://example.com/disgust'
    }

    if emotion in playlist_urls:
        return redirect(playlist_urls[emotion])
    else:
        # Handle the case when the emotion is not found in the playlist URLs
        # For example, render an error page or redirect to a default playlist.
        return redirect('https://example.com/default')

if __name__ == '__main__':
    app.run(debug=True)