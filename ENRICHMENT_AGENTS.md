# Lead Enrichment Agents

**IMPORTANT**: This document describes both v1.0 (6 agents) and **v2.0 (3 agents - RECOMMENDED)**.

**For new batches, use Full Pipeline v2.0** - see `OPTIMIZATION_V2.md` for details.

---

## v2.0: 3-Agent Consolidation (RECOMMENDED)

**Status**: Production-ready (tested in Batch 5)
**Performance**: 70% fewer agents, 44% faster processing, quality maintained

### Overview

Full Pipeline v2.0 consolidates 6 agents into 3 with **selective enrichment** based on lead scoring:

**3 Consolidated Agents**:
1. **Location & Economic Profile** - Property + Budget combined
2. **Person & Communication Profile** - Decision-Maker + Digital combined
3. **Project Context & Constraints** - Intent + Timing + Weather combined

**Selective Enrichment**:
- **MINIMAL** (score 0-2): Agent 1 only (Location & Economic)
- **REDUCED** (score 3-5): Agent 1 + Agent 3 (Location + Project Context)
- **FULL** (score 6-9): All 3 agents (complete enrichment)

**Weather**: Pre-fetched via batch API call (see `scripts/simple_weather_cache.py`)

**See**: `OPTIMIZATION_V2.md` for complete v2.0 documentation and `scripts/enrichment_agent_prompts.py` for prompt templates.

---

## v1.0: 6-Agent Parallel Enrichment (LEGACY)

**Note**: v1.0 is still documented below for reference, but **v2.0 is recommended** for new batches.

These agents run in parallel to gather external data about leads across 6 dimensions:

1. **Property & Lot Attributes** - Physical property characteristics (WebSearch)
2. **Project Intent & Timing** - Trigger events and urgency signals (WebSearch)
3. **Decision-Maker Context** - Household and decision-maker info (WebSearch)
4. **Budget & Affordability** - Financial capacity signals (WebSearch)
5. **Digital Engagement** - Communication preferences (WebSearch)
6. **Weather Context** - Current/recent weather conditions (API call)

## Usage

### v2.0 Usage (RECOMMENDED)

**Step 1**: Score the lead (0-9 points) to determine enrichment level:
```python
from scripts.enrichment_scorer import score_lead

result = score_lead(
    lead_id=lead["lead_id"],
    comment=lead["comment"],
    urgency=lead["urgency"],  # high/medium/low
    channel=lead["channel"]
)
# Returns: {"total_score": 8, "enrichment_level": "FULL"}
```

**Step 2**: Launch agents based on enrichment level:
```python
from scripts.enrichment_agent_prompts import (
    get_location_economic_prompt,
    get_person_communication_prompt,
    get_project_context_prompt
)

# MINIMAL (score 0-2): Agent 1 only
if enrichment_level == "MINIMAL":
    Task(subagent_type="Explore", prompt=get_location_economic_prompt(...))

# REDUCED (score 3-5): Agent 1 + Agent 3
elif enrichment_level == "REDUCED":
    Task(subagent_type="Explore", prompt=get_location_economic_prompt(...))
    Task(subagent_type="Explore", prompt=get_project_context_prompt(...))

# FULL (score 6-9): All 3 agents
elif enrichment_level == "FULL":
    Task(subagent_type="Explore", prompt=get_location_economic_prompt(...))
    Task(subagent_type="Explore", prompt=get_person_communication_prompt(...))
    Task(subagent_type="Explore", prompt=get_project_context_prompt(...))
```

**Step 3**: Get weather from pre-fetched cache:
```python
import json
with open("/tmp/weather_cache.json", "r") as f:
    weather_cache = json.load(f)
weather = weather_cache[str(lead_id)]
```

---

### v1.0 Usage (LEGACY)

**Input Parameters**:

Each agent requires these lead parameters:
```
lead_id: {lead_id}
lead_name: "{lead_name}"
lead_address: "{full_address}"
lead_comment: "{comment}"
lead_channel: "{channel}"
latitude: {latitude}    # From geo_address table
longitude: {longitude}  # From geo_address table
```

**Invocation Pattern**:

Run all 6 agents in parallel:

