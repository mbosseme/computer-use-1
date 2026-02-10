
import difflib

workflow_systems = [
    {"name": "Advocate Health", "spend": 9590494288.50},
    {"name": "AdventHealth (AHS Florida)", "spend": 8410965370.58},
    {"name": "Dignity Health", "spend": 4253248925.80},
    {"name": "Catholic Health Initiatives", "spend": 3940107681.69},
    {"name": "Northwell Health", "spend": 2899699163.20},
    {"name": "EM_OSF", "spend": 2717487644.81},
    {"name": "EM_UHS", "spend": 2512707041.39},
    {"name": "EM_UCSD", "spend": 2097441503.22},
    {"name": "EM_Fletcher", "spend": 2022383732.60},
    {"name": "Northwestern Memorial HealthCare", "spend": 1672597085.64},
    {"name": "EM_CCH", "spend": 1582305439.37},
    {"name": "Henry Ford Health System", "spend": 1446874094.77},
    {"name": "Beth Israel Lahey Health", "spend": 1352710797.32},
    {"name": "EM_Renown", "spend": 1292339501.28},
    {"name": "Adventist Health (California HQ)", "spend": 1266062574.44},
    {"name": "EM_ULHealth", "spend": 1231682480.26},
    {"name": "EM_UCI", "spend": 1188283324.61},
    {"name": "EM_HonorHealth", "spend": 1056258570.61},
    {"name": "THE METHODIST HOSPITAL RESEARCH INSTITUTE", "spend": 1052239261.55},
    {"name": "Atrium Health", "spend": 982560560.06}
]

