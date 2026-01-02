"""
Lambda function for AutoCorp AI Chatbox - Chat Handler
Handles user queries using Bedrock Knowledge Base (RAG) and Nova Pro

Environment Variables:
    KNOWLEDGE_BASE_ID: Bedrock Knowledge Base ID
    MODEL_ID: Bedrock model ID (amazon.nova-pro-v1:0)
    MAX_RESULTS: Number of retrieval results (default: 5)
    MAX_TOKENS: Maximum response tokens (default: 500)
"""

import json
import os
import logging
from typing import Dict, List, Any

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Environment variables
KNOWLEDGE_BASE_ID = os.environ.get('KNOWLEDGE_BASE_ID', 'UQSLM6QEVT')
MODEL_ID = os.environ.get('MODEL_ID', 'amazon.nova-pro-v1:0')
MAX_RESULTS = int(os.environ.get('MAX_RESULTS', '5'))
MAX_TOKENS = int(os.environ.get('MAX_TOKENS', '500'))
TEMPERATURE = float(os.environ.get('TEMPERATURE', '0.7'))


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for chat requests
    
    Args:
        event: API Gateway proxy event with 'body' containing JSON: {"message": "user query"}
        context: Lambda context object
        
    Returns:
        API Gateway proxy response with statusCode, headers, and body
    """
    try:
        # Parse request body
        logger.info(f"Received event: {json.dumps(event)}")
        
        if 'body' not in event:
            return create_response(400, {'error': 'Missing request body'})
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        if 'message' not in body:
            return create_response(400, {'error': 'Missing "message" field in request'})
        
        user_query = body['message'].strip()
        
        if not user_query:
            return create_response(400, {'error': 'Empty message'})
        
        logger.info(f"Processing query: {user_query}")
        
        # Step 1: Retrieve context from Knowledge Base
        logger.info(f"Retrieving from Knowledge Base: {KNOWLEDGE_BASE_ID}")
        context_results = retrieve_from_knowledge_base(user_query)
        
        if not context_results:
            return create_response(200, {
                'message': "I couldn't find relevant information in the knowledge base. Could you rephrase your question?",
                'sources': []
            })
        
        # Step 2: Build context from retrieval results
        context_text = build_context(context_results)
        logger.info(f"Built context from {len(context_results)} results")
        
        # Step 3: Generate response with Nova Pro
        logger.info(f"Invoking model: {MODEL_ID}")
        answer = generate_response(user_query, context_text)
        
        # Step 4: Extract sources
        sources = extract_sources(context_results)
        
        logger.info(f"Successfully generated response with {len(sources)} sources")
        
        return create_response(200, {
            'message': answer,
            'sources': sources,
            'metadata': {
                'knowledge_base_results': len(context_results),
                'model': MODEL_ID
            }
        })
        
    except ClientError as e:
        logger.error(f"AWS ClientError: {str(e)}")
        return create_response(500, {
            'error': 'AWS service error',
            'details': str(e)
        })
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })


def retrieve_from_knowledge_base(query: str) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context from Bedrock Knowledge Base
    
    Args:
        query: User query text
        
    Returns:
        List of retrieval results with content and metadata
    """
    try:
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': MAX_RESULTS
                }
            }
        )
        
        return response.get('retrievalResults', [])
        
    except ClientError as e:
        logger.error(f"Knowledge Base retrieval error: {str(e)}")
        raise


def build_context(results: List[Dict[str, Any]]) -> str:
    """
    Build context string from retrieval results
    
    Args:
        results: List of retrieval results from Knowledge Base
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    for idx, result in enumerate(results, 1):
        content = result.get('content', {}).get('text', '')
        score = result.get('score', 0.0)
        
        if content:
            context_parts.append(f"[Source {idx}] (Relevance: {score:.2f})\n{content}")
    
    return "\n\n".join(context_parts)


def generate_response(query: str, context: str) -> str:
    """
    Generate response using Bedrock Nova Pro with RAG context
    
    Args:
        query: User query
        context: Retrieved context from Knowledge Base
        
    Returns:
        Generated answer text
    """
    # Build prompt with RAG pattern
    prompt = f"""You are an AI assistant for AutoCorp, an automotive parts and services company. Use the provided context to answer the user's question accurately and concisely.

Context from Knowledge Base:
{context}

User Question: {query}

Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say so
- Be specific and include relevant details (part numbers, prices, categories)
- Keep responses concise and professional

Answer:"""

    try:
        # Invoke Nova Pro model with Messages API format
        request_body = {
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {'text': prompt}
                    ]
                }
            ],
            'inferenceConfig': {
                'maxTokens': MAX_TOKENS,
                'temperature': TEMPERATURE,
                'topP': 0.9
            },
            'system': [
                {
                    'text': 'You are an AI assistant for AutoCorp, an automotive parts and services company.'
                }
            ]
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        
        # Extract completion from Nova Pro response (Messages API format)
        if 'output' in response_body and 'message' in response_body['output']:
            message = response_body['output']['message']
            if 'content' in message and len(message['content']) > 0:
                answer = message['content'][0].get('text', '').strip()
            else:
                answer = ''
        else:
            answer = ''
        
        if not answer:
            logger.warning("Empty response from model")
            return "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
        
        return answer
        
    except ClientError as e:
        logger.error(f"Model invocation error: {str(e)}")
        raise


def extract_sources(results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extract source metadata from retrieval results
    
    Args:
        results: List of retrieval results
        
    Returns:
        List of source dictionaries with uri and score
    """
    sources = []
    
    for result in results[:3]:  # Top 3 sources
        location = result.get('location', {})
        score = result.get('score', 0.0)
        
        # Extract S3 location if available
        if 's3Location' in location:
            s3_loc = location['s3Location']
            uri = s3_loc.get('uri', '')
            if uri:
                sources.append({
                    'uri': uri,
                    'relevance_score': round(score, 3)
                })
    
    return sources


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create API Gateway proxy response
    
    Args:
        status_code: HTTP status code
        body: Response body dictionary
        
    Returns:
        API Gateway proxy response format
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
