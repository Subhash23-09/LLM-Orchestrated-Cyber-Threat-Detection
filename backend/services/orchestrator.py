import json
import asyncio
from typing import AsyncGenerator, Dict, Any
from services.memory_store import MemoryService
from services.llm_service import LLMService
from agents.auth_agent import AuthAgent
from agents.system_agent import SystemAgent
from agents.exfiltration_agent import ExfiltrationAgent

from agents.network_flood_agent import NetworkFloodAgent
from agents.general_security_agent import GeneralSecurityAgent
from agents.orchestrator_schema import OrchestratorDecision

class OrchestratorService:
    @staticmethod
    async def orchestrate(signals: list, context: dict) -> Dict[str, Any]:
        """
        Runs the full multi-agent pipeline and returns synthesized results.
        """
        results = []
        
        # 1. Deployment
        auth_res = await AuthAgent().analyze(signals, context)
        sys_res = await SystemAgent().analyze(signals, context)
        exfil_res = await ExfiltrationAgent().analyze(signals, context)

        flood_res = await NetworkFloodAgent().analyze(signals, context)
        general_res = await GeneralSecurityAgent().analyze(signals, context)

        results = [auth_res, sys_res, exfil_res, flood_res, general_res]
        
        # 3. Synthesis
        synthesized_plan = await OrchestratorService.synthesize_plan(signals, results)
        
        return {
            "agents_analyzed": results,
            "synthesized_plan": synthesized_plan
        }

    @staticmethod
    async def stream_agent_updates(signals: list, context: dict) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Async generator for SSE (thoughts + answer mesh).
        """
        # Step 1: Initial Thought
        yield {
            "type": "thought",
            "content": f"Orchestrator received {len(signals)} raw security signals. Initializing multi-agent triage..."
        }
        await asyncio.sleep(1)

        # Parallelize for performance in stream
        agents = [AuthAgent(), SystemAgent(), ExfiltrationAgent(), NetworkFloodAgent()]
        agent_names = ["AUTH", "SYSTEM", "EXFIL", "DDOS"]
        
        agent_results = []
        for agent, display_name in zip(agents, agent_names):
            yield {
                "type": "thought",
                "content": f"Deploying {display_name}_AGENT for deep forensic analysis..."
            }
            res = await agent.analyze(signals, context)
            agent_results.append(res)
            
            # Assuming agent.analyze returns an object with a 'verdict' attribute
            # If it returns a dict, use res['verdict']
            verdict_value = res.verdict if hasattr(res, 'verdict') else res.get('verdict', 'UNKNOWN')
            
            yield {
                "type": "thought",
                "content": f"{display_name}_AGENT investigation complete. Verdict: {verdict_value}."
            }
            await asyncio.sleep(0.3)

        # Step 4: Synthesis Thought
        yield {
            "type": "thought",
            "content": "Consolidating agent findings into a master defense plan..."
        }
        
        # Step 5: Streaming the Synthesis (Answer)
        synthesized_plan = await OrchestratorService.synthesize_plan(signals, agent_results)
        
        # Stream the synthesis token by token or in chunks
        # synthesized_plan is now an OrchestratorDecision object
        for chunk in synthesized_plan.reasoning_markdown.split(' '):
            await asyncio.sleep(0.05)
            yield {
                "type": "answer",
                "content": chunk + " "
            }

        yield {
            "type": "thought",
            "content": "Autonomous Defense Plan delivered. Monitoring for perimeter deviations."
        }

    @staticmethod
    async def synthesize_plan(signals: list, agent_results: list) -> OrchestratorDecision:
        """
        Uses LLM to combine all findings into a structured OrchestratorDecision.
        """
        from services.llm_service import LLMService
        llm = LLMService.get_llm()
        
        if not llm:
            return OrchestratorDecision(
                decision="IGNORE",
                reasoning_markdown="## Defense Plan (Heuristic Mode)\n- Monitor flagged patterns.\n- Isolate suspicious IPs found by agents.",
                confidence=0.5,
                risk_level="LOW"
            )

        try:
            from langchain_core.prompts import ChatPromptTemplate
            structured_llm = llm.with_structured_output(OrchestratorDecision)
            
            prompt = ChatPromptTemplate.from_template("""
            You are the "Master Orchestrator" for an Autonomous Cyber Defense system.
            Combine the findings from multiple specialized agents and the raw security signals into a unified defense strategy.
            
            AGENT FINDINGS:
            {findings}
            
            ACTIVE SIGNALS:
            {signals}
            
            Your task:
            1. Synthesize a comprehensive Markdown defense plan (reasoning_markdown).
            2. Determine the final 'decision' string. 
               - If agents found malicious activity, use their names (e.g., "AUTH", "EXFIL").
               - If the activity is suspicious but not definitively malicious, use "GENERAL" or "INVESTIGATE".
               - Only use "IGNORE" if the activity is clearly benign.
            3. Set an overall risk_level and confidence score.
            
            Structure the reasoning_markdown with:
            ### 1. Executive Summary
            ### 2. Detailed Technical Findings
            ### 3. Mitigation & Response Playbook
            ### 4. Continuous Monitoring Strategy
            
            Tone: Professional, expert, security-first.
            """)
            
            chain = prompt | structured_llm
            # Filter signals to focus on significant threats (MEDIUM, HIGH, CRITICAL)
            filtered_signals = [
                s for s in signals 
                if s.get('anomaly_score') in ['MEDIUM', 'HIGH', 'CRITICAL'] 
                or s.get('risk_level') in ['MEDIUM', 'HIGH', 'CRITICAL']
            ]
            
            # If all signals were low/info, just take top 5 to avoid empty context
            if not filtered_signals and signals:
                filtered_signals = signals[:5]

            return await chain.ainvoke({
                "findings": json.dumps([r.model_dump() if hasattr(r, 'model_dump') else r for r in agent_results], default=str), 
                "signals": json.dumps(filtered_signals[:50], default=str)
            })
        except Exception as e:
            print(f"Synthesis failed: {e}")
            return OrchestratorDecision(
                decision="ERROR",
                reasoning_markdown=f"Synthesis failed: {str(e)}. Please review individual agent findings.",
                confidence=0.0,
                risk_level="HIGH"
            )

    @staticmethod
    async def run_cycle():
        """
        Asynchronous wrapper for the new orchestration flow to support the existing UI.
        """
        from services.memory_store import MemoryService
        
        # Run the async orchestration
        try:
            # Fetch context asynchronously
            context = await MemoryService.get_context()
            signals = context['short_term']['active_context']
            
            if not signals:
                return {
                    "status": "idle",
                    "plan": {
                        "decision": "IGNORE",
                        "reasoning": "No active signals found in memory.",
                        "confidence": "HIGH"
                    }
                }

            result = await OrchestratorService.orchestrate(signals, context)
            decision_obj = result['synthesized_plan']
            
            # Intelligent Decision Builder
            # 1. Use the LLM's recommended decision if it's not IGNORE
            # 2. Otherwise fallback to agent verdicts
            final_decision = decision_obj.decision
            
            if final_decision == "IGNORE":
                malicious_agents = [r for r in result['agents_analyzed'] if r.verdict == 'MALICIOUS']
                suspicious_agents = [r for r in result['agents_analyzed'] if r.verdict == 'SUSPICIOUS']
                
                if malicious_agents:
                    final_decision = ", ".join([r.agent_name.replace("_AGENT", "") for r in malicious_agents])
                elif suspicious_agents:
                    final_decision = "INVESTIGATE (" + ", ".join([r.agent_name.replace("_AGENT", "") for r in suspicious_agents]) + ")"
            
            return {
                "status": "active",
                "plan": {
                    "decision": final_decision,
                    "reasoning": decision_obj.reasoning_markdown, 
                    "confidence": f"{decision_obj.confidence:.2%}",
                    "risk_level": decision_obj.risk_level
                }
            }
        except Exception as e:
            print(f"Error in run_cycle: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "plan": {
                    "decision": "ERROR",
                    "reasoning": str(e),
                    "confidence": "LOW"
                }
            }