tsa_systems = [
    "ACURITY FKA GNYHA SERVICES, INC.",
    "ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE",
    "ALLSPIRE HEALTH GPO",
    "UPMC HEALTH SYSTEM",
    "PREMIER TEST 300",
    "MCLAREN HEALTH CARE",
    "ADVENTHEALTH",
    "WEST VIRGINIA UNITED HEALTH SYSTEM",
    "TEXAS HEALTH RESOURCES",
    "PRISMA HEALTH",
    "MEMBER 24 - TEST",
    "YANKEE ALLIANCE INC",
    "OREGON HEALTH SCIENCES UNIVERSITY",
    "UNIVERSITY OF VIRGINIA HEALTH SYSTEM",
    "UNIVERSITY HEALTH SYSTEM",
    "CONDUCTIV",
    "HONORHEALTH",
    "FAIRVIEW HEALTH SERVICES",
    "COST TECHNOLOGY PARENT 2",
    "BANNER HEALTH",
    "BAPTIST HEALTHCARE SYSTEM",
    "CHILDREN'S HOSPITAL CORPORATION",
    "ALLIANT HOLDING, LLC",
    "UNIVERSITY OF CALIFORNIA - IRVINE",
    "ST LUKE'S UNIVERSITY HEALTH NETWORK",
    "SOUTH BROWARD HOSPITAL DISTRICT",
    "UHS OF DELAWARE, INC.",
    "PEACEHEALTH",
    "ECU HEALTH",
    "HEALTH FIRST SHARED SERVICES, INC",
    "COST TECHNOLOGY PARENT 1",
    "BAYSTATE HEALTH INC.",
    "MTWY HEALTH",
    "OSF HEALTHCARE SYSTEM",
    "HARRIS COUNTY HOSPITAL DISTRICT",
    "UNIVERSITY HOSPITALS HEALTH SYSTEM, INC.",
    "MOUNT SINAI MEDICAL CENTER OF FLORIDA, INC.",
    "PRESBYTERIAN HEALTHCARE SERVICES",
    "RECRUITMENT TEST FACILITY 1",
    "UNITYPOINT HEALTH",
    "ADVENTIST HEALTH",
    "VCU HEALTH SYSTEM AUTHORITY",
    "HEALTHPARTNERS, INC.",
    "SUMMA HEALTH",
    "AVERA HEALTH",
    "RENOWN HEALTH",
    "LUMINIS HEALTH",
    "SAINT FRANCIS HOSPITAL, INC.",
    "LIFEBRIDGE HEALTH",
    "COMMUNITY FOUNDATION OF NORTHWEST INDIANA, INC.",
    "CARILION CLINIC",
    "ROCHESTER REGIONAL HEALTH",
    "BALLAD HEALTH",
    "OPTUM, INC.",
    "MEDICAL CENTER HOSPITAL",
    "MHS PURCHASING, LLC",
    "METHODIST HEALTH SYSTEM",
    "BEEBE HEALTHCARE",
    "SHRINERS INTERNATIONAL",
    "NORTON HEALTHCARE, INC.",
    "BAPTIST HEALTH SOUTH FLORIDA",
    "WAKEMED",
    "MEMBER 2 - TEST",
    "COMMUNITY MEDICAL CENTERS",
    "BAPTIST HEALTH SYSTEM",
    "TJUH SYSTEM",
    "CARLE HOSPITAL",
    "HOSPITAL SHARED SERVICES ASSOCIATION",
    "BOARD OF COMMISSIONERS OF PUBLIC HOSPITAL DISTRICT NO. 1 OF KING COUNTY",
    "UNIVERSITY OF TENNESSEE MEDICAL CENTER",
    "CAPE FEAR VALLEY HEALTH SYSTEM",
    "METHODIST LE BONHEUR HEALTHCARE- CORPORATE ADMINISTRATION",
    "ST. JOSEPH'S - CANDLER HEALTH SYSTEM, INC.",
    "TIDALHEALTH INC",
    "LEXINGTON MEDICAL CENTER",
    "SAINT PETER'S HEALTHCARE SYSTEM",
    "MARSHALL HEALTH NETWORK, INC.",
    "MIDLAND MEMORIAL HOSPITAL",
    "RIVERSIDE HEALTH SYSTEM",
    "SALEM HEALTH",
    "FIRSTHEALTH OF THE CAROLINAS",
    "MOSES H. CONE MEMORIAL HOSPITAL",
    "TERREBONNE GENERAL HEALTH SYSTEM",
    "NEMOURS FOUNDATION",
    "MONUMENT HEALTH RAPID CITY HOSPITAL, INC.",
    "MERCY HEALTH CORPORATION",
    "WELLLINK GROUP PURCHASING - CHAMPS HEALTHCARE",
    "PREMIER HEALTH SYSTEM DEMO",
    "EISENHOWER MEDICAL CENTER",
    "GENERAL HEALTH SYSTEM",
    "BAYHEALTH",
    "THE METHODIST HOSPITALS, INC. - NORTHLAKE CAMPUS",
    "GREATER BALTIMORE MEDICAL CENTER",
    "CATAWBA VALLEY MEDICAL CENTER",
    "HOLY NAME MEDICAL CENTER",
    "HEALTH ENTERPRISES COOPERATIVE",
    "PRAIRIE HEALTH VENTURES",
    "ST. ELIZABETH MEDICAL CENTER, INC.",
    "MERCY HEALTH SERVICES, INC.",
    "ADVENTIST HEALTHCARE, INC.",
    "ANMED HEALTH",
    "CAPSTONE HEALTH ALLIANCE",
    "COMMONWEALTH HEALTH CORPORATION",
    "CONWAY MEDICAL CENTER",
    "NORTHERN ARIZONA HEALTHCARE",
    "FREDERICK HEALTH HOSPITAL",
    "HOWARD UNIVERSITY HOSPITAL CORPORATION",
    "NORTH OAKS HEALTH SYSTEM",
    "TANNER MEDICAL CENTER, INC.",
    "EPHRAIM MCDOWELL HEALTH",
    "CONSOLIDATED SUPPLY CHAIN SERVICES, LLC",
    "CHESAPEAKE REGIONAL MEDICAL CENTER",
    "SINAI HEALTH SYSTEM",
    "KUAKINI HEALTH SYSTEM",
    "T. J. SAMSON COMMUNITY HOSPITAL, INC.",
    "SOUTHEAST GEORGIA HEALTH SYSTEM",
    "THE MOSES H CONE MEMORIAL HOSPITAL - PARENT",
    "ABINGTON MEMORIAL HOSPITAL",
    "IPC GROUP PURCHASING",
    "UNIVERSITY MEDICAL CENTER",
    "PANDION OPTIMIZATION ALLIANCE- CAPSTONE",
    "JEFFERSON REGIONAL MEDICAL CENTER",
    "FLAGLER HOSPITAL, INC.",
    "FIRELANDS HEALTH",
    "SOUTH CENTRAL REGIONAL MEDICAL CENTER",
    "CARTERET COUNTY GENERAL HOSPITAL",
    "KING'S DAUGHTERS MEDICAL CENTER",
    "WHITE RIVER MEDICAL CENTER",
    "MCBRIDE CLINIC ORTHOPEDIC HOSPITAL",
    "WESLEY LONG COMMUNITY HOSPITAL",
    "JEFFERSON TORRESDALE HOSPITAL",
    "IREDELL MEMORIAL HOSPITAL, INC.",
    "MURRAY-CALLOWAY COUNTY HOSPITAL",
    "INNOVATIX, LLC NATIONAL HEADQUARTERS",
    "PIPELINE HEALTH SYSTEM HOLDINGS, LLC",
    "SOUTHEASTERN REGIONAL MEDICAL CENTER",
    "H. LEE MOFFITT HOSPITAL CENTER",
    "COMPREHENSIVE PURCHASING ALLIANCE, LLC",
    "KENNEDY MEMORIAL HOSPITALS UNIV MED CTR",
    "MCHS SW - OFFSITE DISTRIBUTION CENTER",
    "DAVIS MEDICAL CENTER",
    "ANNIE PENN MEMORIAL HOSPITAL",
    "WOMAN'S HOSPITAL FOUNDATION",
    "NORTH ARKANSAS REGIONAL MEDICAL CENTER",
    "CENTRAL MAINE HEALTH CARE",
    "MIS INFORMATION SYSTEM",
    "STEVEN D. BELL HEART AND VASCULAR CENTER",
    "PREMIER, INC.",
    "ALLIED HEALTH SOLUTIONS"
]

