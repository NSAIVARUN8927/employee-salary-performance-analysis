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


# ==================== GLOBAL STYLING ====================

THEME = st.session_state.get("theme_choice", "Light")
IS_DARK = THEME == "Dark"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    padding-top: 1.7rem;
    max-width: 1350px;
    padding-bottom: 3rem;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Manrope', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.035em;
}

h1 {
    font-size: 2.15rem !important;
}

h2 {
    font-size: 1.65rem !important;
}

h3 {
    font-size: 1.25rem !important;
}

/* Dashboard banner */

.banner {
    padding: 25px 29px;
    border-radius: 17px;
    margin-bottom: 22px;
    box-shadow: 0 9px 28px rgba(15, 23, 42, 0.10);
    border: 1px solid transparent;
}

.banner h1 {
    color: #ffffff !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 2rem !important;
    margin: 0;
}

.banner p {
    margin: 7px 0 0;
    line-height: 1.7;
}

/* KPI cards */

.kpi {
    border-radius: 15px;
    padding: 19px;
    border: 1px solid transparent;
    border-top: 4px solid #14b8a6;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
}

.kpi span {
    display: block;
    font-size: 0.86rem;
    font-weight: 600;
    margin-bottom: 8px;
}

.kpi b {
    display: block;
    font-family: 'Manrope', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
}

/* Buttons */

[data-testid="stButton"] > button,
[data-testid="stDownloadButton"] > button {
    border-radius: 10px;
    min-height: 42px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        background 0.18s ease;
}

[data-testid="stButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    border-radius: 9px;
}

[data-testid="stTabs"] button {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
}

/* Dialog animation */

[data-testid="stDialog"] [role="dialog"] {
    animation: metricDialogEntrance 0.22s ease-out;
    border-radius: 16px;
}

