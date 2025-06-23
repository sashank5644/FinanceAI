# api/routers/reports.py
"""Report generation API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from agents.report_agent import ReportAgent
from utils.db import get_db

router = APIRouter()

# Global report agent instance
report_agent = None


class ReportRequest(BaseModel):
    """Report generation request."""
    report_type: str  # research_summary, strategy_performance, market_analysis, portfolio_review
    title: str
    parameters: Dict[str, Any]
    format: str = "markdown"  # markdown, html, pdf


class ReportResponse(BaseModel):
    """Report response model."""
    report_id: str
    status: str
    title: str
    created_at: datetime
    download_url: Optional[str] = None
    content: Optional[str] = None


# In-memory storage for demo (use database in production)
reports_storage = {}


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks
):
    """Generate a new investment report."""
    global report_agent
    
    try:
        if report_agent is None:
            report_agent = ReportAgent()
            await report_agent.initialize()
        
        # Generate report
        result = await report_agent.generate_report(
            report_type=request.report_type,
            title=request.title,
            parameters=request.parameters
        )
        
        if result["success"]:
            report = result["report"]
            
            # Store report
            reports_storage[report["id"]] = report
            
            # Export to requested format
            if request.format != "markdown":
                export_result = await report_agent.export_report(report, request.format)
                if export_result["success"]:
                    report["export"] = export_result
            
            return ReportResponse(
                report_id=report["id"],
                status="completed",
                title=report["title"],
                created_at=datetime.fromisoformat(report["created_at"]),
                download_url=f"/api/v1/reports/{report['id']}/download",
                content=report["content"] if request.format == "markdown" else None
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_reports(
    limit: int = 10,
    offset: int = 0
):
    """List generated reports."""
    try:
        # Get reports from storage (sorted by creation date)
        all_reports = sorted(
            reports_storage.values(),
            key=lambda x: x["created_at"],
            reverse=True
        )
        
        # Paginate
        paginated = all_reports[offset:offset + limit]
        
        return {
            "total": len(all_reports),
            "limit": limit,
            "offset": offset,
            "items": [
                {
                    "id": report["id"],
                    "type": report["type"],
                    "title": report["title"],
                    "created_at": report["created_at"],
                    "word_count": report["metadata"]["word_count"],
                    "sections": len(report["metadata"]["sections"])
                }
                for report in paginated
            ]
        }
    except Exception as e:
        return {
            "total": 0,
            "limit": limit,
            "offset": offset,
            "items": [],
            "error": str(e)
        }


@router.get("/{report_id}")
async def get_report(report_id: str):
    """Get a specific report."""
    if report_id not in reports_storage:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = reports_storage[report_id]
    return {
        "report": report
    }


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = "markdown"
):
    """Download a report in specified format."""
    global report_agent
    
    if report_id not in reports_storage:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = reports_storage[report_id]
    
    try:
        if report_agent is None:
            report_agent = ReportAgent()
            await report_agent.initialize()
        
        # Export report
        export_result = await report_agent.export_report(report, format)
        
        if export_result["success"]:
            if format == "html":
                return HTMLResponse(
                    content=export_result["content"],
                    headers={
                        "Content-Disposition": f"attachment; filename={export_result['filename']}"
                    }
                )
            else:
                # For markdown or other text formats
                return HTMLResponse(
                    content=export_result["content"],
                    media_type="text/plain",
                    headers={
                        "Content-Disposition": f"attachment; filename={export_result['filename']}"
                    }
                )
        else:
            raise HTTPException(status_code=500, detail=export_result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/list")
async def get_report_templates():
    """Get available report templates."""
    return {
        "templates": [
            {
                "id": "research_summary",
                "name": "Research Summary Report",
                "description": "Comprehensive summary of research findings with actionable insights",
                "parameters": {
                    "research_ids": "List of research IDs to include",
                    "time_period": "Time period for analysis",
                    "focus_areas": "Specific areas to emphasize"
                }
            },
            {
                "id": "strategy_performance",
                "name": "Strategy Performance Report",
                "description": "Detailed analysis of strategy performance with risk metrics",
                "parameters": {
                    "strategy_ids": "List of strategy IDs to analyze",
                    "benchmark": "Benchmark for comparison",
                    "include_backtest": "Include backtest results"
                }
            },
            {
                "id": "market_analysis",
                "name": "Market Analysis Report",
                "description": "Current market conditions and outlook",
                "parameters": {
                    "sectors": "Sectors to analyze",
                    "indicators": "Key indicators to include",
                    "time_horizon": "Forward-looking time period"
                }
            },
            {
                "id": "portfolio_review",
                "name": "Portfolio Review Report",
                "description": "Comprehensive portfolio analysis and recommendations",
                "parameters": {
                    "portfolio_id": "Portfolio identifier",
                    "risk_analysis": "Include detailed risk analysis",
                    "rebalancing": "Include rebalancing recommendations"
                }
            }
        ]
    }


@router.post("/preview")
async def preview_report(request: ReportRequest):
    """Generate a preview of a report."""
    global report_agent
    
    try:
        if report_agent is None:
            report_agent = ReportAgent()
            await report_agent.initialize()
        
        # Generate a shortened preview
        preview_params = request.parameters.copy()
        preview_params["preview"] = True
        preview_params["max_length"] = 500
        
        result = await report_agent.generate_report(
            report_type=request.report_type,
            title=f"Preview: {request.title}",
            parameters=preview_params
        )
        
        if result["success"]:
            report = result["report"]
            # Truncate content for preview
            content = report["content"]
            if len(content) > 1000:
                content = content[:1000] + "\n\n... (Preview truncated)"
            
            return {
                "preview": content,
                "sections": report["metadata"]["sections"][:3],  # First 3 sections
                "estimated_pages": report["metadata"]["word_count"] // 250  # Rough estimate
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))