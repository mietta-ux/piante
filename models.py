from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(100))
    image_url = db.Column(db.String(200), default='default_plant.jpg')
    watering_frequency = db.Column(db.Integer, default=1)  # in days
    last_watered = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tips = db.Column(db.Text, nullable=True)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=True)
    children = db.relationship('Plant', backref=db.backref('parent', remote_side=[id]))
    
    notes = db.relationship('DiaryNote', backref='plant', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Plant {self.name}>'

class DiaryNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)

    def __repr__(self):
        return f'<DiaryNote {self.date_added}>'
