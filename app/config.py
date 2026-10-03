"""
Configuration module for Scholarship Intelligence Crawler.
Defines scoring weights, verification thresholds, database paths, and crawler parameters.
"""
from pathlib import Path
from typing import List, Set

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
STATIC_DIR = APP_DIR / "static"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_PATH = DATA_DIR / "scholarships.db"

# Verification & Confidence Scoring Thresholds
VERIFICATION_THRESHOLD_PERCENT = 95.0  # >= 95% is VERIFIED, < 95% is REVIEW_REQUIRED
EXPIRING_SOON_DAYS = 15

# Confidence Scoring Rubric Weights (Total: 100.0)
WEIGHT_SOURCE_AUTHORITY = 25.0       # Official domain (.gov.in, .nic.in, .ac.in, verified foundation)
WEIGHT_LIVE_PRESENCE = 20.0          # HTTP 200 + Content Presence / Title match
WEIGHT_APPLICATION_URL = 15.0        # Live official direct application portal link
WEIGHT_FIELD_GROUNDING = 25.0        # Verbatim text evidence support for key fields (amount, criteria, dates)
WEIGHT_FRESHNESS = 15.0              # Current cycle status & temporal freshness

# Domain Authority Tiers
OFFICIAL_GOV_DOMAINS: Set[str] = {
    ".gov.in", ".nic.in", ".ac.in", ".edu.in", ".res.in"
}

KNOWN_OFFICIAL_DOMAINS: Set[str] = {
    "scholarships.gov.in",
    "education.gov.in",
    "desw.gov.in",
    "minorityaffairs.gov.in",
    "aicte-india.org",
    "online-inspire.gov.in",
    "dst.gov.in",
    "dbtindia.gov.in",
    "ugc.ac.in",
    "ugc.gov.in",
    "nosmsje.gov.in",
    "mahadbt.maharashtra.gov.in",
    "ssp.postmatric.karnataka.gov.in",
    "scholarship.up.gov.in",
    "svmcm.wbhed.gov.in",
    "scholarships.reliancefoundation.org",
    "reliancefoundation.org",
    "tatatrusts.org",
    "hdfcbank.com",
    "kotakeducation.org",
    "infosys.com",
    "ongcscholar.org",
    "ongcindia.com",
    "kcmet.org",
    "sitaramjindalfoundation.org",
    "inlaksfoundation.org",
    "glowandlovelycareers.in",
    "loreal.com"
}

KNOWN_AGGREGATORS: Set[str] = {
    "buddy4study.com",
    "edurev.in",
    "collegedunia.com",
    "shiksha.com",
    "scholarshipportal.com",
    "careerindia.com",
    "jagranjosh.com"
}

# Network & Crawler Settings
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (ScholarshipIntelligenceCrawler/2.0; +https://edxso.org)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}

REQUEST_TIMEOUT_SECONDS = 15.0
MAX_RETRIES = 3
RATE_LIMIT_DELAY_SECONDS = 0.5
