"""Supervisor / router skeleton."""

import os
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        # A simple state-machine router logic since it ensures sequence
        next_route = "done"
        if not state.research_notes:
            next_route = "researcher"
        elif not state.analysis_notes:
            next_route = "analyst"
        elif not state.final_answer:
            next_route = "writer"
            
        state.record_route(next_route)
        
        state.agent_results.append(AgentResult(
            agent=self.name,
            content=f"Routed to {next_route}"
        ))
        
        return state
