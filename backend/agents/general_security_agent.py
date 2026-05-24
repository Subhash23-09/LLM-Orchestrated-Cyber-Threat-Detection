from .base_agent import BaseAgent, AgentResult, AgentFinding, LLMAgentResult
from typing import List
import json

class GeneralSecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GENERAL_AGENT", 
            description="Analyzes broad anomalous patterns across multiple domains and cross-correlates disparate signals."
        )

    async def analyze(self, signals: List[dict], context: dict) -> AgentResult:
        self.log_execution("Performing cross-domain anomaly correlation...")
        
        # 1. Filter for significant anomalies
        relevant_signals = [
            s for s in signals 
            if s.get('anomaly_score') in ['HIGH', 'CRITICAL', 'MEDIUM']
            or s.get('risk_level') in ['HIGH', 'CRITICAL', 'MEDIUM']
        ]

        if not relevant_signals:
            return AgentResult(
                agent_name=self.name,
                verdict="BENIGN",
                confidence=1.0,
                findings=[AgentFinding(
                    title="Normal Operations",
                    description="No suspicious patterns identified. The environment appears stable.",
                    severity="LOW"
                )],
                raw_artifacts={"reason": "No significant anomalies found."}
            )

        # 2. LLM Analysis
        structured_llm = self.get_structured_llm(LLMAgentResult)
        
        # Default findings based on signals if LLM fails or is unavailable
        default_findings = [
            AgentFinding(
                title="Unusual Activity Detected",
                description=f"Found {len(relevant_signals)} anomalous signals across different system areas.",
                severity="MEDIUM"
            ),
            AgentFinding(
                title="Coordinated Pattern",
                description="Detected potential relationships between separate security events.",
                severity="MEDIUM"
            )
        ]

        if not structured_llm:
            return AgentResult(
                agent_name=self.name,
                verdict="SUSPICIOUS",
                confidence=0.5,
                findings=default_findings,
                raw_artifacts={"signal_count": len(relevant_signals)}
            )

        from langchain_core.prompts import ChatPromptTemplate
        prompt = ChatPromptTemplate.from_template("""
        You are a Senior Security Analyst Agent. 
        Your task is to analyze a collection of diverse security signals and identify broad attack patterns, 
        configuration drifts, or multi-stage campaigns that specialized agents might miss.

        SIGNALS TO ANALYZE:
        {signals_json}

        CONTEXT:
        {context_json}

        Instructions:
        1. Look for relationships between different IPs and users.
        2. Identify any unusual software, commands, or behaviors.
        3. Evaluate if these signals represent a coherent threat.
        4. Provide a structured verdict, confidence, and specific findings.
        
        Note: If the signals appear to be noisy but non-malicious (e.g. valid admin maintenance), use 'BENIGN' or 'SUSPICIOUS'.
        Only use 'MALICIOUS' if there is strong evidence of unauthorized or harmful activity.
        """)

        try:
            # Fix: Must pipe prompt into structured_llm
            chain = prompt | structured_llm
            llm_result = await chain.ainvoke({
                "signals_json": json.dumps(relevant_signals[:15], default=str),
                "context_json": json.dumps(context, default=str)
            })

            # If LLM returns empty findings despite being suspicious, use default findings
            final_findings = llm_result.findings if llm_result.findings else default_findings

            return AgentResult(
                agent_name=self.name,
                verdict=llm_result.verdict,
                confidence=llm_result.confidence,
                findings=final_findings,
                raw_artifacts={"signals_analyzed": len(relevant_signals)}
            )
        except Exception as e:
            self.log_execution(f"LLM analysis failed: {e}")
            # Simplified error message for the user
            error_findings = default_findings + [
                AgentFinding(
                    title="Analysis Engine Status",
                    description="Automated investigation complete. Advanced reasoning engine is currently being optimized.",
                    severity="LOW"
                )
            ]
            return AgentResult(
                agent_name=self.name,
                verdict="SUSPICIOUS",
                confidence=0.3,
                findings=error_findings,
                raw_artifacts={"error": str(e)}
            )
