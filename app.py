import os
import re
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import extra_streamlit_components as stx
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from backend import analytics as an, auth, database as db, sql_queries as Q


# ============================================================
# APP CONFIGURATION AND DATABASE INITIALIZATION
# ============================================================

st.set_page_config(
    page_title="Employee Salary & Performance Analysis",
    page_icon="📊",
    layout="wide",
)

db.init_db()

CSV = "data/employee_salary_performance.csv"

if not db.is_seeded():
    db.seed_database(an.prepare(an.load_data(CSV))[0])


# ============================================================
# PERSISTENT LOGIN
# ============================================================

COOKIE_NAME = "staffmetrics_auth"
COOKIE_MAX_AGE = 7 * 24 * 60 * 60

APP_SECRET = os.environ.get("STAFFMETRICS_SECRET_KEY")

if not APP_SECRET:
    try:
        APP_SECRET = st.secrets["STAFFMETRICS_SECRET_KEY"]
    except (KeyError, FileNotFoundError):
        APP_SECRET = (
            "local-development-only-change-this-secret-before-deploying"
        )

auth_serializer = URLSafeTimedSerializer(
    APP_SECRET,
    salt="staffmetrics-auth-v1",
)

cookie_manager = stx.CookieManager(
    key="staffmetrics_cookie_manager"
)


def save_login_cookie(user):
    """Save a signed login token in the browser cookie."""

    safe_user = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user.get("full_name") or user["username"],
        "role": user["role"],
    }

    token = auth_serializer.dumps(safe_user)

    cookie_manager.set(
        COOKIE_NAME,
        token,
        expires_at=datetime.now() + timedelta(days=7),
        key="staffmetrics_save_auth_cookie",
    )
def restore_login_cookie():
    """Restore the signed-in user after a browser refresh."""

    token = cookie_manager.get(COOKIE_NAME)

    if not token:
        return None

    try:
        user = auth_serializer.loads(
            token,
            max_age=COOKIE_MAX_AGE,
        )

        required_fields = {
            "id",
            "username",
            "full_name",
            "role",
        }

        if not required_fields.issubset(user):
            clear_login_cookie()
            return None

        if user["role"] not in {"admin", "user"}:
            clear_login_cookie()
            return None

        return user

    except (BadSignature, SignatureExpired):
        clear_login_cookie()
        return None


def clear_login_cookie():
    """Remove the saved login cookie."""

    try:
        cookie_manager.delete(COOKIE_NAME)
    except Exception:
        pass


# ============================================================
# GLOBAL STYLING
# ============================================================

# ============================================================
# GLOBAL STYLING — LIGHT AND DARK THEMES
# ============================================================

THEME_OPTIONS = ["☀️ Light", "🌙 Dark"]

# Streamlit updates widget state before rerunning the script.
# This makes the selected theme persist across reruns.
theme_choice = st.session_state.get("theme_choice", "☀️ Light")

APP_THEME = "dark" if theme_choice == "🌙 Dark" else "light"

if APP_THEME == "dark":
    BG_COLOR = "#0b1220"
    CARD_COLOR = "#151f30"
    SIDEBAR_COLOR = "#101a2b"
    TEXT_COLOR = "#e8eef8"
    MUTED_COLOR = "#a7b5ca"
    BORDER_COLOR = "#2b3b52"
    INPUT_COLOR = "#1b2940"
    HOVER_COLOR = "#243b55"
    ACTIVE_COLOR = "#0f766e"
    TABLE_HEADER = "#1b3650"
else:
    BG_COLOR = "#f4f7fb"
    CARD_COLOR = "#ffffff"
    SIDEBAR_COLOR = "#17243b"
    TEXT_COLOR = "#17243b"
    MUTED_COLOR = "#64748b"
    BORDER_COLOR = "#dce5ef"
    INPUT_COLOR = "#ffffff"
    HOVER_COLOR = "#e4f3f1"
    ACTIVE_COLOR = "#0f766e"
    TABLE_HEADER = "#e8f1f8"


