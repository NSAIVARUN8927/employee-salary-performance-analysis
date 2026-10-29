import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import io
from backend import analytics as an, auth, database as db

st.set_page_config(
    page_title="Employee Salary & Performance Analysis",
    page_icon="📊",
    layout="wide"
)

db.init_db()

CSV = "data/employee_salary_performance.csv"

if not db.is_seeded():
    db.seed_database(an.prepare(an.load_data(CSV))[0])


# ==================== GLOBAL AND SIDEBAR STYLING ====================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

/* Global fonts */
html,
body,
[class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ==================== SIDEBAR ==================== */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #172554 100%);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #F8FAFC;
}

/* Improve visibility of sidebar labels */
.stApp [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
.stApp [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #67E8F9 !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}
/* Navigation and data source dropdowns */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #263449 !important;
    border: 1px solid #475569 !important;
    border-radius: 9px !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] input {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
}

/* ==================== SIGN OUT BUTTON ==================== */

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 43px;
    background: linear-gradient(135deg, #EF4444, #B91C1C) !important;
    color: #FFFFFF !important;
    border: 1px solid #F87171 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(185, 28, 28, 0.25);
    transition: all 0.25s ease-in-out !important;
}

[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #DC2626, #7F1D1D) !important;
    border-color: #FCA5A5 !important;
    box-shadow: 0 7px 18px rgba(185, 28, 28, 0.35);
    transform: translateY(-2px);
}

[data-testid="stSidebar"] .stButton > button:active {
    transform: translateY(0);
}

/* ==================== KPI STATISTIC CARDS ==================== */

.kpi-card {
    position: relative;
    overflow: hidden;
    min-height: 125px;
    padding: 21px 20px;
    margin: 5px 0 12px 0;
    background: linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%);
    border: 1px solid #D8E2EF;
    border-left: 5px solid #2563EB;
    border-radius: 14px;
    box-shadow: 0 5px 16px rgba(15, 23, 42, 0.07);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(15, 23, 42, 0.13);
}

.kpi-label {
    display: block;
    margin-bottom: 13px;
    color: #475569 !important;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    line-height: 1.4;
}

.kpi-value {
    display: block;
    color: #0F172A !important;
    font-family: 'Inter', sans-serif;
    font-size: clamp(21px, 2vw, 29px);
    font-weight: 800;
    letter-spacing: -0.7px;
    line-height: 1.3;
    overflow-wrap: anywhere;
}

/* Different colors for each statistic card */
.kpi-blue {
    background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
    border-left-color: #2563EB;
}

.kpi-green {
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    border-left-color: #059669;
}

