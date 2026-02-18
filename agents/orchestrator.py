#!/usr/bin/env python3
"""
Multi-Agent Document Analysis System - Main Orchestrator

This script orchestrates the interaction between the Manager Agent and Specialist Agent
to answer user questions using the MCP document retrieval server.
"""

import os
import sys
import argparse
import logging
import time
from typing import Optional

# Allow running this file directly (python agents/orchestrator.py) from repo root.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from config import Config
from agents.manager import ManagerAgent
from agents.specialist import SpecialistAgent

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentAnalysisOrchestrator:
    """Main orchestrator for the multi-agent document analysis system."""
    
    def __init__(self):
        self.manager = ManagerAgent()
        self.specialist = SpecialistAgent()
        logger.info("Document Analysis Orchestrator initialized")
    
    def process_question(self, question: str) -> str:
        """
        Process a user question through the multi-agent workflow.
        
        Args:
            question: The user's question
        
        Returns:
            The final answer with citations
        """
        start_time = time.time()
        logger.info(f"Processing question: {question}")
        
        try:
            # Step 1: Manager decides if document retrieval is needed
            tool_needed, search_query, retrieved_context = self.manager.decide(question)
            
            # Step 2: Specialist synthesizes the answer
            if tool_needed and retrieved_context:
                logger.info(f"Using retrieved context with {len(retrieved_context.get('snippets', []))} snippets")
                answer = self.specialist.synthesize(question, retrieved_context)
            else:
                logger.info("Proceeding without retrieved context")
                answer = self.specialist.synthesize(question)
            
            # Log timing
            processing_time = time.time() - start_time
            logger.info(f"Question processed in {processing_time:.2f} seconds")
            
            return answer
            
        except Exception as e:
            error_msg = f"Error processing question: {str(e)}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error while processing your question: {error_msg}"
    
    def interactive_mode(self):
        """Run the orchestrator in interactive mode."""
        print("Multi-Agent Document Analysis System")
        print("Type 'quit' or 'exit' to end the session")
        print("-" * 50)
        
        while True:
            try:
                question = input("\nYour question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not question:
                    print("Please enter a question.")
                    continue
                
                print("\nProcessing...")
                answer = self.process_question(question)
                print(f"\nAnswer:\n{answer}")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Document Analysis System"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Single question to process (non-interactive mode)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = DocumentAnalysisOrchestrator()
    
    if args.query:
        # Single query mode
        answer = orchestrator.process_question(args.query)
        print(answer)
    elif args.interactive:
        # Interactive mode
        orchestrator.interactive_mode()
    else:
        # Default to interactive mode
        print("No query provided. Starting interactive mode...")
        orchestrator.interactive_mode()

if __name__ == "__main__":
    main()
