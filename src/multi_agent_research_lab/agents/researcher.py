"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"
    
    def __init__(self):
        self.search_client = SearchClient()
        self.llm = LLMClient(model_name=get_settings().gemini_fast_model)

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        sources = self.search_client.search(state.request.query, max_results=state.request.max_sources)
        state.sources = sources
        
        system_prompt = "You are a researcher. Given the search sources, write concise research notes focusing on facts relevant to the query."
        sources_text = "\n\n".join([f"Title: {s.title}\nURL: {s.url}\nSnippet: {s.snippet}" for s in sources])
        user_prompt = f"Query: {state.request.query}\n\nSources:\n{sources_text}\n\nPlease generate research notes."
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.research_notes = response.content
        
        state.agent_results.append(AgentResult(
            agent=self.name,
            content=f"Found {len(sources)} sources and created notes.",
            metadata={"input_tokens": response.input_tokens, "output_tokens": response.output_tokens}
        ))
        
        return state
