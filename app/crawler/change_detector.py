from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any

from app.models import Scholarship, HistoryRecord, ScholarshipStatus


def detect_field_differences(
    existing: Scholarship,
    updated: Scholarship
) -> List[HistoryRecord]:
    """
    Compares two instances of the same scholarship and produces structured HistoryRecord diffs.
    """
    changes: List[HistoryRecord] = []
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    tracked_fields = [
        ("closing_date", "DEADLINE_CHANGED", "Application Deadline"),
        ("amount_benefit", "AMOUNT_REVISED", "Scholarship Benefit Amount"),
        ("income_criteria", "INCOME_CRITERIA_UPDATED", "Family Income Limit"),
        ("academic_requirements", "ELIGIBILITY_UPDATED", "Academic Requirements"),
        ("application_url", "APPLICATION_URL_UPDATED", "Official Application Link"),
        ("current_status", "STATUS_CHANGED", "Lifecycle Status"),
        ("verification_status", "VERIFICATION_STATUS_CHANGED", "Verification Status")
    ]
    
    for field_name, change_type, human_label in tracked_fields:
        old_val = getattr(existing, field_name)
        new_val = getattr(updated, field_name)
        
        old_str = str(old_val.value if hasattr(old_val, "value") else (old_val or "Not specified"))
        new_str = str(new_val.value if hasattr(new_val, "value") else (new_val or "Not specified"))
        
        if old_str != new_str:
            snippet = None
            if updated.evidence_ledger and field_name in updated.evidence_ledger:
                snippet = updated.evidence_ledger[field_name].get("snippet")
                
            # Distinguish deadline extension specifically
            if field_name == "closing_date" and old_str != "Not specified" and new_str != "Not specified":
                c_type = "DEADLINE_EXTENDED"
            else:
                c_type = change_type
                
            record = HistoryRecord(
                scholarship_id=updated.id,
                scholarship_name=updated.name,
                field_name=human_label,
                old_value=old_str,
                new_value=new_str,
                change_type=c_type,
                detected_at=now_str,
                source_url=updated.official_source_url,
                evidence_snippet=snippet
            )
            changes.append(record)
            
    # Check Confidence Score Shift
    if abs(existing.confidence_score - updated.confidence_score) >= 1.0:
        changes.append(HistoryRecord(
            scholarship_id=updated.id,
            scholarship_name=updated.name,
            field_name="Confidence Score",
            old_value=f"{existing.confidence_score:.1f}%",
            new_value=f"{updated.confidence_score:.1f}%",
            change_type="CONFIDENCE_RECALCULATED",
            detected_at=now_str,
            source_url=updated.official_source_url,
            evidence_snippet=f"Recalculated based on fresh verification audit (previous: {existing.confidence_score:.1f}%)"
        ))
        
    return changes
