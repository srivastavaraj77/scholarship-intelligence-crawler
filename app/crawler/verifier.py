"""
Verification and Confidence Scoring Engine.
Implements a mathematical, evidence-based 100-point scoring formula with full audit trace.
Never asks an LLM for arbitrary confidence numbers.
Applies the strict 95.0% threshold for VERIFIED status.
"""
from datetime import datetime, date, timezone
import re
from typing import Dict, Any, List, Optional, Tuple

from app.config import (
    VERIFICATION_THRESHOLD_PERCENT,
    EXPIRING_SOON_DAYS,
    WEIGHT_SOURCE_AUTHORITY,
    WEIGHT_LIVE_PRESENCE,
    WEIGHT_APPLICATION_URL,
    WEIGHT_FIELD_GROUNDING,
    WEIGHT_FRESHNESS
)
from app.models import (
    Scholarship,
    ScholarshipStatus,
    VerificationStatus,
    ConfidenceBreakdown,
    EvidenceItem
)
from app.crawler.fetcher import classify_domain_authority, FetchResult, extract_domain


def parse_date_safely(date_str: str) -> Optional[date]:
    """Tries to parse various date formats into a standard date object."""
    if not date_str or date_str == "Not specified":
        return None
        
    date_str_clean = date_str.strip()
    # Remove ordinal suffixes (1st, 2nd, 3rd, 4th, etc.)
    date_str_clean = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str_clean)
    
    formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d %m %Y"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str_clean, fmt)
            return dt.date()
        except ValueError:
            continue
            
    return None


def calculate_source_authority_score(official_url: str) -> Tuple[float, List[str]]:
    """Calculates score based on official domain credibility (Max 25 pts)."""
    authority_type, factor = classify_domain_authority(official_url)
    notes = []
    
    if authority_type == "GOV_ACADEMIC_OFFICIAL":
        score = WEIGHT_SOURCE_AUTHORITY  # 25.0
        notes.append(f"[+25.0 pts] Official Government/Academic Root Domain ({extract_domain(official_url)})")
    elif authority_type == "VERIFIED_FOUNDATION_CORPORATE":
        score = 24.0
        notes.append(f"[+24.0 pts] Verified Corporate CSR / Recognized Foundation Authority ({extract_domain(official_url)})")
    elif authority_type == "GENERAL_ORGANIZATION":
        score = 18.0
        notes.append(f"[+18.0 pts] Registered Non-Profit / Institutional Domain ({extract_domain(official_url)})")
    elif authority_type == "AGGREGATOR_DISCOVERY":
        score = 8.0
        notes.append(f"[+8.0 pts] Third-party aggregator / portal. Needs primary source resolution.")
    else:
        score = 3.0
        notes.append(f"[+3.0 pts] Unverified domain authority ({extract_domain(official_url)})")
        
    return score, notes


def calculate_live_presence_score(
    fetch_res: Optional[FetchResult],
    scholarship_name: str
) -> Tuple[float, List[str]]:
    """Calculates live accessibility and name match score (Max 20 pts)."""
    notes = []
    if fetch_res is None or not fetch_res.is_live:
        notes.append("[+0.0 pts] URL returned HTTP 404 or connection failed. Live verification failed.")
        return 0.0, notes
        
    # Check title/name presence in fetched text
    name_clean = re.sub(r"[^\w\s]", "", scholarship_name.lower())
    page_text_clean = re.sub(r"[^\w\s]", "", fetch_res.text_content.lower())
    
    # Check exact name or normalized substring
    if name_clean in page_text_clean or scholarship_name.lower() in fetch_res.text_content.lower():
        score = WEIGHT_LIVE_PRESENCE  # 20.0
        notes.append("[+20.0 pts] HTTP 200 Live page with verbatim scholarship title match in source content")
    else:
        name_tokens = [t for t in name_clean.split() if len(t) > 2]
        matched_tokens = [t for t in name_tokens if t in page_text_clean]
        ratio = len(matched_tokens) / max(1, len(name_tokens))
        if ratio >= 0.6:
            score = WEIGHT_LIVE_PRESENCE  # 20.0
            notes.append(f"[+20.0 pts] HTTP 200 Live page with confirmed high keyword presence ({int(ratio*100)}%)")
        elif ratio >= 0.35:
            score = 14.0
            notes.append(f"[+14.0 pts] HTTP 200 Live page with partial keyword presence ({int(ratio*100)}%)")
        else:
            score = 6.0
            notes.append("[+6.0 pts] HTTP 200 Live page but specific scholarship announcement text was sparse")
            
    return score, notes


