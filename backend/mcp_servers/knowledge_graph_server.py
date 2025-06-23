# mcp_servers/knowledge_graph_server.py
"""MCP Server for knowledge graph operations."""

import logging
from typing import Dict, Any, List
from datetime import datetime

from mcp.server import MCPServer
from services.graph_service import graph_service
from models.graph_models import CompanyNode, SectorNode, RelationshipEdge

logger = logging.getLogger(__name__)


class KnowledgeGraphMCPServer(MCPServer):
    """MCP Server providing knowledge graph tools."""
    
    def __init__(self):
        super().__init__(host="0.0.0.0", port=8082)
        self.register_graph_tools()
    
    def register_graph_tools(self):
        """Register all knowledge graph tools."""
        
        # Node creation tools
        self.register_tool("create_company_node", {
            "name": "Create Company Node",
            "description": "Add a company to the knowledge graph",
            "category": "knowledge_graph",
            "parameters": {
                "symbol": {"type": "string", "required": True},
                "name": {"type": "string", "required": True},
                "sector": {"type": "string", "required": False},
                "market_cap": {"type": "number", "required": False}
            },
            "handler": self.create_company_node,
            "capabilities": ["write", "graph"]
        })
        
        # Relationship tools
        self.register_tool("create_relationship", {
            "name": "Create Relationship",
            "description": "Create a relationship between entities",
            "category": "knowledge_graph",
            "parameters": {
                "source_id": {"type": "string", "required": True},
                "target_id": {"type": "string", "required": True},
                "relationship_type": {"type": "string", "required": True,
                                    "enum": ["COMPETITOR_OF", "SUPPLIER_OF", "PARTNER_WITH", 
                                           "BELONGS_TO", "CORRELATES_WITH"]},
                "weight": {"type": "number", "default": 1.0}
            },
            "handler": self.create_relationship,
            "capabilities": ["write", "graph"]
        })
        
        # Query tools
        self.register_tool("find_related_entities", {
            "name": "Find Related Entities",
            "description": "Find entities related to a given node",
            "category": "knowledge_graph",
            "parameters": {
                "node_id": {"type": "string", "required": True},
                "relationship_type": {"type": "string", "required": False},
                "max_depth": {"type": "integer", "default": 2}
            },
            "handler": self.find_related_entities,
            "capabilities": ["read", "graph", "search"]
        })
        
        # Path finding
        self.register_tool("find_connection_path", {
            "name": "Find Connection Path",
            "description": "Find the shortest path between two entities",
            "category": "knowledge_graph",
            "parameters": {
                "start_node": {"type": "string", "required": True},
                "end_node": {"type": "string", "required": True}
            },
            "handler": self.find_connection_path,
            "capabilities": ["read", "graph", "analysis"]
        })
        
        # Graph analysis
        self.register_tool("analyze_entity_importance", {
            "name": "Analyze Entity Importance",
            "description": "Calculate importance metrics for an entity",
            "category": "knowledge_graph",
            "parameters": {
                "node_id": {"type": "string", "required": True}
            },
            "handler": self.analyze_entity_importance,
            "capabilities": ["read", "graph", "analysis"]
        })
        
        # Sector analysis
        self.register_tool("analyze_sector_relationships", {
            "name": "Analyze Sector Relationships",
            "description": "Analyze relationships within a sector",
            "category": "knowledge_graph",
            "parameters": {
                "sector": {"type": "string", "required": True}
            },
            "handler": self.analyze_sector_relationships,
            "capabilities": ["read", "graph", "analysis", "sector"]
        })
    
    async def create_company_node(
        self, 
        symbol: str, 
        name: str, 
        sector: str = None,
        market_cap: float = None
    ) -> Dict[str, Any]:
        """Create a company node in the graph."""
        try:
            node = CompanyNode(
                id=f"company_{symbol.lower()}",
                name=name,
                symbol=symbol,
                sector=sector,
                market_cap=market_cap
            )
            
            success = graph_service.create_company_node(node)
            
            if success:
                return {
                    "success": True,
                    "node_id": node.id,
                    "message": f"Created company node: {name}"
                }
            else:
                return {"success": False, "error": "Failed to create node"}
                
        except Exception as e:
            logger.error(f"Error creating company node: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        weight: float = 1.0
    ) -> Dict[str, Any]:
        """Create a relationship between entities."""
        try:
            edge = RelationshipEdge(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type,
                weight=weight
            )
            
            success = graph_service.create_relationship(edge)
            
            if success:
                return {
                    "success": True,
                    "message": f"Created {relationship_type} relationship"
                }
            else:
                return {"success": False, "error": "Failed to create relationship"}
                
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return {"success": False, "error": str(e)}
    
    async def find_related_entities(
        self,
        node_id: str,
        relationship_type: str = None,
        max_depth: int = 2
    ) -> Dict[str, Any]:
        """Find entities related to a given node."""
        try:
            subgraph = graph_service.get_subgraph(node_id, max_depth)
            
            # Filter by relationship type if specified
            if relationship_type and "edges" in subgraph:
                subgraph["edges"] = [
                    edge for edge in subgraph["edges"]
                    if edge.get("type") == relationship_type
                ]
            
            return {
                "success": True,
                "data": {
                    "center_node": node_id,
                    "related_entities": len(subgraph.get("nodes", [])) - 1,
                    "relationships": len(subgraph.get("edges", [])),
                    "subgraph": subgraph
                }
            }
            
        except Exception as e:
            logger.error(f"Error finding related entities: {e}")
            return {"success": False, "error": str(e)}
    
    async def find_connection_path(
        self,
        start_node: str,
        end_node: str
    ) -> Dict[str, Any]:
        """Find shortest path between two nodes."""
        try:
            # This would use Neo4j's shortest path algorithm
            # For now, return mock data
            return {
                "success": True,
                "data": {
                    "start": start_node,
                    "end": end_node,
                    "path_length": 3,
                    "path": [start_node, "intermediate_node", end_node],
                    "relationships": ["COMPETITOR_OF", "PARTNER_WITH"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_entity_importance(self, node_id: str) -> Dict[str, Any]:
        """Analyze the importance of an entity in the graph."""
        try:
            subgraph = graph_service.get_subgraph(node_id, max_depth=1)
            
            # Calculate metrics
            degree = len(subgraph.get("edges", []))
            
            # Categorize relationships
            relationship_types = {}
            for edge in subgraph.get("edges", []):
                rel_type = edge.get("type", "UNKNOWN")
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
            
            return {
                "success": True,
                "data": {
                    "node_id": node_id,
                    "degree_centrality": degree,
                    "relationship_breakdown": relationship_types,
                    "importance_score": min(degree / 10, 1.0),  # Simple scoring
                    "analysis": {
                        "highly_connected": degree > 10,
                        "hub_node": degree > 15,
                        "isolated": degree < 3
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing entity: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_sector_relationships(self, sector: str) -> Dict[str, Any]:
        """Analyze relationships within a sector."""
        try:
            # Get sector statistics
            stats = graph_service.get_graph_stats()
            
            # This would query Neo4j for sector-specific data
            # For now, return mock analysis
            return {
                "success": True,
                "data": {
                    "sector": sector,
                    "company_count": 5,
                    "internal_relationships": 12,
                    "external_relationships": 8,
                    "key_players": ["AAPL", "MSFT", "GOOGL"],
                    "relationship_density": 0.6,
                    "insights": [
                        "High competition within sector",
                        "Strong supplier relationships",
                        "Emerging partnerships"
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector: {e}")
            return {"success": False, "error": str(e)}