import requests
import json

print("=" * 50)
print("SENTINEL — LIVE CONFLICT DATA TEST")
print("=" * 50)
print()
print("Connecting to GDELT global event database...")
print()

url = "https://api.gdeltproject.org/api/v2/doc/doc"

params = {
    "query": "military conflict",
    "mode": "artlist",
    "maxrecords": 5,
    "format": "json"
}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if "articles" in data:
        articles = data["articles"]
        print(f"SUCCESS — {len(articles)} live events detected")
        print()
        for i, article in enumerate(articles):
            print(f"EVENT {i+1}")
            print(f"  Title   : {article.get('title', 'N/A')}")
            print(f"  Country : {article.get('sourcecountry', 'N/A')}")
            print(f"  Source  : {article.get('domain', 'N/A')}")
            print(f"  Time    : {article.get('seendate', 'N/A')}")
            print()
    else:
        print("Connected. Raw response:")
        print(json.dumps(data, indent=2)[:500])

except Exception as e:
    print(f"ERROR: {e}")

print("=" * 50)
print("SENTINEL is alive.")
print("=" * 50)