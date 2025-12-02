# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG (Retrieval-Augmented Generation) system that uses BGE-M3 embeddings with ChromaDB vector storage and Groq/DeepSeek as the LLM. The system processes markdown documents, generates embeddings, stores them in ChromaDB, and enables semantic search to answer user queries.

**Key features:**
- Document ingestion from markdown files
- BGE-M3 embeddings (1024 dimensions)
- ChromaDB vector database for storage
- Groq API (ultra-fast, recommended) or DeepSeek API for LLM
- Interactive chatbot with conversation history
- CLI for queries and document management

## Common Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (only LLM API key needed)
cp .env.example .env
# Then edit .env with your Groq or DeepSeek API key
```

### Document Ingestion
```bash
# Basic ingestion (processes .md files from data/docs/)
python src/main.py --ingest

# Ingestion with chunking (splits large documents)
python src/main.py --ingest --chunk

# Force re-processing of existing documents
python src/main.py --ingest --force

# Use DeepSeek instead of Groq
python src/main.py --ingest --llm-provider deepseek
```

### Querying
```bash
# Single query
python src/main.py --query "your question"

# Query with sources displayed
python src/main.py --query "your question" --show-sources

# Interactive mode (default when no flags provided)
python src/main.py

# Interactive chatbot with history (recommended)
python src/chat.py

# Advanced query options
python src/main.py --query "your question" --top-k 5 --temperature 0.7

# Use DeepSeek instead of Groq
python src/main.py --query "your question" --llm-provider deepseek
python src/chat.py --llm-provider deepseek
```

### System Management
```bash
# View system statistics
python src/main.py --stats

# Clear database
python src/main.py --reset

# Test individual components
python src/embeddings/embedder.py
python src/llm/groq_client.py
python src/llm/deepseek_client.py
python src/rag/retriever.py
```

## Architecture

### Core Components

**RAGPipeline** (`src/rag/rag_pipeline.py`)
- Main orchestrator for the entire RAG system
- Initializes all components (embedder, ChromaDB, LLM)
- Handles both ingestion and query workflows
- LLM provider can be switched between "groq" and "deepseek"

**Embedder** (`src/embeddings/embedder.py`)
- Uses BGE-M3 model from sentence-transformers
- Generates 1024-dimensional float32 embeddings
- Critical methods:
  - `generate_embedding(text)`: Creates embedding for single text
  - `embedding_to_bytes()`: Converts numpy array to bytes
  - `bytes_to_embedding()`: Converts bytes back to numpy array

**ChromaVectorStore** (`src/database/chroma_vector_store.py`)
- Vector database designed specifically for embeddings
- Automatic persistence to disk (`data/chroma/`)
- Uses HNSW algorithm with cosine similarity
- Metadata stored with vectors in ChromaDB
- Zero configuration required
- Key methods:
  - `add_document()`: Adds document with embedding
  - `get_all_documents()`: Retrieves all documents
  - `search_similar()`: Finds similar documents using HNSW
  - `delete_all_documents()`: Clears the collection

**DocumentRepository** (`src/database/repository.py`)
- CRUD operations for documents with ChromaDB
- Abstraction layer over ChromaVectorStore
- Key methods: `insert_document()`, `get_all_documents()`, `document_exists()`, `count_documents()`

**DocumentRetriever** (`src/rag/retriever.py`)
- Semantic search using cosine similarity
- Uses ChromaDB's built-in `.query()` method with HNSW for fast search
- Returns top-k most relevant documents with similarity scores

**LLM Clients**
- `GroqClient` (`src/llm/groq_client.py`): Ultra-fast responses using Llama 3.3 70B
- `DeepSeekClient` (`src/llm/deepseek_client.py`): Alternative with good quality
- Both implement `generate_response()` for RAG and `simple_chat()` for basic chat

**RAGChatbot** (`src/chatbot/chatbot.py`)
- Wraps RAGPipeline with conversation history
- Maintains last N messages (default: 5)
- Supports both RAG-based and history-only chat modes

### Data Flow

**Ingestion Pipeline:**
1. Load .md files from `data/docs/`
2. Clean/preprocess text
3. Generate BGE-M3 embeddings (1024-dim float32)
4. Convert embedding to list for ChromaDB
5. Add to ChromaDB collection with metadata (filename, content)

**Query Pipeline:**
1. Convert user question to embedding
2. Use ChromaDB's `.query()` method with HNSW algorithm
3. Retrieve top-k most similar documents with cosine similarity scores
4. Build RAG prompt with context documents
5. Send to Groq/DeepSeek API
6. Return response with sources

### Critical Implementation Details

**Embedding Storage/Retrieval (ChromaDB):**
```python
# Store
embedding_list = embedding.astype('float32').tolist()
collection.add(embeddings=[embedding_list], documents=[content],
               metadatas=[{"filename": filename}], ids=[doc_id])

