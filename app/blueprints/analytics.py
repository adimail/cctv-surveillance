from flask import Blueprint, render_template, jsonify
from app.models import Anomaly, AlarmHistory

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
def analytics_home():
    return render_template('analytics.html')

@analytics_bp.route('/get-analytics-data')
def get_analytics_data():
    anomalies_query = Anomaly.query.all()
    alarm_history_query = AlarmHistory.query.all()

    anomalies = [{
         "id": anomaly.id,
         "location": anomaly.location or "",
         "camera_id": anomaly.camera_id or "",
         "ipaddress": anomaly.ipaddress or "",
         "anomaly_code": anomaly.anomaly_code or "",
         "anomaly_name": anomaly.anomaly_name or "",
         "timestamp": anomaly.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
         "duration": anomaly.duration if anomaly.duration is not None else 0,
         "confidence": anomaly.confidence if anomaly.confidence is not None else 0,
         "status": anomaly.status or "Unknown",
         "actions_taken": anomaly.actions_taken or "",
         "videopath": anomaly.videopath or ""
    } for anomaly in anomalies_query]

    alarm_history = [{
         "id": record.id,
         "alarm_id": record.alarm_id,
         "room": record.room,
         "location": record.location or "",
         "activated_by": record.activated_by,
         "start_time": record.start_time.strftime("%Y-%m-%d %H:%M:%S"),
         "end_time": record.end_time.strftime("%Y-%m-%d %H:%M:%S") if record.end_time else "",
         "duration": record.duration if record.duration is not None else 0
    } for record in alarm_history_query]

    return jsonify({
         "anomalies": anomalies,
         "alarm_history": alarm_history
    })
