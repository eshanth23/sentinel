# SIPRI verified arms transfer data — publicly available
# Source: sipri.org/databases/armstransfers
# Updated annually — 2024 data

ARMS_IMPORTS = {
    "india": {
        "major_suppliers": ["Russia (32%)", "France (29%)", "USA (11%)"],
        "recent_imports": [
            "36 Rafale fighter jets from France (2022-2024)",
            "S-400 air defence systems from Russia (2021)",
            "MH-60R Seahawk helicopters from USA (2023)",
            "P-8I Poseidon maritime patrol aircraft from USA",
            "AH-64E Apache attack helicopters from USA"
        ],
        "annual_spend": "$13.7 billion (2023)",
        "trend": "Increasing — up 4.7% from 2022"
    },
    "pakistan": {
        "major_suppliers": ["China (77%)", "USA (8%)", "Turkey (5%)"],
        "recent_imports": [
            "J-10C fighter jets from China (2022)",
            "Type 054A/P frigates from China (2022-2024)",
            "PL-15 air-to-air missiles from China",
            "TB2 Bayraktar drones from Turkey (2023)",
            "HQ-9/P air defence systems from China"
        ],
        "annual_spend": "$1.7 billion (2023)",
        "trend": "Stable — heavily China dependent"
    },
    "china": {
        "major_suppliers": ["Domestic (95%)", "Russia (4%)"],
        "recent_imports": [
            "Su-35 fighter jets from Russia (residual deliveries)",
            "S-400 components from Russia",
            "Domestic J-20 stealth fighters — 200+ operational",
            "Type 003 carrier Fujian — commissioned 2024",
            "DF-41 ICBM deployments — multiple brigades"
        ],
        "annual_spend": "$224 billion defence budget (2024)",
        "trend": "Rapidly expanding domestic production"
    },
    "russia": {
        "major_suppliers": ["Domestic (99%)"],
        "recent_imports": [
            "North Korean artillery shells — 2-3 million rounds (2023-2024)",
            "Iranian Shahed drones — 2000+ imported",
            "Chinese dual-use components for weapons systems",
            "Domestic T-90M tanks — accelerated production",
            "Kinzhal hypersonic missiles — expanded deployment"
        ],
        "annual_spend": "$109 billion (2024 wartime budget)",
        "trend": "Wartime surge — North Korea and Iran supplying"
    },
    "ukraine": {
        "major_suppliers": ["USA (40%)", "Germany (13%)", "UK (10%)"],
        "recent_imports": [
            "F-16 fighter jets from Netherlands and Denmark (2024)",
            "ATACMS long-range missiles from USA (2024)",
            "Patriot air defence systems from USA and Germany",
            "Leopard 2 tanks from Germany and Poland",
            "HIMARS rocket systems — 38 units from USA"
        ],
        "annual_spend": "Receiving $75B+ in military aid (2022-2024)",
        "trend": "Entirely dependent on Western support"
    },
    "israel": {
        "major_suppliers": ["USA (69%)", "Germany (30%)"],
        "recent_imports": [
            "F-35I Adir stealth fighters — 50 delivered",
            "GBU-28 bunker buster bombs from USA (2024)",
            "KC-46 tanker aircraft from USA",
            "Iron Dome interceptors — domestic + US funded",
            "Arrow 3 anti-ballistic system — co-developed with USA"
        ],
        "annual_spend": "$23.6 billion (2024 wartime budget)",
        "trend": "Surge due to Gaza conflict and Iran threat"
    },
    "iran": {
        "major_suppliers": ["Domestic (80%)", "Russia (15%)", "China (5%)"],
        "recent_imports": [
            "Su-35 fighter jets from Russia — delivery ongoing",
            "Yak-130 trainer jets from Russia (2023)",
            "S-300 air defence — Russian supplied",
            "Domestic Shahed drones — exporting to Russia",
            "Domestic Fateh-110 ballistic missiles — operational"
        ],
        "annual_spend": "$10.3 billion (2023)",
        "trend": "Expanding domestic production, Russia partnership"
    },
    "taiwan": {
        "major_suppliers": ["USA (100%)"],
        "recent_imports": [
            "F-16V Viper upgrades — 141 aircraft",
            "M1A2T Abrams tanks — 108 ordered",
            "Harpoon coastal defence missiles — 100 batteries",
            "HIMARS rocket systems — 29 ordered",
            "Stinger MANPADS — 250 launchers"
        ],
        "annual_spend": "$19.1 billion (2024 — record high)",
        "trend": "Rapidly increasing — responding to China threat"
    },
    "saudi arabia": {
        "major_suppliers": ["USA (73%)", "UK (13%)", "France (5%)"],
        "recent_imports": [
            "F-15SA Eagle II fighters — 84 units",
            "THAAD air defence system from USA",
            "Patriot PAC-3 missiles from USA",
            "AH-64E Apache helicopters from USA",
            "Typhoon fighter jets from UK"
        ],
        "annual_spend": "$75.8 billion (2023)",
        "trend": "World's 5th largest defence spender"
    },
    "north korea": {
        "major_suppliers": ["Domestic (95%)", "Russia (5%)"],
        "recent_imports": [
            "Russian technology transfers — ballistic missile guidance",
            "Domestic Hwasong-18 ICBM — solid fuel operational",
            "KN-25 600mm MLRS — exporting to Russia",
            "Domestic submarine-launched ballistic missiles",
            "Nuclear warhead miniaturization — claimed operational"
        ],
        "annual_spend": "Unknown — estimated $4B (25% of GDP)",
        "trend": "Accelerating — partnering with Russia"
    }
}

def get_arms_data(country_name):
    """Get verified arms import data for a country"""
    name_lower = country_name.lower()
    
    for key, data in ARMS_IMPORTS.items():
        if key in name_lower or name_lower in key:
            return {
                "country": country_name,
                "found": True,
                "data": data
            }
    
    return {
        "country": country_name,
        "found": False,
        "message": "Detailed arms data not available for this region in SIPRI database"
    }

if __name__ == "__main__":
    # Test
    for country in ["india", "russia", "taiwan", "iran"]:
        data = get_arms_data(country)
        print(f"\n{data['country'].upper()}")
        if data["found"]:
            print(f"  Suppliers: {', '.join(data['data']['major_suppliers'])}")
            print(f"  Spend: {data['data']['annual_spend']}")
            print(f"  Recent: {data['data']['recent_imports'][0]}")