import re

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import analytics as an, auth, database as db


# ==================== APPLICATION CONFIGURATION ====================

st.set_page_config(
    page_title="Employee Salary & Performance Analysis",
    page_icon="📊",
    layout="wide"
)

db.init_db()

CSV = "data/employee_salary_performance.csv"

if not db.is_seeded():
    db.seed_database(an.prepare(an.load_data(CSV))[0])


# ==================== THEME CONFIGURATION ====================

THEME = st.session_state.get("theme_choice", "Light")
IS_DARK = THEME == "Dark"

if IS_DARK:
    PAGE_BG = "#0B1020"
    SURFACE = "#121D32"
    TEXT = "#F1F5F9"
    MUTED = "#B9C9E4"
    BORDER = "#344866"
    INPUT_BG = "#17243B"
    ACCENT = "#5EEAD4"
else:
    PAGE_BG = "#F5F7FC"
    SURFACE = "#FFFFFF"
    TEXT = "#172033"
    MUTED = "#64748B"
    BORDER = "#D9E2F0"
    INPUT_BG = "#FFFFFF"
    ACCENT = "#0F766E"


# ==================== GLOBAL STYLING ====================

st.markdown(
    f"""
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap'
    );

    :root {{
        color-scheme: {"dark" if IS_DARK else "light"};
        --page-bg: {PAGE_BG};
        --surface: {SURFACE};
        --text: {TEXT};
        --muted: {MUTED};
        --border: {BORDER};
        --input-bg: {INPUT_BG};
        --accent: {ACCENT};
    }}

    html,
    body,
    [class*="css"],
    [data-testid="stAppViewContainer"] {{
        font-family: 'DM Sans', sans-serif !important;
    }}

    .stApp,
    [data-testid="stAppViewContainer"] {{
        background: var(--page-bg) !important;
        color: var(--text) !important;
    }}

    [data-testid="stHeader"] {{
        background: var(--page-bg) !important;
    }}

    .block-container {{
        padding-top: 1.7rem;
        max-width: 1350px;
        padding-bottom: 3rem;
    }}

    /* Typography */

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Manrope', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.035em;
        color: var(--text) !important;
    }}

    h1 {{
        font-size: 2.15rem !important;
    }}

    h2 {{
        font-size: 1.65rem !important;
    }}

    h3 {{
        font-size: 1.25rem !important;
    }}

    p,
    li,
    label,
    legend,
    small,
    summary,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"] {{
        color: var(--text);
    }}

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {{
        color: var(--muted) !important;
    }}

    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] *,
    [data-testid="stMarkdownContainer"] p {{
        color: var(--text) !important;
    }}

    /* Sidebar */

    [data-testid="stSidebar"] {{
        background: {"linear-gradient(180deg, #111A31, #172640)" if IS_DARK else "linear-gradient(180deg, #FFFFFF, #EDF3FB)"} !important;
        border-right: 1px solid var(--border);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--text);
    }}

    /* Dashboard banner */

    .banner {{
        padding: 25px 29px;
        border-radius: 17px;
        margin-bottom: 22px;
        box-shadow: 0 9px 28px rgba(15, 23, 42, 0.10);
        border: 1px solid transparent;
        background: {"linear-gradient(120deg, #172554, #164E63)" if IS_DARK else "linear-gradient(120deg, #14213D, #155E75)"};
    }}

    .banner h1 {{
        color: #FFFFFF !important;
        font-family: 'Manrope', sans-serif !important;
        font-size: 2rem !important;
        margin: 0;
    }}

    .banner p {{
        color: #DBEAFE !important;
        margin: 7px 0 0;
        line-height: 1.7;
    }}

    /* KPI cards */

    .kpi {{
        border-radius: 15px;
        padding: 19px;
        border: 1px solid var(--border);
        border-top: 4px solid {"#2DD4BF" if IS_DARK else "#0F766E"};
        background: {"linear-gradient(145deg, #17243B, #1C2C46)" if IS_DARK else "linear-gradient(145deg, #FFFFFF, #F1F7FC)"};
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .kpi:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
    }}

    .kpi span {{
        display: block;
        color: {"#BDCCE4" if IS_DARK else "#53647D"} !important;
        font-size: 0.86rem;
        font-weight: 600;
        margin-bottom: 8px;
    }}

    .kpi b {{
        display: block;
        color: {"#F8FAFC" if IS_DARK else "#14213D"} !important;
        font-family: 'Manrope', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
    }}

    /* Buttons */

    [data-testid="stButton"] > button,
    [data-testid="stDownloadButton"] > button {{
        border-radius: 10px;
        min-height: 42px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 700;
        color: var(--text) !important;
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        transition: transform 0.18s ease,
                    box-shadow 0.18s ease,
                    background 0.18s ease;
    }}

    [data-testid="stButton"] > button *,
    [data-testid="stDownloadButton"] > button * {{
        color: inherit !important;
    }}

    [data-testid="stButton"] > button:hover,
    [data-testid="stDownloadButton"] > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
        border-color: var(--accent) !important;
    }}

    /* Inputs */

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {{
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        background: var(--input-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 9px;
    }}

    input::placeholder,
    textarea::placeholder {{
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted) !important;
        opacity: 1;
    }}

    /* Selectboxes and dropdowns */

    [data-baseweb="select"] > div {{
        background: var(--input-bg) !important;
        border-color: var(--border) !important;
    }}

    [data-baseweb="select"] input,
    [data-baseweb="select"] span,
    [data-baseweb="select"] div {{
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }}

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {{
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }}

    [role="option"] {{
        background: var(--surface) !important;
        color: var(--text) !important;
    }}

    [role="option"]:hover {{
        background: {"#263B5A" if IS_DARK else "#E6F4F8"} !important;
    }}

    /* Checkboxes and radio buttons */

    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] label *,
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] label *,
    [data-testid="stToggle"] label {{
        color: var(--text) !important;
    }}

    /* Tabs */

    [data-testid="stTabs"] button,
    [data-testid="stTabs"] button p {{
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif;
        font-weight: 700;
    }}

    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: var(--accent) !important;
    }}

    /* Data tables */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
        color: var(--text) !important;
        border-color: var(--border) !important;
    }}

    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"] {{
        color: var(--text) !important;
    }}

    /* Expanders */

    [data-testid="stExpander"] {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px;
    }}

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {{
        color: var(--text) !important;
    }}

    /* Dialog */

    [data-testid="stDialog"] [role="dialog"] {{
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px;
        animation: metricDialogEntrance 0.22s ease-out;
    }}

    @keyframes metricDialogEntrance {{
        from {{
            opacity: 0;
            transform: translateY(10px) scale(0.985);
        }}
        to {{
            opacity: 1;
            transform: translateY(0) scale(1);
        }}
    }}

    /* Login page */

    .login-brand {{
        background: linear-gradient(145deg, #14213D, #155E75);
        color: #FFFFFF;
        padding: 42px 30px;
        border-radius: 20px 0 0 20px;
        min-height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 12px 35px rgba(20, 33, 61, 0.14);
    }}

    .login-brand h1 {{
        color: #FFFFFF !important;
        font-size: 2.5rem !important;
        margin-top: 8px;
    }}

    .login-brand p {{
        color: #DBEAFE !important;
        font-size: 1rem;
        line-height: 1.8;
    }}

    .brand-icon {{
        width: 84px;
        height: 84px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 24px;
        font-size: 2.8rem;
        background: rgba(255, 255, 255, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        margin-bottom: 14px;
    }}

    .login-card {{
        padding: 25px 28px;
        border: 1px solid var(--border);
        border-radius: 0 20px 20px 0;
        min-height: 150px;
        background: var(--surface);
        box-shadow: 0 12px 35px rgba(20, 33, 61, 0.08);
    }}

    .login-heading {{
        color: var(--text) !important;
        font-family: 'Manrope', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 5px;
    }}

    .login-description {{
        color: var(--muted) !important;
        margin-bottom: 20px;
    }}

    .security-note {{
        color: var(--muted) !important;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 20px;
    }}

    a {{
        color: {"#67E8F9" if IS_DARK else "#075985"} !important;
    }}

    hr {{
        border-color: var(--border) !important;
    }}

    @media (prefers-reduced-motion: reduce) {{
        *,
        *::before,
        *::after {{
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }}
    }}

    @media (max-width: 700px) {{
        .block-container {{
            padding-top: 1rem;
        }}

        .login-brand {{
            border-radius: 18px 18px 0 0;
            min-height: auto;
            padding: 25px;
        }}

        .login-card {{
            border-radius: 0 0 18px 18px;
            min-height: auto;
            padding: 20px;
        }}

        h1 {{
            font-size: 1.8rem !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ==================== COMMON FUNCTIONS ====================

def banner(title, subtitle=""):
    st.markdown(
        f"""
        <div class="banner">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
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
            unsafe_allow_html=True
        )


