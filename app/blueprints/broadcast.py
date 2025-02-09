from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models import AlarmHistory

broadcast_bp = Blueprint('broadcast', __name__)

# Sample alarm list (for demo purposes)
alarms = [
    {"id": 1, "room": "Lobby", "location": "Main Lobby", "active": False},
    {"id": 2, "room": "Entrance", "location": "Main Entrance", "active": False},
    {"id": 3, "room": "Reading Hall", "location": "Reading Hall", "active": False},
    {"id": 4, "room": "Balcony", "location": "Second Floor Balcony", "active": False},
    {"id": 5, "room": "Conference Room", "location": "Third Floor Conference Room", "active": False},
    {"id": 6, "room": "Cafeteria", "location": "Ground Floor Cafeteria", "active": False},
    {"id": 7, "room": "Restroom", "location": "First Floor Restroom", "active": False},
    {"id": 8, "room": "Parking Lot", "location": "Underground Parking", "active": False},
    {"id": 9, "room": "Elevator", "location": "Central Elevator", "active": False},
    {"id": 10, "room": "Staircase", "location": "North Staircase", "active": False}
]

@broadcast_bp.route('/')
@login_required
def home():
    if current_user.role != 'admin':
        abort(403)
    return render_template("broadcast.html", alarms=alarms)

@broadcast_bp.route('/toggle/<int:alarm_id>')
@login_required
def toggle(alarm_id):
    if current_user.role != 'admin':
        abort(403)
    for alarm in alarms:
        if alarm["id"] == alarm_id:
            new_state = not alarm["active"]
            alarm["active"] = new_state
            if new_state:
                new_record = AlarmHistory(
                    alarm_id=alarm["id"],
                    room=alarm["room"],
                    location=alarm["location"],
                    activated_by=current_user.username,
                    start_time=datetime.utcnow()
                )
                db.session.add(new_record)
            else:
                record = AlarmHistory.query.filter_by(alarm_id=alarm["id"], end_time=None)\
                                             .order_by(AlarmHistory.start_time.desc()).first()
                if record:
                    record.end_time = datetime.utcnow()
                    record.duration = (record.end_time - record.start_time).total_seconds()
            db.session.commit()
            flash(f"Alarm in {alarm['room']} toggled to {'active' if new_state else 'inactive'}.", category='info')
            break
    else:
        flash("Alarm not found.", category='error')
    return redirect(url_for('broadcast.home'))

@broadcast_bp.route('/voice', methods=['POST'])
@login_required
def broadcast_voice():
    if current_user.role != 'admin':
        abort(403)
    audio_data = request.data
    flash("Voice message received and broadcasted.", category="info")
    return "OK", 200
