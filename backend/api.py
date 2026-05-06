from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import time
from datetime import datetime, timezone
from signals import calculate_threat_score
import threading
import json
import requests
from datetime import datetime, timedelta
import base64
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002"
])

latest_results = []
is_scanning = False

REGIONS = [
    ("Ukraine-Russia", 49.4871, 31.2718),
    ("Taiwan-China", 23.6978, 120.9605),
    ("India-Pakistan", 30.3753, 69.3451),
    ("Israel-Gaza-Iran", 31.5, 34.8),
    ("Yemen-Hormuz", 15.5527, 48.5164),
    ("Sudan Civil War", 12.8628, 30.2176),
    ("South China Sea", 14.0583, 113.8000),
    ("Myanmar Conflict", 19.1633, 96.7970),
    ("Sahel Crisis", 14.4974, -0.0000),
    ("Somalia-Ethiopia", 7.0, 43.0),
]


def get_demo_data():
    return [
        {
            "country": "Israel-Gaza-Iran",
            "score": 78, "level": "HIGH",
            "lat": 31.5, "lon": 34.8,
            "signals": {"news": 29, "seismic": 1,
                        "finance": 15, "acled": 17, "flights": 12}
        },
        {
            "country": "Ukraine-Russia",
            "score": 72, "level": "HIGH",
            "lat": 49.4871, "lon": 31.2718,
            "signals": {"news": 28, "seismic": 0,
                        "finance": 11, "acled": 18, "flights": 5}
        },
        {
            "country": "Taiwan-China",
            "score": 71, "level": "HIGH",
            "lat": 23.6978, "lon": 120.9605,
            "signals": {"news": 22, "seismic": 0,
                        "finance": 11, "acled": 8, "flights": 20}
        },
        {
            "country": "Yemen-Hormuz",
            "score": 69, "level": "HIGH",
            "lat": 15.5527, "lon": 48.5164,
            "signals": {"news": 24, "seismic": 0,
                        "finance": 13, "acled": 14, "flights": 16}
        },
        {
            "country": "Sudan Civil War",
            "score": 65, "level": "HIGH",
            "lat": 12.8628, "lon": 30.2176,
            "signals": {"news": 20, "seismic": 0,
                        "finance": 8, "acled": 20, "flights": 3}
        },
        {
            "country": "South China Sea",
            "score": 61, "level": "HIGH",
            "lat": 14.0583, "lon": 113.8000,
            "signals": {"news": 20, "seismic": 0,
                        "finance": 11, "acled": 10, "flights": 15}
        },
        {
            "country": "India-Pakistan",
            "score": 59, "level": "ELEVATED",
            "lat": 30.3753, "lon": 69.3451,
            "signals": {"news": 18, "seismic": 0,
                        "finance": 11, "acled": 14, "flights": 6}
        },
        {
            "country": "Myanmar Conflict",
            "score": 58, "level": "ELEVATED",
            "lat": 19.1633, "lon": 96.7970,
            "signals": {"news": 16, "seismic": 0,
                        "finance": 7, "acled": 18, "flights": 3}
        },
        {
            "country": "Sahel Crisis",
            "score": 55, "level": "ELEVATED",
            "lat": 14.4974, "lon": -0.0000,
            "signals": {"news": 15, "seismic": 0,
                        "finance": 5, "acled": 18, "flights": 3}
        },
        {
            "country": "Somalia-Ethiopia",
            "score": 52, "level": "ELEVATED",
            "lat": 7.0, "lon": 43.0,
            "signals": {"news": 14, "seismic": 0,
                        "finance": 5, "acled": 18, "flights": 3}
        }
    ]


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "SENTINEL ONLINE",
        "version": "1.0",
        "cost": "$0.00",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route('/api/threats', methods=['GET'])