# Search
query_list = query_embedding.astype('float32').tolist()
results = collection.query(query_embeddings=[query_list], n_results=top_k)
# Returns: results['distances'], results['documents'], results['metadatas']
```

**RAG Prompt Pattern:**
Both LLM clients use strict instructions to only answer from context:
```python
system_prompt = "Answer ONLY based on provided context. Don't use external knowledge."
user_prompt = f"Context:\n{documents}\n\nQuestion:\n{query}"
```

**LLM Provider Selection:**
The system defaults to Groq but can use DeepSeek:
```python
# In RAGPipeline.__init__() or RAGChatbot.__init__()
RAGPipeline(llm_provider="groq")    # Default: ultra-fast
RAGPipeline(llm_provider="deepseek")  # Alternative

# CLI flags
python src/main.py --llm-provider deepseek
python src/chat.py --llm-provider groq
```

**Conversation History:**
RAGChatbot maintains history as list of tuples:
```python
conversation_history = [(user_msg1, bot_msg1), (user_msg2, bot_msg2), ...]
# Automatically limited to max_history entries
```

## Environment Variables

Required in `.env`:
```
# LLM API (at least one required, both can be configured)
GROQ_API_KEY=your_groq_api_key_here        # Recommended: ultra-fast
DEEPSEEK_API_KEY=your_deepseek_api_key_here  # Alternative
```

**Notes**:
- **ChromaDB**: No database credentials needed. Data automatically stored in `data/chroma/`
- **No SQL Server or ODBC drivers required**

## Key Files

- `src/main.py`: CLI entry point for ingestion/queries
- `src/chat.py`: Interactive chatbot entry point
- `src/rag/rag_pipeline.py`: Main orchestrator
- `src/chatbot/chatbot.py`: Chatbot with conversation history
- `src/embeddings/embedder.py`: BGE-M3 embedding generation
- `src/database/repository.py`: CRUD operations abstraction
- `src/database/chroma_vector_store.py`: ChromaDB backend
- `src/llm/groq_client.py`: Groq API client (recommended, ultra-fast)
- `src/llm/deepseek_client.py`: DeepSeek API client
- `src/rag/retriever.py`: Semantic search with cosine similarity

## Error Handling Notes

All modules handle common errors:
- **ChromaDB issues**: Delete `data/chroma/` and re-run ingestion if corruption occurs
- **Missing API keys**: Verify `.env` file exists and has correct keys for chosen LLM provider
- **Empty storage**: Run `--ingest` first before queries
- **Model download**: BGE-M3 is ~2GB, downloads to `~/.cache/huggingface/` on first run

## ChromaDB Details

**Storage Location**: `data/chroma/`
**Collection Name**: `documents`
**Similarity Metric**: Cosine similarity
**Index Type**: HNSW (Hierarchical Navigable Small World)
**Persistence**: Automatic to disk

**Why ChromaDB?**
- Zero configuration required
- Designed specifically for embeddings
- Fast search with HNSW algorithm
- Automatic persistence
- Metadata integrated with vectors
- Excellent for both development and production
