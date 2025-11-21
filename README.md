AI-Earnings-Sentiment-Trading

The AI-Powered Earnings Sentiment Trading System is an automated pipeline that monitors NSE/BSE corporate announcements, downloads quarterly results PDFs in real time, extracts key financial metrics using an AI model, performs sentiment analysis, and executes trades automatically based on the results.

This project is part of an end-to-end AI Trading Automation Suite integrating Python, n8n workflows, Google Cloud VM, and broker APIs.

🚀 Key Features
1. Real-Time NSE/BSE Monitoring

Continuously checks for new Board Meeting Outcome result PDFs

Detects companies scheduled to release quarterly results

2. Automatic PDF Downloading

Saves PDFs instantly when an announcement is published

Stores files in a clean, organized directory structure

3. AI-Powered PDF Parsing

Extracts key financial metrics using an LLM-powered parser:

Revenue (QoQ & YoY)

Profit (QoQ & YoY)

EBITDA

Margins

Additional financial metrics

Handles inconsistent PDF formatting with natural language extraction.

4. Sentiment Classification

Compares extracted financial values with broker estimates

Classifies earnings as:

Positive

Negative

Neutral

5. Automated Trade Execution

Uses broker APIs to place trades based on sentiment

Implements:

Position sizing

Risk–reward calculations

Auto-sell on Target / Stop Loss / Timeout

Real-time trade monitoring

6. Logging & Analytics

Stores parsed result JSON files

Maintains trade logs for backtesting

Tracks processed companies to avoid duplicate parsing

7. Deployment Ready

Fully containerized with Docker

Runs on Google Cloud VM (Compute Engine)

Supports background execution using tmux

🧱 Architecture
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

n8n Workflow Automation

LLM-Based PDF Extraction (Gemini / Custom Model)

Yahoo Finance API (Live Market Data)

Watchdog (Filesystem Listener)

Docker / Docker Compose

Cron Jobs / Scheduled Automation

📁 Directory Structure
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
git clone https://github.com/yourusername/AI-Earnings-Sentiment-Trading.git
cd AI-Earnings-Sentiment-Trading

2. Install Dependencies
pip install -r requirements.txt

3. Configure Environment Variables

Create a .env file:

BROKER_API_KEY=xxxx
BROKER_API_SECRET=xxxx
GEMINI_API_KEY=xxxx

4. Start Watcher Service
python src/watcher.py

5. Start PDF Parser
python src/parser.py

6. Run Sentiment Engine
python src/sentiment.py

7. Execute Trade Engine
python src/trade.py

🧪 How It Works (Step-by-Step)

System detects new quarterly result announcement

Downloads PDF to the downloads/ folder

AI model extracts financial metrics

Compares extracted numbers with broker estimates

Assigns sentiment (Positive / Negative / Neutral)

Calculates quantity, SL, target & risk

Places order via broker API

Monitors live price via Yahoo Finance

Automatically exits based on SL/Target/Timeout

Logs trade and parsed data for future analysis

🧹 Auto Cleanup

A scheduled cleanup process deletes:

PDFs older than 7 days

JSON parsed files older than 7 days

This keeps storage clean and optimized.

⚖️ Legal Disclaimer

This system uses publicly available information from NSE/BSE and is intended purely for personal automated trading.

It does not redistribute or sell any market data

It does not provide financial advice

It adheres to public-domain data usage norms

Users are responsible for ensuring compliance with SEBI, exchange policies, and broker API rules.
