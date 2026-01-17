# First SMS to Inbound Lead - CTO Innovation Day Submission

**Author**: Jose Carranza
**Date**: January 16, 2026
**Competition**: CTO Innovation Day - Ergeon

## Overview

Automated generation of personalized, high-converting first SMS responses for 100 inbound fence leads using an 8-stage pipeline with GPT-5.2 critique loop and LVE-focused CTAs.

## Key Results

- **33 leads processed** with Full Pipeline v2.0 (Batches 1-8)
- **70% agent reduction**: Average 9-12 agents per batch vs 30 with baseline approach
- **Quality maintained**: Full enrichment for high-score leads, selective for low-score
- **SMS optimized**: All messages 160-320 characters
- **Response mechanics**: "Reply 1 or 2" friction reducers, photo alternatives

## Repository Structure

```
.
├── samples_first_smses.md          # Main deliverable: 33 personalized SMS responses
├── SKILL.md                        # Complete skill documentation
├── ENRICHMENT_AGENTS.md           # Agent architecture and prompts
├── OPTIMIZATION_V2.md             # Optimization strategy and results
├── scripts/
│   ├── enrichment_scorer.py       # Lead scoring (0-9 points)
│   ├── enrichment_agent_prompts.py # Agent prompt templates
│   ├── simple_weather_cache.py    # Weather pre-fetching utility
│   └── README.md                  # Scripts documentation
└── batch_summaries/               # Detailed batch completion reports
    ├── batch6_completion_summary.md
    ├── batch7_completion_summary.md
    └── batch8_completion_summary.md
```

## Pipeline Architecture

### 1. Selective Enrichment Scoring (0-9 points)

Determines enrichment level based on comment quality, urgency, and specificity:

- **MINIMAL (0-2 points)**: 1 agent - Location & Economic only
- **REDUCED (3-5 points)**: 2 agents - Location + Project Context
- **FULL (6-9 points)**: 3 agents - All dimensions

### 2. 3-Agent Consolidation

**Agent 1: Location & Economic Profile**
- Property type, size, age, features
- Home value and neighborhood median
- Household income estimate
- Economic tier classification

**Agent 2: Person & Communication Profile**
- Decision-maker profile research
- Digital footprint / social presence
- Communication preferences
- Household characteristics

**Agent 3: Project Context & Constraints**
- Project intent signals
- Local permit/HOA requirements
- Timing/urgency factors
- Weather conditions

### 3. Weather Pre-fetching

Batch API calls to weather service, cached in JSON for instant lookups.

### 4. GPT-5-nano Classification

Fast lead classification:
- **project_type**: Installation | Replacement | Replacement + Gate | Repair | Unknown
- **buyer_stage**: Awareness | Consideration | Decision | Unknown
- **urgency**: Low | Medium | High

### 5. SMS Drafting

Manual drafting using enrichment data and classifications.

### 6. GPT-5.2 Critique

Expert review of draft messages with specific feedback on:
- Personalization quality
- Channel fit (Angi Ads, Home Depot, etc.)
- CTA effectiveness
- Length and tone

### 7. Refinement

Apply GPT-5.2 feedback to improve messages.

### 8. Documentation

Full Pipeline v2.0 format with enrichment summary, final SMS, WHY section, and refinements applied.

## Key Innovations

### Reply Friction Reducers
```
"Reply 1 or 2" mechanic for easy response vs open-ended questions
```

### Photo Alternatives
```
"Quick 10-min video call or text 2-3 photos" - lowers barrier for leads who prefer not to video call
```

### HOA/Permit Awareness
```
"check any HOA/permit limits" - proactive for areas like Winter Park FL where constraints likely
```

### Timeline Matching
```
Urgent leads: "Today 2pm ET or tomorrow 9am ET"
Planning leads: "This week or early next week"
```

### Economic Tier Handling
Successfully handled range from Lower-middle ($49K HH income) to Affluent-Premium ($98K HH income).

## Sample Results

### Lead 768152: Andy Ortiz (FULL Enrichment)
**Context**: Director of Operations, Winter Park FL, vinyl replacing wood, 2-week timeline, needs height recommendation

**Final SMS** (273 chars):
```
Hi Andy! For your vinyl fence replacement in Winter Park - we can recommend the right height (and check any HOA/permit limits) plus meet your 2-week timeline. Quick 10-min video call for same-day quote. Tomorrow 10am ET or Thu 3pm ET? Reply 1 or 2. - Ergeon Team
```

