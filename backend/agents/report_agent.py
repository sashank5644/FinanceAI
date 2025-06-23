# agents/report_agent.py
"""Report generation agent for creating professional investment reports."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid
from io import BytesIO
import base64

from langchain.tools import Tool

from .base_agent import BaseAgent
from models.postgres_models import Research
from models.strategy_models import Strategy
from models.backtest_models import BacktestResult
from services.graph_service import graph_service
from utils.db import get_db

logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):
    """Agent for generating professional investment reports."""
    
    def __init__(self, mcp_servers: Optional[List[str]] = None):
        super().__init__(
            name="ReportAgent",
            description="Generates professional investment reports and summaries",
            model_name="gemini-1.5-pro",
            mcp_servers=mcp_servers or []
        )
    
    def get_system_prompt(self) -> str:
        """System prompt for report generation."""
        return """You are an expert financial analyst and report writer specializing in investment research.

Your role is to create professional, insightful, and actionable investment reports that:
1. Present complex financial data in a clear, structured manner
2. Provide executive summaries with key takeaways
3. Include data-driven insights and recommendations
4. Use appropriate financial terminology while remaining accessible
5. Highlight risks and opportunities objectively

Report sections should include:
- **Executive Summary**: Key findings and recommendations (1-2 pages)
- **Market Overview**: Current market conditions and trends
- **Company/Sector Analysis**: Detailed analysis with metrics
- **Investment Thesis**: Clear rationale for recommendations
- **Risk Assessment**: Key risks and mitigation strategies
- **Financial Metrics**: Relevant KPIs and comparisons
- **Recommendations**: Specific, actionable next steps

