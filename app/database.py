"""
Database management module using SQLite with WAL mode.
Provides ACID transactions, relational schema for Atlas records, change history audit logs, and analytics.
"""
import sqlite3
import json
import io
import csv
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

from app.config import DATABASE_PATH, VERIFICATION_THRESHOLD_PERCENT
from app.models import (
    Scholarship,
    ScholarshipStatus,
    VerificationStatus,
    SourceType,
    ConfidenceBreakdown,
    HistoryRecord,
    CrawlRunSummary
)


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory and WAL mode enabled."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    """Initializes normalized database schema with indices."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Main Scholarships Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scholarships (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                source_type TEXT NOT NULL,
                official_source_url TEXT NOT NULL,
                application_url TEXT,
                discovery_url TEXT,
                amount_benefit TEXT NOT NULL,
                amount_numerical REAL,
                eligibility_summary TEXT NOT NULL,
                academic_requirements TEXT,
                education_level TEXT,
                income_criteria TEXT,
                age_criteria TEXT,
                gender_criteria TEXT,
                category_criteria TEXT,
                domicile_state TEXT,
                institution_requirements TEXT,
                opening_date TEXT,
                closing_date TEXT,
                documents_required TEXT, -- JSON array
                selection_process TEXT,
                renewal_requirements TEXT,
                current_status TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                confidence_breakdown TEXT, -- JSON object
                evidence_ledger TEXT, -- JSON object mapping fields to citations
                last_verified_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        
        # 2. Change Detection & Audit History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scholarship_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scholarship_id TEXT NOT NULL,
                scholarship_name TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT NOT NULL,
                change_type TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                source_url TEXT NOT NULL,
                evidence_snippet TEXT,
                FOREIGN KEY (scholarship_id) REFERENCES scholarships(id) ON DELETE CASCADE
            );
        """)
        
        # 3. Crawler Execution Runs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crawl_runs (
                run_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                run_type TEXT NOT NULL,
                total_discovered INTEGER NOT NULL,
                total_verified INTEGER NOT NULL,
                total_review_required INTEGER NOT NULL,
                changes_detected INTEGER NOT NULL,
                expired_detected INTEGER NOT NULL,
                avg_confidence REAL NOT NULL,
                status TEXT NOT NULL
            );
        """)
        
        # Indices for rapid querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scholarships_status ON scholarships(current_status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scholarships_verification ON scholarships(verification_status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scholarships_source_type ON scholarships(source_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_scholarship_id ON scholarship_history(scholarship_id);")
        
        conn.commit()


def _row_to_scholarship(row: sqlite3.Row) -> Scholarship:
    """Converts a SQLite database row into a Pydantic Scholarship model."""
    data = dict(row)
    
    # Parse JSON fields
    if data.get("documents_required"):
        try:
            data["documents_required"] = json.loads(data["documents_required"])
        except Exception:
            data["documents_required"] = []
    else:
        data["documents_required"] = []
        
    if data.get("confidence_breakdown"):
        try:
            cb_data = json.loads(data["confidence_breakdown"])
            data["confidence_breakdown"] = ConfidenceBreakdown(**cb_data)
        except Exception:
            data["confidence_breakdown"] = None
            
    if data.get("evidence_ledger"):
        try:
            data["evidence_ledger"] = json.loads(data["evidence_ledger"])
        except Exception:
            data["evidence_ledger"] = {}
    else:
        data["evidence_ledger"] = {}
        
    return Scholarship(**data)


