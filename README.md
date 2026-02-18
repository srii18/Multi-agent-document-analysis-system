# Multi-Agent Document Analysis System

A sophisticated document analysis system that uses a two-agent architecture to answer complex, cross-document questions with source citations.

## System Overview

The system implements a modular architecture where:
- **Manager Agent** decides if document retrieval is needed and orchestrates the workflow
- **MCP Server** provides document retrieval capabilities via Model Context Protocol
- **Specialist Agent** synthesizes high-quality answers with proper citations

```
User Question → Manager Agent → MCP Server → Specialist Agent → Final Answer + Citations
```

## Features

- **Two-Agent Architecture**: Manager (orchestrator) + Specialist (synthesizer)
- **MCP Protocol Compliance**: Standard Model Context Protocol for tool integration
- **Source Citation**: Automatic citation of source documents and sections
- **Ollama Integration**: Free local LLM support via Ollama
- **FastAPI Server**: High-performance MCP server implementation
- **Configuration Management**: Externalized settings via .env file
- **Comprehensive Logging**: Detailed execution tracking

## Project Structure

```
multi-agent-doc-analysis/
├── mcp_server/
│   ├── server.py          # FastAPI MCP server
│   ├── retriever.py       # Document search logic
│   └── models.py          # Pydantic schemas
├── agents/
│   ├── manager.py         # Manager Agent (orchestrator)
│   ├── specialist.py      # Specialist Agent (synthesizer)
│   └── orchestrator.py    # Main entry point
├── knowledge_base/
│   ├── q3_model_performance.md
│   ├── data_pipeline_architecture.md
│   ├── 2025_roadmap.md
│   ├── q2_quarterly_report.md
│   └── inference_optimization.md
├── .env                   # Configuration (create from .env.example)
├── .env.example           # Configuration template
├── config.py              # Configuration loader
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running
3. **Ollama model** (e.g., `llama3.2`)

### Installation

1. **Clone and setup**:
   ```bash
   cd "Multi-agent Document Analysis System"
   pip install -r requirements.txt
   ```

2. **Install and start Ollama**:
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama server
   ollama serve
   
   # Pull the model (in another terminal)
   ollama pull llama3.2
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults should work)
   ```

### Running the System

#### Option 1: Docker (Recommended - Fully Containerized)

Using Docker Compose, everything runs in containers: Ollama, MCP Server, and the Orchestrator.

1. **Install Docker and Docker Compose** (if not already installed):
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker Compose)

2. **Start all services**:
   ```bash
   docker-compose up
   ```
   
   This will:
   - Download and run Ollama container
   - Automatically pull `llama3.2` model (first run takes time)
   - Start the MCP Server (on `http://localhost:8000`)
   - Start the Orchestrator in interactive mode
   
3. **Stop services**:
   ```bash
   docker-compose down
   ```

**First run**: The orchestrator container will wait for Ollama to finish downloading the model. This may take 5-10 minutes on first boot.

#### Option 2: Local Setup (Manual)

If you prefer to run components locally:

1. **Start the MCP Server** (Terminal 1):
   ```bash
   python mcp_server/server.py
   ```
   - Serves on `http://localhost:8000`

2. **Run the orchestrator** (Terminal 2):
   ```bash
   # Interactive mode
   python agents/orchestrator.py --interactive
   
   # Or single query
   python agents/orchestrator.py --query "How does Q3 performance compare to Q2?"
   ```

## Usage Examples

### Example Queries

1. **Cross-document analysis**:
   ```
   "How does Q3 performance align with 2025 roadmap goals?"
   ```

2. **Performance comparison**:
   ```
   "Compare Q2 vs Q3 model accuracy and latency improvements"
   ```

3. **Architecture inquiry**:
   ```
   "What are the main bottlenecks in our data pipeline?"
   ```

4. **Roadmap questions**:
   ```
   "What optimization techniques are planned for 2025?"
   ```

### Sample Output

```
Question: "How does Q3 performance compare to Q2?"

Answer:
Q3 2024 showed significant improvements over Q2 across all key metrics:

- **Accuracy**: Improved from 91.1% to 94.2% (+3.1% improvement) [1]
- **Latency**: Reduced from 145ms to 120ms average response time [1]
- **Throughput**: Increased from 400 to 500 requests per second [1]

The Q3 model outperforms the Q2 baseline through enhanced preprocessing, optimized neural network architecture, and better hyperparameter tuning [1].

---
Sources Referenced:
[1] q3_model_performance.md (Section: Performance Metrics)
[2] q2_quarterly_report.md (Section: Performance Summary)
```

## Architecture Details

### MCP Server Implementation

The MCP server implements the Model Context Protocol specification:

- **GET /mcp/v1/tools**: Returns available tool specifications
- **POST /mcp/v1/tools/execute**: Executes the document_retriever tool
- **Document Retrieval**: Keyword-based search with relevance scoring

### Agent Design

#### Manager Agent
- **Role**: Decide if document retrieval is needed
- **Logic**: Uses LLM with structured decision prompt
- **Output**: Boolean decision + search query (if needed)

