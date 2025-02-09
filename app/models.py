from app.extensions import db
from flask_login import UserMixin
import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Anomaly(db.Model):
    __tablename__ = 'anomalies'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=True)
    camera_id = db.Column(db.String(50), nullable=True)
    ipaddress = db.Column(db.String(45), nullable=True)
    anomaly_code = db.Column(db.String(50), nullable=True)
    anomaly_name = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    duration = db.Column(db.Float, nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), nullable=True)
    actions_taken = db.Column(db.Text, nullable=True)
    videopath = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return (f"Anomaly(id={self.id}, location='{self.location}', camera_id='{self.camera_id}', "
                f"ipaddress='{self.ipaddress}', anomaly_code='{self.anomaly_code}', "
                f"anomaly_name='{self.anomaly_name}', timestamp='{self.timestamp}', "
                f"duration={self.duration}, confidence={self.confidence}, status='{self.status}', "
                f"actions_taken='{self.actions_taken}', videopath='{self.videopath}')")

class AlarmHistory(db.Model):
    __tablename__ = 'alarm_history'

    id = db.Column(db.Integer, primary_key=True)
    alarm_id = db.Column(db.Integer, nullable=False)
    room = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    activated_by = db.Column(db.String(150), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return (f"AlarmHistory(alarm_id={self.alarm_id}, room='{self.room}', "
                f"activated_by='{self.activated_by}', start_time='{self.start_time}', "
                f"end_time='{self.end_time}', duration={self.duration})")
