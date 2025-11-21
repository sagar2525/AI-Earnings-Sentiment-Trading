# AI-Earnings-Sentiment-Trading
The AI-Powered Earnings Sentiment Trading System is an automated pipeline that monitors NSE/BSE corporate announcements, downloads quarterly results PDFs in real time, extracts key financial metrics using an AI model, performs sentiment analysis, and executes trades automatically based on the results.

This project is part of an end-to-end AI Trading Automation Suite that integrates Python, n8n workflows, a Google Cloud VM, and broker APIs.

🚀 Key Features
1. Real-Time NSE/BSE Monitoring

Continuously checks for new Board Meeting Outcome result PDFs.

Detects companies scheduled to release quarterly results.

2. Automatic PDF Downloading

Saves PDFs instantly when an announcement is published.

Stores structured directories for organized data.

3. AI-Powered PDF Parsing

Uses a Large Language Model (LLM) to extract:

Revenue (QoQ & YoY)

Profit (QoQ & YoY)

EBITDA

Margins

Additional financial metrics

Handles inconsistent PDF formatting using natural language extraction.

4. Sentiment Classification

Compares extracted values with broker estimates.

Tags the earnings result as:

Positive

Negative

Neutral

5. Automated Trade Execution

Uses broker APIs to place trades based on sentiment.

Implements:

Position sizing

Risk and reward calculations

Auto sell on Target/Stop Loss/Timeout

Real-time monitoring

6. Logging & Analytics

Stores parsed results

Saves trade logs for backtesting

Maintains a history of processed companies

7. Deployment Ready

Fully containerized (Docker)

Runs on Google Cloud VM (Compute Engine)

Supports background execution using tmux


NSE/BSE Announcements  
        │
        ▼
Watcher Script (Python + Watchdog)
        │
        ▼
Download PDF → Save Directory  
        │
        ▼
AI PDF Parser (LLM Model)
        │
        ▼
Extracted Values → Sentiment Engine  
        │
        ▼
Trade Decision Logic (SL / TGT / Risk)  
        │
        ▼
Broker API → Auto Buy/Sell  
        │
        ▼
Logs & Backtesting Storage



🛠 Tech Stack

Python 3.10+

Google Cloud VM (Ubuntu)

n8n workflow automation

LLM-based PDF extraction (Gemini / custom model)

Yahoo Finance (live data)

Watchdog (filesystem events)

Docker

Cron / scheduled jobs

*📁 Directory Structure*
project/
│── downloads/               # Raw downloaded PDFs
│── parsed_results/          # AI-extracted JSON data
│── logs/                    # Trade logs & signals
│── processed_companies.json # To avoid reprocessing
│── src/
│     ├── watcher.py         # Monitors NSE filings
│     ├── parser.py          # AI-based PDF extraction
│     ├── sentiment.py       # Sentiment logic
│     ├── trade.py           # Broker API execution
│     ├── cleanup.py         # Auto-delete old files
│── dockerfile
│── requirements.txt
│── README.md


⚙️ Setup & Installation
1. Clone Repository
git clone https://github.com/yourusername/earnings-sentiment-trading.git
cd earnings-sentiment-trading

2. Install Dependencies
pip install -r requirements.txt

3. Environment Variables

Create a .env file:

BROKER_API_KEY=xxxx
BROKER_API_SECRET=xxxx
GEMINI_API_KEY=xxxx

4. Start Watcher
python src/watcher.py

5. Start PDF Parser
python src/parser.py

6. Run Sentiment Engine
python src/sentiment.py

7. Run Trade Execution
python src/trade.py

🧪 How It Works (Step-by-Step)

System detects new quarterly result announcement

Downloads PDF to downloads/

AI model reads PDF and extracts financial metrics

Compares with broker estimates

Assigns sentiment (Positive/Negative/Neutral)

Trade logic calculates quantity, SL, target, and risk

Sends order to broker API

Monitors live price

Auto exits position

Logs data for future analysis

🧹 Auto Cleanup

Old files older than 7 days (PDFs + JSON outputs) are automatically deleted every night.

⚖️ Legal Disclaimer

This system uses public information from NSE/BSE and is intended for personal trading automation.

It does not distribute or sell data

It does not provide financial advice

It complies with public-domain data usage norms

Users must ensure compliance with SEBI and broker API rules for their region.
