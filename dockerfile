# Use a compatible base image for ARM64
FROM --platform=linux/arm64 python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies and update pip
RUN apt-get update && \
    apt-get install -y git && \
    pip install --upgrade pip

# Copy the requirements file first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and model
COPY legal_doc_simplifier.py .
COPY DeepSeek-R1-Distill-Qwen-1.5B ./DeepSeek-R1-Distill-Qwen-1.5B

# Set the environment variable for MPS backend
ENV PYTORCH_ENABLE_MPS_FALLBACK=1

# Run the Streamlit app
CMD ["streamlit", "run", "legal_doc_simplifier.py"]
