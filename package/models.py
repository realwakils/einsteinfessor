from datetime import datetime
from package import db

class User(db.Model):
    ip = db.Column(db.String(), nullable=False, primary_key=True)
    first_visit = db.Column(db.DateTime, nullable=False, default=datetime.now)
    latest_visit = db.Column(db.DateTime, nullable=False, default=datetime.now)
    latest_url_visited = db.Column(db.String, nullable=False, default="/")
    Calculations = db.relationship('Calculation', backref='performer', lazy=True)

    def __repr__(self):
        return f"User('{self.ip}', '{self.first_visit}', '{self.latest_visit}', '{self.latest_url_visited}')"

class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    results = db.Column(db.String(), nullable=False)
    ip = db.Column(db.String(), db.ForeignKey('user.ip'), nullable=False)
    raw = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"Calculation('{self.id}', '{self.ip}', '{self.results}, '{self.time}', '{self.raw}')"

class BuffRates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rates = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"BuffRates('{self.id}', '{self.rates}')"