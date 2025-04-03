#!/bin/bash
# Stop script for the Note Generator API
# This script stops the FastAPI server

# Set text colors
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${YELLOW}Stopping Note Generator API server...${NC}"

# Check if server is running
if pgrep -f "uvicorn src.note_gen.app:app" > /dev/null; then
    # Kill the server
    pkill -f "uvicorn src.note_gen.app:app"

    # Verify server was stopped
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Server stopped successfully.${NC}"
    else
        echo -e "${RED}Failed to stop server.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}No server was running.${NC}"
fi

exit 0