```python
# WebSearch agents (via Task tool):
Task(subagent_type="Explore", prompt=PROPERTY_AGENT.format(...))
Task(subagent_type="Explore", prompt=INTENT_AGENT.format(...))
Task(subagent_type="Explore", prompt=DECISION_MAKER_AGENT.format(...))
Task(subagent_type="Explore", prompt=BUDGET_AGENT.format(...))
Task(subagent_type="Explore", prompt=DIGITAL_AGENT.format(...))

# Weather API agent (via Bash curl):
Bash(command=f"curl -s 'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=$OPENWEATHERMAP_API_KEY&units=imperial'")
```

**Note**: This approach uses 6 agents per lead. v2.0 reduces this to 1-3 agents per lead based on scoring.

---

## Agent 1: Property & Lot Attributes

**Purpose**: Find property-specific data for fence scoping and pricing.

**Data to Find**:
- Property type (single family, condo, townhouse)
- Lot size (sq ft or acres)
- Year built
- Ownership status (owner-occupied vs rental)
- Corner lot vs interior lot
- Pool presence
- Yard size / building footprint

**Prompt Template**:
```
You are a Property & Lot Attributes enrichment agent for Ergeon warm leads.

**Lead to Research:**
- Name: {lead_name}
- Address: {lead_address}

**Your Task:** Use WebSearch to find property-specific data that helps with fence project scoping and pricing.

**Data to Find:**
1. Property type (single family, condo, etc.)
2. Lot size (sq ft or acres)
3. Year built
4. Ownership status (owner-occupied vs rental)
5. Corner lot vs interior lot
6. Pool presence
7. Yard size / building footprint

**Search Patterns to Try:**
- "{lead_address}" property details
- "{lead_address}" lot size parcel
- "{lead_address}" zillow OR redfin OR realtor
- "{lead_address}" county assessor

**Output Format:**
Return a structured summary:

PROPERTY ENRICHMENT - {lead_id} {lead_name}
=========================================
Property Type: [value or "Not found"]
Lot Size: [value or "Not found"]
Year Built: [value or "Not found"]
Owner Status: [value or "Not found"]
Corner Lot: [Yes/No/Unknown]
Pool: [Yes/No/Unknown]
Yard Size Estimate: [value or "Not found"]

Confidence: [High/Medium/Low]
Sources: [list URLs]

Do NOT generate code. Only perform web searches and return the structured summary.
```

---

## Agent 2: Project Intent, Triggers & Timing

**Purpose**: Find trigger events and timing signals that explain WHY they need a fence now.

**Data to Find**:
- Recent home purchase
- Recent permits filed (fence, pool, remodel)
- Recent storm damage in the area
- Code violations or HOA issues
- Neighborhood fence trends

**Prompt Template**:
```
You are a Project Intent, Triggers & Timing enrichment agent for Ergeon warm leads.

**Lead to Research:**
- Name: {lead_name}
- Address: {lead_address}
- Lead Comment: "{lead_comment}"

**Your Task:** Use WebSearch to find trigger events and timing signals that explain WHY they need a fence now.

**Data to Find:**
1. Recent home purchase (did they just buy the property?)
2. Recent permits filed (fence, pool, remodel)
3. Recent storm damage in the area
4. Code violations or HOA issues
5. Neighborhood fence trends

**Search Patterns to Try:**
- "{lead_address}" sold recently
- "{city} {state} {zip}" fence permit 2025 2026
- "{city} {state}" storm damage fence news
- "{county}" fence permit requirements

**Output Format:**
Return a structured summary:

PROJECT INTENT ENRICHMENT - {lead_id} {lead_name}
===============================================
Recent Purchase: [Yes/No/Unknown] - [date if found]
Recent Permits: [Yes/No/Unknown] - [details]
Storm Damage Area: [Yes/No/Unknown]
Code/HOA Issues: [Yes/No/Unknown]
Trigger Event: [summary of likely trigger]

Urgency Signal: [High/Medium/Low]
Sources: [list URLs]

Do NOT generate code. Only perform web searches and return the structured summary.
```

---

## Agent 3: Decision-Maker & Household Context

**Purpose**: Find information about the decision-maker to personalize outreach.

**Data to Find**:
- Full name confirmation and co-owners
- Approximate age bracket
- Household composition (family, pets)
- Professional role/occupation
- Tenure in home
- Property manager / HOA role (if commercial)

