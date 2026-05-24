
import asyncio
import json
from unittest.mock import MagicMock, patch
import sys
import os

# Mock the database and models before importing NarrativeService
sys.modules['database'] = MagicMock()
sys.modules['models_v2'] = MagicMock()
sys.modules['models'] = MagicMock()

# Mock the LLM service to capture the prompt
mock_llm = MagicMock()

async def test_narrative_formatting():
    from services.narrative_service import NarrativeService
    
    agent_reports = {
        "AUTH_AGENT": {
            "agent": "AUTH_AGENT",
            "report": {
                "verdict": "MALICIOUS",
                "findings": [
                    {"title": "High Auth Failure Count", "description": "IP 195.144.21.143 (Russia) exceeded failure threshold."}
                ]
            }
        }
    }
    
    decision = {
        "executive_summary": "Confirmed brute force attack."
    }
    
    context = {
        "short_term": {
            "active_context": [
                {
                    "event_type": "auth_failure",
                    "actor": {"source_ip": "195.144.21.143"},
                    "target": {"user": "admin"},
                    "metrics": {"confidence": 95},
                    "context": {
                        "geoip": {"country": "Russia"}
                    },
                    "created_at": "2026-01-06T07:45:01"
                }
            ]
        }
    }
    
    with patch('services.llm_service.LLMService.stream_decision') as mock_stream:
        NarrativeService.generate_storyline(agent_reports, decision, context)
        
        # Verify the input_data passed to stream_decision
        args, kwargs = mock_stream.call_args
        template = args[0]
        input_data = args[1]
        
        print("--- TEMPLATE CHECK ---")
        if "GEOGRAPHICAL LOCATION" in template:
            print("✅ Template contains location instructions.")
        else:
            print("❌ Template MISSING location instructions.")
            
        print("\n--- SIGNALS CHECK ---")
        signals_text = input_data['signals']
        print(f"Signals text:\n{signals_text}")
        if "Russia" in signals_text:
            print("✅ Signals include country name.")
        else:
            print("❌ Signals MISSING country name.")
            
        print("\n--- FINDINGS CHECK ---")
        findings_text = input_data['findings']
        print(f"Findings text:\n{findings_text}")
        if "Russia" in findings_text:
            print("✅ Findings include country name.")
        else:
            print("❌ Findings MISSING country name.")

if __name__ == "__main__":
    asyncio.run(test_narrative_formatting())
