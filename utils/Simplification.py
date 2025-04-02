import os
import torch
from functools import lru_cache
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from .formatter import format_messages
import ollama
import streamlit as st
from utils.ollama_config import get_selected_model, OLLAMA_API_HOST, SYSTEM_TEMPLATE

os.environ["TRANSFORMERS_OFFLINE"] = "1"

local_model_path = "./DeepSeek-R1-Distill-Qwen-1.5B"

# Cache Model Loading (Ensures it's loaded only once)


@lru_cache(maxsize=1)
def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,  # More efficient than 8-bit
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        llm_int8_enable_fp32_cpu_offload=True  # Prevents CPU-GPU mismatch issues
    )

    model = AutoModelForCausalLM.from_pretrained(
        local_model_path,
        device_map="auto",  # Optimizes layer placement across CUDA devices
        torch_dtype=torch.float16,
        quantization_config=quantization_config
    )

    tokenizer = AutoTokenizer.from_pretrained(local_model_path)

    return model, tokenizer, device


# Load model & tokenizer once
model, tokenizer, device = load_model()


@st.cache_data(show_spinner=True)
def simplify_document(user_input, max_tokens=4096):
    """
    Simplifies a legal document using Ollama.

    Args:
        user_input (str): The legal text to simplify
        max_tokens (int): Maximum number of tokens for the response

    Returns:
        str: The simplified text
    """
    try:
        # Get the selected model
        model = get_selected_model()

        # Set up the host
        client = ollama.Client(host=OLLAMA_API_HOST)

        # Generate simplified text using Ollama
        response = client.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_TEMPLATE
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            options={
                "num_predict": max_tokens,
                "temperature": 0.1  # Low temperature for more deterministic output
            }
        )

        # Extract the simplified text from the response
        simplified_text = response["message"]["content"]

        return simplified_text

    except Exception as e:
        st.error(f"Error during simplification: {str(e)}")
        # Return fallback message in case of error
        return "Sorry, there was an error simplifying the document. Please try again."


def check_model_availability():
    """
    Check if the selected Ollama model is available locally.
    If not, provide download instructions.

    Returns:
        bool: True if model is available, False otherwise
    """
    try:
        model = get_selected_model()
        client = ollama.Client(host=OLLAMA_API_HOST)
        models = client.list()

        # Check if our model is in the list
        available_models = [m["name"] for m in models["models"]]

        if model in available_models:
            return True
        else:
            st.warning(f"""
            The model '{model}' is not available locally. 
            To download it, open a terminal and run:
            ```
            ollama pull {model}
            ```
            """)
            return False

    except Exception as e:
        st.error(f"""
        Error connecting to Ollama: {str(e)}
        
        Please ensure Ollama is installed and running with:
        ```
        ollama serve
        ```
        
        Visit https://ollama.com to install Ollama.
        """)
        return False
