from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Anomaly, AlarmHistory

history_bp = Blueprint('history', __name__)

@history_bp.route('/')
@login_required
def home():
    anomalies_query = Anomaly.query.order_by(Anomaly.timestamp.desc()).all()
    alarm_history_query = AlarmHistory.query.order_by(AlarmHistory.start_time.desc()).all()

    anomalies = [{
        "id": anomaly.id,
        "location": anomaly.location or "",
        "camera_id": anomaly.camera_id or "",
        "ipaddress": anomaly.ipaddress or "",
        "anomaly_code": anomaly.anomaly_code or "",
        "anomaly_name": anomaly.anomaly_name or "",
        "timestamp": anomaly.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": anomaly.duration or "",
        "confidence": anomaly.confidence or "",
        "status": anomaly.status or "",
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
        "duration": record.duration or ""
    } for record in alarm_history_query]

    return render_template("history.html", anomalies=anomalies, alarm_history=alarm_history)

@history_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        location = data.get('location')
        camera_id = data.get('camera_id')
        ipaddress = data.get('ipaddress')
        anomaly_code = data.get('anomaly_code')
        anomaly_name = data.get('anomaly_name')
        duration = data.get('duration')
        confidence = data.get('confidence')
        status = data.get('status')
        actions_taken = data.get('actions_taken')
        videopath = data.get('videopath')

        new_anomaly = Anomaly(
            location=location,
            camera_id=camera_id,
            ipaddress=ipaddress,
            anomaly_code=anomaly_code,
            anomaly_name=anomaly_name,
            duration=duration,
            confidence=confidence,
            status=status,
            actions_taken=actions_taken,
            videopath=videopath
        )
        db.session.add(new_anomaly)
        db.session.commit()
        flash("Anomaly added successfully!", category="success")

    return render_template("add_anomaly.html")

@history_bp.route('/edit/<int:anomaly_id>', methods=['GET', 'POST'])
@login_required
def edit(anomaly_id):
    if current_user.role != 'admin':
        abort(403)
    anomaly = Anomaly.query.get_or_404(anomaly_id)
    if request.method == 'POST':
        anomaly.location = request.form.get('location')
        anomaly.camera_id = request.form.get('camera_id')
        anomaly.ipaddress = request.form.get('ipaddress')
        anomaly.anomaly_code = request.form.get('anomaly_code')
        anomaly.anomaly_name = request.form.get('anomaly_name')
        duration = request.form.get('duration')
        confidence = request.form.get('confidence')
        anomaly.status = request.form.get('status')
        anomaly.actions_taken = request.form.get('actions_taken')
        anomaly.videopath = request.form.get('videopath')
        try:
            anomaly.duration = float(duration) if duration else None
        except ValueError:
            anomaly.duration = None
        try:
            anomaly.confidence = float(confidence) if confidence else None
        except ValueError:
            anomaly.confidence = None

        db.session.commit()
        flash("Anomaly updated successfully!", category="success")
        return redirect(url_for('history.home'))

    return render_template("edit_anomaly.html", anomaly=anomaly)
