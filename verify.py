import requests
import json
import os
from datetime import datetime, timezone

def verify_claim(claim, regions=None):
    """
    Cross-reference a military claim against live SENTINEL signals
    Returns a credibility score and evidence breakdown
    """
    
    claim_lower = claim.lower()
    
    # Load current threat data
    if not regions:
        try:
            if os.path.exists("threat_cache.json"):
                with open("threat_cache.json", "r") as f:
                    cache = json.load(f)
                regions = cache.get("regions", [])
        except Exception:
            regions = []
    
    # Find which region this claim is about
    region_keywords = {
        "ukraine": "Ukraine-Russia",
        "russia": "Ukraine-Russia",
        "taiwan": "Taiwan-China",
        "china": "Taiwan-China",
        "israel": "Israel-Gaza-Iran",
        "iran": "Israel-Gaza-Iran",
        "gaza": "Israel-Gaza-Iran",
        "india": "India-Pakistan",
        "pakistan": "India-Pakistan",
        "kashmir": "India-Pakistan",
        "hormuz": "Yemen-Hormuz",
        "yemen": "Yemen-Hormuz",
        "sudan": "Sudan Civil War",
        "myanmar": "Myanmar Conflict",
        "sahel": "Sahel Crisis",
        "mali": "Sahel Crisis",
        "somalia": "Somalia-Ethiopia",
        "ethiopia": "Somalia-Ethiopia",
        "korea": "Korean Peninsula",
        "north korea": "Korean Peninsula",
        "pyongyang": "Korean Peninsula",
        "nato": "NATO Eastern Flank",
        "eastern europe": "NATO Eastern Flank",
        "poland": "NATO Eastern Flank",
        "baltic": "NATO Eastern Flank",
        "south china sea": "South China Sea",
        "spratly": "South China Sea",
        "paracel": "South China Sea",
        "persian gulf": "Yemen-Hormuz",
        "strait of hormuz": "Yemen-Hormuz",
        "houthi": "Yemen-Hormuz",
        "myanmar": "Myanmar Conflict",
        "burma": "Myanmar Conflict",
        "us troops": "NATO Eastern Flank",
        "american troops": "NATO Eastern Flank",
        "united states": "NATO Eastern Flank",
    }
    
    matched_region = None
    matched_key = None
    
    for keyword, region_name in region_keywords.items():
        if keyword in claim_lower:
            matched_key = keyword
            for r in regions:
                if r["country"] == region_name:
                    matched_region = r
                    break
            break
    
    # Detect claim type
    claim_types = {
        "military_movement": [
            "troops", "soldiers", "tanks", "military", "forces",
            "army", "battalion", "brigade", "regiment", "division",
            "massing", "deployment", "repositioning", "advancing"
        ],
        "aerial": [
            "aircraft", "jets", "planes", "airforce", "bombing",
            "airstrike", "drone", "missile", "helicopter", "airspace"
        ],
        "naval": [
            "ships", "navy", "naval", "fleet", "warship",
            "submarine", "carrier", "destroyer", "strait"
        ],
        "nuclear": [
            "nuclear", "atomic", "warhead", "missile", "ballistic",
            "icbm", "radiation", "detonation", "test"
        ],
        "diplomatic": [
            "meeting", "talks", "negotiation", "ceasefire",
            "agreement", "summit", "diplomat", "embassy"
        ],
        "conflict": [
            "attack", "invasion", "war", "conflict", "battle",
            "fighting", "casualties", "killed", "wounded", "shelling"
        ]
    }
    
    detected_types = []
    for claim_type, keywords in claim_types.items():
        if any(kw in claim_lower for kw in keywords):
            detected_types.append(claim_type)
    
    # Build evidence based on signals
    evidence = []
    credibility_score = 50  # Start neutral
    supporting = []
    contradicting = []
    
    if matched_region:
        signals = matched_region.get("signals", {})
        score = matched_region.get("score", 0)
        level = matched_region.get("level", "NORMAL")
        
        # News signal check
        news = signals.get("news", 0)
        if news >= 20:
            supporting.append(
                f"News/Media signal HIGH ({news}/30) — "
                f"significant conflict reporting in {matched_region['country']}"
            )
            credibility_score += 15
        elif news >= 10:
            supporting.append(
                f"News/Media signal MODERATE ({news}/30) — "
                f"some conflict reporting detected"
            )
            credibility_score += 5
        else:
            contradicting.append(
                f"News/Media signal LOW ({news}/30) — "
                f"minimal conflict reporting in region"
            )
            credibility_score -= 10
        
        # Flight signal check for aerial/military claims
        flights = signals.get("flights", 0)
        if "aerial" in detected_types or "military_movement" in detected_types:
            if flights >= 15:
                supporting.append(
                    f"Flight Activity HIGH ({flights}/20) — "
                    f"OpenSky confirms unusual aircraft activity"
                )
                credibility_score += 15
            elif flights >= 8:
                supporting.append(
                    f"Flight Activity MODERATE ({flights}/20) — "
                    f"elevated aircraft presence detected"
                )
                credibility_score += 5
            else:
                contradicting.append(
                    f"Flight Activity LOW ({flights}/20) — "
                    f"OpenSky does not confirm aerial activity"
                )
                credibility_score -= 10
        
        # Seismic check for nuclear/explosion claims
        seismic = signals.get("seismic", 0)
        if "nuclear" in detected_types or "conflict" in detected_types:
            if seismic >= 5:
                supporting.append(
                    f"Seismic Activity DETECTED ({seismic}/20) — "
                    f"USGS confirms underground activity in region"
                )
                credibility_score += 20
            else:
                contradicting.append(
                    f"Seismic Activity NONE ({seismic}/20) — "
                    f"USGS detects no unusual underground events"
                )
                credibility_score -= 5
        
        # Finance check
        finance = signals.get("finance", 0)
        if finance >= 15:
            supporting.append(
                f"Defence Stocks SURGING ({finance}/30) — "
                f"financial markets pricing in military risk"
            )
            credibility_score += 10
        elif finance >= 8:
            supporting.append(
                f"Defence Stocks ELEVATED ({finance}/30) — "
                f"some financial signal of military activity"
            )
            credibility_score += 5
        
        # ACLED check
        acled = signals.get("acled", 0)
        if acled >= 15:
            supporting.append(
                f"Armed Conflict Events HIGH ({acled}/20) — "
                f"ACLED confirms active armed incidents in region"
            )
            credibility_score += 15
        elif acled >= 8:
            supporting.append(
                f"Armed Conflict Events MODERATE ({acled}/20) — "
                f"some armed incidents detected"
            )
            credibility_score += 5
        else:
            contradicting.append(
                f"Armed Conflict Events LOW ({acled}/20) — "
                f"ACLED does not confirm significant armed activity"
            )
            credibility_score -= 5
        
        # Overall threat level bonus
        if score >= 75:
            credibility_score += 10
        elif score >= 55:
            credibility_score += 5
        elif score < 35:
            credibility_score -= 15
    
    else:
        # Region not in SENTINEL database
        contradicting.append(
            "Region not currently monitored by SENTINEL — "
            "cannot cross-reference signals"
        )
        credibility_score = 30
    
    # Cap score
    credibility_score = max(0, min(100, credibility_score))
    
    # Determine verdict
    if credibility_score >= 75:
        verdict = "LIKELY CREDIBLE"
        verdict_color = "high"
        verdict_detail = (
            "Multiple independent SENTINEL signals support this claim. "
            "Recommend further verification through official channels."
        )
    elif credibility_score >= 55:
        verdict = "PARTIALLY SUPPORTED"
        verdict_color = "elevated"
        verdict_detail = (
            "Some signals support this claim but evidence is incomplete. "
            "Treat with caution pending additional verification."
        )
    elif credibility_score >= 35:
        verdict = "INSUFFICIENT EVIDENCE"
        verdict_color = "normal"
        verdict_detail = (
            "SENTINEL signals do not strongly support or contradict this claim. "
            "Cannot determine credibility from available data."
        )
    else:
        verdict = "LOW CREDIBILITY"
        verdict_color = "normal"
        verdict_detail = (
            "SENTINEL signals do not support this claim. "
            "Multiple indicators contradict the reported activity."
        )
    
    return {
        "claim": claim,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "credibility_score": credibility_score,
        "verdict_detail": verdict_detail,
        "region": matched_region["country"] if matched_region else "Unknown",
        "region_score": matched_region["score"] if matched_region else 0,
        "region_level": matched_region["level"] if matched_region else "UNKNOWN",
        "detected_claim_types": detected_types,
        "supporting_signals": supporting,
        "contradicting_signals": contradicting,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_sources": [
            "GDELT (news)", "OpenSky (flights)",
            "USGS (seismic)", "Yahoo Finance", "ACLED"
        ]
    }


if __name__ == "__main__":
    print("SENTINEL — Claim Verification Engine")
    print("=" * 60)
    print()
    
    test_claims = [
        "Russian tanks are massing at the Ukrainian border today",
        "Iran has launched missiles at Israel",
        "North Korea conducted a nuclear test this morning",
        "Chinese naval vessels are surrounding Taiwan",
        "US troops are deploying to Eastern Europe"
    ]
    
    for claim in test_claims:
        print(f"CLAIM: {claim}")
        result = verify_claim(claim)
        print(f"VERDICT: {result['verdict']} — {result['credibility_score']}/100")
        print(f"Region: {result['region']} ({result['region_score']}/100)")
        print("Supporting:")
        for s in result['supporting_signals']:
            print(f"  ✓ {s}")
        print("Contradicting:")
        for c in result['contradicting_signals']:
            print(f"  ✗ {c}")
        print()