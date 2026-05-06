"""LangGraph workflow skeleton."""

from langgraph.graph import StateGraph, START, END

from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph."""

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()

    def build(self) -> object:
        """Create a LangGraph graph."""
        workflow = StateGraph(ResearchState)
        
        workflow.add_node("supervisor", self.supervisor.run)
        workflow.add_node("researcher", self.researcher.run)
        workflow.add_node("analyst", self.analyst.run)
        workflow.add_node("writer", self.writer.run)
        
        def route(state: ResearchState) -> str:
            if not state.route_history:
                return END
            last_route = state.route_history[-1]
            if last_route == "done":
                return END
            return last_route

        workflow.add_edge(START, "supervisor")
        workflow.add_conditional_edges("supervisor", route, {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            END: END
        })
        
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")

        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        app = self.build()
        
        config = {}
        # Setup Langfuse if keys are present
        import os
        if os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"):
            try:
                from langfuse.callback import CallbackHandler
                langfuse_handler = CallbackHandler()
                config["callbacks"] = [langfuse_handler]
            except ImportError:
                pass
                
        result = app.invoke(state, config=config)
        # Ensure we return a ResearchState object, as LangGraph might return a dict
        if isinstance(result, dict):
            return ResearchState(**result)
        return result
