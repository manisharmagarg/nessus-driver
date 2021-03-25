from driverapp import db
import uuid
import datetime
from sqlalchemy import Column, Integer, Text
from sqlalchemy import ForeignKey
# from sqlalchemy.dialects.postgresql import JSON, JSONB


def generate_uuid():
    return str(uuid.uuid4())


class Events(db.Model):
    id = db.Column(Integer, primary_key=True)
    redtree_event_id = db.Column(Integer, nullable=True)
    event_status = db.Column(db.String(80), nullable=True)
    created = db.Column(db.DateTime, nullable=False,
                        default=datetime.datetime.utcnow)

    def __str__(self):
        return self.id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'redtree_event_id': self.redtree_event_id,
            'event_status': self.event_status
        }


class Scan(db.Model):
    id = db.Column(db.String(100), primary_key=True, default=generate_uuid)
    targets = db.Column(db.Text(), nullable=True)
    scan_name = db.Column(db.String(80), nullable=True)
    scan_type = db.Column(db.String(80), nullable=True)
    nessus_url = db.Column(db.String(80), nullable=True)
    nessus_username = db.Column(db.String(80), nullable=True)
    nessus_password = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(80), nullable=True)
    scan_message = db.Column(db.String(100), nullable=True)
    result = db.Column(db.String(200), nullable=True, default="False")
    event_id = db.Column(Integer, ForeignKey('events.id'))
    process_started = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, nullable=False,
                        default=datetime.datetime.utcnow)

    def __str__(self):
        return self.id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'targets': self.targets,
            'scan_name': self.scan_name,
            'scan_type': self.scan_type,
            'nessus_url': self.nessus_url,
            'nessus_username': self.nessus_username,
            'nessus_password': self.nessus_password,
            'status': self.status,
            'scan_message': self.scan_message,
            'result': self.result,
            'event_id': self.event_id,
            'process_started': self.process_started,
            'created': self.created
        }


class ScanEvents(db.Model):
    id = db.Column(Integer, primary_key=True)
    scan_id = db.Column(db.String(100), ForeignKey('scan.id'))
    event_id = db.Column(Integer, ForeignKey('events.id'))
    scan_event_history = db.Column(db.Text(), nullable=True)
    created = db.Column(db.DateTime, nullable=False,
                        default=datetime.datetime.utcnow)

    def __str__(self):
        return self.scan_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'event_id': self.event_id,
            'scan_event_history': self.scan_event_history
        }
