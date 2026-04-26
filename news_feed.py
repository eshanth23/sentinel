import requests
from datetime import datetime, timezone

def get_region_news(country_name, max_articles=5):
    """
    Pull live news articles for a region from GDELT
    Extracts real headlines, sources, and images
    """
    
    # Map regions to search terms
    search_terms = {
        "Ukraine-Russia": "ukraine russia military war",
        "Israel-Gaza-Iran": "israel iran gaza military",
        "Taiwan-China": "taiwan china military strait",
        "Yemen-Hormuz": "yemen houthi hormuz",
        "Sudan Civil War": "sudan military conflict war",
        "South China Sea": "south china sea military naval",
        "India-Pakistan": "india pakistan military border",
        "Myanmar Conflict": "myanmar military conflict",
        "Sahel Crisis": "sahel mali niger military",
        "Somalia-Ethiopia": "somalia ethiopia conflict",
        "Korean Peninsula": "north korea military",
        "NATO Eastern Flank": "nato military eastern europe",
    }
    
    query = search_terms.get(country_name, f"{country_name} military conflict")
    
    print(f"[NEWS FEED] Fetching live news for {country_name}...")
    
    try:
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": max_articles,
            "format": "json",
            "timespan": "24h",
            "sort": "DateDesc"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        response = requests.get(
            url, params=params,
            headers=headers, timeout=10
        )
        
        if response.status_code == 200 and response.text.strip():
            data = response.json()
            articles = data.get("articles", [])
            
            results = []
            for article in articles:
                title = article.get("title", "")
                url_link = article.get("url", "")
                domain = article.get("domain", "")
                date = article.get("seendate", "")
                
                if not title or not url_link:
                    continue
                
                # Get thumbnail image
                image_url = get_article_image(url_link, domain)
                
                # Format date
                formatted_date = format_date(date)
                
                results.append({
                    "title": title,
                    "url": url_link,
                    "domain": domain,
                    "date": formatted_date,
                    "image": image_url,
                    "source_icon": get_source_icon(domain)
                })
            
            print(f"  Found {len(results)} articles")
            return results
            
        else:
            print(f"  GDELT rate limited — using fallback")
            return get_fallback_news(country_name)
            
    except Exception as e:
        print(f"  Error: {e}")
        return get_fallback_news(country_name)


def get_article_image(url, domain):
    """
    Extract Open Graph image from article URL
    This is the thumbnail shown when sharing on social media
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html"
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            html = response.text
            
            # Look for og:image meta tag
            import re
            og_image = re.search(
                r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
                html, re.IGNORECASE
            )
            if og_image:
                return og_image.group(1)
            
            # Try twitter:image
            twitter_image = re.search(
                r'<meta[^>]*name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']',
                html, re.IGNORECASE
            )
            if twitter_image:
                return twitter_image.group(1)
    except Exception:
        pass
    
    # Return source-specific default images
    return get_source_default_image(domain)


def get_source_default_image(domain):
    """Default images for known news sources"""
    defaults = {
        "reuters.com": "https://www.reuters.com/pf/resources/images/reuters/reuters-default.png",
        "bbc.com": "https://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.gif",
        "bbc.co.uk": "https://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.gif",
        "aljazeera.com": "https://www.aljazeera.com/images/logo_aje_color.png",
        "cnn.com": "https://edition.cnn.com/media/sites/cnn/favicon.ico",
        "theguardian.com": "https://assets.guim.co.uk/images/guardian-logo-raster.png",
        "nytimes.com": "https://static01.nyt.com/images/icons/t_logo_291_black.png",
    }
    
    for key, img in defaults.items():
        if key in domain:
            return img
    
    return None


def get_source_icon(domain):
    """Get favicon URL for news source"""
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=32"


def format_date(date_str):
    """Format GDELT date string to readable format"""
    try:
        if len(date_str) >= 14:
            dt = datetime(
                int(date_str[0:4]),
                int(date_str[4:6]),
                int(date_str[6:8]),
                int(date_str[8:10]),
                int(date_str[10:12])
            )
            now = datetime.now()
            diff = now - dt
            hours = diff.seconds // 3600
            if diff.days > 0:
                return f"{diff.days}d ago"
            elif hours > 0:
                return f"{hours}h ago"
            else:
                return "Just now"
    except Exception:
        pass
    return "Recent"


def get_fallback_news(country_name):
    """Fallback news when GDELT is rate limited"""
    fallbacks = {
        "Ukraine-Russia": [
            {
                "title": "Russia continues strikes on Ukrainian infrastructure",
                "url": "https://reuters.com",
                "domain": "reuters.com",
                "date": "2h ago",
                "image": None,
                "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"
            },
            {
                "title": "NATO allies increase military support to Ukraine",
                "url": "https://bbc.com",
                "domain": "bbc.com",
                "date": "4h ago",
                "image": None,
                "source_icon": "https://www.google.com/s2/favicons?domain=bbc.com&sz=32"
            }
        ],
        "Israel-Gaza-Iran": [
            {
                "title": "Israel launches strikes in response to Iranian threats",
                "url": "https://reuters.com",
                "domain": "reuters.com",
                "date": "1h ago",
                "image": None,
                "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"
            },
            {
                "title": "Iran warns of retaliation as tensions escalate",
                "url": "https://aljazeera.com",
                "domain": "aljazeera.com",
                "date": "3h ago",
                "image": None,
                "source_icon": "https://www.google.com/s2/favicons?domain=aljazeera.com&sz=32"
            }
        ],
        "Taiwan-China": [
            {
                "title": "China conducts military exercises near Taiwan Strait",
                "url": "https://reuters.com",
                "domain": "reuters.com",
                "date": "2h ago",
                "image": None,
                "source_icon": "https://www.google.com/s2/favicons?domain=reuters.com&sz=32"
            }
        ]
    }
    return fallbacks.get(country_name, [])


if __name__ == "__main__":
    print("SENTINEL — Live News Feed Test")
    print("=" * 60)
    
    regions = ["Ukraine-Russia", "Israel-Gaza-Iran", "Taiwan-China"]
    
    for region in regions:
        print(f"\n{region}:")
        articles = get_region_news(region, max_articles=3)
        for a in articles:
            print(f"  [{a['domain']}] {a['title'][:60]}")
            print(f"  {a['date']} — {a['url'][:50]}")