# Base image
FROM python:3.11-slim-bookworm

# Update packages and security fixes
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    ca-certificates && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/app/
COPY assets/ /app/assets/
COPY utils/ /app/utils/
COPY legal_doc_simplifier.py LICENSE.txt README.md /app/

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Set environment variables
ENV OLLAMA_API_HOST="http://ollama:11434"

# Expose Streamlit port
EXPOSE 8501

# Add a healthcheck script
COPY <<EOF /app/wait-for-ollama.sh
#!/bin/bash
set -e

MAX_RETRIES=30
RETRY_INTERVAL=2
OLLAMA_URL="\${OLLAMA_API_HOST}/api/tags"

echo "Waiting for Ollama to be ready at \${OLLAMA_URL}..."
for i in \$(seq 1 \$MAX_RETRIES); do
  if curl -s -f "\${OLLAMA_URL}" > /dev/null 2>&1; then
    echo "Ollama is ready!"
    exit 0
  fi
  echo "Waiting for Ollama to be ready... (\$i/\$MAX_RETRIES)"
  sleep \$RETRY_INTERVAL
done

echo "Timed out waiting for Ollama to be ready. The application may experience connection issues."
EOF

RUN chmod +x /app/wait-for-ollama.sh

# Add model check script
RUN echo '#!/bin/bash\n\
echo "Checking for required model..."\n\
curl -s "${OLLAMA_API_HOST}/api/pull" -d '"'"'{"name":"llama3"}'"'"' || echo "Model will be pulled on demand"\n\
' > /app/check-model.sh && chmod +x /app/check-model.sh

# Command to run the application
CMD ["/bin/bash", "-c", "/app/wait-for-ollama.sh && /app/check-model.sh && streamlit run legal_doc_simplifier.py --server.address=0.0.0.0"]
