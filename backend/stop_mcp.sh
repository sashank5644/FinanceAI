#!/bin/bash
# stop_mcp.sh - Stop MCP servers

echo "🛑 Stopping MCP Servers..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PID file exists
if [ -f .mcp_pid ]; then
    PID=$(cat .mcp_pid)
    
    # Check if process is running
    if ps -p $PID > /dev/null; then
        echo "Stopping MCP Server Manager (PID: $PID)..."
        kill $PID
        
        # Wait for graceful shutdown
        sleep 2
        
        # Force kill if still running
        if ps -p $PID > /dev/null; then
            echo "Force stopping..."
            kill -9 $PID
        fi
        
        echo -e "${GREEN}✓ MCP Servers stopped${NC}"
    else
        echo -e "${RED}MCP Servers not running${NC}"
    fi
    
    # Remove PID file
    rm .mcp_pid
else
    echo -e "${RED}No PID file found${NC}"
    echo "MCP Servers may not be running"
fi