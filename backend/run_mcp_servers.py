# run_mcp_servers.py
"""Script to run all MCP servers."""

import asyncio
import logging
import signal
import sys
from typing import List

from mcp_servers.financial_data_server import FinancialDataMCPServer
from mcp_servers.knowledge_graph_server import KnowledgeGraphMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manages multiple MCP servers."""
    
    def __init__(self):
        self.servers = []
        self.tasks = []
        self.running = False
    
    def add_server(self, server):
        """Add a server to manage."""
        self.servers.append(server)
    
    async def start_all(self):
        """Start all servers."""
        self.running = True
        
        # Create tasks for each server
        for server in self.servers:
            task = asyncio.create_task(server.start())
            self.tasks.append(task)
            logger.info(f"Started {server.__class__.__name__} on port {server.port}")
        
        # Wait for all tasks
        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("Server tasks cancelled")
    
    async def stop_all(self):
        """Stop all servers."""
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("All servers stopped")
    
    def handle_signal(self, sig, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {sig}")
        asyncio.create_task(self.stop_all())
        sys.exit(0)


async def main():
    """Main function to run MCP servers."""
    manager = MCPServerManager()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, manager.handle_signal)
    signal.signal(signal.SIGTERM, manager.handle_signal)
    
    # Create and add servers
    logger.info("Initializing MCP servers...")
    
    # Financial Data Server
    financial_server = FinancialDataMCPServer()
    manager.add_server(financial_server)
    
    # Knowledge Graph Server
    graph_server = KnowledgeGraphMCPServer()
    manager.add_server(graph_server)
    
    # Analysis Server
    from mcp_servers.analysis_server import AnalysisMCPServer
    analysis_server = AnalysisMCPServer()
    manager.add_server(analysis_server)
    
    # Document Server
    from mcp_servers.document_server import DocumentMCPServer
    document_server = DocumentMCPServer()
    manager.add_server(document_server)
    
    logger.info(f"Starting {len(manager.servers)} MCP servers...")
    
    # Start all servers
    await manager.start_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.error(f"Error running MCP servers: {e}")
        sys.exit(1)