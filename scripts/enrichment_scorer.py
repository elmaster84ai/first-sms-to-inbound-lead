#!/usr/bin/env python3
"""
Enrichment Decision Tree Scorer
Determines enrichment level (MINIMAL/REDUCED/FULL) based on lead characteristics
"""

import json
import re

# Enrichment levels
MINIMAL = "MINIMAL"    # Weather + Location only (score 0-2)
REDUCED = "REDUCED"    # Location + Project, skip Digital (score 3-5)
FULL = "FULL"          # All 3 agents (score 6-9)

def calculate_comment_score(comment):
    """
    Score based on comment length
    0 chars = 0 points (awareness)
    1-50 chars = 1 point (basic awareness)
    51-150 chars = 2 points (consideration)
    150+ chars = 3 points (decision)
    """
    if not comment or comment.strip() == "":
        return 0

    # Clean comment
    clean_comment = comment.strip()

    # Filter out common no-comment placeholders
    no_comment_phrases = [
        "customer did not provide additional comments",
        "please contact the customer",
        "info verified",
        "message:",
    ]

    is_placeholder = any(phrase in clean_comment.lower() for phrase in no_comment_phrases)

    if is_placeholder:
        return 0

    length = len(clean_comment)

    if length == 0:
        return 0
    elif length <= 50:
        return 1
    elif length <= 150:
        return 2
    else:
        return 3

def calculate_urgency_score(urgency):
    """
    Score based on urgency classification
    Low = 0 points
    Medium = 2 points
    High = 3 points
    """
    urgency_lower = urgency.lower() if urgency else ""

    if "high" in urgency_lower:
        return 3
    elif "medium" in urgency_lower:
        return 2
    else:  # low or unknown
        return 0

def calculate_specificity_score(comment):
    """
    Score based on specificity indicators
    Mentions exact measurements = +1 (scope known)
    Mentions timeline/deadline = +1 (urgency known)
    """
    if not comment:
        return 0

    score = 0
    comment_lower = comment.lower()

    # Check for measurements (feet, ft, inches, linear feet, sqft, etc.)
    measurement_patterns = [
        r'\d+\s*ft\b',
        r'\d+\s*feet\b',
        r'\d+\s*foot\b',
        r'\d+\s*linear\s*feet',
        r'\d+\s*sqft',
        r'\d+\s*inches',
        r'\d+\s*x\s*\d+',
        r'\d+\s*acres',
    ]

    has_measurements = any(re.search(pattern, comment_lower) for pattern in measurement_patterns)
    if has_measurements:
        score += 1

    # Check for timeline mentions
    timeline_keywords = [
        "asap", "urgent", "immediately", "right away", "within",
        "deadline", "timeline", "by", "before", "this week",
        "next week", "two weeks", "days", "month"
    ]

    has_timeline = any(keyword in comment_lower for keyword in timeline_keywords)
    if has_timeline:
        score += 1

    return min(score, 2)  # Cap at 2 points

def calculate_source_score(channel):
    """
    Score based on lead source
    Direct/Website = +1 (high intent)
    Angi/Yelp/other = 0 (comparison shopping)
    """
    if not channel:
        return 0

    channel_lower = channel.lower()

    high_intent_sources = ["direct", "website", "ergeon.com"]

    if any(source in channel_lower for source in high_intent_sources):
        return 1

    return 0

def score_lead(lead_id, comment, urgency, channel):
    """
    Calculate total enrichment score for a lead

    Returns:
        dict with score breakdown and enrichment level
    """
    comment_score = calculate_comment_score(comment)
    urgency_score = calculate_urgency_score(urgency)
    specificity_score = calculate_specificity_score(comment)
    source_score = calculate_source_score(channel)

    total_score = comment_score + urgency_score + specificity_score + source_score

    # Determine enrichment level
    if total_score <= 2:
        enrichment_level = MINIMAL
    elif total_score <= 5:
        enrichment_level = REDUCED
    else:
        enrichment_level = FULL

    return {
        "lead_id": lead_id,
        "total_score": total_score,
        "enrichment_level": enrichment_level,
        "breakdown": {
            "comment": comment_score,
            "urgency": urgency_score,
            "specificity": specificity_score,
            "source": source_score,
        }
    }

