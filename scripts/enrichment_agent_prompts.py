#!/usr/bin/env python3
"""
3-Agent Enrichment Prompt Templates
Consolidates 6 agents into 3 for faster execution
"""

def get_location_economic_prompt(lead_id, full_name, address, coords):
    """
    AGENT 1: Location & Economic Profile
    Combines: Property + Budget agents
    """
    lat, lon = coords if coords else (None, None)

    prompt = f"""LEAD: {full_name}, {address}
COORDS: {lat}, {lon}

TASK: Location & Economic Profile Agent

Use WebSearch to find:

**PROPERTY ATTRIBUTES:**
1. Property details ({address})
   - Square footage, beds/baths
   - Lot size (acres or sqft)
   - Year built, property type
   - Sale history, owner if available
2. Neighborhood characteristics
   - Area name/subdivision
   - Typical lot sizes and home styles
   - Any notable features (greenbelt, HOA, etc.)

**ECONOMIC INDICATORS:**
3. Home values in the area
   - Median home price
   - Recent sale prices
   - Price range
4. Household income data
   - Median household income
   - Economic tier indicators
5. Budget tier classification
   - Budget-conscious / Mid-range / Premium / Affluent

Search queries to try:
- "{address}"
- "{address.split(',')[0] if ',' in address else address} property records"
- "{address.split(',')[-2].strip() if ',' in address else ''} home values median price"
- "{address.split(',')[-2].strip() if ',' in address else ''} median household income"

Return findings in this format:
**Property**: [sqft, beds/baths, lot size, year built, owner/features]
**Neighborhood**: [area name, characteristics, typical values]
**Home Values**: [median price, range]
**Income Level**: [median HH income, economic tier]
**Budget Tier**: [classification with reasoning]"""

    return prompt

def get_person_communication_prompt(lead_id, full_name, address, channel):
    """
    AGENT 2: Person & Communication Profile
    Combines: Decision-Maker + Digital agents
    """
    prompt = f"""LEAD: {full_name}, {address}
CHANNEL: {channel}

TASK: Person & Communication Profile Agent

Use WebSearch to find:

**DECISION-MAKER CONTEXT:**
1. Person information
   - Full name, age if available
   - Professional background (LinkedIn, business profiles)
   - Household composition if available
2. Public records
   - Property ownership verification
   - Any business affiliations

**DIGITAL ENGAGEMENT:**
3. Online presence
   - Reviews on Yelp, Google, Angi, etc.
   - Social media profiles (LinkedIn, Facebook if public)
   - Digital footprint assessment
4. Communication preferences
   - Review activity level
   - Professional vs casual tone indicators
   - Channel engagement patterns

Search queries:
- "{full_name} {address.split(',')[-2].strip() if ',' in address else ''}"
- "{full_name} {address}"
- "{full_name} reviews"
- "{full_name} LinkedIn"

Return findings:
**Decision-Maker**: [name, age/background, household info if found]
**Professional**: [LinkedIn/business context if found]
**Digital Presence**: [reviews, social media, engagement level]
**Communication Style**: [High-engagement / Moderate / Privacy-conscious / Minimal]
**Channel Rec**: [recommended tone and approach]"""

    return prompt

def get_project_context_prompt(lead_id, full_name, address, coords, comment):
    """
    AGENT 3: Project Context & Constraints
    Combines: Intent + Timing agents
    """
    lat, lon = coords if coords else (None, None)
    location = address.split(',')[-2].strip() if ',' in address else address

    prompt = f"""LEAD: {full_name}, {location}
COMMENT: {comment if comment else "No comment provided"}
COORDS: {lat}, {lon}

TASK: Project Context & Constraints Agent

Use WebSearch to find:

**WEATHER & STORM TRIGGERS:**
1. Recent weather events (past 12 months)
   - Major storms, hail, wind damage
   - Flooding, tornadoes, severe weather
   - Storm damage reports or declarations
2. Current weather patterns
   - Seasonal context
   - Recent unusual weather

**REGULATORY REQUIREMENTS:**
3. Local fence regulations
   - HOA requirements in the area
   - City/county fence height limits
   - Permit requirements
   - Setback rules if applicable

**PROJECT DRIVERS & TIMING:**
4. Urgency signals from context
   - Storm damage correlation
   - Neighbor disputes or issues
   - HOA enforcement actions
   - Property sale/transaction signals
5. Timeline indicators
   - Seasonal considerations
   - Regulatory deadlines

Search queries:
- "{location} storm damage 2025 2026"
- "{location} fence regulations HOA"
- "{location} fence permits requirements"
- "{location} severe weather reports"

Return findings:
**Weather Triggers**: [recent storms, damage reports, severity]
**Regulations**: [HOA requirements, permits, height limits]
**Project Drivers**: [what's likely driving this project]
**Timing Signals**: [urgency indicators, timeline constraints]
**Recommended Approach**: [how to frame messaging based on drivers]"""

    return prompt

# Template for MINIMAL enrichment (Location only)
def get_minimal_enrichment_prompt(lead_id, full_name, address, coords):
    """
    MINIMAL: Just Location & Economic (for score 0-2 leads)
    """
    return get_location_economic_prompt(lead_id, full_name, address, coords)

# Template for REDUCED enrichment (Location + Project)
def get_reduced_enrichment_prompts(lead_id, full_name, address, coords, comment):
    """
    REDUCED: Location & Project, skip Communication (for score 3-5 leads)
    """
    return [
        get_location_economic_prompt(lead_id, full_name, address, coords),
        get_project_context_prompt(lead_id, full_name, address, coords, comment),
    ]

# Template for FULL enrichment (All 3 agents)
def get_full_enrichment_prompts(lead_id, full_name, address, coords, channel, comment):
    """
    FULL: All 3 agents (for score 6-9 leads)
    """
    return [
        get_location_economic_prompt(lead_id, full_name, address, coords),
        get_person_communication_prompt(lead_id, full_name, address, channel),
        get_project_context_prompt(lead_id, full_name, address, coords, comment),
    ]

# Example usage
if __name__ == "__main__":
    # Test prompt generation
    test_lead = {
        "id": 768088,
        "name": "Susan LYNN",
        "address": "2117 Maconda Ln, Houston, TX 77027",
        "coords": (29.74593470, -95.43733200),
        "channel": "Angi Ads",
        "comment": "I need my wooden gates repaired on a 68 ft fence."
    }

    print("=" * 70)
    print("FULL ENRICHMENT PROMPTS (3 agents)")
    print("=" * 70)

    prompts = get_full_enrichment_prompts(
        test_lead["id"],
        test_lead["name"],
        test_lead["address"],
        test_lead["coords"],
        test_lead["channel"],
        test_lead["comment"]
    )

    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'='*70}")
        print(f"AGENT {i}")
        print('='*70)
        print(prompt)