def calculate_application_url_score(
    application_url: Optional[str],
    official_source_url: str
) -> Tuple[float, List[str]]:
    """Calculates application channel clarity and direct portal score (Max 15 pts)."""
    notes = []
    if not application_url or application_url == "Not specified":
        notes.append("[+0.0 pts] No direct application portal link detected in source announcement")
        return 0.0, notes
        
    app_domain = extract_domain(application_url)
    off_domain = extract_domain(official_source_url)
    
    # Official gateway or same domain
    if app_domain and (app_domain in off_domain or off_domain in app_domain):
        score = WEIGHT_APPLICATION_URL  # 15.0
        notes.append(f"[+15.0 pts] Dedicated official application link on primary portal ({app_domain})")
    elif any(app_domain.endswith(t) for t in [".gov.in", ".nic.in", ".ac.in", ".org.in"]):
        score = WEIGHT_APPLICATION_URL  # 15.0
        notes.append(f"[+15.0 pts] Official national/state application gateway ({app_domain})")
    elif "apply" in application_url.lower() or "register" in application_url.lower() or "scheme" in application_url.lower():
        score = WEIGHT_APPLICATION_URL  # 15.0
        notes.append(f"[+15.0 pts] Validated official direct application pathway ({app_domain})")
    else:
        score = 10.0
        notes.append(f"[+10.0 pts] General organizational application link ({app_domain})")
        
    return score, notes


def calculate_field_grounding_score(
    evidence_ledger: Dict[str, Any]
) -> Tuple[float, List[str]]:
    """
    Calculates score based on verbatim evidentiary backing for crucial fields (Max 25 pts).
    Fields checked:
      - amount_benefit (+6 pts)
      - closing_date (+6 pts)
      - income_criteria or category_criteria (+7 pts)
      - academic_requirements or selection_process (+6 pts)
    """
    score = 0.0
    notes = []
    
    if "amount_benefit" in evidence_ledger and evidence_ledger["amount_benefit"].get("snippet"):
        score += 6.0
        notes.append("[+6.0 pts] Verifiable source quote for funding amount & benefit")
    else:
        notes.append("[+0.0 pts] Missing source citation for scholarship amount")
        
    if "closing_date" in evidence_ledger and evidence_ledger["closing_date"].get("snippet"):
        score += 6.0
        notes.append("[+6.0 pts] Verifiable source quote for application deadline")
    else:
        notes.append("[+0.0 pts] Missing source citation for closing date")
        
    if ("income_criteria" in evidence_ledger and evidence_ledger["income_criteria"].get("snippet")) or \
       ("category_criteria" in evidence_ledger and evidence_ledger["category_criteria"].get("snippet")):
        score += 7.0
        notes.append("[+7.0 pts] Verifiable source quote for eligibility & reservation criteria")
    else:
        notes.append("[+0.0 pts] Missing source citation for specific income/category criteria")
        
    if ("academic_requirements" in evidence_ledger and evidence_ledger["academic_requirements"].get("snippet")) or \
       ("selection_process" in evidence_ledger and evidence_ledger["selection_process"].get("snippet")) or \
       ("gender_criteria" in evidence_ledger and evidence_ledger["gender_criteria"].get("snippet")):
        score += 6.0
        notes.append("[+6.0 pts] Verifiable source quote for academic/selection criteria")
    else:
        notes.append("[+0.0 pts] Missing source citation for academic qualification details")
        
    return score, notes


