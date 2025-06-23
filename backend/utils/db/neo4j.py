"""Neo4j database connection management."""

from neo4j import GraphDatabase
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

_driver: Optional[GraphDatabase.driver] = None


def get_neo4j_driver():
    """Get Neo4j driver instance."""
    global _driver
    
    if _driver is None:
        if not all([settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password]):
            logger.warning("Neo4j credentials not configured")
            return None
        
        try:
            _driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_lifetime=3600
            )
            _driver.verify_connectivity()
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    return _driver


def close_neo4j_driver():
    """Close Neo4j driver."""
    global _driver
    if _driver:
        _driver.close()
        _driver = None
        logger.info("Neo4j connection closed")


def run_query(query: str, parameters: dict = None):
    """Execute a Neo4j query."""
    driver = get_neo4j_driver()
    if not driver:
        raise Exception("Neo4j driver not available")
    
    with driver.session() as session:
        result = session.run(query, parameters or {})
        return list(result)
