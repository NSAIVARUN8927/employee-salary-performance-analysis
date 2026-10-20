import os
import re
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import extra_streamlit_components as stx

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from backend import analytics as an, auth, database as db


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StaffMetrics | Employee Analytics",
    page_icon="📊",
    layout="wide",
)

db.init_db()

CSV = "data/employee_salary_performance.csv"

if not db.is_seeded():
    db.seed_database(an.prepare(an.load_data(CSV))[0])


# ============================================================
# LOGIN COOKIE CONFIGURATION
# ============================================================

COOKIE_NAME = "staffmetrics_auth"
COOKIE_MAX_AGE = 7 * 24 * 60 * 60

APP_SECRET = os.environ.get("STAFFMETRICS_SECRET_KEY")

if not APP_SECRET:
    try:
        APP_SECRET = st.secrets["STAFFMETRICS_SECRET_KEY"]
    except (KeyError, FileNotFoundError):
        APP_SECRET = "local-development-only-change-this-secret"

auth_serializer = URLSafeTimedSerializer(
    APP_SECRET,
    salt="staffmetrics-auth-v1",
)

cookie_manager = stx.CookieManager(
    key="staffmetrics_cookie_manager"
)


def save_login_cookie(user):
    safe_user = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user.get("full_name") or user["username"],
        "role": user["role"],
    }

    token = auth_serializer.dumps(safe_user)

    cookie_manager.set(
        cookie=COOKIE_NAME,
        value=token,
        expires_at=datetime.now() + timedelta(days=7),
        key="staffmetrics_save_auth_cookie",
    )


def restore_login_cookie():
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

        if (
            not required_fields.issubset(user)
            or user["role"] not in {"admin", "user"}
        ):
            clear_login_cookie()
            return None

        return user

    except (BadSignature, SignatureExpired):
        clear_login_cookie()
        return None


def clear_login_cookie():
    try:
        cookie_manager.delete(COOKIE_NAME)
    except Exception:
        pass


# ============================================================
# THEME CONFIGURATION
# ============================================================

if "theme_choice" not in st.session_state:
    st.session_state["theme_choice"] = "Light"

APP_THEME = st.session_state.get("theme_choice", "Light")

if APP_THEME == "Dark":
    BG = "#0b1120"
    CARD = "#151e30"
    SIDEBAR_BG = "#111827"
    TEXT = "#e5e7eb"
    MUTED = "#aab6c8"
    BORDER = "#334155"
    INPUT_BG = "#1e293b"
    TABLE_BG = "#151e30"
    ACCENT = "#2dd4bf"
    BANNER_BG = "#14213d"
    KPI_BG = "#182538"
else:
    BG = "#f5f7fb"
    CARD = "#ffffff"
    SIDEBAR_BG = "#ffffff"
    TEXT = "#172033"
    MUTED = "#64748b"
    BORDER = "#dbe3ee"
    INPUT_BG = "#ffffff"
    TABLE_BG = "#ffffff"
    ACCENT = "#0f766e"
    BANNER_BG = "#14213d"
    KPI_BG = "#ffffff"


# ============================================================
# GLOBAL CSS — LIGHT AND DARK THEMES
# ============================================================

# ============================================================
# GLOBAL STYLING — LIGHT & DARK THEMES
# ============================================================

APP_THEME = st.session_state.get("theme_choice", "☀️ Light")
IS_DARK = APP_THEME == "🌙 Dark"

if IS_DARK:
    BG_COLOR = "#0E1117"
    CARD_COLOR = "#1B2430"
    TEXT_COLOR = "#F1F5F9"
    MUTED_TEXT = "#CBD5E1"
    HEADING_COLOR = "#FFFFFF"
    BORDER_COLOR = "#374151"
    INPUT_BG = "#1F2937"
    SIDEBAR_BG = "#111827"
    SIDEBAR_TEXT = "#F9FAFB"
    ACCENT_COLOR = "#5EEAD4"
    TABLE_HEADER_BG = "#263449"
    HOVER_BG = "#263449"
