# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) system that uses BGE-M3 embeddings, SQL Server for vector storage, and DeepSeek API as the LLM. The system processes markdown documents, generates embeddings, stores them in SQL Server, and enables semantic search to answer user queries.

## Project Structure

```
rag_system/
├── data/
│   └── docs/              # Input .md files for ingestion
├── src/
│   ├── embeddings/
│   │   └── embedder.py    # BGE-M3 embedding generation
│   ├── database/
│   │   ├── connection.py  # SQL Server connection management
│   │   └── repository.py  # Database operations (CRUD)
│   ├── ingestion/
│   │   └── ingest_docs.py # Document loading and processing
│   ├── rag/
│   │   ├── retriever.py   # Semantic search with cosine similarity
│   │   └── rag_pipeline.py # Complete RAG workflow
│   ├── llm/
│   │   └── deepseek_client.py # DeepSeek API integration
│   └── main.py            # Entry point
├── .env                   # Environment variables (not committed)
├── requirements.txt
└── README.md
```

## Environment Setup

1. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate on Windows
   ```

2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables** (`.env`):
   ```
   DB_HOST=
   DB_PORT=
   DB_NAME=
   DB_USER=
   DB_PASSWORD=
   DEEPSEEK_API_KEY=
   ```

## Database Schema

SQL Server table structure:

```sql
CREATE TABLE Documents (
    id INT PRIMARY KEY IDENTITY(1,1),
    filename NVARCHAR(255),
    content NVARCHAR(MAX),
    embedding VARBINARY(MAX)
);
```

**Important**: Embeddings are numpy float32 arrays converted to VARBINARY(MAX) for storage. Use numpy's `tobytes()` and `frombuffer()` for conversion.

## Development Commands

### Running the System

- **Ingest documents**: Process .md files and store embeddings
  ```bash
  python src/main.py --ingest
  ```

- **Query the system**: Ask questions against the knowledge base
  ```bash
  python src/main.py --query "your question here"
  ```

### Testing Individual Components

- **Test database connection**:
  ```bash
  python src/database/connection.py
  ```

- **Test embeddings**:
  ```bash
  python src/embeddings/embedder.py
  ```

- **Test DeepSeek client**:
  ```bash
  python src/llm/deepseek_client.py
  ```

## Architecture Details

### RAG Pipeline Flow

1. **Ingestion Phase**:
   - Load .md files from `data/docs/`
   - Clean and preprocess text
   - Generate embeddings using BGE-M3 (`sentence-transformers`)
   - Convert float32 embeddings to VARBINARY
   - Store in SQL Server

2. **Query Phase**:
   - Convert user question to embedding
   - Retrieve ALL documents from SQL Server
   - Calculate cosine similarity in Python (not in SQL)
   - Select top-k most relevant documents
   - Build RAG prompt with context
   - Send to DeepSeek API
   - Return clean response

### Key Technical Decisions

- **Database**: SQL Server with pyodbc or SQLAlchemy (mssql+pyodbc)
- **Embeddings**: BGE-M3 via sentence-transformers
- **Similarity**: Cosine similarity calculated in Python after fetching all rows
- **LLM**: DeepSeek API (not a local model)

### Critical Implementation Notes

1. **Embedding Storage**: Convert numpy arrays before SQL insert:
   ```python
   embedding_bytes = embedding_array.astype('float32').tobytes()
   ```

2. **Embedding Retrieval**: Convert back from VARBINARY:
   ```python
   embedding_array = np.frombuffer(embedding_bytes, dtype='float32')
   ```

3. **RAG Prompt Template**: DeepSeek should receive strict instructions:
   ```
   Usa SOLO esta información de contexto para responder:
   [documentos recuperados]

   Pregunta del usuario:
   [query]
   ```

4. **Error Handling**: All modules should handle:
   - Database connection failures
   - Missing .env variables
   - API rate limits/errors
   - Invalid file formats
   - Empty query results

## Dependencies

Core libraries (see requirements.txt):
- `python-dotenv` - Environment variable management
- `sentence-transformers` - BGE-M3 embeddings
- `transformers`, `accelerate` - Transformer models support
- `pyodbc` - SQL Server connectivity
- `numpy`, `pandas` - Data processing
- `requests` - DeepSeek API calls
- `sqlalchemy` (optional) - ORM for database operations
