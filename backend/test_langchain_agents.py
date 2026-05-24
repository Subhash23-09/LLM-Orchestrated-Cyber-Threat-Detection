import asyncio
import json
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.auth_agent import AuthAgent
from agents.network_flood_agent import NetworkFloodAgent
from agents.exfiltration_agent import ExfiltrationAgent

from agents.system_agent import SystemAgent
from agents.base_agent import AgentResult

async def test_agents():
    print("🚀 Starting Agent Verification with Structured Output...")
    
    # Mock signals
    mock_auth_signals = [
        {"actor": {"source_ip": "1.1.1.1"}, "event_type": "auth_failure", "mitre_id": "T1110", "metrics": {"failed_attempts": 10}}
    ]
    mock_flood_signals = [
        {"actor": {"source_ip": "2.2.2.2"}, "event_type": "network_flood", "mitre_id": "T1498", "metrics": {"failed_attempts": 5000}}
    ]
    
    context = {"user_baselines": {}, "short_term": {"active_context": []}}
    
    agents = [
        (AuthAgent(), mock_auth_signals),
        (NetworkFloodAgent(), mock_flood_signals)
    ]
    
    for agent, signals in agents:
        print(f"\n🧪 Testing {agent.name}...")
        try:
            result = await agent.analyze(signals, context)
            print(f"✅ Result Type: {type(result)}")
            print(f"✅ Verdict: {result.verdict}")
            print(f"✅ Findings: {len(result.findings)}")
            for f in result.findings:
                print(f"   - {f.title}: {f.severity}")
            
            if not isinstance(result, AgentResult):
                print(f"❌ Error: {agent.name} did not return an AgentResult object!")
            else:
                print(f"✨ {agent.name} passed successfully.")
                
        except Exception as e:
            print(f"❌ Error testing {agent.name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agents())
