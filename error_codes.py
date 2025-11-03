"""
Error Code Registry for Sofas & Stuff Pricing Platform v2.5.0

This module defines standardized error codes for tracking and debugging across
the entire platform (backend, frontend, dashboards).

Error Code Format:
- E1xxx: Network & External API Errors
- E2xxx: Validation & Data Errors
- E3xxx: Internal System Errors
- E4xxx: LLM/Tool Execution Errors
- F1xxx: Frontend Network Errors
- F2xxx: Frontend Validation Errors
- F3xxx: Frontend Rendering Errors
- F4xxx: Frontend Storage Errors

Usage:
    from error_codes import ERROR_CODES, create_error_response

    # Return standardized error
    return create_error_response(
        "E2001",
        "Product not found",
        suggested_action="Try: 'Alwinton', 'Midhurst', or 'Petworth'"
    ), 404
"""

# ============================================================================
# BACKEND ERROR CODES (E-codes)
# ============================================================================

ERROR_CODES = {
    # E1xxx: Network & External API Errors
    "E1001": {
        "name": "SOFA_API_TIMEOUT",
        "description": "S&S API request timed out",
        "user_message": "The request took too long. Please try again.",
        "suggested_action": "Try again in a few moments."
    },
    "E1002": {
        "name": "SOFA_API_CONNECTION_REFUSED",
        "description": "Cannot connect to S&S API",
        "user_message": "Unable to connect to pricing service.",
        "suggested_action": "Check your internet connection and try again."
    },
    "E1003": {
        "name": "SOFA_API_DNS_FAILURE",
        "description": "DNS resolution failed for sofasandstuff.com",
        "user_message": "Network error occurred.",
        "suggested_action": "Check your network and try again."
    },
    "E1004": {
        "name": "SOFA_API_RATE_LIMIT",
        "description": "Rate limit exceeded (429 from S&S API)",
        "user_message": "Too many requests. Please wait a moment.",
        "suggested_action": "Wait 60 seconds before trying again."
    },
    "E1005": {
        "name": "OPENROUTER_API_FAILURE",
        "description": "Grok/OpenRouter API failure",
        "user_message": "Chat service temporarily unavailable.",
        "suggested_action": "Use direct product queries instead, or try again later."
    },
    "E1006": {
        "name": "OPENROUTER_AUTH_FAILED",
        "description": "OpenRouter API key invalid or missing",
        "user_message": "Chat service not configured.",
        "suggested_action": "Contact system administrator."
    },

    # E2xxx: Validation & Data Errors
    "E2001": {
        "name": "PRODUCT_NOT_FOUND",
        "description": "No product matched the query",
        "user_message": "I couldn't find that product. Common products include Alwinton, Midhurst, Petworth, and Rye.",
        "suggested_action": "Try: 'How much is Alwinton snuggler?' or 'Show me Midhurst 3 seater'"
    },
    "E2002": {
        "name": "AMBIGUOUS_PRODUCT",
        "description": "Multiple products matched",
        "user_message": "Multiple products match your query. Please be more specific.",
        "suggested_action": "Choose one: See specific options in response above"
    },
    "E2003": {
        "name": "SIZE_NOT_FOUND",
        "description": "Size not available for product",
        "user_message": "That size isn't available for this product. Common sizes: Snuggler, 2 Seater, 3 Seater, 4 Seater.",
        "suggested_action": "Try: 'Show me [product] snuggler' or 'Price for [product] 3 seater'"
    },
    "E2004": {
        "name": "FABRIC_NOT_FOUND",
        "description": "Fabric/color not found",
        "user_message": "I couldn't find that fabric or color. Popular options: Pacific, Mink, Waves, Sky, Sussex Plain.",
        "suggested_action": "Try: '[product] in pacific' or 'Show me blue fabrics for [product]'"
    },
    "E2005": {
        "name": "AMBIGUOUS_FABRIC",
        "description": "Multiple fabrics matched",
        "user_message": "Multiple fabrics match. Please be more specific.",
        "suggested_action": None  # Specific suggestions provided in details
    },
    "E2006": {
        "name": "INVALID_REQUEST_FORMAT",
        "description": "Malformed JSON or invalid content-type",
        "user_message": "Invalid request format.",
        "suggested_action": "Check request format and try again."
    },
    "E2007": {
        "name": "MISSING_REQUIRED_FIELD",
        "description": "Required field missing from request",
        "user_message": "Missing required information.",
        "suggested_action": None  # Specific field mentioned in details
    },

    # E3xxx: Internal System Errors
    "E3001": {
        "name": "DICTIONARY_LOAD_FAILED",
        "description": "Failed to load products/sizes/fabrics JSON",
        "user_message": "System configuration error.",
        "suggested_action": "Contact system administrator."
    },
    "E3002": {
        "name": "DICTIONARY_MALFORMED",
        "description": "JSON file corrupted or invalid",
        "user_message": "System data corrupted.",
        "suggested_action": "Contact system administrator."
    },
    "E3003": {
        "name": "CACHE_WRITE_FAILED",
        "description": "Failed to write to cache",
        "user_message": None,  # Non-fatal, logged only
        "suggested_action": None
    },
    "E3004": {
        "name": "UNEXPECTED_EXCEPTION",
        "description": "Unexpected error occurred",
        "user_message": "An unexpected error occurred.",
        "suggested_action": "Try again, or contact support if problem persists."
    },

    # E4xxx: LLM/Tool Execution Errors
    "E4001": {
        "name": "TOOL_EXECUTION_FAILED",
        "description": "Tool handler threw exception",
        "user_message": "Failed to process request.",
        "suggested_action": "Try rephrasing your query or use direct product search."
    },
    "E4002": {
        "name": "TOOL_MAX_ITERATIONS",
        "description": "Hit max tool calling iterations",
        "user_message": "Request too complex to process.",
        "suggested_action": "Try breaking into smaller queries or rephrase."
    },
    "E4003": {
        "name": "LLM_PARSE_ERROR",
        "description": "Cannot parse LLM tool arguments",
        "user_message": "Failed to understand request.",
        "suggested_action": "Try rephrasing your query."
    },
    "E4004": {
        "name": "LLM_NO_RESPONSE",
        "description": "LLM returned empty response",
        "user_message": "No response generated.",
        "suggested_action": "Try again or rephrase your query."
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_error_response(error_code, custom_user_message=None, details=None, suggested_action=None):
    """
    Creates a standardized error response dictionary.

    Args:
        error_code (str): Error code from ERROR_CODES (e.g., "E2001")
        custom_user_message (str, optional): Override default user message
        details (dict, optional): Additional error context (e.g., matched options)
        suggested_action (str, optional): Override default suggested action

    Returns:
        dict: Standardized error response with:
            - error: User-facing message (friendly, actionable)
            - error_code: Machine-readable code (for logging/filtering)
            - details: Additional context
            - suggested_action: What user should do next

    Example:
        >>> create_error_response("E2001", suggested_action="Try: 'Alwinton' or 'Midhurst'")
        {
            "error": "Product not found.",
            "error_code": "E2001",
            "details": {},
            "suggested_action": "Try: 'Alwinton' or 'Midhurst'"
        }
    """
    if error_code not in ERROR_CODES:
        # Unknown error code - return generic error
        return {
            "error": custom_user_message or "An error occurred.",
            "error_code": error_code,
            "details": details or {},
            "suggested_action": suggested_action
        }

    error_info = ERROR_CODES[error_code]

    return {
        "error": custom_user_message or error_info["user_message"],
        "error_code": error_code,
        "details": details or {},
        "suggested_action": suggested_action or error_info["suggested_action"]
    }


def get_error_name(error_code):
    """Get the error name for a given code."""
    return ERROR_CODES.get(error_code, {}).get("name", "UNKNOWN_ERROR")


def get_error_description(error_code):
    """Get the error description for a given code."""
    return ERROR_CODES.get(error_code, {}).get("description", "Unknown error")


# ============================================================================
# FRONTEND ERROR CODES (F-codes) - For documentation only
# ============================================================================
# These are defined in index.html but documented here for reference:
#
# F1xxx: Network Errors
#   F1001: NETWORK_OFFLINE - User is offline
#   F1002: REQUEST_TIMEOUT - Fetch timeout exceeded
#   F1003: BACKEND_UNREACHABLE - Cannot connect to backend
#   F1004: CORS_BLOCKED - CORS policy blocked request
#
# F2xxx: Validation Errors
#   F2001: EMPTY_QUERY - User submitted empty query
#   F2002: QUERY_TOO_LONG - Query exceeds max length
#   F2003: INVALID_SESSION - Session ID invalid
#
# F3xxx: Rendering Errors
#   F3001: MARKDOWN_PARSE_FAILED - Cannot parse LLM response
#   F3002: RESPONSE_EMPTY - Empty response received
#
# F4xxx: Storage Errors
#   F4001: LOCALSTORAGE_FULL - localStorage quota exceeded
#   F4002: LOCALSTORAGE_DISABLED - localStorage not available
# ============================================================================
