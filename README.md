# AI-Orchestrated Multi-Agent Framework for Log-Centric Cyber Threat Detection and Analysis

This project presents an advanced, log-centric cybersecurity framework that leverages artificial intelligence and a multi-agent system to enhance threat detection and analysis.

By autonomously ingesting and processing large volumes of raw logs, the framework identifies anomalous behaviors, correlates multi-stage attack patterns, and orchestrates specialized LLM-powered agents for in-depth analysis.

The system transforms raw security data into **clear, actionable intelligence** and **comprehensive narrative reports**, enabling proactive defense mechanisms.

---

## Key Features

### 1. Multi-Agent Security Orchestration

The platform uses an LLM-powered orchestrator to route detected threats to specialized Attack specific agents:

* **Auth Agent** – Detects anomalous logins and brute-force attempts
* **System Agent** – Analyzes privilege escalation and suspicious commands
* **Exfiltration Agent** – Tracks abnormal data transfers and potential breaches
* **Network Agent** – Identifies DDoS patterns and traffic anomalies

---

### 2. Intelligent Threat Detection

The system processes logs from multiple sources (Windows, SSH, Firewall) and performs:

* Data normalization
* Time-window aggregation
* Context enrichment (GeoIP, VirusTotal)

This results in **high-fidelity security signals with reduced false positives**.

---

### 3. Automated Attack Storylines

The framework correlates signals and agent outputs to generate:

* Human-readable reports
* Structured attack storylines

This reduces analyst workload and improves decision-making.

---

### 4. Real-Time Security Dashboard

A modern frontend interface allows users to:

* Upload logs
* Monitor threats in real time
* Review detailed agent-based investigations

---

## Technology Stack

* **Frontend**: React, TypeScript, Vite, Tailwind CSS
* **Backend**: Python, FastAPI, Celery
* **Database**: MySQL
* **Agents Building Framework**: LangChain
* **LLM**: Llama 3.3B model(Groq)

---

##  Getting Started

### Prerequisites

* Python 3.10+
* Node.js 18+
* MySQL Server

---

### 1. Database Setup

```bash
mysql -u root -p < backend/schema.sql
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv_acd
source venv_acd/bin/activate   # Windows: .\venv_acd\Scripts\activate
pip install -r requirements.txt
```

#### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=acd_sdi

VIRUSTOTAL_API=your_virustotal_api_key_here
```

#### Run Backend Server

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access the dashboard at:
`http://localhost:5173`

---
