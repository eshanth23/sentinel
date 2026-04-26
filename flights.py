import requests
import json
import time
from datetime import datetime, timezone

print("=" * 60)
print("SENTINEL — FLIGHT TRACKING SIGNAL")
print("OpenSky Network — Free, No API Key Required")
print("=" * 60)
print()

def get_flights_in_region(name, lat_min, lat_max, lon_min, lon_max):
    """
    Get all aircraft currently flying over a region
    OpenSky free tier — no signup needed
    """
    print(f"[OPENSKY] Scanning airspace over {name}...")
    
    url = "https://opensky-network.org/api/states/all"
    params = {
        "lamin": lat_min,
        "lamax": lat_max,
        "lomin": lon_min,
        "lomax": lon_max
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            states = data.get("states", []) or []
            
            # Each state is an aircraft
            # state[0] = icao24 (unique ID)
            # state[1] = callsign
            # state[2] = origin country
            # state[5] = longitude
            # state[6] = latitude
            # state[9] = velocity
            # state[13] = true_track (heading)
            
            total = len(states)
            
            # Filter interesting aircraft
            military_patterns = [
                'RRR', 'MMM', 'NAF', 'UAF', 'RAF',
                'DUKE', 'COBRA', 'VIPER', 'EAGLE',
                'IRON', 'STEEL', 'GHOST', 'SHADOW'
            ]
            
            military = []
            unknown = []
            fast = []
            
            for s in states:
                callsign = str(s[1]).strip() if s[1] else ""
                country = str(s[2]) if s[2] else ""
                velocity = s[9] if s[9] else 0
                
                # Check for military callsigns
                for pattern in military_patterns:
                    if pattern in callsign.upper():
                        military.append({
                            "callsign": callsign,
                            "country": country,
                            "velocity": velocity
                        })
                        break
                
                # No callsign = potentially sensitive flight
                if not callsign or callsign == "":
                    unknown.append({
                        "country": country,
                        "velocity": velocity
                    })
                
                # Very fast aircraft (potential military)
                if velocity and velocity > 250:
                    fast.append({
                        "callsign": callsign,
                        "velocity": round(velocity, 1),
                        "country": country
                    })
            
            print(f"  Total aircraft: {total}")
            print(f"  Military callsigns: {len(military)}")
            print(f"  Unknown/no callsign: {len(unknown)}")
            print(f"  High speed (250m/s+): {len(fast)}")
            
            # Calculate flight anomaly score
            # More aircraft + military presence = higher score
            score = min(
                (total // 5) +
                (len(military) * 3) +
                (len(unknown) // 3) +
                (len(fast) // 2),
                20
            )
            
            print(f"  Flight score: {score}/20")
            
            return score, {
                "total": total,
                "military": military[:3],
                "unknown": len(unknown),
                "fast": fast[:3]
            }
            
        elif response.status_code == 429:
            print(f"  Rate limited — using baseline score")
            return get_flight_baseline(name), {}
            
        else:
            print(f"  HTTP {response.status_code} — using baseline")
            return get_flight_baseline(name), {}
            
    except Exception as e:
        print(f"  ERROR: {e}")
        print(f"  Using baseline score")
        return get_flight_baseline(name), {}


def get_flight_baseline(region_name):
    """
    Baseline flight activity scores based on
    known military presence in each region
    """
    baselines = {
        "ukraine": 14,
        "russia": 12,
        "taiwan": 10,
        "china": 9,
        "pakistan": 8,
        "india": 7,
        "middle east": 11,
        "korea": 8,
        "iran": 10,
        "israel": 13,
    }
    
    name_lower = region_name.lower()
    for key, score in baselines.items():
        if key in name_lower:
            return score
    return 5


# Test regions
regions = [
    {
        "name": "Ukraine-Russia Border",
        "lat_min": 44.0, "lat_max": 54.0,
        "lon_min": 22.0, "lon_max": 42.0
    },
    {
        "name": "Taiwan Strait",
        "lat_min": 20.0, "lat_max": 28.0,
        "lon_min": 116.0, "lon_max": 124.0
    },
    {
        "name": "India-Pakistan Border",
        "lat_min": 24.0, "lat_max": 36.0,
        "lon_min": 62.0, "lon_max": 78.0
    }
]

print("Scanning global airspace for anomalies...")
print("This is real data from OpenSky Network")
print()

results = []

for region in regions:
    score, data = get_flights_in_region(
        region["name"],
        region["lat_min"],
        region["lat_max"],
        region["lon_min"],
        region["lon_max"]
    )
    
    results.append({
        "name": region["name"],
        "score": score,
        "data": data
    })
    
    print()
    time.sleep(2)  # Respect rate limits

print("=" * 60)
print("FLIGHT SIGNAL SUMMARY")
print("=" * 60)
for r in results:
    bar = "█" * r["score"] + "░" * (20 - r["score"])
    print(f"  {r['name'][:25]:<25} [{bar}] {r['score']}/20")

print()
print("=" * 60)
print("Cost: $0.00 — OpenSky Network free tier")
print("=" * 60)