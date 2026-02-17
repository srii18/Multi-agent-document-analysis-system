from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ToolInput(BaseModel):
    query: str = Field(..., description="Search query for document retrieval")

class DocumentSnippet(BaseModel):
    content: str = Field(..., description="Retrieved text snippet")
    source: str = Field(..., description="Source document filename")
    section: Optional[str] = Field(None, description="Section or heading from source")

class ToolResult(BaseModel):
    snippets: List[DocumentSnippet] = Field(..., description="List of relevant document snippets")

class ToolExecutionRequest(BaseModel):
    name: str = Field(..., description="Tool name to execute")
    arguments: Dict[str, Any] = Field(..., description="Tool arguments")

class ToolExecutionResponse(BaseModel):
    result: ToolResult

class ToolSpecification(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolsListResponse(BaseModel):
    tools: List[ToolSpecification]
