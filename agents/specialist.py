import logging
from typing import List, Dict, Any
from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class SpecialistAgent:
    """The Specialist Agent synthesizes high-quality answers with citations."""
    
    def __init__(self):
        self.llm_provider = Config.LLM_PROVIDER
        self.model_name = Config.MODEL_NAME
        
        # Initialize LLM client based on provider
        if self.llm_provider == "ollama":
            import ollama
            self.base_url = Config.OLLAMA_BASE_URL
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def synthesize(self, question: str, retrieved_context: Dict[str, Any] = None) -> str:
        """
        Synthesize a high-quality answer based on the question and retrieved context.
        
        Args:
            question: The original user question
            retrieved_context: Retrieved document snippets (optional)
        
        Returns:
            Formatted answer with citations
        """
        logger.info(f"Specialist synthesizing answer for: {question}")
        
        # Prepare the prompt with context
        prompt = self._build_prompt(question, retrieved_context)
        
        # Call LLM
        response = self._call_llm(prompt)
        
        # Format the response with proper citations
        formatted_response = self._format_response(response, retrieved_context)
        
        logger.info("Answer synthesis complete")
        return formatted_response
    
    def _build_prompt(self, question: str, context: Dict[str, Any] = None) -> str:
        """Build the prompt for the Specialist Agent."""
        
        system_prompt = """You are a meticulous technical analyst. Your job is to synthesize a clear, concise answer based only on the provided context and the user's question.

RULES:
1. Answer ONLY from the provided context
2. Always cite sources using inline citations [1], [2], etc.
3. If insufficient information, state this explicitly
4. Be precise with numbers, dates, and technical terms
5. Organize your answer with clear structure

ANSWER FORMAT:
[Your detailed answer with inline citations]

---
Sources Referenced:
[1] filename.md (Section: Section Name)
[2] filename.md (Section: Section Name)"""

        if context and context.get("snippets"):
            # Format the retrieved snippets
            context_text = "RETRIEVED CONTEXT:\n\n"
            for i, snippet in enumerate(context["snippets"], 1):
                source_info = f"[{i}] {snippet['source']}"
                if snippet.get("section"):
                    source_info += f" (Section: {snippet['section']})"
                
                context_text += f"{source_info}\n{snippet['content']}\n\n"
            
            user_prompt = f"User Question: {question}\n\n{context_text}\n\nBased on the provided context, please answer the user's question."
        else:
            user_prompt = f"User Question: {question}\n\nNo specific context was provided. Please answer based on general knowledge."
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API."""
        try:
            if self.llm_provider == "ollama":
                return self._call_ollama(prompt)
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        import ollama
        
        client = ollama.Client(host=self.base_url)
        
        try:
            response = client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def _format_response(self, response: str, context: Dict[str, Any] = None) -> str:
        """Format the response with proper source citations."""
        
        if not context or not context.get("snippets"):
            # No context to cite, return response as-is
            return response
        
        # Extract sources from context
        sources = []
        for i, snippet in enumerate(context["snippets"], 1):
            source_info = f"[{i}] {snippet['source']}"
            if snippet.get("section"):
                source_info += f" (Section: {snippet['section']})"
            sources.append(source_info)
        
        # Check if response already has source citations
        if "Sources Referenced:" not in response:
            # Add source citations at the end
            response += f"\n\n---\nSources Referenced:\n" + "\n".join(sources)
        
        return response.strip()