**Prompt Template**:
```
You are a Decision-Maker & Household Context enrichment agent for Ergeon warm leads.

**Lead to Research:**
- Name: {lead_name}
- Address: {lead_address}

**Your Task:** Use WebSearch to find information about the decision-maker that helps personalize outreach.

**Data to Find:**
1. Full name confirmation and any co-owners
2. Approximate age bracket
3. Household composition clues (family, pets, etc.)
4. Professional role/occupation (LinkedIn)
5. Tenure in home (how long have they lived there?)
6. If commercial: property manager, HOA board role

**Search Patterns to Try:**
- "{lead_name}" {city} {state}
- "{lead_name}" {city} LinkedIn
- "{lead_address}" owner name
- "{lead_name}" {metro_area}

**Output Format:**
Return a structured summary:

DECISION-MAKER ENRICHMENT - {lead_id} {lead_name}
===============================================
Full Name: [confirmed name]
Co-Owners: [names if found]
Age Bracket: [estimate or "Unknown"]
Household: [family/single/unknown]
Occupation: [if found]
Tenure: [years or "Unknown"]
Role Type: [Homeowner/Property Manager/Other]

Personalization Notes: [any useful context for outreach]
Sources: [list URLs]

Do NOT generate code. Only perform web searches and return the structured summary.
```

---

## Agent 4: Budget, Affordability & Value Sensitivity

**Purpose**: Find financial signals for pricing strategy and financing offers.

**Data to Find**:
- Estimated home value
- Neighborhood median home values
- Neighborhood income level indicators
- Other visible improvements (solar, pool, landscaping)
- Price sensitivity signals

**Prompt Template**:
```
You are a Budget, Affordability & Value Sensitivity enrichment agent for Ergeon warm leads.

**Lead to Research:**
- Name: {lead_name}
- Address: {lead_address}

**Your Task:** Use WebSearch to find financial signals that help with pricing strategy and financing offers.

**Data to Find:**
1. Estimated home value (Zillow, Redfin, etc.)
2. Neighborhood median home values
3. Neighborhood income level indicators
4. Other visible improvements (solar panels, pool, landscaping)
5. Price sensitivity signals

**Search Patterns to Try:**
- "{lead_address}" home value zillow
- "{lead_address}" estimate redfin
- "{city} {state} {zip}" median home price
- "{city} {state}" home improvement trends

**Output Format:**
Return a structured summary:

BUDGET ENRICHMENT - {lead_id} {lead_name}
=======================================
Home Value Estimate: $[value or "Not found"]
Neighborhood Median: $[value or "Not found"]
Income Indicators: [High/Medium/Low/Unknown]
Visible Improvements: [list or "None visible"]
Value Tier: [Premium/Mid-Range/Budget-Conscious]

Pricing Strategy Note: [recommendation]
Sources: [list URLs]

Do NOT generate code. Only perform web searches and return the structured summary.
```

---

## Agent 5: Digital Engagement & Channel Preferences

**Purpose**: Find the lead's digital footprint and communication preferences.

**Data to Find**:
- Reviews they've left for contractors
- Social media presence
- Local community group participation
- Sentiment toward contractors
- Language preference
- Communication style clues

**Prompt Template**:
```
You are a Digital Engagement & Channel Preferences enrichment agent for Ergeon warm leads.

**Lead to Research:**
- Name: {lead_name}
- Address: {city}, {state} {zip}
- Channel: {lead_channel}

**Your Task:** Use WebSearch to find the lead's digital footprint and communication preferences.

**Data to Find:**
1. Reviews they've left for contractors (Yelp, Google, Angi)
2. Social media presence and activity
3. Local community group participation
4. Sentiment toward contractors/home projects
5. Language preference (English/Spanish)
6. Communication style clues

**Search Patterns to Try:**
- "{lead_name}" {city} review
- "{lead_name}" {metro_area} Yelp Google review
- "{lead_name}" {city} Facebook
- "{lead_name}" contractor review

**Output Format:**
Return a structured summary:

DIGITAL ENGAGEMENT ENRICHMENT - {lead_id} {lead_name}
===================================================
Reviews Left: [count and summary or "None found"]
Social Presence: [platforms found]
Community Groups: [any local groups]
Contractor Sentiment: [Positive/Negative/Neutral/Unknown]
Language: [English/Spanish/Bilingual]
Communication Style: [Formal/Casual/Direct/Unknown]

Channel Recommendation: [SMS/Email/Phone preference]
Tone Recommendation: [suggested approach]
Sources: [list URLs]

Do NOT generate code. Only perform web searches and return the structured summary.
```

---

## Agent 6: Weather Context

**Purpose**: Get current weather conditions and recent weather events at the lead's location.

**IMPORTANT**: This agent uses the OpenWeatherMap API, NOT WebSearch.

