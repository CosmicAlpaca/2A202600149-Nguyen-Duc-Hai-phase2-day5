from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import time
from dotenv import load_dotenv

from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.evaluation.benchmark import run_benchmark

load_dotenv()
settings = get_settings()

app = FastAPI(title="Research Lab Benchmarker")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str

def get_baseline_runner(q: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=q))
    llm = LLMClient(model_name=settings.gemini_model)
    sys_prompt = "You are a helpful assistant. Research and answer the query."
    response = llm.complete(sys_prompt, q)
    state.final_answer = response.content
    # Fake some token info if not available, but response should have them
    return state

def get_multi_agent_runner(q: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=q))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)

@app.post("/api/research/baseline")
async def run_baseline(req: QueryRequest):
    try:
        final_state, metrics = run_benchmark("baseline", req.query, get_baseline_runner)
        # Log results
        with open("web_logs.jsonl", "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps({"type": "baseline", "query": req.query, "metrics": metrics.model_dump()}) + "\n")
        return {
            "answer": final_state.final_answer,
            "metrics": metrics.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research/multi-agent")
async def run_multi_agent(req: QueryRequest):
    try:
        final_state, metrics = run_benchmark("multi-agent", req.query, get_multi_agent_runner)
        # Log results
        with open("web_logs.jsonl", "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps({"type": "multi-agent", "query": req.query, "metrics": metrics.model_dump()}) + "\n")
        return {
            "answer": final_state.final_answer,
            "metrics": metrics.model_dump(),
            "sources": [{"title": s.title, "url": s.url} for s in final_state.sources]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
