"""
Test Suite for 8-Phase Signal Engine
Tests all phases with diverse attack scenarios
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from database import AsyncSessionLocal
from services_v2.preprocessor import PreprocessorService
from models_v2 import Asset, SecuritySignal
from sqlalchemy import select


async def setup_test_assets(session):
    """Seed test assets for taint-aware scoring validation"""
    test_assets = [
        Asset(username='admin', criticality='CRITICAL', mfa_status=0, privilege_level='root', department='IT'),
        Asset(username='root', criticality='CRITICAL', mfa_status=1, privilege_level='superuser', department='System'),
        Asset(username='dbadmin', criticality='HIGH', mfa_status=0, privilege_level='dba', department='Database'),
        Asset(username='guest', criticality='LOW', mfa_status=0, privilege_level='none', department='Demo'),
        Asset(username='testuser', criticality='MEDIUM', mfa_status=1, privilege_level='user', department='Engineering'),
    ]
    
    for asset in test_assets:
        # Check if exists
        stmt = select(Asset).where(Asset.username == asset.username)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if not existing:
            session.add(asset)
    
    await session.commit()
    print("✅ Test assets seeded")


def create_test_log_scenarios():
    """
    Create diverse test log scenarios covering:
    - Multi-source logs (SSH, Windows, Firewall)
    - Different attack types
    - Escalation patterns
    - Critical vs low-value targets
    """
    
    scenarios = {
        'scenario1_brute_force_critical': [
            # High-risk brute force on CRITICAL asset from Russia
            'Jan 3 16:30:01 server sshd[12345]: Failed password for admin from 185.220.101.50 port 44332 ssh2',
            'Jan 3 16:30:15 server sshd[12346]: Failed password for admin from 185.220.101.50 port 44333 ssh2',
            'Jan 3 16:30:30 server sshd[12347]: Failed password for admin from 185.220.101.50 port 44334 ssh2',
            'Jan 3 16:31:05 server sshd[12348]: Failed password for admin from 185.220.101.50 port 44335 ssh2',
            'Jan 3 16:31:20 server sshd[12349]: Failed password for admin from 185.220.101.50 port 44336 ssh2',
            'Jan 3 16:31:45 server sshd[12350]: Failed password for admin from 185.220.101.50 port 44337 ssh2',
            'Jan 3 16:32:10 server sshd[12351]: Failed password for admin from 185.220.101.50 port 44338 ssh2',
            'Jan 3 16:32:35 server sshd[12352]: Failed password for admin from 185.220.101.50 port 44339 ssh2',
            'Jan 3 16:33:00 server sshd[12353]: Failed password for admin from 185.220.101.50 port 44340 ssh2',
            'Jan 3 16:33:25 server sshd[12354]: Failed password for admin from 185.220.101.50 port 44341 ssh2',
            'Jan 3 16:33:50 server sshd[12355]: Failed password for admin from 185.220.101.50 port 44342 ssh2',
            'Jan 3 16:34:15 server sshd[12356]: Failed password for admin from 185.220.101.50 port 44343 ssh2',
        ],
        
        'scenario2_brute_force_low_target': [
            # Same attack but against LOW criticality target
            'Jan 3 16:30:01 server sshd[22345]: Failed password for guest from 192.168.1.100 port 55432 ssh2',
            'Jan 3 16:30:15 server sshd[22346]: Failed password for guest from 192.168.1.100 port 55433 ssh2',
            'Jan 3 16:30:30 server sshd[22347]: Failed password for guest from 192.168.1.100 port 55434 ssh2',
            'Jan 3 16:31:05 server sshd[22348]: Failed password for guest from 192.168.1.100 port 55435 ssh2',
            'Jan 3 16:31:20 server sshd[22349]: Failed password for guest from 192.168.1.100 port 55436 ssh2',
        ],
        
        'scenario3_privilege_escalation': [
            # Sudo abuse
            'Jan 3 16:35:01 server sudo: testuser : TTY=pts/0 ; PWD=/home/testuser ; USER=root ; COMMAND=/bin/bash',
            'Jan 3 16:35:10 server sudo: testuser : TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow',
            'Jan 3 16:35:25 server sudo: admin : TTY=pts/1 ; PWD=/var/log ; USER=root ; COMMAND=/bin/rm -rf /var/log/*',
        ],
        
        'scenario4_dos_attack': [
            # Volumetric HTTP flood
            *[f'Jan 3 16:40:{i:02d} nginx: 45.142.212.30 - - [03/Jan/2026:16:40:{i:02d}] "GET /api/data HTTP/1.1" 200' 
              for i in range(60)],
        ],
        
        'scenario5_multi_source': [
            # Windows Event Logs
            'EventID=4625 TargetUserName=dbadmin IpAddress=103.89.91.95 LogonType=3 Status=0xC000006D',
            'EventID=4625 TargetUserName=dbadmin IpAddress=103.89.91.95 LogonType=3 Status=0xC000006D',
            # SSH
            'Failed password for dbadmin from 103.89.91.95 port 33221 ssh2',
            'Failed password for dbadmin from 103.89.91.95 port 33222 ssh2',
            # Firewall
            'DENY TCP src=103.89.91.95 dst=10.0.0.5 sport=44532 dport=3306',
        ]
    }
    
    return scenarios


async def run_scenario_test(scenario_name: str, log_lines: list):
    """Run a single test scenario"""
    print(f"\n{'='*80}")
    print(f"Testing: {scenario_name}")
    print(f"{'='*80}")
    
    # Write test log file
    test_file = Path(__file__).parent / 'test_logs' / f'{scenario_name}.log'
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text('\n'.join(log_lines))
    
    # Process
    async with AsyncSessionLocal() as session:
        await setup_test_assets(session)
        
        signals, stats = await PreprocessorService.process_file(str(test_file), session)
        
        print(f"\n📊 Statistics:")
        print(f"  Total lines: {stats['total_lines']}")
        print(f"  Signals generated: {stats['signals_generated']}")
        print(f"  Compression ratio: {stats.get('compression_ratio', 'N/A')}")
        
        print(f"\n🎯 Signals Generated:")
        for i, sig in enumerate(signals, 1):
            print(f"\n  Signal #{i}:")
            print(f"    Attack Type: {sig.attack_type}")
            print(f"    Risk Level: {sig.risk_level}")
            print(f"    Confidence: {sig.confidence:.2%}")
            print(f"    MITRE: {sig.mitre_id}")
            print(f"    Source IP: {sig.source_ip}")
            print(f"    Target: {sig.target_user}")
            print(f"    Event Count: {sig.event_count}")
            print(f"    Reasoning: {sig.reasoning}")
            
            if sig.context_json:
                ctx = sig.context_json
                print(f"    GeoIP: {ctx.get('geoip', {}).get('country', 'N/A')}")
                print(f"    VPN: {ctx.get('is_vpn', False)}")
                print(f"    Malicious: {ctx.get('is_malicious', False)}")
                print(f"    Evidence: {len(ctx.get('evidence', []))} rules triggered")
                if ctx.get('evidence'):
                    for evidence in ctx['evidence'][:3]:
                        print(f"      - {evidence}")


async def run_all_tests():
    """Run complete test suite"""
    print("🚀 Starting 8-Phase Signal Engine Test Suite")
    print("="*80)
    
    scenarios = create_test_log_scenarios()
    
    for name, logs in scenarios.items():
        await run_scenario_test(name, logs)
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)


if __name__ == '__main__':
    asyncio.run(run_all_tests())
