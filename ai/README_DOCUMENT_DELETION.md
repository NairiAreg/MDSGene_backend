# Document Deletion Functionality

This document describes the implementation of the document deletion functionality, which allows you to delete a document and all related data from the system.

## Overview

The document deletion functionality consists of three main components:

1. **Vector Store Service Endpoint**: A DELETE endpoint in the vector store service that allows deleting a document from the vector store.
2. **Vector Store Client Method**: A client method that calls the DELETE endpoint.
3. **Cache Utility Functions**: Utility functions for deleting cache folders and removing entries from the pmid_cache.json file.

## Components

### 1. Vector Store Service Endpoint

The vector store service now includes a DELETE endpoint at `/delete_document_from_store` that allows deleting a document from the vector store based on its name.

```python
@app.delete("/delete_document_from_store")
def delete_document_from_store(document_name: str, storage_path: str):
    """
    Delete a document from the vector store.

    Args:
        document_name: The name of the document to delete
        storage_path: Path to the vector store

    Returns:
        Success message
    """
    # Implementation details...
```

### 2. Vector Store Client Method

The `VectorStoreClient` class now includes a method for deleting a document from the vector store:

```python
def delete_document_from_store(self, document_name: str, storage_path: str) -> Dict[str, Any]:
    """
    Delete a document from the vector store.

    Args:
        document_name: The name of the document to delete
        storage_path: Path to the vector store

    Returns:
        Response from the service
    """
    # Implementation details...
```

### 3. Cache Utility Functions

The `cache_utils.py` file contains utility functions for deleting cache folders and removing entries from the pmid_cache.json file:

- `delete_pmid_cache(pmid, cache_root)`: Deletes the entire cache folder for a specific PMID.
- `remove_document_from_pmid_cache(pdf_filename, pmid_cache_path)`: Removes a document entry from the pmid_cache.json file.
- `delete_document_and_all_related_data(pdf_filename, pmid, storage_path, cache_root, pmid_cache_path, vector_store_client)`: A comprehensive function that combines the above two functions and also deletes the document from the vector store.

## Usage

### Using the Utility Functions

```python
from pathlib import Path
from vector_store_client import VectorStoreClient
from cache_utils import delete_document_and_all_related_data

# Configuration
cache_root = Path("cache")
pmid_cache_path = cache_root / "pmid_cache.json"
storage_path = "vector_store/faiss_index"

# Initialize vector store client
vector_store_client = VectorStoreClient(service_url="http://localhost:8002")

# Delete document and all related data
delete_document_and_all_related_data(
    pdf_filename="document.pdf",
    pmid="12345678",
    storage_path=storage_path,
    cache_root=cache_root,
    pmid_cache_path=pmid_cache_path,
    vector_store_client=vector_store_client
)
```

### Using the Example Script

You can also use the provided example script `delete_document_example.py`:

```bash
python delete_document_example.py
```

The script will prompt you for the PDF filename and PMID, and then delete all related data.

## Benefits

- **Complete Cleanup**: Ensures that all data related to a document is removed from the system, including cache files, vector store entries, and pmid_cache.json entries.
- **Modularity**: Each component can be used independently if needed.
- **User-Friendly**: The example script provides a simple interface for deleting documents.