def get_scholarship_by_id(scholarship_id: str) -> Optional[Scholarship]:
    """Retrieves a single scholarship by identifier."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scholarships WHERE id = ?", (scholarship_id,))
        row = cursor.fetchone()
        if row:
            return _row_to_scholarship(row)
        return None


def get_all_scholarships(
    query: Optional[str] = None,
    source_type: Optional[str] = None,
    status: Optional[str] = None,
    verification_status: Optional[str] = None,
    education_level: Optional[str] = None,
    domicile_state: Optional[str] = None,
    sort_by: str = "confidence_score",
    sort_order: str = "desc"
) -> List[Scholarship]:
    """Searches and filters scholarships with dynamic conditions."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        conditions = []
        params = []
        
        if query:
            q_wildcard = f"%{query.strip()}%"
            conditions.append("(name LIKE ? OR provider LIKE ? OR eligibility_summary LIKE ?)")
            params.extend([q_wildcard, q_wildcard, q_wildcard])
            
        if source_type and source_type != "ALL":
            conditions.append("source_type = ?")
            params.append(source_type)
            
        if status and status != "ALL":
            conditions.append("current_status = ?")
            params.append(status)
            
        if verification_status and verification_status != "ALL":
            conditions.append("verification_status = ?")
            params.append(verification_status)
            
        if education_level and education_level != "ALL":
            conditions.append("education_level LIKE ?")
            params.append(f"%{education_level}%")
            
        if domicile_state and domicile_state != "ALL":
            conditions.append("(domicile_state = ? OR domicile_state = 'All India')")
            params.append(domicile_state)
            
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        valid_sort_cols = {"confidence_score", "name", "updated_at", "closing_date", "amount_numerical"}
        col = sort_by if sort_by in valid_sort_cols else "confidence_score"
        direction = "DESC" if sort_order.lower() == "desc" else "ASC"
        
        sql = f"SELECT * FROM scholarships{where_clause} ORDER BY {col} {direction}"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [_row_to_scholarship(r) for r in rows]