st.markdown(
    f"""
    <style>

    /* =====================================================
       GLOBAL COLORS
       ===================================================== */

    :root {{
        --app-bg: {BG_COLOR};
        --card-bg: {CARD_COLOR};
        --sidebar-bg: {SIDEBAR_COLOR};
        --text-color: {TEXT_COLOR};
        --muted-color: {MUTED_COLOR};
        --border-color: {BORDER_COLOR};
        --input-bg: {INPUT_COLOR};
        --hover-bg: {HOVER_COLOR};
        --active-color: {ACTIVE_COLOR};
        --table-header: {TABLE_HEADER};
    }}

    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans', sans-serif;
    }}

    .stApp {{
        background-color: var(--app-bg);
        color: var(--text-color);
        transition:
            background-color 0.25s ease,
            color 0.25s ease;
    }}

    .block-container {{
        max-width: 1350px;
        padding-top: 1.6rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-color) !important;
    }}

    p, label, span {{
        color: inherit;
    }}

    [data-testid="stCaptionContainer"] {{
        color: var(--muted-color) !important;
    }}


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color);
    }}

    [data-testid="stSidebar"] > div {{
        background: var(--sidebar-bg) !important;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: #ffffff !important;
    }}

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {{
        color: #e2eaf7;
    }}

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: #e2eaf7;
    }}

    /* Sidebar navigation options */

    [data-testid="stSidebar"] [data-testid="stRadio"] {{
        margin-top: 8px;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        display: flex;
        align-items: center;
        width: 100%;
        min-height: 42px;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 9px;
        background: rgba(255,255,255,0.045);
        border: 1px solid transparent;
        color: #dce6f5 !important;
        cursor: pointer;
        transition:
            background 0.18s ease,
            border-color 0.18s ease,
            transform 0.18s ease;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background: rgba(45,212,191,0.15);
        border-color: rgba(45,212,191,0.35);
        transform: translateX(3px);
    }}

    /* Highlight the selected navigation item */

    [data-testid="stSidebar"]
    [data-testid="stRadio"]
    label:has(input:checked) {{
        background: linear-gradient(
            100deg,
            #0f766e,
            #115e59
        ) !important;
        border: 1px solid #2dd4bf !important;
        box-shadow: 0 4px 12px rgba(15,118,110,0.2);
    }}

    [data-testid="stSidebar"]
    [data-testid="stRadio"]
    label:has(input:checked) p,
    [data-testid="stSidebar"]
    [data-testid="stRadio"]
    label:has(input:checked) span {{
        color: #ffffff !important;
        font-weight: 700 !important;
    }}

    /* Hide radio circles while retaining accessible labels */

    [data-testid="stSidebar"]
    [data-testid="stRadio"] input {{
        accent-color: #2dd4bf;
    }}


    /* =====================================================
       SIDEBAR INPUTS
       ===================================================== */

    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: #1d2c43 !important;
        border-color: #3a4b63 !important;
        color: #ffffff !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] input {{
        color: #ffffff !important;
    }}

    [data-testid="stSidebar"] [data-testid="stButton"] > button {{
        background: #26364e;
        color: #ffffff;
        border: 1px solid #52647c;
        border-radius: 10px;
        font-weight: 600;
    }}

    [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {{
        background: #b91c1c;
        border-color: #f87171;
        color: #ffffff;
    }}


    /* =====================================================
       THEME SELECTOR
       ===================================================== */

    [data-testid="stSidebar"] [data-testid="stRadio"] {{
        color: #ffffff;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(
        input:checked
    ) {{
        outline: none;
    }}


    /* =====================================================
       BUTTONS
       ===================================================== */

    [data-testid="stButton"] > button {{
        border-radius: 10px;
        border: 1px solid var(--border-color);
        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            background 0.18s ease;
    }}

    [data-testid="stButton"] > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 7px 18px rgba(15,118,110,0.16);
        border-color: #0f766e;
    }}


    /* =====================================================
       INPUTS AND DROPDOWNS
       ===================================================== */

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {{
        background: var(--input-bg) !important;
        color: var(--text-color) !important;
        border-color: var(--border-color) !important;
        border-radius: 9px;
    }}

    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
        background: var(--input-bg) !important;
        border-color: var(--border-color) !important;
        color: var(--text-color) !important;
    }}

    [data-testid="stSelectbox"] [data-baseweb="select"] *,
    [data-testid="stMultiSelect"] [data-baseweb="select"] * {{
        color: var(--text-color);
    }}

    [data-testid="stSlider"] {{
        color: var(--active-color);
    }}

    [data-testid="stCheckbox"] label {{
        color: var(--text-color) !important;
    }}


    /* =====================================================
       DATAFRAMES AND TABLES
       ===================================================== */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
        border: 1px solid var(--border-color);
        border-radius: 10px;
        overflow: hidden;
    }}

    [data-testid="stDataFrame"] *,
    [data-testid="stTable"] * {{
        color: var(--text-color);
    }}


    /* =====================================================
       METRIC CARDS
       ===================================================== */

    .kpi {{
        background: var(--card-bg);
        padding: 20px;
        border: 1px solid var(--border-color);
        border-left: 4px solid #0f766e;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }}

    .kpi span {{
        display: block;
        color: var(--muted-color);
        font-size: 0.9rem;
        margin-bottom: 8px;
    }}

    .kpi b {{
        color: var(--text-color);
        font-size: 1.7rem;
    }}


    /* =====================================================
       BANNER
       ===================================================== */

    .banner {{
        background: linear-gradient(
            115deg,
            #14213d,
            #1e3a66,
            #0f766e
        );
        color: #ffffff;
        padding: 24px 28px;
        border-radius: 14px;
        margin-bottom: 22px;
        box-shadow: 0 8px 24px rgba(20,33,61,0.12);
    }}

    .banner h1 {{
        color: #ffffff !important;
        margin: 0;
        font-size: 1.8rem;
    }}

    .banner p {{
        color: #d8e5f7 !important;
        margin: 7px 0 0;
    }}


    /* =====================================================
       TABS AND EXPANDERS
       ===================================================== */

    [data-testid="stTabs"] button {{
        color: var(--text-color);
    }}

    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: #0f766e !important;
        font-weight: 700;
    }}

    [data-testid="stExpander"] {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
    }}


    /* =====================================================
       KPI BUTTON CARDS
       ===================================================== */

    [class*="st-key-dashboard_kpi_"]
    [data-testid="stButton"] > button {{
        position: relative;
        width: 100%;
        min-height: 124px;
        height: 124px;
        white-space: pre-line;
        text-align: left;
        justify-content: flex-start;
        background: var(--card-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-left: 5px solid #0f766e !important;
        border-radius: 14px !important;
        padding: 16px !important;
        box-shadow: 0 5px 16px rgba(0,0,0,0.06);
    }}

    [class*="st-key-dashboard_kpi_"]
    [data-testid="stButton"] > button:hover {{
        background: var(--hover-bg) !important;
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(15,118,110,0.13);
    }}

    /* Popup menus */

    [data-baseweb="popover"] {{
        background: var(--card-bg) !important;
    }}

    /* Accessibility */

    @media (prefers-reduced-motion: reduce) {{
        *,
        *::before,
        *::after {{
            animation: none !important;
            transition: none !important;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True,
)
# ============================================================
# COMMON FUNCTIONS
# ============================================================

def banner(title, subtitle=""):
    st.markdown(
        f"""
        <div class="banner">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpis(items):
    for col, (label, value) in zip(st.columns(len(items)), items):
        col.markdown(
            f"""
            <div class="kpi">
                <span>{label}</span>
                <b>{value}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# KPI INFORMATION
# ============================================================

KPI_DETAILS = {
    "Average salary": {
        "icon": "💰",
        "description": (
            "The average basic salary across employees matching "
            "the current dashboard filters. It provides a high-level "
            "view of salary levels in the selected workforce."
        ),
        "module": "Analysis",
    },
    "Median salary": {
        "icon": "⚖️",
        "description": (
            "The median is the middle basic-salary value after salaries "
            "are ordered. It can describe a typical salary more robustly "
            "than the average when unusually high or low salaries are present."
        ),
        "module": "Analysis",
    },
    "Minimum salary": {
        "icon": "📉",
        "description": (
            "The lowest basic salary among employees matching your "
            "dashboard filters. Use the analysis module to explore "
            "salary distribution and differences."
        ),
        "module": "Analysis",
    },
    "Maximum salary": {
        "icon": "📈",
        "description": (
            "The highest basic salary among employees matching your "
            "dashboard filters. Use the analysis module to explore "
            "salary distribution and differences."
        ),
        "module": "Analysis",
    },
    "Average performance": {
        "icon": "⭐",
        "description": (
            "The average performance score for employees matching "
            "your dashboard filters."
        ),
        "module": "Analysis",
    },
    "Maximum performance": {
        "icon": "🏆",
        "description": (
            "The highest performance score for employees matching "
            "your dashboard filters."
        ),
        "module": "Analysis",
    },
}


def request_page_navigation(module):
    """Schedule navigation for the next rerun."""

    st.session_state["_pending_page_navigation"] = module
    st.session_state.pop("_metric_dialog", None)
    st.rerun()


def interactive_kpi_cards(items, section_key):
    """Display clickable dashboard KPI cards."""

    columns = st.columns(len(items))

    for index, (label, value) in enumerate(items):
        with columns[index]:

            icons = {
                "Employees": "👥",
                "Average salary": "💰",
                "Median salary": "⚖️",
                "Minimum salary": "📉",
                "Maximum salary": "📈",
                "Average performance": "⭐",
                "Maximum performance": "🏆",
            }

            clicked = st.button(
                f"{icons.get(label, '📊')}  {label}\n\n{value}",
                key=f"{section_key}_{index}",
                use_container_width=True,
                help=(
                    "Open the Employees module"
                    if label == "Employees"
                    else f"Learn what {label.lower()} means"
                ),
            )

        if clicked:
            if label == "Employees":
                request_page_navigation("Employees")
            else:
                st.session_state["_metric_dialog"] = label
                st.rerun()


@st.dialog("Metric overview", width="small")
def metric_information_dialog():
    """Explain the selected KPI and offer module navigation."""

    label = st.session_state.get("_metric_dialog")
    details = KPI_DETAILS.get(label)

    if not details:
        st.write("Metric information is not available.")
        return

    st.markdown(f"### {details['icon']} {label}")
    st.write(details["description"])
    st.divider()

    st.caption(f"Recommended module: {details['module']}")

    if st.button(
        f"Open {details['module']} module  →",
        key="metric_dialog_open_module",
        type="primary",
        use_container_width=True,
    ):
        request_page_navigation(details["module"])

    if st.button(
        "Close",
        key="metric_dialog_close",
        use_container_width=True,
    ):
        st.session_state.pop("_metric_dialog", None)
        st.rerun()


# ============================================================
# LOGIN AND REGISTRATION PAGE
# ============================================================

def auth_page():
    """Display the animated login screen with the StaffMetrics logo."""

    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 8% 8%,
                    rgba(20,184,166,.13),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 92% 90%,
                    rgba(59,130,246,.13),
                    transparent 32%
                ),
                linear-gradient(135deg, #f7faff, #edf3fb);
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            max-width: 1120px;
            padding-top: 2.4rem;
            padding-bottom: 2rem;
        }

        @keyframes panelIn {
            from {
                opacity: 0;
                transform: translateY(18px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes logoFloat {
            0%, 100% {
                transform: translateY(0) rotate(0deg);
            }
            50% {
                transform: translateY(-5px) rotate(2deg);
            }
        }

        .login-card {
            background: rgba(255,255,255,.96);
            padding: 30px 30px 22px;
            border: 1px solid #e0e8f2;
            border-radius: 20px;
            min-height: 500px;
            box-shadow: 0 22px 55px rgba(20,33,61,.10);
            animation: panelIn .72s ease-out both;
        }

        .login-heading {
            color: #14213d;
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: -.6px;
            margin-bottom: 5px;
        }

        .login-description {
            color: #64748b;
            margin-bottom: 20px;
            line-height: 1.6;
        }

        [data-testid="stTextInput"] input {
            border-radius: 11px;
            border: 1px solid #d6e0eb;
            min-height: 43px;
        }

        [data-testid="stTextInput"] input:focus {
            border-color: #0f766e;
            box-shadow: 0 0 0 3px rgba(15,118,110,.10);
        }

        [data-testid="stTabs"] button {
            font-weight: 700;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            color: #0f766e !important;
        }

        .stButton > button {
            border-radius: 11px;
            min-height: 46px;
            font-weight: 700;
            transition: transform .18s ease, box-shadow .18s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(37,99,235,.17);
        }

        .security-note {
            font-size: .78rem;
            color: #94a3b8;
            text-align: center;
            margin-top: 18px;
        }

        @media (max-width: 700px) {
            .block-container {
                padding-top: 1rem;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .login-card {
                animation: none !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [1, 1.08],
        gap="small",
        vertical_alignment="center",
    )

    # --------------------------------------------------------
    # LEFT PANEL: LOGO AND BRANDING
    # --------------------------------------------------------

    with left:
        components.html(
            """
            <!doctype html>
            <html>
            <head>
                <meta name="viewport"
                      content="width=device-width, initial-scale=1">

                <style>
                    * {
                        box-sizing: border-box;
                    }

                    body {
                        margin: 0;
                        font-family: Arial, Helvetica, sans-serif;
                    }

                    .brand {
                        position: relative;
                        overflow: hidden;
                        min-height: 520px;
                        padding: 42px 32px;
                        border-radius: 24px;
                        color: #fff;
                        background: linear-gradient(
                            145deg,
                            #101d38 0%,
                            #1e3a66 58%,
                            #0f766e 130%
                        );
                        box-shadow: 0 22px 55px rgba(20,33,61,.18);
                        animation: appear .55s ease-out both;
                    }

                    .circle {
                        position: absolute;
                        border: 1px solid rgba(255,255,255,.16);
                        border-radius: 50%;
                        pointer-events: none;
                    }

                    .c1 {
                        width: 260px;
                        height: 260px;
                        right: -105px;
                        top: -100px;
                        box-shadow:
                            0 0 0 24px rgba(255,255,255,.035),
                            0 0 0 48px rgba(255,255,255,.025);
                    }

                    .c2 {
                        width: 190px;
                        height: 190px;
                        left: -105px;
                        bottom: -100px;
                        background: rgba(45,212,191,.08);
                    }

                    .logo {
                        width: 76px;
                        height: 76px;
                        display: grid;
                        place-items: center;
                        border-radius: 23px;
                        margin-bottom: 24px;
                        background: linear-gradient(
                            135deg,
                            rgba(255,255,255,.22),
                            rgba(255,255,255,.08)
                        );
                        border: 1px solid rgba(255,255,255,.28);
                        box-shadow: 0 12px 28px rgba(0,0,0,.15);
                        animation: float 4s ease-in-out infinite;
                    }

                    h1 {
                        font-size: 39px;
                        letter-spacing: -1.2px;
                        margin: 0 0 12px;
                        font-weight: 800;
                    }

                    .tagline {
                        color: #dbeafe;
                        font-size: 15px;
                        line-height: 1.8;
                        margin: 0 0 22px;
                        max-width: 390px;
                    }

                    .feature {
                        display: flex;
                        align-items: center;
                        gap: 11px;
                        color: #f0fdfa;
                        margin: 13px 0;
                        font-size: 15px;
                    }

                    .dot {
                        width: 28px;
                        height: 28px;
                        flex: 0 0 28px;
                        display: grid;
                        place-items: center;
                        border-radius: 9px;
                        background: rgba(45,212,191,.16);
                        border: 1px solid rgba(153,246,228,.25);
                        color: #99f6e4;
                    }

                    @keyframes appear {
                        from {
                            opacity: 0;
                            transform: translateY(18px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }

                    @keyframes float {
                        0%, 100% {
                            transform: translateY(0);
                        }
                        50% {
                            transform: translateY(-5px);
                        }
                    }

                    @media(max-width:700px) {
                        .brand {
                            min-height: auto;
                            padding: 28px 24px;
                        }

                        h1 {
                            font-size: 32px;
                        }
                    }

                    @media(prefers-reduced-motion:reduce) {
                        .brand, .logo {
                            animation: none;
                        }
                    }
                </style>
            </head>

            <body>
                <div class="brand">
                    <span class="circle c1"></span>
                    <span class="circle c2"></span>

                    <div class="logo">
                        <svg
                            width="42"
                            height="42"
                            viewBox="0 0 48 48"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                            aria-label="StaffMetrics logo"
                        >
                            <rect
                                x="5"
                                y="5"
                                width="38"
                                height="38"
                                rx="11"
                                stroke="white"
                                stroke-width="2"
                                opacity=".9"
                            />

                            <path
                                d="M13 31V25M21 31V17M29 31V21M37 31V13"
                                stroke="#99F6E4"
                                stroke-width="4"
                                stroke-linecap="round"
                            />
                        </svg>
                    </div>

                    <h1>StaffMetrics</h1>

                    <p class="tagline">
                        Turn employee data into meaningful insights.
                        Understand salaries, track performance, and make
                        confident workforce decisions.
                    </p>

                    <div class="feature">
                        <span class="dot">✓</span>
                        <span>Smart employee analytics</span>
                    </div>

                    <div class="feature">
                        <span class="dot">↗</span>
                        <span>Clear salary insights</span>
                    </div>

                    <div class="feature">
                        <span class="dot">★</span>
                        <span>Performance reporting</span>
                    </div>

                    <div class="feature">
                        <span class="dot">⌘</span>
                        <span>Workforce management</span>
                    </div>
                </div>
            </body>
            </html>
            """,
            height=540,
            scrolling=False,
        )

    # --------------------------------------------------------
    # RIGHT PANEL: LOGIN AND REGISTRATION
    # --------------------------------------------------------

    with right:
        st.markdown(
            """
            <div class="login-card">
                <div class="login-heading">Welcome back</div>
                <div class="login-description">
                    Sign in to continue to your employee analytics workspace.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        login_tab, register_tab = st.tabs(
            ["🔐 Sign in", "✨ Create account"]
        )

        # ----------------------------------------------------
        # LOGIN TAB
        # ----------------------------------------------------

        with login_tab:
            st.subheader("Sign in to your account")

            login_id = st.text_input(
                "Username or email",
                key="login_username",
            )

            show_login_password = st.checkbox(
                "Show password",
                key="show_login_password",
            )

            login_password = st.text_input(
                "Password",
                type="default" if show_login_password else "password",
                key="login_password",
            )

            remember_me = st.checkbox(
                "Keep me signed in for 7 days",
                value=True,
                key="remember_me",
            )

            if st.button(
                "Sign in  →",
                key="login_button",
                use_container_width=True,
                type="primary",
            ):
                if not login_id.strip() or not login_password:
                    st.warning(
                        "Enter your username/email and password."
                    )

                else:
                    user = auth.login(
                        login_id,
                        login_password,
                    )

                    if user:
                        st.session_state["user"] = user

                        if remember_me:
                            save_login_cookie(user)
                        else:
                            clear_login_cookie()

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

        # ----------------------------------------------------
        # REGISTRATION TAB
        # ----------------------------------------------------

        with register_tab:
            st.subheader("Create your account")

            full_name = st.text_input(
                "Full name",
                key="register_full_name",
            )

            email = st.text_input(
                "Email address",
                key="register_email",
            )

            username = st.text_input(
                "Choose a username",
                key="register_username",
            )

            show_register_password = st.checkbox(
                "Show registration passwords",
                key="show_register_password",
            )

            password_type = (
                "default" if show_register_password else "password"
            )

            password = st.text_input(
                "Create password",
                type=password_type,
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type=password_type,
                key="register_confirm_password",
            )

            if password:
                score = sum(
                    [
                        len(password) >= 8,
                        bool(re.search(r"[A-Z]", password)),
                        bool(re.search(r"[a-z]", password)),
                        bool(re.search(r"[0-9]", password)),
                        bool(re.search(r"[^A-Za-z0-9]", password)),
                    ]
                )

                if score <= 2:
                    st.warning("Password strength: Weak")

                elif score <= 4:
                    st.info("Password strength: Moderate")

                else:
                    st.success("Password strength: Strong")

            st.caption(
                "Use at least 8 characters. A mix of letters, "
                "numbers, and symbols is recommended."
            )

            if st.button(
                "Create account  →",
                key="register_button",
                use_container_width=True,
                type="primary",
            ):
                if not all(
                    [
                        full_name.strip(),
                        email.strip(),
                        username.strip(),
                        password,
                        confirm_password,
                    ]
                ):
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
                        password,
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
            """
            <div class="security-note">
                StaffMetrics · Employee Salary & Performance Analysis
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# CHART HELPER
# ============================================================

def show(fig):
    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

def page_dashboard(df):
    banner(
        "Executive Dashboard",
        (
            f"Welcome, "
            f"{st.session_state.user['full_name'] or st.session_state.user['username']}"
        ),
    )

    st.subheader("Dashboard Filters")

    c1, c2, c3 = st.columns(3)

    departments = sorted(
        df["Department"].dropna().unique().tolist()
    )

    designations = sorted(
        df["Designation"].dropna().astype(str).unique().tolist()
    )

    with c1:
        selected_departments = st.multiselect(
            "Department",
            departments,
            default=departments,
            key="dashboard_departments",
        )

    with c2:
        selected_designations = st.multiselect(
            "Designation",
            designations,
            default=designations,
            key="dashboard_designations",
        )

    with c3:
        chart_choice = st.selectbox(
            "Chart to display",
            [
                "All charts",
                "Department-wise salary",
                "Salary distribution",
                "Department-wise performance",
                "Salary vs. performance",
            ],
            key="dashboard_chart",
        )

    salary_min = float(df["Basic_Salary"].min())
    salary_max = float(df["Basic_Salary"].max())

    if salary_min == salary_max:
        selected_salary = (salary_min, salary_max)
        st.caption(f"Salary filter: {salary_min:,.0f}")

    else:
        selected_salary = st.slider(
            "Basic salary range",
            min_value=salary_min,
            max_value=salary_max,
            value=(salary_min, salary_max),
            key="dashboard_salary",
        )

    c4, c5 = st.columns(2)

    exp_min = int(df["Experience_Years"].min())
    exp_max = int(df["Experience_Years"].max())

    with c4:
        if exp_min == exp_max:
            selected_experience = (exp_min, exp_max)
            st.caption(f"Experience: {exp_min} years")

        else:
            selected_experience = st.slider(
                "Experience (years)",
                min_value=exp_min,
                max_value=exp_max,
                value=(exp_min, exp_max),
                key="dashboard_experience",
            )

    perf_min = float(df["Performance_Score"].min())
    perf_max = float(df["Performance_Score"].max())

    with c5:
        if perf_min == perf_max:
            selected_performance = (perf_min, perf_max)
            st.caption(f"Performance score: {perf_min}")

        else:
            selected_performance = st.slider(
                "Performance score",
                min_value=perf_min,
                max_value=perf_max,
                value=(perf_min, perf_max),
                key="dashboard_performance",
            )

    filtered_df = df[
        df["Department"].isin(selected_departments)
        & df["Designation"].astype(str).isin(selected_designations)
        & df["Basic_Salary"].between(*selected_salary)
        & df["Experience_Years"].between(*selected_experience)
        & df["Performance_Score"].between(*selected_performance)
    ]

    if filtered_df.empty:
        st.warning("No employees match your selected filters.")
        return

    st.caption(
        f"Showing {len(filtered_df):,} of {len(df):,} employee records."
    )

    k = an.kpis(filtered_df)

    interactive_kpi_cards(
        [
            ("Employees", f"{k['total_employees']:,}"),
            ("Average salary", f"{k['average_salary']:,.0f}"),
            ("Median salary", f"{k['median_salary']:,.0f}"),
            ("Minimum salary", f"{k['minimum_salary']:,.0f}"),
        ],
        section_key="dashboard_kpi_top",
    )

    st.write("")

    interactive_kpi_cards(
        [
            ("Maximum salary", f"{k['maximum_salary']:,.0f}"),
            (
                "Average performance",
                f"{k['average_performance']:.2f}",
            ),
            (
                "Maximum performance",
                f"{k['maximum_performance']:.2f}",
            ),
        ],
        section_key="dashboard_kpi_bottom",
    )

    if st.session_state.get("_metric_dialog"):
        metric_information_dialog()

    st.subheader("Automated Insights")

    for line in an.insights(filtered_df):
        st.info(line)

    st.subheader("Visual Analytics")

    chart_functions = {
        "Department-wise salary": an.fig_dept_salary,
        "Salary distribution": an.fig_salary_dist,
        "Department-wise performance": an.fig_dept_perf,
        "Salary vs. performance": an.fig_salary_vs_perf,
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


# ============================================================
# EMPLOYEE MANAGEMENT
# ============================================================

def manage_employees(df):
    uid = st.session_state.user["id"]

    with st.expander("Add an employee"):
        with st.form("add_emp"):
            c = st.columns(3)

            employee = {
                "Employee_ID": c[0].text_input("Employee ID"),
                "Name": c[1].text_input("Name"),
                "Age": c[2].number_input(
                    "Age", 18, 70, 30
                ),
                "Gender": c[0].selectbox(
                    "Gender", ["Female", "Male"]
                ),
                "Department": c[1].selectbox(
                    "Department",
                    sorted(df["Department"].unique()),
                ),
                "Designation": c[2].text_input("Designation"),
                "Experience_Years": c[0].number_input(
                    "Experience (years)", 0, 45, 3
                ),
                "Joining_Year": c[1].number_input(
                    "Joining year", 1990, 2030, 2024
                ),
                "Basic_Salary": c[2].number_input(
                    "Basic salary", 1.0, 1e7, 50000.0
                ),
                "Bonus": c[0].number_input(
                    "Bonus", 0.0, 1e6, 0.0
                ),
                "Performance_Score": c[1].number_input(
                    "Performance score (0-5)",
                    0.0,
                    5.0,
                    3.0,
                    0.5,
                ),
            }

            if st.form_submit_button("Add employee"):
                try:
                    db.add_employee(employee)

                    db.log_activity(
                        uid,
                        f"added employee {employee['Employee_ID']}",
                    )

                    st.success(
                        "Employee added. It appears in the table "
                        "the next time the page refreshes."
                    )

                except Exception as ex:
                    st.error(
                        f"The employee could not be added: {ex}"
                    )

    with st.expander("Delete an employee"):
        who = st.selectbox(
            "Employee",
            df["Employee_ID"],
        )

        if st.button("Delete employee"):
            db.delete_employee(who)

            db.log_activity(
                uid,
                f"deleted employee {who}",
            )

            st.rerun()


def page_employees(df, is_db):
    banner(
        "Employees",
        "Search, filter and manage employee records",
    )

    c1, c2, c3 = st.columns(3)

    dept = c1.multiselect(
        "Department",
        sorted(df["Department"].unique()),
    )

    role = c2.multiselect(
        "Designation",
        sorted(df["Designation"].astype(str).unique()),
    )

    lo = int(df["Experience_Years"].min())
    hi = int(df["Experience_Years"].max())

    exp = c3.slider(
        "Experience (years)",
        lo,
        max(hi, lo + 1),
        (lo, max(hi, lo + 1)),
    )

    q = st.text_input("Search by ID or name")

    filtered = df[df["Experience_Years"].between(*exp)]

    if dept:
        filtered = filtered[
            filtered["Department"].isin(dept)
        ]

    if role:
        filtered = filtered[
            filtered["Designation"].astype(str).isin(role)
        ]

    if q:
        filtered = filtered[
            filtered["Employee_ID"].astype(str).str.contains(
                q,
                case=False,
            )
            | filtered["Name"].astype(str).str.contains(
                q,
                case=False,
            )
        ]

    st.caption(f"{len(filtered)} employees")

    st.dataframe(
        filtered,
        hide_index=True,
        use_container_width=True,
    )

    st.download_button(
        "Download filtered records (CSV)",
        filtered.to_csv(index=False),
        "employees_filtered.csv",
    )

    if is_db and st.session_state.user["role"] == "admin":
        manage_employees(df)


# ============================================================
# SALARY AND PERFORMANCE ANALYSIS
# ============================================================

def page_analysis(df):
    banner(
        "Salary and performance analysis",
        "Statistics, experience trends and correlations",
    )

    t1, t2, t3 = st.tabs(
        ["Salary", "Performance", "Correlation"]
    )

    with t1:
        st.dataframe(
            an.salary_summary(df).round(2).to_frame("Value"),
            use_container_width=True,
        )

        show(an.fig_salary_dist(df))

        st.subheader("By experience")

        st.dataframe(
            an.by_experience(df),
            hide_index=True,
            use_container_width=True,
        )

        show(an.fig_experience(df))

    with t2:
        st.dataframe(
            an.performance_summary(df)
            .round(2)
            .to_frame("Value"),
            use_container_width=True,
        )

        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))

    with t3:
        st.dataframe(
            an.correlation(df).round(2),
            use_container_width=True,
        )

        show(an.fig_corr(df))


# ============================================================
# DEPARTMENTS
# ============================================================

def page_departments(df):
    banner(
        "Departments",
        "Employee count, salary and performance by department",
    )

    st.dataframe(
        an.dept_table(df),
        hide_index=True,
        use_container_width=True,
    )

    a, b = st.columns(2)

    with a:
        show(an.fig_dept_count(df))

    with b:
        show(an.fig_dept_salary(df))


# ============================================================
# SQL EXPLORER
# ============================================================

def page_sql():
    banner(
        "SQL explorer",
        "Run the prepared queries or write your own SELECT",
    )

    titles = [
        f"Q{i}. {title}"
        for i, (title, _) in enumerate(Q.QUERIES, 1)
    ]

    pick = st.selectbox(
        "Prepared query",
        titles,
    )

    sql = st.text_area(
        "SQL (read-only)",
        Q.QUERIES[titles.index(pick)][1],
        height=130,
    )

    if st.button("Run query"):
        if not sql.strip().lower().startswith("select"):
            st.error(
                "Only SELECT statements can be run here."
            )

        else:
            try:
                st.dataframe(
                    db.run_query(sql),
                    hide_index=True,
                    use_container_width=True,
                )

            except Exception as ex:
                st.error(f"The query failed: {ex}")


# ============================================================
# UPLOAD AND EXPORT
# ============================================================

def page_data(df):
    banner(
        "Upload and export",
        "Analyse your own CSV and download results",
    )

    uploaded_file = st.file_uploader(
        "Upload a CSV with the same columns as the sample dataset",
        type="csv",
    )

    if uploaded_file and st.button("Analyse this file"):
        try:
            st.session_state.upload, log = an.prepare(
                an.load_data(uploaded_file)
            )

            st.toast(
                "File analysed. Choose 'Uploaded file' as the "
                "data source in the sidebar."
            )

            st.rerun()

        except Exception as ex:
            st.error(str(ex))

    st.subheader("Export")

    columns = st.columns(4)

    columns[0].download_button(
        "Cleaned data (CSV)",
        df.to_csv(index=False),
        "Employee_Salary_Performance_Cleaned.csv",
    )

    columns[1].download_button(
        "KPI summary (CSV)",
        pd.Series(an.kpis(df)).rename("value").to_csv(),
        "kpi_summary.csv",
    )

    columns[2].download_button(
        "Correlation matrix (CSV)",
        an.correlation(df).round(3).to_csv(),
        "correlation_matrix.csv",
    )

    columns[3].download_button(
        "Printable report (HTML)",
        an.report_html(
            df,
            st.session_state.user["username"],
        ),
        "report.html",
        mime="text/html",
    )


# ============================================================
# ADMINISTRATION
# ============================================================

def page_admin():
    banner(
        "Administration",
        "Registered users and recent activity",
    )

    st.subheader("Registered users")

    st.dataframe(
        pd.DataFrame(db.list_users()),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Recent activity")

    st.dataframe(
        pd.DataFrame(db.recent_activity()),
        hide_index=True,
        use_container_width=True,
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    user = st.session_state.user

    pages = [
        "Dashboard",
        "Employees",
        "Analysis",
        "Departments",
        
        "Upload and export",
    ]

    if user["role"] == "admin":
        pages.append("Administration")

    pending_page = st.session_state.pop(
        "_pending_page_navigation",
        None,
    )

    if pending_page in pages:
        st.session_state["page_navigation"] = pending_page

    # ============================================================
# SIDEBAR — THEME SWITCHER AND NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            padding: 12px 5px 18px 5px;
            border-bottom: 1px solid #3a4b63;
            margin-bottom: 16px;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <div style="
                    width: 43px;
                    height: 43px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(
                        135deg,
                        #0f766e,
                        #14b8a6
                    );
                    border-radius: 12px;
                    color: white;
                    font-size: 23px;
                    font-weight: bold;
                ">S</div>

                <div>
                    <div style="
                        font-size: 20px;
                        font-weight: 800;
                        color: #ffffff;
                    ">StaffMetrics</div>

                    <div style="
                        font-size: 11px;
                        color: #a7b5ca;
                    ">Employee Intelligence</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
# SIDEBAR USER PROFILE
# ============================================================

user = st.session_state.get("user")

if user is None:
    st.error("Your session has expired. Please sign in again.")
    st.stop()

display_name = user.get("full_name") or user.get("username", "User")
display_role = user.get("role", "user").upper()

st.markdown(
    f"""
    <div style="
        padding: 12px;
        margin-bottom: 16px;
        background: #1d2c43;
        border: 1px solid #3a4b63;
        border-radius: 12px;
    ">
        <div style="
            color: #99f6e4;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
            margin-bottom: 6px;
        ">SIGNED IN AS</div>

        <div style="
            color: #ffffff;
            font-size: 16px;
            font-weight: 700;
        ">{display_name}</div>

        <div style="
            display: inline-block;
            margin-top: 7px;
            padding: 4px 9px;
            border-radius: 6px;
            background: rgba(45,212,191,0.14);
            color: #99f6e4;
            font-size: 11px;
            font-weight: 700;
        ">{display_role}</div>
    </div>
    """,
    unsafe_allow_html=True,
)    
# --------------------------------------------------------
    # THEME SELECTOR
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            color: #99f6e4;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            margin: 8px 0;
        ">🎨 APPEARANCE</div>
        """,
        unsafe_allow_html=True,
    )

    theme_choice = st.radio(
        "Choose website theme",
        options=["☀️ Light", "🌙 Dark"],
        index=0 if APP_THEME == "light" else 1,
        horizontal=True,
        key="theme_choice",
        label_visibility="collapsed",
    )

    st.caption(
        "Switch between light and dark appearance."
    )

    st.divider()

    # --------------------------------------------------------
    # NAVIGATION MENU
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            color: #99f6e4;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            margin: 8px 0 12px 0;
        ">📍 MAIN MENU</div>
        """,
        unsafe_allow_html=True,
    )

    pages = [
        "Dashboard",
        "Employees",
        "Analysis",
        "Departments",
        "SQL explorer",
        "Upload and export",
    ]

    if user["role"] == "admin":
        pages.append("Administration")

    # Emoji labels make every navigation option easier to identify.
    page_icons = {
        "Dashboard": "📊",
        "Employees": "👥",
        "Analysis": "📈",
        "Departments": "🏢",
        "SQL explorer": "🗄️",
        "Upload and export": "📂",
        "Administration": "⚙️",
    }

    page_labels = {
        page: f"{page_icons.get(page, '📌')}  {page}"
        for page in pages
    }

    label_to_page = {
        label: page
        for page, label in page_labels.items()
    }

    # Preserve programmatic navigation from the KPI cards.
    pending_page = st.session_state.pop(
        "_pending_page_navigation",
        None,
    )

    if pending_page in pages:
        st.session_state["page_navigation"] = pending_page

    current_page = st.session_state.get(
        "page_navigation",
        "Dashboard",
    )

    if current_page not in pages:
        current_page = "Dashboard"

    current_label = page_labels[current_page]

    selected_label = st.radio(
        "Application navigation",
        options=list(page_labels.values()),
        index=list(page_labels.values()).index(current_label),
        key="sidebar_navigation_choice",
        label_visibility="collapsed",
    )

    page = label_to_page[selected_label]

    # Keep the canonical page name for existing navigation code.
    st.session_state["page_navigation"] = page

    st.divider()

    # --------------------------------------------------------
    # DATA SOURCE
    # --------------------------------------------------------

    uploaded_data = st.session_state.get("upload")

    data_sources = ["Employee database"]

    if uploaded_data is not None:
        data_sources.append("Uploaded file")

    source = st.selectbox(
        "📁 Data source",
        data_sources,
        key="sidebar_data_source",
    )

    st.divider()

    # --------------------------------------------------------
    # SIGN OUT
    # --------------------------------------------------------

    if st.button(
        "🚪 Sign out",
        key="sidebar_signout",
        use_container_width=True,
    ):
        db.log_activity(
            user["id"],
            "signed out",
        )

        clear_login_cookie()

        st.session_state.pop("user", None)

        st.rerun()

# ------------------------------------------------------------
# SELECT DATA SOURCE
# ------------------------------------------------------------

is_db = source == "Employee database"

if is_db:
    df = db.employee_frame()
else:
    df = uploaded_data
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

    elif page == "Administration":
        page_admin()


# ============================================================
# RESTORE LOGIN AFTER A REFRESH
# ============================================================

if "user" not in st.session_state:
    saved_user = restore_login_cookie()

    if saved_user is not None:
        st.session_state["user"] = saved_user


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if "user" in st.session_state:
    main()
else:
    auth_page()
