"""
Fetcher module for robust, resilient HTTP operations.
Includes domain authority classification, HTML text cleaning, status verification, and retry handling.
"""
import httpx
import re
import urllib.parse
from typing import Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup

from app.config import (
    DEFAULT_HEADERS,
    REQUEST_TIMEOUT_SECONDS,
    OFFICIAL_GOV_DOMAINS,
    KNOWN_OFFICIAL_DOMAINS,
    KNOWN_AGGREGATORS
)


class FetchResult:
    def __init__(
        self,
        url: str,
        status_code: int,
        is_live: bool,
        text_content: str = "",
        raw_html: str = "",
        title: str = "",
        error_message: Optional[str] = None
    ):
        self.url = url
        self.status_code = status_code
        self.is_live = is_live
        self.text_content = text_content
        self.raw_html = raw_html
        self.title = title
        self.error_message = error_message


def extract_domain(url: str) -> str:
    """Extracts the clean root domain name from a URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        if ":" in netloc:
            netloc = netloc.split(":")[0]
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""


def classify_domain_authority(url: str) -> Tuple[str, float]:
    """
    Classifies the domain authority score (0.0 to 1.0) and type.
    Types:
      - GOV_ACADEMIC_OFFICIAL (1.0) -> .gov.in, .nic.in, .ac.in, .edu.in
      - VERIFIED_FOUNDATION_CORPORATE (0.95) -> Known trust/corporate portal
      - AGGREGATOR_DISCOVERY (0.50) -> Aggregator/news portals (Buddy4Study, etc.)
      - UNVERIFIED_THIRD_PARTY (0.20) -> General internet domain
    """
    domain = extract_domain(url)
    
    # 1. Government and Academic TLDs
    for gov_tld in OFFICIAL_GOV_DOMAINS:
        if domain.endswith(gov_tld) or f"{gov_tld}." in domain:
            return "GOV_ACADEMIC_OFFICIAL", 1.0
            
    # 2. Known Official Foundations and Corporate Portals
    for off_domain in KNOWN_OFFICIAL_DOMAINS:
        if domain == off_domain or domain.endswith(f".{off_domain}"):
            return "VERIFIED_FOUNDATION_CORPORATE", 0.95
            
    # 3. Known Aggregators
    for agg_domain in KNOWN_AGGREGATORS:
        if domain == agg_domain or domain.endswith(f".{agg_domain}"):
            return "AGGREGATOR_DISCOVERY", 0.50
            
    # 4. Fallback: Check if it's an educational or organization domain
    if domain.endswith(".org") or domain.endswith(".org.in") or domain.endswith(".edu"):
        return "GENERAL_ORGANIZATION", 0.70
        
    return "UNVERIFIED_THIRD_PARTY", 0.20


def clean_html_to_text(html_content: str) -> Tuple[str, str]:
    """
    Strips scripts, styles, navigation bars, and extracts structured readable text and page title.
    """
    if not html_content:
        return "", ""
        
    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception:
        soup = BeautifulSoup(html_content, "html.parser")
        
    # Extract Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        
    # Remove unwanted tags
    for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        element.extract()
        
    text = soup.get_text(separator=" ", strip=True)
    # Normalize whitespaces
    clean_text = re.sub(r"\s+", " ", text).strip()
    return clean_text, title


async def fetch_page_async(url: str, client: Optional[httpx.AsyncClient] = None) -> FetchResult:
    """
    Asynchronously fetches a URL and returns structured clean text and live status.
    """
    close_client = False
    if client is None:
        client = httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True)
        close_client = True
        
    try:
        response = await client.get(url)
        is_live = response.status_code == 200
        clean_text, title = clean_html_to_text(response.text) if is_live else ("", "")
        return FetchResult(
            url=url,
            status_code=response.status_code,
            is_live=is_live,
            text_content=clean_text,
            raw_html=response.text if is_live else "",
            title=title
        )
    except httpx.RequestError as e:
        return FetchResult(
            url=url,
            status_code=0,
            is_live=False,
            error_message=f"Request failed: {str(e)}"
        )
    finally:
        if close_client:
            await client.aclose()


def fetch_page_sync(url: str) -> FetchResult:
    """
    Synchronous fetching wrapper with fallback.
    """
    try:
        with httpx.Client(headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True) as client:
            resp = client.get(url)
            is_live = resp.status_code == 200
            clean_text, title = clean_html_to_text(resp.text) if is_live else ("", "")
            return FetchResult(
                url=url,
                status_code=resp.status_code,
                is_live=is_live,
                text_content=clean_text,
                raw_html=resp.text if is_live else "",
                title=title
            )
    except Exception as e:
        return FetchResult(
            url=url,
            status_code=0,
            is_live=False,
            error_message=f"Network error: {str(e)}"
        )
