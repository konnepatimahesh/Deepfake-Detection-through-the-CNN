from models.user import db, User
from app import create_app

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='mahi').first()
    if user:
        user.role = 'admin'
        db.session.commit()
        print(f"✅ {user.username} is now an admin!")
    else:
        print("❌ User not found")