**Required Parameters**:
- `latitude` - From geo_address table
- `longitude` - From geo_address table

**Data to Find**:
- Current temperature and conditions
- Recent precipitation/storms
- Weather alerts
- Wind conditions (relevant for fence damage)

### API Endpoints

**Current Weather**:
```bash
curl -s "https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=$OPENWEATHERMAP_API_KEY&units=imperial"
```

**Response Fields to Extract**:
```json
{
  "weather": [{"main": "Clear", "description": "clear sky"}],
  "main": {"temp": 77.4, "humidity": 20},
  "wind": {"speed": 1.99, "gust": 5.01},
  "name": "City Name"
}
```

### Processing Logic

```python
import json
import os

def get_weather_enrichment(latitude: float, longitude: float) -> dict:
    """
    Fetch weather data from OpenWeatherMap API.

    Args:
        latitude: Lead's latitude from geo_address
        longitude: Lead's longitude from geo_address

    Returns:
        Weather enrichment dict
    """
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")

    # Current weather
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=imperial"
    response = requests.get(url)
    data = response.json()

    # Extract relevant fields
    weather = {
        "location": data.get("name", "Unknown"),
        "temp_f": data["main"]["temp"],
        "conditions": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "wind_gust": data["wind"].get("gust", 0),

        # Derived signals
        "is_stormy": data["weather"][0]["main"] in ["Thunderstorm", "Rain", "Snow"],
        "high_wind": data["wind"].get("gust", 0) > 25,  # >25 mph gusts
        "recent_rain": data["weather"][0]["main"] == "Rain",
    }

    return weather
```

### Output Format

```
WEATHER ENRICHMENT - {lead_id} {lead_name}
==========================================
Location: {city_name}
Temperature: {temp}°F
Conditions: {description}
Humidity: {humidity}%
Wind: {wind_speed} mph (gusts: {wind_gust} mph)

Weather Signals:
- Is Stormy: [Yes/No]
- High Wind: [Yes/No] (>25 mph gusts)
- Recent Rain: [Yes/No]

SMS Hook Recommendation: [if applicable]
```

### Weather-Aware SMS Hooks

| Weather Signal | SMS Hook |
|----------------|----------|
| `is_stormy = true` | "With the recent storms in {city}..." |
| `high_wind = true` | "After the high winds this week..." |
| `recent_rain = true` | "Now that the rain has passed..." |
| Clear + hot (>90°F) | "Before the summer heat picks up..." |
| Clear + cold (<40°F) | "Before winter weather arrives..." |

### When to Use Weather Data

**High Value** (definitely use):
- Lead comment mentions "storm", "wind", "damage"
- Lead is in a flood zone (from regrid data)
- Recent severe weather alerts in area

**Medium Value** (consider using):
- Seasonal messaging opportunities
- Time-sensitive outdoor work window

**Low Value** (skip):
- Normal weather, no comment about weather
- Lead urgency is low/flexible

---

## Consolidated Output Schema

After all 6 agents complete, combine into a single enrichment object:

```json
{
  "lead_id": "{lead_id}",
  "lead_name": "{lead_name}",
  "enrichment_timestamp": "{timestamp}",

  "property": {
    "type": "{property_type}",
    "lot_size": "{lot_size}",
    "year_built": "{year_built}",
    "bedrooms": "{bedrooms}",
    "bathrooms": "{bathrooms}",
    "sqft": "{sqft}",
    "pool": "{pool: true|false}",
    "corner_lot": "{corner_lot: yes|no|unknown}",
    "confidence": "{confidence: high|medium|low}"
  },

  "intent": {
    "recent_purchase": "{recent_purchase: yes|no|unknown}",
    "recent_permits": "{recent_permits: yes|no|unknown}",
    "storm_damage_area": "{storm_damage: true|false}",
    "code_issues": "{code_issues: yes|no|possible|unknown}",
    "trigger_event": "{trigger_summary}",
    "urgency_signal": "{urgency: high|medium-high|medium|low}"
  },

  "decision_maker": {
    "full_name": "{full_name}",
    "co_owners": "{co_owners|null}",
    "age_bracket": "{age_bracket|unknown}",
    "household_size": "{household_size}",
    "occupation": "{occupation|unknown}",
    "tenure_years": "{tenure|unknown}",
    "role_type": "{role: homeowner|property_manager|other}"
  },

  "budget": {
    "home_value": "{home_value}",
    "neighborhood_median": "{neighborhood_median}",
    "income_indicators": "{income: high|medium|low|unknown}",
    "visible_improvements": ["{improvements}"],
    "value_tier": "{tier: premium|mid-range|budget-conscious}",
    "pricing_strategy": "{pricing_recommendation}"
  },

  "digital": {
    "reviews_left": "{review_count}",
    "social_presence": "{social: active|limited|none}",
    "community_groups": ["{groups}"],
    "contractor_sentiment": "{sentiment: positive|negative|neutral|unknown}",
    "language": "{language: english|spanish|bilingual}",
    "communication_style": "{style: formal|casual|direct|unknown}",
    "channel_recommendation": "{channel_pref: sms|phone|email}",
    "tone_recommendation": "{tone_guidance}"
  },

  "weather": {
    "location": "{city}",
    "temp_f": "{temperature}",
    "conditions": "{weather_description}",
    "humidity": "{humidity_pct}",
    "wind_speed": "{wind_mph}",
    "wind_gust": "{gust_mph}",
    "is_stormy": "{is_stormy: true|false}",
    "high_wind": "{high_wind: true|false}",
    "recent_rain": "{recent_rain: true|false}",
    "sms_hook": "{weather_hook|null}"
  }
}
```

