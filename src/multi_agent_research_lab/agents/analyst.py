"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"
    
    def __init__(self):
        self.llm = LLMClient(model_name=get_settings().gemini_model)

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        system_prompt = "You are a critical analyst. Turn the research notes into structured insights. Extract key claims, compare viewpoints, and flag weak evidence."
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\nPlease generate analysis notes."
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.analysis_notes = response.content
        
        state.agent_results.append(AgentResult(
            agent=self.name,
            content="Created analysis notes.",
            metadata={"input_tokens": response.input_tokens, "output_tokens": response.output_tokens}
        ))
        
        return state
