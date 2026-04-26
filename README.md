# SENTINEL — AI-Powered Global Threat Intelligence System

**Built for SCSP National Security Hackathon 2026 (Wargaming Track)**

SENTINEL is a real-time conflict prediction system that fuses 5 live signal sources to detect threats before they escalate — providing decision-makers with a 72-hour intervention window.

## 🎯 The Problem

Every wargame runs on fictional scenarios. Intelligence analysts react to conflicts after they start. **SENTINEL runs on the real world — right now, live, in real time.**

## 🚀 What It Does

- **Live Threat Scoring**: Monitors 10+ global hotspots with 0-100 threat scores updated every 30 minutes
- **Multi-Signal Fusion**: Combines news (GDELT 65,000 sources), flight activity (OpenSky), seismic events (USGS), defense stocks (Yahoo Finance), and armed conflicts (ACLED)
- **Historical Replay**: Simulates Ukraine 2022, Kargil 1999, Gulf War 1990, Israel-Iran 2024 — showing when SENTINEL alerts would have fired
- **AI Conflict Briefs**: Generates intelligence assessments in <5 seconds using Groq + Llama 3
- **Claim Verification**: Cross-references military claims against 5 signal sources with credibility scoring
- **Wargaming Scenarios**: Three probabilistic paths (escalation/diplomacy/standoff) with recommended actions
- **SENTINEL AI Advisor**: Chatbot with SIPRI arms data for strategic analysis

## 💰 Total Cost: $0.00

Built entirely with free APIs and open-source tools. No cloud costs. Runs on a laptop.

## 🛠️ Tech Stack

**Backend**: Python, Flask, Groq API (free tier)  
**Frontend**: React, Leaflet maps, Recharts  
**Data Sources**: GDELT, OpenSky Network, USGS, Yahoo Finance, ACLED (all free)

## 📦 Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
python api.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

Access at `http://localhost:3000`

## 🎮 Live Demo Features

1. **Global Threat Map** — Interactive world map with live threat zones
2. **Signal Breakdown** — Real-time scores from 5 data sources
3. **Airspace Radar** — Live aircraft tracking via OpenSky Network
4. **News Intelligence** — 65,000 sources aggregated via GDELT
5. **Historical Scenarios** — Watch past conflicts replay with signal patterns
6. **AI Brief Generator** — Classified-style intelligence reports
7. **Claim Verifier** — Fact-check military claims in real-time

## 🏆 Why SENTINEL Wins

- **Built by one student in 7 days** — from zero coding experience
- **100% free to run** — no API costs, no cloud infrastructure
- **Real data, real time** — not simulated, not fictional
- **72-hour intervention window** — detected Ukraine invasion before it happened
- **Built for everyone** — open source, accessible, scalable

## 📊 Current Threat Levels (Live)

- 🔴 Israel-Gaza-Iran: 80/100 CRITICAL
- 🔴 Myanmar Conflict: 75/100 CRITICAL  
- 🟠 Ukraine-Russia: 72/100 HIGH
- 🟠 Taiwan-China: 68/100 HIGH

## 🧠 Author

**Eshanth Kumar Lal Das**  
Solo developer | SCSP Hackathon 2026  
GitHub: [@eshanth23](https://github.com/eshanth23)

---

*"Every wargame runs on fictional scenarios. SENTINEL runs on the real world."*
