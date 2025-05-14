# Vector Store Service

This document describes the implementation of the vector store functionality as a separate service, similar to the Gemini processor implementation.

## Overview

The vector store service is a standalone microservice that encapsulates all vector store operations, including:
- Creating vector stores
- Processing documents (splitting, embedding, and storing)
- Searching for content in documents

The service is implemented using FastAPI and can be run independently from the main application.

## Components

### 1. Vector Store Service (`vector_store_service.py`)

A FastAPI application that provides endpoints for vector store operations:
- `/create_vector_store`: Creates an empty vector store at the specified path
- `/process_document`: Processes a document by splitting, embedding, and storing it
- `/search`: Searches for content in a specific document using an environment variable for the storage path
- `/search_with_path`: Searches for content in a specific document with a specified storage path

### 2. Vector Store Client (`vector_store_client.py`)

A client class that interacts with the Vector Store Service:
- `create_vector_store`: Creates an empty vector store
- `process_document`: Processes a document
- `search_document_content`: Searches for content in a document
- `search_document_content_with_path`: Searches for content with a specified storage path

### 3. Modified Existing Code

The following classes have been updated to use the vector store service:
- `DataQuery`: Uses the vector store client for searching content
- `DataUploader`: Uses the vector store client for loading documents
- `DocumentProcessor`: Uses the vector store client internally while maintaining backward compatibility

## Running the Service

To run the vector store service:

```bash
cd D:\QualityControl\qc_project\ai
uvicorn vector_store_service:app --host 0.0.0.0 --port 8002
```

## Environment Variables

The vector store service uses the following environment variables:
- `VECTOR_STORE_PATH`: The default path to the vector store (used by the `/search` endpoint)
- `USE_VECTOR_STORE`: Controls whether the vector store functionality is used (default: "true")
  - If set to "false", all vector store operations will be skipped
  - If set to "true" or not set, vector store operations will be performed normally

## Usage Examples

### Creating a Vector Store

```python
from ai.vector_store_client import VectorStoreClient

client = VectorStoreClient()
response = client.create_vector_store("path/to/vector/store")
print(response)
```

### Processing a Document

```python
from ai.vector_store_client import VectorStoreClient
from ai.pdf_text_extractor import PdfTextExtractor
from pathlib import Path

client = VectorStoreClient()
extractor = PdfTextExtractor()
text = extractor.extract_text(Path("path/to/document.pdf"))
response = client.process_document(
    text=text,
    source_filename="document.pdf",
    storage_path="path/to/vector/store"
)
print(response)
```

### Searching for Content

```python
from ai.vector_store_client import VectorStoreClient

client = VectorStoreClient()
results = client.search_document_content_with_path(
    question="What is the main topic of the document?",
    document_name="document.pdf",
    storage_path="path/to/vector/store",
    k=3  # Number of results to return (default is 3)
)

if results:
    # Process individual results
    for i, result in enumerate(results):
        print(f"Result {i+1}:")
        print(f"Content: {result['page_content']}")
        print(f"Metadata: {result['metadata']}")
        print()

    # Or combine results into a single string
    combined_context = "\n\n".join([res["page_content"] for res in results])
    print("Combined context:")
    print(combined_context)
else:
    print("No results found.")
```

## Backward Compatibility

The implementation maintains backward compatibility with existing code:
- `DocumentProcessor` still works with the same interface
- Methods that directly use the vector store functionality now use the service internally
- Fallback mechanisms ensure that if the service is unavailable, the system can still function using direct vector store access

## Benefits

- **Modularity**: Clearly separates concerns and allows easier updates or replacements of the vector store without affecting other services
- **Scalability**: Can be independently scaled and deployed across different environments
- **Maintainability**: Easier debugging and maintenance as each component has a single responsibility
