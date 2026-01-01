#!/bin/bash

# API Gateway Endpoint Test Script
# Tests chat and analytics endpoints with sample queries

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API Configuration
API_BASE_URL="https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev"
API_KEY="nWU3TtU4G88fmNm0VDLyBONFlvx6gwE6WZGRTEY7"

echo "=========================================="
echo "AutoCorp API Gateway Test Suite"
echo "=========================================="
echo ""

# Test 1: Chat Endpoint - Oil Change Query
echo -e "${YELLOW}Test 1: Chat Endpoint - Oil Change Query${NC}"
echo "Endpoint: POST $API_BASE_URL/chat"
echo ""

CHAT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "message": "What parts are needed for an oil change?"
  }')

HTTP_CODE=$(echo "$CHAT_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$CHAT_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
  echo -e "${GREEN}✓ Status: $HTTP_CODE OK${NC}"
  echo ""
  echo "Response:"
  echo "$RESPONSE_BODY" | jq -r '.response' 2>/dev/null || echo "$RESPONSE_BODY"
  echo ""
  
  # Check for sources
  SOURCES=$(echo "$RESPONSE_BODY" | jq -r '.sources[]?.title' 2>/dev/null | wc -l)
  if [ "$SOURCES" -gt 0 ]; then
    echo -e "${GREEN}✓ RAG Sources Retrieved: $SOURCES${NC}"
  else
    echo -e "${YELLOW}⚠ No RAG sources found${NC}"
  fi
else
  echo -e "${RED}✗ Status: $HTTP_CODE FAILED${NC}"
  echo "Response: $RESPONSE_BODY"
fi

echo ""
echo "=========================================="
echo ""

# Test 2: Chat Endpoint - Service Query
echo -e "${YELLOW}Test 2: Chat Endpoint - Service Query${NC}"
echo "Endpoint: POST $API_BASE_URL/chat"
echo ""

CHAT_RESPONSE2=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "message": "How much does a brake inspection cost?"
  }')

HTTP_CODE2=$(echo "$CHAT_RESPONSE2" | tail -n1)
RESPONSE_BODY2=$(echo "$CHAT_RESPONSE2" | sed '$d')

if [ "$HTTP_CODE2" -eq 200 ]; then
  echo -e "${GREEN}✓ Status: $HTTP_CODE2 OK${NC}"
  echo ""
  echo "Response:"
  echo "$RESPONSE_BODY2" | jq -r '.response' 2>/dev/null || echo "$RESPONSE_BODY2"
else
  echo -e "${RED}✗ Status: $HTTP_CODE2 FAILED${NC}"
  echo "Response: $RESPONSE_BODY2"
fi

echo ""
echo "=========================================="
echo ""

# Test 3: Analytics Endpoint - Sales Summary
echo -e "${YELLOW}Test 3: Analytics Endpoint - Sales Summary${NC}"
echo "Endpoint: POST $API_BASE_URL/analytics"
echo ""

ANALYTICS_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/analytics" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "query_name": "sales_summary"
  }')

HTTP_CODE3=$(echo "$ANALYTICS_RESPONSE" | tail -n1)
RESPONSE_BODY3=$(echo "$ANALYTICS_RESPONSE" | sed '$d')

if [ "$HTTP_CODE3" -eq 200 ]; then
  echo -e "${GREEN}✓ Status: $HTTP_CODE3 OK${NC}"
  echo ""
  echo "Response:"
  echo "$RESPONSE_BODY3" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY3"
  
  # Count rows returned
  ROW_COUNT=$(echo "$RESPONSE_BODY3" | jq '.results | length' 2>/dev/null)
  if [ ! -z "$ROW_COUNT" ] && [ "$ROW_COUNT" -gt 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Rows Returned: $ROW_COUNT${NC}"
  fi
else
  echo -e "${RED}✗ Status: $HTTP_CODE3 FAILED${NC}"
  echo "Response: $RESPONSE_BODY3"
fi

echo ""
echo "=========================================="
echo ""

# Test 4: Error Handling - Invalid API Key
echo -e "${YELLOW}Test 4: Error Handling - Invalid API Key${NC}"
echo "Endpoint: POST $API_BASE_URL/chat"
echo ""

ERROR_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: INVALID_KEY" \
  -d '{
    "message": "Test message"
  }')

HTTP_CODE4=$(echo "$ERROR_RESPONSE" | tail -n1)

if [ "$HTTP_CODE4" -eq 403 ]; then
  echo -e "${GREEN}✓ Status: $HTTP_CODE4 Forbidden (Expected)${NC}"
  echo "API key validation working correctly"
else
  echo -e "${YELLOW}⚠ Status: $HTTP_CODE4 (Expected 403)${NC}"
fi

echo ""
echo "=========================================="
echo ""

# Test 5: Error Handling - Missing Message
echo -e "${YELLOW}Test 5: Error Handling - Missing Message${NC}"
echo "Endpoint: POST $API_BASE_URL/chat"
echo ""

ERROR_RESPONSE2=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{}')

HTTP_CODE5=$(echo "$ERROR_RESPONSE2" | tail -n1)
RESPONSE_BODY5=$(echo "$ERROR_RESPONSE2" | sed '$d')

if [ "$HTTP_CODE5" -eq 400 ]; then
  echo -e "${GREEN}✓ Status: $HTTP_CODE5 Bad Request (Expected)${NC}"
  echo "Input validation working correctly"
  echo "Error: $(echo "$RESPONSE_BODY5" | jq -r '.error' 2>/dev/null)"
else
  echo -e "${YELLOW}⚠ Status: $HTTP_CODE5 (Expected 400)${NC}"
  echo "Response: $RESPONSE_BODY5"
fi

echo ""
echo "=========================================="
echo ""

# Summary
echo -e "${YELLOW}Test Summary${NC}"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

if [ "$HTTP_CODE" = "200" ]; then ((PASS_COUNT++)); else ((FAIL_COUNT++)); fi
if [ "$HTTP_CODE2" = "200" ]; then ((PASS_COUNT++)); else ((FAIL_COUNT++)); fi
if [ "$HTTP_CODE3" = "200" ]; then ((PASS_COUNT++)); else ((FAIL_COUNT++)); fi
if [ "$HTTP_CODE4" = "403" ]; then ((PASS_COUNT++)); else ((FAIL_COUNT++)); fi
if [ "$HTTP_CODE5" = "400" ]; then ((PASS_COUNT++)); else ((FAIL_COUNT++)); fi

echo "Total Tests: 5"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
[ "$FAIL_COUNT" -gt 0 ] && echo -e "${RED}Failed: $FAIL_COUNT${NC}" || echo "Failed: 0"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
  echo -e "${GREEN}All tests passed! ✓${NC}"
  exit 0
else
  echo -e "${RED}Some tests failed ✗${NC}"
  exit 1
fi
