"""
Extractor module with strict Anti-Hallucination constraints.
Extracts structured Atlas scholarship records and constructs a field-by-field evidence ledger
containing verbatim citations. If a field is not found in the source text, it is set to 'Not specified'.
"""
import re
from typing import Dict, Any, List, Optional, Tuple


INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Chandigarh", "Puducherry"
]


def extract_verbatim_snippet(text: str, match_text: str, context_chars: int = 60) -> str:
    """Finds match_text in source text and returns an expanded excerpt for context."""
    if not text or not match_text:
        return ""
    pos = text.lower().find(match_text.lower())
    if pos == -1:
        return match_text
    start = max(0, pos - context_chars)
    end = min(len(text), pos + len(match_text) + context_chars)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def extract_amounts(text: str) -> Tuple[str, Optional[float], Optional[str]]:
    """
    Extracts monetary benefits and provides exact snippet evidence.
    """
    amount_patterns = [
        r"(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d+)?)\s*(?:per\s*(?:annum|year|month)|/-\s*per\s*year|p\.a\.|once)?",
        r"(?:up to|upto|maximum of|worth)\s*(?:₹|Rs\.?|INR)\s*([\d,]+)",
        r"(?:₹|Rs\.?|INR)\s*([\d,]+)\s*(?:lakh|lakhs|LPA)",
        r"(?:100%|50%|full)\s*(?:tuition fee waiver|fee reimbursement|financial assistance)"
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_str = match.group(0)
            snippet = extract_verbatim_snippet(text, matched_str)
            # Try parsing numerical
            num_match = re.search(r"[\d,]+", matched_str)
            num_val = None
            if num_match:
                try:
                    num_val = float(num_match.group(0).replace(",", ""))
                    if "lakh" in matched_str.lower():
                        num_val = num_val * 100000
                except ValueError:
                    num_val = None
            return matched_str, num_val, snippet
            
    return "Not specified", None, None


def extract_deadlines(text: str) -> Tuple[str, Optional[str]]:
    """
    Extracts application deadlines / closing dates with text snippet.
    """
    date_patterns = [
        r"(?:last date|closing date|deadline|application closes|apply before|end date)\s*(?:is|:|-)?\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{4})",
        r"(?:last date|closing date|deadline)\s*(?:is|:|-)?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
        r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_date = match.group(1) if len(match.groups()) > 0 else match.group(0)
            snippet = extract_verbatim_snippet(text, match.group(0))
            return matched_date.strip(), snippet
            
    return "Not specified", None


def extract_income_limit(text: str) -> Tuple[str, Optional[str]]:
    """
    Extracts family income threshold with evidence snippet.
    """
    income_patterns = [
        r"(?:family income|parental income|annual income|gross income)\s*(?:must not exceed|should not exceed|not exceeding|not more than|not greater than|less than|up to|below|shall be less than|is less than|shall not exceed)?\s*(?:₹|Rs\.?|INR)?\s*([\d,.]+\s*(?:lakh|lakhs|LPA|per annum|per year|/-)?)",
        r"(?:income limit|income criteria|income ceiling)\s*(?:is|:|-)?\s*(?:₹|Rs\.?|INR)?\s*([\d,.]+\s*(?:lakh|lakhs|LPA|per annum)?)",
        r"(?:below poverty line|BPL|EWS category)"
    ]
    
    for pattern in income_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_str = match.group(0)
            snippet = extract_verbatim_snippet(text, matched_str)
            return matched_str.strip(), snippet
            
    return "Not specified", None


def extract_academic_criteria(text: str) -> Tuple[str, Optional[str]]:
    """
    Extracts minimum percentage, CGPA, or qualifying exam criteria.
    """
    academic_patterns = [
        r"(?:minimum|at least|securing|scored)\s*(\d{1,2}%\s*(?:marks|aggregate)?|\d\.\d\s*CGPA)",
        r"(?:top\s*\d+%\s*in\s*class\s*12|merit in qualifying examination|valid\s*(?:JEE|GATE|NEET)\s*score)",
        r"(?:passed\s*class\s*(?:10|12|graduation)\s*with\s*\d{1,2}%|\d{1,2}%\s*in\s*previous\s*academic\s*year)"
    ]
    
    for pattern in academic_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_str = match.group(0)
            snippet = extract_verbatim_snippet(text, matched_str)
            return matched_str.strip(), snippet
            
    return "Not specified", None


def extract_gender_criteria(text: str) -> Tuple[str, Optional[str]]:
    """
    Detects targeted gender requirements.
    """
    if re.search(r"\b(?:girls? only|women only|female students?|girl child|for girls)\b", text, re.IGNORECASE):
        match = re.search(r"\b(?:girls? only|women only|female students?|girl child|for girls)\b", text, re.IGNORECASE)
        snippet = extract_verbatim_snippet(text, match.group(0))
        return "Female Only", snippet
    elif re.search(r"\b(?:transgender|third gender)\b", text, re.IGNORECASE):
        match = re.search(r"\b(?:transgender|third gender)\b", text, re.IGNORECASE)
        snippet = extract_verbatim_snippet(text, match.group(0))
        return "Transgender Inclusive", snippet
    return "All", None


def extract_category_criteria(text: str) -> Tuple[str, Optional[str]]:
    """
    Detects targeted caste/social category reservation.
    """
    categories = []
    snippets = []
    
    if re.search(r"\b(?:SC/ST|SC\s*&\s*ST|Scheduled Caste|Scheduled Tribe)\b", text, re.IGNORECASE):
        categories.append("SC/ST")
        match = re.search(r"\b(?:SC/ST|SC\s*&\s*ST|Scheduled Caste|Scheduled Tribe)\b", text, re.IGNORECASE)
        snippets.append(extract_verbatim_snippet(text, match.group(0)))
        
    if re.search(r"\b(?:OBC|Other Backward Classes)\b", text, re.IGNORECASE):
        categories.append("OBC")
        
    if re.search(r"\b(?:Minorities|Minority Communities|Muslim|Christian|Sikh|Buddhist|Jain|Parsi)\b", text, re.IGNORECASE):
        categories.append("Minority")
        
    if re.search(r"\b(?:EWS|Economically Weaker Section)\b", text, re.IGNORECASE):
        categories.append("EWS")
        
    if re.search(r"\b(?:PWD|Physically Challenged|Divyangjan|Specially Abled|Disability)\b", text, re.IGNORECASE):
        categories.append("Disability / PWD")
        
    if categories:
        combined = ", ".join(categories)
        return combined, (snippets[0] if snippets else combined)
        
    return "All Categories", None


def extract_domicile(text: str) -> Tuple[str, Optional[str]]:
    """
    Detects state domicile requirements or Pan-India applicability.
    """
    for state in INDIAN_STATES:
        pattern = rf"\b(?:domicile of|resident of|belonging to|studying in)\s+{re.escape(state)}\b|\b{re.escape(state)}\s+domicile\b"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            snippet = extract_verbatim_snippet(text, match.group(0))
            return state, snippet
            
    # Check if specifically state name appears prominently
    for state in INDIAN_STATES:
        if f"Government of {state}" in text or f"Govt of {state}" in text or f"{state} State" in text:
            match = re.search(rf"(?:Government of|Govt of|State of)\s+{re.escape(state)}", text, re.IGNORECASE)
            snippet = extract_verbatim_snippet(text, match.group(0) if match else state)
            return state, snippet
            
    return "All India", None


def extract_education_level(text: str) -> Tuple[str, Optional[str]]:
    """
    Extracts applicable course / degree level.
    """
    if re.search(r"\b(?:Ph\.?D|Doctoral|Research Scholars?|Postdoctoral)\b", text, re.IGNORECASE):
        return "Doctoral (Ph.D / Research)", extract_verbatim_snippet(text, "PhD")
    elif re.search(r"\b(?:Postgraduate|PG|Master'?s|M\.Tech|M\.Sc|MBA|MD)\b", text, re.IGNORECASE):
        return "Postgraduate (PG / M.Tech / M.Sc / MBA)", extract_verbatim_snippet(text, "Postgraduate")
    elif re.search(r"\b(?:Undergraduate|UG|Bachelor'?s|B\.Tech|B\.E|MBBS|B\.Sc|B\.Com|BA)\b", text, re.IGNORECASE):
        return "Undergraduate (UG / B.Tech / MBBS / B.Sc)", extract_verbatim_snippet(text, "Undergraduate")
    elif re.search(r"\b(?:Diploma|Polytechnic|ITI)\b", text, re.IGNORECASE):
        return "Diploma / Polytechnic", extract_verbatim_snippet(text, "Diploma")
    elif re.search(r"\b(?:Class\s*1[0-2]|Class\s*[1-9]|School|High School|Matric)\b", text, re.IGNORECASE):
        return "School (Class 1-12)", extract_verbatim_snippet(text, "School")
    return "All Levels", None


def build_evidence_ledger(
    source_url: str,
    fields_extracted: Dict[str, Tuple[str, Optional[str]]]
) -> Dict[str, Dict[str, str]]:
    """
    Constructs an evidence ledger connecting each field to its verbatim source excerpt.
    """
    ledger = {}
    for field_name, (val, snippet) in fields_extracted.items():
        if snippet and val != "Not specified":
            ledger[field_name] = {
                "field_name": field_name,
                "extracted_value": val,
                "snippet": snippet,
                "source_url": source_url,
                "match_type": "VERBATIM_EVIDENCE"
            }
    return ledger