def show(fig):
    st.pyplot(fig)
    plt.close(fig)


# ==================== KPI INFORMATION ====================

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
            "The median is the middle basic-salary value after "
            "salaries are ordered. It can describe a typical salary "
            "more robustly than the average when unusually high "
            "or low salaries are present."
        ),
        "module": "Analysis",
    },
    "Minimum salary": {
        "icon": "📉",
        "description": (
            "The lowest basic salary among employees matching "
            "the current dashboard filters. Use the analysis module "
            "to explore salary distributions and differences."
        ),
        "module": "Analysis",
    },
    "Maximum salary": {
        "icon": "📈",
        "description": (
            "The highest basic salary among employees matching "
            "the current dashboard filters. Use the analysis module "
            "to explore salary distributions and differences."
        ),
        "module": "Analysis",
    },
    "Average performance": {
        "icon": "⭐",
        "description": (
            "The average performance score for employees matching "
            "the current dashboard filters. It summarizes the "
            "performance level of the selected workforce."
        ),
        "module": "Analysis",
    },
    "Maximum performance": {
        "icon": "🏆",
        "description": (
            "The highest performance score among employees matching "
            "the current dashboard filters. Use the analysis module "
            "for additional performance summaries and charts."
        ),
        "module": "Analysis",
    },
}


