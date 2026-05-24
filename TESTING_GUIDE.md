# 🧪 End-to-End Testing Guide - 8-Phase Signal Engine

## System Status

| Component | Status | URL/Port |
|-----------|--------|----------|
| **Backend** | ✅ Running | http://localhost:8000 |
| **Frontend** | ✅ Running | http://localhost:5173 (check terminal) |
| **Database** | ⚠️ Check MySQL | localhost:3306 |

---

## Testing Steps

### 1. Open the Application

**Open your browser** and navigate to:
```
http://localhost:5173
```

### 2. Login (if required)

Try these credentials:
- Username: `admin` or `test`
- Password: `admin` or `password`

### 3. Upload Test Logs

#### Option A: Use Sample Log File

Use the existing sample: `d:\Project_8th\threat_sample.log`

#### Option B: Create Quick Test File

Create a file `test_attack.log` with this content:

```
Jan 3 17:00:01 server sshd[12345]: Failed password for admin from 185.220.101.50 port 44332 ssh2
Jan 3 17:00:15 server sshd[12346]: Failed password for admin from 185.220.101.50 port 44333 ssh2
Jan 3 17:00:30 server sshd[12347]: Failed password for admin from 185.220.101.50 port 44334 ssh2
Jan 3 17:01:05 server sshd[12348]: Failed password for admin from 185.220.101.50 port 44335 ssh2
Jan 3 17:01:20 server sshd[12349]: Failed password for admin from 185.220.101.50 port 44336 ssh2
Jan 3 17:01:45 server sshd[12350]: Failed password for admin from 185.220.101.50 port 44337 ssh2
Jan 3 17:02:10 server sshd[12351]: Failed password for admin from 185.220.101.50 port 44338 ssh2
Jan 3 17:02:35 server sshd[12352]: Failed password for admin from 185.220.101.50 port 44339 ssh2
Jan 3 17:03:00 server sshd[12353]: Failed password for admin from 185.220.101.50 port 44340 ssh2
Jan 3 17:03:25 server sshd[12354]: Failed password for admin from 185.220.101.50 port 44341 ssh2
Jan 3 17:03:50 server sshd[12355]: Failed password for admin from 185.220.101.50 port 44342 ssh2
Jan 3 17:04:15 server sshd[12356]: Failed password for admin from 185.220.101.50 port 44343 ssh2
```

This simulates a **brute force attack on CRITICAL asset (admin)**.

---

### 4. What to Look For

After uploading, check the generated signals for:

#### ✅ Phase 3: Field Normalization
- IP extracted: `185.220.101.50`
- User extracted: `admin`
- Event type: `auth_failure`

#### ✅ Phase 4: Time-Window Aggregation
- **Event Count**: 12
- **Compression**: 12 logs → 1 signal
- **Escalation Detected**: Should show pattern

#### ✅ Phase 5: GeoIP Enrichment  
Look in signal's `context_json`:
```json
{
  "geoip": {
    "country": "Russia" or other,
    "isp": "...",
    "proxy": true/false
  }
}
```

#### ✅ Phase 6: 6-Rule Scoring
Check `evidence` field:
```json
{
  "evidence": [
    "High attempt count: 12 events (+12)",
    "Critical asset targeted: admin (+30)",
    "Target lacks MFA (+15)",
    "Attack from high-risk country: RU (+20)",
    ...
  ]
}
```

#### ✅ Phase 7: Taint-Aware Scoring
- **Asset Multiplier**: Should be 1.5x (admin is CRITICAL)
- **Confidence**: ~85-95% (high due to critical target)

#### ✅ Phase 8: MITRE Mapping
- **MITRE ID**: `T1110` or `T1110.001` (Brute Force)

---

## Expected Signal Output

```json
{
  "attack_type": "Authentication Attack",
  "risk_level": "CRITICAL" or "HIGH",
  "confidence": 0.85-0.95,
  "mitre_id": "T1110.001",
  "source_ip": "185.220.101.50",
  "target_user": "admin",
  "event_count": 12,
  "context_json": {
    "geoip": {...},
    "virustotal": {...} (if API key configured),
    "compression_ratio": 12,
    "evidence": [...],
    "asset_multiplier": 1.5
  }
}
```

---

## Troubleshooting

### No Signals Generated
1. Check MySQL is running: `mysql -u root -p`
2. Verify database: `USE acd_sdi; SHOW TABLES;`
3. Check backend logs for errors

### No GeoIP Data
- Normal for private IPs (127.x, 192.168.x)
- Check internet connectivity for public IPs

### No VirusTotal Data
- Add API key to `.env`: `VIRUSTOTAL_API=your_key`
- Restart backend after adding key

### Missing Asset Data
- Ensure assets table populated:
  ```sql
  SELECT * FROM assets;
  ```
- Should see entries for: admin, root, guest, etc.

---

## Comparison Test

### Test 1: Attack on CRITICAL Asset (admin)
**Expected**: Risk = CRITICAL, Confidence ~90%

### Test 2: Same Attack on LOW Asset (guest)
Change logs to target `guest` instead of `admin`

**Expected**: Risk = LOW/MEDIUM, Confidence ~40% (taint-aware downgrade)

This proves Phase 7 (Taint-Aware Scoring) is working!

---

## Success Criteria

✅ **Phase 1-4**: Logs processed, normalized, aggregated  
✅ **Phase 5**: GeoIP data present (if public IP)  
✅ **Phase 6**: Evidence list with 6-rule scores  
✅ **Phase 7**: Asset multiplier applied (1.5x for admin)  
✅ **Phase 8**: Correct MITRE technique mapped  

**Compression**: 12+ logs → 1 comprehensive signal ✅

---

## 🎉 You're Testing Live!

The 8-phase signal engine is now processing your logs in real-time with:
- Field normalization
- GeoIP enrichment
- VirusTotal reputation
- Asset-aware scoring
- Evidence-based confidence
- MITRE mapping

**Happy Testing!** 🚀
