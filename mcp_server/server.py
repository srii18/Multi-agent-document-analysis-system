import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Allow running this file directly (python mcp_server/server.py) from repo root.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from config import Config
from mcp_server.models import (
    ToolsListResponse, ToolSpecification, ToolExecutionRequest, 
    ToolExecutionResponse, ToolResult, DocumentSnippet
)
from mcp_server.retriever import DocumentRetriever

app = FastAPI(title="MCP Document Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize document retriever
retriever = DocumentRetriever()

@app.get("/mcp/v1/tools", response_model=ToolsListResponse)
async def list_tools():
    """Return the specification of available tools."""
    tools = [
        ToolSpecification(
            name="document_retriever",
            description="Retrieves relevant text snippets from the knowledge base based on a search query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for document retrieval"
                    }
                },
                "required": ["query"]
            }
        )
    ]
    
    return ToolsListResponse(tools=tools)

@app.post("/mcp/v1/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute a tool and return the result."""
    
    if request.name != "document_retriever":
        raise HTTPException(status_code=404, detail=f"Tool '{request.name}' not found")
    
    if "query" not in request.arguments:
        raise HTTPException(status_code=400, detail="Missing required argument: query")
    
    try:
        # Perform document search
        snippets = retriever.search(request.arguments["query"])
        
        # Convert to response format
        tool_result = ToolResult(snippets=snippets)
        
        return ToolExecutionResponse(result=tool_result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "documents_loaded": len(retriever.documents)}

@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "MCP Document Server",
        "version": "1.0.0",
        "description": "Model Context Protocol server for document retrieval"
    }

if __name__ == "__main__":
    print(f"Starting MCP Server on {Config.MCP_SERVER_HOST}:{Config.MCP_SERVER_PORT}")
    uvicorn.run(
        "mcp_server.server:app",
        host=Config.MCP_SERVER_HOST,
        port=Config.MCP_SERVER_PORT,
        reload=True
    )
