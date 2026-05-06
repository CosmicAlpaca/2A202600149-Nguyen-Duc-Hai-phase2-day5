"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    total_input_tokens = 0
    total_output_tokens = 0
    for res in state.agent_results:
        total_input_tokens += res.metadata.get("input_tokens") or 0
        total_output_tokens += res.metadata.get("output_tokens") or 0
    
    # Heuristic cost for Gemini 1.5 Flash (approx)
    # $0.075 / 1M input, $0.30 / 1M output
    cost = (total_input_tokens * 0.075 / 1_000_000) + (total_output_tokens * 0.30 / 1_000_000)
    
    # Quality score heuristic
    quality_score = 0.0
    if state.final_answer:
        length = len(state.final_answer)
        if length > 2000: quality_score += 4.0
        elif length > 1000: quality_score += 2.0
        
        if "GraphRAG" in state.final_answer: quality_score += 2.0
        if "Research" in state.final_answer or "Sources" in state.final_answer: quality_score += 1.0
        if len(state.sources) > 0: quality_score += 3.0
    
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=cost,
        quality_score=min(10.0, quality_score),
        total_tokens=total_input_tokens + total_output_tokens
    )
    return state, metrics
