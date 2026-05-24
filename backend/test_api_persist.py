import requests
import json

url = "http://localhost:8000/api/v1/narrative/learn"
payload = {
    "case_file": {
        "investigation_details": {
            "involved_trace": ["9.9.9.9"],
            "target_user": "manual_test_user",
            "attack_types": ["MANUAL_PERSISTENCE_CHECK"],
            "agent_deployed": "TEST_AGENT"
        }
    }
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
