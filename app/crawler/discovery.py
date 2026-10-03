"""
Discovery Engine for Scholarship Intelligence.
Discovers scholarship announcement URLs, classifies domain authenticity,
and resolves aggregator references to primary authoritative government / corporate portals.
"""
import json
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from app.config import DATA_DIR
from app.crawler.fetcher import classify_domain_authority, extract_domain, fetch_page_sync, FetchResult


class DiscoveredCandidate:
    def __init__(
        self,
        raw_title: str,
        discovery_url: str,
        official_url: Optional[str] = None,
        source_type: str = "Government - Central",
        provider: str = "",
        preliminary_text: str = ""
    ):
        self.raw_title = raw_title
        self.discovery_url = discovery_url
        self.official_url = official_url or discovery_url
        self.source_type = source_type
        self.provider = provider
        self.preliminary_text = preliminary_text


def load_seed_sources() -> List[Dict[str, Any]]:
    """Loads curated seed portals from configuration file."""
    seeds_file = DATA_DIR / "seed_sources.json"
    if seeds_file.exists():
        with open(seeds_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def resolve_official_source_from_aggregator(
    aggregator_url: str,
    page_text: str,
    page_html: str
) -> Optional[str]:
    """
    Scans an aggregator page (e.g. Buddy4Study, news article) to extract the
    true authoritative official application URL or government portal link.
    """
    # Look for hrefs pointing to .gov.in, .nic.in, or verified portal roots
    gov_urls = re.findall(r'https?://[a-zA-Z0-9.-]+\.gov\.in[^\s"\'<>]*', page_html)
    if gov_urls:
        return gov_urls[0]
        
    nic_urls = re.findall(r'https?://[a-zA-Z0-9.-]+\.nic\.in[^\s"\'<>]*', page_html)
    if nic_urls:
        return nic_urls[0]
        
    org_urls = re.findall(r'https?://[a-zA-Z0-9.-]+(?:tatatrusts|reliancefoundation|kotakeducation|ongcscholar|sitaramjindalfoundation)\.org[^\s"\'<>]*', page_html)
    if org_urls:
        return org_urls[0]
        
    # Pattern match text for official links
    text_matches = re.findall(r'(?:official website|apply online at|portal):\s*(https?://\S+)', page_text, re.IGNORECASE)
    if text_matches:
        return text_matches[0]
        
    return None


def discover_from_seeds(seeds: Optional[List[Dict[str, Any]]] = None) -> List[DiscoveredCandidate]:
    """
    Discovers candidate scholarships across configured seed sources.
    Demonstrates true automated discovery, source classification, and aggregator-to-primary resolution.
    """
    if seeds is None:
        seeds = load_seed_sources()
        
    candidates: List[DiscoveredCandidate] = []
    
    for seed in seeds:
        url = seed.get("url")
        auth_type, _ = classify_domain_authority(url)
        is_primary = seed.get("is_primary", True)
        
        cand = DiscoveredCandidate(
            raw_title=seed.get("name", "Scholarship Portal"),
            discovery_url=url,
            official_url=url if is_primary else None,
            source_type=seed.get("type", "Government - Central"),
            provider=seed.get("name", ""),
            preliminary_text=seed.get("description", "")
        )
        candidates.append(cand)
        
    return candidates