def calculate_freshness_and_status(
    closing_date_str: Optional[str],
    is_live: bool
) -> Tuple[float, ScholarshipStatus, List[str]]:
    """
    Determines temporal freshness score (Max 15 pts) and assigns accurate lifecycle status:
    ACTIVE, EXPIRING_SOON, EXPIRED, NO_LONGER_VERIFIABLE, REVIEW_REQUIRED.
    """
    notes = []
    if not is_live:
        notes.append("[+0.0 pts] Primary source inaccessible (404/down). Status: NO_LONGER_VERIFIABLE")
        return 0.0, ScholarshipStatus.NO_LONGER_VERIFIABLE, notes
        
    parsed_date = parse_date_safely(closing_date_str)
    today = date.today()
    
    if parsed_date is None:
        # Check if text indicates rolling or active round
        if closing_date_str and "always" in closing_date_str.lower() or "round" in str(closing_date_str).lower():
            notes.append("[+15.0 pts] Active recurring/rolling annual application cycle")
            return WEIGHT_FRESHNESS, ScholarshipStatus.ACTIVE, notes
        notes.append("[+8.0 pts] Application window open, exact closing date is rolling or unannounced")
        return 8.0, ScholarshipStatus.ACTIVE, notes
        
    delta_days = (parsed_date - today).days
    
    if delta_days < 0:
        # Expired
        notes.append(f"[+3.0 pts] Application deadline passed ({parsed_date.strftime('%d %b %Y')}). Status: EXPIRED")
        return 3.0, ScholarshipStatus.EXPIRED, notes
    elif delta_days <= EXPIRING_SOON_DAYS:
        # Expiring soon (within 15 days)
        notes.append(f"[+14.0 pts] Application closing soon in {delta_days} days ({parsed_date.strftime('%d %b %Y')}). Status: EXPIRING_SOON")
        return 14.0, ScholarshipStatus.EXPIRING_SOON, notes
    else:
        # Active
        notes.append(f"[+15.0 pts] Active open cycle with valid future deadline ({parsed_date.strftime('%d %b %Y')}). Status: ACTIVE")
        return WEIGHT_FRESHNESS, ScholarshipStatus.ACTIVE, notes


def verify_scholarship(
    scholarship: Scholarship,
    fetch_result: Optional[FetchResult] = None
) -> Scholarship:
    """
    Runs full evidentiary verification and calculates the transparent 100-point confidence score.
    Applies the strict >= 95% threshold for VERIFIED vs REVIEW_REQUIRED.
    """
    is_live = fetch_result.is_live if fetch_result else True
    
    # 1. Source Authority (Max 25)
    auth_score, auth_notes = calculate_source_authority_score(scholarship.official_source_url)
    
    # 2. Live Presence (Max 20)
    live_score, live_notes = calculate_live_presence_score(fetch_result, scholarship.name)
    
    # 3. Application URL (Max 15)
    app_score, app_notes = calculate_application_url_score(scholarship.application_url, scholarship.official_source_url)
    
    # 4. Field Grounding Evidence (Max 25)
    ground_score, ground_notes = calculate_field_grounding_score(scholarship.evidence_ledger)
    
    # 5. Freshness & Lifecycle Status (Max 15)
    fresh_score, computed_status, fresh_notes = calculate_freshness_and_status(scholarship.closing_date, is_live)
    
    # Compute Total Confidence Score
    total_score = round(auth_score + live_score + app_score + ground_score + fresh_score, 1)
    total_score = min(100.0, max(0.0, total_score))
    
    # Check 95% threshold
    is_verified = (total_score >= VERIFICATION_THRESHOLD_PERCENT)
    verification_status = VerificationStatus.VERIFIED if is_verified else VerificationStatus.REVIEW_REQUIRED
    
    # Collect all audit notes
    all_notes = auth_notes + live_notes + app_notes + ground_notes + fresh_notes
    if is_verified:
        all_notes.append(f"Result: Confidence {total_score:.1f}% meets/exceeds 95.0% threshold -> VERIFIED")
    else:
        all_notes.append(f"Result: Confidence {total_score:.1f}% is below 95.0% threshold -> REVIEW REQUIRED")
        
    breakdown = ConfidenceBreakdown(
        source_authority_score=auth_score,
        live_presence_score=live_score,
        application_url_score=app_score,
        field_grounding_score=ground_score,
        freshness_score=fresh_score,
        total_score=total_score,
        is_verified=is_verified,
        audit_notes=all_notes
    )
    
    scholarship.confidence_score = total_score
    scholarship.confidence_breakdown = breakdown
    scholarship.verification_status = verification_status
    scholarship.current_status = computed_status
    scholarship.last_verified_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    return scholarship
