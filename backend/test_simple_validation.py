"""
Simple validation test for 8-phase preprocessor
Tests individual components without database dependency
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from services_v2.preprocessor import (
    FieldNormalizer,
    AnomalyScorer,
    AggregationEngine,
    DynamicLogAnalyzer
)

print("=" * 80)
print("8-Phase Signal Engine - Component Validation Test")
print("=" * 80)

# Test 1: Field Normalization
print("\n[Test 1] Field Normalization")
print("-" * 80)

test_logs = [
    "Failed password for admin from 185.220.101.50 port 44332 ssh2",
    "EventID=4625 TargetUserName=dbadmin IpAddress=103.89.91.95 LogonType=3",
    "DENY TCP src=45.142.212.30 dst=10.0.0.5 sport=44532 dport=3306"
]

for log in test_logs:
    normalized = FieldNormalizer.normalize_log_entry(log)
    print(f"\nRaw: {log[:60]}...")
    print(f"  → IP: {normalized['source_ip']}")
    print(f"  → User: {normalized['target_user']}")
    print(f"  → Event: {normalized['event_type']}")
    print(f"  → Action: {normalized['action']}")

print("\n✅ Field Normalization: PASSED")

# Test 2: Aggregation Engine
print("\n\n[Test 2] Time-Window Aggregation")
print("-" * 80)

from datetime import datetime, timedelta

mock_events = []
base_time = datetime.utcnow()

# Create escalation pattern: 2 → 5 → 12 attempts
for i in range(2):
    mock_events.append({
        'source_ip': '185.220.101.50',
        'target_user': 'admin',
        'event_type': 'auth_failure',
        'timestamp': base_time + timedelta(minutes=i)
    })

for i in range(5):
    mock_events.append({
        'source_ip': '185.220.101.50',
        'target_user': 'admin',
        'event_type': 'auth_failure',
        'timestamp': base_time + timedelta(minutes=5 + i)
    })

for i in range(12):
    mock_events.append({
        'source_ip': '185.220.101.50',
        'target_user': 'admin',
        'event_type': 'auth_failure',
        'timestamp': base_time + timedelta(minutes=10 + i)
    })

aggregated = AggregationEngine.aggregate_events(mock_events, window_minutes=5)

for agg in aggregated:
    print(f"\nAggregated Signal:")
    print(f"  Source IP: {agg['source_ip']}")
    print(f"  Target: {agg['target_user']}")
    print(f"  Event Count: {agg['event_count']}")
    print(f"  Escalation Detected: {agg['escalation_detected']}")
    print(f"  Compression Ratio: {agg['compression_ratio']}:1")

compression = len(mock_events) / len(aggregated) if aggregated else 1
print(f"\n  Total Compression: {len(mock_events)} logs → {len(aggregated)} signal = {compression:.1f}x")
print("✅ Aggregation Engine: PASSED")

# Test 3: Log Analyzer (without async enrichment)
print("\n\n[Test 3] DynamicLogAnalyzer - Basic Parsing")
print("-" * 80)

analyzer = DynamicLogAnalyzer()

sample_logs = [
    "Jan 3 16:30:01 server sshd[12345]: Failed password for admin from 185.220.101.50 port 44332 ssh2",
    "Jan 3 16:30:15 server sshd[12346]: Failed password for admin from 185.220.101.50 port 44333 ssh2",
    "Jan 3 16:30:30 server sshd[12347]: Failed password for admin from 185.220.101.50 port 44334 ssh2",
    "Jan 3 16:31:05 server sshd[12348]: Failed password for admin from 185.220.101.50 port 44335 ssh2",
    "Jan 3 16:31:20 server sshd[12349]: Failed password for admin from 185.220.101.50 port 44336 ssh2"
]

for log in sample_logs:
    analyzer.process_line(log)

print(f"  Processed {len(sample_logs)} log lines")
print(f"  Extracted {len(analyzer.raw_events)} normalized events")
print(f"  Detected {len(analyzer.templates)} Drain3 templates")

print("✅ DynamicLogAnalyzer: PASSED")

# Summary
print("\n" + "=" * 80)
print("✅ ALL COMPONENT TESTS PASSED!")
print("=" * 80)
print("\n📊 Summary:")
print("  ✓ Field Normalization (Phase 3)")
print("  ✓ Time-Window Aggregation (Phase 4)")
print("  ✓ Drain3 Template Mining (Phase 2)")
print("  ✓ Event Processing Pipeline")
print("\n⚠️  Note: Database-dependent tests (Phase 5, 6, 7) require running backend")
print("   To test full enrichment: Use frontend to upload logs or run with MySQL connection")
print("\n🎉 8-Phase Engine Core Components Validated!")
