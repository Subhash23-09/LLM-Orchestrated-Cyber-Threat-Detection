import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from agents.auth_agent import AuthAgent
from agents.exfiltration_agent import ExfiltrationAgent

from agents.network_flood_agent import NetworkFloodAgent
from agents.system_agent import SystemAgent

async def test_agents():
    # 1. Mock Signals
    mock_signals = [
        {"event_type": "authentication", "source_ip": "1.2.3.4", "failed_attempts": 25},
        {"event_type": "file_transfer", "dest_ip": "9.9.9.9", "size_bytes": 1024*1024*600, "file_name": "confidential_project_X.zip"},
        {"event_type": "arp", "source_ip": "192.168.1.1", "details": "duplicate_mac detected for gateway"},
        {"event_type": "ssl_error", "domain": "bank.com", "details": "certificate mismatch"},
        {"event_type": "network_flow", "source_ip": "1.1.1.1", "request_count": 5000},
        {"event_type": "system", "details": "critical process segfault core dumped"}
    ]
    
    context = {"tenant": "test_corp", "assets": []}
    
    agents = [
        AuthAgent(),
        ExfiltrationAgent(),

        NetworkFloodAgent(),
        SystemAgent()
    ]
    
    print("\n--- Starting Multi-Agent Forensic Verification ---")
    for agent in agents:
        print(f"\n[DEPLOYING] {agent.name}...")
        try:
            result = await agent.analyze(mock_signals, context)
            print(f"[VERDICT] {agent.name}: {result.verdict} (Confidence: {result.confidence*100:.1f}%)")
            for f in result.findings:
                print(f"  - [{f.severity}] {f.title}: {f.description}")
        except Exception as e:
            print(f"[ERROR] Agent {agent.name} failed: {e}")
    
    print("\n--- Final Delivery Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(test_agents())
