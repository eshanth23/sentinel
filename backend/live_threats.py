import requests
import time
from datetime import datetime, timezone

def get_live_threats():
    """
    Pull live conflict threats entirely from GDELT
    No predefined regions — wherever conflict news is
    happening right now becomes a threat card
    """
    print("[LIVE THREATS] Scanning global news for active conflicts...")

    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": "military attack conflict war explosion missile strike killed",
        "mode": "artlist",
        "maxrecords": 50,
        "format": "json",
        "timespan": "24h",
        "sort": "toneasc"  # Most negative tone first = most conflict
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # World locations with coordinates
    # This covers every country and region on earth
    world_locations = {
        # Active war zones
        "gaza": {"lat": 31.3547, "lon": 34.3088, "region": "Gaza Strip"},
        "ukraine": {"lat": 49.4871, "lon": 31.2718, "region": "Ukraine"},
        "russia": {"lat": 55.7558, "lon": 37.6173, "region": "Russia"},
        "israel": {"lat": 31.7683, "lon": 35.2137, "region": "Israel"},
        "iran": {"lat": 35.6892, "lon": 51.3890, "region": "Iran"},
        "syria": {"lat": 34.8021, "lon": 38.9968, "region": "Syria"},
        "yemen": {"lat": 15.5527, "lon": 48.5164, "region": "Yemen"},
        "sudan": {"lat": 12.8628, "lon": 30.2176, "region": "Sudan"},
        "myanmar": {"lat": 19.1633, "lon": 96.7970, "region": "Myanmar"},
        "somalia": {"lat": 5.1521, "lon": 46.1996, "region": "Somalia"},
        "iraq": {"lat": 33.2232, "lon": 43.6793, "region": "Iraq"},
        "lebanon": {"lat": 33.8547, "lon": 35.8623, "region": "Lebanon"},
        "pakistan": {"lat": 30.3753, "lon": 69.3451, "region": "Pakistan"},
        "afghanistan": {"lat": 33.9391, "lon": 67.7100, "region": "Afghanistan"},
        "kashmir": {"lat": 34.0837, "lon": 74.7973, "region": "Kashmir"},
        "taiwan": {"lat": 23.6978, "lon": 120.9605, "region": "Taiwan Strait"},
        "hormuz": {"lat": 26.5667, "lon": 56.2500, "region": "Strait of Hormuz"},
        "south china sea": {"lat": 14.0583, "lon": 113.8000, "region": "South China Sea"},
        "mali": {"lat": 17.5707, "lon": -3.9962, "region": "Mali"},
        "nigeria": {"lat": 9.0820, "lon": 8.6753, "region": "Nigeria"},
        "ethiopia": {"lat": 9.1450, "lon": 40.4897, "region": "Ethiopia"},
        "libya": {"lat": 26.3351, "lon": 17.2283, "region": "Libya"},
        "sahel": {"lat": 14.4974, "lon": -0.0000, "region": "Sahel Region"},
        "burkina": {"lat": 12.3641, "lon": -1.5275, "region": "Burkina Faso"},
        "haiti": {"lat": 18.9712, "lon": -72.2852, "region": "Haiti"},
        "venezuela": {"lat": 6.4238, "lon": -66.5897, "region": "Venezuela"},
        "colombia": {"lat": 4.5709, "lon": -74.2973, "region": "Colombia"},
        "mexico": {"lat": 23.6345, "lon": -102.5528, "region": "Mexico"},
        "myanmar": {"lat": 19.1633, "lon": 96.7970, "region": "Myanmar"},
        "azerbaijan": {"lat": 40.1431, "lon": 47.5769, "region": "Azerbaijan"},
        "korea": {"lat": 37.5665, "lon": 126.9780, "region": "Korean Peninsula"},
        "nato": {"lat": 52.2297, "lon": 21.0122, "region": "NATO Eastern Flank"},
        "china": {"lat": 35.8617, "lon": 104.1954, "region": "China"},
        "india": {"lat": 20.5937, "lon": 78.9629, "region": "India"},
        "philippines": {"lat": 12.8797, "lon": 121.7740, "region": "Philippines"},
        "indonesia": {"lat": -0.7893, "lon": 113.9213, "region": "Indonesia"},
        "bangladesh": {"lat": 23.6850, "lon": 90.3563, "region": "Bangladesh"},
        "serbia": {"lat": 44.0165, "lon": 21.0059, "region": "Serbia"},
        "kosovo": {"lat": 42.6026, "lon": 20.9030, "region": "Kosovo"},
        "georgia": {"lat": 42.3154, "lon": 43.3569, "region": "Georgia"},
        "armenia": {"lat": 40.0691, "lon": 45.0382, "region": "Armenia"},
        "egypt": {"lat": 26.8206, "lon": 30.8025, "region": "Egypt"},
        "saudi": {"lat": 23.8859, "lon": 45.0792, "region": "Saudi Arabia"},
        "turkey": {"lat": 38.9637, "lon": 35.2433, "region": "Turkey"},
        "algeria": {"lat": 28.0339, "lon": 1.6596, "region": "Algeria"},
        "tunisia": {"lat": 33.8869, "lon": 9.5375, "region": "Tunisia"},
        "morocco": {"lat": 31.7917, "lon": -7.0926, "region": "Morocco"},
        "senegal": {"lat": 14.4974, "lon": -14.4524, "region": "Senegal"},
        "cameroon": {"lat": 7.3697, "lon": 12.3547, "region": "Cameroon"},
        "congo": {"lat": -4.0383, "lon": 21.7587, "region": "DR Congo"},
        "mozambique": {"lat": -18.6657, "lon": 35.5296, "region": "Mozambique"},
        "zimbabwe": {"lat": -19.0154, "lon": 29.1549, "region": "Zimbabwe"},
        "kenya": {"lat": -0.0236, "lon": 37.9062, "region": "Kenya"},
        "tanzania": {"lat": -6.3690, "lon": 34.8888, "region": "Tanzania"},
    }

    try:
        response = requests.get(
            url, params=params, headers=headers, timeout=15
        )

        threats = {}

        if response.status_code == 200 and response.text.strip():
            data = response.json()
            articles = data.get("articles", [])

            for article in articles:
                title = article.get("title", "")
                title_lower = title.lower()
                domain = article.get("domain", "unknown")
                date = article.get("seendate", "")
                url_link = article.get("url", "")

                # Find which location this article is about
                for keyword, loc in world_locations.items():
                    if keyword in title_lower:
                        region = loc["region"]

                        if region not in threats:
                            threats[region] = {
                                "region": region,
                                "lat": loc["lat"],
                                "lon": loc["lon"],
                                "articles": [],
                                "article_count": 0
                            }

                        threats[region]["articles"].append({
                            "title": title[:100],
                            "source": domain,
                            "date": date,
                            "url": url_link
                        })
                        threats[region]["article_count"] += 1
                        break

        # Convert to scored threat list
        threat_list = []

        for region, data in threats.items():
            count = data["article_count"]

            # Score based on article volume
            # More articles = more conflict activity = higher score
            base = 20
            news_score = min(count * 4, 35)
            total = min(base + news_score, 100)

            if total >= 75:
                level = "CRITICAL"
            elif total >= 55:
                level = "HIGH"
            elif total >= 35:
                level = "ELEVATED"
            else:
                level = "NORMAL"

            threat_list.append({
                "country": region,
                "region": region,
                "lat": data["lat"],
                "lon": data["lon"],
                "score": total,
                "level": level,
                "article_count": count,
                "latest_headline": data["articles"][0]["title"] if data["articles"] else "",
                "source": data["articles"][0]["source"] if data["articles"] else "",
                "signals": {
                    "news": news_score,
                    "seismic": 0,
                    "finance": 0,
                    "acled": 0,
                    "flights": 0
                }
            })

        # Sort by score
        threat_list.sort(key=lambda x: x["score"], reverse=True)

        print(f"  Detected {len(threat_list)} active conflict zones from live news")
        return threat_list

    except Exception as e:
        print(f"  ERROR: {e}")
        return []


if __name__ == "__main__":
    print("SENTINEL — Live Threat Detection")
    print("=" * 60)
    threats = get_live_threats()
    print()
    for t in threats:
        print(f"  {t['region']:<25} {t['score']:3}/100 {t['level']:<10} ({t['article_count']} articles)")
        print(f"  Latest: {t['latest_headline'][:60]}")
        print()
        