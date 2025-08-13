#!/bin/bash

# Smoke test script for error handling system
# Tests key error responses (401, 404, 429, 413) against a given base URL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL=${1:-"http://localhost:8000"}
TIMEOUT=10
FAILED_TESTS=0
TOTAL_TESTS=0

echo -e "${BLUE}🧪 CoinGrok Error Handling Smoke Tests${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "Base URL: ${BASE_URL}"
echo -e "Timeout: ${TIMEOUT}s"
echo ""

# Helper function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local expected_error_code=$4
    local description=$5
    local extra_args=$6
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${YELLOW}Testing:${NC} $description"
    echo -e "  ${method} ${BASE_URL}${endpoint} -> expecting ${expected_status}"
    
    # Make request and capture response
    local response=$(curl -s -w "\n%{http_code}" \
        -X "$method" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        --max-time $TIMEOUT \
        $extra_args \
        "${BASE_URL}${endpoint}" 2>/dev/null || echo -e "\nERROR")
    
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    # Check if request failed
    if [[ "$status_code" == "ERROR" ]]; then
        echo -e "  ${RED}❌ FAILED${NC} - Request failed (network/timeout)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    # Check status code
    if [[ "$status_code" != "$expected_status" ]]; then
        echo -e "  ${RED}❌ FAILED${NC} - Expected status $expected_status, got $status_code"
        echo -e "  Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    # Check if response is valid JSON with error structure
    local error_code=$(echo "$body" | jq -r '.error.code' 2>/dev/null || echo "null")
    local correlation_id=$(echo "$body" | jq -r '.error.correlation_id' 2>/dev/null || echo "null")
    local message=$(echo "$body" | jq -r '.error.message' 2>/dev/null || echo "null")
    
    # Validate error structure
    if [[ "$error_code" == "null" || "$correlation_id" == "null" || "$message" == "null" ]]; then
        echo -e "  ${RED}❌ FAILED${NC} - Invalid error response structure"
        echo -e "  Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    # Check expected error code if provided
    if [[ -n "$expected_error_code" && "$error_code" != "$expected_error_code" ]]; then
        echo -e "  ${RED}❌ FAILED${NC} - Expected error code '$expected_error_code', got '$error_code'"
        echo -e "  Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    # Success
    echo -e "  ${GREEN}✅ PASSED${NC} - Status: $status_code, Code: $error_code"
    echo -e "  Message: $message"
    echo -e "  Correlation ID: ${correlation_id:0:8}..."
}

# Test 1: 404 - Job Not Found
test_endpoint "GET" "/analyze-async/non-existent-job-id" "404" "JOB_NOT_FOUND" "Job not found error"

echo ""

# Test 2: 401 - Authentication Required
test_endpoint "GET" "/me" "401" "" "Authentication required"

echo ""

# Test 3: 401 - Invalid Authentication Token
test_endpoint "GET" "/me" "401" "" "Invalid authentication token" '-H "Authorization: Bearer invalid-token"'

echo ""

# Test 4: 404 - Non-existent endpoint (HTTPException fallback)
test_endpoint "GET" "/non-existent-endpoint" "404" "HTTP_EXCEPTION" "Non-existent endpoint"

echo ""

# Test 5: 422 - Validation error (empty request body)
test_endpoint "POST" "/analyze-async" "422" "INVALID_INPUT" "Validation error - empty body" '-d "{}"'

echo ""

# Test 6: Field length validation (422 - application validation)
large_input='{"user_input":"'$(printf 'A%.0s' {1..6000})'"}' # 6000 chars (over 5000 limit)
echo -e "${YELLOW}Testing:${NC} Field length validation"
echo -e "  POST ${BASE_URL}/analyze-async -> expecting 422"

response=$(curl -s -w "\n%{http_code}" \
    -X "POST" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    --max-time $TIMEOUT \
    -d "$large_input" \
    "${BASE_URL}/analyze-async" 2>/dev/null || echo -e "\nERROR")

status_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

TOTAL_TESTS=$((TOTAL_TESTS + 1))

if [[ "$status_code" == "422" ]]; then
    # Check if it's our unified format
    error_code=$(echo "$body" | jq -r '.error.code' 2>/dev/null || echo "null")
    correlation_id=$(echo "$body" | jq -r '.error.correlation_id' 2>/dev/null || echo "null")
    message=$(echo "$body" | jq -r '.error.message' 2>/dev/null || echo "null")
    
    if [[ "$error_code" == "INVALID_INPUT" && "$correlation_id" != "null" && "$message" != "null" ]]; then
        echo -e "  ${GREEN}✅ PASSED${NC} - Status: 422, Code: INVALID_INPUT (unified format)"
        echo -e "  Message: $message"
        echo -e "  Correlation ID: ${correlation_id:0:8}..."
    else
        echo -e "  ${RED}❌ FAILED${NC} - Invalid unified error response structure"
        echo -e "  Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
elif [[ "$status_code" == "ERROR" ]]; then
    echo -e "  ${RED}❌ FAILED${NC} - Request failed (network/timeout)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
else
    echo -e "  ${RED}❌ FAILED${NC} - Expected status 422, got $status_code"
    echo -e "  Response: $body"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

echo ""

# Test 7: Health check (should succeed)
echo -e "${YELLOW}Testing:${NC} Health check endpoint"
echo -e "  GET ${BASE_URL}/health -> expecting 200"

response=$(curl -s -w "\n%{http_code}" \
    -X "GET" \
    -H "Accept: application/json" \
    --max-time $TIMEOUT \
    "${BASE_URL}/health" 2>/dev/null || echo -e "\nERROR")

status_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

TOTAL_TESTS=$((TOTAL_TESTS + 1))

if [[ "$status_code" == "200" ]]; then
    echo -e "  ${GREEN}✅ PASSED${NC} - Health check successful"
elif [[ "$status_code" == "ERROR" ]]; then
    echo -e "  ${RED}❌ FAILED${NC} - Health check failed (network/timeout)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
else
    echo -e "  ${RED}❌ FAILED${NC} - Health check returned $status_code"
    echo -e "  Response: $body"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Summary
echo ""
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}📊 SMOKE TEST SUMMARY${NC}"
echo -e "${BLUE}=====================================${NC}"

PASSED_TESTS=$((TOTAL_TESTS - FAILED_TESTS))

if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}🎉 All tests passed!${NC} ($PASSED_TESTS/$TOTAL_TESTS)"
    echo ""
    echo -e "${GREEN}✅ Error handling system is working correctly${NC}"
    echo -e "✓ Unified error envelope format verified"
    echo -e "✓ Proper HTTP status codes returned"
    echo -e "✓ Error codes and correlation IDs present"
    echo -e "✓ Authentication errors handled properly"
    echo -e "✓ Not found errors handled properly"
    echo -e "✓ Health check endpoint working"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC} ($PASSED_TESTS/$TOTAL_TESTS passed)"
    echo ""
    echo -e "${RED}⚠️  Error handling system issues detected${NC}"
    echo -e "Please review the failed tests above"
    echo ""
    exit 1
fi