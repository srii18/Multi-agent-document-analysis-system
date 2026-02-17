import requests
import json
import logging
from typing import Optional, Dict, Any, Tuple
from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class ManagerAgent:
    """The Manager Agent decides if document retrieval is needed and orchestrates the workflow."""
    
    def __init__(self):
        self.llm_provider = Config.LLM_PROVIDER
        self.model_name = Config.MODEL_NAME
        self.mcp_server_url = Config.MCP_SERVER_URL
        
        # Initialize LLM client based on provider
        if self.llm_provider == "ollama":
            import ollama
            self.llm_client = ollama.Client
            self.base_url = Config.OLLAMA_BASE_URL
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def decide(self, user_question: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Decide if document retrieval is needed and execute if necessary.
        
        Returns:
            Tuple of (tool_needed, search_query, retrieved_context)
        """
        logger.info(f"Manager processing question: {user_question}")
        
        # Step 1: Use LLM to decide if tool is needed
        decision = self._make_tool_decision(user_question)
        logger.info(f"Tool decision: {decision}")
        
        if decision["use_tool"]:
            # Step 2: Extract search query and call MCP server
            search_query = decision["query"]
            logger.info(f"Searching with query: {search_query}")
            
            retrieved_context = self._call_mcp_server(search_query)
            return True, search_query, retrieved_context
        else:
            logger.info("No tool needed, proceeding without context")
            return False, None, None
    
    def _make_tool_decision(self, question: str) -> Dict[str, Any]:
        """Use LLM to decide if document_retriever tool is needed."""
        
        system_prompt = """You are an orchestrator. Determine if the user's question requires our internal knowledge base.

USE document_retriever for:
- Questions about OUR systems/performance/plans
- Queries needing factual internal data
- Comparative analysis requiring concrete data
- Questions about metrics, architecture, or roadmap

DON'T USE for:
- General knowledge questions
- Definitional/conceptual questions
- Questions about external topics

Format your response as JSON:
{
  "use_tool": true/false,
  "query": "search query if tool needed",
  "reason": "explanation for decision"
}

Examples:
User: "How does Q3 performance compare to Q2?"
Response: {"use_tool": true, "query": "Q3 performance metrics Q2 comparison", "reason": "Needs internal performance data"}

User: "What is machine learning?"
Response: {"use_tool": false, "query": "", "reason": "General knowledge question"}"""

        try:
            if self.llm_provider == "ollama":
                response = self._call_ollama(question, system_prompt)
                # Parse JSON response
                decision = json.loads(response.strip())
                return decision
        except Exception as e:
            logger.error(f"Error in tool decision: {e}")
            # Default to using tool if there's an error
            return {
                "use_tool": True,
                "query": question,
                "reason": "Error in decision making, defaulting to tool use"
            }
    
    def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Call Ollama API."""
        import ollama
        
        client = ollama.Client(host=self.base_url)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = client.chat(
                model=self.model_name,
                messages=messages
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def _call_mcp_server(self, query: str) -> Dict[str, Any]:
        """Call the MCP server to retrieve documents."""
        url = f"{self.mcp_server_url}/mcp/v1/tools/execute"
        
        payload = {
            "name": "document_retriever",
            "arguments": {"query": query}
        }
        
        try:
            logger.info(f"Calling MCP server: {url}")
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Retrieved {len(result['result']['snippets'])} snippets")
            return result["result"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP server error: {e}")
            raise Exception(f"Failed to call MCP server: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing MCP response: {e}")
            raise
