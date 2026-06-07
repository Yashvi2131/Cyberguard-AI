# 🛡️ CyberGuard AI X
### AI-Powered Cybercrime Complaint Intelligence & Management System

---

## 🔍 Overview

CyberGuard AI X is a production-grade cybercrime complaint management platform that combines Artificial Intelligence, Machine Learning, NLP, and full-stack web development into a professional government-style dashboard.

### Key Features

| Feature | Description |
|---|---|
| 🤖 AI Classification | TF-IDF + Logistic Regression classifies 7 cybercrime categories |
| 🌐 Multilingual | Auto-detects and translates Hindi, Gujarati, English |
| ⚠️ Severity Analysis | Keyword-based High/Medium/Low severity detection |
| 🏢 Department Routing | Auto-recommends the appropriate cyber cell department |
| 📊 Analytics Dashboard | 6 interactive charts with real-time data |
| 🔐 JWT Authentication | Role-based access (Admin / User) |
| 📄 Report Export | PDF and Excel report generation |
| 💡 AI Explainability | Confidence scores, probability distributions, keywords |
| 🖥️ Streamlit Dashboard | Standalone Streamlit interface consuming Flask APIs |

---

## 🗂️ Project Structure

```
CyberGuard-AI-X/
│
├── frontend/
│   ├── templates/
│   │   ├── index.html          ← Login page
│   │   └── dashboard.html      ← Main dashboard (all sections)
│   └── static/
│       ├── css/cyber.css       ← Global styles
│       └── js/app.js           ← Shared utilities
│
├── backend/
│   ├── app.py                  ← Flask app factory
│   ├── seed_admin.py           ← Admin user seeder
│   ├── routes/
│   │   ├── auth_routes.py      ← Login, register, JWT
│   │   ├── complaint_routes.py ← CRUD, submit, filter
│   │   ├── analytics_routes.py ← Charts data APIs
│   │   ├── ai_routes.py        ← Prediction, severity, department APIs
│   │   └── report_routes.py    ← PDF and Excel export
│   └── database/
│       └── db.py               ← MySQL connection manager
│
├── ml/
│   ├── preprocessor.py         ← Text cleaning pipeline
│   ├── translator.py           ← Multilingual detection & translation
│   ├── severity.py             ← Severity + department engine
│   ├── train_model.py          ← Model training script
│   ├── predict.py              ← Full prediction pipeline
│   └── model.pkl               ← Trained model (auto-generated)
│
├── database/
│   └── schema.sql              ← MySQL schema & seed
│
├── streamlit_dashboard/
│   └── dashboard.py            ← Streamlit frontend
│
├── reports/                    ← Generated reports output
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Technology Stack

### Backend
- **Python 3.10+**
- **Flask 3.0** — REST API framework
- **Flask-JWT-Extended** — JWT authentication
- **Flask-CORS** — Cross-origin resource sharing
- **MySQL / XAMPP** — Database

### Machine Learning
- **scikit-learn** — TF-IDF vectorizer + Logistic Regression
- **NLTK** — Text preprocessing, tokenization, stopwords
- **langdetect** — Language detection
- **deep-translator** — Google Translate API wrapper

### Frontend
- **Bootstrap 5.3** — Responsive grid
- **Chart.js 4** — Interactive charts
- **Vanilla JS + AJAX** — Dynamic data loading

### Streamlit Dashboard
- **Streamlit 1.31** — Python-based web UI
- **Plotly** — Advanced charts

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- XAMPP (MySQL + Apache)
- Git

---

### Step 1 — Database Setup

1. Start XAMPP and make sure **MySQL** is running
2. Open **phpMyAdmin**: `http://localhost/phpmyadmin`
3. Create a new database named `cyberguard_ai`
4. Import the schema:
   ```
   File → Import → database/schema.sql → Go
   ```

---

### Step 2 — Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3 — Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# DB_PASSWORD= (leave blank for XAMPP default)
```

---

### Step 4 — Train the ML Model

```bash
cd ml
python train_model.py
```

This creates `ml/model.pkl` with the trained classifier.

---

### Step 5 — Seed Admin User

```bash
cd backend
python seed_admin.py
```

Default credentials:
- **Email:** `admin@cyberguard.ai`
- **Password:** `Admin@123`

---

### Step 6 — Start Flask Backend

```bash
cd backend
python app.py
```

Backend runs at: `http://localhost:5000`

