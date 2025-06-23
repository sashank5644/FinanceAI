#!/bin/bash
# start_mcp.sh - Start MCP servers for Financial Research Agent

echo "🚀 Starting MCP Servers..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${RED}Error: Virtual environment not activated${NC}"
    echo "Please activate your virtual environment first"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python -c "import websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing websockets..."
    pip install websockets
fi

# Create logs directory
mkdir -p logs

# Start MCP servers in background
echo -e "${GREEN}Starting MCP Server Manager...${NC}"
python run_mcp_servers.py > logs/mcp_servers.log 2>&1 &
MCP_PID=$!

echo "MCP Server Manager PID: $MCP_PID"

# Wait a moment for servers to start
sleep 3

# Check if servers are running
if ps -p $MCP_PID > /dev/null; then
    echo -e "${GREEN}✓ MCP Servers started successfully${NC}"
    echo ""
    echo "Servers running on:"
    echo "  - Financial Data Server: ws://localhost:8081"
    echo "  - Knowledge Graph Server: ws://localhost:8082"
    echo ""
    echo "Logs: tail -f logs/mcp_servers.log"
    echo "Stop: kill $MCP_PID"
    
    # Save PID for stop script
    echo $MCP_PID > .mcp_pid
else
    echo -e "${RED}✗ Failed to start MCP Servers${NC}"
    echo "Check logs/mcp_servers.log for errors"
    exit 1
fi