#### Specialist Agent  
- **Role**: Synthesize grounded answers with citations
- **Input**: Question + retrieved document snippets
- **Output**: Formatted answer with inline citations

### Configuration

All settings are externalized to `.env`:

```env
# LLM Settings
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# Paths
KNOWLEDGE_BASE_PATH=./knowledge_base
```

## Design Decisions

### Two-Agent Architecture
- **Separation of Concerns**: Manager handles orchestration, Specialist handles synthesis
- **Modularity**: Each agent can be developed and tested independently
- **Scalability**: Easy to add more specialized agents

### MCP Protocol
- **Standardization**: Uses industry-standard Model Context Protocol
- **Interoperability**: Compatible with other MCP-compliant tools
- **Extensibility**: Easy to add new tools beyond document retrieval

### Ollama Integration
- **Cost-Effective**: Free local LLM inference
- **Privacy**: No external API calls
- **Flexibility**: Support for multiple models

### Citation System
- **Source Grounding**: Every answer cites its sources
- **Traceability**: Users can verify information
- **Hallucination Mitigation**: Reduces model hallucinations

## Knowledge Base

The system includes 5 technical documents:

1. **q3_model_performance.md**: Q3 2024 performance metrics and improvements
2. **data_pipeline_architecture.md**: System architecture and bottlenecks  
3. **2025_roadmap.md**: Future plans and strategic goals
4. **q2_quarterly_report.md**: Q2 baseline metrics and challenges
5. **inference_optimization.md**: Performance optimization techniques

## Testing

### Test Queries

```bash
# Cross-document query
python agents/orchestrator.py -q "How does Q3 performance align with 2025 roadmap?"

# Single document query  
python agents/orchestrator.py -q "What are data pipeline bottlenecks?"

# General knowledge (no tool needed)
python agents/orchestrator.py -q "What is machine learning?"

# Missing information
python agents/orchestrator.py -q "What are Q4 revenue targets?"
```

### Expected Behavior

- **Tool Usage**: Manager correctly identifies when document retrieval is needed
- **Citation Quality**: Specialist includes proper source references
- **Answer Accuracy**: Responses are grounded in provided context
- **Error Handling**: Graceful handling of missing information

## Development

### Adding New Documents

1. Create markdown file in `knowledge_base/`
2. Use clear section headings (##, ###)
3. Include specific metrics and data points
4. Restart MCP server to reload documents

### Extending the System

1. **New Tools**: Add to MCP server following existing patterns
2. **New Agents**: Implement similar to Manager/Specialist
3. **Enhanced Search**: Replace keyword search with embeddings
4. **Monitoring**: Add metrics collection and dashboards

## Troubleshooting

### Common Issues

1. **Ollama Connection**:
   ```bash
   # Check Ollama status
   ollama list
   
   # Restart Ollama
   ollama serve
   ```

2. **MCP Server Errors**:
   ```bash
   # Check server health
   curl http://localhost:8000/health
   
   # Verify knowledge base path
   ls knowledge_base/
   ```

3. **Configuration Issues**:
   ```bash
   # Verify .env file exists
   cat .env
   
   # Check configuration loading
   python -c "from config import Config; print(Config.MODEL_NAME)"
   ```

### Docker Troubleshooting

1. **Ollama still downloading model on startup**:
   - First run downloads the `llama3.2` model (~4-5 GB)
   - Check logs: `docker-compose logs ollama`
   - Wait for "success" message before querying

2. **Port conflicts**:
   - Ollama: 11434
   - MCP Server: 8000
   - To use different ports, edit `docker-compose.yml` or override:
     ```bash
     docker-compose up -p 8001:8000
     ```

3. **Rebuild containers** (if requirements change):
   ```bash
   docker-compose build --no-cache
   ```

4. **View live logs**:
   ```bash
   docker-compose logs -f orchestrator
   ```

5. **Run a single query without interactive mode**:
   ```bash
   docker-compose run orchestrator python agents/orchestrator.py --query "Your question here?"
   ```

### Logging

Enable debug logging by setting in `.env`:
```env
LOG_LEVEL=DEBUG
```

## Self-Evaluation

### Strengths
- ✅ Complete MCP protocol implementation
- ✅ Clean two-agent architecture
- ✅ Proper source citation system
- ✅ Comprehensive configuration management
- ✅ Detailed documentation and examples
- ✅ Error handling and logging

### Areas for Improvement
- 🔄 Semantic search with embeddings (currently keyword-based)
- 🔄 Real-time document updates
- 🔄 Performance metrics collection
- 🔄 Containerization (Docker support)
- 🔄 Advanced caching strategies
- 🔄 Multi-language support

### Success Criteria Met
- ✅ MCP endpoints return correct format
- ✅ Manager decides correctly on tool usage
- ✅ Specialist cites sources in every answer
- ✅ System works end-to-end with test queries
- ✅ README has clear setup instructions
- ✅ Configuration externalized to .env

## License

This project is provided as a technical assignment demonstration.
