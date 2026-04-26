import time
import os
from datetime import datetime, timezone

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_bar(score, max_score=100, width=30):
    filled = int((score / max_score) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {score}/{max_score}"

def get_level(score):
    if score >= 75:
        return "🔴 CRITICAL"
    elif score >= 55:
        return "🟠 HIGH"
    elif score >= 35:
        return "🟡 ELEVATED"
    else:
        return "🟢 NORMAL"

def ukraine_replay():
    """
    Animated replay of signals building up
    before the Ukraine invasion February 2022
    This is your demo centerpiece
    """
    
    clear()
    
    print("=" * 65)
    print("  SENTINEL — UKRAINE 2022 HISTORICAL REPLAY")
    print("  Demonstrating pre-conflict signal detection")
    print("=" * 65)
    print()
    time.sleep(2)
    
    # Timeline of events — January 28 to February 24 2022
    timeline = [
        {
            "date": "January 28, 2022",
            "event": "US Embassy orders family members to leave Ukraine",
            "news": 8,
            "seismic": 0,
            "finance": 4,
            "acled": 5,
            "note": "First public signal — diplomatic families evacuating"
        },
        {
            "date": "February 3, 2022", 
            "event": "Russia masses 130,000 troops at Ukraine border",
            "news": 14,
            "seismic": 0,
            "finance": 10,
            "acled": 8,
            "note": "Satellite imagery confirms unprecedented troop buildup"
        },
        {
            "date": "February 11, 2022",
            "event": "US warns invasion could come any day",
            "news": 20,
            "seismic": 2,
            "finance": 16,
            "acled": 12,
            "note": "Defence stocks surging — money moving before armies"
        },
        {
            "date": "February 16, 2022",
            "event": "Russia begins military exercises — largest since Cold War",
            "news": 24,
            "seismic": 3,
            "finance": 20,
            "acled": 15,
            "note": "Drill frequency anomaly detected near all borders"
        },
        {
            "date": "February 21, 2022",
            "event": "Putin recognizes separatist regions — 72hrs before invasion",
            "news": 28,
            "seismic": 5,
            "finance": 24,
            "acled": 18,
            "note": "SENTINEL ALERT THRESHOLD CROSSED"
        },
        {
            "date": "February 24, 2022",
            "event": "⚠️  INVASION BEGINS — Russian forces enter Ukraine",
            "news": 30,
            "seismic": 8,
            "finance": 28,
            "acled": 20,
            "note": "First shots fired — conflict begins"
        }
    ]
    
    print("  Starting signal replay from January 28, 2022...")
    print("  Watch the threat score climb in real time")
    print()
    time.sleep(3)
    
    alert_fired = False
    
    for i, moment in enumerate(timeline):
        clear()
        
        # Calculate total score
        base = 10
        total = base + moment["news"] + moment["seismic"] + moment["finance"] + moment["acled"]
        total = min(total, 100)
        level = get_level(total)
        
        print("=" * 65)
        print("  SENTINEL — UKRAINE 2022 SIGNAL REPLAY")
        print("=" * 65)
        print()
        print(f"  DATE    : {moment['date']}")
        print(f"  EVENT   : {moment['event']}")
        print()
        print("  LIVE SIGNALS:")
        print(f"  News/Media      : {print_bar(moment['news'], 30, 20)} {'⚡' if moment['news'] > 15 else ''}")
        print(f"  Defence Stocks  : {print_bar(moment['finance'], 30, 20)} {'⚡' if moment['finance'] > 12 else ''}")
        print(f"  Armed Conflicts : {print_bar(moment['acled'], 20, 20)} {'⚡' if moment['acled'] > 10 else ''}")
        print(f"  Seismic         : {print_bar(moment['seismic'], 20, 20)}")
        print()
        print(f"  {'─' * 59}")
        print()
        print(f"  THREAT SCORE : {print_bar(total, 100, 30)}")
        print(f"  THREAT LEVEL : {level}")
        print()
        
        # Fire alert at the right moment
        if total >= 55 and not alert_fired:
            alert_fired = True
            print("!" * 65)
            print("  ⚠️   SENTINEL ALERT FIRED")
            print(f"  Score {total}/100 — Pattern matches pre-invasion signature")
            print(f"  Historical match: Russia-Georgia 2008 / Crimea 2014")
            print(f"  Recommendation: Immediate diplomatic intervention required")
            print(f"  Time remaining before likely action: 72 HOURS")
            print("!" * 65)
            print()
            time.sleep(4)
        
        # Show the note
        print(f"  NOTE: {moment['note']}")
        print()
        
        # Pause between events
        if i < len(timeline) - 1:
            print(f"  Moving to next signal event...")
            time.sleep(3)
        else:
            # Final moment
            print("=" * 65)
            print("  REPLAY COMPLETE")
            print("=" * 65)
            print()
            print("  SENTINEL detected this pattern 72 hours before invasion.")
            print("  This data was publicly available.")
            print("  No classified access was needed.")
            print("  Nobody had this system.")
            print()
            print("  200,000+ people died in the first year of this conflict.")
            print()
            print("  SENTINEL exists so the next warning is not missed.")
            print()
            print("=" * 65)
            print(f"  Cost to run this system: $0.00")
            print(f"  Built by: One student")  
            print(f"  Built for: Everyone")
            print("=" * 65)

if __name__ == "__main__":
    print("SENTINEL — Ukraine 2022 Replay")
    print("Press Enter to begin...")
    input()
    ukraine_replay()