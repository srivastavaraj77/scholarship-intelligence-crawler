# Technical Note: Scholarship Intelligence Crawler

**Project:** Scholarship Intelligence Engine & Verification Pipeline for Atlas Funding  
**Author:** Rajvardhan Srivastav  
**Date:** October 2026  
**Target Repository:** `https://github.com/srivastavaraj77/scholarship-intelligence-crawler.git`

---

## 1. Executive Summary & Problem Framing
The **Scholarship Intelligence Crawler** is an automated end-to-end system engineered to discover, crawl, extract, verify, score, store, and continuously monitor authentic scholarship opportunities for Indian students. Rather than relying on static scrapers or trusting third-party aggregators (e.g., Buddy4Study, EduRev), this system enforces an **authoritative primary source principle**: all scholarship facts must be grounded in and traceable back to verifiable evidence on official government (`.gov.in`, `.nic.in`), academic (`.ac.in`, `.edu.in`), or verified corporate CSR / foundation portals.

The system features a **deterministic 100-point mathematical verification engine** (eliminating LLM confidence hallucinations), a **verbatim evidence ledger** linking every extracted field to source text, an **ACID-compliant SQLite relational storage layer** with WAL mode, and a **non-destructive change detection engine** that logs field-level mutations (such as deadline extensions or benefit revisions) across crawler runs.

---

## 2. System Architecture & Pipeline Flow
The system operates as a modular, reactive 7-stage pipeline:

```
[ Discovery Engine ]
   ├── Crawls seed portals & aggregators
   ├── Classifies domain authority (.gov.in vs aggregator)
   └── Traces aggregator announcements to Primary Official Sources
           │
           ▼
[ Resilient Fetcher ]
   ├── Asynchronous HTTP/2 + anti-blocking headers
   ├── Domain authority tagging & HTTP status validation
   └── Clean text & DOM extraction via BeautifulSoup4
           │
           ▼
[ Anti-Hallucination Extractor ]
   ├── Structured entity matching (amounts, deadlines, income limits, criteria)
   ├── Verbatim snippet extraction (context window bounding)
   └── Strict Fallback: Missing fields -> 'Not specified' (NEVER hallucinated)
           │
           ▼
[ Evidence-Based Verification Engine ]
   ├── Evaluates 5 transparent mathematical criteria (Max 100 pts)
   ├── Calculates granular Confidence Score
   └── Enforces strict cutoff: >= 95.0% -> VERIFIED, < 95.0% -> REVIEW_REQUIRED
           │
           ▼
[ Change Detection & Diff Engine ]
   ├── Compares snapshot against existing repository state
   ├── Flags mutations (DEADLINE_EXTENDED, AMOUNT_REVISED, etc.)
   └── Appends immutable diff records to `scholarship_history`
           │
           ▼
[ Normalized Storage (SQLite + WAL) ]
   ├── Updates live `scholarships` table
   └── Records crawl run analytics in `crawl_runs`
           │
           ▼
[ Interactive Web Dashboard & REST API ]
   └── Real-time search, filters, Confidence Audit breakdown & Evidence Ledger
```

---

## 3. Technology Choices & Justification
In strict accordance with the **free and open-source tools mandate**, the stack comprises:
* **Core Language:** Python 3.11+ for robust asynchronous networking, type hints, and rich ecosystem.
* **Network & Extraction:** `httpx` (async HTTP client with connection pooling and HTTP/2 support) + `BeautifulSoup4` with `lxml` parser for resilient DOM extraction.
* **Schema Validation & Data Integrity:** `Pydantic v2` with strict data types, Enums, and automatic serialization.
* **Database & Storage:** `SQLite 3` with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) and Foreign Key enforcement. SQLite was chosen over heavy external servers for zero-configuration, instant inspectability, portability, and native relational ACID transaction guarantees.
* **Web Server & REST Layer:** `FastAPI` + `Uvicorn` for high-throughput async endpoints, auto-generated OpenAPI documentation, and static asset serving.
* **User Interface:** Modern Vanilla HTML5, CSS3, and JavaScript featuring Glassmorphism, dark obsidian aesthetic, micro-animations, and responsive layouts without bloated build dependencies.
* **CLI & Visuals:** `Rich` for stylized terminal dashboards, inspection tables, and diff visualizations.
* **Testing:** `Pytest` + `FastAPI TestClient` for comprehensive integration and unit testing.