def clean_name(name):
    """Normalize name for easier matching."""
    n = name.upper()
    n = n.replace("EM_", "").replace(" (AHS FLORIDA)", "").replace(" (CALIFORNIA HQ)", "")
    n = n.replace(" HEALTH SYSTEM", "").replace(" HEALTHCARE", "").replace(" HEALTH", "")
    n = n.replace(" INC.", "").replace(", INC", "").replace(" LLC", "")
    return n.strip()

print(f"| Rank | Workflow System Name | Invoice Total (2025) | Proposed TSA Match | Score |")
print(f"|---|---|---|---|---|")

rank = 1
for wf_sys in workflow_systems:
    original_name = wf_sys["name"]
    wf_name_clean = clean_name(original_name)
    
    # Try fuzzy match on cleaned names first
    best_match = None
    best_score = 0
    
    # Manual overrides for tricky ones
    overrides = {
        "EM_OSF": "OSF HEALTHCARE SYSTEM",
        "EM_UHS": "UHS OF DELAWARE, INC.", # Or University Health System? UHS usually Universal Health Services -> UHS of Delaware
        "EM_UCI": "UNIVERSITY OF CALIFORNIA - IRVINE",
        "EM_UCSD": "UNIVERSITY OF CALIFORNIA SAN DIEGO", # Not in top 100? Let's see. 
        # UCSD is surprisingly not in the top 100 TSA list or named differently?
        # Maybe "University of California"? 
        # I only grabbed top 100. If UCSD is lower in TSA, we miss it.
        # But given $2B in Workflow, it should be huge in TSA unless mapped elsewhere or missing.
        "EM_CCH": "COOK COUNTY HEALTH", # Likely guess
        "EM_Fletcher": "Fletcher Allen? Not in list",
        "EM_Renown": "RENOWN HEALTH",
        "EM_HonorHealth": "HONORHEALTH",
         "EM_ULHealth": "UofL Health?"
    }
    
    candidate_match = overrides.get(original_name)
    
    if not candidate_match:
        # Fuzzy search
        matches = difflib.get_close_matches(original_name.upper(), tsa_systems, n=1, cutoff=0.4)
        if matches:
            candidate_match = matches[0]
            best_score = difflib.SequenceMatcher(None, original_name.upper(), candidate_match).ratio()
        
        # If strict fail, try cleaning
        if not candidate_match:
             # Logic to search tsa list with cleaned names
             for tsa_orig in tsa_systems:
                 tsa_clean = clean_name(tsa_orig)
                 score = difflib.SequenceMatcher(None, wf_name_clean, tsa_clean).ratio()
                 if score > best_score:
                     best_score = score
                     best_match = tsa_orig
             
             if best_score > 0.6: # Threshold
                 candidate_match = best_match

    formatted_spend = f"${wf_sys['spend']:,.0f}"
    
    print(f"| {rank} | {original_name} | {formatted_spend} | {candidate_match if candidate_match else 'NO MATCH GUIDED'} | {best_score:.2f} |")
    rank += 1
