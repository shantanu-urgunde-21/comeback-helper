"""POST /api/query — hybrid RAG question answering."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()


class QueryRequest(BaseModel):
    prompt: str
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    course: Optional[str] = None
    use_graph: bool = True


@router.post("/api/query")
async def query_knowledge_base(payload: QueryRequest, request: Request):
    """
    Asks mathematical questions to the hybrid RAG engine with
    configurable retrieval parameters.
    """
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Query prompt cannot be empty.")

    try:
        engine = request.app.state.query_engine
        answer = engine.query(
            prompt=payload.prompt,
            top_k=payload.top_k,
            temperature=payload.temperature,
            course=payload.course,
            use_graph=payload.use_graph,
        )
        return JSONResponse({"status": "success", "answer": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
