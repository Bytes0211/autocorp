"""
Lambda function for AutoCorp AI Chatbox - Analytics Query Handler
Executes Athena queries for real-time analytics and data insights

Environment Variables:
    DATABASE_NAME: Athena database name (default: autocorp_dev)
    OUTPUT_LOCATION: S3 location for query results
    WORKGROUP: Athena workgroup name
"""

import json
import os
import logging
import time
from typing import Dict, List, Any, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
athena = boto3.client('athena', region_name='us-east-1')
glue = boto3.client('glue', region_name='us-east-1')

# Environment variables
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'autocorp_dev')
OUTPUT_LOCATION = os.environ.get('OUTPUT_LOCATION', 's3://autocorp-datalake-dev/athena-results/')
WORKGROUP = os.environ.get('WORKGROUP', 'autocorp-workgroup-dev')
MAX_WAIT_TIME = int(os.environ.get('MAX_WAIT_TIME', '30'))  # seconds

# Predefined safe queries
PREDEFINED_QUERIES = {
    'sales_summary': 'SELECT COUNT(*) as total_orders, SUM(total_amount) as total_revenue FROM sales_order',
    'top_customers': 'SELECT customer_id, COUNT(*) as order_count FROM sales_order GROUP BY customer_id ORDER BY order_count DESC LIMIT 10',
    'popular_parts': 'SELECT part_sku, COUNT(*) as order_count FROM sales_order_parts GROUP BY part_sku ORDER BY order_count DESC LIMIT 10',
    'popular_services': 'SELECT service_id, COUNT(*) as order_count FROM sales_order_services GROUP BY service_id ORDER BY order_count DESC LIMIT 10',
    'recent_orders': 'SELECT invoice_number, customer_id, total_amount, order_date FROM sales_order ORDER BY order_date DESC LIMIT 20'
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for analytics query requests
    
    Args:
        event: API Gateway proxy event with 'body' containing:
               - query_name (str): Name of predefined query
               OR
               - query (str): Custom SQL query (restricted)
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
        
        # Determine query to execute
        query = None
        query_source = None
        
        if 'query_name' in body:
            query_name = body['query_name']
            if query_name not in PREDEFINED_QUERIES:
                return create_response(400, {
                    'error': f'Invalid query_name. Available: {list(PREDEFINED_QUERIES.keys())}'
                })
            query = PREDEFINED_QUERIES[query_name]
            query_source = f'predefined:{query_name}'
            logger.info(f"Using predefined query: {query_name}")
            
        elif 'query' in body:
            custom_query = body['query'].strip()
            
            # Security check: only allow SELECT queries
            if not is_safe_query(custom_query):
                return create_response(403, {
                    'error': 'Only SELECT queries are allowed. No DDL/DML operations permitted.'
                })
            
            query = custom_query
            query_source = 'custom'
            logger.info(f"Using custom query (first 100 chars): {query[:100]}")
            
        else:
            return create_response(400, {
                'error': 'Must provide either "query_name" or "query" field'
            })
        
        # Execute query
        logger.info(f"Executing Athena query in database: {DATABASE_NAME}")
        execution_id = start_query_execution(query)
        logger.info(f"Query execution ID: {execution_id}")
        
        # Wait for query to complete
        status = wait_for_query_completion(execution_id, MAX_WAIT_TIME)
        
        if status != 'SUCCEEDED':
            error_msg = get_query_error(execution_id)
            return create_response(500, {
                'error': f'Query failed with status: {status}',
                'details': error_msg,
                'execution_id': execution_id
            })
        
        # Get query results
        results = get_query_results(execution_id)
        
        logger.info(f"Successfully executed query, returned {len(results)} rows")
        
        return create_response(200, {
            'data': results,
            'metadata': {
                'execution_id': execution_id,
                'database': DATABASE_NAME,
                'query_source': query_source,
                'row_count': len(results)
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


def is_safe_query(query: str) -> bool:
    """
    Validate that query is safe (SELECT only, no DDL/DML)
    
    Args:
        query: SQL query string
        
    Returns:
        True if query is safe, False otherwise
    """
    query_upper = query.upper().strip()
    
    # Must start with SELECT
    if not query_upper.startswith('SELECT'):
        return False
    
    # Forbidden keywords
    forbidden = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'REPLACE', 'MERGE', 'GRANT', 'REVOKE'
    ]
    
    for keyword in forbidden:
        if keyword in query_upper:
            logger.warning(f"Query contains forbidden keyword: {keyword}")
            return False
    
    return True


def start_query_execution(query: str) -> str:
    """
    Start Athena query execution
    
    Args:
        query: SQL query string
        
    Returns:
        Query execution ID
    """
    try:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': DATABASE_NAME
            },
            ResultConfiguration={
                'OutputLocation': OUTPUT_LOCATION
            },
            WorkGroup=WORKGROUP
        )
        
        return response['QueryExecutionId']
        
    except ClientError as e:
        logger.error(f"Failed to start query execution: {str(e)}")
        raise


def wait_for_query_completion(execution_id: str, max_wait: int) -> str:
    """
    Wait for Athena query to complete
    
    Args:
        execution_id: Query execution ID
        max_wait: Maximum wait time in seconds
        
    Returns:
        Final query status (SUCCEEDED, FAILED, CANCELLED)
    """
    elapsed = 0
    poll_interval = 1  # seconds
    
    while elapsed < max_wait:
        response = athena.get_query_execution(QueryExecutionId=execution_id)
        status = response['QueryExecution']['Status']['State']
        
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            return status
        
        time.sleep(poll_interval)
        elapsed += poll_interval
    
    logger.warning(f"Query execution timeout after {max_wait}s")
    return 'TIMEOUT'


def get_query_error(execution_id: str) -> Optional[str]:
    """
    Get error message for failed query
    
    Args:
        execution_id: Query execution ID
        
    Returns:
        Error message or None
    """
    try:
        response = athena.get_query_execution(QueryExecutionId=execution_id)
        status = response['QueryExecution']['Status']
        
        if 'StateChangeReason' in status:
            return status['StateChangeReason']
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get query error: {str(e)}")
        return str(e)


def get_query_results(execution_id: str) -> List[Dict[str, Any]]:
    """
    Get results from completed Athena query
    
    Args:
        execution_id: Query execution ID
        
    Returns:
        List of result rows as dictionaries
    """
    try:
        response = athena.get_query_results(QueryExecutionId=execution_id)
        
        # Extract column names from first row
        result_set = response['ResultSet']
        rows = result_set['Rows']
        
        if not rows:
            return []
        
        # First row contains column metadata
        columns = [col['VarCharValue'] for col in rows[0]['Data']]
        
        # Convert remaining rows to dictionaries
        results = []
        for row in rows[1:]:  # Skip header row
            values = []
            for col in row['Data']:
                # Handle null values
                if 'VarCharValue' in col:
                    values.append(col['VarCharValue'])
                else:
                    values.append(None)
            
            results.append(dict(zip(columns, values)))
        
        return results
        
    except ClientError as e:
        logger.error(f"Failed to get query results: {str(e)}")
        raise


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
