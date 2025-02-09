from app import create_app, db
from app.models import User, Anomaly, AlarmHistory
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password='admin', role='admin')
        db.session.add(admin_user)
        db.session.commit()

    if not Anomaly.query.first():
        anomaly1 = Anomaly(
            location="Entrance",
            camera_id="CAM001",
            ipaddress="192.168.1.10",
            anomaly_code="A001",
            anomaly_name="Suspicious Activity",
            timestamp=datetime.utcnow() - timedelta(days=60),
            duration=30.5,
            confidence=0.95,
            status="Reviewed",
            actions_taken="Alerted security",
            videopath="/videos/anomaly1.mp4"
        )
        anomaly2 = Anomaly(
            location="Lobby",
            camera_id="CAM002",
            ipaddress="192.168.1.11",
            anomaly_code="A002",
            anomaly_name="Loitering",
            timestamp=datetime.utcnow() - timedelta(days=45),
            duration=45.0,
            confidence=0.85,
            status="Pending",
            actions_taken="None",
            videopath=""
        )
        anomaly3 = Anomaly(
            location="Reading Hall",
            camera_id="CAM003",
            ipaddress="192.168.1.12",
            anomaly_code="A003",
            anomaly_name="Unattended Bag",
            timestamp=datetime.utcnow() - timedelta(days=30),
            duration=20.0,
            confidence=0.90,
            status="Reviewed",
            actions_taken="Security notified",
            videopath="/videos/anomaly3.mp4"
        )
        anomaly4 = Anomaly(
            location="Reading Hall",
            camera_id="CAM003",
            ipaddress="192.168.1.12",
            anomaly_code="A008",
            anomaly_name="Fight",
            timestamp=datetime.utcnow() - timedelta(days=90),
            duration=20.0,
            confidence=0.90,
            status="Notified Engineer",
            actions_taken="Security notified",
            videopath="/videos/anomaly7.mp4"
        )
        db.session.add(anomaly1)
        db.session.add(anomaly2)
        db.session.add(anomaly3)
        db.session.add(anomaly4)
        db.session.commit()

    if not AlarmHistory.query.first():
        alarm_history1 = AlarmHistory(
            alarm_id=1,
            room="Lobby",
            location="Main Lobby",
            activated_by="Aditya",
            start_time=datetime.utcnow() - timedelta(days=60, hours=2),
            end_time=datetime.utcnow() - timedelta(days=60, hours=1, minutes=30),
            duration=1800
        )
        alarm_history2 = AlarmHistory(
            alarm_id=2,
            room="Entrance",
            location="Main Entrance",
            activated_by="Chinmay",
            start_time=datetime.utcnow() - timedelta(days=55, hours=3),
            end_time=datetime.utcnow() - timedelta(days=55, hours=2, minutes=45),
            duration=900
        )
        alarm_history5 = AlarmHistory(
            alarm_id=5,
            room="Entrance",
            location="Main Entrance",
            activated_by="Aditya",
            start_time=datetime.utcnow() - timedelta(days=55, hours=3),
            end_time=datetime.utcnow() - timedelta(days=55, hours=2, minutes=45),
            duration=900
        )
        alarm_history3 = AlarmHistory(
            alarm_id=3,
            room="Reading Hall",
            location="Reading Hall",
            activated_by="Manshi",
            start_time=datetime.utcnow() - timedelta(days=40, hours=1),
            end_time=datetime.utcnow() - timedelta(days=40, minutes=30),
            duration=1800
        )
        alarm_history4 = AlarmHistory(
            alarm_id=4,
            room="Balcony",
            location="Second Floor Balcony",
            activated_by="Swaroop",
            start_time=datetime.utcnow() - timedelta(days=35, hours=4),
            end_time=datetime.utcnow() - timedelta(days=35, hours=3, minutes=15),
            duration=2700
        )
        db.session.add(alarm_history1)
        db.session.add(alarm_history2)
        db.session.add(alarm_history3)
        db.session.add(alarm_history4)
        db.session.add(alarm_history5)
        db.session.commit()
