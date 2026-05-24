import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Security Keys
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'acd-sdi-platform-secret-2025')
    INGESTION_API_KEY = os.environ.get('INGESTION_API_KEY', 'acd-sdi-secret-key-2025')
    
    # LLM & AI Services
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # Threat Intelligence APIs
    VIRUSTOTAL_API_KEY = os.environ.get('VIRUSTOTAL_API', 'your_virustotal_key_here')
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql+aiomysql://root:@localhost:3306/acd_sdi?charset=utf8mb4')
    
    # Derived Sync URLs for Celery
    _SYNC_URL = DATABASE_URL.replace("mysql+aiomysql", "mysql+pymysql")
    CELERY_BROKER_URL = "sqla+" + _SYNC_URL
    CELERY_RESULT_BACKEND = "db+" + _SYNC_URL
    
    # Enrichment Settings
    GEOIP_API_URL = "http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,city,isp,org,as,proxy,hosting"
    VIRUSTOTAL_IP_URL = "https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    
    # Phase 5: Enrichment Config
    ENABLE_GEOIP = True
    ENABLE_VIRUSTOTAL = True  # Set to False if API key not available
    ENABLE_INCIDENT_MEMORY = True
    
    # API Rate Limiting
    GEOIP_RATE_LIMIT = 45  # requests per minute (free tier: 45/min)
    VIRUSTOTAL_RATE_LIMIT = 4  # requests per minute (free tier)
    
    # Phase 4: Aggregation Settings
    TIME_WINDOW_MINUTES = 5
    ESCALATION_THRESHOLD = 1.5  # 50% increase triggers escalation alert
    
    # Phase 6: Scoring Thresholds
    HIGH_ATTEMPT_THRESHOLD = 10
    CRITICAL_GEOGRAPHY = ['CN', 'RU', 'KP', 'IR']  # Sanctioned/high-risk countries
    MALICIOUS_IP_SCORE_THRESHOLD = 5  # VirusTotal malicious vendor count

class AgentConfig:
    """
    Consolidated configuration for all Agent Rules to avoid hardcoding.
    """
    # AUTH AGENT
    AUTH_BRUTE_FORCE_THRESHOLD = 10
    AUTH_BRUTE_FORCE_WINDOW_MINUTES = 2
    AUTH_CREDENTIAL_STUFFING_THRESHOLD = 15
    AUTH_CREDENTIAL_STUFFING_WINDOW_MINUTES = 5
    AUTH_SUSPICIOUS_TIME_START = 22 # 10 PM
    AUTH_SUSPICIOUS_TIME_END = 6    # 6 AM
    
    # EXFIL AGENT
    EXFIL_VOLUME_THRESHOLD_MB = 100
    EXFIL_VOLUME_WINDOW_MINUTES = 10
    EXFIL_SENSITIVE_KEYWORDS = ["confidential", "secret", "proprietary", "key", "credential", "passport", "ssn"]
    EXFIL_SENSITIVE_EXTENSIONS = [".key", ".p12", ".pfx", ".jks"]
    EXFIL_SUSPICIOUS_PROTOCOLS = ["dns", "icmp"]
    EXFIL_BEACONING_INTERVAL_MIN = 60
    EXFIL_BEACONING_INTERVAL_MAX = 300
    EXFIL_SUSPICIOUS_USER_AGENTS = ["requests", "python", "curl"]



    # DDOS AGENT
    DDOS_RATE_LIMIT_RPS = 10000
    DDOS_BANDWIDTH_THRESHOLD_PERCENT = 80

    # SYSTEM AGENT
    SYSTEM_CRITICAL_ERRORS = ["segfault", "core dumped"]
    SYSTEM_SUSPICIOUS_COMMANDS = [
        "net user", "net group", "whoami /priv", # Discovery
        "schtasks", "cron", # Persistence
        "sc create", "systemctl enable", # Service
        "wevtutil cl", "Clear-EventLog", "rm -rf /var/log", # Log Clearing
        "vssadmin delete shadows", # Ransomware
        "powershell -EncodedCommand", # Obfuscation
        "certutil", "bitsadmin", "rundll32", "regsvr32" # LOLBins
    ]
    SYSTEM_SENSITIVE_REGISTRY_KEYS = [
        r"Software\Microsoft\Windows\CurrentVersion\Run"
    ]
