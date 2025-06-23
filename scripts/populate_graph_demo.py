"""Populate Neo4j with demo financial data."""

import uuid
from datetime import datetime
from services.graph_service import graph_service
from models.graph_models import CompanyNode, SectorNode, RelationshipEdge

def create_demo_data():
    """Create demo nodes and relationships."""
    print("🚀 Starting to populate graph with demo data...")
    
    # Create sectors
    sectors = [
        {"name": "Technology", "description": "Technology companies"},
        {"name": "Finance", "description": "Financial services"},
        {"name": "Healthcare", "description": "Healthcare and pharmaceuticals"},
        {"name": "Consumer", "description": "Consumer goods and services"},
        {"name": "Energy", "description": "Energy and utilities"}
    ]
    
    sector_nodes = {}
    for sector_data in sectors:
        sector = SectorNode(
            id=f"sector_{sector_data['name'].lower()}",
            name=sector_data["name"],
            description=sector_data["description"]
        )
        if graph_service.create_sector_node(sector):
            sector_nodes[sector.name] = sector
            print(f"✓ Created sector: {sector.name}")
    
    # Create companies
    companies = [
        # Tech companies
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "market_cap": 3000000000000},
        {"symbol": "MSFT", "name": "Microsoft Corp.", "sector": "Technology", "market_cap": 2800000000000},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "market_cap": 1800000000000},
        {"symbol": "META", "name": "Meta Platforms", "sector": "Technology", "market_cap": 900000000000},
        {"symbol": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology", "market_cap": 1100000000000},
        
        # Finance companies
        {"symbol": "JPM", "name": "JPMorgan Chase", "sector": "Finance", "market_cap": 500000000000},
        {"symbol": "BAC", "name": "Bank of America", "sector": "Finance", "market_cap": 300000000000},
        {"symbol": "GS", "name": "Goldman Sachs", "sector": "Finance", "market_cap": 120000000000},
        
        # Healthcare companies
        {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "market_cap": 400000000000},
        {"symbol": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare", "market_cap": 250000000000},
        {"symbol": "UNH", "name": "UnitedHealth", "sector": "Healthcare", "market_cap": 500000000000},
        
        # Consumer companies
        {"symbol": "AMZN", "name": "Amazon.com", "sector": "Consumer", "market_cap": 1700000000000},
        {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Consumer", "market_cap": 450000000000},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer", "market_cap": 800000000000},
    ]
    
    company_nodes = {}
    for company_data in companies:
        company = CompanyNode(
            id=f"company_{company_data['symbol'].lower()}",
            name=company_data["name"],
            symbol=company_data["symbol"],
            sector=company_data["sector"],
            market_cap=company_data["market_cap"]
        )
        if graph_service.create_company_node(company):
            company_nodes[company.symbol] = company
            print(f"✓ Created company: {company.name}")
    
    # Create relationships
    relationships = [
        # Companies to sectors
        ("company_aapl", "sector_technology", "BELONGS_TO", 1.0),
        ("company_msft", "sector_technology", "BELONGS_TO", 1.0),
        ("company_googl", "sector_technology", "BELONGS_TO", 1.0),
        ("company_meta", "sector_technology", "BELONGS_TO", 1.0),
        ("company_nvda", "sector_technology", "BELONGS_TO", 1.0),
        ("company_jpm", "sector_finance", "BELONGS_TO", 1.0),
        ("company_bac", "sector_finance", "BELONGS_TO", 1.0),
        ("company_gs", "sector_finance", "BELONGS_TO", 1.0),
        ("company_jnj", "sector_healthcare", "BELONGS_TO", 1.0),
        ("company_pfe", "sector_healthcare", "BELONGS_TO", 1.0),
        ("company_unh", "sector_healthcare", "BELONGS_TO", 1.0),
        ("company_amzn", "sector_consumer", "BELONGS_TO", 1.0),
        ("company_wmt", "sector_consumer", "BELONGS_TO", 1.0),
        ("company_tsla", "sector_consumer", "BELONGS_TO", 1.0),
        
        # Competitor relationships
        ("company_aapl", "company_msft", "COMPETITOR_OF", 0.9),
        ("company_msft", "company_aapl", "COMPETITOR_OF", 0.9),
        ("company_googl", "company_meta", "COMPETITOR_OF", 0.8),
        ("company_meta", "company_googl", "COMPETITOR_OF", 0.8),
        ("company_jpm", "company_bac", "COMPETITOR_OF", 0.9),
        ("company_bac", "company_jpm", "COMPETITOR_OF", 0.9),
        ("company_amzn", "company_wmt", "COMPETITOR_OF", 0.7),
        ("company_wmt", "company_amzn", "COMPETITOR_OF", 0.7),
        
        # Supplier relationships
        ("company_nvda", "company_tsla", "SUPPLIER_OF", 0.6),
        ("company_nvda", "company_meta", "SUPPLIER_OF", 0.8),
        ("company_nvda", "company_amzn", "SUPPLIER_OF", 0.7),
        
        # Partnership relationships
        ("company_msft", "company_nvda", "PARTNER_WITH", 0.8),
        ("company_nvda", "company_msft", "PARTNER_WITH", 0.8),
        
        # Correlation relationships (companies that tend to move together)
        ("company_aapl", "company_nvda", "CORRELATES_WITH", 0.7),
        ("company_googl", "company_msft", "CORRELATES_WITH", 0.75),
        ("company_jpm", "company_gs", "CORRELATES_WITH", 0.85),
    ]
    
    for source, target, rel_type, weight in relationships:
        edge = RelationshipEdge(
            source_id=source,
            target_id=target,
            relationship_type=rel_type,
            weight=weight
        )
        if graph_service.create_relationship(edge):
            print(f"✓ Created relationship: {source} -{rel_type}-> {target}")
    
    # Get and display stats
    stats = graph_service.get_graph_stats()
    print("\n📊 Graph Statistics:")
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Total edges: {stats['total_edges']}")
    print(f"Node types: {stats['node_types']}")
    print(f"Edge types: {stats['edge_types']}")
    
    print("\n✅ Demo data population complete!")


if __name__ == "__main__":
    try:
        create_demo_data()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        graph_service.close()