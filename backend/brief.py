import os
from groq import Groq
from dotenv import load_dotenv
import json
from datetime import datetime, timezone

# Load API key from .env file
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_conflict_brief(country_name, threat_score, threat_level, signals, articles, anomalies):
    """
    Generate a real intelligence brief using AI
    Fed by SENTINEL's live signal data
    """
    
    print()
    print("=" * 60)
    print("SENTINEL — AI CONFLICT BRIEF GENERATOR")
    print("=" * 60)
    print(f"Generating brief for: {country_name}")
    print("Powered by: Groq (free) + Llama 3")
    print("Cost: $0.00")
    print()
    
    # Build context from our real signals
    signal_context = f"""
SENTINEL SIGNAL DATA — {country_name}
Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

THREAT SCORE: {threat_score}/100
THREAT LEVEL: {threat_level}

SIGNAL BREAKDOWN:
- News/Media signals: {signals['news']}/30
- Seismic activity: {signals['seismic']}/20  
- Defence stock anomalies: {signals['finance']}/30
- Armed conflict events (ACLED): {signals.get('acled', 'N/A')}/20

FINANCIAL ANOMALIES DETECTED:
{json.dumps(anomalies, indent=2) if anomalies else "No significant anomalies"}

RECENT NEWS ARTICLES:
{chr(10).join([f"- {a.get('title', 'N/A')} ({a.get('domain', 'N/A')})" for a in articles[:3]]) if articles else "Using baseline intelligence data"}
"""

    # The prompt that turns data into intelligence
    prompt = f"""You are SENTINEL, an AI-powered pre-conflict intelligence system. 
You have just detected elevated threat signals for {country_name}.

Based on the following real signal data, generate a concise military intelligence brief 
in the style of a classified threat assessment. Be specific, analytical, and professional.

{signal_context}

Generate a brief with these exact sections:

SITUATION SUMMARY (2-3 sentences on current threat status)

KEY INDICATORS (bullet points of what signals are elevated and why they matter)

HISTORICAL PATTERN MATCH (which past conflict does this most closely resemble and why)

SCENARIO ASSESSMENT:
- Path A — Escalation (probability % and what triggers it)
- Path B — De-escalation (probability % and what prevents conflict)  
- Path C — Frozen standoff (probability % and timeline)

RECOMMENDED ACTIONS (what decision makers should do in the next 72 hours)

CONFIDENCE LEVEL: (Low/Medium/High and why)

Keep the entire brief under 400 words. Write like a real intelligence analyst."""

    try:
        # Call Groq API - completely free
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are SENTINEL, a professional military intelligence AI system. You generate concise, analytical threat assessments based on real signal data. Your briefs are used by decision makers to prevent conflict."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],model="llama-3.1-8b-instant",
            
            temperature=0.3,  # Low temperature = more focused, less random
            max_tokens=600,
        )
        
        brief = chat_completion.choices[0].message.content
        
        print("=" * 60)
        print("CLASSIFIED — SENTINEL INTELLIGENCE BRIEF")
        print("=" * 60)
        print(brief)
        print("=" * 60)
        print(f"Brief generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        print("=" * 60)
        
        return brief
        
    except Exception as e:
        print(f"ERROR generating brief: {e}")
        print("Check your GROQ_API_KEY in .env file")
        return None


def generate_ukraine_2022_brief():
    """
    Special demo brief for Ukraine 2022 historical replay
    This is your jaw-drop moment in the demo
    """
    
    signals = {
        "news": 28,
        "seismic": 5,
        "finance": 24,
        "acled": 18
    }
    
    articles = [
        {"title": "Russia masses 130,000 troops on Ukraine border", "domain": "reuters.com"},
        {"title": "NATO warns of imminent Russian invasion", "domain": "bbc.com"},
        {"title": "Ukraine declares state of emergency", "domain": "theguardian.com"}
    ]
    
    anomalies = [
        {"stock": "LMT", "name": "Lockheed Martin", "volume_ratio": 3.2, "price_change": 8.4},
        {"stock": "RTX", "name": "Raytheon", "volume_ratio": 2.8, "price_change": 6.1},
        {"stock": "NOC", "name": "Northrop Grumman", "volume_ratio": 2.5, "price_change": 5.8}
    ]
    
    print()
    print("!" * 60)
    print("UKRAINE 2022 HISTORICAL REPLAY")
    print("Date: February 21, 2022 — 72 hours before invasion")
    print("!" * 60)
    
    return generate_conflict_brief(
        country_name="Ukraine-Russia Border",
        threat_score=79,
        threat_level="CRITICAL",
        signals=signals,
        articles=articles,
        anomalies=anomalies
    )


# ============================================================
# MAIN — Test the brief generator
# ============================================================

if __name__ == "__main__":
    
    print("SENTINEL — AI BRIEF GENERATOR TEST")
    print()
    print("Choose what to generate:")
    print("1. Live brief for Ukraine-Russia (current signals)")
    print("2. Historical replay — Ukraine February 2022")
    print()
    
    choice = input("Enter 1 or 2: ").strip()
    
    if choice == "2":
        # The demo moment
        generate_ukraine_2022_brief()
        
    else:
        # Live current brief
        # Use the signals from our last run
        signals = {
            "news": 28,
            "seismic": 0,
            "finance": 11,
            "acled": 18
        }
        
        articles = [
            {"title": "Russia-Ukraine conflict continues", "domain": "reuters.com"},
            {"title": "NATO expands eastern presence", "domain": "bbc.com"}
        ]
        
        anomalies = [
            {"stock": "LMT", "name": "Lockheed Martin", 
             "volume_ratio": 1.5, "price_change": -2.5},
            {"stock": "BA", "name": "Boeing", 
             "volume_ratio": 1.4, "price_change": 2.1}
        ]
        
        generate_conflict_brief(
            country_name="Ukraine-Russia Border",
            threat_score=67,
            threat_level="HIGH",
            signals=signals,
            articles=articles,
            anomalies=anomalies
        )