"""
Data models and Atlas Schema definitions for Scholarship Intelligence Crawler.
Provides strict Pydantic validation, evidence tracking, and history models.
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, timezone


class SourceType(str, Enum):
    GOVT_CENTRAL = "Government - Central"
    GOVT_STATE = "Government - State"
    CORPORATE_CSR = "Corporate CSR"
    FOUNDATION_TRUST = "Foundation / Trust"
    UNIVERSITY = "University / Institution"
    INTERNATIONAL = "International"


class ScholarshipStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NO_LONGER_VERIFIABLE = "NO_LONGER_VERIFIABLE"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class GenderCriteria(str, Enum):
    ALL = "All"
    FEMALE = "Female Only"
    MALE = "Male Only"
    TRANSGENDER = "Transgender Inclusive"


class EducationLevel(str, Enum):
    ALL = "All Levels"
    SCHOOL = "Class 1-12 / School"
    DIPLOMA = "Diploma / ITI"
    UNDERGRADUATE = "Undergraduate (UG / B.Tech / MBBS / B.Sc)"
    POSTGRADUATE = "Postgraduate (PG / M.Tech / MD / M.Sc)"
    DOCTORAL = "Doctoral (Ph.D / Postdoc)"
    PROFESSIONAL = "Professional / Vocational"


class EvidenceItem(BaseModel):
    """Verifiable source quote supporting an extracted field."""
    field_name: str
    extracted_value: str
    snippet: str
    source_url: str
    match_type: str = "EXACT_VERBATIM"  # EXACT_VERBATIM, REGEX_MATCH, DOM_EXTRACT


class ConfidenceBreakdown(BaseModel):
    """Granular point-by-point breakdown for confidence score calculation."""
    source_authority_score: float = Field(..., description="Points for official domain authority (Max 25)")
    live_presence_score: float = Field(..., description="Points for HTTP 200 & title match (Max 20)")
    application_url_score: float = Field(..., description="Points for official application portal URL (Max 15)")
    field_grounding_score: float = Field(..., description="Points for verbatim evidence support across fields (Max 25)")
    freshness_score: float = Field(..., description="Points for current active cycle & deadlines (Max 15)")
    total_score: float = Field(..., description="Calculated total confidence percentage (0.0 to 100.0)")
    is_verified: bool = Field(..., description="True if total_score >= 95.0")
    audit_notes: List[str] = Field(default_factory=list, description="Detailed reasoning log for the score")


class HistoryRecord(BaseModel):
    """Audit log entry representing a detected change across crawler runs."""
    history_id: Optional[int] = None
    scholarship_id: str
    scholarship_name: str
    field_name: str
    old_value: Optional[str]
    new_value: str
    change_type: str  # CREATED, DEADLINE_EXTENDED, AMOUNT_REVISED, ELIGIBILITY_UPDATED, STATUS_CHANGE
    detected_at: str
    source_url: str
    evidence_snippet: Optional[str] = None


class Scholarship(BaseModel):
    """Atlas Universal Schema for verified funding opportunities."""
    id: str = Field(..., description="Unique slug or alphanumeric identifier")
    name: str = Field(..., description="Official name of the scholarship")
    provider: str = Field(..., description="Issuing organization, ministry, or corporate body")
    source_type: SourceType = Field(..., description="Classified category of funding body")
    
    # Authoritative URLs
    official_source_url: str = Field(..., description="Authoritative primary source URL")
    application_url: Optional[str] = Field("Not specified", description="Direct official portal to apply")
    discovery_url: Optional[str] = Field(None, description="Initial discovery portal if different from official")
    
    # Financial benefits
    amount_benefit: str = Field(..., description="Monetary support or tuition waiver description")
    amount_numerical: Optional[float] = Field(None, description="Normalized annual maximum value in INR if quantifiable")
    
    # Eligibility and criteria
    eligibility_summary: str = Field(..., description="Human-readable comprehensive eligibility summary")
    academic_requirements: str = Field("Not specified", description="Minimum marks, CGPA, or qualifying exam ranks")
    education_level: str = Field("All Levels", description="Applicable levels of study")
    income_criteria: str = Field("Not specified", description="Family income limit per annum (or Not specified)")
    age_criteria: str = Field("Not specified", description="Age limits if enforced")
    gender_criteria: str = Field("All", description="Target gender eligibility")
    category_criteria: str = Field("All Categories", description="Caste / Social Category (SC, ST, OBC, General, Minority, EWS)")
    domicile_state: str = Field("All India", description="State residency requirement or All India")
    institution_requirements: str = Field("Recognized Indian Institutions", description="Institution accreditation/type")
    
    # Application lifecycle
    opening_date: Optional[str] = Field("Not specified", description="Start date of application window")
    closing_date: Optional[str] = Field("Not specified", description="Application deadline date")
    documents_required: List[str] = Field(default_factory=list, description="List of mandatory documents")
    selection_process: str = Field("Not specified", description="Merit-based, Means-based, Entrance Test, Interview")
    renewal_requirements: str = Field("Not specified", description="Conditions for subsequent year renewal")
    
    # System Status & Verification
    current_status: ScholarshipStatus = Field(ScholarshipStatus.ACTIVE, description="Active, Expiring Soon, Expired, Review Required")
    verification_status: VerificationStatus = Field(VerificationStatus.REVIEW_REQUIRED, description="VERIFIED if score >= 95%, else REVIEW_REQUIRED")
    confidence_score: float = Field(0.0, description="Evidentiary confidence score (0-100%)")
    confidence_breakdown: Optional[ConfidenceBreakdown] = None
    
    # Evidence Ledger (Anti-hallucination source traceable mappings)
    evidence_ledger: Dict[str, Any] = Field(default_factory=dict, description="Field-to-snippet traceability map")
    
    # Metadata
    last_verified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))


class CrawlRunSummary(BaseModel):
    """Metadata summary of an automated crawler cycle."""
    run_id: str
    started_at: str
    completed_at: str
    run_type: str = "FULL_DISCOVERY_AND_VERIFY"
    total_discovered: int
    total_verified: int
    total_review_required: int
    changes_detected: int
    expired_detected: int
    avg_confidence: float
    status: str = "COMPLETED"
