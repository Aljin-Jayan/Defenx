<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:ff3333,100:0d1117&height=180&section=header&text=DEFENX&fontSize=70&fontColor=ff3333&animation=fadeIn&fontAlignY=38&desc=Website%20Defacement%20Detection%20%26%20Response%20System&descAlignY=60&descSize=16&descColor=ff6666" width="100%"/>
</p>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Security](https://img.shields.io/badge/Category-Blue%20Team%20%7C%20Defense-blue?style=for-the-badge&logo=shield&logoColor=white)]()
[![OWASP](https://img.shields.io/badge/OWASP-A05%3A2021%20Security%20Misconfiguration-red?style=for-the-badge)](https://owasp.org)

</div>

---

## 🔍 What is Defenx?

**Defenx** is a real-time **Website Defacement Detection and Automated Response System** built with FastAPI. It continuously monitors websites for unauthorized content modifications — a critical threat vector used by hacktivists and APT groups — and instantly triggers alerts or automated remediation.

> ⚠️ Website defacement is classified under **OWASP Top 10 A05:2021 – Security Misconfiguration** and is a common attack vector following successful initial access.

---

## 🏗️ System Architecture

```
  ┌─────────────────────────────────────────────────────────────┐
  │                     DEFENX ARCHITECTURE                     │
  │                                                             │
  │   Target Website                                            │
  │        │                                                    │
  │        ▼                                                    │
  │   ┌──────────┐    hash comparison    ┌──────────────────┐   │
  │   │ Crawler  │ ──────────────────►  │  Hash Store (DB) │   │
  │   │ Module   │ ◄──────────────────  │  (SQLite)        │   │
  │   └──────────┘   baseline snapshot  └──────────────────┘   │
  │        │                                                    │
  │        │  CHANGE DETECTED                                   │
  │        ▼                                                    │
  │   ┌──────────┐                       ┌──────────────────┐   │
  │   │ Alert    │ ──── SMTP/Webhook ──► │ Admin Dashboard  │   │
  │   │ Engine   │                       │ (FastAPI UI)     │   │
  │   └──────────┘                       └──────────────────┘   │
  │        │                                                    │
  │        ▼                                                    │
  │   ┌──────────┐                                              │
  │   │  Logger  │ ──► Audit Logs & Forensic Evidence          │
  │   └──────────┘                                              │
  └─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Real-time Monitoring** | Continuously crawls and hashes website content |
| 🔐 **Hash-based Detection** | SHA-256 comparison between baseline and current state |
| 📧 **Alert System** | Email (SMTP) + webhook notifications on defacement |
| 📝 **Audit Logging** | Timestamped logs for forensic investigation |
| ⚡ **FastAPI Backend** | High-performance async REST API |
| 🌐 **Browser Extension** | Optional extension for real-time status checks |
| 🗄️ **SQLite Storage** | Lightweight, embedded log and baseline database |

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+  |  FastAPI  |  Uvicorn  |  SQLite  |  SMTP (optional)
```

### 1. Clone the Repository

```bash
git clone https://github.com/Aljin-Jayan/Defenx.git
cd Defenx
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy and edit your environment config
cp .env.example .env
```

```env
# .env
DATABASE_URL=sqlite:///./defenx.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your_password
ADMIN_EMAIL=admin@yourdomain.com
```

### 4. Launch the Server

```bash
uvicorn main:app --reload
```

> Server running at `http://127.0.0.1:8000` · API Docs at `http://127.0.0.1:8000/docs`

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/status` | Get monitoring system status |
| `POST` | `/monitor` | Register a new website for monitoring |
| `GET` | `/detect` | Run defacement detection on monitored sites |
| `GET` | `/logs` | Retrieve audit logs |
| `DELETE` | `/monitor/{id}` | Remove a website from monitoring |

### Example: Start Monitoring

```bash
curl -X POST http://127.0.0.1:8000/monitor \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourtarget.com"}'
```

```json
{
  "message": "Website monitoring started successfully.",
  "baseline_hash": "a3f1c9e2b4d7...",
  "monitored_since": "2025-05-06T10:00:00Z"
}
```

### Example: Defacement Detected

```json
{
  "defacement_detected": true,
  "url": "https://yourtarget.com",
  "details": "Unauthorized content change detected in <body> section.",
  "severity": "HIGH",
  "timestamp": "2025-05-06T14:32:01Z"
}
```

---

## 🌐 Browser Extension

The optional browser extension allows direct interaction with Defenx from your browser:

1. Load the extension manually via `chrome://extensions` → **Load Unpacked**
2. Click the Defenx icon to view monitoring status
3. Trigger detection scans directly from the toolbar

---

## 📁 Project Structure

```
Defenx/
├── Defenx/
│   ├── main.py           # FastAPI app entrypoint
│   ├── monitor.py        # Website crawler & hash engine
│   ├── alert.py          # Email/webhook alert system
│   ├── logger.py         # Audit logging module
│   └── models.py         # Database models
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🗺️ Roadmap

- [x] Hash-based defacement detection
- [x] SMTP alert notifications
- [x] FastAPI REST API
- [ ] Dashboard UI (React frontend)
- [ ] Discord/Slack webhook alerts
- [ ] Scheduled auto-restore (backup-based remediation)
- [ ] SIEM integration (Splunk/ELK)
- [ ] Docker containerization

---

## 🤝 Contributing

```bash
# Fork → Branch → Commit → Push → PR
git checkout -b feature/your-feature
git commit -m "feat: describe your change"
git push origin feature/your-feature
```

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [Aljin Jayan](https://github.com/Aljin-Jayan) — OSCP | Offenso Certified Security Professional**

[![GitHub](https://img.shields.io/badge/GitHub-Aljin--Jayan-181717?style=flat-square&logo=github)](https://github.com/Aljin-Jayan)

</div>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:ff3333,100:0d1117&height=100&section=footer" width="100%"/>
</p>
