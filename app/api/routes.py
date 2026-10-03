"""
FastAPI REST API routes for Scholarship Intelligence Crawler.
Provides endpoints for scholarship search/filter, full record inspection,
confidence audit breakdown, change history, crawler execution, and exports.
"""
from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Optional, List, Dict, Any

from app.models import Scholarship, HistoryRecord, CrawlRunSummary
from app.database import (
    get_all_scholarships,
    get_scholarship_by_id,
    get_metrics,
    get_history,
    get_recent_crawl_runs,
    export_all_json,
    export_all_csv
)
from app.crawler.pipeline import CrawlerPipeline

router = APIRouter(prefix="/api", tags=["Scholarships"])
pipeline = CrawlerPipeline(simulate_network=True)


@router.get("/metrics")
def api_get_metrics():
    """Returns dashboard overview analytics and KPI counts."""
    return get_metrics()


@router.get("/scholarships")
def api_get_scholarships(
    q: Optional[str] = Query(None, description="Search keyword in name, provider, eligibility"),
    source_type: Optional[str] = Query("ALL", description="Filter by SourceType"),
    status: Optional[str] = Query("ALL", description="Filter by ScholarshipStatus"),
    verification_status: Optional[str] = Query("ALL", description="Filter by VerificationStatus"),
    education_level: Optional[str] = Query("ALL", description="Filter by EducationLevel"),
    domicile_state: Optional[str] = Query("ALL", description="Filter by DomicileState"),
    sort_by: str = Query("confidence_score", description="Field to sort by"),
    sort_order: str = Query("desc", description="asc or desc")
):
    """Returns a filtered and sorted list of scholarships."""
    results = get_all_scholarships(
        query=q,
        source_type=source_type,
        status=status,
        verification_status=verification_status,
        education_level=education_level,
        domicile_state=domicile_state,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "count": len(results),
        "data": [s.model_dump() for s in results]
    }


@router.get("/scholarships/{scholarship_id}")
def api_get_scholarship_detail(scholarship_id: str):
    """Returns the complete scholarship profile with evidence ledger, confidence breakdown and audit history."""
    scholarship = get_scholarship_by_id(scholarship_id)
    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship record not found")
        
    history = get_history(scholarship_id=scholarship_id, limit=50)
    
    return {
        "scholarship": scholarship.model_dump(),
        "history": [h.model_dump() for h in history]
    }


@router.get("/history")
def api_get_history(
    scholarship_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Returns historical mutation logs across all scholarships or for a specific one."""
    records = get_history(scholarship_id=scholarship_id, limit=limit)
    return {
        "count": len(records),
        "data": [r.model_dump() for r in records]
    }


@router.get("/crawl/runs")
def api_get_crawl_runs(limit: int = Query(10, ge=1, le=50)):
    """Returns summaries of recent automated crawler executions."""
    runs = get_recent_crawl_runs(limit=limit)
    return {
        "count": len(runs),
        "data": [r.model_dump() for r in runs]
    }


@router.post("/crawl/run")
async def api_trigger_crawl():
    """Triggers an automated crawler re-verification cycle."""
    summary, changes = await pipeline.run_full_crawler_cycle()
    return {
        "status": "success",
        "message": f"Crawler execution completed. Discovered: {summary.total_discovered}, Verified: {summary.total_verified}, Changes detected: {summary.changes_detected}",
        "summary": summary.model_dump(),
        "changes_detected_count": len(changes)
    }


@router.post("/crawl/simulate-change")
def api_simulate_change_detection():
    """
    Demonstrates Run 2 Change Detection by updating announcements
    (e.g. deadline extension, benefit increase, income limit update) and logging diffs.
    """
    summary, diffs = pipeline.simulate_run_2_changes()
    return {
        "status": "success",
        "message": f"Run 2 completed. Detected and logged {len(diffs)} mutations to audit history.",
        "summary": summary.model_dump(),
        "mutations": [d.model_dump() for d in diffs]
    }


@router.get("/export/json")
def api_export_json():
    """Exports entire database as a JSON dataset."""
    data = export_all_json()
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": "attachment; filename=scholarships_intelligence_export.json"}
    )


@router.get("/export/csv")
def api_export_csv():
    """Exports key scholarship records as a downloadable CSV."""
    csv_content = export_all_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scholarships_intelligence_export.csv"}
    )
