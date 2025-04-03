import ollama
import streamlit as st
from utils.ollama_config import get_selected_model, OLLAMA_API_HOST, SYSTEM_TEMPLATE


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
        import requests
        model = get_selected_model()

        # Get API host without http:// if present
        api_host = OLLAMA_API_HOST.replace("http://", "")

        # Direct HTTP request (more reliable)
        try:
            response = requests.get(f"http://{api_host}/api/tags")

            if response.status_code == 200:
                data = response.json()

                # Extract model names using different possible formats
                available_models = []

                # Format 1: "models" key with objects that have "name"
                if "models" in data and isinstance(data["models"], list):
                    for model_info in data["models"]:
                        if isinstance(model_info, dict) and "name" in model_info:
                            available_models.append(model_info["name"])

                # Format 2: Direct list of model names
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "name" in item:
                            available_models.append(item["name"])
                        elif isinstance(item, str):
                            available_models.append(item)

                # Check if model is available
                if model in available_models:
                    return True
                else:
                    # Check if model without version tag is available
                    base_model = model.split(":")[0] if ":" in model else model
                    base_matches = [
                        m for m in available_models if m.startswith(base_model)]

                    if base_matches:
                        st.info(
                            f"Using available model variant: {base_matches[0]}")
                        # Update the selected model to the available variant
                        from utils.ollama_config import set_selected_model
                        set_selected_model(base_matches[0])
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
            else:
                st.error(
                    f"Ollama API returned status code: {response.status_code}")
                return False

        except requests.exceptions.RequestException as req_error:
            st.error(f"HTTP request to Ollama failed: {str(req_error)}")
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
