# Full Pipeline v2.0 Scripts

This directory contains the optimization scripts for Full Pipeline v2.0.

## Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `enrichment_scorer.py` | Score leads 0-9 to determine enrichment level | `from enrichment_scorer import score_lead` |
| `enrichment_agent_prompts.py` | Generate prompts for 3 consolidated agents | `from enrichment_agent_prompts import get_location_economic_prompt` |
| `simple_weather_cache.py` | Pre-fetch weather for all leads (batch API call) | `python simple_weather_cache.py` |

## Quick Start

### 1. Pre-fetch Weather (one-time per batch set)

```bash
cd ~/.claude/skills/users/jose/first-sms-to-inbound-lead/scripts/
python simple_weather_cache.py
```

This creates `/tmp/weather_cache.json` with weather data for all 40 remaining leads.

### 2. Score Leads for Selective Enrichment

```python
#!/usr/bin/env python3
import sys
sys.path.append('/home/jose-carranza/.claude/skills/users/jose/first-sms-to-inbound-lead/scripts')
from enrichment_scorer import score_lead

# Example: Score a single lead
result = score_lead(
    lead_id=768088,
    comment="I need my wooden gates repaired on a 68 ft fence...",
    urgency="high",  # high/medium/low
    channel="Angi Ads"
)

print(f"Lead {result['lead_id']}: Score {result['total_score']} → {result['enrichment_level']}")
# Output: Lead 768088: Score 8 → FULL
```

### 3. Generate Agent Prompts

```python
#!/usr/bin/env python3
import sys
sys.path.append('/home/jose-carranza/.claude/skills/users/jose/first-sms-to-inbound-lead/scripts')
from enrichment_agent_prompts import (
    get_location_economic_prompt,
    get_person_communication_prompt,
    get_project_context_prompt
)

# Example: Generate prompts for FULL enrichment lead
lead_id = 768088
full_name = "Susan LYNN"
address = "2117 Maconda Ln, Houston, TX 77027"
coords = "29.7604,-95.3698"
comment = "I need my wooden gates repaired on a 68 ft fence..."
channel = "Angi Ads"

# Agent 1: Location & Economic
prompt1 = get_location_economic_prompt(lead_id, full_name, address, coords)

# Agent 2: Person & Communication
prompt2 = get_person_communication_prompt(lead_id, full_name, address, channel)

# Agent 3: Project Context
prompt3 = get_project_context_prompt(lead_id, full_name, address, coords, comment)

# Launch Task agents with these prompts
# Task(subagent_type="Explore", prompt=prompt1)
# Task(subagent_type="Explore", prompt=prompt2)
# Task(subagent_type="Explore", prompt=prompt3)
```

### 4. Read Weather from Cache

```python
import json

# Read pre-fetched weather
with open("/tmp/weather_cache.json", "r") as f:
    weather_cache = json.load(f)

lead_id = 768088
weather = weather_cache[str(lead_id)]

print(f"Weather: {weather['description']}, {weather['temp_f']}°F, wind {weather['wind_mph']} mph")
# Output: Weather: Partly cloudy, 52°F, wind 8 mph
```

## Enrichment Scoring Logic

### Scoring Parameters (0-9 points)

```python
# 1. Comment Length (0-3 points)
if len(comment) == 0 or is_placeholder: 0 points
elif len(comment) <= 50: 1 point
elif len(comment) <= 150: 2 points
else: 3 points

# 2. Urgency (0-3 points)
if urgency == "high": 3 points
elif urgency == "medium": 2 points
else: 0 points

# 3. Specificity (0-2 points)
has_measurements = "\d+ ft" in comment  # +1 point
has_timeline = "asap|urgent|within|deadline" in comment  # +1 point

# 4. Lead Source (0-1 point)
if channel in ["Direct", "Website"]: 1 point
else: 0 points
```

### Enrichment Levels

| Score | Enrichment Level | Agents Launched | What Gets Enriched |
|-------|------------------|-----------------|---------------------|
| 0-2 | **MINIMAL** | 1 agent | Location & Economic only |
| 3-5 | **REDUCED** | 2 agents | Location + Project Context |
| 6-9 | **FULL** | 3 agents | All dimensions |

