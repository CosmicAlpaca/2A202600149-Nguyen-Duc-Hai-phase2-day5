"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"
    
    def __init__(self):
        # We will use fast model from settings
        self.llm = LLMClient(model_name=get_settings().gemini_fast_model)

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        system_prompt = f"You are an expert writer. Synthesize a clear response for the audience: {state.request.audience}. Include citations to sources."
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\nAnalysis Notes:\n{state.analysis_notes}\n\nPlease generate the final answer."
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        
        state.agent_results.append(AgentResult(
            agent=self.name,
            content="Created final answer.",
            metadata={"input_tokens": response.input_tokens, "output_tokens": response.output_tokens}
        ))
        
        return state
