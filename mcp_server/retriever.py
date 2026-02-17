import os
import re
from typing import List, Dict, Any
from pathlib import Path
from config import Config
from mcp_server.models import DocumentSnippet

class DocumentRetriever:
    def __init__(self, knowledge_base_path: str = None):
        self.knowledge_base_path = knowledge_base_path or Config.KNOWLEDGE_BASE_PATH
        self.documents = self._load_documents()
    
    def _load_documents(self) -> Dict[str, str]:
        """Load all markdown documents from knowledge base."""
        documents = {}
        kb_path = Path(self.knowledge_base_path)
        
        if not kb_path.exists():
            print(f"Knowledge base path not found: {self.knowledge_base_path}")
            return documents
        
        for file_path in kb_path.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents[file_path.name] = f.read()
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(documents)} documents from knowledge base")
        return documents
    
    def search(self, query: str) -> List[DocumentSnippet]:
        """Search for relevant document snippets using keyword matching."""
        snippets = []
        query_terms = query.lower().split()
        
        for filename, content in self.documents.items():
            # Split content into sections by headings
            sections = self._split_into_sections(content)
            
            for section_name, section_content in sections:
                # Calculate relevance score based on keyword matches
                score = self._calculate_relevance(query_terms, section_content)
                
                if score > 0:  # Only include sections with matches
                    snippet = DocumentSnippet(
                        content=section_content.strip(),
                        source=filename,
                        section=section_name
                    )
                    snippets.append(snippet)
        
        # Sort by relevance score (descending)
        snippets.sort(key=lambda x: self._calculate_relevance(query_terms, x.content), reverse=True)
        
        # Return top 5 most relevant snippets
        return snippets[:5]
    
    def _split_into_sections(self, content: str) -> List[tuple]:
        """Split document content into sections based on markdown headings."""
        sections = []
        lines = content.split('\n')
        current_section = ""
        current_heading = "Introduction"
        
        for line in lines:
            if line.startswith('#'):
                # Save previous section
                if current_section.strip():
                    sections.append((current_heading, current_section.strip()))
                
                # Start new section
                current_heading = line.strip('#').strip()
                current_section = ""
            else:
                current_section += line + "\n"
        
        # Add last section
        if current_section.strip():
            sections.append((current_heading, current_section.strip()))
        
        return sections
    
    def _calculate_relevance(self, query_terms: List[str], content: str) -> int:
        """Calculate relevance score based on keyword frequency."""
        content_lower = content.lower()
        score = 0
        
        for term in query_terms:
            # Count occurrences of the term
            term_count = content_lower.count(term)
            score += term_count
            
            # Bonus for exact phrase matches
            if ' '.join(query_terms) in content_lower:
                score += 5
        
        return score
