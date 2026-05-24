from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }

class LogEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_file = db.Column(db.String(100), nullable=False)
    raw_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)

class Signal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))
    source_ip = db.Column(db.String(50))
    target_user = db.Column(db.String(50))
    failed_attempts = db.Column(db.Integer, default=0)
    time_window = db.Column(db.String(50))
    anomaly_score = db.Column(db.String(20)) # LOW, MEDIUM, HIGH, CRITICAL
    suspected_attack = db.Column(db.String(100))
    mitre_id = db.Column(db.String(50))
    confidence = db.Column(db.Integer, default=80) 
    context_info = db.Column(db.Text, default='{}') # JSON string for 6-Factor "Context"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        try:
            ctx = json.loads(self.context_info) if self.context_info else {}
        except:
            ctx = {}

        return {
            "id": self.id,
            "event_type": self.event_type, # Top level type
            "actor": {
                "source_ip": self.source_ip,
                # "user": "derived from logs if avail" -> currently not separate col, maybe inside context or add if needed.
                # User provided example has "user" inside actor. 
                # My model has 'target_user' which is arguably Target. 
                # I'll stick to source_ip for actor for now.
            },
            "target": {
                "user": self.target_user,
                "destination": "server" # Implicit for now
            },
            "action": self.suspected_attack, # Semantic meaning
            "metrics": {
                "failed_attempts": self.failed_attempts,
                "confidence": self.confidence 
            },
            "time_window": self.time_window,
            "context": ctx,
            "mitre_id": self.mitre_id,
            "anomaly_score": self.anomaly_score,
            "created_at": self.created_at.isoformat()
        }

class HistoricalIncident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(50), nullable=False)
    attack_type = db.Column(db.String(100))
    verdict = db.Column(db.String(50))
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "attack_type": self.attack_type,
            "verdict": self.verdict,
            "summary": self.summary,
            "created_at": self.created_at.isoformat()
        }