# ==================== NAVIGATION ====================

def request_page_navigation(module):
    st.session_state["_pending_page_navigation"] = module
    st.session_state.pop("_metric_dialog", None)
    st.rerun()


# ==================== INTERACTIVE KPI CARDS ====================

def interactive_kpi_cards(items, section_key):
    columns = st.columns(len(items))

    for index, (label, value) in enumerate(items):
        icon = (
            "👥"
            if label == "Employees"
            else KPI_DETAILS[label]["icon"]
        )

        with columns[index]:
            clicked = st.button(
                f"{icon}  **{label}**\n\n"
                f"# {value}\n\n"
                "Click to explore  ↗",
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


# ==================== KPI INFORMATION POP-UP ====================

@st.dialog("Metric overview", width="small")
def metric_information_dialog():
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
        f"Open {details['module']} module →",
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


# ==================== LOGIN AND REGISTRATION ====================

def auth_page():
    # The theme selector works before login as well.
    st.selectbox(
        "🎨 Appearance",
        ["Light", "Dark"],
        key="theme_choice"
    )

    # Streamlit reruns the app after changing the theme.
    # The global CSS then applies the newly selected colors.

    is_dark = st.session_state.get("theme_choice", "Light") == "Dark"

    login_background = (
        "radial-gradient(circle at top left, "
        "rgba(45, 212, 191, 0.12), transparent 35%), "
        "linear-gradient(135deg, #080E1B, #101D32)"
        if is_dark
        else
        "radial-gradient(circle at top left, "
        "rgba(59, 130, 246, 0.15), transparent 35%), "
        "linear-gradient(135deg, #F8FAFC, #EAF0FB)"
    )

    st.markdown(
        f"""
        <style>
        .stApp,
        [data-testid="stAppViewContainer"] {{
            background: {login_background} !important;
        }}

        [data-testid="stSidebar"] {{
            display: none;
        }}

        .block-container {{
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 1.15], gap="small")

    # ==================== BRAND PANEL ====================

    with left:
        st.markdown(
            """
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
            """,
            unsafe_allow_html=True
        )

    # ==================== LOGIN AND REGISTRATION ====================

    with right:
        st.markdown(
            """
            <div class="login-card">
                <div class="login-heading">Welcome back!</div>

                <div class="login-description">
                    Sign in to access your analytics dashboard.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        login_tab, register_tab = st.tabs(
            ["🔐 Sign in", "✨ Create account"]
        )

        # ==================== LOGIN ====================

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

            st.checkbox(
                "Remember me on this session",
                key="remember_me"
            )

            if st.button("Sign in", key="login_button"):
                if not login_id.strip() or not login_password:
                    st.warning(
                        "Enter your username/email and password."
                    )
                else:
                    user = auth.login(login_id, login_password)

                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error(
                            "The username/email or password is incorrect."
                        )

            with st.expander("Forgot your password?"):
                st.write(
                    "Password recovery requires a configured "
                    "email or authentication provider."
                )
                st.info(
                    "The password-reset service must be configured "
                    "before a recovery email can be sent."
                )

        # ==================== REGISTRATION ====================

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
                "default"
                if show_register_password
                else "password"
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

            # Password strength

            if password:
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
                "Use at least 8 characters. A combination of uppercase "
                "letters, lowercase letters, numbers, and symbols "
                "is recommended."
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
            """
            <div class="security-note">
                StaffMetrics · Employee Salary & Performance Analysis
            </div>
            """,
            unsafe_allow_html=True
        )


# ==================== EXECUTIVE DASHBOARD ====================

def page_dashboard(df):
    banner(
        "Executive Dashboard",
        f"Welcome, "
        f"{st.session_state.user['full_name'] or st.session_state.user['username']}"
    )

    if df.empty:
        st.warning("No employee records are available.")
        return

    st.subheader("Dashboard Filters")

    departments = sorted(
        df["Department"].dropna().astype(str).unique().tolist()
    )

    designations = sorted(
        df["Designation"].dropna().astype(str).unique().tolist()
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        selected_department = st.selectbox(
            "Department",
            ["All departments"] + departments,
            key="dashboard_department"
        )

    with c2:
        selected_designation = st.selectbox(
            "Designation",
            ["All designations"] + designations,
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

    # Salary range

    salary_values = pd.to_numeric(
        df["Basic_Salary"],
        errors="coerce"
    ).dropna()

    if salary_values.empty:
        st.warning("Salary information is unavailable in this dataset.")
        return

    salary_min = float(salary_values.min())
    salary_max = float(salary_values.max())

    if salary_min == salary_max:
        selected_salary = (salary_min, salary_max)
        st.caption(f"Available salary: {salary_min:,.0f}")
    else:
        selected_salary = st.slider(
            "Basic salary range",
            min_value=salary_min,
            max_value=salary_max,
            value=(salary_min, salary_max),
            key="dashboard_salary"
        )

    # Dynamic experience range

    exp_values = pd.to_numeric(
        df["Experience_Years"],
        errors="coerce"
    ).dropna()

    if exp_values.empty:
        st.warning(
            "Experience information is unavailable in this dataset."
        )
        return

    exp_min = float(exp_values.min())
    exp_max = float(exp_values.max())

    st.markdown("#### Experience Range")
    st.caption(
        f"Available experience: {exp_min:g}–{exp_max:g} years"
    )

    c4, c5 = st.columns(2)

    with c4:
        selected_exp_min = st.number_input(
            "Minimum experience (years)",
            min_value=exp_min,
            max_value=exp_max,
            value=exp_min,
            step=1.0,
            key="dashboard_experience_min"
        )

    with c5:
        selected_exp_max = st.number_input(
            "Maximum experience (years)",
            min_value=exp_min,
            max_value=exp_max,
            value=exp_max,
            step=1.0,
            key="dashboard_experience_max"
        )

    if selected_exp_min > selected_exp_max:
        st.warning(
            "Minimum experience exceeds maximum experience. "
            "The values will be swapped for filtering."
        )
        selected_experience = (
            selected_exp_max,
            selected_exp_min
        )
    else:
        selected_experience = (
            selected_exp_min,
            selected_exp_max
        )

    # Performance range

    perf_values = pd.to_numeric(
        df["Performance_Score"],
        errors="coerce"
    ).dropna()

    if perf_values.empty:
        st.warning(
            "Performance information is unavailable in this dataset."
        )
        return

    perf_min = float(perf_values.min())
    perf_max = float(perf_values.max())

    if perf_min == perf_max:
        selected_performance = (perf_min, perf_max)
        st.caption(
            f"Available performance score: {perf_min:g}"
        )
    else:
        selected_performance = st.slider(
            "Performance score range",
            min_value=perf_min,
            max_value=perf_max,
            value=(perf_min, perf_max),
            key="dashboard_performance"
        )

    # Apply filters

    filtered_df = df.copy()

    if selected_department != "All departments":
        filtered_df = filtered_df[
            filtered_df["Department"].astype(str)
            == selected_department
        ]

    if selected_designation != "All designations":
        filtered_df = filtered_df[
            filtered_df["Designation"].astype(str)
            == selected_designation
        ]

    filtered_df = filtered_df[
        pd.to_numeric(
            filtered_df["Basic_Salary"],
            errors="coerce"
        ).between(*selected_salary)
        &
        pd.to_numeric(
            filtered_df["Experience_Years"],
            errors="coerce"
        ).between(*selected_experience)
        &
        pd.to_numeric(
            filtered_df["Performance_Score"],
            errors="coerce"
        ).between(*selected_performance)
    ]

    if filtered_df.empty:
        st.warning(
            "No employees match your selected filters. "
            "Try changing one or more filters."
        )
        return

    st.caption(
        f"Showing {len(filtered_df):,} of {len(df):,} employee records."
    )

    # KPI cards

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
            ("Average performance", f"{k['average_performance']:.2f}"),
            ("Maximum performance", f"{k['maximum_performance']:.2f}"),
        ],
        section_key="dashboard_kpi_bottom",
    )

    if st.session_state.get("_metric_dialog"):
        metric_information_dialog()

    # Automated insights

    st.subheader("Automated Insights")

    for line in an.insights(filtered_df):
        st.info(line)

    # Visual analytics

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

    # Filtered employee records

    with st.expander("View filtered employee records"):
        st.dataframe(
            filtered_df,
            hide_index=True,
            use_container_width=True
        )

        st.download_button(
            "Download filtered employee data",
            filtered_df.to_csv(index=False),
            "filtered_employee_records.csv",
            mime="text/csv"
        )


# ==================== EMPLOYEE MANAGEMENT ====================

def manage_employees(df):
    uid = st.session_state.user["id"]

    with st.expander("Add an employee"), st.form("add_emp"):
        c = st.columns(3)

        e = {
            "Employee_ID": c[0].text_input("Employee ID"),
            "Name": c[1].text_input("Name"),
            "Age": c[2].number_input("Age", 18, 70, 30),
            "Gender": c[0].selectbox("Gender", ["Female", "Male"]),
            "Department": c[1].selectbox(
                "Department",
                sorted(df["Department"].unique())
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
                "Performance score (0-5)", 0.0, 5.0, 3.0, 0.5
            )
        }

        if st.form_submit_button("Add employee"):
            try:
                db.add_employee(e)

                db.log_activity(
                    uid,
                    f"added employee {e['Employee_ID']}"
                )

                st.success(
                    "Employee added successfully. "
                    "Refresh the page to see the updated table."
                )
            except Exception as ex:
                st.error(f"The employee could not be added: {ex}")

    with st.expander("Delete an employee"):
        who = st.selectbox("Employee", df["Employee_ID"])

        if st.button("Delete employee"):
            db.delete_employee(who)

            db.log_activity(
                uid,
                f"deleted employee {who}"
            )

            st.rerun()


# ==================== EMPLOYEES PAGE ====================

def page_employees(df, is_db):
    banner(
        "Employees",
        "Search, filter and manage employee records"
    )

    if df.empty:
        st.warning("No employee records are available.")
        return

    c1, c2, c3 = st.columns(3)

    dept = c1.multiselect(
        "Department",
        sorted(df["Department"].dropna().unique())
    )

    role = c2.multiselect(
        "Designation",
        sorted(df["Designation"].dropna().astype(str).unique())
    )

    experience_values = pd.to_numeric(
        df["Experience_Years"],
        errors="coerce"
    ).dropna()

    if experience_values.empty:
        st.warning("Experience information is unavailable.")
        return

    lo = int(experience_values.min())
    hi = int(experience_values.max())

    if lo == hi:
        exp = (lo, hi)
        c3.caption(f"Experience: {lo} years")
    else:
        exp = c3.slider(
            "Experience (years)",
            lo,
            hi,
            (lo, hi),
            key="employee_experience_filter"
        )

    q = st.text_input("Search by ID or name")

    f = df[
        pd.to_numeric(
            df["Experience_Years"],
            errors="coerce"
        ).between(*exp)
    ]

    if dept:
        f = f[f["Department"].isin(dept)]

    if role:
        f = f[f["Designation"].astype(str).isin(role)]

    if q:
        f = f[
            f["Employee_ID"].astype(str).str.contains(
                q, case=False, na=False
            )
            |
            f["Name"].astype(str).str.contains(
                q, case=False, na=False
            )
        ]

    st.caption(f"{len(f)} employees")

    st.dataframe(
        f,
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        "Download filtered records (CSV)",
        f.to_csv(index=False),
        "employees_filtered.csv"
    )

    if is_db and st.session_state.user["role"] == "admin":
        manage_employees(df)


# ==================== ANALYSIS PAGE ====================

def page_analysis(df):
    banner(
        "Salary and performance analysis",
        "Statistics, experience trends and correlations"
    )

    if df.empty:
        st.warning("No employee records are available for analysis.")
        return

    t1, t2, t3 = st.tabs(
        ["Salary", "Performance", "Correlation"]
    )

    def summary_value(summary, word, fallback_index):
        for label, value in summary.items():
            if word in str(label).lower():
                return value

        return summary.iloc[fallback_index]

    with t1:
        st.subheader("Salary Summary")

        salary_summary = an.salary_summary(df).round(2)

        salary_table = pd.DataFrame({
            "Metric": ["Average", "Minimum", "Maximum"],
            "Salary": [
                summary_value(salary_summary, "average", 0),
                summary_value(salary_summary, "minimum", 1),
                summary_value(salary_summary, "maximum", 2),
            ],
        })

        st.dataframe(
            salary_table,
            hide_index=True,
            use_container_width=True
        )

        show(an.fig_salary_dist(df))

        st.subheader("By experience")

        st.dataframe(
            an.by_experience(df),
            hide_index=True,
            use_container_width=True
        )

        show(an.fig_experience(df))

    with t2:
        st.subheader("Performance Summary")

        performance_summary = an.performance_summary(df).round(2)

        performance_table = pd.DataFrame({
            "Metric": ["Average", "Minimum", "Maximum"],
            "Performance": [
                summary_value(performance_summary, "average", 0),
                summary_value(performance_summary, "minimum", 1),
                summary_value(performance_summary, "maximum", 2),
            ],
        })

        st.dataframe(
            performance_table,
            hide_index=True,
            use_container_width=True
        )

        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))

    with t3:
        st.dataframe(
            an.correlation(df).round(2),
            use_container_width=True
        )

        show(an.fig_corr(df))


