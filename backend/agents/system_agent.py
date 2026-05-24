from .base_agent import BaseAgent, AgentResult, AgentFinding
import json
from typing import List

class SystemAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SYSTEM_AGENT", description="Detects System-level anomalies and privilege escalations")
        
    async def analyze(self, signals: List[dict], context: dict) -> AgentResult:
        from config import AgentConfig
        
        self.log_execution("Investigating System Logs, Persistence, and Integrity...")
        
        findings = []
        is_malicious = False
        max_confidence = 0.0
        
        # 1. Broaden Filter
        system_signals = [
            s for s in signals 
            if s.get('mitre_id') in ['T1203', 'T1548', 'T1068', 'T1053', 'T1547', 'T1543', 'T1070', 'T1562', 'T1027', 'T1218', 'T1486', 'T1490']
            or any(k in s.get('event_type', '') for k in ['System', 'Process', 'Registry', 'Service', 'File', 'Command', 'Error'])
        ]
        
        for signal in system_signals:
            raw = str(signal).lower()
            sig_context = signal.get('context', {})
            details = str(sig_context.get('details', '')).lower()
            reasoning = str(sig_context.get('reasoning', '')).strip()
            suspected_attack = str(signal.get('suspected_attack', '')).strip()
            evt_type = str(signal.get('event_type', '')).lower()

            # ------------------------------------------------------------------
            # Rule 1: Process Anomalies
            # Logic: Segfaults, core dumps
            # ------------------------------------------------------------------
            if any(err in raw for err in AgentConfig.SYSTEM_CRITICAL_ERRORS):
                findings.append(AgentFinding(
                    title="Process Memory Corruption",
                    description="Detected segmentation fault (segfault) or core dump. Possible exploitation attempt.",
                    severity="HIGH",
                    mitre_technique="T1203"
                ))
                is_malicious = True
                max_confidence = max(max_confidence, 0.85)

            # ------------------------------------------------------------------
            # Rule 2: Privilege Escalation
            # Logic: sudo abuse, semantic anomalies (T1548)
            # ------------------------------------------------------------------
            if "t1548" in str(signal.get('mitre_id', '')).lower() or "sudo" in raw or "privilege escalation" in raw:
                 desc = "Detected potential privilege escalation or sudo abuse."
                 if reasoning:
                     desc += f" Reasoning: {reasoning}"
                 elif details:
                     desc += f" Details: {details}"
                 elif suspected_attack:
                     desc += f" Specifics: {suspected_attack}"
                     
                 findings.append(AgentFinding(
                     title="Privilege Escalation Attempt",
                     description=desc,
                     severity="CRITICAL",
                     mitre_technique="T1548"
                 ))
                 is_malicious = True
                 max_confidence = max(max_confidence, 0.95)

            # ------------------------------------------------------------------
            # Rule 4: Persistence (Scheduled Tasks)
            # Logic: schtasks, cron
            # ------------------------------------------------------------------
            if "schtasks" in raw or "cron" in raw:
                findings.append(AgentFinding(
                     title="Scheduled Task Persistence",
                     description=f"Scheduled task modification detected: {details}",
                     severity="HIGH",
                     mitre_technique="T1053"
                ))
                is_malicious = True
                max_confidence = max(max_confidence, 0.9)

            # ------------------------------------------------------------------
            # Rule 5: Registry Run Keys
            # Logic: Writes to Run keys
            # ------------------------------------------------------------------
            if "registry" in evt_type and any(key.lower() in details for key in AgentConfig.SYSTEM_SENSITIVE_REGISTRY_KEYS):
                 findings.append(AgentFinding(
                     title="Registry Persistence Attempt",
                     description=f"Modification to Startup Registry Key detected: {details}",
                     severity="CRITICAL",
                     mitre_technique="T1547.001"
                 ))
                 is_malicious = True
                 max_confidence = max(max_confidence, 0.95)

            # ------------------------------------------------------------------
            # Rule 6: New Service Creation
            # Logic: sc create, systemctl
            # ------------------------------------------------------------------
            if "sc create" in raw or "systemctl enable" in raw:
                 findings.append(AgentFinding(
                     title="New Service Created",
                     description=f"System service creation detected: {details}",
                     severity="HIGH",
                     mitre_technique="T1543"
                 ))
                 is_malicious = True
                 max_confidence = max(max_confidence, 0.9)

            # ------------------------------------------------------------------
            # Rule 8: Log Clearing
            # Logic: wevtutil, rm logs
            # ------------------------------------------------------------------
            if any(cmd in raw for cmd in ["wevtutil cl", "clear-eventlog", "rm -rf /var/log"]):
                 findings.append(AgentFinding(
                     title="Log Clearing Detected",
                     description="Adversary attempted to clear system logs to cover tracks.",
                     severity="CRITICAL",
                     mitre_technique="T1070"
                 ))
                 is_malicious = True
                 max_confidence = max(max_confidence, 0.99)

            # ------------------------------------------------------------------
            # Rule 9: Security Tools Disabling
            # Logic: Stopping Defender/AV
            # ------------------------------------------------------------------
            if "stop-service" in raw and ("defender" in raw or "antivirus" in raw):
                 findings.append(AgentFinding(
                     title="Security Defense Evasion",
                     description="Attempt to disable security service detected.",
                     severity="CRITICAL",
                     mitre_technique="T1562.001"
                 ))
                 is_malicious = True
                 max_confidence = max(max_confidence, 0.95)

            # ------------------------------------------------------------------
            # Rule 10: Obfuscated Scripts
            # Logic: EncodedCommand
            # ------------------------------------------------------------------
            if "powershell" in raw and "encodedcommand" in raw:
                 findings.append(AgentFinding(
                     title="Obfuscated PowerShell Script",
                     description="PowerShell execution with EncodedCommand detected.",
                     severity="HIGH",
                     mitre_technique="T1027"
                 ))
                 is_malicious = True
                 max_confidence = max(max_confidence, 0.85)

            # ------------------------------------------------------------------
            # Rule 11: LOLBins
            # Logic: certutil, rundll32
            # ------------------------------------------------------------------
            if any(bin in raw for bin in ["certutil", "bitsadmin", "rundll32", "regsvr32"]):
                 findings.append(AgentFinding(
                     title="LOLBin Execution Detected",
                     description=f"Suspicious usage of system binary (LOLBin): {details}",
                     severity="MEDIUM",
                     mitre_technique="T1218"
                 ))
                 is_malicious = True
                 max_confidence = max(max_confidence, 0.75)

            # ------------------------------------------------------------------
            # Rule 13: Ransomware Behavior
            # Logic: vssadmin, mass modification
            # ------------------------------------------------------------------
            if "vssadmin delete shadows" in raw:
                 findings.append(AgentFinding(
                     title="Ransomware Precursor (Shadow Copy Deletion)",
                     description="Critical: vssadmin used to delete shadow copies.",
                     severity="CRITICAL",
                     mitre_technique="T1490"
                 ))
                 is_malicious = True
                 max_confidence = max(max_confidence, 1.0)

        # final_verdict logic
        final_verdict = "BENIGN"
        if is_malicious:
            final_verdict = "MALICIOUS"
        elif any(f.severity in ["HIGH", "CRITICAL"] for f in findings):
            final_verdict = "SUSPICIOUS"

        # Deduplicate findings based on description to avoid UI repetition
        unique_findings = []
        seen_descriptions = set()
        for f in findings:
            if f.description not in seen_descriptions:
                unique_findings.append(f)
                seen_descriptions.add(f.description)

        return AgentResult(
            agent_name=self.name,
            verdict=final_verdict,
            confidence=max_confidence,
            findings=unique_findings,
            raw_artifacts={"system_signal_count": len(system_signals)}
        )
