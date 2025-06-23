"""Knowledge graph API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from services.graph_service import graph_service
from models.graph_models import CompanyNode, SectorNode, RelationshipEdge

router = APIRouter()


class GraphNode(BaseModel):
    """Graph node model."""
    id: str
    type: str  # company, sector, indicator, event
    properties: Dict[str, Any]


class GraphEdge(BaseModel):
    """Graph edge model."""
    source: str
    target: str
    type: str  # owns, correlates_with, influences, belongs_to
    properties: Dict[str, Any] = {}


class GraphQuery(BaseModel):
    """Graph query model."""
    query_type: str  # neighbors, path, subgraph
    start_node: str
    end_node: Optional[str] = None
    max_depth: int = 3


@router.post("/query")
async def query_graph(query: GraphQuery):
    """Query the knowledge graph."""
    try:
        if query.query_type == "subgraph":
            result = graph_service.get_subgraph(
                node_id=query.start_node,
                max_depth=query.max_depth
            )
            return {
                "query": query.dict(),
                "results": result
            }
        else:
            # TODO: Implement other query types
            return {
                "query": query.dict(),
                "results": {
                    "nodes": [],
                    "edges": []
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nodes/company")
async def add_company_node(company: CompanyNode):
    """Add a company node to the knowledge graph."""
    try:
        success = graph_service.create_company_node(company)
        if success:
            return {"status": "created", "node_id": company.id}
        else:
            raise HTTPException(status_code=400, detail="Failed to create node")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nodes/sector")
async def add_sector_node(sector: SectorNode):
    """Add a sector node to the knowledge graph."""
    try:
        success = graph_service.create_sector_node(sector)
        if success:
            return {"status": "created", "node_id": sector.id}
        else:
            raise HTTPException(status_code=400, detail="Failed to create node")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edges")
async def add_edge(edge: RelationshipEdge):
    """Add an edge to the knowledge graph."""
    try:
        success = graph_service.create_relationship(edge)
        if success:
            return {"status": "created", "edge": edge.dict()}
        else:
            raise HTTPException(status_code=400, detail="Failed to create edge")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_graph_stats():
    """Get knowledge graph statistics."""
    try:
        stats = graph_service.get_graph_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualization")
async def get_visualization_data(limit: int = Query(100, le=500)):
    """Get graph data formatted for visualization."""
    try:
        graph_data = graph_service.get_full_graph(limit=limit)
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_nodes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, le=50)
):
    """Search for nodes by name or symbol."""
    try:
        if len(q) < 2:
            return {"results": []}
        
        results = graph_service.search_nodes(query=q, limit=limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node/{node_id}")
async def get_node_details(node_id: str):
    """Get detailed information about a specific node and its connections."""
    try:
        subgraph = graph_service.get_subgraph(node_id=node_id, max_depth=1)
        
        # Find the main node
        main_node = None
        for node in subgraph.get("nodes", []):
            if node.get("id") == node_id:
                main_node = node
                break
        
        if not main_node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        return {
            "node": main_node,
            "connections": subgraph
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))