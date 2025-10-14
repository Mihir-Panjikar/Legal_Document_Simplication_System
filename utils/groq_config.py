"""
Groq Configuration Module
Manages API keys, models, and rate limits for Groq Cloud API
"""

import os
import streamlit as st
from datetime import datetime
from typing import Dict, Tuple


# ==============================================================================
# Groq API Configuration
# ==============================================================================

GROQ_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

# Production models (stable, not deprecated)
AVAILABLE_GROQ_MODELS = {
    "llama-3.1-8b-instant": {
        "name": "Llama 3.1 8B (Fast)",
        "speed": "560 tokens/sec",
        "description": "Fast inference, excellent for legal text",
        "use_case": "General simplification and translation",
    },
    "llama-3.3-70b-versatile": {
        "name": "Llama 3.3 70B (Quality)",
        "speed": "280 tokens/sec", 
        "description": "Higher quality for complex documents",
        "use_case": "Complex legal documents requiring nuance",
    },
}

DEFAULT_MODEL = "llama-3.1-8b-instant"


# ==============================================================================
# Rate Limits Configuration (Dynamic from Secrets)
# ==============================================================================

def get_rate_limits() -> Dict[str, Dict[str, int]]:
    """
    Get rate limits from Streamlit secrets with fallback to documented defaults.
    Allows admins to adjust limits without code changes if Groq updates them.
    
    Returns:
        Dict with rate limits per model
    """
    try:
        # Try to read from Streamlit secrets first (preferred)
        if hasattr(st, 'secrets'):
            return {
                "llama-3.1-8b-instant": {
                    "tokens_per_minute": int(st.secrets.get("GROQ_TPM_8B", 250000)),
                    "requests_per_minute": int(st.secrets.get("GROQ_RPM_8B", 1000)),
                    "requests_per_day": int(st.secrets.get("GROQ_RPD_8B", 14400)),
                },
                "llama-3.3-70b-versatile": {
                    "tokens_per_minute": int(st.secrets.get("GROQ_TPM_70B", 300000)),
                    "requests_per_minute": int(st.secrets.get("GROQ_RPM_70B", 1000)),
                    "requests_per_day": int(st.secrets.get("GROQ_RPD_70B", 14400)),
                },
            }
    except Exception:
        pass
    
    # Fallback to official documented defaults (as of Oct 2025)
    return {
        "llama-3.1-8b-instant": {
            "tokens_per_minute": 250000,
            "requests_per_minute": 1000,
            "requests_per_day": 14400,
        },
        "llama-3.3-70b-versatile": {
            "tokens_per_minute": 300000,
            "requests_per_minute": 1000,
            "requests_per_day": 14400,
        },
    }


def get_warning_threshold() -> int:
    """Get the warning threshold percentage from secrets or default to 80%"""
    try:
        if hasattr(st, 'secrets'):
            return int(st.secrets.get("RATE_LIMIT_WARNING_THRESHOLD", 80))
    except Exception:
        pass
    return 80


def get_max_tokens_per_request() -> int:
    """Get max tokens per request from secrets or default to 4096"""
    try:
        if hasattr(st, 'secrets'):
            return int(st.secrets.get("MAX_TOKENS_PER_REQUEST", 4096))
    except Exception:
        pass
    return 4096


def get_api_timeout() -> int:
    """Get API timeout in seconds from secrets or default to 30"""
    try:
        if hasattr(st, 'secrets'):
            return int(st.secrets.get("API_TIMEOUT_SECONDS", 30))
    except Exception:
        pass
    return 30


def is_debug_mode() -> bool:
    """Check if debug mode is enabled from secrets"""
    try:
        if hasattr(st, 'secrets'):
            return str(st.secrets.get("DEBUG_MODE", "false")).lower() == "true"
    except Exception:
        pass
    return False


# ==============================================================================
# API Key Management
# ==============================================================================

def get_groq_api_key() -> str:
    """
    Retrieve Groq API key from multiple sources in priority order:
    1. Session state (if already loaded)
    2. Streamlit secrets (preferred for deployment)
    3. Environment variables (local development)
    
    Returns:
        API key string or empty string if not found
    """
    # 1. Check session state first (cached)
    if hasattr(st, 'session_state') and 'groq_api_key' in st.session_state:
        if st.session_state.groq_api_key:
            return st.session_state.groq_api_key
    
    # 2. Check Streamlit secrets (preferred)
    try:
        if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
            if api_key and api_key != "gsk_your_actual_api_key_here":
                return api_key
    except Exception:
        pass
    
    # 3. Check environment variables (local dev)
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key and api_key != "gsk_your_actual_api_key_here":
        return api_key
    
    return ""


def validate_groq_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate Groq API key format
    
    Args:
        api_key: The API key to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is empty"
    
    if api_key == "gsk_your_actual_api_key_here":
        return False, "Please replace placeholder with your actual API key"
    
    if not api_key.startswith("gsk_"):
        return False, "Groq API keys should start with 'gsk_'"
    
    if len(api_key) < 20:
        return False, "API key seems too short"
    
    return True, ""


