from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()

    # Create an admin user if not already present (optional check)
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password='admin', role='admin')
        db.session.add(admin_user)
        db.session.commit()
