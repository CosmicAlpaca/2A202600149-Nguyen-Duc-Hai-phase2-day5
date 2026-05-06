"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    from dotenv import load_dotenv
    load_dotenv()
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    from multi_agent_research_lab.evaluation.report import render_markdown_report
    import os
    
    def single_agent_runner(q: str) -> ResearchState:
        settings = get_settings()
        llm = LLMClient(model_name=settings.gemini_model)
        sys_prompt = "You are a helpful assistant. Research and answer the query."
        response = llm.complete(sys_prompt, q)
        state.final_answer = response.content
        return state
        
    final_state, metrics = run_benchmark("baseline", query, single_agent_runner)
    
    console.print(Panel.fit(final_state.final_answer or "", title="Single-Agent Baseline"))
    console.print(render_markdown_report([metrics]))

@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    from multi_agent_research_lab.evaluation.report import render_markdown_report
    
    def multi_agent_runner(q: str) -> ResearchState:
        return workflow.run(state)
        
    try:
        final_state, metrics = run_benchmark("multi-agent", query, multi_agent_runner)
    except Exception as exc:
        console.print(Panel.fit(str(exc), title="Error", style="red"))
        raise typer.Exit(code=2) from exc
        
    console.print(Panel.fit(final_state.final_answer or "No answer", title="Multi-Agent Result"))
    console.print(render_markdown_report([metrics]))

if __name__ == "__main__":
    app()
