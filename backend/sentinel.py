import time
import sys
from signals import calculate_threat_score
from brief import generate_conflict_brief
from ukraine_replay import ukraine_replay

def run_sentinel():
    
    print("=" * 65)
    print("  SENTINEL — GLOBAL THREAT INTELLIGENCE SYSTEM")
    print("  Signal-based Early Warning Network")
    print("  For: SCSP Hackathon 2026 — Wargaming Track")
    print("  Cost: $0.00")
    print("=" * 65)
    print()
    print("  Select mode:")
    print()
    print("  1. Live global threat scan")
    print("  2. Ukraine 2022 historical replay")
    print("  3. Generate AI conflict brief")
    print()
    
    choice = input("  Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        print()
        countries = [
            ("Ukraine-Russia Border", 49.4871, 31.2718),
            ("Taiwan Strait", 23.6978, 120.9605),
            ("India-Pakistan Border", 30.3753, 69.3451),
        ]
        
        results = []
        for country, lat, lon in countries:
            result = calculate_threat_score(country, lat, lon)
            results.append(result)
            time.sleep(2)
            
        # Show highest threat
        results.sort(key=lambda x: x["score"], reverse=True)
        top = results[0]
        
        if top["score"] >= 55:
            print()
            print("ALERT — Generating AI brief for highest threat zone...")
            time.sleep(1)
            generate_conflict_brief(
                country_name=top["country"],
                threat_score=top["score"],
                threat_level=top["level"],
                signals=top["signals"],
                articles=top.get("articles", []),
                anomalies=top.get("anomalies", [])
            )
    
    elif choice == "2":
        ukraine_replay()
        print()
        print("Generating AI brief for this historical moment...")
        time.sleep(2)
        from backend.brief import generate_ukraine_2022_brief
        generate_ukraine_2022_brief()
        
    elif choice == "3":
        from backend.brief import generate_ukraine_2022_brief
        generate_ukraine_2022_brief()
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    run_sentinel()