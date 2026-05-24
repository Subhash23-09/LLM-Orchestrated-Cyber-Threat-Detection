from flask import Flask
from models import db
from services.learning_service import LearningService
import os
from sqlalchemy import text

# Setup minimal Flask app to provide application context
app = Flask(__name__)
# Use the same DB URL as the main app
db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/acd_sdi')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def test_learning_fix():
    with app.app_context():
        print("Testing Learning Service Fix...")
        
        # Mock Case File
        mock_case = {
            "case_id": "TEST-001",
            "executive_verdict": {
                "executive_summary": "Test Incident for Memory Fix"
            },
            "investigation_details": {
                "agent_deployed": "TEST_AGENT",
                "involved_trace": ["1.2.3.4"],
                "agent_verdict": "MALICIOUS"
            }
        }
        
        # Call Service
        try:
            result = LearningService.learn_from_incident(mock_case)
            print(f"Service returned: {result}")
            
            # Verify in DB
            sql = text("SELECT count(*) FROM incident_memory WHERE entity_value = '1.2.3.4'")
            count = db.session.execute(sql).scalar()
            print(f"Rows found in incident_memory for 1.2.3.4: {count}")
            
            if count > 0:
                print("✅ SUCESS: Memory correctly written to 'incident_memory' table!")
            else:
                print("❌ FAILURE: Data not found in 'incident_memory'.")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_learning_fix()
