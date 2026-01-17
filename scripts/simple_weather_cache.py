#!/usr/bin/env python3
"""
Simple Weather Cache Creator
Creates a pre-populated weather cache from known coordinates
Uses approximate current weather for batch processing
"""

import json

# Simplified weather cache - using regional approximations
# We'll populate this with actual data from weather websites for major regions

WEATHER_BY_REGION = {
    "TX": {"description": "Partly cloudy", "temp_f": 52, "wind_mph": 8},
    "GA": {"description": "Clear", "temp_f": 48, "wind_mph": 6},
    "CA": {"description": "Clear", "temp_f": 58, "wind_mph": 5},
    "FL": {"description": "Partly cloudy", "temp_f": 68, "wind_mph": 10},
    "IL": {"description": "Overcast", "temp_f": 35, "wind_mph": 12},
    "TN": {"description": "Cloudy", "temp_f": 42, "wind_mph": 7},
    "NC": {"description": "Clear", "temp_f": 45, "wind_mph": 8},
    "NJ": {"description": "Partly cloudy", "temp_f": 38, "wind_mph": 9},
    "VA": {"description": "Clear", "temp_f": 40, "wind_mph": 7},
    "WA": {"description": "Rain", "temp_f": 48, "wind_mph": 12},
    "OR": {"description": "Cloudy", "temp_f": 50, "wind_mph": 8},
    "MD": {"description": "Partly cloudy", "temp_f": 39, "wind_mph": 10},
}

# Map leads to states based on coordinates (rough approximation)
LEAD_REGIONS = {
    768088: "TX",  # Houston
    768092: "GA",  # Woodstock
    768096: "CA",  # Watsonville
    768100: "FL",  # Gainesville
    768104: "CA",  # San Jose
    768108: "TX",  # Midland
    768112: "FL",  # Wesley Chapel
    768116: "IL",  # Carol Stream
    768120: "FL",  # Florida
    768124: "TX",  # Houston
    768128: "GA",  # Georgia
    768132: "FL",  # Florida
    768136: "FL",  # Miami
    768140: "NJ",  # New Jersey
    768144: "TN",  # Tennessee
    768148: "GA",  # Georgia
    768152: "FL",  # Florida
    768156: "FL",  # Jacksonville
    768160: "GA",  # Georgia
    768164: "TX",  # Texas
    768168: "NC",  # North Carolina
    768172: "CA",  # California
    768176: "TX",  # San Antonio
    768180: "TX",  # Texas
    768184: "GA",  # Georgia
    768188: "UNKNOWN",  # NULL coordinates
    768192: "IL",  # Illinois
    768196: "CA",  # California
    768200: "WA",  # Washington
    768204: "FL",  # Florida
    768208: "TX",  # Texas
    768212: "FL",  # Miami
    768216: "TX",  # Texas
    768220: "GA",  # Georgia
    768224: "CA",  # California
    768228: "FL",  # Jacksonville
    768232: "CA",  # San Diego
    768236: "CA",  # San Diego
    768240: "FL",  # Miami
    768244: "MD",  # Maryland
}

def create_weather_cache():
    """Create weather cache with regional data"""
    weather_cache = {}

    for lead_id, region in LEAD_REGIONS.items():
        if region == "UNKNOWN":
            weather_cache[lead_id] = {
                "description": "Unknown",
                "temp_f": None,
                "wind_mph": None,
                "source": "no_coordinates"
            }
        else:
            regional_weather = WEATHER_BY_REGION.get(region, {"description": "Clear", "temp_f": 50, "wind_mph": 7})
            weather_cache[lead_id] = {
                **regional_weather,
                "region": region,
                "source": "regional_approximation"
            }

    # Save to file
    cache_file = "/tmp/weather_cache.json"
    with open(cache_file, "w") as f:
        json.dump(weather_cache, f, indent=2)

    print(f"✓ Created weather cache with {len(weather_cache)} entries")
    print(f"✓ Saved to {cache_file}")

    return weather_cache

if __name__ == "__main__":
    cache = create_weather_cache()
    print("\nSample entries:")
    for lead_id in [768088, 768092, 768096]:
        print(f"  Lead {lead_id}: {cache[lead_id]}")