# ==============================================================================
# Model Management
# ==============================================================================

def get_available_groq_models() -> Dict[str, Dict[str, str]]:
    """Get list of available Groq models"""
    return AVAILABLE_GROQ_MODELS


def get_selected_groq_model() -> str:
    """
    Get currently selected Groq model
    
    Returns:
        Model identifier string
    """
    # Check session state
    if hasattr(st, 'session_state') and 'groq_model' in st.session_state:
        return st.session_state.groq_model
    
    # Check secrets for default
    try:
        if hasattr(st, 'secrets') and 'GROQ_DEFAULT_MODEL' in st.secrets:
            return st.secrets["GROQ_DEFAULT_MODEL"]
    except Exception:
        pass
    
    return DEFAULT_MODEL


def set_selected_groq_model(model_name: str) -> None:
    """
    Set the selected Groq model in session state
    
    Args:
        model_name: Model identifier
    """
    if model_name in AVAILABLE_GROQ_MODELS:
        st.session_state.groq_model = model_name


def get_model_info(model_name: str) -> Dict[str, str]:
    """
    Get information about a specific model
    
    Args:
        model_name: Model identifier
        
    Returns:
        Dict with model information
    """
    return AVAILABLE_GROQ_MODELS.get(model_name, {})


def get_recommended_model(task_type: str = "simplification", 
                          quality_preference: str = "fast") -> Tuple[str, str]:
    """
    Get recommended model based on task and quality preference
    
    Args:
        task_type: "simplification" or "translation"
        quality_preference: "fast" or "quality"
        
    Returns:
        Tuple of (model_name, reason)
    """
    if quality_preference == "quality":
        return "llama-3.3-70b-versatile", "Higher quality for complex content"
    else:
        return "llama-3.1-8b-instant", "Fast and efficient"


# ==============================================================================
# System Prompts
# ==============================================================================

SIMPLIFICATION_PROMPT = """You are a legal document simplification expert. Your task is to simplify complex legal text into clear, easy-to-understand language while maintaining accuracy and legal meaning.

Guidelines:
1. Replace complex legal jargon with everyday language
2. Break down long sentences into shorter, clearer ones
3. Maintain the original legal meaning and intent
4. Use active voice instead of passive where appropriate
5. Keep important legal terms but explain them in parentheses
6. Organize information in a logical, easy-to-follow structure

Simplify the following legal text:"""

TRANSLATION_PROMPT_TEMPLATE = """You are a professional legal translator. Translate the following legal text from English to {target_language}.

Guidelines:
1. Maintain the simplified, clear tone
2. Use appropriate legal terminology in the target language
3. Keep the meaning accurate and precise
4. Ensure cultural and linguistic appropriateness

Translate to {target_language}:"""


def get_simplification_prompt() -> str:
    """Get the system prompt for simplification"""
    return SIMPLIFICATION_PROMPT


def get_translation_prompt(target_language: str) -> str:
    """
    Get the system prompt for translation
    
    Args:
        target_language: Target language name
        
    Returns:
        Formatted translation prompt
    """
    return TRANSLATION_PROMPT_TEMPLATE.format(target_language=target_language)


# ==============================================================================
# Rate Limit Tracking
# ==============================================================================

def initialize_rate_limit_tracking() -> None:
    """Initialize rate limit tracking in session state"""
    if 'rate_limit_tracking' not in st.session_state:
        st.session_state.rate_limit_tracking = {
            "last_request_time": None,
            "requests_this_minute": 0,
            "requests_today": 0,
            "tokens_this_minute": 0,
            "tokens_today": 0,
            "last_minute_reset": datetime.now(),
            "last_day_reset": datetime.now(),
            # From response headers (more accurate)
            "remaining_requests": None,
            "remaining_tokens": None,
            "reset_requests_time": None,
            "reset_tokens_time": None,
        }


def get_free_tier_status() -> Dict:
    """
    Get current free tier usage status
    
    Returns:
        Dict with current usage statistics
    """
    if 'rate_limit_tracking' not in st.session_state:
        initialize_rate_limit_tracking()
    
    return st.session_state.rate_limit_tracking


# ==============================================================================
# Utility Functions
# ==============================================================================

def get_api_endpoint() -> str:
    """Get Groq API endpoint from secrets or default"""
    try:
        if hasattr(st, 'secrets') and 'GROQ_API_ENDPOINT' in st.secrets:
            return st.secrets["GROQ_API_ENDPOINT"]
    except Exception:
        pass
    return GROQ_API_ENDPOINT


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text
    Uses conservative estimation: ~1 token per 4 characters + 50% safety margin
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    base_estimate = len(text) / 4
    # Add 50% safety margin
    return int(base_estimate * 1.5)