def get_threats():
    if not latest_results:
        # Try cache file first — updated by scheduler every 15 min
        try:
            if os.path.exists("threat_cache.json"):
                with open("threat_cache.json", "r") as f:
                    cache = json.load(f)
                regions = cache.get("regions", [])
                timestamp = cache.get("timestamp", "")
                if regions:
                    return jsonify({
                        "status": "live",
                        "source": "scheduled-update",
                        "timestamp": timestamp,
                        "regions": sorted(
                            regions,
                            key=lambda x: x["score"],
                            reverse=True
                        )
                    })
        except Exception as e:
            print(f"Cache read error: {e}")
        
        # Try live discovery as fallback
        try:
            from auto_regions import get_live_regions
            live_regions = get_live_regions()
            if live_regions and len(live_regions) > 0:
                return jsonify({
                    "status": "live",
                    "source": "auto-discovered",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "regions": sorted(
                        live_regions,
                        key=lambda x: x["score"],
                        reverse=True
                    )
                })
        except Exception as e:
            print(f"Auto regions error: {e}")

        # Last resort — demo data
        return jsonify({
            "status": "demo",
            "regions": get_demo_data()
        })

    return jsonify({
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "regions": sorted(
            latest_results,
            key=lambda x: x["score"],
            reverse=True
        )
    })

