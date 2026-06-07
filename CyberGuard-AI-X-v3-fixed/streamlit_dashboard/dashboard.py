"""
CyberGuard AI X - Streamlit Dashboard
Connects to Flask APIs and displays analytics
Run: streamlit run streamlit_dashboard/dashboard.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberGuard AI X",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = "http://localhost:5000/api"

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@400;600;800&display=swap');
  html, body, [class*="css"] { font-family: 'Exo 2', sans-serif; }
  .stApp { background: #050510; color: #e0e0ff; }
  .block-container { padding: 1.5rem 2rem; }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #0d0d2b;
    border: 1px solid #1a1a3e;
    border-radius: 12px;
    padding: 16px;
    border-top: 2px solid #00b4ff;
  }
  [data-testid="stMetricLabel"] { color: #7070a0 !important; font-size: 0.72rem !important; letter-spacing: 2px; text-transform: uppercase; }
  [data-testid="stMetricValue"] { color: #00b4ff !important; font-weight: 800; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0a0a1e !important; border-right: 1px solid #1a1a3e; }
  [data-testid="stSidebar"] * { color: #e0e0ff !important; }

  /* Headers */
  h1, h2, h3 { color: #e0e0ff !important; }
  h1 { font-size: 1.4rem !important; letter-spacing: 2px; }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #003060, #005090) !important;
    color: #00b4ff !important;
    border: 1px solid rgba(0,180,255,0.3) !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
  }

  /* Text area / inputs */
  .stTextArea textarea, .stTextInput input, .stSelectbox select {
    background: #0a0a1e !important;
    border: 1px solid #1a1a3e !important;
    color: #e0e0ff !important;
    border-radius: 8px !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab"] { color: #7070a0 !important; }
  .stTabs [aria-selected="true"] { color: #00b4ff !important; border-bottom-color: #00b4ff !important; }

  /* Info boxes */
  .stInfo { background: rgba(0,180,255,0.1) !important; border: 1px solid rgba(0,180,255,0.3) !important; }
  .stSuccess { background: rgba(0,255,136,0.1) !important; border: 1px solid rgba(0,255,136,0.3) !important; }
  .stError { background: rgba(255,68,68,0.1) !important; border: 1px solid rgba(255,68,68,0.3) !important; }
  .stWarning { background: rgba(255,204,0,0.1) !important; border: 1px solid rgba(255,204,0,0.3) !important; }

  .section-header {
    font-size: 0.75rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #7070a0;
    border-bottom: 1px solid #1a1a3e;
    padding-bottom: 8px;
    margin-bottom: 16px;
  }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#7070a0', size=11),
    colorway=['#00b4ff','#00ff88','#ff4444','#ffcc00','#aa66ff','#ff8800','#00ffff'],
    xaxis=dict(gridcolor='#1a1a3e', linecolor='#1a1a3e'),
    yaxis=dict(gridcolor='#1a1a3e', linecolor='#1a1a3e'),
)


# ─── Session State ─────────────────────────────────────────────────────────────
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


# ─── API Helpers ───────────────────────────────────────────────────────────────
def api_get(endpoint):
    try:
        headers = {'Authorization': f'Bearer {st.session_state.token}'}
        r = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=8)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def api_post(endpoint, payload):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {st.session_state.token}'
        }
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, headers=headers, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {'error': str(e)}, 500


# ─── Login Page ────────────────────────────────────────────────────────────────
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding:20px 0;">
          <div style="font-size:3rem; margin-bottom:12px;">🛡️</div>
          <h1 style="color:#00b4ff !important; letter-spacing:4px; font-size:1.6rem !important;">CYBERGUARD AI X</h1>
          <p style="color:#7070a0; font-size:0.75rem; letter-spacing:3px;">ADVANCED CYBERCRIME INTELLIGENCE PLATFORM</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐  LOGIN", "📝  REGISTER"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="agent@cyberguard.gov.in")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("ACCESS SYSTEM", use_container_width=True)
                if submitted:
                    data, code = api_post('/auth/login', {'email': email, 'password': password})
                    if code == 200:
                        st.session_state.token = data['access_token']
                        st.session_state.user = data['user']
                        st.success("Access granted!")
                        st.rerun()
                    else:
                        st.error(data.get('error', 'Authentication failed'))

        with tab2:
            with st.form("register_form"):
                name = st.text_input("Full Name", placeholder="Agent Name")
                email_r = st.text_input("Email Address", placeholder="agent@cyberguard.gov.in", key="reg_email")
                password_r = st.text_input("Password", type="password", placeholder="Min 8 characters", key="reg_pw")
                submitted_r = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)
                if submitted_r:
                    data, code = api_post('/auth/register', {'name': name, 'email': email_r, 'password': password_r})
                    if code == 201:
                        st.success("Account created! Please login.")
                    else:
                        st.error(data.get('error', 'Registration failed'))

        st.markdown("""
        <div style="text-align:center; margin-top:16px; padding:8px; background:rgba(0,255,136,0.05);
             border:1px solid rgba(0,255,136,0.15); border-radius:6px; font-size:0.7rem; color:#7070a0;">
          🔒 SECURE CONNECTION · TLS 1.3 · AES-256
        </div>
        """, unsafe_allow_html=True)


# ─── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:8px 0; border-bottom:1px solid #1a1a3e; margin-bottom:16px;">
          <span style="font-size:1.2rem">🛡️</span>
          <span style="font-size:0.9rem; font-weight:700; letter-spacing:2px; margin-left:8px;">CYBERGUARD AI X</span>
          <br><span style="font-size:0.6rem; color:#7070a0; letter-spacing:1px; margin-left:30px;">Intelligence Platform</span>
        </div>
        """, unsafe_allow_html=True)

        user = st.session_state.user or {}
        st.markdown(f"""
        <div style="background:#0d0d2b; border:1px solid #1a1a3e; border-radius:10px;
             padding:12px; margin-bottom:16px; display:flex; align-items:center; gap:10px;">
          <div style="width:36px;height:36px;background:linear-gradient(135deg,#00b4ff,#aa66ff);
               border-radius:50%;display:flex;align-items:center;justify-content:center;
               font-weight:700;color:white;font-size:14px;">{user.get('name','U')[0].upper()}</div>
          <div>
            <div style="font-size:0.82rem;font-weight:600;">{user.get('name','Unknown')}</div>
            <div style="font-size:0.65rem;color:#00ff88;letter-spacing:1px;text-transform:uppercase;">{user.get('role','user')}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📁 Submit Complaint", "📜 Complaint History",
             "📈 Analytics", "🤖 AI Predictor"] +
            (["👑 Admin Panel"] if user.get('role') == 'admin' else []),
            label_visibility="collapsed"
        )

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 PDF", use_container_width=True):
                st.info("Use the web dashboard for PDF export.")
        with col2:
            if st.button("📊 Excel", use_container_width=True):
                st.info("Use the web dashboard for Excel export.")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

        st.markdown(f"""
        <div style="font-size:0.65rem; color:#3a3a6a; text-align:center; margin-top:8px;">
          {datetime.now().strftime('%d %b %Y  %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)

    return page


# ─── Dashboard Page ────────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown('<div class="section-header">⚡ SYSTEM OVERVIEW</div>', unsafe_allow_html=True)

    overview = api_get('/analytics/overview') or {}

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📁 Total Complaints", overview.get('total_complaints', 0))
    col2.metric("🔴 High Severity", overview.get('high_severity', 0))
    col3.metric("💳 Fraud Cases", overview.get('fraud_cases', 0))
    col4.metric("👥 Active Users", overview.get('active_users', 0))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("✅ Resolved", overview.get('resolved_cases', 0))
    col6.metric("⏳ Pending", overview.get('pending_cases', 0))
    col7.metric("📅 Today", overview.get('today_complaints', 0))
    col8.metric("🔍 Under Review", overview.get('total_complaints', 0) - overview.get('resolved_cases', 0) - overview.get('pending_cases', 0))

    st.markdown("---")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-header">📊 CATEGORY DISTRIBUTION</div>', unsafe_allow_html=True)
        cat_data = api_get('/analytics/category-distribution')
        if cat_data and cat_data.get('data'):
            df = pd.DataFrame(cat_data['data'])
            fig = px.bar(df, x='category', y='count', color='category',
                         color_discrete_sequence=PLOTLY_THEME['colorway'])
            fig.update_layout(**PLOTLY_THEME, showlegend=False, height=300,
                              margin=dict(l=0, r=0, t=10, b=0))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")

    with col_right:
        st.markdown('<div class="section-header">🔴 SEVERITY SPLIT</div>', unsafe_allow_html=True)
        sev_data = api_get('/analytics/severity-distribution')
        if sev_data and sev_data.get('data'):
            df = pd.DataFrame(sev_data['data'])
            color_map = {'High': '#ff4444', 'Medium': '#ffcc00', 'Low': '#00ff88'}
            fig = px.pie(df, names='severity', values='count', hole=0.6,
                         color='severity', color_discrete_map=color_map)
            fig.update_layout(**PLOTLY_THEME, height=300, margin=dict(l=0, r=0, t=10, b=0))
            fig.update_traces(textfont_color='white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No severity data")

    # Monthly trends
    st.markdown('<div class="section-header">📈 MONTHLY TRENDS</div>', unsafe_allow_html=True)
    monthly = api_get('/analytics/monthly-trends')
    if monthly and monthly.get('data'):
        df = pd.DataFrame(monthly['data'])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['month'], y=df['count'], name='Total',
                                 fill='tozeroy', line=dict(color='#00b4ff', width=2),
                                 fillcolor='rgba(0,180,255,0.1)'))
        if 'high_count' in df.columns:
            fig.add_trace(go.Scatter(x=df['month'], y=df['high_count'], name='High Severity',
                                     fill='tozeroy', line=dict(color='#ff4444', width=2),
                                     fillcolor='rgba(255,68,68,0.1)'))
        fig.update_layout(**PLOTLY_THEME, height=260, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No monthly trend data")

    # Recent complaints
    st.markdown('<div class="section-header">🕐 RECENT COMPLAINTS</div>', unsafe_allow_html=True)
    recent = overview.get('recent_complaints', [])
    if recent:
        df = pd.DataFrame(recent)[['id', 'user_name', 'category', 'severity', 'status', 'created_at']]
        df.columns = ['ID', 'User', 'Category', 'Severity', 'Status', 'Date']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent complaints")


# ─── Submit Complaint Page ─────────────────────────────────────────────────────
def page_submit():
    st.markdown('<div class="section-header">📁 SUBMIT NEW COMPLAINT</div>', unsafe_allow_html=True)
    col_form, col_result = st.columns([1, 1])

    with col_form:
        with st.form("complaint_form"):
            complaint_text = st.text_area(
                "Complaint Description *",
                height=180,
                placeholder="Describe the cybercrime incident in detail.\nSupports English, Hindi, and Gujarati.\nMinimum 20 characters required.",
            )
            language = st.selectbox(
                "Language (Optional)",
                ["Auto Detect", "English (en)", "Hindi (hi)", "Gujarati (gu)"]
            )
            lang_map = {"Auto Detect": None, "English (en)": "en", "Hindi (hi)": "hi", "Gujarati (gu)": "gu"}
            lang_code = lang_map[language]

            col_a, col_b = st.columns(2)
            with col_a:
                submitted = st.form_submit_button("🚀 SUBMIT COMPLAINT", use_container_width=True)
            with col_b:
                analyze_only = st.form_submit_button("🧠 ANALYZE ONLY", use_container_width=True)

        if submitted or analyze_only:
            if not complaint_text or len(complaint_text.strip()) < 20:
                st.error("Complaint must be at least 20 characters.")
            else:
                with st.spinner("AI analyzing complaint..."):
                    if submitted:
                        payload = {'complaint_text': complaint_text}
                        if lang_code:
                            payload['language'] = lang_code
                        data, code = api_post('/complaints/submit', payload)
                        if code == 201:
                            st.success(f"✅ Complaint submitted! ID: #{data.get('complaint_id')}")
                            result = data.get('prediction', {})
                        else:
                            st.error(data.get('error', 'Submission failed'))
                            result = None
                    else:
                        data, code = api_post('/ai/predict', {'text': complaint_text, 'language': lang_code})
                        result = data.get('result') if code == 200 else None
                        if not result:
                            st.error(data.get('error', 'Analysis failed'))

                if result:
                    st.session_state['last_result'] = result

    with col_result:
        result = st.session_state.get('last_result')
        if result:
            st.markdown('<div class="section-header">🤖 AI ANALYSIS RESULT</div>', unsafe_allow_html=True)

            sev_color = {'High': '#ff4444', 'Medium': '#ffcc00', 'Low': '#00ff88'}
            sev = result.get('severity', 'Low')

            st.markdown(f"""
            <div style="background:#0d0d2b; border:1px solid #1a1a3e; border-radius:12px; padding:20px;">
              <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                <span style="color:#7070a0;font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;">Category</span>
                <span style="color:#00b4ff;font-weight:700;">{result.get('category','—')}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                <span style="color:#7070a0;font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;">Confidence</span>
                <span style="color:#e0e0ff;font-weight:700;">{result.get('confidence',0):.1f}%</span>
              </div>
              <div style="height:6px;background:#1a1a3e;border-radius:3px;margin-bottom:14px;">
                <div style="height:100%;width:{result.get('confidence',0)}%;background:linear-gradient(90deg,#00b4ff,#00ff88);border-radius:3px;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                <span style="color:#7070a0;font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;">Severity</span>
                <span style="color:{sev_color.get(sev,'#e0e0ff')};font-weight:700;">{sev}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                <span style="color:#7070a0;font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;">Department</span>
                <span style="color:#e0e0ff;font-size:0.82rem;text-align:right;max-width:180px;">{result.get('department','—')}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                <span style="color:#7070a0;font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;">Helpline</span>
                <span style="color:#00ff88;font-size:0.82rem;">{result.get('contact','—')}</span>
              </div>
              <div style="display:flex;justify-content:space-between;">
                <span style="color:#7070a0;font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;">Priority</span>
                <span style="color:#ffcc00;font-size:0.8rem;">{result.get('priority','—')}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Keywords
            kws = result.get('top_keywords', [])
            if kws:
                st.markdown("**Detected Keywords:**")
                st.markdown(' '.join([f'`{k}`' for k in kws]))

            # Probability distribution
            prob = result.get('probability_distribution', {})
            if prob:
                st.markdown("**Probability Distribution:**")
                df_prob = pd.DataFrame(list(prob.items()), columns=['Category', 'Probability'])
                df_prob = df_prob.sort_values('Probability', ascending=True)
                fig = px.bar(df_prob, x='Probability', y='Category', orientation='h',
                             color='Probability', color_continuous_scale=['#1a1a3e', '#00b4ff'])
                fig.update_layout(**PLOTLY_THEME, height=280, showlegend=False,
                                  margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
            <div style="background:#0d0d2b; border:1px dashed #1a1a3e; border-radius:12px; padding:40px; text-align:center;">
              <div style="font-size:2rem; margin-bottom:12px;">🤖</div>
              <div style="color:#7070a0; font-size:0.85rem;">Submit or analyze a complaint to see AI predictions here.</div>
            </div>
            """, unsafe_allow_html=True)


# ─── Complaint History Page ────────────────────────────────────────────────────
def page_history():
    st.markdown('<div class="section-header">📜 COMPLAINT HISTORY</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("Search", placeholder="Search complaints...")
    with col2:
        cat_filter = st.selectbox("Category", ["All", "Phishing", "Hacking", "Malware",
                                               "Online Fraud", "Financial Fraud", "Identity Theft", "Cyberbullying"])
    with col3:
        sev_filter = st.selectbox("Severity", ["All", "High", "Medium", "Low"])
    with col4:
        sta_filter = st.selectbox("Status", ["All", "Pending", "Under Review", "Resolved", "Closed"])

    params = "?per_page=100"
    if search: params += f"&search={search}"
    if cat_filter != "All": params += f"&category={cat_filter}"
    if sev_filter != "All": params += f"&severity={sev_filter}"
    if sta_filter != "All": params += f"&status={sta_filter}"

    data = api_get(f'/complaints/{params}')
    if data and data.get('complaints'):
        complaints = data['complaints']
        st.info(f"Showing {len(complaints)} of {data.get('total', len(complaints))} complaints")
        df = pd.DataFrame(complaints)
        cols = ['id', 'complaint_text', 'category', 'confidence_score', 'severity', 'department', 'status', 'created_at']
        cols = [c for c in cols if c in df.columns]
        df = df[cols].copy()
        df.columns = [c.replace('_', ' ').title() for c in cols]
        if 'Complaint Text' in df.columns:
            df['Complaint Text'] = df['Complaint Text'].str[:60] + '...'
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No complaints found.")


# ─── Analytics Page ────────────────────────────────────────────────────────────
def page_analytics():
    st.markdown('<div class="section-header">📈 ADVANCED ANALYTICS</div>', unsafe_allow_html=True)

    cat = api_get('/analytics/category-distribution') or {'data': []}
    sev = api_get('/analytics/severity-distribution') or {'data': []}
    monthly = api_get('/analytics/monthly-trends') or {'data': []}
    dept = api_get('/analytics/department-distribution') or {'data': []}
    lang = api_get('/analytics/language-distribution') or {'data': []}

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Category Distribution (Bar)</div>', unsafe_allow_html=True)
        if cat['data']:
            df = pd.DataFrame(cat['data'])
            fig = px.bar(df, x='category', y='count', color='category',
                         color_discrete_sequence=PLOTLY_THEME['colorway'])
            fig.update_layout(**PLOTLY_THEME, height=280, showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Complaint Share (Pie)</div>', unsafe_allow_html=True)
        if cat['data']:
            df = pd.DataFrame(cat['data'])
            fig = px.pie(df, names='category', values='count',
                         color_discrete_sequence=PLOTLY_THEME['colorway'])
            fig.update_layout(**PLOTLY_THEME, height=280, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns([1, 2])
    with col3:
        st.markdown('<div class="section-header">Severity Donut</div>', unsafe_allow_html=True)
        if sev['data']:
            df = pd.DataFrame(sev['data'])
            color_map = {'High': '#ff4444', 'Medium': '#ffcc00', 'Low': '#00ff88'}
            fig = px.pie(df, names='severity', values='count', hole=0.6,
                         color='severity', color_discrete_map=color_map)
            fig.update_layout(**PLOTLY_THEME, height=280, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Monthly Trend (Line)</div>', unsafe_allow_html=True)
        if monthly['data']:
            df = pd.DataFrame(monthly['data'])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['month'], y=df['count'], name='Total',
                                     fill='tozeroy', line=dict(color='#00b4ff', width=2),
                                     fillcolor='rgba(0,180,255,0.1)'))
            if 'high_count' in df.columns:
                fig.add_trace(go.Scatter(x=df['month'], y=df['high_count'], name='High',
                                         line=dict(color='#ff4444', width=2)))
            fig.update_layout(**PLOTLY_THEME, height=280, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<div class="section-header">Department Cases (Horizontal Bar)</div>', unsafe_allow_html=True)
        if dept['data']:
            df = pd.DataFrame(dept['data'])
            fig = px.bar(df, x='count', y='department', orientation='h',
                         color='count', color_continuous_scale=['#003060', '#00b4ff'])
            fig.update_layout(**PLOTLY_THEME, height=280, showlegend=False,
                              margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with col6:
        st.markdown('<div class="section-header">Language Usage</div>', unsafe_allow_html=True)
        if lang['data']:
            df = pd.DataFrame(lang['data'])
            fig = px.pie(df, names='language_name', values='count',
                         color_discrete_sequence=['#00b4ff','#ff8800','#aa66ff'])
            fig.update_layout(**PLOTLY_THEME, height=280, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)


# ─── AI Predictor Page ─────────────────────────────────────────────────────────
def page_ai_predictor():
    st.markdown('<div class="section-header">🤖 AI PREDICTION ENGINE</div>', unsafe_allow_html=True)
    st.info("**Model:** TF-IDF + Logistic Regression | **Languages:** English, Hindi, Gujarati | **Categories:** 7")

    text = st.text_area("Enter complaint text for analysis:", height=150,
                        placeholder="Paste any cybercrime complaint text here...")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔍 ANALYZE", use_container_width=True):
            if text and len(text.strip()) >= 10:
                with st.spinner("Running AI analysis..."):
                    data, code = api_post('/ai/predict', {'text': text})
                    if code == 200:
                        st.session_state['ai_pred_result'] = data.get('result', {})
                    else:
                        st.error(data.get('error', 'Analysis failed'))

    result = st.session_state.get('ai_pred_result')
    if result:
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔖 Category", result.get('category', '—'))
        c2.metric("📊 Confidence", f"{result.get('confidence', 0):.1f}%")
        c3.metric("⚠️ Severity", result.get('severity', '—'))
        c4.metric("🏢 Department", result.get('department', '—')[:20])

        col_kw, col_prob = st.columns(2)
        with col_kw:
            st.markdown("**🔑 Top Keywords:**")
            kws = result.get('top_keywords', [])
            if kws:
                st.markdown(' '.join([f'`{k}`' for k in kws]))
            st.markdown(f"**📞 Helpline:** `{result.get('contact','—')}`")
            st.markdown(f"**⏱ Priority:** `{result.get('priority','—')}`")
            st.markdown(f"**🌐 Language:** `{result.get('language_name','—')}`")

        with col_prob:
            prob = result.get('probability_distribution', {})
            if prob:
                st.markdown("**📊 Probability Distribution:**")
                df_prob = pd.DataFrame(list(prob.items()), columns=['Category', 'Probability'])
                df_prob = df_prob.sort_values('Probability', ascending=False)
                fig = px.bar(df_prob, x='Category', y='Probability', color='Probability',
                             color_continuous_scale=['#1a1a3e', '#00b4ff'])
                fig.update_layout(**PLOTLY_THEME, height=250, showlegend=False,
                                  margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)


# ─── Admin Panel Page ──────────────────────────────────────────────────────────
def page_admin():
    user = st.session_state.user or {}
    if user.get('role') != 'admin':
        st.error("Admin access required.")
        return

    st.markdown('<div class="section-header">👑 ADMIN PANEL</div>', unsafe_allow_html=True)
    overview = api_get('/analytics/overview') or {}

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Complaints", overview.get('total_complaints', 0))
    col2.metric("Pending", overview.get('pending_cases', 0))
    col3.metric("Resolved", overview.get('resolved_cases', 0))
    col4.metric("High Severity", overview.get('high_severity', 0))

    st.markdown("---")
    st.markdown('<div class="section-header">All Complaints</div>', unsafe_allow_html=True)

    data = api_get('/complaints/?per_page=200')
    if data and data.get('complaints'):
        complaints = data['complaints']
        df = pd.DataFrame(complaints)
        cols = ['id', 'user_name', 'category', 'severity', 'department', 'status', 'created_at']
        cols = [c for c in cols if c in df.columns]
        df_display = df[cols].copy()
        df_display.columns = [c.replace('_', ' ').title() for c in cols]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No complaints found.")

    st.markdown("---")
    st.markdown('<div class="section-header">Registered Users</div>', unsafe_allow_html=True)
    users_data = api_get('/auth/users')
    if users_data and users_data.get('users'):
        df_users = pd.DataFrame(users_data['users'])[['id', 'name', 'email', 'role', 'created_at']]
        st.dataframe(df_users, use_container_width=True, hide_index=True)


# ─── Main ───────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.token:
        login_page()
        return

    page = render_sidebar()

    if "Dashboard" in page:
        page_dashboard()
    elif "Submit" in page:
        page_submit()
    elif "History" in page:
        page_history()
    elif "Analytics" in page:
        page_analytics()
    elif "AI Predictor" in page:
        page_ai_predictor()
    elif "Admin" in page:
        page_admin()


if __name__ == "__main__":
    main()