### Lead 768160: alva goldston (REDUCED Enrichment)
**Context**: Middle-income, Covington GA, broken gate (urgent repair)

**Final SMS** (210 chars):
```
Hi Alva! For your broken gate in Covington - we can get you secure quickly. Quick 10-min video call or text 2-3 photos for same-day repair quote. Today 2pm ET or tomorrow 9am ET? Reply 1 or 2. - Ergeon Team
```

### Lead 768164: Danny Alvarado (MINIMAL Enrichment)
**Context**: Lower-middle income, Pharr TX, no comment, Home Depot channel

**Final SMS** (241 chars):
```
Hi Danny! Thanks for reaching out through Home Depot. For your Pharr fence project - new fence or replacing one? Quick 10-min video call (or text photos) for same-day quote. Tomorrow 11am CT or 4pm CT? Reply 1 or 2. - Ergeon Team
```

## Performance Metrics

| Metric | Batch 6 | Batch 7 | Batch 8 | Average |
|--------|---------|---------|---------|---------|
| Leads Processed | 5 | 4 | 5 | 4.7 |
| Agents Used | 9 | 10 | 9 | 9.3 |
| Agent Reduction | 70% | 67% | 70% | 69% |
| Processing Time | ~14 min | ~16 min | ~16 min | ~15 min |
| Character Count | 171-225 | 217-248 | 210-273 | 210-249 |

## Time Savings Projection

- **Old approach**: 100 leads × 6 agents × 5 min/agent = **30 hours**
- **New approach**: 100 leads × 1.8 avg agents × 5 min/agent = **~9 hours**
- **Time saved**: **~21 hours (70% faster)** ✅

## Usage

### Prerequisites
- Python 3.8+
- OpenAI API access (GPT-5-nano, GPT-5.2)
- Claude Code CLI
- Access to lead database

### Quick Start

1. **Score leads**:
```bash
cd scripts
python3 enrichment_scorer.py
```

2. **Launch enrichment agents** (via Claude Code):
Use Task tool with `general-purpose` subagent and prompts from `enrichment_agent_prompts.py`

3. **Classify with GPT-5-nano**:
```bash
~/.claude/skills/development-engineering-openai-chat/scripts/openai_chat.py \
  --model gpt-5-nano \
  --system "You are a lead classification expert..." \
  --prompt-file classify_batch.txt
```

4. **Draft SMS messages** manually using enrichment data

5. **Critique with GPT-5.2**:
```bash
~/.claude/skills/development-engineering-openai-chat/scripts/openai_chat.py \
  --model gpt-5.2 \
  --system "You are a sales communication expert..." \
  --prompt-file batch_critique.txt
```

6. **Refine** based on GPT-5.2 feedback

7. **Update** samples_first_smses.md with Full Pipeline v2.0 format

## Documentation

- **[SKILL.md](SKILL.md)**: Complete skill documentation with usage instructions
- **[ENRICHMENT_AGENTS.md](ENRICHMENT_AGENTS.md)**: Agent architecture, prompts, and rationale
- **[OPTIMIZATION_V2.md](OPTIMIZATION_V2.md)**: Optimization strategy, selective enrichment, and 3-agent consolidation
- **[scripts/README.md](scripts/README.md)**: Helper scripts documentation

## Batch Summaries

Detailed completion reports with enrichment quality checks, GPT-5.2 critique applications, and key learnings:

- **[Batch 6](batch_summaries/batch6_completion_summary.md)**: 5 leads, 70% reduction
- **[Batch 7](batch_summaries/batch7_completion_summary.md)**: 4 leads (1 out of scope), 67% reduction
- **[Batch 8](batch_summaries/batch8_completion_summary.md)**: 5 leads, 70% reduction

## Progress Status

- ✅ **Batches 1-8 complete**: 33 leads processed (32 in-scope)
- ⏳ **Remaining**: Batches 9-12 (~20 leads)
- 🎯 **Completion**: 65% done

## License

Internal Ergeon project - CTO Innovation Day submission

## Contact

**Jose Carranza**
Email: jose@ergeon.com
GitHub: [@elmaster84ai](https://github.com/elmaster84ai)
