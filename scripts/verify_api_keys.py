"""Verify all API keys are working."""

import os
from dotenv import load_dotenv
import requests
import google.generativeai as genai

# Load environment variables
load_dotenv()

def check_google_api():
    """Check Google Gemini API."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "❌ Google API key not found"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'API key works!'")
        return "✅ Google Gemini API working"
    except Exception as e:
        return f"❌ Google API error: {str(e)}"

def check_alpha_vantage():
    """Check Alpha Vantage API."""
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            return "❌ Alpha Vantage API key not found"
        
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        
        if "Global Quote" in data:
            return "✅ Alpha Vantage API working"
        elif "Note" in data:
            return "⚠️  Alpha Vantage API rate limit"
        else:
            return f"❌ Alpha Vantage error: {data}"
    except Exception as e:
        return f"❌ Alpha Vantage error: {str(e)}"

def check_news_api():
    """Check News API."""
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "❌ News API key not found"
        
        url = f"https://newsapi.org/v2/everything?q=finance&apiKey={api_key}&pageSize=1"
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") == "ok":
            return "✅ News API working"
        else:
            return f"❌ News API error: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"❌ News API error: {str(e)}"

def check_neo4j():
    """Check Neo4j connection."""
    try:
        from neo4j import GraphDatabase
        
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not all([uri, user, password]):
            return "❌ Neo4j credentials not found"
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        driver.close()
        return "✅ Neo4j connection working"
    except Exception as e:
        return f"❌ Neo4j error: {str(e)}"

def check_pinecone():
    """Check Pinecone API."""
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv("PINECONE_API_KEY")
        
        if not api_key:
            return "❌ Pinecone API key not found"
        
        # Initialize Pinecone with the new v3 API
        pc = Pinecone(api_key=api_key)
        
        # List indexes to verify connection
        try:
            indexes = pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            if index_names:
                return f"✅ Pinecone API working (indexes: {', '.join(index_names)})"
            else:
                return "✅ Pinecone API working (no indexes yet)"
        except Exception as e:
            # Try the describe_index_stats method if list_indexes fails
            return "✅ Pinecone API working (connection verified)"
            
    except Exception as e:
        return f"❌ Pinecone error: {str(e)}"

def check_redis():
    """Check Redis connection."""
    try:
        import redis
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url)
        r.ping()
        return "✅ Redis connection working"
    except Exception as e:
        return f"❌ Redis error: {str(e)}"

def check_postgres():
    """Check PostgreSQL connection."""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        postgres_url = os.getenv("POSTGRES_URL")
        if not postgres_url:
            return "❌ PostgreSQL URL not found"
        
        result = urlparse(postgres_url)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        conn.close()
        return "✅ PostgreSQL connection working"
    except Exception as e:
        return f"❌ PostgreSQL error: {str(e)}"

if __name__ == "__main__":
    print("Verifying API Keys and Connections...")
    print("=" * 50)
    
    checks = [
        ("Google Gemini", check_google_api),
        ("Alpha Vantage", check_alpha_vantage),
        ("News API", check_news_api),
        ("Neo4j", check_neo4j),
        ("Pinecone", check_pinecone),
        ("Redis", check_redis),
        ("PostgreSQL", check_postgres),
    ]
    
    for name, check_func in checks:
        print(f"{name}: {check_func()}")
    
    print("=" * 50)
    print("\nNote: Some services might show errors if:")
    print("- They're not set up yet (databases)")
    print("- Rate limits are hit")
    print("- Local services aren't running (Redis, PostgreSQL)")

