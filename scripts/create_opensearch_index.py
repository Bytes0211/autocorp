#!/usr/bin/env python3
"""
Create OpenSearch Serverless Index for Bedrock Knowledge Base

This script creates the vector index in OpenSearch Serverless that Bedrock
Knowledge Base requires before it can be deployed.

Usage:
    python scripts/create_opensearch_index.py <collection-endpoint> <index-name>
"""

import sys
import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def create_bedrock_index(collection_endpoint, index_name):
    """Create OpenSearch index for Bedrock Knowledge Base"""
    
    # Get AWS credentials
    session = boto3.Session()
    credentials = session.get_credentials()
    region = session.region_name or 'us-east-1'
    
    # Create AWS Signature V4 auth
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'aoss',
        session_token=credentials.token
    )
    
    # Remove https:// from endpoint if present
    endpoint = collection_endpoint.replace('https://', '').replace('http://', '')
    
    # Create OpenSearch client
    client = OpenSearch(
        hosts=[{'host': endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30
    )
    
    # Check if index already exists
    if client.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists")
        return True
    
    # Define index mapping for Bedrock Knowledge Base
    index_body = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 512
            }
        },
        "mappings": {
            "properties": {
                "bedrock-knowledge-base-default-vector": {
                    "type": "knn_vector",
                    "dimension": 1536,
                    "method": {
                        "name": "hnsw",
                        "engine": "faiss",
                        "parameters": {
                            "ef_construction": 512,
                            "m": 16
                        },
                        "space_type": "l2"
                    }
                },
                "AMAZON_BEDROCK_TEXT_CHUNK": {
                    "type": "text"
                },
                "AMAZON_BEDROCK_METADATA": {
                    "type": "text"
                }
            }
        }
    }
    
    # Create index
    try:
        response = client.indices.create(index=index_name, body=index_body)
        print(f"Successfully created index '{index_name}'")
        print(f"Response: {json.dumps(response, indent=2)}")
        return True
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python create_opensearch_index.py <collection-endpoint> <index-name>")
        print("Example: python create_opensearch_index.py zkxlftz38nvgobqfnsgi.us-east-1.aoss.amazonaws.com bedrock-knowledge-base-default-index")
        return 1
    
    collection_endpoint = sys.argv[1]
    index_name = sys.argv[2]
    
    print(f"Creating OpenSearch Serverless index...")
    print(f"Collection endpoint: {collection_endpoint}")
    print(f"Index name: {index_name}")
    print("")
    
    success = create_bedrock_index(collection_endpoint, index_name)
    
    if success:
        print("\n✓ Index created successfully!")
        print("\nNext steps:")
        print("1. Deploy Bedrock Knowledge Base: cd terraform && terraform apply -target=module.bedrock")
        return 0
    else:
        print("\n✗ Failed to create index")
        return 1

if __name__ == "__main__":
    sys.exit(main())