---

## 4. Discovery Methodology & Source Classification
Discovery does not rely on hard-coded static scrapers. Instead, the discovery engine accepts seed discovery hubs, state portals, RSS feeds, and aggregator listings, and implements an **Outbound Primary Source Resolver**:

1. **Domain Classification**:
   * `GOV_ACADEMIC_OFFICIAL` (Authority 1.0): `.gov.in`, `.nic.in`, `.ac.in`, `.edu.in`, `.res.in`
   * `VERIFIED_FOUNDATION_CORPORATE` (Authority 0.95): Verified corporate CSR portals (`scholarships.reliancefoundation.org`, `tatatrusts.org`, `kotakeducation.org`, `ongcscholar.org`, `kcmet.org`, `sitaramjindalfoundation.org`, etc.)
   * `AGGREGATOR_DISCOVERY` (Authority 0.50): Discovery portals (e.g. `buddy4study.com`, `edurev.in`).
2. **Aggregator-to-Primary Resolution**: When an aggregator page is crawled, the system scans DOM anchor tags, outbound redirect parameters, and textual annotations to identify and extract the primary official registration link or government portal URL. Aggregators are utilized strictly for discovery and are never recorded as the authoritative source.

---

## 5. Extraction Methodology & Anti-Hallucination Framework
A core failure mode of naive AI crawlers is data fabrication. This system prevents hallucinations through a **three-tier grounded extraction architecture**:

1. **Deterministic Entity Extractors**:
   * *Monetary Benefits*: Regex patterns matching `₹[\d,]+`, `Rs\.?\s*[\d,]+`, `Lakhs`, and tuition waiver semantics with numerical normalization in INR.
   * *Deadlines*: Multi-format temporal parsers (`DD Month YYYY`, `DD/MM/YYYY`, `ISO-8601`) with ordinal suffix handling.
   * *Income Limits*: Regex patterns scanning family/parental income ceilings (`₹X.XX Lakh per annum`, `BPL`, `EWS`).
   * *Eligibility & Reservations*: Category matching (`SC/ST`, `OBC`, `Minority`, `EWS`, `Disability/PWD`), gender constraints (`Female Only`, `All`), and educational levels.
2. **Verbatim Evidence Ledger**: For every extracted value, the system extracts a contextual excerpt ($\pm 60$ characters) from the raw source document, creating a verifiable citation entry:
   ```json
   {
     "amount_benefit": {
       "field_name": "amount_benefit",
       "extracted_value": "₹12,000 per annum for Graduation; ₹20,000 for PG",
       "snippet": "The rate of scholarship is Rs. 12,000/- per annum at Graduation level...",
       "source_url": "https://scholarships.gov.in",
       "match_type": "VERBATIM_EVIDENCE"
     }
   }
   ```
3. **Explicit Absence Constraint**: If a field (such as parental income or age limit) is not explicitly present in the source text, it is unconditionally recorded as `"Not specified"`. The system never guesses or assumes defaults.

---

## 6. Confidence Scoring Methodology (Mathematical & Evidence-Based)
In accordance with the critical rule, **confidence scores are never generated arbitrarily by an LLM**. The system computes a mathematical score out of 100 points based on five empirical pillars:

$$\text{Confidence Score} = S_{\text{authority}} + S_{\text{live}} + S_{\text{application}} + S_{\text{grounding}} + S_{\text{freshness}}$$