@keyframes metricDialogEntrance {
    from {
        opacity: 0;
        transform: translateY(10px) scale(0.985);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* Login and registration */

.login-brand {
    background: linear-gradient(145deg, #14213d, #155e75);
    color: #ffffff;
    padding: 42px 30px;
    border-radius: 20px 0 0 20px;
    min-height: 450px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 12px 35px rgba(20, 33, 61, 0.14);
}

.login-brand h1 {
    color: #ffffff !important;
    font-size: 2.5rem !important;
}

.login-brand p {
    color: #dbeafe !important;
    font-size: 1rem;
    line-height: 1.8;
}

.login-brand .brand-icon {
    font-size: 3.5rem;
    margin-bottom: 15px;
}

.login-card {
    padding: 25px 28px;
    border: 1px solid transparent;
    border-radius: 0 20px 20px 0;
    min-height: 450px;
    box-shadow: 0 12px 35px rgba(20, 33, 61, 0.08);
}

.login-heading {
    font-family: 'Manrope', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 5px;
}

.login-description {
    margin-bottom: 20px;
}

.security-note {
    font-size: 0.8rem;
    text-align: center;
    margin-top: 20px;
}

/* Responsive layout */

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
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

    h1 {
        font-size: 1.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ==================== DARK THEME ====================

if IS_DARK:

    st.markdown("""
    <style>
    :root {
        color-scheme: dark;
    }

    .stApp,
    [data-testid="stAppViewContainer"] {
        background: #0b1020 !important;
        color: #e8eefc !important;
    }

    [data-testid="stHeader"] {
        background: #0b1020 !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #111a31,
            #172640
        ) !important;
        border-right: 1px solid #263b5a;
    }

    [data-testid="stSidebar"] * {
        color: #e8eefc !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }

    p, li,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"] {
        color: #d3def2 !important;
    }

    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: #c8d6f0 !important;
        font-weight: 700 !important;
    }

    /* Dark inputs */

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        background: #17243b !important;
        border: 1px solid #425675 !important;
    }

    /* Dropdowns */

    [data-baseweb="select"] > div {
        background: #17243b !important;
        border-color: #425675 !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="select"] span {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #17243b !important;
        color: #f8fafc !important;
        border: 1px solid #425675 !important;
    }

    [role="option"] {
        color: #f8fafc !important;
    }

    [role="option"]:hover {
        background: #263b5a !important;
    }

    /* Tables, expanders and dialogs */

    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    [data-testid="stExpander"],
    [data-testid="stDialog"] [role="dialog"] {
        background: #121d32 !important;
        color: #e8eefc !important;
        border-color: #344866 !important;
    }

    [data-testid="stMetricLabel"] p {
        color: #b9c9e4 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    /* Dark buttons */

    [data-testid="stButton"] button,
    [data-testid="stDownloadButton"] button {
        color: #f8fafc !important;
        background: #203451 !important;
        border: 1px solid #496181 !important;
    }

    [data-testid="stButton"] button p,
    [data-testid="stButton"] button span {
        color: #f8fafc !important;
    }

    [data-testid="stButton"] button:hover,
    [data-testid="stDownloadButton"] button:hover {
        background: #28506c !important;
        border-color: #5eead4 !important;
    }

    /* Dark dashboard components */

    .banner {
        background: linear-gradient(
            120deg,
            #172554,
            #164e63
        ) !important;
        border-color: #2c5573;
    }

    .banner h1 {
        color: #ffffff !important;
    }

    .banner p {
        color: #d6e9ff !important;
    }

    .kpi {
        background: linear-gradient(
            145deg,
            #17243b,
            #1c2c46
        ) !important;
        border-color: #344866 !important;
        border-top-color: #2dd4bf !important;
    }

    .kpi span {
        color: #bdcce4 !important;
    }

    .kpi b {
        color: #f8fafc !important;
    }

    .login-card {
        background: #121d32 !important;
        border-color: #344866 !important;
    }

    .login-heading {
        color: #f8fafc !important;
    }

    .login-description,
    .security-note {
        color: #bdcce4 !important;
    }

    hr {
        border-color: #344866 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== LIGHT THEME ====================

else:

    st.markdown("""
    <style>
    :root {
        color-scheme: light;
    }

    .stApp,
    [data-testid="stAppViewContainer"] {
        background: #f5f7fc !important;
        color: #172033 !important;
    }

    [data-testid="stHeader"] {
        background: #f5f7fc !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #ffffff,
            #edf3fb
        ) !important;
        border-right: 1px solid #d9e2f0;
    }

    [data-testid="stSidebar"] * {
        color: #1e2a43 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #14213d !important;
    }

    p, li,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"] {
        color: #334155 !important;
    }

    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: #24334d !important;
        font-weight: 700 !important;
    }

    /* Light inputs */

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        background: #ffffff !important;
        border: 1px solid #c5d0e0 !important;
    }

    /* Dropdowns */

    [data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #c5d0e0 !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="select"] span {
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #ffffff !important;
        color: #172033 !important;
        border: 1px solid #d4deeb !important;
    }

    [role="option"] {
        color: #172033 !important;
    }

    [role="option"]:hover {
        background: #e6f4f8 !important;
    }

    /* Tables, expanders and dialogs */

    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    [data-testid="stExpander"],
    [data-testid="stDialog"] [role="dialog"] {
        background: #ffffff !important;
        color: #172033 !important;
        border-color: #d9e2f0 !important;
    }

    [data-testid="stMetricLabel"] p {
        color: #53647d !important;
    }

    [data-testid="stMetricValue"] {
        color: #14213d !important;
    }

    /* Light buttons */

    [data-testid="stButton"] button,
    [data-testid="stDownloadButton"] button {
        color: #14213d !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 700 !important;
    }

    [data-testid="stButton"] button:hover,
    [data-testid="stDownloadButton"] button:hover {
        color: #075985 !important;
        background: #e8f7f7 !important;
        border-color: #0f766e !important;
    }

    /* Light dashboard components */

    .banner {
        background: linear-gradient(
            120deg,
            #14213d,
            #155e75
        ) !important;
    }

    .banner h1 {
        color: #ffffff !important;
    }

    .banner p {
        color: #dbeafe !important;
    }

    .kpi {
        background: linear-gradient(
            145deg,
            #ffffff,
            #f1f7fc
        ) !important;
        border-color: #d9e2f0 !important;
        border-top-color: #0f766e !important;
    }

    .kpi span {
        color: #53647d !important;
    }

    .kpi b {
        color: #14213d !important;
    }

    .login-card {
        background: #ffffff !important;
        border-color: #d9e2f0 !important;
    }

    .login-heading {
        color: #14213d !important;
    }

    .login-description,
    .security-note {
        color: #64748b !important;
    }

    hr {
        border-color: #d9e2f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


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
    """
    Save the destination before the sidebar navigation widget
    is created. This avoids Streamlit widget-state conflicts.
    """

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

    st.caption(
        f"Recommended module: {details['module']}"
    )

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

    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(59, 130, 246, 0.15),
                transparent 35%
            ),
            linear-gradient(135deg, #f8fafc, #eaf0fb);
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

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
                type=(
                    "default"
                    if show_login_password
                    else "password"
                ),
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

                    user = auth.login(
                        login_id,
                        login_password
                    )

                    if user:

                        st.session_state.user = user
                        st.rerun()

                    else:

                        st.error(
                            "The username/email or password "
                            "is incorrect."
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

            if st.button(
                "Create account",
                key="register_button"
            ):

                if not all([
                    full_name.strip(),
                    email.strip(),
                    username.strip(),
                    password,
                    confirm_password
                ]):

                    st.warning(
                        "Please complete all the fields."
                    )

                elif password != confirm_password:

                    st.error(
                        "The passwords do not match."
                    )

                elif len(password) < 8:

                    st.error(
                        "Your password must contain "
                        "at least 8 characters."
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

    # Department and designation dropdowns

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

    # ==================== SALARY RANGE ====================

    salary_values = pd.to_numeric(
        df["Basic_Salary"],
        errors="coerce"
    ).dropna()

    if salary_values.empty:
        st.warning(
            "Salary information is unavailable in this dataset."
        )
        return

    salary_min = float(salary_values.min())
    salary_max = float(salary_values.max())

    if salary_min == salary_max:

        selected_salary = (
            salary_min,
            salary_max
        )

        st.caption(
            f"Available salary: {salary_min:,.0f}"
        )

    else:

        selected_salary = st.slider(
            "Basic salary range",
            min_value=salary_min,
            max_value=salary_max,
            value=(salary_min, salary_max),
            key="dashboard_salary"
        )

    # ==================== EXPERIENCE RANGE ====================

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

    # ==================== PERFORMANCE RANGE ====================

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

        selected_performance = (
            perf_min,
            perf_max
        )

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

    # ==================== APPLY FILTERS ====================

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
        f"Showing {len(filtered_df):,} of "
        f"{len(df):,} employee records."
    )

    # ==================== KPI CARDS ====================

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

            show(
                an.fig_dept_salary(filtered_df)
            )

            show(
                an.fig_salary_dist(filtered_df)
            )

        with b:

            show(
                an.fig_dept_perf(filtered_df)
            )

            show(
                an.fig_salary_vs_perf(filtered_df)
            )

    else:

        show(
            chart_functions[chart_choice](filtered_df)
        )

    # ==================== FILTERED RECORDS ====================

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
            "Employee_ID": c[0].text_input(
                "Employee ID"
            ),

            "Name": c[1].text_input(
                "Name"
            ),

            "Age": c[2].number_input(
                "Age", 18, 70, 30
            ),

            "Gender": c[0].selectbox(
                "Gender",
                ["Female", "Male"]
            ),

            "Department": c[1].selectbox(
                "Department",
                sorted(df["Department"].unique())
            ),

            "Designation": c[2].text_input(
                "Designation"
            ),

            "Experience_Years": c[0].number_input(
                "Experience (years)",
                0, 45, 3
            ),

            "Joining_Year": c[1].number_input(
                "Joining year",
                1990, 2030, 2024
            ),

            "Basic_Salary": c[2].number_input(
                "Basic salary",
                1.0, 1e7, 50000.0
            ),

            "Bonus": c[0].number_input(
                "Bonus",
                0.0, 1e6, 0.0
            ),

            "Performance_Score": c[1].number_input(
                "Performance score (0-5)",
                0.0, 5.0, 3.0, 0.5
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

                st.error(
                    f"The employee could not be added: {ex}"
                )

    with st.expander("Delete an employee"):

        who = st.selectbox(
            "Employee",
            df["Employee_ID"]
        )

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

    c1, c2, c3 = st.columns(3)

    dept = c1.multiselect(
        "Department",
        sorted(df["Department"].unique())
    )

    role = c2.multiselect(
        "Designation",
        sorted(df["Designation"].astype(str).unique())
    )

    lo = int(df["Experience_Years"].min())
    hi = int(df["Experience_Years"].max())

    exp = c3.slider(
        "Experience (years)",
        lo,
        max(hi, lo + 1),
        (lo, max(hi, lo + 1))
    )

    q = st.text_input(
        "Search by ID or name"
    )

    f = df[
        df["Experience_Years"].between(*exp)
    ]

    if dept:

        f = f[
            f["Department"].isin(dept)
        ]

    if role:

        f = f[
            f["Designation"].astype(str).isin(role)
        ]

    if q:

        f = f[
            f["Employee_ID"].astype(str).str.contains(
                q, case=False
            )
            |
            f["Name"].astype(str).str.contains(
                q, case=False
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

    if (
        is_db
        and st.session_state.user["role"] == "admin"
    ):
        manage_employees(df)


# ==================== ANALYSIS PAGE ====================

def page_analysis(df):

    banner(
        "Salary and performance analysis",
        "Statistics, experience trends and correlations"
    )

    t1, t2, t3 = st.tabs(
        ["Salary", "Performance", "Correlation"]
    )

    with t1:

        st.subheader("Salary Summary")

        salary_summary = an.salary_summary(df).round(2)

        def summary_value(summary, word, fallback_index):

            for label, value in summary.items():

                if word in str(label).lower():
                    return value

            return summary.iloc[fallback_index]

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

        show(
            an.fig_salary_dist(df)
        )

        st.subheader("By experience")

        st.dataframe(
            an.by_experience(df),
            hide_index=True,
            use_container_width=True
        )

        show(
            an.fig_experience(df)
        )

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

        show(
            an.fig_perf_dist(df)
        )

        show(
            an.fig_dept_perf(df)
        )

    with t3:

        st.dataframe(
            an.correlation(df).round(2),
            use_container_width=True
        )

        show(
            an.fig_corr(df)
        )


# ==================== DEPARTMENTS PAGE ====================

def page_departments(df):

    banner(
        "Departments",
        "Employee count, salary and performance by department"
    )

    st.dataframe(
        an.dept_table(df),
        hide_index=True,
        use_container_width=True
    )

    a, b = st.columns(2)

    with a:

        show(
            an.fig_dept_count(df)
        )

    with b:

        show(
            an.fig_dept_salary(df)
        )


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
        pd.Series(
            an.kpis(df)
        ).rename("value").to_csv(),
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

    # Apply navigation before creating the selectbox.

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

        st.caption(
            f"{user['role'].title()} account"
        )

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

    # Display selected page.

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
