from pydantic import BaseModel, Field
from typing import List, Literal

class OrchestratorDecision(BaseModel):
    decision: str = Field(..., description="The final action to take. Should be 'IGNORE' if benign, or list the agents that found issues, or 'MANUAL_REVIEW' if suspicious.")
    reasoning_markdown: str = Field(..., description="The full Markdown defense plan and reasoning.")
    confidence: float = Field(..., description="Confidence in the orchestration result (0.0 to 1.0)")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Overall risk level of the incident.")
