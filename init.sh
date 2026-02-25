#!/bin/bash

# MetisAI Project Initialization Script
# This script sets up the development environment and starts the servers

set -e  # Exit on error
set -o pipefail  # Fail on pipe errors

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MetisAI Project Initialization ===${NC}"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
check_requirements() {
    echo -e "${YELLOW}Checking required tools...${NC}"

    # Check Docker
    if command_exists docker; then
        echo -e "  ✅ Docker installed"
    else
        echo -e "  ❌ Docker not found"
        echo -e "Please install Docker: https://www.docker.com/get-started"
        return 1
    fi

    # Check Docker Compose
    if command_exists docker-compose; then
        echo -e "  ✅ Docker Compose installed"
    else
        echo -e "  ❌ Docker Compose not found"
        return 1
    fi

    # Check Python
    if command_exists python3; then
        echo -e "  ✅ Python 3 installed"
    else
        echo -e "  ❌ Python 3 not found"
        return 1
    fi

    # Check Node.js
    if command_exists node; then
        echo -e "  ✅ Node.js installed"
    else
        echo -e "  ❌ Node.js not found"
        return 1
    fi

    # Check Git
    if command_exists git; then
        echo -e "  ✅ Git installed"
    else
        echo -e "  ❌ Git not found"
        return 1
    fi

    echo
    echo -e "${GREEN}All required tools installed${NC}"
    echo
}

# Create directories if they don't exist
setup_directories() {
    echo -e "${YELLOW}Creating project directories...${NC}"

    mkdir -p backend
    mkdir -p frontend
    mkdir -p data

    echo -e "  ✅ Directories created"
    echo
}

# Initialize backend
setup_backend() {
    echo -e "${YELLOW}Setting up backend...${NC}"

    cd backend

    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate venv and install dependencies
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo -e "${RED}Failed to activate virtual environment${NC}"
        cd ..
        return 1
    fi

    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo "Creating requirements.txt..."
        cat > requirements.txt << EOF
fastapi
uvicorn
sqlalchemy
pydantic
python-jose[cryptography]
python-multipart
python-socketio
litellm
EOF
    fi

    echo "Installing Python dependencies..."
    pip install -q -r requirements.txt

    cd ..
    echo -e "  ✅ Backend setup complete"
    echo
}

# Initialize frontend
setup_frontend() {
    echo -e "${YELLOW}Setting up frontend...${NC}"

    cd frontend

    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo "Initializing Vite + React + TypeScript project..."
        npm create vite@latest . -- --template react-ts
    fi

    echo "Installing npm dependencies..."
    npm install -q

    cd ..
    echo -e "  ✅ Frontend setup complete"
    echo
}

# Create docker-compose.yml if it doesn't exist
create_docker_config() {
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${YELLOW}Creating docker-compose.yml...${NC}"

        cat > docker-compose.yml << EOF
version: "3.8"

services:
  backend:
    build: ./backend
    container_name: metisai-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/metisai.db
    volumes:
      - ./data:/app/data
    depends_on:
      - frontend

  frontend:
    build: ./frontend
    container_name: metisai-frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
EOF
    fi

    echo -e "  ✅ Docker configuration created"
    echo
}

# Start development servers
start_servers() {
    echo -e "${YELLOW}Starting development servers...${NC}"

    echo "=== Starting Backend ==="
    cd backend
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    fi
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..

    echo "=== Starting Frontend ==="
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo -e "  ✅ Servers starting..."
    echo
}

# Main execution
main() {
    check_requirements
    setup_directories
    setup_backend
    setup_frontend
    create_docker_config

    echo -e "${GREEN}=== Initialization complete! ===${NC}"
    echo
    echo -e "Next steps:"
    echo "1. Read task.json to select your next task"
    echo "2. Implement the task following the workflow"
    echo "3. Test thoroughly and update progress.txt"
    echo
    echo -e "Servers will start in the background..."
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:5173"
    echo

    start_servers
}

# Cleanup on script exit
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
}

# Trap for clean exit
trap cleanup EXIT

# Execute main function
main "$@"