else:
    BG_COLOR = "#FFFFFF"
    CARD_COLOR = "#F8FAFC"
    TEXT_COLOR = "#1E293B"
    MUTED_TEXT = "#475569"
    HEADING_COLOR = "#14213D"
    BORDER_COLOR = "#D1D5DB"
    INPUT_BG = "#FFFFFF"
    SIDEBAR_BG = "#14213D"
    SIDEBAR_TEXT = "#F8FAFC"
    ACCENT_COLOR = "#0F766E"
    TABLE_HEADER_BG = "#E2E8F0"
    HOVER_BG = "#F1F5F9"


st.markdown(
    f"""
    <style>
    /* ==============================
       MAIN PAGE
    ============================== */

    .stApp {{
        background-color: {BG_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main,
    .block-container {{
        background-color: {BG_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}

    html, body, [class*="css"] {{
        color: {TEXT_COLOR};
    }}

    p, span, label, li, small, div {{
        color: inherit;
    }}

    /* ==============================
       HEADINGS
    ============================== */

    h1, h2, h3, h4, h5, h6 {{
        color: {HEADING_COLOR} !important;
    }}

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
        color: {TEXT_COLOR};
    }}

    [data-testid="stCaptionContainer"] {{
        color: {MUTED_TEXT} !important;
    }}

    /* ==============================
       SIDEBAR
    ============================== */

    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG} !important;
    }}

    [data-testid="stSidebar"] * {{
        color: {SIDEBAR_TEXT};
    }}

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: {SIDEBAR_TEXT} !important;
    }}

    /* ==============================
       INPUT FIELDS
    ============================== */

    input,
    textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        -webkit-text-fill-color: {TEXT_COLOR} !important;
        border-color: {BORDER_COLOR} !important;
    }}

    [data-baseweb="select"] > div {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        border-color: {BORDER_COLOR} !important;
    }}

    [data-baseweb="select"] input,
    [data-baseweb="select"] span {{
        color: {TEXT_COLOR} !important;
    }}

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"],
    [role="option"] {{
        background-color: {CARD_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}

    /* ==============================
       BUTTONS
    ============================== */

    [data-testid="stButton"] button {{
        color: {TEXT_COLOR} !important;
        border-color: {BORDER_COLOR} !important;
    }}

    [data-testid="stButton"] button p {{
        color: {TEXT_COLOR} !important;
    }}

    /* ==============================
       METRICS
    ============================== */

    [data-testid="stMetric"] {{
        background-color: {CARD_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 14px;
    }}

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {{
        color: {MUTED_TEXT} !important;
    }}

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {{
        color: {HEADING_COLOR} !important;
    }}

    /* ==============================
       DATAFRAMES AND TABLES
    ============================== */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
        color: {TEXT_COLOR} !important;
    }}

    [data-testid="stDataFrame"] *,
    [data-testid="stTable"] * {{
        color: {TEXT_COLOR};
    }}

    /* ==============================
       TABS
    ============================== */

    [data-baseweb="tab-list"] {{
        background-color: {BG_COLOR} !important;
    }}

    [data-baseweb="tab"] {{
        color: {TEXT_COLOR} !important;
    }}

    [aria-selected="true"] {{
        color: {ACCENT_COLOR} !important;
    }}

    /* ==============================
       EXPANDERS
    ============================== */

    [data-testid="stExpander"] {{
        background-color: {CARD_COLOR} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 10px;
    }}

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {{
        color: {TEXT_COLOR} !important;
    }}

    /* ==============================
       ALERTS AND DIALOGS
    ============================== */

    [data-testid="stAlert"] {{
        color: {TEXT_COLOR} !important;
    }}

    [data-testid="stDialog"] [role="dialog"] {{
        background-color: {CARD_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}

    [data-testid="stDialog"] h1,
    [data-testid="stDialog"] h2,
    [data-testid="stDialog"] h3,
    [data-testid="stDialog"] p {{
        color: {TEXT_COLOR} !important;
    }}

    /* ==============================
       CUSTOM BANNER
    ============================== */

    .banner {{
        background-color: {SIDEBAR_BG} !important;
        color: {SIDEBAR_TEXT} !important;
        padding: 22px 28px;
        border-radius: 10px;
        margin-bottom: 20px;
    }}

    .banner h1 {{
        color: {SIDEBAR_TEXT} !important;
    }}

    .banner p {{
        color: {SIDEBAR_TEXT} !important;
        opacity: 0.85;
    }}

    /* ==============================
       HOVER EFFECTS
    ============================== */

    [data-testid="stButton"] button:hover {{
        border-color: {ACCENT_COLOR} !important;
        transition: all 0.2s ease;
    }}

    /* ==============================
       LOGIN PAGE
    ============================== */

    .login-heading {{
        color: {HEADING_COLOR} !important;
    }}

    .login-description {{
        color: {MUTED_TEXT} !important;
    }}

    /* ==============================
       GENERAL BORDERS
    ============================== */

    hr {{
        border-color: {BORDER_COLOR} !important;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)
# ============================================================
# COMMON UI HELPERS
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


def show(fig):
    st.pyplot(fig)
    plt.close(fig)


def kpis(items):
    columns = st.columns(len(items))

    for col, (label, value) in zip(columns, items):
        col.metric(label, value)


# ============================================================
# INTERACTIVE KPI CARDS
# ============================================================

KPI_DETAILS = {
    "Average salary": {
        "icon": "💰",
        "description": (
            "The average basic salary for employees matching "
            "the current dashboard filters."
        ),
        "module": "Analysis",
    },
    "Median salary": {
        "icon": "⚖️",
        "description": (
            "The middle salary value when salaries are sorted."
        ),
        "module": "Analysis",
    },
    "Minimum salary": {
        "icon": "📉",
        "description": (
            "The lowest basic salary in the selected employee group."
        ),
        "module": "Analysis",
    },
    "Maximum salary": {
        "icon": "📈",
        "description": (
            "The highest basic salary in the selected employee group."
        ),
        "module": "Analysis",
    },
    "Average performance": {
        "icon": "⭐",
        "description": (
            "The average performance score for the selected employees."
        ),
        "module": "Analysis",
    },
    "Maximum performance": {
        "icon": "🏆",
        "description": (
            "The highest performance score in the selected employee group."
        ),
        "module": "Analysis",
    },
}


def request_page_navigation(module):
    st.session_state["_pending_page_navigation"] = module
    st.session_state.pop("_metric_dialog", None)
    st.rerun()


def interactive_kpi_cards(items, section_key):
    columns = st.columns(len(items))

    icons = {
        "Employees": "👥",
        "Average salary": "💰",
        "Median salary": "⚖️",
        "Minimum salary": "📉",
        "Maximum salary": "📈",
        "Average performance": "⭐",
        "Maximum performance": "🏆",
    }

    for index, (label, value) in enumerate(items):
        with columns[index]:
            clicked = st.button(
                f"{icons.get(label, '📊')}  {label}\n\n{value}",
                key=f"{section_key}_{index}",
                use_container_width=True,
                help=(
                    "Open Employees"
                    if label == "Employees"
                    else f"Learn about {label.lower()}"
                ),
            )

        if clicked:
            if label == "Employees":
                request_page_navigation("Employees")
            else:
                st.session_state["_metric_dialog"] = label
                st.rerun()


@st.dialog("Metric information", width="small")
def metric_information_dialog():
    label = st.session_state.get("_metric_dialog")
    details = KPI_DETAILS.get(label)

    if not details:
        st.write("Metric information is not available.")
        return

    st.markdown(f"### {details['icon']} {label}")
    st.write(details["description"])
    st.divider()

    if st.button(
        f"Open {details['module']} →",
        type="primary",
        use_container_width=True,
    ):
        request_page_navigation(details["module"])

    if st.button("Close", use_container_width=True):
        st.session_state.pop("_metric_dialog", None)
        st.rerun()


# ============================================================
# LOGIN AND REGISTRATION
# ============================================================

def auth_page():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        .login-panel {
            padding: 28px;
            border-radius: 18px;
            border: 1px solid var(--border-color);
            background: var(--card-bg);
        }

        .login-brand {
            background: linear-gradient(145deg, #101d38, #0f766e);
            color: #ffffff;
            border-radius: 18px;
            padding: 40px 30px;
            min-height: 430px;
        }

        .login-brand h1 {
            color: #ffffff !important;
            font-size: 2.5rem;
        }

        .login-brand p {
            color: #e0f2fe !important;
            line-height: 1.8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [1, 1.1],
        gap="large",
        vertical_alignment="center",
    )

    with left:
        st.markdown(
            """
            <div class="login-brand">
                <h1>📊 StaffMetrics</h1>
                <p>
                    Turn employee data into meaningful insights.
                    Understand salaries, monitor performance,
                    and make better workforce decisions.
                </p>
                <p>✓ Employee analytics</p>
                <p>✓ Salary insights</p>
                <p>✓ Performance reports</p>
                <p>✓ Workforce management</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="login-panel">', unsafe_allow_html=True)

        st.subheader("Welcome to StaffMetrics")
        st.caption("Sign in or create an account to continue.")

        login_tab, register_tab = st.tabs(
            ["🔐 Sign in", "✨ Create account"]
        )

        with login_tab:
            login_id = st.text_input(
                "Username or email",
                key="login_username",
            )

            show_password = st.checkbox(
                "Show password",
                key="show_login_password",
            )

            password = st.text_input(
                "Password",
                type="default" if show_password else "password",
                key="login_password",
            )

            remember_me = st.checkbox(
                "Keep me signed in for 7 days",
                value=True,
                key="remember_me",
            )

            if st.button(
                "Sign in →",
                key="login_button",
                type="primary",
                use_container_width=True,
            ):
                if not login_id.strip() or not password:
                    st.warning(
                        "Enter your username/email and password."
                    )
                else:
                    user = auth.login(login_id, password)

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
                    "Password recovery requires a configured "
                    "email or authentication provider."
                )

        with register_tab:
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
                "default"
                if show_register_password
                else "password"
            )

            new_password = st.text_input(
                "Create password",
                type=password_type,
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type=password_type,
                key="register_confirm_password",
            )

            if new_password:
                score = sum(
                    [
                        len(new_password) >= 8,
                        bool(re.search(r"[A-Z]", new_password)),
                        bool(re.search(r"[a-z]", new_password)),
                        bool(re.search(r"[0-9]", new_password)),
                        bool(re.search(r"[^A-Za-z0-9]", new_password)),
                    ]
                )

                if score <= 2:
                    st.warning("Password strength: Weak")
                elif score <= 4:
                    st.info("Password strength: Moderate")
                else:
                    st.success("Password strength: Strong")

            if st.button(
                "Create account →",
                key="register_button",
                type="primary",
                use_container_width=True,
            ):
                if not all(
                    [
                        full_name.strip(),
                        email.strip(),
                        username.strip(),
                        new_password,
                        confirm_password,
                    ]
                ):
                    st.warning("Please complete all fields.")

                elif new_password != confirm_password:
                    st.error("The passwords do not match.")

                elif len(new_password) < 8:
                    st.error(
                        "Your password must contain at least 8 characters."
                    )

                else:
                    success, message = auth.register(
                        username,
                        email,
                        full_name,
                        new_password,
                    )

                    if success:
                        st.success(message)
                        st.info(
                            "Your account has been created. "
                            "Switch to Sign in to continue."
                        )
                    else:
                        st.error(message)

        st.caption(
            "StaffMetrics · Employee Salary & Performance Analysis"
        )