.kpi-purple {
    background: linear-gradient(135deg, #F5F3FF, #EDE9FE);
    border-left-color: #7C3AED;
}

.kpi-orange {
    background: linear-gradient(135deg, #FFF7ED, #FFEDD5);
    border-left-color: #EA580C;
}

.kpi-pink {
    background: linear-gradient(135deg, #FDF2F8, #FCE7F3);
    border-left-color: #DB2777;
}

.kpi-cyan {
    background: linear-gradient(135deg, #ECFEFF, #CFFAFE);
    border-left-color: #0891B2;
}

.kpi-teal {
    background: linear-gradient(135deg, #F0FDFA, #CCFBF1);
    border-left-color: #0D9488;
}

/* Responsive card sizing */
@media (max-width: 768px) {
    .kpi-card {
        min-height: 105px;
        padding: 16px;
    }

    .kpi-value {
        font-size: 22px;
    }
}
/* Professional Employees Header */
.employee-page-banner {
    position: relative;
    padding: 24px 28px;
    margin: 10px 0 26px 0;
    border-radius: 16px;
    background: linear-gradient(120deg, #101B35 0%, #1D3557 55%, #304B75 100%);
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.employee-page-banner::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 5px;
    height: 100%;
    background: linear-gradient(180deg, #38BDF8, #818CF8);
}

.employee-page-banner h2 {
    margin: 0;
    padding: 0;
    color: #F8FAFC;
    font-size: 28px;
    font-weight: 750;
    letter-spacing: -0.6px;
}

.employee-page-banner p {
    margin: 7px 0 0 0;
    color: #CBD5E1;
    font-size: 14px;
    line-height: 1.6;
}

.employee-page-banner .banner-divider {
    height: 2px;
    width: 100%;
    margin-top: 17px;
    border-radius: 10px;
    background: linear-gradient(
        90deg,
        #38BDF8 0%,
        #818CF8 35%,
        rgba(255, 255, 255, 0.12) 100%
    );
}

@media (hover: hover) {
    .employee-page-banner:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.24);
    }
}

@media (prefers-reduced-motion: reduce) {
    .employee-page-banner {
        transition: none;
    }
}

/* ==================== ANALYSIS PAGE HEADER ==================== */

.analysis-page-banner {
    position: relative;
    overflow: hidden;
    padding: 25px 28px;
    margin: 10px 0 26px 0;
    border-radius: 18px;
    background: linear-gradient(
        120deg,
        #2E1065 0%,
        #4C1D95 48%,
        #6D28D9 100%
    );
    border: 1px solid rgba(196, 181, 253, 0.35);
    box-shadow:
        0 10px 28px rgba(76, 29, 149, 0.18),
        0 3px 8px rgba(46, 16, 101, 0.10);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

/* Violet accent on the left */
.analysis-page-banner::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6px;
    background: linear-gradient(
        180deg,
        #C4B5FD,
        #F0ABFC
    );
}

/* Decorative glow */
.analysis-page-banner::after {
    content: "";
    position: absolute;
    top: -55px;
    right: -35px;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: rgba(196, 181, 253, 0.10);
    pointer-events: none;
}

.analysis-page-banner h2 {
    position: relative;
    z-index: 1;
    margin: 0;
    padding: 0;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif;
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -0.7px;
    line-height: 1.4;
}

.analysis-page-banner p {
    position: relative;
    z-index: 1;
    margin: 7px 0 0 0;
    padding: 0;
    color: #E9D5FF !important;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.7;
}

/* Elegant divider */
.analysis-page-banner .analysis-header-divider {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 2px;
    margin-top: 18px;
    border-radius: 10px;
    background: linear-gradient(
        90deg,
        #C4B5FD 0%,
        #F0ABFC 35%,
        rgba(255, 255, 255, 0.12) 100%
    );
}

@media (hover: hover) {
    .analysis-page-banner:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 34px rgba(76, 29, 149, 0.25);
    }
}

@media (max-width: 768px) {
    .analysis-page-banner {
        padding: 20px;
        border-radius: 14px;
    }

    .analysis-page-banner h2 {
        font-size: 24px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .analysis-page-banner {
        transition: none;
    }
}

/* ==================== DEPARTMENTS PAGE HEADER ==================== */

.departments-page-banner {
    position: relative;
    overflow: hidden;
    padding: 25px 28px;
    margin: 10px 0 26px 0;
    border-radius: 18px;
    background: linear-gradient(
        120deg,
        #064E3B 0%,
        #047857 50%,
        #0F766E 100%
    );
    border: 1px solid rgba(110, 231, 183, 0.35);
    box-shadow:
        0 10px 28px rgba(6, 78, 59, 0.18),
        0 3px 8px rgba(6, 78, 59, 0.10);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

/* Green accent on the left */
.departments-page-banner::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6px;
    background: linear-gradient(
        180deg,
        #6EE7B7,
        #67E8F9
    );
}

/* Soft decorative circle */
.departments-page-banner::after {
    content: "";
    position: absolute;
    top: -55px;
    right: -35px;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: rgba(167, 243, 208, 0.10);
    pointer-events: none;
}

.departments-page-banner h2 {
    position: relative;
    z-index: 1;
    margin: 0;
    padding: 0;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif;
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -0.7px;
    line-height: 1.4;
}

.departments-page-banner p {
    position: relative;
    z-index: 1;
    margin: 7px 0 0 0;
    padding: 0;
    color: #D1FAE5 !important;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.7;
}

.departments-page-banner .departments-header-divider {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 2px;
    margin-top: 18px;
    border-radius: 10px;
    background: linear-gradient(
        90deg,
        #6EE7B7 0%,
        #67E8F9 35%,
        rgba(255, 255, 255, 0.12) 100%
    );
}

@media (hover: hover) {
    .departments-page-banner:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 34px rgba(6, 78, 59, 0.25);
    }
}

@media (max-width: 768px) {
    .departments-page-banner {
        padding: 20px;
        border-radius: 14px;
    }

    .departments-page-banner h2 {
        font-size: 24px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .departments-page-banner {
        transition: none;
    }
}

/* ==================== UPLOAD & EXPORT PAGE HEADER ==================== */

.upload-export-page-banner {
    position: relative;
    overflow: hidden;
    padding: 25px 28px;
    margin: 10px 0 26px 0;
    border-radius: 18px;
    background: linear-gradient(
        120deg,
        #431407 0%,
        #7C2D12 48%,
        #C2410C 100%
    );
    border: 1px solid rgba(253, 186, 116, 0.35);
    box-shadow:
        0 10px 28px rgba(124, 45, 18, 0.20),
        0 3px 8px rgba(67, 20, 7, 0.10);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

/* Orange accent on the left */
.upload-export-page-banner::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6px;
    background: linear-gradient(
        180deg,
        #FDBA74,
        #FDE68A
    );
}

/* Soft decorative circle */
.upload-export-page-banner::after {
    content: "";
    position: absolute;
    top: -65px;
    right: -35px;
    width: 190px;
    height: 190px;
    border-radius: 50%;
    background: rgba(253, 186, 116, 0.10);
    pointer-events: none;
}

.upload-export-page-banner h2 {
    position: relative;
    z-index: 1;
    margin: 0;
    padding: 0;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif;
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -0.7px;
    line-height: 1.4;
}

.upload-export-page-banner p {
    position: relative;
    z-index: 1;
    margin: 7px 0 0 0;
    padding: 0;
    color: #FFEDD5 !important;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.7;
}

/* Orange-gold divider */
.upload-export-page-banner .upload-export-header-divider {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 2px;
    margin-top: 18px;
    border-radius: 10px;
    background: linear-gradient(
        90deg,
        #FDBA74 0%,
        #FDE68A 35%,
        rgba(255, 255, 255, 0.12) 100%
    );
}

@media (hover: hover) {
    .upload-export-page-banner:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 34px rgba(124, 45, 18, 0.28);
    }
}

@media (max-width: 768px) {
    .upload-export-page-banner {
        padding: 20px;
        border-radius: 14px;
    }

    .upload-export-page-banner h2 {
        font-size: 24px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .upload-export-page-banner {
        transition: none;
    }
}


/* =========================================
   USER DATA — PREMIUM TEAL & BLUE THEME
========================================= */

.user-data-page-banner {
    position: relative;
    overflow: hidden;
    padding: 30px 34px;
    margin: 8px 0 28px 0;
    border-radius: 20px;

    background: linear-gradient(
        125deg,
        #042F2E 0%,
        #075985 58%,
        #0E7490 100%
    );

    border: 1px solid rgba(103, 232, 249, 0.32);

    box-shadow:
        0 12px 30px rgba(8, 47, 73, 0.24),
        0 4px 12px rgba(6, 182, 212, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.12);

    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease,
        border-color 0.3s ease;
}

/* Decorative cyan accent */
.user-data-page-banner::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 7px;
    height: 100%;

    background: linear-gradient(
        180deg,
        #67E8F9,
        #2DD4BF,
        #38BDF8
    );

    box-shadow: 0 0 18px rgba(103, 232, 249, 0.55);
}

/* Decorative glow in the top-right corner */
.user-data-page-banner::after {
    content: "";
    position: absolute;
    width: 180px;
    height: 180px;
    right: -65px;
    top: -90px;
    border-radius: 50%;

    background: rgba(103, 232, 249, 0.12);
    border: 1px solid rgba(165, 243, 252, 0.15);

    box-shadow:
        0 0 50px rgba(34, 211, 238, 0.12);
    
    pointer-events: none;
}

.user-data-page-banner:hover {
    transform: translateY(-3px);

    border-color: rgba(103, 232, 249, 0.65);

    box-shadow:
        0 18px 38px rgba(8, 47, 73, 0.30),
        0 6px 20px rgba(6, 182, 212, 0.20),
        inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

/* Main heading */
.user-data-page-banner h2 {
    position: relative;
    z-index: 1;

    margin: 0 0 10px 0;
    padding: 0;

    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.8px;
    line-height: 1.3;

    text-shadow: 0 3px 12px rgba(0, 0, 0, 0.20);
}

/* Subtitle */
.user-data-page-banner p {
    position: relative;
    z-index: 1;

    margin: 0;
    max-width: 760px;

    color: #CFFAFE !important;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 15px;
    font-weight: 400;
    line-height: 1.7;
    letter-spacing: 0.2px;
}

/* Bottom accent divider */
.user-data-header-divider {
    position: relative;
    z-index: 1;

    width: 92px;
    height: 4px;
    margin-top: 19px;
    border-radius: 20px;

    background: linear-gradient(
        90deg,
        #67E8F9,
        #2DD4BF,
        #38BDF8
    );

    box-shadow: 0 0 12px rgba(103, 232, 249, 0.35);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .user-data-page-banner {
        padding: 24px 23px;
        margin-bottom: 22px;
        border-radius: 16px;
    }

    .user-data-page-banner h2 {
        font-size: 24px;
    }

    .user-data-page-banner p {
        font-size: 14px;
    }

    .user-data-page-banner::after {
        width: 120px;
        height: 120px;
        right: -50px;
        top: -60px;
    }
}


/* ==========================================
   USER DATA — REGISTRATION DETAILS VISIBILITY
========================================== */

/* Registration section headings */
.user-data-page-banner ~ div h1,
.user-data-page-banner ~ div h2,
.user-data-page-banner ~ div h3 {
    color: #0F766E !important;
    font-weight: 750 !important;
}

/* Form labels and field labels */
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stWidgetLabel"] label,
.stApp .stTextInput label,
.stApp .stNumberInput label,
.stApp .stSelectbox label,
.stApp .stDateInput label,
.stApp .stTextArea label,
.stApp .stRadio label,
.stApp .stCheckbox label {
    color: #164E63 !important;
    font-weight: 650 !important;
    opacity: 1 !important;
}

/* Text input fields */
.stApp div[data-baseweb="input"] input,
.stApp div[data-baseweb="textarea"] textarea,
.stApp div[data-baseweb="select"] input {
    color: #102A43 !important;
    -webkit-text-fill-color: #102A43 !important;
    background-color: #FFFFFF !important;
    caret-color: #0891B2 !important;
    font-weight: 500 !important;
}

/* Input field backgrounds and borders */
.stApp div[data-baseweb="input"],
.stApp div[data-baseweb="textarea"],
.stApp div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #94C5D3 !important;
    border-radius: 9px !important;
}

/* Focused input fields */
.stApp div[data-baseweb="input"]:focus-within,
.stApp div[data-baseweb="textarea"]:focus-within,
.stApp div[data-baseweb="select"]:focus-within {
    border-color: #0891B2 !important;
    box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.15) !important;
}

/* Placeholder text */
.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
    opacity: 1 !important;
}

/* Registration details and informational text */
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li {
    line-height: 1.7;
}

/* Captions and secondary information */
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] p {
    color: #475569 !important;
    opacity: 1 !important;
}

/* Information boxes */
.stApp [data-testid="stAlert"] {
    background-color: #ECFEFF !important;
    border: 1px solid #67C8D7 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 14px rgba(8, 47, 73, 0.08) !important;
}

.stApp [data-testid="stAlert"] p,
.stApp [data-testid="stAlert"] li {
    color: #164E63 !important;
    opacity: 1 !important;
}

/* Registration data displayed in bordered containers */
.stApp [data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #B6DCE5 !important;
    border-radius: 14px !important;
    box-shadow: 0 5px 16px rgba(8, 47, 73, 0.07) !important;
}

/* Selectbox selected text and dropdown indicators */
.stApp [data-baseweb="select"] *,
.stApp [data-baseweb="select"] svg {
    color: #102A43 !important;
}

/* Ensure disabled/read-only values remain readable */
.stApp input:disabled,
.stApp textarea:disabled {
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    opacity: 1 !important;
    background-color: #F1F5F9 !important;
}

/* Responsive spacing */
@media (max-width: 768px) {
    .stApp [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 10px !important;
    }

    .stApp [data-testid="stWidgetLabel"] p {
        font-size: 14px !important;
    }
}



</style>
""", unsafe_allow_html=True)


def banner(title, subtitle=""):
    st.markdown(f'<div class="banner"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


# ============================================================
# INTERACTIVE DASHBOARD KPI CARDS
# ============================================================

@st.dialog("Statistical Measure")
def show_metric_dialog(label, value, description, formula):

    st.metric(label, value)

    st.markdown("### About this metric")
    st.write(description)

    st.markdown("### How is it calculated?")
    st.info(formula)

    if st.button("Close", key="close_metric_dialog", use_container_width=True):
        st.session_state.pop("selected_metric", None)
        st.rerun()
# ============================================================
# FULLY CLICKABLE KPI CARDS
# ============================================================

def kpis(items):
    """Make the entire KPI card clickable."""

    import html

    descriptions = {
        "Average salary": (
            "The average salary of employees matching the current dashboard filters.",
            "Average Salary = Total Salary of Employees / Number of Employees"
        ),
        "Median salary": (
            "The middle salary when employee salaries are arranged in ascending order. "
            "It helps identify the typical salary without being heavily affected by "
            "extremely high or low salaries.",
            "Sort all salaries. For an odd number of employees, select the middle value. "
            "For an even number, calculate the average of the two middle values."
        ),
        "Minimum salary": (
            "The lowest salary among employees matching the current dashboard filters.",
            "Minimum Salary = The smallest salary in the selected employee records."
        ),
        "Maximum salary": (
            "The highest salary among employees matching the current dashboard filters.",
            "Maximum Salary = The largest salary in the selected employee records."
        ),
        "Average performance": (
            "The average performance score of employees matching the current dashboard filters.",
            "Average Performance = Total Performance Score / Number of Employees"
        ),
        "Maximum performance": (
            "The highest performance score among employees matching the current dashboard filters.",
            "Maximum Performance = The largest performance score in the selected records."
        )
    }

    card_colors = [
        "#2563EB",
        "#059669",
        "#7C3AED",
        "#EA580C",
        "#DB2777",
        "#0891B2",
        "#0F766E"
    ]

    # Style the actual buttons as KPI cards.
    st.markdown(
        """
        <style>
        /* Each KPI button becomes a complete clickable card */
        div[class*="st-key-kpi_card_"] button {
            width: 100% !important;
            min-height: 132px !important;
            height: auto !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            text-align: left !important;
            white-space: pre-wrap !important;
            overflow-wrap: anywhere !important;
            padding: 20px 18px !important;
            border-radius: 15px !important;
            border: 1px solid #D8E2EF !important;
            border-top: 4px solid var(--kpi-accent, #2563EB) !important;
            background: linear-gradient(
                135deg,
                #FFFFFF 0%,
                #EFF6FF 100%
            ) !important;
            box-shadow: 0 5px 16px rgba(15, 23, 42, 0.07) !important;
            transition: all 0.22s ease-in-out !important;
        }

        /* Hover over any part of the card */
        div[class*="st-key-kpi_card_"] button:hover {
            transform: translateY(-4px) !important;
            border-color: var(--kpi-accent, #2563EB) !important;
            box-shadow: 0 12px 25px rgba(15, 23, 42, 0.14) !important;
            background: linear-gradient(
                135deg,
                #EFF6FF 0%,
                #DBEAFE 100%
            ) !important;
        }

        /* Make card text readable */
        div[class*="st-key-kpi_card_"] button p {
            color: #0F172A !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            line-height: 1.8 !important;
            white-space: pre-wrap !important;
        }

        /* Click feedback */
        div[class*="st-key-kpi_card_"] button:active {
            transform: scale(0.98) !important;
        }

        @media (max-width: 768px) {
            div[class*="st-key-kpi_card_"] button {
                min-height: 105px !important;
                padding: 14px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    columns = st.columns(len(items), gap="medium")

    for index, (col, item) in enumerate(zip(columns, items)):
        label, value = item
        accent = card_colors[index % len(card_colors)]

        # The whole card is one Streamlit button.
        with col:
            with st.container(key=f"kpi_card_{items[0][0].replace(' ', '_').lower()}_{index}"):

                st.markdown(
                    f"""
                    <style>
                    div.st-key-kpi_card_{index} {{
                        --kpi-accent: {accent};
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                card_text = (
                    f"**{label}**\n\n"
                    f"{value}\n\n"
                    f"{'Click to view employee records' if label == 'Employees' else 'Click anywhere to view details →'}"
                )

                clicked = st.button(
                    card_text,
                    key=f"kpi_button_{items[0][0].replace(' ', '_').lower()}_{index}",
                    use_container_width=True
                )

                if clicked:
                    if label == "Employees":
                        # Apply Dashboard filters when opening Employees.
                        st.session_state["apply_dashboard_filters_to_employees"] = True
                
                        # Transfer Department and Designation filters.
                        dashboard_department = st.session_state.get(
                            "dashboard_department", "All Departments"
                        )
                        dashboard_designation = st.session_state.get(
                            "dashboard_designation", "All Designations"
                        )
                
                        st.session_state["employees_department"] = (
                            [] if dashboard_department == "All Departments"
                            else [dashboard_department]
                        )
                
                        st.session_state["employees_designation"] = (
                            [] if dashboard_designation == "All Designations"
                            else [dashboard_designation]
                        )
                
                        # Transfer Experience range.
                        st.session_state["employees_min_exp"] = int(
                            st.session_state.get("dashboard_experience_min", 0)
                        )
                
                        st.session_state["employees_max_exp"] = int(
                            st.session_state.get("dashboard_experience_max", 0)
                        )
                
                        # Navigate to Employees using your existing navigation.
                        st.session_state["navigate_to_employees"] = True
                        st.rerun()
                
                    else:
                        description, formula = descriptions.get(
                            label,
                            (
                                "This statistic summarizes the employee data "
                                "currently selected in the dashboard.",
                                "The value is calculated using the employee "
                                "records included in the current filters."
                            )
                        )
                
                        st.session_state["selected_metric"] = {
                            "label": label,
                            "value": value,
                            "description": description,
                            "formula": formula
                        }
                
                        st.rerun()

                    
    # Display the selected metric popup.
    selected = st.session_state.get("selected_metric")

    if selected:
        show_metric_dialog(
            selected["label"],
            selected["value"],
            selected["description"],
            selected["formula"]
        )
def auth_page():
    # Login page styling
    st.markdown("""
    <style>
    .stApp {
    background:
        linear-gradient(
            135deg,
            rgba(248, 250, 252, 0.94),
            rgba(226, 232, 240, 0.88)
        ),
        url("https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1920&q=80");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    min-height: 100vh;
    }    
    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    .login-brand {
        background: linear-gradient(145deg, #14213d, #233e70);
        color: white;
        padding: 45px 32px;
        border-radius: 22px 0 0 22px;
        min-height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 15px 40px rgba(20, 33, 61, 0.15);
    }

    .login-brand h1 {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .login-brand p {
        color: #dbeafe;
        font-size: 1.05rem;
        line-height: 1.8;
    }

    .login-brand .brand-icon {
        font-size: 3.5rem;
        margin-bottom: 15px;
    }

    .login-card {
        background: rgba(255, 255, 255, 0.92);
        padding: 25px 28px;
        border: 1px solid #e2e8f0;
        border-radius: 0 22px 22px 0;
        min-height: 450px;
        box-shadow: 0 15px 40px rgba(20, 33, 61, 0.10);
    }

    .login-heading {
        color: #14213d;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .login-description {
        color: #64748b;
        margin-bottom: 20px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        min-height: 45px;
        font-weight: 600;
        border: none;
        background: linear-gradient(90deg, #2563eb, #0f766e);
        color: white;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 18px rgba(37, 99, 235, 0.2);
        color: white;
    }

    [data-testid="stTextInput"] input {
        border-radius: 9px;
        border: 1px solid #cbd5e1;
    }

    [data-testid="stTabs"] button {
        font-weight: 600;
    }

    .security-note {
        font-size: 0.8rem;
        color: #64748b;
        text-align: center;
        margin-top: 20px;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-top: 1rem;
        }

        .login-brand {
            border-radius: 18px 18px 0 0;
            min-height: auto;
            padding: 25px;
        }

        .login-card {
            border-radius: 0 0 18px 18px;
            min-height: auto;
            padding: 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Two-column layout
    left, right = st.columns([1, 1.15], gap="small")

    with left:
        st.markdown("""
        <div class="login-brand">
            <div class="brand-icon">📊</div>
            <h1>StaffMetrics</h1>
            <p>
                Turn employee data into meaningful insights.
                Analyze salaries, monitor performance, and
                make better workforce decisions.
            </p>
            <p>
                ✓ Employee analytics<br>
                ✓ Salary insights<br>
                ✓ Performance reports<br>
                ✓ Workforce management
            </p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="login-card">
            <div class="login-heading">Welcome back!</div>
            <div class="login-description">
                Sign in to access your analytics dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)

        login_tab, register_tab = st.tabs(
            ["🔐 Sign in", "✨ Create account"]
        )

        # ---------------- LOGIN ----------------
        with login_tab:
            st.subheader("Sign in to your account")

            login_id = st.text_input(
                "Username or email",
                key="login_username"
            )

            show_login_password = st.checkbox(
                "Show password",
                key="show_login_password"
            )

            login_password = st.text_input(
                "Password",
                type="default" if show_login_password else "password",
                key="login_password"
            )

            remember_me = st.checkbox(
                "Remember me on this session",
                key="remember_me"
            )

            if st.button("Sign in", key="login_button"):
                if not login_id.strip() or not login_password:
                    st.warning("Enter your username/email and password.")
                else:
                    user = auth.login(login_id, login_password)

                    if user:
                        st.session_state.user = user

                        # This flag records the user's preference for
                        # the current Streamlit session only.
                        

                        st.rerun()
                    else:
                        st.error(
                            "The username/email or password is incorrect."
                        )

            with st.expander("Forgot your password?"):
                st.write(
                    "Password recovery requires a configured email "
                    "or authentication provider."
                )
                st.info(
                    "The password-reset service must be configured "
                    "before a recovery email can be sent."
                )

        # ---------------- REGISTRATION ----------------
        with register_tab:
            st.subheader("Create your account")

            full_name = st.text_input(
                "Full name",
                key="register_full_name"
            )

            email = st.text_input(
                "Email address",
                key="register_email"
            )

            username = st.text_input(
                "Choose a username",
                key="register_username"
            )

            show_register_password = st.checkbox(
                "Show registration passwords",
                key="show_register_password"
            )

            password_type = (
                "default" if show_register_password else "password"
            )

            password = st.text_input(
                "Create password",
                type=password_type,
                key="register_password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type=password_type,
                key="register_confirm_password"
            )

            # Password-strength feedback
            if password:
                import re

                score = 0

                if len(password) >= 8:
                    score += 1
                if re.search(r"[A-Z]", password):
                    score += 1
                if re.search(r"[a-z]", password):
                    score += 1
                if re.search(r"[0-9]", password):
                    score += 1
                if re.search(r"[^A-Za-z0-9]", password):
                    score += 1

                if score <= 2:
                    st.warning("Password strength: Weak")
                elif score <= 4:
                    st.info("Password strength: Moderate")
                else:
                    st.success("Password strength: Strong")

            st.caption(
                "Use at least 8 characters. A combination of "
                "uppercase letters, lowercase letters, numbers, "
                "and symbols is recommended."
            )

            if st.button("Create account", key="register_button"):
                if not all([
                    full_name.strip(),
                    email.strip(),
                    username.strip(),
                    password,
                    confirm_password
                ]):
                    st.warning("Please complete all the fields.")

                elif password != confirm_password:
                    st.error("The passwords do not match.")

                elif len(password) < 8:
                    st.error(
                        "Your password must contain at least 8 characters."
                    )

                else:
                    success, message = auth.register(
                        username,
                        email,
                        full_name,
                        password
                    )

                    if success:
                        st.success(message)
                        st.info(
                            "Your account has been created. "
                            "Switch to Sign in to continue."
                        )
                    else:
                        st.error(message)

        st.markdown(
            '<div class="security-note">'
            'StaffMetrics · Employee Salary & Performance Analysis'
            '</div>',
            unsafe_allow_html=True
        )
def show(fig):
    st.pyplot(fig)
    plt.close(fig)



@st.dialog("KPI Details")
def show_metric_popup(title, value, description):
    st.metric(title, value)
    st.write(description)

    if st.button("Close", use_container_width=True):
        st.rerun()

def page_dashboard(df):
    # ==================== EXECUTIVE DASHBOARD WELCOME BANNER ====================

    user = st.session_state.user
    display_name = user.get("full_name") or user.get("username") or "User"

    st.markdown("""
    <style>
    .executive-banner {
        position: relative;
        overflow: hidden;
        padding: 30px 34px;
        margin: 5px 0 28px 0;
        border-radius: 20px;
        background: linear-gradient(
            120deg,
            #0F172A 0%,
            #1E3A8A 55%,
            #0F766E 100%
        );
        border: 1px solid rgba(147, 197, 253, 0.35);
        box-shadow:
            0 12px 30px rgba(15, 23, 42, 0.20),
            0 4px 10px rgba(37, 99, 235, 0.12);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .executive-banner:hover {
        transform: translateY(-2px);
        box-shadow:
            0 18px 38px rgba(15, 23, 42, 0.25),
            0 6px 16px rgba(37, 99, 235, 0.18);
    }

    .executive-banner::before {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        top: -125px;
        right: -45px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.08);
    }

    .executive-banner::after {
        content: "";
        position: absolute;
        width: 150px;
        height: 150px;
        bottom: -105px;
        right: 115px;
        border-radius: 50%;
        background: rgba(45, 212, 191, 0.13);
    }

    .executive-banner-content {
        position: relative;
        z-index: 1;
    }

    .executive-eyebrow {
        margin-bottom: 8px;
        color: #99F6E4 !important;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .executive-title {
        margin: 0 0 12px 0;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
        font-size: clamp(26px, 3vw, 36px);
        font-weight: 800;
        line-height: 1.25;
        letter-spacing: -0.8px;
    }

    .executive-welcome {
        margin: 0;
        color: #DBEAFE !important;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 16px;
        font-weight: 500;
        line-height: 1.6;
    }

    .executive-welcome strong {
        color: #FFFFFF !important;
        font-weight: 700;
    }

    @media (max-width: 640px) {
        .executive-banner {
            padding: 24px 20px;
            border-radius: 15px;
        }

        .executive-welcome {
            font-size: 14px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="executive-banner">
            <div class="executive-banner-content">
                <div class="executive-eyebrow">
                    STAFFMETRICS · WORKFORCE INTELLIGENCE
                </div>
                <h1 class="executive-title">
                    Executive Dashboard
                </h1>
                <p class="executive-welcome">
                    Welcome back, <strong>{display_name}</strong>!
                    Here's your employee analytics overview.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Continue with your existing Dashboard Filters section below.


    # ==================== DEPARTMENT & DESIGNATION DROPDOWNS ====================

    c1, c2, c3 = st.columns(3)

    departments = sorted(df["Department"].dropna().unique().tolist())
    designations = sorted(
        df["Designation"].dropna().astype(str).unique().tolist()
    )

    with c1:
        selected_department = st.selectbox(
            "Department",
            ["All Departments"] + departments,
            key="dashboard_department"
        )

    with c2:
        selected_designation = st.selectbox(
            "Designation",
            ["All Designations"] + designations,
            key="dashboard_designation"
        )

    with c3:
        chart_choice = st.selectbox(
            "Chart to display",
            [
                "All charts",
                "Department-wise salary",
                "Salary distribution",
                "Department-wise performance",
                "Salary vs. performance"
            ],
            key="dashboard_chart"
        )

    # ==================== BASIC SALARY RANGE ====================

    salary_values = pd.to_numeric(
        df["Basic_Salary"], errors="coerce"
    ).dropna()

    if salary_values.empty:
        st.warning("Salary data is unavailable.")
        return

    salary_min = float(salary_values.min())
    salary_max = float(salary_values.max())

    st.markdown("**Basic Salary Range**")

    s1, s2 = st.columns(2)

    with s1:
        selected_salary_min = st.number_input(
            "Minimum Salary",
            min_value=salary_min,
            max_value=salary_max,
            value=salary_min,
            key="dashboard_salary_min"
        )

    with s2:
        selected_salary_max = st.number_input(
            "Maximum Salary",
            min_value=salary_min,
            max_value=salary_max,
            value=salary_max,
            key="dashboard_salary_max"
        )

    # ==================== EXPERIENCE RANGE ====================

    experience_values = pd.to_numeric(
        df["Experience_Years"], errors="coerce"
    ).dropna()

    if experience_values.empty:
        st.warning("Experience data is unavailable.")
        return

    exp_min = 0
    exp_max = max(0, int(experience_values.max()))

    st.markdown("**Experience Range (Years)**")

    e1, e2 = st.columns(2)

    with e1:
        selected_experience_min = st.number_input(
            "Minimum Experience",
            min_value=exp_min,
            max_value=exp_max,
            value=exp_min,
            step=1,
            key="dashboard_experience_min"
        )

    with e2:
        selected_experience_max = st.number_input(
            "Maximum Experience",
            min_value=exp_min,
            max_value=exp_max,
            value=exp_max,
            step=1,
            key="dashboard_experience_max"
        )

    # ==================== PERFORMANCE RANGE ====================

    performance_values = pd.to_numeric(
        df["Performance_Score"], errors="coerce"
    ).dropna()

    if performance_values.empty:
        st.warning("Performance data is unavailable.")
        return

    perf_min = float(performance_values.min())
    perf_max = float(performance_values.max())

    st.markdown("**Performance Score Range**")

    p1, p2 = st.columns(2)

    with p1:
        selected_performance_min = st.number_input(
            "Minimum Performance",
            min_value=perf_min,
            max_value=perf_max,
            value=perf_min,
            key="dashboard_performance_min"
        )

    with p2:
        selected_performance_max = st.number_input(
            "Maximum Performance",
            min_value=perf_min,
            max_value=perf_max,
            value=perf_max,
            key="dashboard_performance_max"
        )

    # ==================== VALIDATE RANGES ====================

    if selected_salary_min > selected_salary_max:
        st.error("Minimum salary cannot exceed maximum salary.")
        return

    if selected_experience_min > selected_experience_max:
        st.error("Minimum experience cannot exceed maximum experience.")
        return

    if selected_performance_min > selected_performance_max:
        st.error("Minimum performance cannot exceed maximum performance.")
        return

    # ==================== APPLY FILTERS ====================

    filtered_df = df.copy()

    filtered_df["Basic_Salary"] = pd.to_numeric(
        filtered_df["Basic_Salary"], errors="coerce"
    )

    filtered_df["Experience_Years"] = pd.to_numeric(
        filtered_df["Experience_Years"], errors="coerce"
    )

    filtered_df["Performance_Score"] = pd.to_numeric(
        filtered_df["Performance_Score"], errors="coerce"
    )

    filtered_df = filtered_df[
        filtered_df["Basic_Salary"].between(
            selected_salary_min, selected_salary_max
        )
        & filtered_df["Experience_Years"].between(
            selected_experience_min, selected_experience_max
        )
        & filtered_df["Performance_Score"].between(
            selected_performance_min, selected_performance_max
        )
    ]

    if selected_department != "All Departments":
        filtered_df = filtered_df[
            filtered_df["Department"] == selected_department
        ]

    if selected_designation != "All Designations":
        filtered_df = filtered_df[
            filtered_df["Designation"].astype(str)
            == selected_designation
        ]

    # ==================== FILTER RESULTS ====================

    if filtered_df.empty:
        st.warning("No employees match your selected filters.")
        return

    st.caption(
        f"Showing {len(filtered_df):,} of {len(df):,} employee records."
    )

    # ==================== KPI CARDS ====================

    k = an.kpis(filtered_df)

    kpis([
        ("Employees", f"{k['total_employees']:,}"),
        ("Average salary", f"{k['average_salary']:,.0f}"),
        ("Median salary", f"{k['median_salary']:,.0f}"),
        ("Minimum salary", f"{k['minimum_salary']:,.0f}")
    ])

    st.write("")

    kpis([
        ("Maximum salary", f"{k['maximum_salary']:,.0f}"),
        ("Average performance", f"{k['average_performance']:.2f}"),
        ("Maximum performance", f"{k['maximum_performance']:.2f}")
    ])

    # ==================== AUTOMATED INSIGHTS ====================

    st.subheader("Automated Insights")

    for line in an.insights(filtered_df):
        st.info(line)

    # ==================== VISUAL ANALYTICS ====================

    st.subheader("Visual Analytics")

    chart_functions = {
        "Department-wise salary": an.fig_dept_salary,
        "Salary distribution": an.fig_salary_dist,
        "Department-wise performance": an.fig_dept_perf,
        "Salary vs. performance": an.fig_salary_vs_perf
    }

    if chart_choice == "All charts":
        a, b = st.columns(2)

        with a:
            show(an.fig_dept_salary(filtered_df))
            show(an.fig_salary_dist(filtered_df))

        with b:
            show(an.fig_dept_perf(filtered_df))
            show(an.fig_salary_vs_perf(filtered_df))

    else:
        show(chart_functions[chart_choice](filtered_df))

        
def manage_employees(df):
    uid = st.session_state.user["id"]
    with st.expander("Add an employee"), st.form("add_emp"):
        c = st.columns(3)
        e = {"Employee_ID": c[0].text_input("Employee ID"), "Name": c[1].text_input("Name"), "Age": c[2].number_input("Age", 18, 70, 30),
             "Gender": c[0].selectbox("Gender", ["Female", "Male"]), "Department": c[1].selectbox("Department", sorted(df["Department"].unique())),
             "Designation": c[2].text_input("Designation"), "Experience_Years": c[0].number_input("Experience (years)", 0, 45, 3),
             "Joining_Year": c[1].number_input("Joining year", 1990, 2030, 2024), "Basic_Salary": c[2].number_input("Basic salary", 1.0, 1e7, 50000.0),
             "Performance_Score": c[1].number_input("Performance score (0-5)", 0.0, 5.0, 3.0, 0.5)}
        if st.form_submit_button("Add employee"):
            try:
                db.add_employee(e)
                db.log_activity(uid, f"added employee {e['Employee_ID']}")
                st.success("Employee added. It appears in the table the next time the page refreshes.")
            except Exception as ex:
                st.error(f"The employee could not be added: {ex}")
    with st.expander("Delete an employee"):
        who = st.selectbox("Employee", df["Employee_ID"])
        if st.button("Delete employee"):
            db.delete_employee(who)
            db.log_activity(uid, f"deleted employee {who}")
            st.rerun()


        
def manage_employees(df):
    uid = st.session_state.user["id"]
    with st.expander("Add an employee"), st.form("add_emp"):
        c = st.columns(3)
        e = {"Employee_ID": c[0].text_input("Employee ID"), "Name": c[1].text_input("Name"), "Age": c[2].number_input("Age", 18, 70, 30),
             "Gender": c[0].selectbox("Gender", ["Female", "Male"]), "Department": c[1].selectbox("Department", sorted(df["Department"].unique())),
             "Designation": c[2].text_input("Designation"), "Experience_Years": c[0].number_input("Experience (years)", 0, 45, 3),
             "Joining_Year": c[1].number_input("Joining year", 1990, 2030, 2024), "Basic_Salary": c[2].number_input("Basic salary", 1.0, 1e7, 50000.0),
             "Performance_Score": c[1].number_input("Performance score (0-5)", 0.0, 5.0, 3.0, 0.5)}
        if st.form_submit_button("Add employee"):
            try:
                db.add_employee(e)
                db.log_activity(uid, f"added employee {e['Employee_ID']}")
                st.success("Employee added. It appears in the table the next time the page refreshes.")
            except Exception as ex:
                st.error(f"The employee could not be added: {ex}")
    with st.expander("Delete an employee"):
        who = st.selectbox("Employee", df["Employee_ID"])
        if st.button("Delete employee"):
            db.delete_employee(who)
            db.log_activity(uid, f"deleted employee {who}")
            st.rerun()




def page_employees(df, is_db):
    st.markdown("""
    <div class="employee-page-banner">
        <h2>Employees</h2>
        <p>Search, filter and manage employee records</p>
        <div class="banner-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    # ==================== FILTER OPTIONS ====================

    c1, c2, c3 = st.columns(3)

    dept = c1.multiselect(
        "Department",
        sorted(df["Department"].dropna().unique()),
        key="employees_department"
    )

    role = c2.multiselect(
        "Designation",
        sorted(df["Designation"].dropna().astype(str).unique()),
        key="employees_designation"
    )

    # ==================== DYNAMIC EXPERIENCE RANGE ====================

    experience = pd.to_numeric(
        df["Experience_Years"],
        errors="coerce"
    ).dropna()

    if experience.empty:
        st.warning("Experience data is not available.")
        return

    min_exp = 0
    max_exp = max(0, int(experience.max()))

    with c3:
        st.markdown("**Experience Range (Years)**")

        selected_min_exp = st.number_input(
            "From (Minimum)",
            min_value=min_exp,
            max_value=max_exp,
            value=min_exp,
            step=1,
            key="employees_min_exp"
        )

        selected_max_exp = st.number_input(
            "To (Maximum)",
            min_value=min_exp,
            max_value=max_exp,
            value=max_exp,
            step=1,
            key="employees_max_exp"
        )

    # ==================== SEARCH ====================

    q = st.text_input("Search by ID or name")

    # ==================== VALIDATE EXPERIENCE ====================

    if selected_min_exp > selected_max_exp:
        st.error(
            "Minimum experience cannot be greater than maximum experience."
        )
        return

    # ==================== INITIALIZE DATAFRAME ====================

    f = df.copy()

    f["Experience_Years"] = pd.to_numeric(
        f["Experience_Years"],
        errors="coerce"
    )

    # Convert salary and performance columns to numeric when available.
    if "Basic_Salary" in f.columns:
        f["Basic_Salary"] = pd.to_numeric(
            f["Basic_Salary"],
            errors="coerce"
        )

    if "Performance_Score" in f.columns:
        f["Performance_Score"] = pd.to_numeric(
            f["Performance_Score"],
            errors="coerce"
        )

    # ==================== APPLY EXPERIENCE FILTER ====================

    f = f[
        f["Experience_Years"].between(
            selected_min_exp,
            selected_max_exp,
            inclusive="both"
        )
    ]

    # ==================== APPLY DEPARTMENT FILTER ====================

    if dept:
        f = f[f["Department"].isin(dept)]

    # ==================== APPLY DESIGNATION FILTER ====================

    if role:
        f = f[f["Designation"].astype(str).isin(role)]

    # ==================== APPLY DASHBOARD FILTERS ====================

    if st.session_state.get(
        "apply_dashboard_filters_to_employees", False
    ):
        dashboard_salary_min = st.session_state.get(
            "dashboard_salary_min"
        )
        dashboard_salary_max = st.session_state.get(
            "dashboard_salary_max"
        )
        dashboard_performance_min = st.session_state.get(
            "dashboard_performance_min"
        )
        dashboard_performance_max = st.session_state.get(
            "dashboard_performance_max"
        )

        # Apply salary range selected on the Dashboard.
        if (
            dashboard_salary_min is not None
            and dashboard_salary_max is not None
            and "Basic_Salary" in f.columns
        ):
            f = f[
                f["Basic_Salary"].between(
                    dashboard_salary_min,
                    dashboard_salary_max,
                    inclusive="both"
                )
            ]

        # Apply performance range selected on the Dashboard.
        if (
            dashboard_performance_min is not None
            and dashboard_performance_max is not None
            and "Performance_Score" in f.columns
        ):
            f = f[
                f["Performance_Score"].between(
                    dashboard_performance_min,
                    dashboard_performance_max,
                    inclusive="both"
                )
            ]

        st.info(
            "Dashboard salary and performance filters are applied "
            "to these employee records."
        )

    # ==================== APPLY SEARCH ====================

    if q:
        q = q.strip()

        f = f[
            f["Employee_ID"].astype(str).str.contains(
                q, case=False, na=False, regex=False
            )
            |
            f["Name"].astype(str).str.contains(
                q, case=False, na=False, regex=False
            )
        ]

    # ==================== DISPLAY RESULTS ====================

    st.caption(f"{len(f)} employees found")

    st.dataframe(
        f,
        hide_index=True,
        use_container_width=True
    )

    # ==================== EXPORT ====================

    st.download_button(
        "Download filtered records (CSV)",
        data=f.to_csv(index=False).encode("utf-8"),
        file_name="employees_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ==================== ADMIN MANAGEMENT ====================

    if is_db and st.session_state.user["role"] == "admin":
        manage_employees(df)



def page_analysis(df):
    st.markdown("""
    <div class="analysis-page-banner">
        <h2>Employee Analytics</h2>
        <p>Notebook-aligned salary, performance, workforce and productivity analysis</p>
        <div class="analysis-header-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    # Filters apply consistently to every analysis on this page.
        # ============================================================
    # ANALYSIS FILTERS
    # Department: Dropdown
    # Job Role: Dropdown (dependent on Department)
    # Experience: Editable Min and Max fields
    # ============================================================

    filtered = df.copy()

    # Clean filter columns
    if "Department" in filtered.columns:
        filtered["Department"] = (
            filtered["Department"].fillna("Unknown").astype(str)
        )

    if "Designation" in filtered.columns:
        filtered["Designation"] = (
            filtered["Designation"].fillna("Unknown").astype(str)
        )

    # Three-part filter layout
    department_col, role_col, experience_col = st.columns([1, 1, 1.5])

    # ------------------------------------------------------------
    # 1. DEPARTMENT DROPDOWN
    # ------------------------------------------------------------
    with department_col:
        if "Department" in filtered.columns:
            departments = sorted(filtered["Department"].unique().tolist())

            department_options = ["All Departments"] + departments

            selected_department = st.selectbox(
                "🏢 Department",
                options=department_options,
                index=0,
                key="analysis_department_dropdown",
            )

            if selected_department != "All Departments":
                filtered = filtered[
                    filtered["Department"] == selected_department
                ]
        else:
            selected_department = "All Departments"
            st.caption("Department data unavailable.")

    # ------------------------------------------------------------
    # 2. JOB ROLE DROPDOWN
    # Updates based on the selected department
    # ------------------------------------------------------------
    with role_col:
        if "Designation" in filtered.columns:
            roles = sorted(filtered["Designation"].unique().tolist())

            role_options = ["All Job Roles"] + roles

            selected_role = st.selectbox(
                "💼 Job Role",
                options=role_options,
                index=0,
                key="analysis_job_role_dropdown",
            )

            if selected_role != "All Job Roles":
                filtered = filtered[
                    filtered["Designation"] == selected_role
                ]
        else:
            selected_role = "All Job Roles"
            st.caption("Job role data unavailable.")

    # ------------------------------------------------------------
    # 3. EXPERIENCE MIN AND MAX INPUTS
    # ------------------------------------------------------------
    with experience_col:
        if "Experience_Years" in df.columns:
            all_experience = pd.to_numeric(
                df["Experience_Years"],
                errors="coerce"
            ).dropna()

            if not all_experience.empty:
                experience_min = int(all_experience.min())
                experience_max = int(all_experience.max())

                st.markdown("**⏳ Experience (Years)**")

                min_col, max_col = st.columns(2)

                with min_col:
                    selected_min_experience = st.number_input(
                        "Min",
                        min_value=experience_min,
                        max_value=experience_max,
                        value=experience_min,
                        step=1,
                        key="analysis_min_experience",
                    )

                with max_col:
                    selected_max_experience = st.number_input(
                        "Max",
                        min_value=experience_min,
                        max_value=experience_max,
                        value=experience_max,
                        step=1,
                        key="analysis_max_experience",
                    )

                if selected_min_experience > selected_max_experience:
                    st.warning(
                        "Min experience cannot be greater than Max experience."
                    )
                    return

                filtered_experience = pd.to_numeric(
                    filtered["Experience_Years"],
                    errors="coerce"
                )

                filtered = filtered[
                    filtered_experience.between(
                        selected_min_experience,
                        selected_max_experience
                    )
                ]

            else:
                st.caption("Experience data unavailable.")
        else:
            st.caption("Experience data unavailable.")

    # ------------------------------------------------------------
    # FILTER SUMMARY
    # ------------------------------------------------------------
    st.caption(
        f"📊 Showing analysis for {len(filtered):,} employees "
        "matching your filters."
    )

    st.divider()
    if filtered.empty:
        st.warning("No employees match the selected filters. Change the filters to see analysis.")
        return

    # KPI row. Bonus is intentionally excluded from all analysis.
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Employees analysed", f"{len(filtered):,}")
    if "Basic_Salary" in filtered:
        k2.metric("Average salary", f"₹{pd.to_numeric(filtered['Basic_Salary'], errors='coerce').mean():,.0f}")
        k3.metric("Median salary", f"₹{pd.to_numeric(filtered['Basic_Salary'], errors='coerce').median():,.0f}")
    if "Performance_Score" in filtered:
        k4.metric("Average performance", f"{pd.to_numeric(filtered['Performance_Score'], errors='coerce').mean():.2f} / 5")

    salary_tab, performance_tab, workforce_tab, productivity_tab, correlation_tab = st.tabs([
        "💰 Salary", "⭐ Performance", "👥 Workforce", "📈 Attendance & Productivity", "🔗 Correlation & Data Quality"
    ])

    def show_optional(fig):
        if fig is not None:
            show(fig)

    with salary_tab:
        st.subheader("Salary statistics")
        if "Basic_Salary" in filtered:
            salary_stats = an.salary_summary(filtered).round(2)
            salary_stats_df = pd.DataFrame({
                "Measure": salary_stats.index,
                "Value": salary_stats.values
            })
            st.dataframe(salary_stats_df, hide_index=True, use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                show_optional(an.fig_salary_dist(filtered))
            with c2:
                show_optional(an.fig_salary_box(filtered))

            c1, c2 = st.columns(2)
            with c1:
                show_optional(an.fig_dept_salary(filtered))
            with c2:
                show_optional(an.fig_experience(filtered))

            st.subheader("Salary by job role")
            if "Designation" in filtered:
                role_salary = filtered.groupby("Designation", dropna=False)["Basic_Salary"].mean().sort_values(ascending=False)
                st.bar_chart(role_salary)
                st.dataframe(role_salary.rename("Average salary").round(2).reset_index(), hide_index=True, use_container_width=True)

            st.subheader("Salary vs performance")
            show_optional(an.fig_salary_vs_perf(filtered))

            st.subheader("Top 10 highest-paid employees")
            top_salary_cols = [
                c for c in ["Employee_ID", "Name", "Department", "Designation", "Experience_Years", "Basic_Salary"]
                if c in filtered.columns
            ]
            st.dataframe(
                filtered.sort_values("Basic_Salary", ascending=False)[top_salary_cols].head(10),
                hide_index=True, use_container_width=True
            )
        else:
            st.info("Salary analysis requires a Salary column.")

    with performance_tab:
        st.subheader("Performance statistics")
        if "Performance_Score" in filtered:
            performance_stats = an.performance_summary(filtered).round(2)
            performance_stats_df = pd.DataFrame({
                "Measure": performance_stats.index,
                "Value": performance_stats.values
            })
            st.dataframe(performance_stats_df, hide_index=True, use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                show_optional(an.fig_perf_dist(filtered))
            with c2:
                show_optional(an.fig_performance_box(filtered))
            c1, c2 = st.columns(2)
            with c1:
                show_optional(an.fig_dept_perf(filtered))
            with c2:
                show_optional(an.fig_numeric_relationship(
                    filtered, "Experience_Years", "Performance_Score", "Experience vs performance"
                ))

            st.subheader("Top 10 highest-performing employees")
            top_perf_cols = [
                c for c in ["Employee_ID", "Name", "Department", "Designation", "Performance_Score", "Basic_Salary"]
                if c in filtered.columns
            ]
            st.dataframe(
                filtered.sort_values(
                    ["Performance_Score", "Basic_Salary"], ascending=[False, False]
                )[top_perf_cols].head(10),
                hide_index=True, use_container_width=True
            )
        else:
            st.info("Performance analysis requires a Performance_Rating column.")

    with workforce_tab:
        st.subheader("Workforce composition")
        c1, c2 = st.columns(2)
        with c1:
            show_optional(an._categorical_chart(filtered, "Department", "Employees by department"))
            show_optional(an._categorical_chart(filtered, "Gender", "Employee distribution by gender"))
            show_optional(an._categorical_chart(filtered, "Education", "Employee distribution by education"))
        with c2:
            show_optional(an._categorical_chart(filtered, "Employment_Type", "Employment type distribution", kind="pie"))
            show_optional(an._categorical_chart(filtered, "Designation", "Employee distribution by job role"))
            show_optional(an._categorical_chart(filtered, "Experience_Years", "Employee distribution by experience"))
        st.subheader("Department-level summary")
        summary = an.department_full_summary(filtered)
        if not summary.empty:
            st.dataframe(summary, hide_index=True, use_container_width=True)
        st.subheader("Promotion eligibility")
        eligible = an.promotion_eligible_count(filtered)
        if eligible is not None:
            a, b = st.columns(2)
            a.metric("Promotion-eligible employees", eligible)
            b.metric("Share of filtered workforce", f"{eligible / len(filtered) * 100:.1f}%")
            st.dataframe(
                filtered[filtered["Promotion_Eligible"].astype(str).str.strip().str.lower().isin(["yes", "true", "1"])],
                hide_index=True, use_container_width=True
            )

    with productivity_tab:
        st.subheader("Attendance and productivity statistics")
    
        # Display one shared Department legend above all charts.
        legend_fig = an.fig_department_legend(filtered)
    
        if legend_fig is not None:
            st.pyplot(legend_fig, use_container_width=True)
            plt.close(legend_fig)
    
        metrics = an.productivity_summary(filtered)
    
        if not metrics.empty:
            st.dataframe(
                metrics,
                hide_index=True,
                use_container_width=True
            )
    
        c1, c2 = st.columns(2)
    
        with c1:
            show_optional(an.fig_attendance_vs_performance(filtered))
            show_optional(an.fig_training_vs_performance(filtered))
    
        with c2:
            show_optional(an.fig_overtime_vs_satisfaction(filtered))
    
            show_optional(
                an.fig_numeric_relationship(
                    filtered,
                    "Projects_Completed",
                    "Experience_Years",
                    "Projects completed vs experience"
                )
            )
    
        if "Attendance_Percentage" in filtered:
            high_attendance = filtered[
                pd.to_numeric(
                    filtered["Attendance_Percentage"],
                    errors="coerce"
                ) >= 90
            ]
    
            st.caption(
                f"Employees with attendance ≥ 90%: {len(high_attendance)}"
            )
    
        # ============================================================
        # TOP EMPLOYEES BY PROJECTS COMPLETED
        # ============================================================

        if "Projects_Completed" in filtered.columns:
            st.subheader("🏆 Top Employees by Projects Completed")
            st.caption(
                "Discover your most productive employees based on "
                "the number of projects they have completed."
            )

            # Select available columns
            cols = [
                c for c in [
                    "Employee_ID",
                    "Name",
                    "Department",
                    "Designation",
                    "Projects_Completed"
                ]
                if c in filtered.columns
            ]

            # Prepare clean data
            project_data = filtered[cols].copy()

            project_data["Projects_Completed"] = pd.to_numeric(
                project_data["Projects_Completed"],
                errors="coerce"
            )

            project_data = project_data.dropna(
                subset=["Projects_Completed"]
            )

            project_data = project_data.sort_values(
                "Projects_Completed",
                ascending=False
            ).reset_index(drop=True)

            if project_data.empty:
                st.info("No valid project completion data is available.")
            else:
                # Summary metrics
                total_projects = int(
                    project_data["Projects_Completed"].sum()
                )

                average_projects = project_data[
                    "Projects_Completed"
                ].mean()

                top_employee = project_data.iloc[0]

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "📁 Total Projects",
                        f"{total_projects:,}"
                    )

                with col2:
                    st.metric(
                        "📊 Average Projects",
                        f"{average_projects:.1f}"
                    )

                with col3:
                    employee_name = (
                        str(top_employee["Name"])
                        if "Name" in project_data.columns
                        else str(top_employee.get("Employee_ID", "N/A"))
                    )

                    st.metric(
                        "🥇 Highest Projects",
                        f"{int(top_employee['Projects_Completed'])}",
                        help=f"Top performer: {employee_name}"
                    )

                st.divider()

                # Display top 10 employees
                top_10 = project_data.head(10).copy()

                # Bar chart
                st.markdown("### 📈 Top 10 Employee Project Rankings")

                chart_data = top_10.copy()

                if "Name" in chart_data.columns:
                    chart_data["Employee"] = (
                        chart_data["Name"].astype(str)
                    )
                elif "Employee_ID" in chart_data.columns:
                    chart_data["Employee"] = (
                        chart_data["Employee_ID"].astype(str)
                    )
                else:
                    chart_data["Employee"] = [
                        f"Employee {i + 1}"
                        for i in range(len(chart_data))
                    ]

                chart_data = chart_data.sort_values(
                    "Projects_Completed",
                    ascending=True
                )

                fig, ax = plt.subplots(figsize=(10, 5))

                bars = ax.barh(
                    chart_data["Employee"],
                    chart_data["Projects_Completed"]
                )

                ax.set_xlabel("Projects Completed")
                ax.set_ylabel("Employee")
                ax.set_title("Top 10 Employees by Projects Completed")
                ax.grid(axis="x", linestyle="--", alpha=0.3)

                for bar in bars:
                    width = bar.get_width()
                    ax.text(
                        width,
                        bar.get_y() + bar.get_height() / 2,
                        f" {width:g}",
                        va="center"
                    )

                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

                # Detailed ranking table
                st.markdown("### 🏅 Employee Leaderboard")

                display_data = top_10.copy()
                display_data.insert(
                    0,
                    "Rank",
                    range(1, len(display_data) + 1)
                )

                st.dataframe(
                    display_data,
                    hide_index=True,
                    use_container_width=True
                )

        else:
            st.warning(
                "The dataset does not contain a 'Projects_Completed' "
                "column. Please check the column name in your CSV file."
            )   
    with correlation_tab:
        st.subheader("Correlation matrix")
        corr = an.numeric_correlation(filtered)
        if not corr.empty:
            st.dataframe(corr.round(2), use_container_width=True)
            show_optional(an.fig_full_corr(filtered))

            if "Basic_Salary" in corr.columns:
                st.subheader("Metrics most correlated with salary")
                st.dataframe(
                    corr["Basic_Salary"].drop(labels=["Basic_Salary"], errors="ignore")
                    .sort_values(key=lambda s: s.abs(), ascending=False)
                    .rename("Correlation with salary").round(3).reset_index()
                    .rename(columns={"index": "Metric"}),
                    hide_index=True, use_container_width=True
                )
            if "Performance_Score" in corr.columns:
                st.subheader("Metrics most correlated with performance")
                st.dataframe(
                    corr["Performance_Score"].drop(labels=["Performance_Score"], errors="ignore")
                    .sort_values(key=lambda s: s.abs(), ascending=False)
                    .rename("Correlation with performance").round(3).reset_index()
                    .rename(columns={"index": "Metric"}),
                    hide_index=True, use_container_width=True
                )
        else:
            st.info("No numeric columns are available for correlation analysis.")

        st.subheader("Data quality")
        st.dataframe(an.missing_summary(filtered), hide_index=True, use_container_width=True)
        st.caption("Missing-value results reflect the data currently supplied to the application. The original notebook's preprocessing fills missing numeric values with medians and missing text values with 'Unknown'.")

def page_departments(df):
    
    st.markdown("""
    <div class="departments-page-banner">
        <h2>Departments</h2>
        <p>Explore department-wise employee distribution, salary trends and performance insights</p>
        <div class="departments-header-divider"></div>
    </div>
    """, unsafe_allow_html=True)


    st.dataframe(an.dept_table(df), hide_index=True)
    a, b = st.columns(2)
    with a:
        show(an.fig_dept_count(df))
    with b:
        show(an.fig_dept_salary(df))



def page_data(df):
    st.markdown("""
    <div class="upload-export-page-banner">
        <h2>Upload & Export</h2>
        <p>Import employee datasets, validate records and export reports with ease</p>
        <div class="upload-export-header-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user

    st.subheader("Upload Employee Dataset")

    up = st.file_uploader(
        "Upload a CSV with the same columns as the sample dataset",
        type=["csv"],
        key="employee_dataset_uploader"
    )

    if up is not None:
        st.caption(f"Selected file: {up.name}")

        if st.button(
            "Upload and analyse",
            key="save_uploaded_dataset",
            use_container_width=True
        ):
            try:
                # Read and validate the uploaded dataset first.
                raw_df = an.load_data(up)
                prepared_df, log = an.prepare(raw_df)

                # Save the original file bytes and filename.
                file_id = db.save_uploaded_file(
                    user_id=user["id"],
                    filename=up.name,
                    file_bytes=up.getvalue()
                )

                # Cache the processed DataFrame for the current session.
                cache = st.session_state.setdefault(
                    "uploaded_dataframe_cache", {}
                )

                cache[file_id] = prepared_df

                # Automatically select the newly uploaded dataset.
                st.session_state["selected_data_source"] = file_id

                db.log_activity(
                    user["id"],
                    f"uploaded dataset {up.name}"
                )

                st.success(
                    f"Successfully uploaded and saved: {up.name}"
                )

                st.rerun()

            except Exception as ex:
                st.error(f"Unable to upload the dataset: {ex}")

    st.divider()

    st.subheader("My Uploaded Files")

    files = db.list_uploaded_files(user["id"])

    if files:
        for uploaded_file in files:
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"📄 {uploaded_file['filename']}")
                st.caption(
                    f"Uploaded: {uploaded_file['uploaded_at']}"
                )

            with col2:
                if st.button(
                    "Delete",
                    key=f"delete_file_{uploaded_file['id']}"
                ):
                    deleted = db.delete_uploaded_file(
                        user["id"],
                        uploaded_file["id"]
                    )

                    if deleted:
                        cache = st.session_state.get(
                            "uploaded_dataframe_cache", {}
                        )

                        cache.pop(uploaded_file["id"], None)

                        if st.session_state.get(
                            "selected_data_source"
                        ) == uploaded_file["id"]:
                            st.session_state[
                                "selected_data_source"
                            ] = "employee_database"

                        db.log_activity(
                            user["id"],
                            f"deleted uploaded dataset "
                            f"{uploaded_file['filename']}"
                        )

                        st.success("File deleted successfully.")
                        st.rerun()

    else:
        st.info(
            "You haven't uploaded any files yet. "
            "Upload a CSV file to see it here."
        )

    st.divider()

    st.subheader("Export")

    export_option = st.selectbox(
        "Choose what to export",
        [
            "Cleaned data (CSV)",
            "KPI summary (CSV)",
            "Correlation matrix (CSV)",
            "Printable report (HTML)"
        ],
        index=None,
        placeholder="Select an export option..."
    )

    if export_option == "Cleaned data (CSV)":
        st.download_button(
            "⬇️ Download",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="Employee_Salary_Performance_Cleaned.csv",
            mime="text/csv",
            use_container_width=True
        )

    elif export_option == "KPI summary (CSV)":
        st.download_button(
            "⬇️ Download",
            data=pd.Series(
                an.kpis(df)
            ).rename("value").to_csv().encode("utf-8"),
            file_name="kpi_summary.csv",
            mime="text/csv",
            use_container_width=True
        )

    elif export_option == "Correlation matrix (CSV)":
        st.download_button(
            "⬇️ Download",
            data=an.numeric_correlation(df).round(3).to_csv().encode("utf-8"),
            file_name="correlation_matrix.csv",
            mime="text/csv",
            use_container_width=True
        )

    elif export_option == "Printable report (HTML)":
        st.download_button(
            "⬇️ Download",
            data=an.report_html(
                df,
                user["username"]
            ),
            file_name="report.html",
            mime="text/html",
            use_container_width=True
        )
def page_profile():
    user = st.session_state.user

    full_name = user.get("full_name") or user.get("username", "User")
    username = user.get("username", "Not available")
    email = user.get("email", "Not available")
    role = user.get("role", "user").title()

    
    st.markdown("""
    <div class="user-data-page-banner">
        <h2>👤 User Data</h2>
        <p>Manage user information, review account details, and maintain your application data in one place.</p>
        <div class="user-data-header-divider"></div>
    </div>
    """, unsafe_allow_html=True)


    st.subheader("My Account")

    # Profile header
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #14213d, #233e70);
            padding: 28px;
            border-radius: 14px;
            color: white;
            margin-bottom: 22px;
        ">
            <div style="
                width: 70px;
                height: 70px;
                border-radius: 50%;
                background: #0f766e;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                font-weight: bold;
                margin-bottom: 14px;
            ">
                {full_name.strip()[:1].upper()}
            </div>
            <h2 style="color: white; margin: 0;">
                {full_name}
            </h2>
            <p style="color: #dbeafe; margin: 6px 0 0;">
                @{username}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Registration Details")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input(
            "Full Name",
            value=full_name,
            disabled=True
        )

        st.text_input(
            "Username",
            value=username,
            disabled=True
        )

    with col2:
        st.text_input(
            "Email Address",
            value=email,
            disabled=True
        )

        st.text_input(
            "Account Role",
            value=role,
            disabled=True
        )

    st.info(
        "This page displays the account details available to the "
        "application. Contact the administrator if your registration "
        "information needs to be corrected."
    )



def main():
    user = st.session_state.user

    display_name = (
        user.get("full_name")
        or user.get("username")
        or "User"
    )

    pages = [
        "Dashboard",
        "Employees",
        "Analysis",
        "Departments",
        "Upload and export"
    ]

    pages.append(display_name)

    # ============================================================
    # LOAD THIS USER'S UPLOADED FILE METADATA
    # ============================================================

    uploaded_files = db.list_uploaded_files(user["id"])

    # Stable identifiers prevent issues when filenames are duplicated.
    file_options = {
        "employee_database": "🗄️ Employee database"
    }

    for uploaded_file in uploaded_files:
        file_options[uploaded_file["id"]] = (
            f"📄 {uploaded_file['filename']}"
        )

    # ============================================================
    # SIDEBAR
    # ============================================================

    with st.sidebar:
        st.markdown("### 📊 StaffMetrics")
        st.markdown(f"### 👤 {display_name}")
        st.caption(f"{user.get('role', 'user').title()} account")

        if st.session_state.pop(
            "navigate_to_employees", False
        ):
            st.session_state["page_navigation"] = "Employees"

        page = st.selectbox(
            "Navigate to page",
            pages,
            key="page_navigation"
        )

        st.divider()

        st.markdown("#### 📂 DATA SOURCES")

        selected_source = st.selectbox(
            "Select a dataset",
            options=list(file_options.keys()),
            format_func=lambda file_id: file_options[file_id],
            key="selected_data_source"
        )

        st.caption(
            f"{len(uploaded_files)} uploaded "
            f"file(s) belonging to your account."
        )

        st.divider()

        if st.button(
            "🚪 Sign out",
            key="sidebar_sign_out",
            use_container_width=True
        ):
            db.log_activity(user["id"], "signed out")

            # Remove user-specific session information.
            st.session_state.pop("user", None)
            st.session_state.pop("upload", None)
            st.session_state.pop(
                "uploaded_dataframe_cache", None
            )
            st.session_state.pop(
                "selected_data_source", None
            )

            st.rerun()

    # ============================================================
    # LOAD SELECTED DATA SOURCE
    # ============================================================

    is_db = selected_source == "employee_database"

    if is_db:
        df = db.employee_frame()

        # Preserve the optional analysis columns in your existing app.
        try:
            source_df, _ = an.prepare(an.load_data(CSV))

            analysis_fields = [
                "Education",
                "Employment_Type",
                "Projects_Completed",
                "Working_Hours_Per_Day",
                "Attendance_Percentage",
                "Training_Hours",
                "Leave_Days",
                "Job_Satisfaction",
                "Promotion_Eligible",
                "Overtime_Hours",
                "Manager_Rating"
            ]

            available_fields = [
                column
                for column in analysis_fields
                if column in source_df.columns
                and column not in df.columns
            ]

            if available_fields:
                df = df.merge(
                    source_df[["Employee_ID"] + available_fields],
                    on="Employee_ID",
                    how="left"
                )

        except Exception as ex:
            st.warning(
                "Some optional analysis columns could not be loaded: "
                f"{ex}"
            )

    else:
        # First check whether this dataset is already processed
        # in the current session.
        cache = st.session_state.setdefault(
            "uploaded_dataframe_cache", {}
        )

        if selected_source not in cache:
            saved_file = db.get_uploaded_file(
                user_id=user["id"],
                file_id=selected_source
            )

            if saved_file is None:
                st.error(
                    "This file is unavailable or does not belong "
                    "to your account."
                )
                st.stop()

            try:
                # Restore the file using its saved bytes.
                raw_df = pd.read_csv(
                    io.BytesIO(saved_file["file_data"])
                )

                df, log = an.prepare(raw_df)

                cache[selected_source] = df

            except Exception as ex:
                st.error(
                    f"Unable to load "
                    f"{saved_file['filename']}: {ex}"
                )
                st.stop()

        df = cache[selected_source]

        st.session_state["upload"] = df

    # ============================================================
    # PAGE NAVIGATION
    # ============================================================

    if page != "Employees":
        st.session_state[
            "apply_dashboard_filters_to_employees"
        ] = False

    if page == "Dashboard":
        page_dashboard(df)

    elif page == "Employees":
        page_employees(df, is_db)

    elif page == "Analysis":
        page_analysis(df)

    elif page == "Departments":
        page_departments(df)

    elif page == "Upload and export":
        page_data(df)

    elif page == display_name:
        page_profile()


if "user" not in st.session_state:
    auth_page()
else:
    main()
