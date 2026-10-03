"""
Tests for Change Detection engine and audit history logging.
"""
import pytest
from app.models import Scholarship, SourceType, ScholarshipStatus, VerificationStatus
from app.crawler.change_detector import detect_field_differences


def test_field_difference_detection():
    old_item = Scholarship(
        id="test-change-scheme",
        name="Tech Innovation Grant",
        provider="Innovation CSR Trust",
        source_type=SourceType.CORPORATE_CSR,
        official_source_url="https://innovate.org",
        application_url="https://innovate.org/apply",
        amount_benefit="₹50,000",
        amount_numerical=50000.0,
        eligibility_summary="Students in tech",
        income_criteria="₹3.0 Lakh",
        closing_date="31 October 2026",
        confidence_score=98.0,
        evidence_ledger={"closing_date": {"snippet": "Deadline 31 October 2026"}}
    )

    new_item = Scholarship(
        id="test-change-scheme",
        name="Tech Innovation Grant",
        provider="Innovation CSR Trust",
        source_type=SourceType.CORPORATE_CSR,
        official_source_url="https://innovate.org",
        application_url="https://innovate.org/apply",
        amount_benefit="₹75,000",  # Changed from 50k to 75k
        amount_numerical=75000.0,
        eligibility_summary="Students in tech",
        income_criteria="₹4.0 Lakh",  # Changed from 3L to 4L
        closing_date="15 November 2026",  # Extended from 31 Oct to 15 Nov
        confidence_score=98.0,
        evidence_ledger={
            "closing_date": {"snippet": "Extended deadline: 15 November 2026"},
            "amount_benefit": {"snippet": "Grant increased to Rs 75,000"},
            "income_criteria": {"snippet": "Income limit raised to Rs 4 Lakhs"}
        }
    )

    diffs = detect_field_differences(old_item, new_item)
    assert len(diffs) >= 3

    field_names = [d.field_name for d in diffs]
    assert "Application Deadline" in field_names
    assert "Scholarship Benefit Amount" in field_names
    assert "Family Income Limit" in field_names

    # Check that old values and new values match
    deadline_diff = next(d for d in diffs if d.field_name == "Application Deadline")
    assert deadline_diff.old_value == "31 October 2026"
    assert deadline_diff.new_value == "15 November 2026"
    assert deadline_diff.change_type == "DEADLINE_EXTENDED"
