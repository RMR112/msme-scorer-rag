#!/usr/bin/env python3
"""
Script to update kv_store_doc_status.json with correct file paths
"""

import json
import os

def update_kv_store_file():
    """Update kv_store_doc_status.json with correct file paths"""
    
    # Paths
    working_dir = os.path.join(os.path.dirname(__file__), "rag-pdf")
    kv_store_file = os.path.join(working_dir, "kv_store_doc_status.json")
    ingestion_file = os.path.join(working_dir, "ingestion_metadata.json")
    
    # Load ingestion metadata to get document mappings
    doc_mappings = {}
    if os.path.exists(ingestion_file):
        with open(ingestion_file, 'r', encoding='utf-8') as f:
            ingestion_data = json.load(f)
        
        # Create mapping from document IDs to file names
        for doc_info in ingestion_data.get("ingestion_session", {}).get("documents_processed", []):
            if doc_info.get("status") == "success" and "metadata" in doc_info:
                doc_metadata = doc_info["metadata"]
                doc_id = doc_metadata.get("document_id")
                filename = doc_metadata.get("document_name")
                if doc_id and filename:
                    doc_mappings[doc_id] = filename
    
    print(f"Found {len(doc_mappings)} document mappings:")
    for doc_id, filename in doc_mappings.items():
        print(f"  {doc_id} -> {filename}")
    
    # Load and update kv_store_doc_status.json
    if os.path.exists(kv_store_file):
        with open(kv_store_file, 'r', encoding='utf-8') as f:
            kv_store_data = json.load(f)
        
        updated_count = 0
        for doc_id, doc_info in kv_store_data.items():
            if doc_info.get("file_path") == "unknown_source":
                # Try to find the corresponding document
                for mapped_doc_id, filename in doc_mappings.items():
                    # Simple heuristic: check if the doc_id contains parts of the mapped_doc_id
                    if mapped_doc_id.lower() in doc_id.lower() or doc_id.lower() in mapped_doc_id.lower():
                        doc_info["file_path"] = filename
                        updated_count += 1
                        print(f"Updated {doc_id} -> {filename}")
                        break
        
        # Save the updated file
        with open(kv_store_file, 'w', encoding='utf-8') as f:
            json.dump(kv_store_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nUpdated {updated_count} documents in kv_store_doc_status.json")
    else:
        print(f"kv_store_doc_status.json not found at {kv_store_file}")

if __name__ == "__main__":
    update_kv_store_file()