# ==================== DEPARTMENTS PAGE ====================

def page_departments(df):
    banner(
        "Departments",
        "Employee count, salary and performance by department"
    )

    if df.empty:
        st.warning("No employee records are available.")
        return

    st.dataframe(
        an.dept_table(df),
        hide_index=True,
        use_container_width=True
    )

    a, b = st.columns(2)

    with a:
        show(an.fig_dept_count(df))

    with b:
        show(an.fig_dept_salary(df))


# ==================== UPLOAD AND EXPORT ====================

def page_data(df):
    banner(
        "Upload and export",
        "Analyse your own CSV and download results"
    )

    up = st.file_uploader(
        "Upload a CSV with the same columns as the sample dataset",
        type="csv"
    )

    if up and st.button("Analyse this file"):
        try:
            st.session_state.upload, log = an.prepare(
                an.load_data(up)
            )

            st.toast(
                "File analysed. Choose 'Uploaded file' "
                "as the data source in the sidebar."
            )

            st.rerun()

        except Exception as ex:
            st.error(str(ex))

    st.subheader("Export")

    c = st.columns(4)

    c[0].download_button(
        "Cleaned data (CSV)",
        df.to_csv(index=False),
        "Employee_Salary_Performance_Cleaned.csv"
    )

    c[1].download_button(
        "KPI summary (CSV)",
        pd.Series(an.kpis(df)).rename("value").to_csv(),
        "kpi_summary.csv"
    )

    c[2].download_button(
        "Correlation matrix (CSV)",
        an.correlation(df).round(3).to_csv(),
        "correlation_matrix.csv"
    )

    c[3].download_button(
        "Printable report (HTML)",
        an.report_html(
            df,
            st.session_state.user["username"]
        ),
        "report.html",
        mime="text/html"
    )


