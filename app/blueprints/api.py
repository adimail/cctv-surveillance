from flask import Blueprint, request, jsonify, Response
import cv2
import numpy as np
import time
from app.model import model

api = Blueprint("api", __name__)

def preprocess_frame(frame):
    frame = cv2.resize(frame, (299, 299))
    frame = frame / 255.0
    frames = np.repeat(np.expand_dims(frame, axis=0), 10, axis=0)
    frames = np.expand_dims(frames, axis=0)
    return frames


@api.route("/predict", methods=['POST'])
def predict():
    if model is None:
        return jsonify({
            'error': 'Model not available. Please check if the model file exists.'
        }), 503

    if 'video_frame' not in request.files:
        return jsonify({'error': 'No video frame provided'}), 400

    file = request.files['video_frame']
    np_img = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    processed_frame = preprocess_frame(frame)
    predictions = model.predict(processed_frame)
    anomaly_score = float(predictions[0][0])

    return jsonify({'anomaly_score': anomaly_score})

## ==========================================
##
##
## Experimental feature to predict anomolies
## from the live video stream.
##
## ==========================================




# @api.route('/stream', methods=['POST', 'GET'])
# def process_stream():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
#
# camera = cv2.VideoCapture(0)
# def generate_frames():
#     last_prediction_time = time.time()
#     anomaly_score = 0.0
#
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#
#         current_time = time.time()
#         if current_time - last_prediction_time >= 10:
#             processed_frame = preprocess_frame(frame)
#             predictions = model.predict(processed_frame)
#             anomaly_score = float(predictions[0][0])
#             last_prediction_time = current_time
#
#         # Overlay anomaly score on the frame
#         height, width, _ = frame.shape
#         text = f"Anomaly Score: {anomaly_score:.2f}"
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         font_scale = 1
#         font_thickness = 2
#         text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
#         text_x = (width - text_size[0]) // 2
#         text_y = (height + text_size[1]) // 2
#
#         cv2.putText(frame, text, (text_x, text_y), font, font_scale, (0, 0, 255), font_thickness, cv2.LINE_AA)
#
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