---

## Integration with SMS Pipeline

### Stage 3: Enrich Data

In the 8-stage SMS pipeline, Stage 3 invokes these 6 agents:

```
Stage 2: Gather Data (DB query) → get latitude/longitude
       ↓
Stage 3: Enrich Data ← RUN ALL 6 AGENTS IN PARALLEL
       │
       ├── Agent 1-5: WebSearch (via Task tool)
       └── Agent 6: Weather API (via Bash curl)
       ↓
Stage 4: Classify Intent (GPT-5-nano)
```

### Using Enrichment in SMS Generation

Pass enrichment data to Claude for draft generation:

```
ENRICHMENT CONTEXT:
- Property: {property.type}, built {property.year_built}, {property.lot_size} lot
- Trigger: {intent.trigger_event} (Urgency: {intent.urgency_signal})
- Budget: {budget.value_tier} tier, ${budget.home_value} home
- Channel Pref: {digital.channel_recommendation}
- Tone: {digital.tone_recommendation}
- Weather: {weather.conditions}, {weather.temp_f}°F, wind {weather.wind_speed}mph
- Weather Hook: {weather.sms_hook} (if applicable)
```

### Enrichment-Aware SMS Examples

**Without enrichment:**
> Hi {first_name}! Thanks for connecting through {channel}. For your {project_scope}...

**With enrichment (storm damage + premium tier):**
> Hi {first_name}! With the recent {city} storms, we've been helping homeowners restore damaged fencing. For your {project_scope}, we handle everything - permits, removal, installation. Quick 10-min video call from your phone gets you a same-day quote. Does today or tomorrow work better? - {signature}

**Changes driven by enrichment:**
- Storm damage hook (from `intent.storm_damage_area`)
- Quality-focused language (from `budget.value_tier`)
- Direct CTA (from `digital.tone_recommendation`)
- Weather context (from `weather.is_stormy` or recent alerts)

---

## Performance Notes

- **Parallel execution**: All 6 agents run simultaneously (~30-60 seconds total)
- **Rate limiting**: WebSearch has built-in rate limiting
- **Weather API**: 60 calls/minute limit (free tier), ~200ms response time
- **Caching**: Results can be cached by lead_id for re-runs
- **Fallbacks**: If an agent fails, continue with partial enrichment
- **API Key**: `OPENWEATHERMAP_API_KEY` must be set in `~/.claude/env`

---

## Maintenance

**Last Updated**: 2026-01-16
**Author**: Jose Carranza
**Competition**: CTO Innovation Day - First SMS to Inbound Lead
**Current Version**: v2.0 (3-agent consolidation with selective enrichment)
**Validated**: Batch 5 (5 leads, 70% agent reduction, quality maintained)

---

## Migration from v1.0 to v2.0

**For new batches (Batches 6-12)**, use the v2.0 workflow:

1. Pre-fetch weather: `python scripts/simple_weather_cache.py`
2. Score leads: `from scripts.enrichment_scorer import score_lead`
3. Use selective enrichment: Launch 1-3 agents based on score
4. Read weather from cache: `/tmp/weather_cache.json`

**See**: `OPTIMIZATION_V2.md` for complete migration guide and performance benchmarks.