def upsert_scholarship(scholarship: Scholarship) -> Tuple[Scholarship, List[HistoryRecord]]:
    """
    Inserts a new scholarship or updates an existing one, detecting field-level changes
    and writing detailed audit logs to scholarship_history without loss of lineage.
    """
    detected_changes: List[HistoryRecord] = []
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scholarships WHERE id = ?", (scholarship.id,))
        existing_row = cursor.fetchone()
        
        if existing_row is None:
            # New record discovery
            history_entry = HistoryRecord(
                scholarship_id=scholarship.id,
                scholarship_name=scholarship.name,
                field_name="RECORD_CREATED",
                old_value=None,
                new_value=f"Discovered and initialized with confidence {scholarship.confidence_score:.1f}%",
                change_type="CREATED",
                detected_at=now_str,
                source_url=scholarship.official_source_url,
                evidence_snippet=scholarship.evidence_ledger.get("name", {}).get("snippet") if scholarship.evidence_ledger else None
            )
            detected_changes.append(history_entry)
            
            cursor.execute("""
                INSERT INTO scholarships (
                    id, name, provider, source_type, official_source_url, application_url,
                    discovery_url, amount_benefit, amount_numerical, eligibility_summary,
                    academic_requirements, education_level, income_criteria, age_criteria,
                    gender_criteria, category_criteria, domicile_state, institution_requirements,
                    opening_date, closing_date, documents_required, selection_process,
                    renewal_requirements, current_status, verification_status, confidence_score,
                    confidence_breakdown, evidence_ledger, last_verified_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scholarship.id, scholarship.name, scholarship.provider, scholarship.source_type.value,
                scholarship.official_source_url, scholarship.application_url, scholarship.discovery_url,
                scholarship.amount_benefit, scholarship.amount_numerical, scholarship.eligibility_summary,
                scholarship.academic_requirements, scholarship.education_level, scholarship.income_criteria,
                scholarship.age_criteria, scholarship.gender_criteria, scholarship.category_criteria,
                scholarship.domicile_state, scholarship.institution_requirements, scholarship.opening_date,
                scholarship.closing_date, json.dumps(scholarship.documents_required),
                scholarship.selection_process, scholarship.renewal_requirements,
                scholarship.current_status.value, scholarship.verification_status.value,
                scholarship.confidence_score,
                json.dumps(scholarship.confidence_breakdown.model_dump()) if scholarship.confidence_breakdown else None,
                json.dumps(scholarship.evidence_ledger),
                scholarship.last_verified_at, scholarship.created_at, scholarship.updated_at
            ))
        else:
            # Existing record: Detect mutations across key fields
            existing = _row_to_scholarship(existing_row)
            fields_to_track = [
                ("closing_date", "DEADLINE_CHANGED"),
                ("amount_benefit", "AMOUNT_REVISED"),
                ("income_criteria", "INCOME_CRITERIA_UPDATED"),
                ("current_status", "STATUS_CHANGED"),
                ("verification_status", "VERIFICATION_STATUS_CHANGED"),
                ("application_url", "APPLICATION_URL_UPDATED"),
                ("confidence_score", "CONFIDENCE_RECALCULATED"),
            ]
            
            for field, change_type in fields_to_track:
                old_val = getattr(existing, field)
                new_val = getattr(scholarship, field)
                
                # Format for comparison
                old_str = str(old_val.value if hasattr(old_val, "value") else old_val)
                new_str = str(new_val.value if hasattr(new_val, "value") else new_val)
                
                # Check significant change
                is_changed = False
                if field == "confidence_score":
                    if abs(float(old_val or 0) - float(new_val or 0)) >= 1.0:
                        is_changed = True
                        old_str = f"{float(old_val or 0):.1f}%"
                        new_str = f"{float(new_val or 0):.1f}%"
                elif old_str != new_str and old_str != "Not specified" and new_str != "Not specified":
                    is_changed = True
                elif old_str != new_str and (old_str == "Not specified" or new_str == "Not specified"):
                    is_changed = True
                    
                if is_changed:
                    snippet = None
                    if scholarship.evidence_ledger and field in scholarship.evidence_ledger:
                        snippet = scholarship.evidence_ledger[field].get("snippet")
                        
                    h = HistoryRecord(
                        scholarship_id=scholarship.id,
                        scholarship_name=scholarship.name,
                        field_name=field,
                        old_value=old_str,
                        new_value=new_str,
                        change_type=change_type,
                        detected_at=now_str,
                        source_url=scholarship.official_source_url,
                        evidence_snippet=snippet
                    )
                    detected_changes.append(h)
                    
            cursor.execute("""
                UPDATE scholarships SET
                    name = ?, provider = ?, source_type = ?, official_source_url = ?,
                    application_url = ?, discovery_url = ?, amount_benefit = ?,
                    amount_numerical = ?, eligibility_summary = ?, academic_requirements = ?,
                    education_level = ?, income_criteria = ?, age_criteria = ?,
                    gender_criteria = ?, category_criteria = ?, domicile_state = ?,
                    institution_requirements = ?, opening_date = ?, closing_date = ?,
                    documents_required = ?, selection_process = ?, renewal_requirements = ?,
                    current_status = ?, verification_status = ?, confidence_score = ?,
                    confidence_breakdown = ?, evidence_ledger = ?, last_verified_at = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                scholarship.name, scholarship.provider, scholarship.source_type.value,
                scholarship.official_source_url, scholarship.application_url, scholarship.discovery_url,
                scholarship.amount_benefit, scholarship.amount_numerical, scholarship.eligibility_summary,
                scholarship.academic_requirements, scholarship.education_level, scholarship.income_criteria,
                scholarship.age_criteria, scholarship.gender_criteria, scholarship.category_criteria,
                scholarship.domicile_state, scholarship.institution_requirements, scholarship.opening_date,
                scholarship.closing_date, json.dumps(scholarship.documents_required),
                scholarship.selection_process, scholarship.renewal_requirements,
                scholarship.current_status.value, scholarship.verification_status.value,
                scholarship.confidence_score,
                json.dumps(scholarship.confidence_breakdown.model_dump()) if scholarship.confidence_breakdown else None,
                json.dumps(scholarship.evidence_ledger),
                scholarship.last_verified_at, now_str,
                scholarship.id
            ))
            
        # Insert audit history entries
        for h in detected_changes:
            cursor.execute("""
                INSERT INTO scholarship_history (
                    scholarship_id, scholarship_name, field_name, old_value, new_value,
                    change_type, detected_at, source_url, evidence_snippet
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                h.scholarship_id, h.scholarship_name, h.field_name, h.old_value,
                h.new_value, h.change_type, h.detected_at, h.source_url, h.evidence_snippet
            ))
            
        conn.commit()
        
    return scholarship, detected_changes


def get_history(scholarship_id: Optional[str] = None, limit: int = 100) -> List[HistoryRecord]:
    """Fetches audit history records across all scholarships or for a specific one."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if scholarship_id:
            cursor.execute("""
                SELECT * FROM scholarship_history 
                WHERE scholarship_id = ? 
                ORDER BY history_id DESC LIMIT ?
            """, (scholarship_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM scholarship_history 
                ORDER BY history_id DESC LIMIT ?
            """, (limit,))
        rows = cursor.fetchall()
        return [HistoryRecord(**dict(r)) for r in rows]


def get_metrics() -> Dict[str, Any]:
    """Calculates live intelligence metrics for the dashboard."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM scholarships")
        total_discovered = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE verification_status = 'VERIFIED'")
        verified_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE verification_status = 'REVIEW_REQUIRED'")
        review_required_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE current_status = 'ACTIVE'")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE current_status = 'EXPIRING_SOON'")
        expiring_soon_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE current_status = 'EXPIRED'")
        expired_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence_score) FROM scholarships")
        avg_conf = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT COUNT(*) FROM scholarship_history WHERE change_type != 'CREATED'")
        total_mutations = cursor.fetchone()[0]
        
        # Breakdown by Source Type
        cursor.execute("SELECT source_type, COUNT(*) FROM scholarships GROUP BY source_type")
        source_type_counts = dict(cursor.fetchall())
        
        # High confidence count >= 95%
        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE confidence_score >= 95.0")
        high_confidence_count = cursor.fetchone()[0]
        
        return {
            "total_discovered": total_discovered,
            "verified_count": verified_count,
            "review_required_count": review_required_count,
            "active_count": active_count,
            "expiring_soon_count": expiring_soon_count,
            "expired_count": expired_count,
            "avg_confidence": round(avg_conf, 1),
            "high_confidence_count": high_confidence_count,
            "total_changes_detected": total_mutations,
            "source_type_distribution": source_type_counts
        }


