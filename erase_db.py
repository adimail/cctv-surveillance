import random
import sys
from app import create_app, db
from app.models import Anomaly, AlarmHistory

app = create_app()

def confirm_deletion():
    code = ''.join(random.choices('0123456789', k=6))
    print("WARNING: This action will permanently delete all anomaly and alarm history data!")
    print(f"To confirm deletion, please type the following code: {code}")
    user_input = input("Enter the confirmation code: ").strip()
    if user_input == code:
        return True
    else:
        print("Confirmation failed. Data deletion aborted.")
        return False

with app.app_context():
    if confirm_deletion():
        num_anomalies_deleted = db.session.query(Anomaly).delete()
        num_alarm_history_deleted = db.session.query(AlarmHistory).delete()
        db.session.commit()
        print(f"Deleted {num_anomalies_deleted} anomaly records and {num_alarm_history_deleted} alarm history records.")
    else:
        sys.exit(1)