# ==================== ADMINISTRATION ====================

def page_admin():
    banner(
        "Administration",
        "Registered users and recent activity"
    )

    st.subheader("Registered users")

    st.dataframe(
        pd.DataFrame(db.list_users()),
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Recent activity")

    st.dataframe(
        pd.DataFrame(db.recent_activity()),
        hide_index=True,
        use_container_width=True
    )


# ==================== MAIN APPLICATION ====================

def main():
    user = st.session_state.user

    pages = [
        "Dashboard",
        "Employees",
        "Analysis",
        "Departments",
        "Upload and export"
    ]

    if user["role"] == "admin":
        pages.append("Administration")

    pending_page = st.session_state.pop(
        "_pending_page_navigation",
        None
    )

    if pending_page in pages:
        st.session_state["page_navigation"] = pending_page

    with st.sidebar:
        st.selectbox(
            "Appearance",
            ["Light", "Dark"],
            key="theme_choice"
        )

        st.markdown(
            f"### {user['full_name'] or user['username']}"
        )

        st.caption(f"{user['role'].title()} account")

        page = st.selectbox(
            "Navigate to page",
            pages,
            key="page_navigation"
        )

        up = st.session_state.get("upload")

        data_sources = ["Employee database"]

        if up is not None:
            data_sources.append("Uploaded file")

        src = st.selectbox(
            "Data source",
            data_sources
        )

        if st.button("Sign out"):
            db.log_activity(
                user["id"],
                "signed out"
            )

            del st.session_state["user"]
            st.rerun()

    is_db = src == "Employee database"

    if is_db:
        df = db.employee_frame()
    else:
        df = up

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
        if user["role"] == "admin":
            page_admin()
        else:
            st.error(
                "You do not have permission to access this page."
            )


# ==================== APPLICATION ENTRY POINT ====================

if "user" not in st.session_state:
    auth_page()
else:
    main()