def record_crawl_run(summary: CrawlRunSummary):
    """Records metadata summary of a completed crawler execution."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO crawl_runs (
                run_id, started_at, completed_at, run_type, total_discovered,
                total_verified, total_review_required, changes_detected,
                expired_detected, avg_confidence, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            summary.run_id, summary.started_at, summary.completed_at, summary.run_type,
            summary.total_discovered, summary.total_verified, summary.total_review_required,
            summary.changes_detected, summary.expired_detected, summary.avg_confidence,
            summary.status
        ))
        conn.commit()


def get_recent_crawl_runs(limit: int = 10) -> List[CrawlRunSummary]:
    """Fetches recent crawler run logs."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crawl_runs ORDER BY started_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [CrawlRunSummary(**dict(r)) for r in rows]


def export_all_json() -> List[Dict[str, Any]]:
    """Exports all scholarship records with full evidence and breakdown as JSON serializable list."""
    scholarships = get_all_scholarships()
    return [s.model_dump() for s in scholarships]


def export_all_csv() -> str:
    """Exports key scholarship fields to a CSV string."""
    scholarships = get_all_scholarships()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "ID", "Name", "Provider", "Source Type", "Official URL", "Application URL",
        "Amount Benefit", "Income Limit", "Academic Req", "Education Level",
        "Category", "Gender", "Domicile", "Deadline", "Status", "Verification Status",
        "Confidence Score (%)", "Last Verified At"
    ])
    
    for s in scholarships:
        writer.writerow([
            s.id, s.name, s.provider, s.source_type.value, s.official_source_url, s.application_url,
            s.amount_benefit, s.income_criteria, s.academic_requirements, s.education_level,
            s.category_criteria, s.gender_criteria, s.domicile_state, s.closing_date,
            s.current_status.value, s.verification_status.value, f"{s.confidence_score:.1f}",
            s.last_verified_at
        ])
        
    return output.getvalue()
