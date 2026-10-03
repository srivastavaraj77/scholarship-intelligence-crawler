"""
Tests for crawler discovery, fetcher, and extraction modules.
"""
import pytest
from app.crawler.fetcher import classify_domain_authority, extract_domain, clean_html_to_text
from app.crawler.discovery import discover_from_seeds, resolve_official_source_from_aggregator
from app.crawler.extractor import (
    extract_amounts,
    extract_deadlines,
    extract_income_limit,
    extract_gender_criteria,
    extract_domicile,
    build_evidence_ledger
)


def test_domain_authority_classification():
    # Government TLDs
    auth_type, score = classify_domain_authority("https://scholarships.gov.in/scheme")
    assert auth_type == "GOV_ACADEMIC_OFFICIAL"
    assert score == 1.0

    auth_type, score = classify_domain_authority("https://mahadbt.maharashtra.gov.in/portal")
    assert auth_type == "GOV_ACADEMIC_OFFICIAL"
    assert score == 1.0

    # Corporate CSR & Foundations
    auth_type, score = classify_domain_authority("https://scholarships.reliancefoundation.org")
    assert auth_type == "VERIFIED_FOUNDATION_CORPORATE"
    assert score == 0.95

    auth_type, score = classify_domain_authority("https://tatatrusts.org/grants")
    assert auth_type == "VERIFIED_FOUNDATION_CORPORATE"
    assert score == 0.95

    # Aggregator
    auth_type, score = classify_domain_authority("https://www.buddy4study.com/scholarship/abc")
    assert auth_type == "AGGREGATOR_DISCOVERY"
    assert score == 0.50


def test_aggregator_to_primary_resolution():
    mock_aggregator_html = """
    <html>
        <body>
            <h1>Central Sector Scheme 2026</h1>
            <p>For more details and official online application, visit the official government portal:</p>
            <a href="https://scholarships.gov.in/fresh/instruction">Apply on National Scholarship Portal</a>
        </body>
    </html>
    """
    resolved_url = resolve_official_source_from_aggregator(
        "https://buddy4study.com/scholarships/central-sector",
        "Central Sector Scheme 2026",
        mock_aggregator_html
    )
    assert resolved_url == "https://scholarships.gov.in/fresh/instruction"


def test_anti_hallucination_extraction():
    text_with_data = "Selected students receive ₹50,000 per annum. Annual family income must not exceed ₹4.50 Lakh per annum. Closing date is 31st October 2026. Only female students are eligible."
    
    amount, num_val, amt_snippet = extract_amounts(text_with_data)
    assert "₹50,000" in amount
    assert num_val == 50000.0
    assert amt_snippet is not None

    income, inc_snippet = extract_income_limit(text_with_data)
    assert "4.50 Lakh" in income
    assert inc_snippet is not None

    gender, gen_snippet = extract_gender_criteria(text_with_data)
    assert gender == "Female Only"
    assert gen_snippet is not None

    deadline, d_snippet = extract_deadlines(text_with_data)
    assert "31st October 2026" in deadline or "31" in deadline

    # Absence Test (Must NOT hallucinate)
    text_without_income = "This scholarship offers ₹20,000 per annum with no income limits specified."
    absent_income, absent_snippet = extract_income_limit(text_without_income)
    assert absent_income == "Not specified"
    assert absent_snippet is None