Always maintain a professional tone and support claims with data.
Format outputs in clean, structured Markdown suitable for conversion to PDF."""
    
    async def get_custom_tools(self) -> List[Tool]:
        """Get report-specific tools."""
        
        def gather_research_data(research_ids: List[str]) -> Dict[str, Any]:
            """Gather research data for report generation."""
            db = next(get_db())
            try:
                research_data = []
                for research_id in research_ids:
                    research = db.query(Research).filter(Research.id == research_id).first()
                    if research:
                        research_data.append({
                            "id": research.id,
                            "query": research.query,
                            "key_findings": research.key_findings,
                            "entities": research.entities_extracted,
                            "sentiment": research.sentiment_analysis,
                            "created_at": research.created_at.isoformat()
                        })
                
                return {
                    "success": True,
                    "data": research_data,
                    "count": len(research_data)
                }
            except Exception as e:
                logger.error(f"Error gathering research data: {e}")
                return {"success": False, "error": str(e)}
            finally:
                db.close()
        
        def gather_strategy_performance(strategy_ids: List[str]) -> Dict[str, Any]:
            """Gather strategy performance data for reports."""
            db = next(get_db())
            try:
                performance_data = []
                for strategy_id in strategy_ids:
                    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
                    if strategy:
                        # Get latest backtest
                        latest_backtest = db.query(BacktestResult).filter(
                            BacktestResult.strategy_id == strategy_id,
                            BacktestResult.status == "completed"
                        ).order_by(BacktestResult.created_at.desc()).first()
                        
                        performance_data.append({
                            "strategy_name": strategy.name,
                            "type": strategy.strategy_type.value if strategy.strategy_type else "unknown",
                            "risk_level": strategy.risk_level.value if strategy.risk_level else "unknown",
                            "instruments": strategy.instruments,
                            "backtest": {
                                "total_return": latest_backtest.total_return if latest_backtest else None,
                                "sharpe_ratio": latest_backtest.sharpe_ratio if latest_backtest else None,
                                "max_drawdown": latest_backtest.max_drawdown if latest_backtest else None,
                                "win_rate": latest_backtest.win_rate if latest_backtest else None
                            } if latest_backtest else None
                        })
                
                return {
                    "success": True,
                    "data": performance_data,
                    "count": len(performance_data)
                }
            except Exception as e:
                logger.error(f"Error gathering strategy data: {e}")
                return {"success": False, "error": str(e)}
            finally:
                db.close()
        
        def get_market_overview() -> Dict[str, Any]:
            """Get current market overview data."""
            try:
                # Get graph statistics
                graph_stats = graph_service.get_graph_stats()
                
                # Mock market data (in production, fetch from market data API)
                market_data = {
                    "indices": {
                        "sp500": {"value": 4750, "change": 0.85},
                        "nasdaq": {"value": 15250, "change": 1.25},
                        "dow": {"value": 37500, "change": 0.65}
                    },
                    "sectors": {
                        "technology": {"performance": 2.1, "trend": "bullish"},
                        "finance": {"performance": 0.8, "trend": "neutral"},
                        "healthcare": {"performance": -0.5, "trend": "bearish"}
                    },
                    "sentiment": "cautiously optimistic",
                    "vix": 15.5
                }
                
                return {
                    "success": True,
                    "data": {
                        "market_data": market_data,
                        "graph_stats": graph_stats,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            except Exception as e:
                logger.error(f"Error getting market overview: {e}")
                return {"success": False, "error": str(e)}
        
        def format_financial_table(data: List[Dict[str, Any]], columns: List[str]) -> str:
            """Format data as a markdown table."""
            if not data or not columns:
                return "No data available"
            
            # Create header
            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---" for _ in columns]) + " |"
            
            # Create rows
            rows = []
            for item in data:
                row_values = []
                for col in columns:
                    value = item.get(col, "N/A")
                    if isinstance(value, float):
                        value = f"{value:.2f}"
                    row_values.append(str(value))
                rows.append("| " + " | ".join(row_values) + " |")
            
            return "\n".join([header, separator] + rows)
        
        return [
            Tool(
                name="gather_research_data",
                func=gather_research_data,
                description="Gather research data for report generation"
            ),
            Tool(
                name="gather_strategy_performance",
                func=gather_strategy_performance,
                description="Gather strategy performance metrics"
            ),
            Tool(
                name="get_market_overview",
                func=get_market_overview,
                description="Get current market overview and sentiment"
            ),
            Tool(
                name="format_financial_table",
                func=format_financial_table,
                description="Format data as a professional markdown table"
            )
        ]
    
    async def generate_report(
        self,
        report_type: str,
        title: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a professional investment report."""
        
        report_id = f"report_{uuid.uuid4().hex[:8]}"
        
        try:
            # Define report prompts based on type
            prompts = {
                "research_summary": f"""
                Generate a comprehensive research summary report with the following:
                Title: {title}
                Parameters: {json.dumps(parameters, indent=2)}
                
                Include:
                1. Executive Summary (key findings and recommendations)
                2. Detailed Analysis of research findings
                3. Market Context and Trends
                4. Investment Opportunities identified
                5. Risk Factors to consider
                6. Actionable Recommendations
                
                Format as professional markdown with clear sections.
                """,
                
                "strategy_performance": f"""
                Generate a strategy performance report with the following:
                Title: {title}
                Parameters: {json.dumps(parameters, indent=2)}
                
                Include:
                1. Executive Summary of strategy performance
                2. Performance Metrics and KPIs
                3. Risk-Adjusted Returns Analysis
                4. Comparison to Benchmarks
                5. Strengths and Weaknesses
                6. Optimization Recommendations
                
                Use tables and bullet points for clarity.
                """,
                
                "market_analysis": f"""
                Generate a market analysis report with the following:
                Title: {title}
                Parameters: {json.dumps(parameters, indent=2)}
                
                Include:
                1. Current Market Overview
                2. Sector Performance Analysis
                3. Key Market Drivers
                4. Technical and Fundamental Indicators
                5. Market Outlook and Predictions
                6. Investment Strategy Recommendations
                
                Include relevant metrics and data visualizations descriptions.
                """,
                
                "portfolio_review": f"""
                Generate a portfolio review report with the following:
                Title: {title}
                Parameters: {json.dumps(parameters, indent=2)}
                
                Include:
                1. Portfolio Performance Summary
                2. Asset Allocation Analysis
                3. Risk Metrics and Exposure
                4. Individual Position Reviews
                5. Rebalancing Recommendations
                6. Forward-Looking Strategy
                
                Provide specific, actionable insights.
                """
            }
            
            prompt = prompts.get(report_type, prompts["research_summary"])
            
            # Generate report using AI
            result = await self.run(prompt)
            
            if result.get("success"):
                report_content = result.get("output", "")
                
                # Structure the report
                report = {
                    "id": report_id,
                    "type": report_type,
                    "title": title,
                    "content": report_content,
                    "format": "markdown",
                    "created_at": datetime.utcnow().isoformat(),
                    "parameters": parameters,
                    "metadata": {
                        "word_count": len(report_content.split()),
                        "sections": self._extract_sections(report_content)
                    }
                }
                
                logger.info(f"Generated report: {report_id}")
                return {
                    "success": True,
                    "report": report
                }
            else:
                raise Exception(f"Failed to generate report: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from markdown content."""
        sections = []
        for line in content.split('\n'):
            if line.startswith('#'):
                # Remove markdown formatting
                section = line.replace('#', '').strip()
                if section:
                    sections.append(section)
        return sections
    
    async def export_report(self, report: Dict[str, Any], format: str = "pdf") -> Dict[str, Any]:
        """Export report to different formats."""
        try:
            if format == "html":
                # Convert markdown to HTML
                html_content = self._markdown_to_html(report["content"])
                
                # Wrap in HTML template
                html_template = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{report['title']}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        h1, h2, h3 {{ color: #333; }}
                        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        .header {{ text-align: center; margin-bottom: 40px; }}
                        .footer {{ text-align: center; margin-top: 40px; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{report['title']}</h1>
                        <p>Generated on {report['created_at']}</p>
                    </div>
                    {html_content}
                    <div class="footer">
                        <p>Generated by Financial Research Agent</p>
                    </div>
                </body>
                </html>
                """
                
                return {
                    "success": True,
                    "format": "html",
                    "content": html_template,
                    "filename": f"{report['id']}.html"
                }
                
            elif format == "pdf":
                # For PDF, we'll return the HTML and let the frontend handle conversion
                html_result = await self.export_report(report, "html")
                if html_result["success"]:
                    return {
                        "success": True,
                        "format": "pdf",
                        "html_content": html_result["content"],
                        "filename": f"{report['id']}.pdf",
                        "message": "Use html_content for PDF generation"
                    }
                
            else:
                # Default to markdown
                return {
                    "success": True,
                    "format": "markdown",
                    "content": report["content"],
                    "filename": f"{report['id']}.md"
                }
                
        except Exception as e:
            logger.error(f"Export error: {e}")
            return {"success": False, "error": str(e)}
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML (simplified version)."""
        import re
        
        html = markdown_content
        
        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html)
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Lists
        html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
        
        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'
        
        # Clean up
        html = re.sub(r'<p>\s*</p>', '', html)
        html = re.sub(r'<p>(<h[1-3]>)', r'\1', html)
        html = re.sub(r'(</h[1-3]>)</p>', r'\1', html)
        
        return html