### Example Scores

**FULL Enrichment (Score 8)**:
- Comment: "I need my wooden gates repaired on a 68 ft fence. Gates currently damaged, not functioning. Need completed within next two weeks." (3 points)
- Urgency: High (3 points)
- Specificity: Has measurements (68 ft) + timeline (two weeks) (2 points)
- Source: Angi Ads (0 points)
- **Total: 8 → FULL enrichment (3 agents)**

**MINIMAL Enrichment (Score 1)**:
- Comment: "Privacy fence" (1 point)
- Urgency: Low (0 points)
- Specificity: None (0 points)
- Source: Home Depot (0 points)
- **Total: 1 → MINIMAL enrichment (1 agent)**

## Batch Processing Workflow

### Complete Batch 6 Example

```python
#!/usr/bin/env python3
import sys
import json
sys.path.append('/home/jose-carranza/.claude/skills/users/jose/first-sms-to-inbound-lead/scripts')
from enrichment_scorer import score_lead
from enrichment_agent_prompts import (
    get_location_economic_prompt,
    get_person_communication_prompt,
    get_project_context_prompt
)

# Batch 6 leads (5 leads)
batch6_leads = [
    {"lead_id": 768108, "name": "Ruben Contreras", "address": "...", "comment": "...", "urgency": "medium", "channel": "Angi Ads"},
    # ... 4 more leads
]

# Step 1: Score all leads
for lead in batch6_leads:
    result = score_lead(lead["lead_id"], lead["comment"], lead["urgency"], lead["channel"])
    lead["score"] = result["total_score"]
    lead["enrichment_level"] = result["enrichment_level"]
    print(f"Lead {lead['lead_id']}: {result['enrichment_level']} (score {result['total_score']})")

# Step 2: Launch agents based on enrichment level
for lead in batch6_leads:
    print(f"\nEnriching Lead {lead['lead_id']} ({lead['enrichment_level']})")

    # All leads get Agent 1
    prompt1 = get_location_economic_prompt(lead["lead_id"], lead["name"], lead["address"], lead["coords"])
    # Task(subagent_type="Explore", prompt=prompt1)

    # REDUCED and FULL get Agent 3
    if lead["enrichment_level"] in ["REDUCED", "FULL"]:
        prompt3 = get_project_context_prompt(lead["lead_id"], lead["name"], lead["address"], lead["coords"], lead["comment"])
        # Task(subagent_type="Explore", prompt=prompt3)

    # FULL gets Agent 2
    if lead["enrichment_level"] == "FULL":
        prompt2 = get_person_communication_prompt(lead["lead_id"], lead["name"], lead["address"], lead["channel"])
        # Task(subagent_type="Explore", prompt=prompt2)

# Step 3: Read weather from cache
with open("/tmp/weather_cache.json", "r") as f:
    weather_cache = json.load(f)

for lead in batch6_leads:
    weather = weather_cache[str(lead["lead_id"])]
    print(f"Lead {lead['lead_id']}: {weather['description']}, {weather['temp_f']}°F")
```

## Performance Benchmarks

### Batch 5 Results (5 leads)

**v1.0 (old)**:
- 5 leads × 6 agents = 30 agents
- Time: ~25-30 minutes

**v2.0 (new)**:
- 2 FULL leads × 3 agents = 6 agents
- 3 MINIMAL leads × 1 agent = 3 agents
- Total: 9 agents
- Time: ~14 minutes

**Improvement**: 70% fewer agents, 44% faster

### Projected for Remaining 35 Leads

**v1.0**: 35 leads × 6 agents = 210 agents, ~5 hours

**v2.0**: ~63 agents (assuming 40% FULL, 60% MINIMAL), ~1.6 hours

**Time saved**: 3.4 hours (68% faster)

## Documentation

For complete documentation on Full Pipeline v2.0:
- **Main docs**: `../OPTIMIZATION_V2.md`
- **Enrichment agents**: `../ENRICHMENT_AGENTS.md`
- **Skill overview**: `../SKILL.md`

---

**Last Updated**: 2026-01-16
**Status**: Production-ready (validated in Batch 5)
