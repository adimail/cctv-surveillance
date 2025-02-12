from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.extensions import db
from datetime import datetime
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
    record_type = request.args.get('record_type', 'anomaly')  # Default to 'anomaly'

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        if record_type == 'alarm':
            room = data.get('room')
            location = data.get('location')
            activated_by = data.get('activated_by')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            duration = data.get('duration')

            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') if start_time else None
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') if end_time else None

            new_record = AlarmHistory(
                room=room,
                location=location,
                activated_by=activated_by,
                start_time=start_time,
                end_time=end_time,
                duration=duration
            )
            flash("Alarm history added successfully!", category="success")
        else:
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

            new_record = Anomaly(
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
            flash("Anomaly added successfully!", category="success")

        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('history.home', record_type=record_type))

    return render_template("add_record.html", record_type=record_type)


@history_bp.route('/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit(record_id):
    if current_user.role != 'admin':
        abort(403)

    record_type = request.args.get('record_type', 'anomaly')  # Default to 'anomaly'

    if record_type == 'alarm':
        record = AlarmHistory.query.get_or_404(record_id)
    else:
        record = Anomaly.query.get_or_404(record_id)

    if request.method == 'POST':
        if record_type == 'alarm':
            record.room = request.form.get('room')
            record.location = request.form.get('location')
            record.activated_by = request.form.get('activated_by')
            record.start_time = request.form.get('start_time')
            record.end_time = request.form.get('end_time')
            record.duration = request.form.get('duration')
            flash("Alarm history updated successfully!", category="success")
        else:
            record.location = request.form.get('location')
            record.camera_id = request.form.get('camera_id')
            record.ipaddress = request.form.get('ipaddress')
            record.anomaly_code = request.form.get('anomaly_code')
            record.anomaly_name = request.form.get('anomaly_name')
            duration = request.form.get('duration')
            confidence = request.form.get('confidence')
            record.status = request.form.get('status')
            record.actions_taken = request.form.get('actions_taken')
            record.videopath = request.form.get('videopath')
            try:
                record.duration = float(duration) if duration else None
            except ValueError:
                record.duration = None
            try:
                record.confidence = float(confidence) if confidence else None
            except ValueError:
                record.confidence = None
            flash("Anomaly updated successfully!", category="success")

        db.session.commit()
        return redirect(url_for('history.home', record_type=record_type))

    return render_template("edit_record.html", record=record, record_type=record_type)