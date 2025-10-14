"""
Groq Inference Module
Core API client for Groq Cloud simplification and translation
"""

import requests
import time
import streamlit as st
from typing import Dict, Tuple, Optional
from datetime import datetime

from utils.groq_config import (
    get_groq_api_key,
    get_api_endpoint,
    get_selected_groq_model,
    get_rate_limits,
    get_api_timeout,
    get_max_tokens_per_request,
    estimate_tokens,
    get_simplification_prompt,
    get_translation_prompt,
    is_debug_mode,
)


# ==============================================================================
# Custom Exceptions
# ==============================================================================

class GroqAPIError(Exception):
    """Base exception for Groq API errors"""
    pass


class MissingAPIKeyError(GroqAPIError):
    """Raised when API key is not configured"""
    pass


class AuthenticationError(GroqAPIError):
    """Raised when API key is invalid"""
    pass


class RateLimitError(GroqAPIError):
    """Raised when rate limit is exceeded"""
    pass


class NetworkError(GroqAPIError):
    """Raised when network connection fails"""
    pass


class MaxRetriesExceeded(GroqAPIError):
    """Raised when max retries are exceeded"""
    pass


# ==============================================================================
# Rate Limit Enforcement
# ==============================================================================

def check_rate_limits(estimated_tokens: int, model_name: str) -> Tuple[bool, str]:
    """
    Check if request is within free tier limits
    
    Args:
        estimated_tokens: Estimated token count for request
        model_name: Model being used
        
    Returns:
        Tuple of (can_proceed, message)
    """
    if 'rate_limit_tracking' not in st.session_state:
        from utils.groq_config import initialize_rate_limit_tracking
        initialize_rate_limit_tracking()
    
    tracking = st.session_state.rate_limit_tracking
    limits = get_rate_limits()
    model_limits = limits.get(model_name, limits["llama-3.1-8b-instant"])
    
    # Reset counters if needed
    now = datetime.now()
    
    # Reset per-minute counters
    if (now - tracking["last_minute_reset"]).seconds >= 60:
        tracking["requests_this_minute"] = 0
        tracking["tokens_this_minute"] = 0
        tracking["last_minute_reset"] = now
    
    # Reset daily counters
    if now.date() > tracking["last_day_reset"].date():
        tracking["requests_today"] = 0
        tracking["tokens_today"] = 0
        tracking["last_day_reset"] = now
    
    # Check limits
    rpm_limit = model_limits["requests_per_minute"]
    tpm_limit = model_limits["tokens_per_minute"]
    rpd_limit = model_limits["requests_per_day"]
    
    if tracking["requests_this_minute"] >= rpm_limit:
        return False, f"Rate limit: {rpm_limit} requests/minute exceeded. Please wait."
    
    if tracking["tokens_this_minute"] + estimated_tokens > tpm_limit:
        return False, f"Token limit: {tpm_limit:,} tokens/minute would be exceeded."
    
    if tracking["requests_today"] >= rpd_limit:
        return False, f"Daily limit: {rpd_limit:,} requests/day exceeded. Try tomorrow."
    
    return True, "OK"


def record_request(token_usage: Dict[str, int]) -> None:
    """
    Record a request in rate limit tracking
    
    Args:
        token_usage: Dict with prompt_tokens, completion_tokens, total_tokens
    """
    if 'rate_limit_tracking' not in st.session_state:
        from utils.groq_config import initialize_rate_limit_tracking
        initialize_rate_limit_tracking()
    
    tracking = st.session_state.rate_limit_tracking
    
    tracking["requests_this_minute"] += 1
    tracking["requests_today"] += 1
    tracking["tokens_this_minute"] += token_usage.get("total_tokens", 0)
    tracking["tokens_today"] += token_usage.get("total_tokens", 0)
    tracking["last_request_time"] = datetime.now()


def update_limits_from_headers(headers: dict) -> None:
    """
    Update rate limit tracking from response headers
    
    Args:
        headers: Response headers from Groq API
    """
    if 'rate_limit_tracking' not in st.session_state:
        return
    
    tracking = st.session_state.rate_limit_tracking
    
    # Update from Groq's rate limit headers
    if "x-ratelimit-remaining-requests" in headers:
        tracking["remaining_requests"] = int(headers["x-ratelimit-remaining-requests"])
    
    if "x-ratelimit-remaining-tokens" in headers:
        tracking["remaining_tokens"] = int(headers["x-ratelimit-remaining-tokens"])
    
    if "x-ratelimit-reset-requests" in headers:
        tracking["reset_requests_time"] = headers["x-ratelimit-reset-requests"]
    
    if "x-ratelimit-reset-tokens" in headers:
        tracking["reset_tokens_time"] = headers["x-ratelimit-reset-tokens"]


# ==============================================================================
# Core API Functions
# ==============================================================================

