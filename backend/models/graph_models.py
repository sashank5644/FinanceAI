"""Neo4j graph models and schemas."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NodeBase(BaseModel):
    """Base class for graph nodes."""
    id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    properties: Dict[str, Any] = {}


class CompanyNode(NodeBase):
    """Company node in the knowledge graph."""
    symbol: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    country: Optional[str] = None
    
    # Financial metrics
    revenue: Optional[float] = None
    earnings: Optional[float] = None
    pe_ratio: Optional[float] = None
    
    # Graph properties
    node_type: str = "Company"
    
    def to_cypher_properties(self) -> Dict[str, Any]:
        """Convert to Cypher query properties."""
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "sector": self.sector,
            "industry": self.industry,
            "market_cap": self.market_cap,
            "created_at": self.created_at.isoformat()
        }


class SectorNode(NodeBase):
    """Sector node in the knowledge graph."""
    description: Optional[str] = None
    parent_sector: Optional[str] = None
    
    # Performance metrics
    avg_pe_ratio: Optional[float] = None
    total_market_cap: Optional[float] = None
    
    node_type: str = "Sector"


class IndicatorNode(NodeBase):
    """Economic indicator node."""
    indicator_type: str  # gdp, inflation, interest_rate, etc.
    frequency: str  # daily, weekly, monthly, quarterly
    source: str
    
    # Latest value
    latest_value: Optional[float] = None
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    
    node_type: str = "Indicator"


class EventNode(NodeBase):
    """Market event node."""
    event_type: str  # earnings, merger, regulation, etc.
    date: datetime
    impact_score: Optional[float] = None  # -1 to 1
    
    # Event details
    description: str
    affected_entities: List[str] = []
    
    node_type: str = "Event"


class RelationshipEdge(BaseModel):
    """Edge/relationship in the knowledge graph."""
    source_id: str
    target_id: str
    relationship_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Common relationship types
    # OWNS, SUBSIDIARY_OF, COMPETITOR_OF, SUPPLIER_OF, CUSTOMER_OF
    # CORRELATES_WITH, INFLUENCES, BELONGS_TO_SECTOR


class GraphQuery(BaseModel):
    """Graph query parameters."""
    query_type: str  # neighbors, shortest_path, subgraph, pattern
    start_node_id: Optional[str] = None
    end_node_id: Optional[str] = None
    relationship_types: List[str] = []
    max_depth: int = 3
    filters: Dict[str, Any] = {}


# Cypher query templates
CYPHER_TEMPLATES = {
    "create_company": """
        CREATE (c:Company {
            id: $id,
            name: $name,
            symbol: $symbol,
            sector: $sector,
            industry: $industry,
            market_cap: $market_cap,
            created_at: datetime($created_at)
        })
        RETURN c
    """,
    
    "create_relationship": """
        MATCH (a {id: $source_id})
        MATCH (b {id: $target_id})
        CREATE (a)-[r:$relationship_type {
            weight: $weight,
            created_at: datetime($created_at)
        }]->(b)
        RETURN r
    """,
    
    "find_neighbors": """
        MATCH (n {id: $node_id})-[r]-(connected)
        WHERE r.weight >= $min_weight
        RETURN n, r, connected
        LIMIT $limit
    """,
    
    "find_path": """
        MATCH path = shortestPath(
            (start {id: $start_id})-[*..10]-(end {id: $end_id})
        )
        RETURN path
    """,
    
    "get_subgraph": """
        MATCH (n {id: $node_id})-[r*1..$depth]-(connected)
        RETURN n, r, connected
    """,
    
    "update_node_properties": """
        MATCH (n {id: $node_id})
        SET n += $properties
        SET n.updated_at = datetime()
        RETURN n
    """
}
