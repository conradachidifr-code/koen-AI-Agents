from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent import agent
from database import db_manager

app = FastAPI(title="DBuddy - Your Database Buddy")


class QueryRequest(BaseModel):
    """Request model for chat queries"""

    query: str


class QueryResponse(BaseModel):
    """Response model for chat queries"""

    success: bool
    response: str = None
    sql_query: str = None
    error: str = None


@app.get("/")
async def read_root():
    """Serve the main chat interface"""
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_connected = db_manager.test_connection()
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": "connected" if db_connected else "disconnected",
    }


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query

    Args:
        request: QueryRequest containing the user's question

    Returns:
        QueryResponse with the answer and SQL query
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = agent.process_query(request.query)

    if result["success"]:
        return QueryResponse(
            success=True,
            response=result["response"],
            sql_query=result["sql_query"],
        )
    else:
        return QueryResponse(
            success=False,
            error=result["error"],
            sql_query=result.get("sql_query"),
        )


@app.get("/api/schema")
async def get_schema():
    """Get the database schema"""
    try:
        schema = db_manager.get_schema()
        return {"success": True, "schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