def load_leads_from_db_export(file_path="/tmp/remaining_leads.txt"):
    """Parse database export and extract lead data"""
    # This would parse the remaining_leads.txt file
    # For now, return sample data structure
    leads = []

    # TODO: Implement actual parsing from file
    # For now, using manual data entry

    return leads

def score_all_leads(leads_data):
    """
    Score all leads and return enrichment strategy

    Args:
        leads_data: List of dicts with keys: lead_id, comment, urgency, channel

    Returns:
        dict mapping lead_id to enrichment score details
    """
    scores = {}

    for lead in leads_data:
        score_result = score_lead(
            lead["lead_id"],
            lead.get("comment", ""),
            lead.get("urgency", "low"),
            lead.get("channel", "")
        )
        scores[lead["lead_id"]] = score_result

    return scores

def print_score_summary(scores):
    """Print summary of scoring results"""
    minimal_count = sum(1 for s in scores.values() if s["enrichment_level"] == MINIMAL)
    reduced_count = sum(1 for s in scores.values() if s["enrichment_level"] == REDUCED)
    full_count = sum(1 for s in scores.values() if s["enrichment_level"] == FULL)

    print("=" * 70)
    print("ENRICHMENT SCORING SUMMARY")
    print("=" * 70)
    print(f"Total leads: {len(scores)}")
    print(f"  MINIMAL (score 0-2): {minimal_count} leads - Weather + Location only")
    print(f"  REDUCED (score 3-5): {reduced_count} leads - Location + Project")
    print(f"  FULL (score 6-9):    {full_count} leads - All 3 agents")
    print("=" * 70)

    # Estimated agent load
    minimal_agents = minimal_count * 1  # Location only
    reduced_agents = reduced_count * 2  # Location + Project
    full_agents = full_count * 3       # All 3
    total_agents = minimal_agents + reduced_agents + full_agents

    print(f"\nEstimated agent load per batch (5 leads):")
    print(f"  Old approach: 5 leads × 6 agents = 30 agents")
    print(f"  New approach: ~{total_agents / (len(scores) / 5):.0f} agents average per 5-lead batch")
    print(f"  Reduction: ~{((30 - (total_agents / (len(scores) / 5))) / 30 * 100):.0f}% fewer agents")
    print()

# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_leads = [
        {
            "lead_id": 768088,
            "comment": "I need my wooden gates repaired on a 68 ft fence. The gates are currently damaged and not functioning properly and Id like them fixed within the next two weeks.",
            "urgency": "high",
            "channel": "Angi Ads"
        },
        {
            "lead_id": 768092,
            "comment": "Privacy fence",
            "urgency": "medium",
            "channel": "Home Depot"
        },
        {
            "lead_id": 768100,
            "comment": "Customer did not provide additional comments.",
            "urgency": "low",
            "channel": "Angi Ads"
        },
        {
            "lead_id": 768096,
            "comment": "info verified\nMessage: CCI wants to get a quote for a wooden fence replacement",
            "urgency": "medium",
            "channel": "Direct"
        },
    ]

    print("Testing Enrichment Scorer on Sample Leads")
    print("=" * 70)

    for lead in test_leads:
        result = score_lead(
            lead["lead_id"],
            lead["comment"],
            lead["urgency"],
            lead["channel"]
        )

        print(f"\nLead {result['lead_id']}")
        print(f"  Comment: {lead['comment'][:60]}...")
        print(f"  Urgency: {lead['urgency']}")
        print(f"  Channel: {lead['channel']}")
        print(f"  → Total Score: {result['total_score']}")
        print(f"  → Enrichment: {result['enrichment_level']}")
        print(f"  → Breakdown: {result['breakdown']}")

    print("\n")
    scores = score_all_leads(test_leads)
    print_score_summary(scores)
