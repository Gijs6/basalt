from flask_sqlalchemy import SQLAlchemy
import random
import string


def random_base36_id(length=8):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


db = SQLAlchemy()


class Entry(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=random_base36_id)

    title = db.Column(db.String(250), nullable=False)

    content = db.Column(db.Text, nullable=False)

    dt_made = db.Column(db.DateTime, nullable=False)
    dt_updated = db.Column(db.DateTime, nullable=False)
