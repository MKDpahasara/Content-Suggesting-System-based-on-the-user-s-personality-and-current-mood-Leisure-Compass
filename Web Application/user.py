from flask_login import UserMixin
from db import get_db

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic, personality_label=None):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.personality_label = personality_label

    @staticmethod
    def get(user_id):
        print("Fetching user from the database...")
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            print("User not found!")
            return None

        user = User(
            id_=user["id"], 
            name=user["name"], 
            email=user["email"], 
            profile_pic=user["profile_pic"],
            personality_label=user["personality_label"]
        )
        print("User fetched successfully:", user)
        return user

    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic) "
            "VALUES (?, ?, ?, ?)",
            (id_, name, email, profile_pic),
        )
        db.commit()

    @staticmethod
    def get_all():
        db = get_db()
        users = db.execute("SELECT * FROM user").fetchall()
        return [
            User(
                id_=user["id"], 
                name=user["name"], 
                email=user["email"], 
                profile_pic=user["profile_pic"],
                personality_label=user["personality_label"]
            ) for user in users
        ]