# ============================================================
# DASHBOARD
# ============================================================

def page_dashboard(df):
    user = st.session_state.user

    banner(
        "Executive Dashboard",
        f"Welcome, {user.get('full_name') or user['username']}",
    )

    if df is None or df.empty:
        st.warning("No employee records are available.")
        return

    st.subheader("Dashboard Filters")

    # Department and designation dropdowns
    c1, c2, c3 = st.columns(3)

    departments = sorted(
        df["Department"].dropna().astype(str).unique().tolist()
    )

    designations = sorted(
        df["Designation"].dropna().astype(str).unique().tolist()
    )

    with c1:
        selected_department = st.selectbox(
            "Department",
            ["All departments"] + departments,
            key="dashboard_department_dropdown",
        )

    with c2:
        selected_designation = st.selectbox(
            "Designation",
            ["All designations"] + designations,
            key="dashboard_designation_dropdown",
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

    # Salary range
    salary_min = float(df["Basic_Salary"].min())
    salary_max = float(df["Basic_Salary"].max())

    if salary_min == salary_max:
        selected_salary = (salary_min, salary_max)
        st.caption(f"Salary: {salary_min:,.0f}")
    else:
        selected_salary = st.slider(
            "Basic salary range",
            min_value=salary_min,
            max_value=salary_max,
            value=(salary_min, salary_max),
            key="dashboard_salary",
        )

    # Experience range
    experience_min = int(df["Experience_Years"].min())
    experience_max = int(df["Experience_Years"].max())

    if experience_min == experience_max:
        selected_experience = (
            experience_min,
            experience_max,
        )
        st.caption(
            f"Experience range: {experience_min} years"
        )
    else:
        selected_experience = st.slider(
            "Experience range (years)",
            min_value=experience_min,
            max_value=experience_max,
            value=(experience_min, experience_max),
            key="dashboard_experience",
        )

    # Performance range
    performance_min = float(df["Performance_Score"].min())
    performance_max = float(df["Performance_Score"].max())

    if performance_min == performance_max:
        selected_performance = (
            performance_min,
            performance_max,
        )
        st.caption(
            f"Performance score: {performance_min}"
        )
    else:
        selected_performance = st.slider(
            "Performance score range",
            min_value=performance_min,
            max_value=performance_max,
            value=(performance_min, performance_max),
            key="dashboard_performance",
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
        filtered_df["Basic_Salary"].between(*selected_salary)
        & filtered_df["Experience_Years"].between(
            *selected_experience
        )
        & filtered_df["Performance_Score"].between(
            *selected_performance
        )
    ]

    if filtered_df.empty:
        st.warning(
            "No employees match the selected filters. "
            "Try changing the department, designation, "
            "or range values."
        )
        return

    st.caption(
        f"Showing {len(filtered_df):,} of {len(df):,} employees."
    )

    # KPI cards
    metrics = an.kpis(filtered_df)

    interactive_kpi_cards(
        [
            (
                "Employees",
                f"{metrics['total_employees']:,}",
            ),
            (
                "Average salary",
                f"{metrics['average_salary']:,.2f}",
            ),
            (
                "Median salary",
                f"{metrics['median_salary']:,.2f}",
            ),
            (
                "Minimum salary",
                f"{metrics['minimum_salary']:,.2f}",
            ),
        ],
        section_key="dashboard_kpi_top",
    )

    st.write("")

    interactive_kpi_cards(
        [
            (
                "Maximum salary",
                f"{metrics['maximum_salary']:,.2f}",
            ),
            (
                "Average performance",
                f"{metrics['average_performance']:.2f}",
            ),
            (
                "Maximum performance",
                f"{metrics['maximum_performance']:.2f}",
            ),
        ],
        section_key="dashboard_kpi_bottom",
    )

    if st.session_state.get("_metric_dialog"):
        metric_information_dialog()

    # Insights
    st.subheader("Automated Insights")

    for insight in an.insights(filtered_df):
        st.info(insight)

    # Charts
    st.subheader("Visual Analytics")

    chart_functions = {
        "Department-wise salary": an.fig_dept_salary,
        "Salary distribution": an.fig_salary_dist,
        "Department-wise performance": an.fig_dept_perf,
        "Salary vs. performance": an.fig_salary_vs_perf,
    }

    if chart_choice == "All charts":
        left, right = st.columns(2)

        with left:
            show(an.fig_dept_salary(filtered_df))
            show(an.fig_salary_dist(filtered_df))

        with right:
            show(an.fig_dept_perf(filtered_df))
            show(an.fig_salary_vs_perf(filtered_df))

    else:
        show(chart_functions[chart_choice](filtered_df))


# ============================================================
# EMPLOYEE MANAGEMENT
# ============================================================

def manage_employees(df):
    user_id = st.session_state.user["id"]

    departments = sorted(
        df["Department"].dropna().astype(str).unique().tolist()
    )

    with st.expander("➕ Add an employee"):
        with st.form("add_employee_form"):
            c1, c2, c3 = st.columns(3)

            employee = {
                "Employee_ID": c1.text_input("Employee ID"),
                "Name": c2.text_input("Name"),
                "Age": c3.number_input(
                    "Age",
                    min_value=18,
                    max_value=70,
                    value=30,
                ),
                "Gender": c1.selectbox(
                    "Gender",
                    ["Female", "Male"],
                ),
                "Department": c2.selectbox(
                    "Department",
                    departments,
                ),
                "Designation": c3.text_input("Designation"),
                "Experience_Years": c1.number_input(
                    "Experience (years)",
                    min_value=0,
                    max_value=45,
                    value=3,
                ),
                "Joining_Year": c2.number_input(
                    "Joining year",
                    min_value=1990,
                    max_value=2030,
                    value=2024,
                ),
                "Basic_Salary": c3.number_input(
                    "Basic salary",
                    min_value=1.0,
                    max_value=10000000.0,
                    value=50000.0,
                ),
                "Bonus": c1.number_input(
                    "Bonus",
                    min_value=0.0,
                    max_value=1000000.0,
                    value=0.0,
                ),
                "Performance_Score": c2.number_input(
                    "Performance score",
                    min_value=0.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.5,
                ),
            }

            submitted = st.form_submit_button(
                "Add employee",
                use_container_width=True,
            )

            if submitted:
                try:
                    db.add_employee(employee)

                    db.log_activity(
                        user_id,
                        f"added employee {employee['Employee_ID']}",
                    )

                    st.success("Employee added successfully.")
                    st.rerun()

                except Exception as ex:
                    st.error(
                        f"Unable to add employee: {ex}"
                    )

    with st.expander("🗑️ Delete an employee"):
        employee_ids = df["Employee_ID"].tolist()

        if employee_ids:
            selected_id = st.selectbox(
                "Select employee ID",
                employee_ids,
                key="delete_employee_id",
            )

            if st.button(
                "Delete employee",
                type="secondary",
            ):
                try:
                    db.delete_employee(selected_id)

                    db.log_activity(
                        user_id,
                        f"deleted employee {selected_id}",
                    )

                    st.success("Employee deleted.")
                    st.rerun()

                except Exception as ex:
                    st.error(
                        f"Unable to delete employee: {ex}"
                    )


# ============================================================
# EMPLOYEES PAGE
# ============================================================

def page_employees(df, is_db):
    banner(
        "Employees",
        "Search, filter and manage employee records",
    )

    if df is None or df.empty:
        st.warning("No employee records are available.")
        return

    c1, c2 = st.columns(2)

    departments = sorted(
        df["Department"].dropna().astype(str).unique().tolist()
    )

    designations = sorted(
        df["Designation"].dropna().astype(str).unique().tolist()
    )

    with c1:
        selected_department = st.selectbox(
            "Department",
            ["All departments"] + departments,
            key="employees_department",
        )

    with c2:
        selected_designation = st.selectbox(
            "Designation",
            ["All designations"] + designations,
            key="employees_designation",
        )

    exp_min = int(df["Experience_Years"].min())
    exp_max = int(df["Experience_Years"].max())

    if exp_min == exp_max:
        experience_range = (exp_min, exp_max)
        st.caption(f"Experience: {exp_min} years")
    else:
        experience_range = st.slider(
            "Experience range (years)",
            min_value=exp_min,
            max_value=exp_max,
            value=(exp_min, exp_max),
            key="employees_experience_range",
        )

    search_text = st.text_input(
        "Search by employee ID or name",
    )

    filtered = df.copy()

    if selected_department != "All departments":
        filtered = filtered[
            filtered["Department"].astype(str)
            == selected_department
        ]

    if selected_designation != "All designations":
        filtered = filtered[
            filtered["Designation"].astype(str)
            == selected_designation
        ]

    filtered = filtered[
        filtered["Experience_Years"].between(
            *experience_range
        )
    ]

    if search_text.strip():
        query = search_text.strip()

        filtered = filtered[
            filtered["Employee_ID"].astype(str).str.contains(
                query,
                case=False,
                na=False,
            )
            | filtered["Name"].astype(str).str.contains(
                query,
                case=False,
                na=False,
            )
        ]

    st.caption(f"{len(filtered):,} employee records")

    st.dataframe(
        filtered,
        hide_index=True,
        use_container_width=True,
    )

    st.download_button(
        "Download filtered employees (CSV)",
        data=filtered.to_csv(index=False),
        file_name="employees_filtered.csv",
        mime="text/csv",
    )

    if is_db and st.session_state.user.get("role") == "admin":
        manage_employees(df)


# ============================================================
# ANALYSIS PAGE
# ============================================================

def page_analysis(df):
    banner(
        "Salary and Performance Analysis",
        "Compare summary statistics, experience trends and correlations",
    )

    if df is None or df.empty:
        st.warning("No employee records are available.")
        return

    salary_tab, performance_tab, correlation_tab = st.tabs(
        [
            "💰 Salary",
            "⭐ Performance",
            "📊 Correlation",
        ]
    )

    # --------------------------------------------------------
    # SALARY ANALYSIS
    # --------------------------------------------------------
    with salary_tab:
        st.subheader("Salary Summary")

        salary_summary = an.salary_summary(df)

        # Display a clear column called Salary.
        salary_table = (
            salary_summary
            .rename_axis("Metric")
            .rename("Salary")
            .reset_index()
        )

        salary_table["Salary"] = salary_table["Salary"].round(2)

        st.dataframe(
            salary_table,
            hide_index=True,
            use_container_width=True,
        )

        show(an.fig_salary_dist(df))

        st.subheader("Salary by Experience")

        experience_table = an.by_experience(df)

        st.dataframe(
            experience_table,
            hide_index=True,
            use_container_width=True,
        )

        show(an.fig_experience(df))

    # --------------------------------------------------------
    # PERFORMANCE ANALYSIS
    # --------------------------------------------------------
    with performance_tab:
        st.subheader("Performance Summary")

        performance_summary = an.performance_summary(df)

        # Display a clear column called Performance.
        performance_table = (
            performance_summary
            .rename_axis("Metric")
            .rename("Performance")
            .reset_index()
        )

        performance_table["Performance"] = (
            performance_table["Performance"].round(2)
        )

        st.dataframe(
            performance_table,
            hide_index=True,
            use_container_width=True,
        )

        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))

    # --------------------------------------------------------
    # CORRELATION ANALYSIS
    # --------------------------------------------------------
    with correlation_tab:
        st.subheader("Correlation Matrix")

        correlation_table = an.correlation(df)

        st.dataframe(
            correlation_table.round(2),
            use_container_width=True,
        )

        show(an.fig_corr(df))


