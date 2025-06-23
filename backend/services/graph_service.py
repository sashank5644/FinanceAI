"""Service for Neo4j graph operations."""

import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from config import settings
from models.graph_models import (
    CompanyNode, SectorNode, RelationshipEdge,
    CYPHER_TEMPLATES
)

logger = logging.getLogger(__name__)


class GraphService:
    """Service for managing the knowledge graph in Neo4j."""
    
    def __init__(self):
        """Initialize Neo4j connection."""
        self._driver = None
        
    @property
    def driver(self):
        """Get or create Neo4j driver."""
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password)
                )
                # Test connection
                self._driver.verify_connectivity()
                logger.info("Connected to Neo4j successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                raise
        return self._driver
    
    def close(self):
        """Close Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
    
    def create_company_node(self, company: CompanyNode) -> bool:
        """Create a company node in the graph."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MERGE (c:Company {symbol: $symbol})
                    SET c += $properties
                    RETURN c
                    """,
                    symbol=company.symbol,
                    properties=company.to_cypher_properties()
                )
                return result.single() is not None
        except Neo4jError as e:
            logger.error(f"Error creating company node: {e}")
            return False
    
    def create_sector_node(self, sector: SectorNode) -> bool:
        """Create a sector node in the graph."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MERGE (s:Sector {name: $name})
                    SET s += $properties
                    RETURN s
                    """,
                    name=sector.name,
                    properties={
                        "id": sector.id,
                        "description": sector.description,
                        "created_at": sector.created_at.isoformat()
                    }
                )
                return result.single() is not None
        except Neo4jError as e:
            logger.error(f"Error creating sector node: {e}")
            return False
    
    def create_relationship(self, edge: RelationshipEdge) -> bool:
        """Create a relationship between nodes."""
        try:
            with self.driver.session() as session:
                # Dynamic relationship creation
                result = session.run(
                    f"""
                    MATCH (a {{id: $source_id}})
                    MATCH (b {{id: $target_id}})
                    MERGE (a)-[r:{edge.relationship_type} {{
                        weight: $weight,
                        created_at: datetime($created_at)
                    }}]->(b)
                    RETURN r
                    """,
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    weight=edge.weight,
                    created_at=edge.created_at.isoformat()
                )
                return result.single() is not None
        except Neo4jError as e:
            logger.error(f"Error creating relationship: {e}")
            return False
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        try:
            with self.driver.session() as session:
                # Count nodes by type
                node_counts = session.run(
                    """
                    MATCH (n)
                    RETURN labels(n)[0] as type, count(n) as count
                    ORDER BY count DESC
                    """
                ).data()
                
                # Count relationships by type
                rel_counts = session.run(
                    """
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                    ORDER BY count DESC
                    """
                ).data()
                
                # Total counts
                total_nodes = sum(item['count'] for item in node_counts)
                total_edges = sum(item['count'] for item in rel_counts)
                
                return {
                    "total_nodes": total_nodes,
                    "total_edges": total_edges,
                    "node_types": {item['type']: item['count'] for item in node_counts},
                    "edge_types": {item['type']: item['count'] for item in rel_counts}
                }
        except Neo4jError as e:
            logger.error(f"Error getting graph stats: {e}")
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "node_types": {},
                "edge_types": {}
            }
    
    def get_subgraph(self, node_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """Get a subgraph centered on a node."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (center {id: $node_id})
                    OPTIONAL MATCH path = (center)-[r*1..$depth]-(connected)
                    WITH center, connected, relationships(path) as rels
                    RETURN 
                        collect(DISTINCT center) + collect(DISTINCT connected) as nodes,
                        collect(DISTINCT rels) as relationships
                    """,
                    node_id=node_id,
                    depth=max_depth
                ).single()
                
                if not result:
                    return {"nodes": [], "edges": []}
                
                # Format nodes
                nodes = []
                for node in result.get("nodes", []):
                    if node:
                        node_data = dict(node)
                        node_data["labels"] = list(node.labels)
                        nodes.append(node_data)
                
                # Format edges
                edges = []
                for rel_list in result.get("relationships", []):
                    if rel_list:
                        for rel in rel_list:
                            edges.append({
                                "source": rel.start_node["id"],
                                "target": rel.end_node["id"],
                                "type": rel.type,
                                "properties": dict(rel)
                            })
                
                return {"nodes": nodes, "edges": edges}
                
        except Neo4jError as e:
            logger.error(f"Error getting subgraph: {e}")
            return {"nodes": [], "edges": []}
    
    def get_full_graph(self, limit: int = 100) -> Dict[str, Any]:
        """Get the full graph (limited for performance)."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WITH n LIMIT $limit
                    OPTIONAL MATCH (n)-[r]-(m)
                    WHERE id(m) <= id(n)
                    RETURN 
                        collect(DISTINCT n) + collect(DISTINCT m) as nodes,
                        collect(DISTINCT r) as edges
                    """,
                    limit=limit
                )
                
                data = result.single()
                if not data:
                    return {"nodes": [], "edges": []}
                
                # Format nodes for visualization
                nodes = []
                node_ids = set()
                
                for node in data.get("nodes", []):
                    if node and node.id not in node_ids:
                        node_ids.add(node.id)
                        nodes.append({
                            "id": node.get("id", str(node.id)),
                            "name": node.get("name", node.get("symbol", "Unknown")),
                            "group": list(node.labels)[0] if node.labels else "Unknown",
                            "properties": dict(node)
                        })
                
                # Format edges for visualization
                edges = []
                for rel in data.get("edges", []):
                    if rel:
                        edges.append({
                            "source": rel.start_node.get("id", str(rel.start_node.id)),
                            "target": rel.end_node.get("id", str(rel.end_node.id)),
                            "type": rel.type,
                            "value": rel.get("weight", 1)
                        })
                
                return {"nodes": nodes, "links": edges}
                
        except Neo4jError as e:
            logger.error(f"Error getting full graph: {e}")
            return {"nodes": [], "links": []}
    
    def search_nodes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for nodes by name or symbol."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WHERE n.name =~ $pattern OR n.symbol =~ $pattern
                    RETURN n
                    LIMIT $limit
                    """,
                    pattern=f"(?i).*{query}.*",
                    limit=limit
                )
                
                nodes = []
                for record in result:
                    node = record["n"]
                    nodes.append({
                        "id": node.get("id"),
                        "name": node.get("name"),
                        "type": list(node.labels)[0] if node.labels else "Unknown",
                        "properties": dict(node)
                    })
                
                return nodes
                
        except Neo4jError as e:
            logger.error(f"Error searching nodes: {e}")
            return []


# Singleton instance
graph_service = GraphService()