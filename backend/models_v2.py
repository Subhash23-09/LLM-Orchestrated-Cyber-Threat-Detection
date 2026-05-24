from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON, Float, Boolean, Date, UniqueConstraint
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }

class Asset(Base):
    __tablename__ = "assets"
    username = Column(String(255), primary_key=True)
    criticality = Column(Enum('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'), default='LOW')
    mfa_status = Column(Integer, default=0)
    privilege_level = Column(String(50))
    department = Column(String(100))

class SecuritySignal(Base):
    __tablename__ = "security_signals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    attack_type = Column(String(255))
    raw_event_type = Column(String(100), nullable=True)
    anomaly_score = Column(Enum('HIGH', 'MEDIUM', 'LOW', 'INFO'))
    confidence = Column(Float)
    risk_level = Column(Enum('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'))
    mitre_id = Column(String(50))
    source_ip = Column(String(50))
    target_user = Column(String(255))
    event_count = Column(Integer, default=1)
    reasoning = Column(Text)
    context_json = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        ctx = self.context_json or {}
        # Merge basic metrics with specialized ones from context
        metrics = {
            "failed_attempts": self.event_count, 
            "confidence": int(self.confidence * 100) if self.confidence <= 1 else int(self.confidence)
        }
        if 'metrics' in ctx:
            metrics.update(ctx['metrics'])
            
        return {
            "id": self.id,
            "event_type": self.attack_type,
            "raw_event_type": self.raw_event_type,
            "actor": {"source_ip": self.source_ip},
            "target": {"user": self.target_user, "destination": "server"},
            "action": self.attack_type,
            "metrics": metrics,
            "time_window": "session",
            "context": ctx,
            "mitre_id": self.mitre_id,
            "anomaly_score": self.anomaly_score,
            "created_at": self.timestamp.isoformat()
        }

class IncidentMemory(Base):
    __tablename__ = "incident_memory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(Enum('ACTOR', 'TARGET', 'ACTION'))
    entity_value = Column(String(255))
    incident_data = Column(JSON)
    feedback_score = Column(Integer, default=0)
    analyst_notes = Column(Text)
    last_seen = Column(DateTime, default=datetime.utcnow)

class AttackStoryline(Base):
    __tablename__ = "attack_storylines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    description = Column(Text)
    mitre_techniques = Column(JSON)
    involved_ips = Column(JSON)
    involved_users = Column(JSON)
    severity = Column(Enum('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'))
    storyline_markdown = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyStats(Base):
    __tablename__ = "daily_stats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.utcnow) # strictly stores date part
    entity_type = Column(Enum('USER', 'IP'))
    entity_val = Column(String(255))
    event_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('date', 'entity_type', 'entity_val', name='_date_entity_uc'),)

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "entity": f"{self.entity_type}:{self.entity_val}",
            "count": self.event_count
        }

class UserBaseline(Base):
    __tablename__ = "user_baselines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(Enum('USER', 'IP'))
    entity_val = Column(String(255))
    avg_events_per_day = Column(Float, default=0.0)
    std_dev_events = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('entity_type', 'entity_val', name='_entity_baseline_uc'),)


class RawLog(Base):
    __tablename__ = "raw_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_system = Column(String(100))
    raw_message = Column(Text)
    ingested_at = Column(DateTime, default=datetime.utcnow)

class ParsedTemplate(Base):
    __tablename__ = "parsed_templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer)
    template_string = Column(Text)
    source_system = Column(String(100))
    last_seen = Column(DateTime, default=datetime.utcnow)
