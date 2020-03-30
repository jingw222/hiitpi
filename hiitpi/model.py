import time
import datetime
from . import db


class WorkoutSession(db.Model):
    __tablename__ = "workout_session"

    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    user_name = db.Column(db.String(80), nullable=False)
    workout = db.Column(db.String(80), nullable=False)
    reps = db.Column(db.Integer(), nullable=False)
    pace = db.Column(db.Float(), nullable=False)

    def __repr__(self):
        return f"<User {self.user_name}>"
