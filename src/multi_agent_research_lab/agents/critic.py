"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"
    
    def __init__(self):
        self.llm = LLMClient(model_name=get_settings().gemini_model)

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""
        if not state.final_answer:
            return state
            
        system_prompt = "You are a critic. Fact-check the final answer against the research notes. Give a short summary of issues found or confirm it is accurate."
        user_prompt = f"Research Notes:\n{state.research_notes}\n\nFinal Answer:\n{state.final_answer}\n\nPlease verify."
        
        response = self.llm.complete(system_prompt, user_prompt)
        
        state.agent_results.append(AgentResult(
            agent=self.name,
            content=f"Critic feedback: {response.content}"
        ))
        
        return state