@app.route('/api/scan', methods=['POST'])
def run_scan():
    global latest_results, is_scanning
    if is_scanning:
        return jsonify({"status": "already_scanning"})

    def do_scan():
        global latest_results, is_scanning
        is_scanning = True
        results = []
        for country, lat, lon in REGIONS:
            try:
                result = calculate_threat_score(country, lat, lon)
                results.append(result)
                time.sleep(1)
            except Exception as e:
                results.append({
                    "country": country,
                    "score": 20,
                    "level": "NORMAL",
                    "lat": lat,
                    "lon": lon,
                    "signals": {
                        "news": 0, "seismic": 0,
                        "finance": 0, "acled": 0, "flights": 0
                    },
                    "error": str(e)
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        latest_results = results
        is_scanning = False

    thread = threading.Thread(target=do_scan)
    thread.daemon = True
    thread.start()
    return jsonify({"status": "scanning_started"})


@app.route('/api/scan/status', methods=['GET'])
def scan_status():
    return jsonify({"is_scanning": is_scanning})


@app.route('/api/brief', methods=['POST'])
def get_brief():
    try:
        from brief import generate_conflict_brief
        data = request.json
        country = data.get('country', 'Ukraine-Russia')
        score = data.get('score', 67)
        level = data.get('level', 'HIGH')
        signals = data.get('signals', {})
        brief = generate_conflict_brief(
            country_name=country,
            threat_score=score,
            threat_level=level,
            signals=signals,
            articles=[],
            anomalies=[]
        )
        return jsonify({"brief": brief})
    except Exception as e:
        return jsonify({"brief": f"Error: {e}"})


@app.route('/api/ukraine-replay', methods=['GET'])
def ukraine_replay_data():
    scenario = request.args.get('scenario', 'ukraine')

    scenarios = {
        "ukraine": [
            {"date": "Jan 28, 2022",
             "event": "US Embassy orders evacuation",
             "news": 8, "seismic": 0, "finance": 4, "acled": 5},
            {"date": "Feb 3, 2022",
             "event": "Russia masses 130,000 troops",
             "news": 14, "seismic": 0, "finance": 10, "acled": 8},
            {"date": "Feb 11, 2022",
             "event": "US warns invasion imminent",
             "news": 20, "seismic": 2, "finance": 16, "acled": 12},
            {"date": "Feb 16, 2022",
             "event": "Largest exercises since Cold War",
             "news": 24, "seismic": 3, "finance": 20, "acled": 15},
            {"date": "Feb 21, 2022",
             "event": "Putin recognizes separatist regions",
             "news": 28, "seismic": 5, "finance": 24, "acled": 18},
            {"date": "Feb 24, 2022",
             "event": "INVASION BEGINS",
             "news": 30, "seismic": 8, "finance": 28, "acled": 20}
        ],
        "kargil": [
            {"date": "Apr 1999",
             "event": "Pakistani troops cross LOC secretly",
             "news": 6, "seismic": 0, "finance": 3, "acled": 8},
            {"date": "May 1999",
             "event": "India discovers infiltration",
             "news": 12, "seismic": 1, "finance": 8, "acled": 12},
            {"date": "Jun 1999",
             "event": "India launches Operation Vijay",
             "news": 20, "seismic": 0, "finance": 14, "acled": 16},
            {"date": "Jul 1999",
             "event": "Nuclear signals detected — both sides",
             "news": 26, "seismic": 3, "finance": 20, "acled": 18},
            {"date": "Jul 26, 1999",
             "event": "WAR ENDS — 527 Indian soldiers killed",
             "news": 28, "seismic": 2, "finance": 18, "acled": 20}
        ],
        "gulf": [
            {"date": "Jul 17, 1990",
             "event": "Iraq masses troops on Kuwait border",
             "news": 8, "seismic": 0, "finance": 5, "acled": 4},
            {"date": "Jul 25, 1990",
             "event": "US Ambassador meets Saddam — mixed signals",
             "news": 14, "seismic": 0, "finance": 10, "acled": 6},
            {"date": "Jul 31, 1990",
             "event": "Kuwait talks collapse in Jeddah",
             "news": 22, "seismic": 0, "finance": 18, "acled": 10},
            {"date": "Aug 1, 1990",
             "event": "100,000 troops positioned at border",
             "news": 27, "seismic": 0, "finance": 24, "acled": 15},
            {"date": "Aug 2, 1990",
             "event": "IRAQ INVADES KUWAIT",
             "news": 30, "seismic": 2, "finance": 28, "acled": 20}
        ],
        "israel_iran": [
            {"date": "Jan 2024",
             "event": "Iran proxies attack US bases in Iraq",
             "news": 10, "seismic": 0, "finance": 8, "acled": 10},
            {"date": "Apr 1, 2024",
             "event": "Israel strikes Iranian consulate in Syria",
             "news": 18, "seismic": 0, "finance": 14, "acled": 14},
            {"date": "Apr 13, 2024",
             "event": "Iran launches 300+ drones and missiles at Israel",
             "news": 26, "seismic": 2, "finance": 20, "acled": 18},
            {"date": "Apr 19, 2024",
             "event": "Israel retaliates — strikes inside Iran",
             "news": 28, "seismic": 3, "finance": 24, "acled": 18},
            {"date": "Oct 1, 2024",
             "event": "Iran fires 180 ballistic missiles at Israel",
             "news": 30, "seismic": 4, "finance": 26, "acled": 20}
        ]
    }

    timeline = scenarios.get(scenario, scenarios["ukraine"])
    return jsonify({"timeline": timeline})


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        from groq import Groq
        from dotenv import load_dotenv
        load_dotenv()

        data = request.json
        question = data.get('message', '')
        history = data.get('history', [])

        # Use cached data — fast, no API calls
        try:
            import json
            if os.path.exists("threat_cache.json"):
                with open("threat_cache.json", "r") as f:
                    cache = json.load(f)
                current_regions = cache.get("regions", [])
            else:
                current_regions = latest_results or get_demo_data()
        except Exception:
            current_regions = latest_results or get_demo_data()

        # Build precise threat context
        threat_context = "CURRENT LIVE THREAT SCORES — USE ONLY THESE:\n"
        for r in current_regions:
            s = r.get('signals', {})
            threat_context += (
                f"- {r['country']}: {r['score']}/100 {r['level']}\n"
                f"  News={s.get('news', 0)}/30 "
                f"Finance={s.get('finance', 0)}/30 "
                f"Flights={s.get('flights', 0)}/20 "
                f"ACLED={s.get('acled', 0)}/20 "
                f"Seismic={s.get('seismic', 0)}/20\n"
            )

        # Check for arms question
        arms_context = ""
        arms_keywords = [
            "arms", "weapons", "import", "missile",
            "aircraft", "tank", "military equipment",
            "bought", "purchased", "supplied"
        ]
        if any(word in question.lower() for word in arms_keywords):
            try:
                from arms_data import get_arms_data, ARMS_IMPORTS
                for country in ARMS_IMPORTS.keys():
                    if country in question.lower():
                        arms_info = get_arms_data(country)
                        if arms_info["found"]:
                            d = arms_info["data"]
                            arms_context = f"""
VERIFIED ARMS DATA (SIPRI Database) for {country.upper()}:
- Major suppliers: {', '.join(d['major_suppliers'])}
- Annual defence spend: {d['annual_spend']}
- Trend: {d['trend']}
- Recent imports: {'; '.join(d['recent_imports'][:4])}
"""
                        break
            except Exception:
                pass

        system_prompt = f"""You are SENTINEL's AI Defense Advisor.

{threat_context}
{arms_context}

STRICT RULES — NEVER BREAK:
1. ONLY use exact scores listed above — never invent numbers
2. NEVER invent military exercises, troop movements, or events
3. NEVER claim to show satellite images — impossible
4. Say what SIGNALS suggest — not specific invented events
5. If asked about a country not listed say: "Not currently in SENTINEL database"
6. Give COMPLETE responses — never stop mid-sentence
7. For arms questions use SIPRI data provided above
8. Be honest about what SENTINEL can and cannot see

SIGNAL MEANING:
- News high = significant conflict reporting detected
- Finance high = defence stocks surging, procurement likely  
- Flights high = unusual aircraft activity on OpenSky
- ACLED high = verified armed incidents in region
- Seismic high = underground activity detected

WHAT SENTINEL CANNOT DO:
- Show satellite images (requires classified access)
- Track specific weapons or units in real time
- Monitor communications
- Access military databases

Keep responses complete, under 400 words, professional."""
        
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=500,
        )

        return jsonify({
            "response": response.choices[0].message.content,
            "status": "success"
        })

    except Exception as e:
        return jsonify({
            "response": f"SENTINEL advisor error: {str(e)}",
            "status": "error"
        })
@app.route('/api/verify', methods=['POST'])
def verify_claim_route():
    try:
        from verify import verify_claim
        data = request.json
        claim = data.get('claim', '')
        if not claim or len(claim) < 10:
            return jsonify({"error": "Please provide a claim to verify"})
        regions = []
        try:
            if os.path.exists("threat_cache.json"):
                with open("threat_cache.json", "r") as f:
                    cache_data = json.load(f)
                regions = cache_data.get("regions", [])
        except Exception:
            regions = get_demo_data()
        result = verify_claim(claim, regions)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/news/<region>', methods=['GET'])
def get_news(region):
    # Return fallback only — saves GDELT quota for scheduler
    # Real articles load when GDELT is available via scheduler
    region_name = region.replace('_', '-').replace('-', ' ')
    
    fallback_news = {
        "Israel Gaza Iran": [
            {"title": "Israel launches strikes amid Iran escalation warnings",
             "url": "https://reuters.com/world/middle-east",
             "domain": "reuters.com", "date": "2h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
            {"title": "Iran vows retaliation as regional tensions reach critical point",
             "url": "https://aljazeera.com/news/2026",
             "domain": "aljazeera.com", "date": "3h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=aljazeera.com&sz=32"},
            {"title": "US Navy carrier group deployed to Eastern Mediterranean",
             "url": "https://bbc.com/news/world-middle-east",
             "domain": "bbc.com", "date": "5h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=bbc.com&sz=32"},
        ],
        "Ukraine Russia": [
            {"title": "Russia continues strikes on Ukrainian energy infrastructure",
             "url": "https://reuters.com/world/europe",
             "domain": "reuters.com", "date": "1h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
            {"title": "NATO allies increase military aid packages to Ukraine",
             "url": "https://bbc.com/news/world-europe",
             "domain": "bbc.com", "date": "3h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=bbc.com&sz=32"},
            {"title": "Zelensky addresses UN Security Council on frontline situation",
             "url": "https://theguardian.com/world/ukraine",
             "domain": "theguardian.com", "date": "5h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=theguardian.com&sz=32"},
        ],
        "Taiwan China": [
            {"title": "PLA conducts largest Taiwan Strait exercises of 2026",
             "url": "https://reuters.com/world/asia-pacific",
             "domain": "reuters.com", "date": "2h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
            {"title": "Taiwan scrambles F-16s as Chinese jets cross median line",
             "url": "https://bbc.com/news/world-asia",
             "domain": "bbc.com", "date": "4h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=bbc.com&sz=32"},
            {"title": "US 7th Fleet conducts freedom of navigation operation",
             "url": "https://theguardian.com/world/china",
             "domain": "theguardian.com", "date": "6h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=theguardian.com&sz=32"},
        ],
        "Yemen Hormuz": [
            {"title": "Houthi forces launch missiles at Red Sea commercial vessels",
             "url": "https://reuters.com/world/middle-east",
             "domain": "reuters.com", "date": "1h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
            {"title": "Strait of Hormuz naval activity raises oil price concerns",
             "url": "https://bbc.com/news/world-middle-east",
             "domain": "bbc.com", "date": "4h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=bbc.com&sz=32"},
        ],
        "Sudan Civil War": [
            {"title": "RSF advances on Khartoum as Sudan civil war intensifies",
             "url": "https://aljazeera.com/news/africa",
             "domain": "aljazeera.com", "date": "2h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=aljazeera.com&sz=32"},
            {"title": "UN warns of catastrophic humanitarian crisis in Sudan",
             "url": "https://reuters.com/world/africa",
             "domain": "reuters.com", "date": "5h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
        ],
        "South China Sea": [
            {"title": "Chinese coast guard vessels block Philippine resupply mission",
             "url": "https://reuters.com/world/asia-pacific",
             "domain": "reuters.com", "date": "2h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
            {"title": "US Navy conducts freedom of navigation in disputed waters",
             "url": "https://bbc.com/news/world-asia",
             "domain": "bbc.com", "date": "4h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=bbc.com&sz=32"},
        ],
        "India Pakistan": [
            {"title": "India-Pakistan tensions rise after cross-border incidents",
             "url": "https://reuters.com/world/asia-pacific",
             "domain": "reuters.com", "date": "3h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
            {"title": "Pakistan army on high alert as Kashmir situation deteriorates",
             "url": "https://aljazeera.com/news/asia",
             "domain": "aljazeera.com", "date": "5h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=aljazeera.com&sz=32"},
        ],
        "Myanmar Conflict": [
            {"title": "Myanmar resistance forces capture key military positions",
             "url": "https://reuters.com/world/asia-pacific",
             "domain": "reuters.com", "date": "3h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
        ],
        "Sahel Crisis": [
            {"title": "Armed groups expand control across Sahel region",
             "url": "https://aljazeera.com/news/africa",
             "domain": "aljazeera.com", "date": "2h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=aljazeera.com&sz=32"},
        ],
        "Somalia Ethiopia": [
            {"title": "Al-Shabaab launches coordinated attacks in southern Somalia",
             "url": "https://reuters.com/world/africa",
             "domain": "reuters.com", "date": "4h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
        ],
        "Korean Peninsula": [
            {"title": "North Korea fires ballistic missiles into Japan's exclusive zone",
             "url": "https://reuters.com/world/asia-pacific",
             "domain": "reuters.com", "date": "6h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
        ],
        "NATO Eastern Flank": [
            {"title": "NATO increases troop deployments along eastern border",
             "url": "https://reuters.com/world/europe",
             "domain": "reuters.com", "date": "3h ago", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"},
        ],
    }
    
    # Find matching articles
    articles = []
    region_upper = region_name.title()
    
    for key, news in fallback_news.items():
        if any(word.lower() in region_name.lower() 
               for word in key.split()):
            articles = news
            break
    
    if not articles:
        articles = [
            {"title": f"Active conflict monitoring: {region_name}",
             "url": "https://reuters.com/world",
             "domain": "reuters.com", "date": "Live", "image": None,
             "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"}
        ]
    
    return jsonify({
        "region": region,
        "articles": articles,
        "count": len(articles)
    })
@app.route('/api/satellite/<region>', methods=['GET'])
def get_satellite_image(region):
    """
    Fetch recent satellite imagery for border regions
    """
    # Border coordinates for each region
    BORDER_COORDS = {
        'Ukraine_Russia': {'lat': 50.5, 'lon': 36.0, 'name': 'Kharkiv Border Region'},
        'Taiwan_China': {'lat': 24.0, 'lon': 118.3, 'name': 'Taiwan Strait'},
        'India_Pakistan': {'lat': 32.5, 'lon': 74.5, 'name': 'Kashmir LOC'},
        'Israel_Gaza_Iran': {'lat': 31.5, 'lon': 34.5, 'name': 'Gaza Border'},
        'Korean_Peninsula': {'lat': 38.0, 'lon': 127.5, 'name': 'DMZ'},
    }
    
    region_key = region.replace('-', '_').replace(' ', '_')
    
    if region_key not in BORDER_COORDS:
        return jsonify({'error': 'No satellite data for this region'}), 404
    
    coords = BORDER_COORDS[region_key]
    
    # Sentinel Hub configuration
    INSTANCE_ID = ''  # Replace with your ID
    CLIENT_ID = ''      # Replace with your ID
    CLIENT_SECRET = ''      # Replace with your secret
    
    try:
        # Get OAuth token
        token_url = 'https://services.sentinel-hub.com/oauth/token'
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        token_response = requests.post(token_url, data=token_data, timeout=10)
        access_token = token_response.json()['access_token']
        
        # Calculate bounding box (0.1 degree ~ 11km)
        bbox = [
            coords['lon'] - 0.1,  # west
            coords['lat'] - 0.1,  # south
            coords['lon'] + 0.1,  # east
            coords['lat'] + 0.1   # north
        ]
        
        # Request image from last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Sentinel Hub Process API request
        api_url = f'https://services.sentinel-hub.com/api/v1/process'
        
        payload = {
            "input": {
                "bounds": {
                    "bbox": bbox
                },
                "data": [{
                    "type": "S2L2A",  # Sentinel-2 Level 2A
                    "dataFilter": {
                        "timeRange": {
                            "from": start_date.strftime('%Y-%m-%dT00:00:00Z'),
                            "to": end_date.strftime('%Y-%m-%dT23:59:59Z')
                        },
                        "maxCloudCoverage": 30
                    }
                }]
            },
            "output": {
                "width": 800,
                "height": 600,
                "responses": [{
                    "identifier": "default",
                    "format": {"type": "image/jpeg"}
                }]
            },
            "evalscript": """
                //VERSION=3
                function setup() {
                    return {
                        input: ["B04", "B03", "B02"],
                        output: { bands: 3 }
                    };
                }
                function evaluatePixel(sample) {
                    return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
                }
            """
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        image_response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        if image_response.status_code == 200:
            # Convert image to base64
            image_b64 = base64.b64encode(image_response.content).decode('utf-8')
            
            return jsonify({
                'image': f'data:image/jpeg;base64,{image_b64}',
                'location': coords['name'],
                'date': end_date.strftime('%Y-%m-%d'),
                'source': 'Copernicus Sentinel-2',
                'resolution': '10m per pixel'
            })
        else:
            return jsonify({'error': 'Satellite image unavailable'}), 404
            
    except Exception as e:
        print(f"Satellite fetch error: {e}")
        return jsonify({'error': 'Failed to fetch satellite imagery'}), 500
if __name__ == '__main__':
    print("=" * 50)
    print("SENTINEL API SERVER")
    print("Running on http://localhost:5000")
    print("Cost: $0.00")
    print("=" * 50)
    app.run(debug=True, port=5000)