def make_groq_request(
    messages: list,
    model: str,
    max_tokens: Optional[int] = None,
    temperature: float = 0.7,
    max_retries: int = 3
) -> Dict:
    """
    Make a request to Groq API with retry logic
    
    Args:
        messages: List of message dicts with role and content
        model: Model identifier
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        max_retries: Maximum retry attempts
        
    Returns:
        Response dict from Groq API
        
    Raises:
        Various GroqAPIError subclasses
    """
    # Get API key
    api_key = get_groq_api_key()
    if not api_key:
        raise MissingAPIKeyError(
            "Groq API key not found. Please add GROQ_API_KEY to Streamlit secrets."
        )
    
    # Get configuration
    endpoint = get_api_endpoint()
    timeout = get_api_timeout()
    if max_tokens is None:
        max_tokens = get_max_tokens_per_request()
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    # Retry loop
    for attempt in range(max_retries):
        try:
            if is_debug_mode():
                st.write(f"🔍 Debug: Request attempt {attempt + 1}/{max_retries}")
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # Update rate limits from headers
            update_limits_from_headers(dict(response.headers))
            
            # Handle response codes
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API key. Please check your Groq API key."
                )
            
            elif response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(response.headers.get("retry-after", 60))
                
                if attempt == max_retries - 1:
                    raise RateLimitError(
                        f"Rate limit exceeded. Please wait {retry_after} seconds."
                    )
                
                st.info(f"⏳ Rate limit hit. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            
            elif response.status_code >= 500:
                # Server error, retry
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    raise GroqAPIError(f"Server error: {response.status_code}")
            
            else:
                raise GroqAPIError(f"API error: {response.status_code} - {response.text}")
        
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise NetworkError("Request timed out. Please check your connection.")
            time.sleep(2 ** attempt)
        
        except requests.exceptions.ConnectionError:
            raise NetworkError("Failed to connect to Groq API. Check your internet.")
    
    raise MaxRetriesExceeded("Failed after maximum retries.")


# ==============================================================================
# Simplification
# ==============================================================================

def simplify_with_groq(
    user_input: str,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None
) -> str:
    """
    Simplify legal text using Groq API
    
    Args:
        user_input: Legal text to simplify
        max_tokens: Max tokens for response
        model: Model to use (defaults to selected model)
        
    Returns:
        Simplified text
        
    Raises:
        Various GroqAPIError subclasses
    """
    if not user_input or not user_input.strip():
        raise ValueError("Input text cannot be empty")
    
    # Get model
    if model is None:
        model = get_selected_groq_model()
    
    # Estimate tokens and check limits
    estimated_tokens = estimate_tokens(user_input)
    can_proceed, message = check_rate_limits(estimated_tokens, model)
    
    if not can_proceed:
        raise RateLimitError(message)
    
    # Prepare messages
    system_prompt = get_simplification_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    # Make request
    response = make_groq_request(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=0.7
    )
    
    # Extract result
    simplified_text = response["choices"][0]["message"]["content"]
    
    # Record usage
    usage = response.get("usage", {})
    record_request(usage)
    
    if is_debug_mode():
        st.write(f"🔍 Debug: Used {usage.get('total_tokens', 0)} tokens")
    
    return simplified_text


# ==============================================================================
# Translation
# ==============================================================================

def translate_with_groq(
    text: str,
    target_language: str,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None,
    max_retries: int = 3
) -> str:
    """
    Translate text using Groq API with retry logic
    
    Args:
        text: Text to translate
        target_language: Target language name (e.g., "Hindi", "Marathi")
        max_tokens: Max tokens for response
        model: Model to use
        max_retries: Maximum retry attempts
        
    Returns:
        Translated text
        
    Raises:
        Various GroqAPIError subclasses
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")
    
    # Get model
    if model is None:
        model = get_selected_groq_model()
    
    # Estimate tokens and check limits
    estimated_tokens = estimate_tokens(text)
    can_proceed, message = check_rate_limits(estimated_tokens, model)
    
    if not can_proceed:
        raise RateLimitError(message)
    
    # Prepare messages
    system_prompt = get_translation_prompt(target_language)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    
    # Retry loop for translation
    for attempt in range(max_retries):
        try:
            # Make request
            response = make_groq_request(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=0.5,  # Lower temperature for translation accuracy
                max_retries=1  # Handle retries at this level
            )
            
            # Extract result
            translated_text = response["choices"][0]["message"]["content"]
            
            # Record usage
            usage = response.get("usage", {})
            record_request(usage)
            
            return translated_text
        
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 60  # Wait 1 minute before retry
                st.info(f"⏳ Rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
        
        except GroqAPIError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                st.warning(f"⚠️ Translation error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
    
    raise MaxRetriesExceeded("Translation failed after maximum retries")


# ==============================================================================
# Utility Functions
# ==============================================================================

def check_groq_connection() -> Tuple[bool, str]:
    """
    Test Groq API connection
    
    Returns:
        Tuple of (success, message)
    """
    try:
        api_key = get_groq_api_key()
        if not api_key:
            return False, "No API key configured"
        
        # Make a minimal test request
        response = make_groq_request(
            messages=[{"role": "user", "content": "Hi"}],
            model="llama-3.1-8b-instant",
            max_tokens=5,
            max_retries=1
        )
        
        if response:
            return True, "✅ Connected to Groq successfully"
    
    except AuthenticationError:
        return False, "❌ Invalid API key"
    
    except NetworkError:
        return False, "❌ Network connection failed"
    
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"
    
    return False, "❌ Unknown error"


def get_groq_models_list() -> list:
    """Get list of available Groq models"""
    from utils.groq_config import get_available_groq_models
    models = get_available_groq_models()
    return list(models.keys())
