from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import time
from app.model import model

api = Blueprint("api", __name__)

def preprocess_frame(frame):
    frame = cv2.resize(frame, (224, 224))
    frame = frame / 255.0
    frame = np.expand_dims(frame, axis=0)
    return frame

@api.route("/predict", methods=['POST'])
def predict():
    if 'video_frame' not in request.files:
        return jsonify({'error': 'No video frame provided'}), 400

    file = request.files['video_frame']
    np_img = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    processed_frame = preprocess_frame(frame)
    predictions = model.predict(processed_frame)
    anomaly_score = float(predictions[0][0])

    return jsonify({'anomaly_score': anomaly_score})

@api.route('/stream', methods=['POST'])
def process_stream():
    video_file = request.files['video']
    cap = cv2.VideoCapture(video_file.read())

    results = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = preprocess_frame(frame)
        predictions = model.predict(processed_frame)
        results.append(float(predictions[0][0]))

        time.sleep(0.1)

    cap.release()
    return jsonify({'scores': results})