# ============================================================
# DEPARTMENTS PAGE
# ============================================================

def page_departments(df):
    banner(
        "Departments",
        "Employee count, salary and performance by department",
    )

    if df is None or df.empty:
        st.warning("No employee records are available.")
        return

    st.subheader("Department Summary")

    st.dataframe(
        an.dept_table(df),
        hide_index=True,
        use_container_width=True,
    )

    left, right = st.columns(2)

    with left:
        show(an.fig_dept_count(df))

    with right:
        show(an.fig_dept_salary(df))


# ============================================================
# UPLOAD AND EXPORT
# ============================================================

def page_data(df):
    banner(
        "Upload and Export",
        "Analyse a CSV dataset and download reports",
    )

    uploaded_file = st.file_uploader(
        "Upload a CSV with the required employee columns",
        type=["csv"],
        key="employee_csv_upload",
    )

    if uploaded_file and st.button(
        "Analyse uploaded file",
        type="primary",
    ):
        try:
            uploaded_df, log = an.prepare(
                an.load_data(uploaded_file)
            )

            st.session_state["upload"] = uploaded_df

            st.success(
                "File processed successfully. "
                "Choose Uploaded file in the sidebar."
            )

            if log:
                st.write(log)

            st.rerun()

        except Exception as ex:
            st.error(f"Unable to process CSV: {ex}")

    st.subheader("Export")

    if df is None or df.empty:
        st.warning("No data is available to export.")
        return

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1:
        st.download_button(
            "Download cleaned data",
            data=df.to_csv(index=False),
            file_name="Employee_Salary_Performance_Cleaned.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with c2:
        st.download_button(
            "Download KPI summary",
            data=pd.Series(
                an.kpis(df)
            ).rename("Value").to_csv(),
            file_name="kpi_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with c3:
        st.download_button(
            "Download correlation matrix",
            data=an.correlation(df).round(3).to_csv(),
            file_name="correlation_matrix.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with c4:
        st.download_button(
            "Download HTML report",
            data=an.report_html(
                df,
                st.session_state.user["username"],
            ),
            file_name="employee_report.html",
            mime="text/html",
            use_container_width=True,
        )


# ============================================================
# ADMINISTRATION
# ============================================================

def page_admin():
    banner(
        "Administration",
        "Registered users and recent activity",
    )

    st.subheader("Registered Users")

    users = db.list_users()

    st.dataframe(
        pd.DataFrame(users),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Recent Activity")

    activities = db.recent_activity()

    st.dataframe(
        pd.DataFrame(activities),
        hide_index=True,
        use_container_width=True,
    )


# ============================================================
# MAIN APPLICATION AND SIDEBAR
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

    if user.get("role") == "admin":
        pages.append("Administration")

    # Apply requested navigation before creating the widget.
    pending_page = st.session_state.pop(
        "_pending_page_navigation",
        None,
    )

    if pending_page in pages:
        st.session_state["page_navigation"] = pending_page

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------
    current_theme = st.session_state.get(
    "theme_choice",
    "☀️ Light"
     )

    with st.sidebar:
        theme_choice = st.radio(
            "Appearance",
            ["☀️ Light", "🌙 Dark"],
            index=(
                1 if current_theme == "🌙 Dark" else 0
            ),
            key="theme_choice",
    )

    if theme_choice != APP_THEME:
        st.rerun()
    with st.sidebar:
        st.markdown("## 📊 StaffMetrics")
        st.caption("Employee Salary & Performance")
        st.divider()

        st.markdown(
            f"### {user.get('full_name') or user['username']}"
        )

        st.caption(
            f"{user.get('role', 'user').title()} account"
        )

        st.divider()

        # Theme switcher
        selected_theme = st.selectbox(
            "🎨 Website Theme",
            ["Light", "Dark"],
            index=(
                0
                if st.session_state.get("theme_choice", "Light") == "Light"
                else 1
            ),
            key="theme_selector",
        )

        if selected_theme != st.session_state.get("theme_choice"):
            st.session_state["theme_choice"] = selected_theme
            st.rerun()

        st.caption(
            f"Current theme: {selected_theme}"
        )

        st.divider()

        page = st.selectbox(
            "Navigate to page",
            pages,
            key="page_navigation",
        )

        st.divider()

        uploaded_df = st.session_state.get("upload")

        data_sources = ["Employee database"]

        if uploaded_df is not None:
            data_sources.append("Uploaded file")

        source = st.selectbox(
            "Data source",
            data_sources,
            key="data_source",
        )

        st.divider()

        if st.button(
            "🚪 Sign out",
            use_container_width=True,
        ):
            try:
                db.log_activity(
                    user["id"],
                    "signed out",
                )
            except Exception:
                pass

            clear_login_cookie()
            st.session_state.pop("user", None)
            st.rerun()

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------
    is_db = source == "Employee database"

    try:
        if is_db:
            df = db.employee_frame()
        else:
            df = st.session_state.get("upload")

        if df is None:
            st.error("No employee data is available.")
            return

        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)

    except Exception as ex:
        st.error("Unable to load employee data.")
        st.exception(ex)
        return

    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------
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
        if user.get("role") == "admin":
            page_admin()
        else:
            st.error(
                "You do not have permission to access this page."
            )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if "user" not in st.session_state:
    saved_user = restore_login_cookie()

    if saved_user is not None:
        st.session_state["user"] = saved_user

if "user" in st.session_state:
    main()
else:
    auth_page()