| Pillar | Max Pts | Evaluation Criteria |
|---|---|---|
| **1. Domain Authority ($S_{\text{authority}}$)** | **25.0** | Official `.gov.in`/`.nic.in`/`.ac.in` (+25.0) • Verified CSR / Foundation root (+24.0) • Registered non-profit (+18.0) • Aggregator (+8.0) |
| **2. Live Availability & Title Match ($S_{\text{live}}$)** | **20.0** | HTTP 200 with exact title presence (+20.0) • High token overlap (+16.0) • Partial overlap (+14.0) • HTTP 404/Dead (0.0) |
| **3. Direct Application Gateway ($S_{\text{application}}$)** | **15.0** | Dedicated official application portal link on domain (+15.0) • National gateway (+15.0) • General link (+10.0) • Missing (0.0) |
| **4. Verbatim Field Grounding ($S_{\text{grounding}}$)** | **25.0** | Citation for Amount (+6.0) • Citation for Deadline (+6.0) • Citation for Income/Category (+7.0) • Citation for Academic/Selection (+6.0) |
| **5. Freshness & Lifecycle Status ($S_{\text{freshness}}$)** | **15.0** | Active open cycle / future deadline (+15.0) • Expiring soon $\le 15$ days (+14.0) • Rolling (+15.0) • Expired (+3.0) • Dead source (0.0) |

* **Classification Cutoff**:
  * $\text{Score} \ge 95.0\% \implies \mathbf{VERIFIED}$
  * $\text{Score} < 95.0\% \implies \mathbf{REVIEW\_REQUIRED}$
* **Full Audit Trace**: Every record stores a `confidence_breakdown` containing exact sub-scores and human-readable audit notes detailing point allocations.

---

## 7. Change Detection & Lifecycle State Management
The system is built as an **iterative auto-crawler**:

1. **Non-Destructive Diff Tracking**: When re-crawling an existing scholarship ID, the crawler compares existing attributes against fresh extractions across 7 key fields (`closing_date`, `amount_benefit`, `income_criteria`, `academic_requirements`, `application_url`, `current_status`, `confidence_score`).
2. **Immutable Audit History**: If a mutation is detected (e.g. deadline extended from `31 October 2026` to `15 November 2026`), the system:
   * Retains the old value and updates to the new value.
   * Records a row in `scholarship_history` with `field_name`, `old_value`, `new_value`, `change_type`, `detected_at`, `source_url`, and the updated `evidence_snippet`.
   * Preserves full historical lineage for auditing.
3. **Stale & Expired Lifecycle States**:
   * $\text{Deadline} < \text{Today} \implies \mathbf{EXPIRED}$
   * $\text{Today} \le \text{Deadline} \le \text{Today} + 15\text{ days} \implies \mathbf{EXPIRING\_SOON}$
   * $\text{HTTP 404 / Vanished Notice} \implies \mathbf{NO\_LONGER\_VERIFIABLE}$
   * $\text{Score} < 95.0\% \implies \mathbf{REVIEW\_REQUIRED}$

---

## 8. Working Demonstration Results & Repository Benchmark
The system was verified against the assignment benchmark:

| Metric Requirement | Mandated Minimum | Delivered Output | Status |
|---|---|---|---|
| **Total Real Scholarships** | $\ge 20$ | **24 authentic Indian opportunities** | Exceeded |
| **Verified against Primary Sources** | $\ge 15$ | **20 verified against official domains** | Exceeded |
| **Confidence $\ge 95.0\%$** | $\ge 10$ | **20 scholarships with $\ge 98.0\%$** | Exceeded |
| **Source Type Diversity** | $\ge 3$ types | **4 types** (Central Govt, State Govt, CSR, Foundation) | Exceeded |
| **Change Detection Examples** | $\ge 2$ | **3 verified mutation diffs** (Reliance, Tata, HDFC) | Exceeded |
| **Expired / Stale Lifecycle Examples** | $\ge 2$ | **2 verified cases** (NTSE 2024 Expired, Discontinued 404) | Exceeded |
| **Automated Test Suite** | Required | **13/13 passing tests** (Pytest unit & API suite) | 100% Pass |
