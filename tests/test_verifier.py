"""
Tests for mathematical verification engine and confidence scoring rubric.
"""
import pytest
from app.models import Scholarship, SourceType, ScholarshipStatus, VerificationStatus
from app.crawler.verifier import verify_scholarship, calculate_source_authority_score
from app.crawler.fetcher import FetchResult


def test_confidence_scoring_formula():
    # 1. Fully verified official government scholarship
    verified_data = {
        "id": "test-official-scheme-1",
        "name": "Central Sector National Merit Scheme",
        "provider": "Ministry of Education, Govt of India",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://scholarships.gov.in",
        "application_url": "https://scholarships.gov.in/apply",
        "amount_benefit": "₹20,000 per annum",
        "amount_numerical": 20000.0,
        "eligibility_summary": "Top 80th percentile students with family income <= ₹4.5 Lakh",
        "income_criteria": "₹4.5 Lakh",
        "closing_date": "31 December 2026",
        "evidence_ledger": {
            "amount_benefit": {"snippet": "Rate of scholarship is Rs 20,000 per annum"},
            "closing_date": {"snippet": "Last date to apply is 31st December 2026"},
            "income_criteria": {"snippet": "Parental income not exceeding Rs 4.5 Lakhs"},
            "academic_requirements": {"snippet": "Top 80th percentile in board exam"}
        }
    }
    
    item = Scholarship(**verified_data)
    mock_fetch = FetchResult(
        url=item.official_source_url,
        status_code=200,
        is_live=True,
        text_content=f"{item.name} {item.provider} Rate of scholarship is Rs 20,000 per annum Last date to apply is 31st December 2026",
        title=item.name
    )
    
    verified = verify_scholarship(item, fetch_result=mock_fetch)
    
    # Check score and status
    assert verified.confidence_score >= 95.0
    assert verified.verification_status == VerificationStatus.VERIFIED
    assert verified.current_status == ScholarshipStatus.ACTIVE
    assert verified.confidence_breakdown is not None
    assert len(verified.confidence_breakdown.audit_notes) > 0


def test_unverified_aggregator_falls_below_threshold():
    # 2. Aggregator listing with missing official domain and weak evidence
    unverified_data = {
        "id": "test-aggregator-listing",
        "name": "Unverified Generic Award",
        "provider": "Unknown Blog",
        "source_type": SourceType.INTERNATIONAL,
        "official_source_url": "https://www.buddy4study.com/scholarship/unverified",
        "application_url": "Not specified",
        "amount_benefit": "₹10,000",
        "eligibility_summary": "General criteria",
        "closing_date": "31 December 2026",
        "evidence_ledger": {}
    }
    
    item = Scholarship(**unverified_data)
    mock_fetch = FetchResult(
        url=item.official_source_url,
        status_code=200,
        is_live=True,
        text_content="Some listing text",
        title="Listing Page"
    )
    
    verified = verify_scholarship(item, fetch_result=mock_fetch)
    
    # Must be below 95% -> REVIEW_REQUIRED
    assert verified.confidence_score < 95.0
    assert verified.verification_status == VerificationStatus.REVIEW_REQUIRED


def test_expired_scholarship_status():
    # 3. Past deadline scholarship
    expired_data = {
        "id": "test-expired-scheme",
        "name": "Past Year Scholarship 2024",
        "provider": "Ministry of Education",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://scholarships.gov.in",
        "application_url": "https://scholarships.gov.in",
        "amount_benefit": "₹10,000",
        "eligibility_summary": "Passed exam",
        "closing_date": "31 December 2024",  # In the past
        "evidence_ledger": {
            "amount_benefit": {"snippet": "Rs 10,000 grant"},
            "closing_date": {"snippet": "Closed on 31 December 2024"}
        }
    }
    
    item = Scholarship(**expired_data)
    mock_fetch = FetchResult(
        url=item.official_source_url,
        status_code=200,
        is_live=True,
        text_content=f"{item.name} Closed on 31 December 2024",
        title=item.name
    )
    
    verified = verify_scholarship(item, fetch_result=mock_fetch)
    assert verified.current_status == ScholarshipStatus.EXPIRED
