#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

export COMPOSE_BAKE=true  # Enable better build performance

APP_NAME="Legal Document Simplification System"
COMPOSE_MAC="docker-compose.mac.yaml"
COMPOSE_NVIDIA="docker-compose.nvidia.yaml"
DOCKERFILE="./Dockerfile"  # Changed from "./docker" to "./Dockerfile"

# Function to detect system type
detect_system() {
    echo -e "${BLUE}Detecting system type...${NC}"
    
    # Check if running on Apple Silicon
    if [[ $(uname -m) == 'arm64' ]]; then
        echo -e "${GREEN}Detected Apple Silicon Mac${NC}"
        SYSTEM_TYPE="mac"
        COMPOSE_FILE=$COMPOSE_MAC
        return 0
    fi
    
    # Check for NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        echo -e "${GREEN}Detected NVIDIA GPU system${NC}"
        SYSTEM_TYPE="nvidia"
        COMPOSE_FILE=$COMPOSE_NVIDIA
        return 0
    fi
    
    # Default to NVIDIA configuration if detection fails
    echo -e "${YELLOW}Could not determine system type, defaulting to NVIDIA configuration${NC}"
    SYSTEM_TYPE="nvidia"
    COMPOSE_FILE=$COMPOSE_NVIDIA
}

# Function to start the application
start_app() {
    echo -e "${BLUE}Starting $APP_NAME...${NC}"
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    # Check if Dockerfile exists
    if [ ! -f "$DOCKERFILE" ]; then
        echo -e "${RED}Error: Dockerfile not found!${NC}"
        exit 1
    fi
    
    # Build and start the containers
    echo -e "${BLUE}Using configuration file: ${COMPOSE_FILE}${NC}"
    docker compose -f $COMPOSE_FILE up --build -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Application started successfully!${NC}"
        echo -e "${GREEN}📋 Access the application at: http://localhost:8501${NC}"
        
        # Check if we need to pull models
        if ! docker exec ollama-service ollama list 2>/dev/null | grep -q "deepseek"; then
            echo -e "${YELLOW}⚠️ No models detected. Would you like to pull the recommended model (deepseek-r1)?${NC} [y/N]"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                echo -e "${BLUE}Pulling deepseek-r1 model. This may take a while...${NC}"
                docker exec ollama-service ollama pull deepseek-r1
            else
                echo -e "${YELLOW}⚠️ No model pulled. You'll need to pull a model before using the application.${NC}"
                echo -e "${YELLOW}You can run 'docker exec ollama-service ollama pull MODEL_NAME'${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ Failed to start application. Check Docker logs for details.${NC}"
        exit 1
    fi
}

# Function to stop the application
stop_app() {
    echo -e "${BLUE}Stopping $APP_NAME...${NC}"
    
    # Stop containers using the appropriate compose file
    if [ -f "$COMPOSE_FILE" ]; then
        docker compose -f $COMPOSE_FILE down
        echo -e "${GREEN}✅ Application stopped successfully!${NC}"
    else
        echo -e "${RED}Error: $COMPOSE_FILE not found!${NC}"
        echo -e "${YELLOW}Attempting to stop containers manually...${NC}"
        docker stop legal-doc-simplifier ollama-service 2>/dev/null
        docker rm legal-doc-simplifier ollama-service 2>/dev/null
        echo -e "${GREEN}✅ Containers stopped and removed!${NC}"
    fi
}

# Function to clean up all resources
cleanup() {
    echo -e "\n${BLUE}Cleaning up resources...${NC}"
    
    # Stop any running containers
    stop_app
    
    echo -e "${GREEN}✅ Cleanup completed!${NC}"
}

# Function to display logs
show_logs() {
    echo -e "${BLUE}Showing logs for $APP_NAME...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to exit logs${NC}"
    docker compose -f $COMPOSE_FILE logs -f
}

# Function to show help
show_help() {
    echo -e "${BLUE}$APP_NAME Management Script${NC}"
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ./run_app.sh [command]"
    echo -e ""
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  start      Start the application (default if no command provided)"
    echo -e "  stop       Stop the application"
    echo -e "  restart    Restart the application"
    echo -e "  logs       Show application logs"
    echo -e "  status     Check the status of the application"
    echo -e "  cleanup    Remove containers, images, and volumes"
    echo -e "  help       Show this help message"
    echo -e ""
    echo -e "${YELLOW}Note:${NC} Run without arguments to start the app, press Ctrl+C to gracefully stop."
}

# Function to show status
show_status() {
    echo -e "${BLUE}Checking status of $APP_NAME...${NC}"
    
    # Check if containers are running
    if docker ps --format '{{.Names}}' | grep -q "legal-doc-simplifier"; then
        echo -e "${GREEN}✅ Application is running${NC}"
        echo -e "${GREEN}📋 Access the application at: http://localhost:8501${NC}"
        
        # Show container status
        echo -e "${YELLOW}Container Status:${NC}"
        docker ps -a --filter "name=legal-doc-simplifier" --filter "name=ollama-service"
        
        # Show models
        echo -e "${YELLOW}Available Models:${NC}"
        docker exec -it ollama-service ollama list 2>/dev/null || echo "Could not list models"
    else
        echo -e "${RED}❌ Application is not running${NC}"
    fi
}

# Function to keep the script running and handle Ctrl+C
keep_running() {
    echo -e "${BLUE}$APP_NAME is running. Press Ctrl+C to stop the application.${NC}"
    
    # Set up trap for cleanup on Ctrl+C (SIGINT)
    trap ctrl_c INT

    # Function to handle Ctrl+C
    function ctrl_c() {
        echo -e "\n${YELLOW}Detected Ctrl+C. Stopping application...${NC}"
        cleanup
        echo -e "${GREEN}Goodbye!${NC}"
        exit 0
    }
    
    # Show the logs while keeping the script running
    docker compose -f $COMPOSE_FILE logs -f
}

# Main execution
# Detect system first
detect_system

# Process command line arguments
case "$1" in
    start)
        start_app
        keep_running
        ;;
    stop)
        stop_app
        ;;
    restart)
        stop_app
        start_app
        keep_running
        ;;
    cleanup)
        cleanup
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    help)
        show_help
        ;;
    *)
        # Default action is to start if no command is provided
        if [ -z "$1" ]; then
            start_app
            keep_running
        else
            echo -e "${RED}Unknown command: $1${NC}"
            show_help
            exit 1
        fi
        ;;
esac

exit 0
