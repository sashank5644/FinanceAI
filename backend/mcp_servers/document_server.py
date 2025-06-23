# mcp_servers/document_server.py
"""MCP Server for document processing and analysis."""

import logging
from typing import Dict, Any, List
import requests
from datetime import datetime
import PyPDF2
import io

from mcp.server import MCPServer
from config import settings

logger = logging.getLogger(__name__)


class DocumentMCPServer(MCPServer):
    """MCP Server providing document processing tools."""
    
    def __init__(self):
        super().__init__(host="0.0.0.0", port=8084)
        self.register_document_tools()
    
    def register_document_tools(self):
        """Register all document processing tools."""
        
        # SEC filing tool
        self.register_tool("fetch_sec_filing", {
            "name": "Fetch SEC Filing",
            "description": "Fetch SEC filings for a company",
            "category": "document",
            "parameters": {
                "symbol": {"type": "string", "required": True},
                "filing_type": {"type": "string", "default": "10-K",
                              "enum": ["10-K", "10-Q", "8-K", "DEF 14A"]}
            },
            "handler": self.fetch_sec_filing,
            "capabilities": ["sec", "document", "regulatory"]
        })
        
        # Earnings call transcript tool
        self.register_tool("get_earnings_transcript", {
            "name": "Get Earnings Transcript",
            "description": "Get latest earnings call transcript",
            "category": "document",
            "parameters": {
                "symbol": {"type": "string", "required": True},
                "quarter": {"type": "string", "required": False}
            },
            "handler": self.get_earnings_transcript,
            "capabilities": ["earnings", "document", "transcript"]
        })
        
        # PDF extraction tool
        self.register_tool("extract_pdf_content", {
            "name": "Extract PDF Content",
            "description": "Extract text content from PDF URL",
            "category": "document",
            "parameters": {
                "pdf_url": {"type": "string", "required": True},
                "max_pages": {"type": "integer", "default": 10}
            },
            "handler": self.extract_pdf_content,
            "capabilities": ["pdf", "extraction", "document"]
        })
        
        # Document summarization tool
        self.register_tool("summarize_document", {
            "name": "Summarize Document",
            "description": "Create a summary of a document",
            "category": "document",
            "parameters": {
                "text": {"type": "string", "required": True},
                "max_length": {"type": "integer", "default": 500}
            },
            "handler": self.summarize_document,
            "capabilities": ["summary", "nlp", "document"]
        })
        
        # Key information extraction
        self.register_tool("extract_key_info", {
            "name": "Extract Key Information",
            "description": "Extract key financial information from text",
            "category": "document",
            "parameters": {
                "text": {"type": "string", "required": True},
                "info_types": {"type": "array", "items": {"type": "string"},
                             "default": ["revenue", "earnings", "guidance"]}
            },
            "handler": self.extract_key_info,
            "capabilities": ["extraction", "nlp", "financial"]
        })
    
    async def fetch_sec_filing(
        self,
        symbol: str,
        filing_type: str = "10-K"
    ) -> Dict[str, Any]:
        """Fetch SEC filing for a company."""
        try:
            # In production, use SEC EDGAR API
            # For demo, return mock data
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "filing_type": filing_type,
                    "filing_date": "2024-02-15",
                    "url": f"https://www.sec.gov/edgar/{symbol}/{filing_type}",
                    "summary": f"Latest {filing_type} filing for {symbol}",
                    "key_sections": {
                        "business": "Company operates in technology sector...",
                        "risk_factors": "Market competition, regulatory changes...",
                        "financials": "Revenue increased 15% year-over-year..."
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching SEC filing: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_earnings_transcript(
        self,
        symbol: str,
        quarter: str = None
    ) -> Dict[str, Any]:
        """Get earnings call transcript."""
        try:
            # In production, fetch from transcript service
            # For demo, return mock data
            current_quarter = quarter or "Q4 2023"
            
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "quarter": current_quarter,
                    "date": "2024-01-25",
                    "participants": ["CEO", "CFO", "Analysts"],
                    "highlights": [
                        "Record revenue of $X billion",
                        "Expanded gross margins to Y%",
                        "Positive guidance for next quarter"
                    ],
                    "sentiment": "positive",
                    "key_quotes": {
                        "CEO": "We're seeing strong demand across all segments...",
                        "CFO": "Our financial position remains robust..."
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            return {"success": False, "error": str(e)}
    
    async def extract_pdf_content(
        self,
        pdf_url: str,
        max_pages: int = 10
    ) -> Dict[str, Any]:
        """Extract content from PDF."""
        try:
            # Download PDF
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Extract text
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            pages_to_read = min(len(pdf_reader.pages), max_pages)
            
            for page_num in range(pages_to_read):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            full_text = "\n".join(text_content)
            
            return {
                "success": True,
                "data": {
                    "url": pdf_url,
                    "total_pages": len(pdf_reader.pages),
                    "pages_extracted": pages_to_read,
                    "text": full_text[:5000],  # Limit text length
                    "word_count": len(full_text.split())
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            return {"success": False, "error": str(e)}
    
    async def summarize_document(
        self,
        text: str,
        max_length: int = 500
    ) -> Dict[str, Any]:
        """Summarize document text."""
        try:
            # Simple extractive summarization
            sentences = text.split(". ")
            
            # For demo, take first few sentences
            summary_sentences = sentences[:5]
            summary = ". ".join(summary_sentences) + "."
            
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return {
                "success": True,
                "data": {
                    "summary": summary,
                    "original_length": len(text),
                    "summary_length": len(summary),
                    "compression_ratio": len(summary) / len(text) if len(text) > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error summarizing: {e}")
            return {"success": False, "error": str(e)}
    
    async def extract_key_info(
        self,
        text: str,
        info_types: List[str] = ["revenue", "earnings", "guidance"]
    ) -> Dict[str, Any]:
        """Extract key information from text."""
        try:
            # Simple keyword-based extraction
            extracted_info = {}
            
            text_lower = text.lower()
            
            # Revenue patterns
            if "revenue" in info_types:
                revenue_keywords = ["revenue", "sales", "top line"]
                for keyword in revenue_keywords:
                    if keyword in text_lower:
                        # Find nearby numbers/percentages
                        extracted_info["revenue"] = "Revenue information found in text"
                        break
            
            # Earnings patterns
            if "earnings" in info_types:
                earnings_keywords = ["earnings", "eps", "profit", "income"]
                for keyword in earnings_keywords:
                    if keyword in text_lower:
                        extracted_info["earnings"] = "Earnings information found in text"
                        break
            
            # Guidance patterns
            if "guidance" in info_types:
                guidance_keywords = ["guidance", "outlook", "forecast", "expect"]
                for keyword in guidance_keywords:
                    if keyword in text_lower:
                        extracted_info["guidance"] = "Forward guidance found in text"
                        break
            
            return {
                "success": True,
                "data": {
                    "extracted_info": extracted_info,
                    "info_types_requested": info_types,
                    "info_types_found": list(extracted_info.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting info: {e}")
            return {"success": False, "error": str(e)}