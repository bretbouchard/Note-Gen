#!/bin/bash
# Run script for the Note Generator API
# This script starts the FastAPI server on port 8000 with hot reloading

# Set text colors
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Check if we're in the virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
fi

# Kill any existing uvicorn processes
echo -e "${BLUE}Checking for existing server processes...${NC}"
pkill -f "uvicorn src.note_gen.app:app" || true

# Start the server with hot reloading
echo -e "${GREEN}Starting server on port 8000 with hot reloading...${NC}"
echo -e "${GREEN}The server will automatically reload when code changes are detected.${NC}"
echo -e "${BLUE}Access the API at: http://localhost:8000${NC}"
echo -e "${BLUE}API documentation at: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

uvicorn src.note_gen.app:app --host 0.0.0.0 --port 8000 --reload --reload-dir src/note_gen