---

### Step 7 — Access the Platform

| URL | Description |
|---|---|
| `http://localhost:5000` | Web login page |
| `http://localhost:5000/dashboard` | Main dashboard |
| `http://localhost:5000/api/health` | API health check |

---

### Step 8 — (Optional) Streamlit Dashboard

```bash
cd streamlit_dashboard
streamlit run dashboard.py
```

Streamlit runs at: `http://localhost:8501`

> Make sure Flask backend is running before starting Streamlit.

---

## 🔐 Authentication

| Role | Access |
|---|---|
| **Admin** | All complaints, analytics, user management, status updates |
| **User** | Submit complaints, view own history, track predictions |

### API Authentication

All protected endpoints require:
```
Authorization: Bearer <JWT_TOKEN>
```

---

## 🤖 Machine Learning Pipeline

```
Input Complaint
      ↓
Language Detection (langdetect)
      ↓
Translation to English (deep-translator)
      ↓
Text Preprocessing (NLTK)
  → Lowercase
  → Remove URLs, emails, punctuation
  → Stopword removal
  → Tokenization
      ↓
TF-IDF Feature Extraction
      ↓
Logistic Regression Classification
      ↓
Severity Analysis (keyword rules)
      ↓
Department Recommendation
      ↓
AI Explainability Output
```

### Categories
- Phishing
- Hacking
- Malware
- Online Fraud
- Financial Fraud
- Identity Theft
- Cyberbullying

---

## 📡 API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user info |
| GET | `/api/auth/users` | All users (admin only) |

### Complaints
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/complaints/submit` | Submit + classify complaint |
| GET | `/api/complaints/` | List complaints (filterable) |
| GET | `/api/complaints/<id>` | Get single complaint |
| PUT | `/api/complaints/<id>/status` | Update status (admin) |
| GET | `/api/complaints/stats/summary` | Summary stats |

### AI
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ai/predict` | Full prediction pipeline |
| POST | `/api/ai/classify` | Quick classification |
| POST | `/api/ai/severity` | Severity analysis only |
| POST | `/api/ai/department` | Department recommendation |
| GET | `/api/ai/model-info` | Model metadata |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analytics/overview` | Dashboard summary |
| GET | `/api/analytics/category-distribution` | Category counts |
| GET | `/api/analytics/severity-distribution` | Severity counts |
| GET | `/api/analytics/monthly-trends` | Monthly data |
| GET | `/api/analytics/department-distribution` | Department counts |
| GET | `/api/analytics/language-distribution` | Language counts |

### Reports
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reports/pdf` | Download PDF report |
| GET | `/api/reports/excel` | Download Excel report |

---

## 🔭 Future Scope

The ML architecture is designed for drop-in model upgrades:

```python
# Current
from sklearn.linear_model import LogisticRegression

# Future (drop-in replacement)
from transformers import pipeline
classifier = pipeline("text-classification", model="bert-base-uncased")
```

Planned upgrades:
- **BERT / RoBERTa** — Transformer-based classification
- **DistilBERT** — Lightweight transformer
- **LLM-based** — GPT/Gemini for complaint analysis
- **Computer Vision** — Screenshot evidence analysis
- **Real-time Alerts** — WebSocket notifications
- **Mobile App** — React Native frontend

---

## 🛡️ Security Features

- JWT tokens with 24-hour expiry
- bcrypt password hashing (salt rounds: 12)
- Role-based access control
- SQL injection prevention (parameterized queries)
- CORS protection
- Login audit logs with IP tracking

---

## 📞 Emergency Contacts

| Helpline | Number/URL |
|---|---|
| National Cyber Crime | 1930 |
| Cyber Crime Portal | cybercrime.gov.in |
| Financial Fraud | 1800-11-6090 |

---

## 📄 License

For educational and government use. Built for cybercrime awareness and complaint management.

---

**CyberGuard AI X** — *Defending the Digital Frontier* 🛡️
