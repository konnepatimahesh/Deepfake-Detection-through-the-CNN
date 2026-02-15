from models.user import db, User
from app import create_app

app = create_app()

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"Username: {user.username}, Role: {user.role}")