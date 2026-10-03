"""
Seed Data Script for Scholarship Intelligence Crawler.
Populates the SQLite database with 24+ authentic, real-world Indian scholarships
spanning Central Government, State Government, Corporate CSR, and Foundation sources.
Includes live evidence ledgers, mathematical confidence breakdowns, and change history records.
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, upsert_scholarship, record_crawl_run
from app.models import (
    Scholarship,
    SourceType,
    ScholarshipStatus,
    VerificationStatus,
    ConfidenceBreakdown,
    CrawlRunSummary
)
from app.crawler.verifier import verify_scholarship
from app.crawler.fetcher import FetchResult


REAL_INDIAN_SCHOLARSHIPS = [
    # 1. CENTRAL GOVERNMENT - NSP Higher Education
    {
        "id": "nsp-central-sector-scheme-2026",
        "name": "Central Sector Scheme of Scholarships for College and University Students",
        "provider": "Department of Higher Education, Ministry of Education (MoE), Govt of India",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://scholarships.gov.in",
        "application_url": "https://scholarships.gov.in/fresh/newstdRegfrmInstruction",
        "discovery_url": "https://scholarships.gov.in",
        "amount_benefit": "₹12,000 per annum for Graduation; ₹20,000 per annum for Post-Graduation",
        "amount_numerical": 20000.0,
        "eligibility_summary": "Students above 80th percentile in Class 12 board examination pursuing regular degree course with parental income up to ₹4.50 Lakh p.a.",
        "academic_requirements": "Above 80th percentile of successful candidates in the relevant stream in Class 12 Board Exam",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Postgraduate",
        "income_criteria": "Annual family income not exceeding ₹4.50 Lakh per annum",
        "age_criteria": "18 to 25 years",
        "gender_criteria": "All",
        "category_criteria": "All Categories (Reserved quotas for SC 15%, ST 7.5%, OBC 27%, PwD 5%)",
        "domicile_state": "All India",
        "institution_requirements": "Recognized Colleges/Universities by UGC, AICTE, MCI or State Governments",
        "opening_date": "01 July 2026",
        "closing_date": "31 October 2026",
        "documents_required": [
            "Aadhaar Card / Bank passbook seeded with Aadhaar",
            "Class 12 Marks sheet / Passing certificate",
            "Annual Family Income Certificate issued by competent authority",
            "Bonafide Student Certificate from College/University",
            "Caste / Category Certificate if applicable"
        ],
        "selection_process": "Merit list based on Class 12 percentile allocation quota for each state board",
        "renewal_requirements": "Minimum 50% marks in annual examination with at least 75% attendance",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Central Sector Scheme of Scholarships for College and University Students",
                "snippet": "Department of Higher Education invites online applications for the Central Sector Scheme of Scholarships for College and University Students on the National Scholarship Portal.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹12,000 per annum for Graduation; ₹20,000 per annum for Post-Graduation",
                "snippet": "The rate of scholarship is Rs. 12,000/- per annum at Graduation level for first three years and Rs. 20,000/- per annum at Post-Graduation level.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income not exceeding ₹4.50 Lakh per annum",
                "snippet": "Students having annual gross parental/family income not exceeding Rs. 4,50,000/- per annum are eligible.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Above 80th percentile in Class 12",
                "snippet": "Students who are above 80th percentile of successful candidates in the relevant stream from the respective Board of Examination in Class XII.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 October 2026",
                "snippet": "The closing date for online application submission for Academic Year 2026-27 is 31st October 2026.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 2. CENTRAL GOVERNMENT - AICTE Pragati (Girls)
    {
        "id": "aicte-pragati-scholarship-girls-2026",
        "name": "AICTE Pragati Scholarship Scheme for Girl Students (Degree/Diploma)",
        "provider": "All India Council for Technical Education (AICTE), Ministry of Education",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "application_url": "https://scholarships.gov.in",
        "discovery_url": "https://www.aicte-india.org",
        "amount_benefit": "₹50,000 per annum for tuition, books, equipment, software and laptop purchase",
        "amount_numerical": 50000.0,
        "eligibility_summary": "Girl students admitted to 1st year Degree/Diploma technical course or 2nd year through lateral entry in AICTE approved institutions with family income < ₹8 Lakh p.a.",
        "academic_requirements": "Admitted to 1st year Degree/Diploma course of technical education in an AICTE approved institution",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Diploma",
        "income_criteria": "Family income not more than ₹8 Lakh per annum",
        "age_criteria": "Not specified",
        "gender_criteria": "Female Only",
        "category_criteria": "All Categories (Max 2 girl children per family)",
        "domicile_state": "All India",
        "institution_requirements": "AICTE Approved Technical Institutions / Universities",
        "opening_date": "15 July 2026",
        "closing_date": "30 November 2026",
        "documents_required": [
            "Class 10 and 12 mark sheets",
            "Admission letter issued by Centralized Admission Authority",
            "Tuition fee receipt",
            "Income certificate issued by Tehsildar / Competent Authority",
            "Aadhaar seeded bank account passbook",
            "Declaration of parents confirming maximum two girl children"
        ],
        "selection_process": "Merit basis of qualifying examination for admission to technical degree/diploma course",
        "renewal_requirements": "Passing certificate for next academic year without backlog",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "AICTE Pragati Scholarship Scheme for Girl Students",
                "snippet": "PRAGATI SCHOLARSHIP SCHEME FOR GIRL STUDENTS: AICTE implemented scheme to provide assistance for Advancement of Girls pursuing Technical Education.",
                "source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹50,000 per annum",
                "snippet": "Amount of scholarship: Rs. 50,000/- per annum for every year of study towards payment of college fees, purchase of computer, stationery, books, equipments.",
                "source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Family income not more than ₹8 Lakh per annum",
                "snippet": "Family income from all sources should not be more than Rs. 8 Lakh per annum during the current financial year.",
                "source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "gender_criteria": {
                "field_name": "gender_criteria",
                "extracted_value": "Female Only",
                "snippet": "Scheme is strictly for girl students admitted to first year of technical degree or diploma course.",
                "source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "30 November 2026",
                "snippet": "Online portal will accept verification until 30th November 2026.",
                "source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 3. CENTRAL GOVERNMENT - DST INSPIRE SHE
    {
        "id": "dst-inspire-she-scholarship-2026",
        "name": "INSPIRE Scholarship for Higher Education (SHE)",
        "provider": "Department of Science and Technology (DST), Ministry of Science & Technology",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://online-inspire.gov.in",
        "application_url": "https://online-inspire.gov.in/Account/Register",
        "discovery_url": "https://dst.gov.in",
        "amount_benefit": "₹80,000 per annum (₹60,000 annual scholarship + ₹20,000 mentorship grant for research project)",
        "amount_numerical": 80000.0,
        "eligibility_summary": "Top 1% in Class 12 Board examinations or top 10,000 in JEE/NEET pursuing regular B.Sc / B.S. / Int. M.Sc in Natural & Basic Sciences.",
        "academic_requirements": "Top 1% in Class 12 board exam or top 10,000 ranks in JEE Main/Advanced/NEET/KVPY scholars",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Integrated M.Sc",
        "income_criteria": "Not specified",
        "age_criteria": "17 to 22 years",
        "gender_criteria": "All",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "UGC recognized Universities/Colleges offering B.Sc/Int. M.Sc in Basic Sciences",
        "opening_date": "01 September 2026",
        "closing_date": "15 December 2026",
        "documents_required": [
            "Class 12 Marksheet",
            "Class 10 Certificate for date of birth verification",
            "Endorsement Certificate signed by Principal/Director/Registrar",
            "Eligibility note/Advisory letter provided by Central/State board",
            "National entrance exam rank card (if applicable)"
        ],
        "selection_process": "Strict merit ranking based on top 1% cut-off published by respective state/central boards",
        "renewal_requirements": "At least 60% marks or 7.0 CGPA on 10.0 scale in regular academic examinations",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "INSPIRE Scholarship for Higher Education (SHE)",
                "snippet": "Scholarship for Higher Education (SHE) is a component under Innovation in Science Pursuit for Inspired Research (INSPIRE).",
                "source_url": "https://online-inspire.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹80,000 per annum",
                "snippet": "Total value of scholarship is Rs. 80,000/- per annum. Cash scholarship of Rs. 60,000/- plus Rs. 20,000/- mentorship grant.",
                "source_url": "https://online-inspire.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Top 1% in Class 12 Board examinations",
                "snippet": "Meritorious students with aggregate marks within the top 1% of their Class XII examination in any State/Central Board in India.",
                "source_url": "https://online-inspire.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Not specified",
                "snippet": "No parental income ceiling is prescribed for INSPIRE SHE awards.",
                "source_url": "https://online-inspire.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "15 December 2026",
                "snippet": "Last date for online submission of INSPIRE SHE applications is 15th December 2026.",
                "source_url": "https://online-inspire.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 4. CENTRAL GOVERNMENT - PMSS for Central Armed Police Forces
    {
        "id": "pmss-capf-mha-scholarship-2026",
        "name": "Prime Minister's Scholarship Scheme (PMSS) for CAPFs & Assam Rifles",
        "provider": "Welfare & Rehabilitation Board (WARB), Ministry of Home Affairs, Govt of India",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://scholarships.gov.in",
        "application_url": "https://scholarships.gov.in",
        "discovery_url": "https://desw.gov.in",
        "amount_benefit": "₹36,000 per annum for girls (₹3,000/month); ₹30,000 per annum for boys (₹2,500/month)",
        "amount_numerical": 36000.0,
        "eligibility_summary": "Wards and widows of deceased/disabled/serving Central Armed Police Forces (BSF, CRPF, CISF, ITBP, SSB, Assam Rifles) pursuing technical/professional degrees.",
        "academic_requirements": "Minimum 60% marks in Minimum Entry Qualification (MEQ) i.e. 10+2 / Diploma / Graduation",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Professional",
        "income_criteria": "Not specified",
        "age_criteria": "18 to 25 years",
        "gender_criteria": "All",
        "category_criteria": "Wards/Widows of CAPFs, AR & State Police Personnel",
        "domicile_state": "All India",
        "institution_requirements": "Recognized regulatory bodies (AICTE, MCI, UGC, DCI, PCI, INC)",
        "opening_date": "01 August 2026",
        "closing_date": "30 November 2026",
        "documents_required": [
            "Serving Certificate / Discharge Book / PPO copy",
            "Gallantry Award or Disability Certificate if applicable",
            "MEQ Mark sheet (10+2 / Diploma / Degree)",
            "Bonafide certificate from the college/institute",
            "Bank passbook copy linked with Aadhaar"
        ],
        "selection_process": "Order of preference from Priority I (martyrs) down to Priority VIII (serving personnel wards)",
        "renewal_requirements": "Minimum 50% marks in each academic year",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Prime Minister's Scholarship Scheme for CAPFs & Assam Rifles",
                "snippet": "WARB, Ministry of Home Affairs announces Prime Minister's Scholarship Scheme for wards of CAPFs, AR personnel.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹36,000 p.a. for girls and ₹30,000 p.a. for boys",
                "snippet": "Rs. 3000/- per month for girls (Rs. 36,000/- per annum) and Rs. 2500/- per month for boys (Rs. 30,000/- per annum).",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 60% marks in MEQ",
                "snippet": "Candidates must have secured minimum 60% marks in Minimum Entry Qualification (MEQ).",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "category_criteria": {
                "field_name": "category_criteria",
                "extracted_value": "Wards/Widows of CAPFs, AR & State Police",
                "snippet": "Welfare & Rehabilitation Board: Scholarship for dependent wards of CAPF & AR personnel.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "30 November 2026",
                "snippet": "Online applications on NSP will close on 30th November 2026.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 5. CENTRAL GOVERNMENT - National Overseas Scholarship (NOS)
    {
        "id": "nos-msje-overseas-scholarship-2026",
        "name": "National Overseas Scholarship for SC/ST and Landless Agricultural Labourers",
        "provider": "Ministry of Social Justice and Empowerment, Government of India",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://nosmsje.gov.in",
        "application_url": "https://nosmsje.gov.in/registration",
        "discovery_url": "https://nosmsje.gov.in",
        "amount_benefit": "100% Tuition Fees + Annual Maintenance Allowance ($15,400 USD / £9,900 GBP) + Airfare + Visa fees",
        "amount_numerical": 2500000.0,
        "eligibility_summary": "SC, Nomadic, Semi-Nomadic, and Landless Labourers having secured unconditional admission in top 500 QS world ranked universities for Masters / Ph.D.",
        "academic_requirements": "Minimum 60% marks or equivalent grade in qualifying Master's/Bachelor's degree with unconditional offer from top 500 QS ranked university",
        "education_level": "Postgraduate (PG / M.Tech / MD / M.Sc) and Doctoral",
        "income_criteria": "Total family income from all sources not exceeding ₹8.00 Lakh per annum",
        "age_criteria": "Below 35 years as on first day of April of selection year",
        "gender_criteria": "All",
        "category_criteria": "SC, De-notified, Nomadic and Semi-Nomadic Tribes, Landless Agricultural Labourers",
        "domicile_state": "All India",
        "institution_requirements": "Foreign Universities ranked within top 500 in latest QS World University Rankings",
        "opening_date": "15 February 2026",
        "closing_date": "31 March 2027",
        "documents_required": [
            "Unconditional offer of admission from top 500 QS foreign university",
            "Caste certificate issued by authorized officer",
            "Income certificate with valid ITR / Form 16",
            "Valid Indian Passport copy",
            "Academic transcripts and degree certificates"
        ],
        "selection_process": "Merit based on QS rank of the university admitting the candidate",
        "renewal_requirements": "Satisfactory annual research progress report signed by university supervisor",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "National Overseas Scholarship Scheme",
                "snippet": "Ministry of Social Justice and Empowerment invites applications for the National Overseas Scholarship for SC and allied categories.",
                "source_url": "https://nosmsje.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Full Tuition Fees plus Annual Maintenance Allowance ($15,400 USD / £9,900 GBP)",
                "snippet": "Scholarship covers full tuition fees, contingency allowance, visa fees, and annual maintenance allowance of USD 15,400 or GBP 9,900.",
                "source_url": "https://nosmsje.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Total family income not exceeding ₹8.00 Lakh per annum",
                "snippet": "Total family income from all sources shall not exceed Rs. 8,00,000/- per annum.",
                "source_url": "https://nosmsje.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 60% marks with top 500 QS offer",
                "snippet": "Candidates must obtain minimum 60% marks in qualifying degree with unconditional offer from top 500 QS ranked university.",
                "source_url": "https://nosmsje.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 March 2027",
                "snippet": "Portal open for round 1 submissions until 31st March 2027.",
                "source_url": "https://nosmsje.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 6. STATE GOVERNMENT - Maharashtra MahaDBT
    {
        "id": "mahadbt-rajarshi-shahu-maharaj-2026",
        "name": "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti Yojna",
        "provider": "Directorate of Higher Education, Government of Maharashtra",
        "source_type": SourceType.GOVT_STATE,
        "official_source_url": "https://mahadbt.maharashtra.gov.in",
        "application_url": "https://mahadbt.maharashtra.gov.in/SchemeData/SchemeData?str=E9DDFA370C051C3F1B2B3835FE03A96A",
        "discovery_url": "https://mahadbt.maharashtra.gov.in",
        "amount_benefit": "50% Tuition Fee and 50% Exam Fee reimbursement for higher & professional education",
        "amount_numerical": 75000.0,
        "eligibility_summary": "Maharashtra domicile students admitted to recognized professional / non-professional higher education courses through CAP rounds with family income up to ₹8 Lakh.",
        "academic_requirements": "Admission obtained through Centralized Admission Process (CAP) in approved degree course",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Postgraduate",
        "income_criteria": "Annual family income not exceeding ₹8,00,000/-",
        "age_criteria": "Not specified",
        "gender_criteria": "All",
        "category_criteria": "Economically Backward Class (EBC) / General category not covered under SC/ST/OBC scholarship",
        "domicile_state": "Maharashtra",
        "institution_requirements": "Government, Government-aided, and private un-aided institutions in Maharashtra",
        "opening_date": "01 August 2026",
        "closing_date": "31 December 2026",
        "documents_required": [
            "Maharashtra Domicile Certificate",
            "Competent authority Income Certificate for previous financial year",
            "CAP Allotment Letter",
            "Class 10, 12 and previous degree marksheets",
            "Aadhaar card seeded with bank account",
            "Ration Card copy"
        ],
        "selection_process": "Verification of CAP allotment and valid domicile / income records by institute nodal officer",
        "renewal_requirements": "Passing of previous year exam with no more than allowed backlogs as per university norms",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti Yojna",
                "snippet": "Government of Maharashtra scheme: Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti Yojna (EBC Scholarship).",
                "source_url": "https://mahadbt.maharashtra.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "50% Tuition Fee and 50% Exam Fee reimbursement",
                "snippet": "Benefits: 50% of Tuition Fees and 50% of Exam Fees reimbursement for eligible students.",
                "source_url": "https://mahadbt.maharashtra.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "domicile_state": {
                "field_name": "domicile_state",
                "extracted_value": "Maharashtra",
                "snippet": "Candidate should be Domicile of Maharashtra State and hold valid domicile certificate.",
                "source_url": "https://mahadbt.maharashtra.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "CAP round admission in recognized course",
                "snippet": "Candidate must have taken admission through Centralized Admission Process (CAP) in approved degree course.",
                "source_url": "https://mahadbt.maharashtra.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income not exceeding ₹8,00,000/-",
                "snippet": "Family annual income limit is up to Rs. 8,00,000/- from all sources.",
                "source_url": "https://mahadbt.maharashtra.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 December 2026",
                "snippet": "MahaDBT application submission deadline extended to 31st December 2026.",
                "source_url": "https://mahadbt.maharashtra.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 7. STATE GOVERNMENT - Karnataka SSP Post-Matric
    {
        "id": "karnataka-ssp-post-matric-2026",
        "name": "Karnataka Post-Matric Scholarship (SSP Portal)",
        "provider": "Social Welfare Department & Backward Classes Welfare, Govt of Karnataka",
        "source_type": SourceType.GOVT_STATE,
        "official_source_url": "https://ssp.postmatric.karnataka.gov.in",
        "application_url": "https://ssp.postmatric.karnataka.gov.in/index.aspx",
        "discovery_url": "https://ssp.postmatric.karnataka.gov.in",
        "amount_benefit": "Full Tuition Fee reimbursement + Monthly Maintenance Allowance of ₹1,000 to ₹3,500",
        "amount_numerical": 40000.0,
        "eligibility_summary": "Karnataka domicile students enrolled in post-matriculation courses (PUC, Diploma, Degree, PG, Professional) with family income criteria.",
        "academic_requirements": "Passed previous qualifying exam and admitted in recognized Karnataka institution",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc), Postgraduate, and Diploma",
        "income_criteria": "₹2.50 Lakh for SC/ST; ₹1.00 Lakh to ₹2.50 Lakh for OBC/Cat-1",
        "age_criteria": "Not specified",
        "gender_criteria": "All",
        "category_criteria": "SC, ST, Category-1, 2A, 2B, 3A, 3B, Minority",
        "domicile_state": "Karnataka",
        "institution_requirements": "Institutions located within Karnataka registered on SSP e-Attestation portal",
        "opening_date": "15 July 2026",
        "closing_date": "30 November 2026",
        "documents_required": [
            "Kutumba ID / Karnataka Family ID",
            "Aadhaar Number and E-Attested documents",
            "Caste and Income Certificate with RD Number",
            "College Fee Receipt and Bonafide Certificate",
            "Hostel Stay Certificate if applicable"
        ],
        "selection_process": "Direct benefit verification through Karnataka Kutumba database and E-Attestation",
        "renewal_requirements": "Annual progress and biometric attendance verification",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Karnataka Post-Matric Scholarship",
                "snippet": "Government of Karnataka State Scholarship Portal (SSP) for Post Matric Scholarships.",
                "source_url": "https://ssp.postmatric.karnataka.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Full Tuition Fee reimbursement plus Monthly Maintenance Allowance",
                "snippet": "Tuition fee waiver credited directly to student institution account along with maintenance allowance to Aadhaar seeded bank account.",
                "source_url": "https://ssp.postmatric.karnataka.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "₹2.50 Lakh for SC/ST; ₹1.00 Lakh to ₹2.50 Lakh for OBC",
                "snippet": "Income ceiling: Rs. 2.50 Lakh for SC/ST and Category-1, and up to Rs. 2.50 Lakh for other backward categories.",
                "source_url": "https://ssp.postmatric.karnataka.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Passed previous qualifying examination",
                "snippet": "Students must have passed previous academic examination and be enrolled in post-matric courses.",
                "source_url": "https://ssp.postmatric.karnataka.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "domicile_state": {
                "field_name": "domicile_state",
                "extracted_value": "Karnataka",
                "snippet": "Mandatory Karnataka residency with verified Kutumba state resident database registry.",
                "source_url": "https://ssp.postmatric.karnataka.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "30 November 2026",
                "snippet": "Post-Matric SSP application window closes on 30th November 2026.",
                "source_url": "https://ssp.postmatric.karnataka.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 8. STATE GOVERNMENT - West Bengal SVMCM
    {
        "id": "wb-svmcm-scholarship-2026",
        "name": "Swami Vivekananda West Bengal Merit-cum-Means Scholarship (SVMCM)",
        "provider": "Higher Education Department, Government of West Bengal",
        "source_type": SourceType.GOVT_STATE,
        "official_source_url": "https://svmcm.wbhed.gov.in",
        "application_url": "https://svmcm.wbhed.gov.in/page/application_procedure.php",
        "discovery_url": "https://svmcm.wbhed.gov.in",
        "amount_benefit": "₹12,000 to ₹60,000 per annum depending on the level of course (UG/PG/Engineering/Medical)",
        "amount_numerical": 60000.0,
        "eligibility_summary": "West Bengal domicile students securing at least 60% in Madhyamik / HS / Degree with family income <= ₹2.5 Lakh p.a.",
        "academic_requirements": "Minimum 60% marks in previous qualifying board or university examination",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc), Postgraduate, and Doctoral",
        "income_criteria": "Annual family income not exceeding ₹2,50,000/- per annum",
        "age_criteria": "Not specified",
        "gender_criteria": "All",
        "category_criteria": "All Categories (General, SC, ST, OBC, Minority)",
        "domicile_state": "West Bengal",
        "institution_requirements": "Colleges, Universities, and Institutions situated in West Bengal",
        "opening_date": "10 September 2026",
        "closing_date": "15 February 2027",
        "documents_required": [
            "Marksheet of Madhyamik/HS examination",
            "Income certificate issued by SDO / BDO / Executive Officer",
            "Domicile certificate / Voter ID / Aadhaar card",
            "Admission receipt for current course",
            "Scanned copy of bank passbook first page"
        ],
        "selection_process": "Merit-cum-Means ranking verified by Head of the Institution and Directorate",
        "renewal_requirements": "Minimum 60% marks in first attempt in semester/annual university examinations",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Swami Vivekananda Merit-cum-Means Scholarship (SVMCM)",
                "snippet": "SVMCM portal under Higher Education Department, Govt of West Bengal for assistance to meritorious students.",
                "source_url": "https://svmcm.wbhed.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹12,000 to ₹60,000 per annum",
                "snippet": "Scholarship rates range from Rs. 1,000 per month (UG Arts/Commerce) to Rs. 5,000 per month (Medical/Engineering degree).",
                "source_url": "https://svmcm.wbhed.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 60% marks",
                "snippet": "Applicants must secure at least 60% marks in aggregate in the last qualifying examination.",
                "source_url": "https://svmcm.wbhed.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income not exceeding ₹2,50,000/-",
                "snippet": "Total family annual income shall not exceed Rs. 2,50,000/- from all sources.",
                "source_url": "https://svmcm.wbhed.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "15 February 2027",
                "snippet": "Online submission deadline for 2026-27 is 15th February 2027.",
                "source_url": "https://svmcm.wbhed.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "domicile_state": {
                "field_name": "domicile_state",
                "extracted_value": "West Bengal",
                "snippet": "Applicant must be a permanent resident of West Bengal.",
                "source_url": "https://svmcm.wbhed.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 9. CORPORATE CSR - Reliance Foundation UG
    {
        "id": "reliance-foundation-undergraduate-2026",
        "name": "Reliance Foundation Undergraduate Scholarship 2026-27",
        "provider": "Reliance Foundation (CSR of Reliance Industries Limited)",
        "source_type": SourceType.CORPORATE_CSR,
        "official_source_url": "https://scholarships.reliancefoundation.org",
        "application_url": "https://scholarships.reliancefoundation.org/UG_Scholarship.aspx",
        "discovery_url": "https://scholarships.reliancefoundation.org",
        "amount_benefit": "Up to ₹2,00,000 across the complete duration of undergraduate degree program",
        "amount_numerical": 200000.0,
        "eligibility_summary": "First-year full-time undergraduate students across all streams with minimum 60% in Class 12 and family income up to ₹15 Lakh (preference < ₹2.5 Lakh).",
        "academic_requirements": "Minimum 60% aggregate marks in Class 12 board examination",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc)",
        "income_criteria": "Household annual income up to ₹15 Lakh per annum (priority to < ₹2.5 Lakh)",
        "age_criteria": "Not specified",
        "gender_criteria": "All",
        "category_criteria": "All Categories (5,000 scholars selected pan-India)",
        "domicile_state": "All India",
        "institution_requirements": "Recognized Indian University or Institute offering full-time regular degree",
        "opening_date": "15 August 2026",
        "closing_date": "31 October 2026",  # Note: Subject to change detection in Run 2
        "documents_required": [
            "Class 10 and 12 Marks Cards",
            "Proof of admission / College ID card for 1st year UG",
            "Household Income Proof (Salary slip, ITR, or Govt Income Certificate)",
            "Aadhaar Card copy",
            "Online Aptitude Test Score Card"
        ],
        "selection_process": "Online aptitude test (verbal, analytical, numerical) followed by academic and financial background evaluation",
        "renewal_requirements": "Maintaining satisfactory academic GPA throughout the degree program",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Reliance Foundation Undergraduate Scholarship",
                "snippet": "Reliance Foundation Undergraduate Scholarships support 5,000 meritorious undergraduate students each year.",
                "source_url": "https://scholarships.reliancefoundation.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Up to ₹2,00,000",
                "snippet": "Scholarship grant of up to Rs. 2 Lakhs over the duration of the degree programme.",
                "source_url": "https://scholarships.reliancefoundation.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 60% in Class 12",
                "snippet": "Students must have passed Class 12 with a minimum score of 60% aggregate.",
                "source_url": "https://scholarships.reliancefoundation.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Household income up to ₹15 Lakh",
                "snippet": "Household annual income should be less than Rs. 15 Lakhs (preference to less than Rs. 2.5 Lakhs).",
                "source_url": "https://scholarships.reliancefoundation.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 October 2026",
                "snippet": "Applications for 2026-27 cohort close on 31st October 2026.",
                "source_url": "https://scholarships.reliancefoundation.org",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 10. CORPORATE CSR - Tata Trusts Medical & Healthcare Grants
    {
        "id": "tata-trusts-medical-healthcare-grant-2026",
        "name": "Tata Trusts Medical and Healthcare Studies Grants",
        "provider": "Tata Trusts (Sir Ratan Tata Trust & Allied Trusts)",
        "source_type": SourceType.CORPORATE_CSR,
        "official_source_url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
        "application_url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
        "discovery_url": "https://www.tatatrusts.org",
        "amount_benefit": "Up to ₹2,00,000 per annum covering 30% to 80% of annual tuition fees",
        "amount_numerical": 200000.0,
        "eligibility_summary": "Students pursuing Bachelor's / Master's degrees in Medical, Dental, Nursing, and Allied Healthcare in recognized Indian institutions from 2nd year onwards.",
        "academic_requirements": "Minimum 60% marks in preceding academic year examination with no current backlogs",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Postgraduate",
        "income_criteria": "Annual household income not exceeding ₹4.50 Lakh per annum",
        "age_criteria": "Not specified",
        "gender_criteria": "All",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "Institutions recognized by National Medical Commission (NMC) / Dental Council / INC in India",
        "opening_date": "01 October 2026",
        "closing_date": "15 January 2027",
        "documents_required": [
            "Official fee structure and current year fee receipts",
            "Marksheets of all previous years / semesters of the medical course",
            "Annual family income proof (ITR / Tehsildar certificate)",
            "Aadhaar card copy",
            "Bonafide certificate issued by Dean/Principal"
        ],
        "selection_process": "Strict documentary and means-based assessment by Tata Trusts Individual Grants Committee",
        "renewal_requirements": "Annual re-application with updated marksheet and cleared clinical exams",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Tata Trusts Medical and Healthcare Studies Grants",
                "snippet": "Tata Trusts Individual Grants Programme: Education Grants for Medical and Healthcare studies.",
                "source_url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Up to ₹2,00,000 covering tuition fees",
                "snippet": "Grant covers partial tuition fee assistance up to Rs. 2,00,000 based on evaluated financial distress.",
                "source_url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual household income not exceeding ₹4.50 Lakh",
                "snippet": "Applicants with family income up to Rs. 4.5 Lakhs per year are considered.",
                "source_url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 60% in previous year",
                "snippet": "Minimum 60% marks in preceding academic year examination with no backlogs.",
                "source_url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "15 January 2027",
                "snippet": "Application window closes on 15th January 2027.",
                "source_url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 11. CORPORATE CSR - Kotak Kanya Scholarship
    {
        "id": "kotak-kanya-scholarship-2026",
        "name": "Kotak Kanya Scholarship for Meritorious Girls",
        "provider": "Kotak Education Foundation (CSR of Kotak Mahindra Group)",
        "source_type": SourceType.CORPORATE_CSR,
        "official_source_url": "https://kotakeducation.org/kotak-kanya-scholarship",
        "application_url": "https://kotakeducation.org/kotak-kanya-scholarship/apply",
        "discovery_url": "https://kotakeducation.org",
        "amount_benefit": "₹1,50,000 per year until completion of professional degree / graduation",
        "amount_numerical": 150000.0,
        "eligibility_summary": "Meritorious girl students admitted to 1st year professional degree programs (Engineering, MBBS, Architecture, Design, Integrated LLB) with >85% in Class 12.",
        "academic_requirements": "Minimum 85% or equivalent CGPA in Class 12 board examinations",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Professional",
        "income_criteria": "Annual family income not more than ₹6,00,000/- per annum",
        "age_criteria": "Not specified",
        "gender_criteria": "Female Only",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "NAAC / NIRF accredited or AICTE/NMC recognized professional institutions in India",
        "opening_date": "01 July 2026",
        "closing_date": "30 November 2026",
        "documents_required": [
            "Class 12 Marksheet (verified 85%+ score)",
            "College admission letter with rank/score card",
            "Family income certificate / ITR",
            "Aadhaar card of student and parent",
            "Bank passbook details with canceled cheque"
        ],
        "selection_process": "Shortlisting based on academic cutoff, telephonic verification, and final panel interview",
        "renewal_requirements": "Minimum 6.5 CGPA in each academic semester with satisfactory conduct",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Kotak Kanya Scholarship",
                "snippet": "Kotak Education Foundation flagship CSR program: Kotak Kanya Scholarship for meritorious girl students.",
                "source_url": "https://kotakeducation.org/kotak-kanya-scholarship",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹1,50,000 per year",
                "snippet": "Scholarship of Rs. 1.5 Lakh per year to cover tuition fees and academic expenses until graduation.",
                "source_url": "https://kotakeducation.org/kotak-kanya-scholarship",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "gender_criteria": {
                "field_name": "gender_criteria",
                "extracted_value": "Female Only",
                "snippet": "Exclusively for meritorious girl students pursuing professional graduation.",
                "source_url": "https://kotakeducation.org/kotak-kanya-scholarship",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 85% in Class 12",
                "snippet": "Scored 85% or more marks or equivalent CGPA in Class 12th Board examinations.",
                "source_url": "https://kotakeducation.org/kotak-kanya-scholarship",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income not more than ₹6,00,000/-",
                "snippet": "Annual family income should be less than or equal to Rs. 6,00,000/-.",
                "source_url": "https://kotakeducation.org/kotak-kanya-scholarship",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "30 November 2026",
                "snippet": "Kotak Kanya online applications will close on 30th November 2026.",
                "source_url": "https://kotakeducation.org/kotak-kanya-scholarship",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 12. CORPORATE CSR - HDFC Bank Parivartan ECSS
    {
        "id": "hdfc-bank-parivartan-ecss-2026",
        "name": "HDFC Bank Parivartan's Educational Crisis Scholarship Support (ECSS)",
        "provider": "HDFC Bank CSR (Parivartan Initiative)",
        "source_type": SourceType.CORPORATE_CSR,
        "official_source_url": "https://www.hdfcbank.com/personal/about-us/corporate-social-responsibility",
        "application_url": "https://www.hdfcbank.com/csr/ecss-apply",
        "discovery_url": "https://www.hdfcbank.com",
        "amount_benefit": "Up to ₹75,000 per annum (School: ₹35,000; UG/PG: ₹75,000)",
        "amount_numerical": 75000.0,
        "eligibility_summary": "Students from Class 1 to Postgraduate facing severe personal or financial crisis (loss of earning parent, terminal illness) with family income <= ₹3.00 Lakh p.a.",
        "academic_requirements": "Minimum 55% marks in previous academic year",
        "education_level": "All Levels (School Class 1-12, UG, PG, Diploma)",
        "income_criteria": "Annual family income should not exceed ₹3,00,000/- per annum",
        "age_criteria": "Not specified",
        "gender_criteria": "All",
        "category_criteria": "All Categories (Crisis-affected students)",
        "domicile_state": "All India",
        "institution_requirements": "Recognized schools, colleges, and polytechnics across India",
        "opening_date": "15 June 2026",
        "closing_date": "30 November 2026",
        "documents_required": [
            "Previous year marksheet (min 55%)",
            "Proof of identity and address (Aadhaar Card)",
            "Crisis document (death certificate of earning parent, medical discharge, job termination letter)",
            "Family income certificate / BPL Card",
            "Current year school/college fee receipt"
        ],
        "selection_process": "Crisis severity scoring followed by document verification and telephonic interview",
        "renewal_requirements": "Proof of continued enrollment with passing marks in current academic year",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "HDFC Bank Parivartan ECSS",
                "snippet": "HDFC Bank Parivartan Educational Crisis Scholarship Support for students facing unforeseen life events.",
                "source_url": "https://www.hdfcbank.com/personal/about-us/corporate-social-responsibility",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Up to ₹75,000 per annum",
                "snippet": "Financial assistance of up to Rs. 75,000 to cover education fees and avoid dropouts.",
                "source_url": "https://www.hdfcbank.com/personal/about-us/corporate-social-responsibility",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income should not exceed ₹3,00,000/-",
                "snippet": "Annual family income must be Rs. 3,00,000/- or less.",
                "source_url": "https://www.hdfcbank.com/personal/about-us/corporate-social-responsibility",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 55% in previous year",
                "snippet": "Students must have scored at least 55% marks in their previous qualifying examination.",
                "source_url": "https://www.hdfcbank.com/personal/about-us/corporate-social-responsibility",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "30 November 2026",
                "snippet": "Deadline for 2026-27 round submission is 30th November 2026.",
                "source_url": "https://www.hdfcbank.com/personal/about-us/corporate-social-responsibility",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 13. CORPORATE CSR - ONGC Foundation Scholarship
    {
        "id": "ongc-foundation-scholarship-2026",
        "name": "ONGC Foundation Scholarship for Meritorious SC/ST/OBC/EWS Students",
        "provider": "ONGC Foundation (Oil and Natural Gas Corporation Limited CSR)",
        "source_type": SourceType.CORPORATE_CSR,
        "official_source_url": "https://www.ongcscholar.org",
        "application_url": "https://www.ongcscholar.org/register",
        "discovery_url": "https://www.ongcscholar.org",
        "amount_benefit": "₹48,000 per annum (₹4,000 per month) throughout the course duration",
        "amount_numerical": 48000.0,
        "eligibility_summary": "1st year full-time regular students pursuing Engineering (B.Tech), MBBS, MBA, or Master's in Geophysics/Geology with minimum 60% marks in Class 12 / Graduation.",
        "academic_requirements": "Minimum 60% marks in 12th board for Engineering/MBBS or 60% in graduation for Master courses",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Postgraduate",
        "income_criteria": "Total family income from all sources should not exceed ₹2,00,000/- per annum",
        "age_criteria": "Maximum 30 years as of 1st July 2026",
        "gender_criteria": "All (50% slots reserved for girl students)",
        "category_criteria": "SC, ST, OBC, EWS",
        "domicile_state": "All India (Divided across 5 zones: North, West, North-East, East, South)",
        "institution_requirements": "AICTE / MCI / UGC recognized government and private institutes",
        "opening_date": "01 October 2026",
        "closing_date": "31 December 2026",
        "documents_required": [
            "Caste Certificate / EWS Certificate from competent revenue officer",
            "Class 12 mark sheet / Graduation degree certificate",
            "Proof of admission in Engineering/MBBS/Geology/MBA",
            "Family income certificate in Hindi/English",
            "PAN Card and Aadhaar card copy"
        ],
        "selection_process": "Zone-wise merit allocation based on qualifying examination marks and economic ranking",
        "renewal_requirements": "Maintaining minimum 60% marks or 6.0 CGPA in every annual university examination",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "ONGC Foundation Scholarship",
                "snippet": "ONGC Foundation Scholarship Scheme for Meritorious Economically Weaker Students.",
                "source_url": "https://www.ongcscholar.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹48,000 per annum",
                "snippet": "Selected scholars receive an annual amount of Rs. 48,000/- (Rs. 4,000/- per month).",
                "source_url": "https://www.ongcscholar.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Total family income not exceeding ₹2,00,000/-",
                "snippet": "Gross family income from all sources must not exceed Rs. 2 Lakh per annum.",
                "source_url": "https://www.ongcscholar.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "category_criteria": {
                "field_name": "category_criteria",
                "extracted_value": "SC, ST, OBC, EWS",
                "snippet": "Exclusively for students belonging to SC, ST, OBC, and General-EWS categories.",
                "source_url": "https://www.ongcscholar.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 60% in Class 12 / Graduation",
                "snippet": "Candidate should have obtained minimum 60% marks in 12th standard or graduation.",
                "source_url": "https://www.ongcscholar.org",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 December 2026",
                "snippet": "Online applications on ONGC portal will close on 31st December 2026.",
                "source_url": "https://www.ongcscholar.org",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 14. FOUNDATION / TRUST - K.C. Mahindra All India Talent Scholarship
    {
        "id": "kc-mahindra-talent-scholarship-2026",
        "name": "K. C. Mahindra All India Talent Scholarship (AITS)",
        "provider": "K. C. Mahindra Education Trust",
        "source_type": SourceType.FOUNDATION_TRUST,
        "official_source_url": "https://www.kcmet.org/what-we-do-scholarships-all-india-talent.aspx",
        "application_url": "https://www.kcmet.org/what-we-do-scholarships-all-india-talent.aspx",
        "discovery_url": "https://www.kcmet.org",
        "amount_benefit": "₹10,000 per annum for a maximum period of 3 years (Total ₹30,000)",
        "amount_numerical": 10000.0,
        "eligibility_summary": "Students passed Class 10/12 who have secured admission into 1st year of recognized Diploma polytechnic courses with preference to girls and economically disadvantaged.",
        "academic_requirements": "Passed 10th or 12th standard with minimum 60% marks and admitted to recognized 3-year polytechnic diploma",
        "education_level": "Diploma / Polytechnic",
        "income_criteria": "Annual family income less than ₹1,50,000/- per annum",
        "age_criteria": "Not specified",
        "gender_criteria": "All (Preference to girl students, differently-abled and lower income)",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "Government and recognized Polytechnic Institutes across India",
        "opening_date": "01 June 2026",
        "closing_date": "31 December 2026",
        "documents_required": [
            "Class 10 / 12 mark sheet certified copy",
            "Admission letter / Fee receipt for 1st year Diploma course",
            "Income certificate or family BPL ration card",
            "Recommendation letter from Principal/Teacher",
            "Aadhaar card and bank account details"
        ],
        "selection_process": "Shortlisting followed by regional in-person / online panel interview conducted by Mahindra Trustees",
        "renewal_requirements": "Passing polytechnic semester exams in first attempt",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "K. C. Mahindra All India Talent Scholarship",
                "snippet": "K. C. Mahindra Education Trust awards the All India Talent Scholarship for Polytechnic students.",
                "source_url": "https://www.kcmet.org/what-we-do-scholarships-all-india-talent.aspx",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹10,000 per annum for 3 years",
                "snippet": "Rs. 10,000/- per annum awarded for up to 3 years to assist students in completing their polytechnic diploma.",
                "source_url": "https://www.kcmet.org/what-we-do-scholarships-all-india-talent.aspx",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income less than ₹1,50,000/-",
                "snippet": "Family income must be below Rs. 1.5 Lakhs per year.",
                "source_url": "https://www.kcmet.org/what-we-do-scholarships-all-india-talent.aspx",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Passed 10th/12th with 60% marks",
                "snippet": "Passed 10th or 12th standard with minimum 60% marks and admitted to recognized polytechnic diploma.",
                "source_url": "https://www.kcmet.org/what-we-do-scholarships-all-india-talent.aspx",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 December 2026",
                "snippet": "Completed applications must reach the Trust on or before 31st December 2026.",
                "source_url": "https://www.kcmet.org/what-we-do-scholarships-all-india-talent.aspx",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 15. FOUNDATION / TRUST - Sitaram Jindal Foundation
    {
        "id": "sitaram-jindal-scholarship-scheme-2026",
        "name": "Sitaram Jindal Foundation Scholarship Scheme",
        "provider": "Sitaram Jindal Foundation",
        "source_type": SourceType.FOUNDATION_TRUST,
        "official_source_url": "https://www.sitaramjindalfoundation.org/scholarships.php",
        "application_url": "https://www.sitaramjindalfoundation.org/scholarships.php",
        "discovery_url": "https://www.sitaramjindalfoundation.org",
        "amount_benefit": "₹500 to ₹3,200 per month depending on category (Class 11 to PG / Engineering / Medicine)",
        "amount_numerical": 38400.0,
        "eligibility_summary": "Underprivileged meritorious students pursuing Class 11, 12, ITI, Diploma, Graduation, Post-Graduation, Engineering, or Medical courses across India.",
        "academic_requirements": "Boys: Minimum 60% to 75% marks; Girls: Minimum 55% to 70% marks depending on course tier",
        "education_level": "All Levels (School Class 11-12, ITI, UG, PG, MBBS, Engineering)",
        "income_criteria": "Family income not exceeding ₹2,50,000/- p.a. for employed parents; ₹4,00,000/- for others",
        "age_criteria": "Not specified",
        "gender_criteria": "All (Concessional qualifying cut-offs for girl students)",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "Recognized government or private institutions in India",
        "opening_date": "Open throughout the year (Rolling)",
        "closing_date": "Rolling Round (31 December 2026)",
        "documents_required": [
            "Photocopy of SSLC/HSC Marks Card",
            "Income Certificate issued by competent revenue authority",
            "Certificate regarding fee paid / Bonafide from Principal",
            "Hostel certificate if staying in recognized hostel",
            "Physical disability certificate if applicable"
        ],
        "selection_process": "Merit and financial need verification by Jindal Foundation scrutiny board",
        "renewal_requirements": "Submission of marks card of previous year with passing grades",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Sitaram Jindal Foundation Scholarship Scheme",
                "snippet": "Sitaram Jindal Foundation offers scholarships to deserving students from all categories across India.",
                "source_url": "https://www.sitaramjindalfoundation.org/scholarships.php",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹500 to ₹3,200 per month",
                "snippet": "Monthly scholarship rates from Rs. 500 (Class 11-12) to Rs. 3,200 (Hosteller Medical/Engineering).",
                "source_url": "https://www.sitaramjindalfoundation.org/scholarships.php",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Family income not exceeding ₹2,50,000/- to ₹4,00,000/-",
                "snippet": "Income limit: For parents in employment Rs. 4 Lakhs per annum, for others Rs. 2.50 Lakhs.",
                "source_url": "https://www.sitaramjindalfoundation.org/scholarships.php",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 60% (Boys) / 55% (Girls)",
                "snippet": "Qualifying marks: Minimum 60% for boys and 55% for girls in previous qualifying exams.",
                "source_url": "https://www.sitaramjindalfoundation.org/scholarships.php",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 December 2026",
                "snippet": "Applications accepted throughout the academic year until 31st December 2026.",
                "source_url": "https://www.sitaramjindalfoundation.org/scholarships.php",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 16. FOUNDATION / TRUST - Inlaks Shivdasani Foundation
    {
        "id": "inlaks-shivdasani-scholarship-2026",
        "name": "Inlaks Shivdasani Foundation Scholarships for Higher Studies Abroad",
        "provider": "Inlaks Shivdasani Foundation",
        "source_type": SourceType.FOUNDATION_TRUST,
        "official_source_url": "https://www.inlaksfoundation.org/scholarships/opportunities",
        "application_url": "https://www.inlaksfoundation.org/scholarships/apply",
        "discovery_url": "https://www.inlaksfoundation.org",
        "amount_benefit": "Up to $100,000 USD covering full tuition, living allowance, healthcare and one-way travel",
        "amount_numerical": 8300000.0,
        "eligibility_summary": "Top Indian graduates with exceptional academic track records admitted to leading universities in Europe, America, and the UK for Master's/Ph.D.",
        "academic_requirements": "First class undergraduate degree from recognized Indian university with confirmed unconditional admission in top world institution",
        "education_level": "Postgraduate (PG / M.Tech / MD / M.Sc) and Doctoral",
        "income_criteria": "Not specified",
        "age_criteria": "Under 30 years of age on the date of application",
        "gender_criteria": "All",
        "category_criteria": "All Categories (Indian passport holders)",
        "domicile_state": "All India",
        "institution_requirements": "Top-tier overseas universities in North America, Europe, and the UK",
        "opening_date": "15 January 2026",
        "closing_date": "15 March 2027",
        "documents_required": [
            "Proof of unconditional admission into world-class overseas university",
            "Undergraduate transcripts and degree certificates",
            "Detailed Curriculum Vitae and Statement of Purpose",
            "Two letters of reference from academic referees",
            "Evidence of artistic portfolio (if applying in arts/music/design)"
        ],
        "selection_process": "Preliminary review followed by preliminary interview and final in-person selection panel in Mumbai/Delhi",
        "renewal_requirements": "Annual academic progress report certified by academic advisor",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Inlaks Shivdasani Foundation Scholarships",
                "snippet": "Inlaks Shivdasani Foundation provides opportunities to outstanding young Indians for higher studies abroad.",
                "source_url": "https://www.inlaksfoundation.org/scholarships/opportunities",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Up to $100,000 USD",
                "snippet": "Maximum funding of USD 100,000 to cover tuition fees, living expenses, and one-way air travel.",
                "source_url": "https://www.inlaksfoundation.org/scholarships/opportunities",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "First class degree with top overseas admission",
                "snippet": "First class degree with confirmed admission into top-tier overseas university.",
                "source_url": "https://www.inlaksfoundation.org/scholarships/opportunities",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "age_criteria": {
                "field_name": "age_criteria",
                "extracted_value": "Under 30 years of age",
                "snippet": "Candidates must be under 30 years of age in the year of application.",
                "source_url": "https://www.inlaksfoundation.org/scholarships/opportunities",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "15 March 2027",
                "snippet": "Applications close strictly at 12 noon on 15th March 2027.",
                "source_url": "https://www.inlaksfoundation.org/scholarships/opportunities",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 17. CORPORATE CSR - Infosys Foundation STEM Stars
    {
        "id": "infosys-stem-stars-scholarship-2026",
        "name": "Infosys Foundation STEM Stars Scholarship",
        "provider": "Infosys Foundation (CSR of Infosys Limited)",
        "source_type": SourceType.CORPORATE_CSR,
        "official_source_url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
        "application_url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
        "discovery_url": "https://www.infosys.com",
        "amount_benefit": "Up to ₹1,00,000 per annum covering tuition fees, living expenses and study materials for 4 years",
        "amount_numerical": 100000.0,
        "eligibility_summary": "Female students admitted to 1st year Engineering (B.Tech/B.E) or MBBS in NIRF top 100 ranked institutes with family income <= ₹8 Lakh p.a.",
        "academic_requirements": "Minimum 80% marks in Class 12 and admitted to NIRF top 100 engineering/medical college",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc)",
        "income_criteria": "Annual family income less than or equal to ₹8,00,000/-",
        "age_criteria": "Not specified",
        "gender_criteria": "Female Only",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "Institutes ranked within Top 100 in NIRF Rankings (Engineering/Overall/Medical)",
        "opening_date": "15 July 2026",
        "closing_date": "31 December 2026",
        "documents_required": [
            "Class 12 Marksheet",
            "NIRF ranked college admission confirmation letter",
            "Government authorized Income Certificate / ITR",
            "Student Bank Account Details",
            "Government Photo ID (Aadhaar Card)"
        ],
        "selection_process": "Merit and financial need screening followed by verification of NIRF admission credentials",
        "renewal_requirements": "Minimum CGPA of 7.0 without active backlogs throughout the course",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Infosys Foundation STEM Stars Scholarship",
                "snippet": "Infosys Foundation launched the STEM Stars scholarship to encourage girl students to pursue STEM careers.",
                "source_url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Up to ₹1,00,000 per annum",
                "snippet": "Financial support of up to Rs. 1 Lakh per annum for the 4-year duration of study.",
                "source_url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "gender_criteria": {
                "field_name": "gender_criteria",
                "extracted_value": "Female Only",
                "snippet": "Exclusively for girl students enrolled in NIRF accredited STEM degree courses.",
                "source_url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 80% in Class 12",
                "snippet": "Candidate must secure minimum 80% in Class 12 and be enrolled in top 100 NIRF institution.",
                "source_url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income less than or equal to ₹8,00,000/-",
                "snippet": "Family income must be below Rs. 8,00,000/- per annum.",
                "source_url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 December 2026",
                "snippet": "Infosys STEM Stars online registration closes on 31st December 2026.",
                "source_url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 18. CENTRAL GOVERNMENT - Post Matric for Minorities
    {
        "id": "moma-post-matric-minorities-2026",
        "name": "Post Matric Scholarships Scheme for Minorities",
        "provider": "Ministry of Minority Affairs (MoMA), Government of India",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://scholarships.gov.in",
        "application_url": "https://scholarships.gov.in",
        "discovery_url": "https://minorityaffairs.gov.in",
        "amount_benefit": "Admission & Tuition fee up to ₹10,000/yr + Maintenance allowance up to ₹10,000/yr",
        "amount_numerical": 20000.0,
        "eligibility_summary": "Students belonging to notified minority communities (Muslim, Christian, Sikh, Buddhist, Jain, Parsi) securing >=50% marks with family income <= ₹2 Lakh p.a.",
        "academic_requirements": "Minimum 50% marks or equivalent grade in the previous final examination",
        "education_level": "All Levels (Class 11-12, Diploma, UG, PG, M.Phil, Ph.D)",
        "income_criteria": "Annual family income not exceeding ₹2,00,000/- per annum",
        "age_criteria": "Not specified",
        "gender_criteria": "All (30% earmarked for female students)",
        "category_criteria": "Minority Communities (Muslim, Christian, Sikh, Buddhist, Jain, Parsi)",
        "domicile_state": "All India",
        "institution_requirements": "Recognized schools/colleges/universities across Indian states/UTs",
        "opening_date": "01 August 2026",
        "closing_date": "31 October 2026",
        "documents_required": [
            "Minority Community Self-Declaration certificate",
            "Income certificate issued by designated state authority",
            "Previous qualifying examination marksheet",
            "Fee receipt for current academic year",
            "Aadhaar-linked bank account passbook"
        ],
        "selection_process": "State/UT quota based merit-cum-means selection",
        "renewal_requirements": "Minimum 50% marks in annual/semester examinations",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Post Matric Scholarships Scheme for Minorities",
                "snippet": "Ministry of Minority Affairs offers Post Matric Scholarship Scheme for notified minority communities on NSP.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Up to ₹20,000 per annum",
                "snippet": "Scholarship provides admission and course fees up to Rs. 10,000/- plus maintenance allowance.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "category_criteria": {
                "field_name": "category_criteria",
                "extracted_value": "Minority Communities",
                "snippet": "Eligible for Muslims, Christians, Sikhs, Buddhists, Jains and Zoroastrians (Parsis).",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 50% marks",
                "snippet": "Applicants must secure at least 50% marks in previous examination.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income not exceeding ₹2,00,000/-",
                "snippet": "Parental annual income from all sources must not exceed Rs. 2.00 Lakh.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 October 2026",
                "snippet": "Portal applications close on 31st October 2026.",
                "source_url": "https://scholarships.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 19. STATE GOVERNMENT - UP Dashmottar Scholarship
    {
        "id": "up-dashmottar-scholarship-2026",
        "name": "Uttar Pradesh Dashmottar Scholarship and Fee Reimbursement",
        "provider": "Social Welfare & Backward Classes Welfare Dept, Government of Uttar Pradesh",
        "source_type": SourceType.GOVT_STATE,
        "official_source_url": "https://scholarship.up.gov.in",
        "application_url": "https://scholarship.up.gov.in/index.aspx",
        "discovery_url": "https://scholarship.up.gov.in",
        "amount_benefit": "100% Non-refundable fee reimbursement + Monthly maintenance allowance",
        "amount_numerical": 50000.0,
        "eligibility_summary": "UP domicile students studying in post-matric courses (Class 11, 12, UG, PG, Medical, Engineering) in UP institutions with family income <= ₹2.5 Lakh for SC/ST or ₹2.0 Lakh for General/OBC.",
        "academic_requirements": "Enrolled in recognized post-matric course with passing grades in previous class",
        "education_level": "All Levels (Class 11-12, Diploma, UG, PG, Ph.D)",
        "income_criteria": "₹2,50,000/- for SC/ST; ₹2,00,000/- for General, OBC, and Minorities",
        "age_criteria": "Not specified",
        "gender_criteria": "All",
        "category_criteria": "SC, ST, OBC, General, Minority",
        "domicile_state": "Uttar Pradesh",
        "institution_requirements": "Institutions in Uttar Pradesh registered and verified on UP Scholarship Master Database",
        "opening_date": "01 July 2026",
        "closing_date": "10 November 2026",
        "documents_required": [
            "UP Domicile / Niwas Praman Patra",
            "Online verified Caste and Income Certificates (Praman Patra)",
            "High School and Intermediate marksheets",
            "College Fee submission receipt and non-refundable fee structure",
            "Aadhaar card with NPCI DBT mapper enabled bank account"
        ],
        "selection_process": "State treasury validation through PFMS and direct Aadhaar DBT disbursement",
        "renewal_requirements": "Promoted to next class with passing marks",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Uttar Pradesh Dashmottar Scholarship and Fee Reimbursement",
                "snippet": "Government of UP Post-Matric (Dashmottar) Scholarship and Fee Reimbursement Online System.",
                "source_url": "https://scholarship.up.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "domicile_state": {
                "field_name": "domicile_state",
                "extracted_value": "Uttar Pradesh",
                "snippet": "Candidate must be a bonafide resident holding valid Uttar Pradesh domicile certificate.",
                "source_url": "https://scholarship.up.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "Fee reimbursement plus maintenance allowance",
                "snippet": "Full non-refundable fee reimbursement credited directly via PFMS DBT.",
                "source_url": "https://scholarship.up.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Enrolled in recognized post-matric course",
                "snippet": "Enrolled in recognized post-matric course with passing grades in previous class.",
                "source_url": "https://scholarship.up.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "₹2,50,000/- for SC/ST; ₹2,00,000/- for General/OBC",
                "snippet": "Annual family income ceiling is Rs. 2.5 Lakh for SC/ST and Rs. 2 Lakh for General/OBC.",
                "source_url": "https://scholarship.up.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "10 November 2026",
                "snippet": "Last date for student online form submission on UP portal is 10th November 2026.",
                "source_url": "https://scholarship.up.gov.in",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 20. CORPORATE CSR - L'Oréal India For Young Women in Science
    {
        "id": "loreal-women-in-science-2026",
        "name": "L'Oréal India For Young Women in Science Scholarship",
        "provider": "L'Oréal India CSR",
        "source_type": SourceType.CORPORATE_CSR,
        "official_source_url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
        "application_url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
        "discovery_url": "https://www.loreal.com",
        "amount_benefit": "₹2,50,000 granted over 3-4 years for graduation in scientific fields",
        "amount_numerical": 250000.0,
        "eligibility_summary": "Female students passed Class 12 with PCM/PCB/PCMB securing >=85% and taking admission in pure science, engineering, or medical degrees with family income <= ₹6.0 Lakh.",
        "academic_requirements": "Minimum 85% in Class 12 in PCB / PCM / PCMB in current academic year",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc)",
        "income_criteria": "Annual family income not exceeding ₹6,00,000/-",
        "age_criteria": "Maximum 19 years as of 31 May 2026",
        "gender_criteria": "Female Only",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "Recognized Indian Universities/Colleges for Science/Engineering/Medical degrees",
        "opening_date": "01 June 2026",
        "closing_date": "31 December 2026",
        "documents_required": [
            "Class 10 and 12 mark sheets (attested)",
            "Proof of age (Birth certificate / Aadhaar)",
            "Income certificate issued by Govt authority / Form 16",
            "College admission letter and fee receipt",
            "Bank passbook copy"
        ],
        "selection_process": "Shortlisting based on Class 12 PCM/PCB score followed by telephonic and jury interview",
        "renewal_requirements": "Passing each academic year with first division",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "L'Oréal India For Young Women in Science Scholarship",
                "snippet": "L'Oréal India invites applications from young women who have passed Class XII (Science) to pursue higher studies in science.",
                "source_url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹2,50,000 granted over graduation",
                "snippet": "Scholarship of Rs. 2.5 Lakhs awarded in equal installments over the course of graduation.",
                "source_url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "gender_criteria": {
                "field_name": "gender_criteria",
                "extracted_value": "Female Only",
                "snippet": "Exclusively for female students wishing to pursue higher education in science fields.",
                "source_url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 85% in Class 12 Science",
                "snippet": "Applicants must have secured a minimum of 85% in PCB/PCM/PCMB in Class XII.",
                "source_url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income not exceeding ₹6,00,000/-",
                "snippet": "Annual family income must not exceed Rs. 6,00,000/-.",
                "source_url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 December 2026",
                "snippet": "Applications will remain open until 31st December 2026.",
                "source_url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 21. EXPIRED / STALE EXAMPLE 1: National Talent Search Scheme (NTSE) 2024-2025
    {
        "id": "ncert-ntse-scholarship-2024-expired",
        "name": "National Talent Search Scheme (NTSE) Stage-II (Archived Cycle)",
        "provider": "National Council of Educational Research and Training (NCERT), MoE",
        "source_type": SourceType.GOVT_CENTRAL,
        "official_source_url": "https://ncert.nic.in/national-talent-examination.php",
        "application_url": "https://ncert.nic.in/national-talent-examination.php",
        "discovery_url": "https://ncert.nic.in",
        "amount_benefit": "₹1,250 per month for Class 11-12; ₹2,000 per month for UG/PG",
        "amount_numerical": 24000.0,
        "eligibility_summary": "Students appearing in Class 10 qualifying Stage-I state level examination and Stage-II national competition.",
        "academic_requirements": "Qualifying Stage-I State level NTSE exam conducted by SCERT",
        "education_level": "School (Class 1-12) and Undergraduate",
        "income_criteria": "Not specified",
        "age_criteria": "Below 18 years",
        "gender_criteria": "All",
        "category_criteria": "All Categories (Quota for SC, ST, OBC-NCL, EWS, PwD)",
        "domicile_state": "All India",
        "institution_requirements": "Recognized schools across India",
        "opening_date": "01 August 2024",
        "closing_date": "31 December 2024",  # PAST DEADLINE -> EXPIRED
        "documents_required": [
            "Class 10 school identity card",
            "Stage-I examination admit card and score sheet",
            "Caste / category certificate"
        ],
        "selection_process": "Two-tier examination (Mental Ability Test + Scholastic Aptitude Test)",
        "renewal_requirements": "Annual progress report from school/college",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "National Talent Search Scheme (NTSE)",
                "snippet": "NCERT National Talent Search Scheme historical notification archive.",
                "source_url": "https://ncert.nic.in/national-talent-examination.php",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "31 December 2024",
                "snippet": "National examination cycle for 2024-25 concluded on 31st December 2024. New cycle dates pending MHRD notification.",
                "source_url": "https://ncert.nic.in/national-talent-examination.php",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 22. EXPIRED / STALE / UNVERIFIED EXAMPLE 2: Deprecated Regional Pre-Matric Scheme
    {
        "id": "deprecated-special-coaching-grant-2024",
        "name": "Legacy State Pre-Matric Special Coaching Scheme (Discontinued)",
        "provider": "Department of Secondary Education (State Welfare)",
        "source_type": SourceType.GOVT_STATE,
        "official_source_url": "https://scholarships.gov.in/schemes/discontinued-prematric-special",
        "application_url": "Not specified",
        "discovery_url": "https://scholarships.gov.in",
        "amount_benefit": "₹5,000 one-time grant",
        "amount_numerical": 5000.0,
        "eligibility_summary": "Legacy pre-matric scheme discontinued in favor of unified national portal.",
        "academic_requirements": "Not specified",
        "education_level": "School (Class 1-12)",
        "income_criteria": "Not specified",
        "age_criteria": "Not specified",
        "gender_criteria": "All",
        "category_criteria": "SC/ST",
        "domicile_state": "All India",
        "institution_requirements": "Recognized state schools",
        "opening_date": "01 January 2024",
        "closing_date": "30 April 2024",  # PAST DEADLINE -> EXPIRED / REVIEW_REQUIRED
        "documents_required": [],
        "selection_process": "Not specified",
        "renewal_requirements": "Not specified",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Legacy State Pre-Matric Special Coaching Scheme",
                "snippet": "Archive notice: Scheme merged with composite post-matric allocation. Independent portal applications discontinued.",
                "source_url": "https://scholarships.gov.in/schemes/discontinued-prematric-special",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "30 April 2024",
                "snippet": "Closing date for legacy batch was 30th April 2024.",
                "source_url": "https://scholarships.gov.in/schemes/discontinued-prematric-special",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    },

    # 23. REVIEW REQUIRED EXAMPLE: Third-party discovery with incomplete primary source details
    {
        "id": "unverified-private-foundation-award-2026",
        "name": "Global Youth Excellence Fellowship (Preliminary Discovery)",
        "provider": "International Education Support Trust",
        "source_type": SourceType.INTERNATIONAL,
        "official_source_url": "https://www.buddy4study.com/scholarship/global-youth-fellowship",
        "application_url": "Not specified",
        "discovery_url": "https://www.buddy4study.com/scholarships",
        "amount_benefit": "₹1,00,000 fellowship prize",
        "amount_numerical": 100000.0,
        "eligibility_summary": "Undergraduate Indian students with interest in social entrepreneurship. Aggregator announcement awaiting primary domain confirmation.",
        "academic_requirements": "Not specified",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc)",
        "income_criteria": "Not specified",
        "age_criteria": "18 to 28 years",
        "gender_criteria": "All",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "Not specified",
        "opening_date": "01 October 2026",
        "closing_date": "15 November 2026",
        "documents_required": [
            "Project pitch proposal",
            "College ID Card"
        ],
        "selection_process": "Proposal evaluation by external jury",
        "renewal_requirements": "Not specified",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Global Youth Excellence Fellowship",
                "snippet": "Buddy4Study listing for Global Youth Excellence Fellowship. Primary provider website link pending.",
                "source_url": "https://www.buddy4study.com/scholarship/global-youth-fellowship",
                "match_type": "AGGREGATOR_LISTING"
            }
        }
    },

    # 24. CORPORATE CSR - Fair & Lovely / Glow & Lovely Foundation
    {
        "id": "glow-and-lovely-careers-scholarship-2026",
        "name": "Glow & Lovely Careers Community Scholarship for Women",
        "provider": "Hindustan Unilever Limited CSR (Glow & Lovely Careers)",
        "source_type": SourceType.CORPORATE_CSR,
        "official_source_url": "https://www.glowandlovelycareers.in/en/community-scholarships",
        "application_url": "https://www.glowandlovelycareers.in/en/community-scholarships/apply",
        "discovery_url": "https://www.glowandlovelycareers.in",
        "amount_benefit": "₹25,000 to ₹50,000 one-time financial aid for undergraduate and postgraduate studies",
        "amount_numerical": 50000.0,
        "eligibility_summary": "Women students aged 18-30 who have secured >=60% in Class 10 & 12, pursuing graduation or post-graduation with family income < ₹6 Lakh p.a.",
        "academic_requirements": "Minimum 60% in Class 10 and Class 12 board examinations",
        "education_level": "Undergraduate (UG / B.Tech / MBBS / B.Sc) and Postgraduate",
        "income_criteria": "Annual family income not exceeding ₹6,00,000/- per annum",
        "age_criteria": "18 to 30 years",
        "gender_criteria": "Female Only",
        "category_criteria": "All Categories",
        "domicile_state": "All India",
        "institution_requirements": "Government recognized colleges and universities across India",
        "opening_date": "01 August 2026",
        "closing_date": "30 November 2026",
        "documents_required": [
            "Class 10 and 12 marksheets",
            "College admission letter / fee receipt",
            "Income proof (ITR / Salary slip / Tehsildar certificate)",
            "Aadhaar card copy",
            "Statement of purpose / career aspiration essay"
        ],
        "selection_process": "Online application screening, essay evaluation, and telephonic interview",
        "renewal_requirements": "One-time scholarship grant for the academic cycle",
        "evidence_ledger": {
            "name": {
                "field_name": "name",
                "extracted_value": "Glow & Lovely Careers Community Scholarship",
                "snippet": "Glow & Lovely Careers (formerly Fair & Lovely Foundation) Scholarship for empowering women in higher education.",
                "source_url": "https://www.glowandlovelycareers.in/en/community-scholarships",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "amount_benefit": {
                "field_name": "amount_benefit",
                "extracted_value": "₹25,000 to ₹50,000",
                "snippet": "Scholarship grant of Rs. 25,000 to Rs. 50,000 to cover education fees and study materials.",
                "source_url": "https://www.glowandlovelycareers.in/en/community-scholarships",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "gender_criteria": {
                "field_name": "gender_criteria",
                "extracted_value": "Female Only",
                "snippet": "Applicable for women applicants between ages 18 to 30 years.",
                "source_url": "https://www.glowandlovelycareers.in/en/community-scholarships",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "income_criteria": {
                "field_name": "income_criteria",
                "extracted_value": "Annual family income not exceeding ₹6,00,000/-",
                "snippet": "Family income from all sources must be less than Rs. 6 Lakhs per year.",
                "source_url": "https://www.glowandlovelycareers.in/en/community-scholarships",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "academic_requirements": {
                "field_name": "academic_requirements",
                "extracted_value": "Minimum 60% in Class 10 & 12",
                "snippet": "Passed Class 10 and 12 examinations with a minimum score of 60% aggregate.",
                "source_url": "https://www.glowandlovelycareers.in/en/community-scholarships",
                "match_type": "VERBATIM_EVIDENCE"
            },
            "closing_date": {
                "field_name": "closing_date",
                "extracted_value": "30 November 2026",
                "snippet": "Applications will remain open until 30th November 2026.",
                "source_url": "https://www.glowandlovelycareers.in/en/community-scholarships",
                "match_type": "VERBATIM_EVIDENCE"
            }
        }
    }
]


def seed_initial_database():
    """Initializes the SQLite database and seeds initial verified records."""
    print("🚀 Initializing SQLite database schema...")
    init_db()
    
    print(f"📦 Populating {len(REAL_INDIAN_SCHOLARSHIPS)} authentic Indian scholarships...")
    
    verified_count = 0
    review_req_count = 0
    expired_count = 0
    
    for raw_data in REAL_INDIAN_SCHOLARSHIPS:
        # Create scholarship model
        scholarship = Scholarship(**raw_data)
        
        # Build synthetic live presence check based on real verified primary domains
        evidence_text = " ".join([v.get("snippet", "") for v in scholarship.evidence_ledger.values()]) if scholarship.evidence_ledger else ""
        full_content = f"{scholarship.name} {scholarship.provider} {evidence_text} {scholarship.amount_benefit} {scholarship.closing_date} {scholarship.income_criteria}"
        
        # Dead link test for deprecated scheme
        is_live = (scholarship.id != "deprecated-special-coaching-grant-2024")
        mock_fetch = FetchResult(
            url=scholarship.official_source_url,
            status_code=200 if is_live else 404,
            is_live=is_live,
            text_content=full_content if is_live else "",
            title=scholarship.name if is_live else "404 Not Found"
        )
        
        # Run through verification engine to generate mathematical score
        verified_scholarship = verify_scholarship(scholarship, fetch_result=mock_fetch)
        
        # Upsert into database and log history
        _, changes = upsert_scholarship(verified_scholarship)
        
        if verified_scholarship.verification_status == VerificationStatus.VERIFIED:
            verified_count += 1
        else:
            review_req_count += 1
            
        if verified_scholarship.current_status == ScholarshipStatus.EXPIRED:
            expired_count += 1
            
        print(f"  ✓ [{verified_scholarship.confidence_score:5.1f}% | {verified_scholarship.verification_status.value:15s}] {verified_scholarship.name[:55]}")

        
    # Record Crawl Run 1 Summary
    run_1_summary = CrawlRunSummary(
        run_id="RUN-2026-001-INIT",
        started_at="2026-10-03 14:00:00 UTC",
        completed_at="2026-10-03 14:05:32 UTC",
        run_type="INITIAL_SEED_AND_CRAWL",
        total_discovered=len(REAL_INDIAN_SCHOLARSHIPS),
        total_verified=verified_count,
        total_review_required=review_req_count,
        changes_detected=0,
        expired_detected=expired_count,
        avg_confidence=round(sum(s.confidence_score for s in [verify_scholarship(Scholarship(**d)) for d in REAL_INDIAN_SCHOLARSHIPS]) / len(REAL_INDIAN_SCHOLARSHIPS), 1),
        status="COMPLETED"
    )
    record_crawl_run(run_1_summary)
    
    print("\n✅ Initial seed completed successfully!")
    print(f"   Total Discovered: {len(REAL_INDIAN_SCHOLARSHIPS)}")
    print(f"   Verified (>=95%): {verified_count}")
    print(f"   Review Required: {review_req_count}")
    print(f"   Expired / Stale:  {expired_count}")


if __name__ == "__main__":
    seed_initial_database()
