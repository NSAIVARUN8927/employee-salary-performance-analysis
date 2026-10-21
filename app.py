import re
import html

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import analytics as an, auth, database as db


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StaffMetrics | Employee Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

db.init_db()

CSV = "data/employee_salary_performance.csv"

if not db.is_seeded():
    db.seed_database(an.prepare(an.load_data(CSV))[0])


# ============================================================
# PROFESSIONAL UI STYLING
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --primary: #4f46e5;
        --primary-dark: #3730a3;
        --sidebar: #111827;
        --sidebar-card: #202c43;
        --background: #f4f6fc;
        --surface: #ffffff;
        --text: #172033;
        --muted: #64748b;
        --border: #e2e8f0;
        --success: #0f766e;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--background);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    /* Main headings */

    h1, h2 {
        font-family: 'Manrope', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.6px;
        color: var(--text);
    }

    h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: #263449;
    }

    p, label, input, textarea {
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #111827 0%,
            #172554 55%,
            #312e81 100%
        );
        border-right: 1px solid #283753;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    [data-testid="stSidebar"] * {
        color: #e5edf8;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #ffffff !important;
        font-family: 'Manrope', sans-serif !important;
    }

    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #cbd5e1 !important;
        font-weight: 600;
    }

    /* Sidebar dropdown box */

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #293957 !important;
        border: 1px solid #52658a !important;
        border-radius: 11px !important;
        min-height: 43px;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
        background: #364b70 !important;
        border-color: #818cf8 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] input {
        color: white !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] span {
        color: #f8fafc !important;
    }

    /* Dropdown popup */

    [data-baseweb="popover"] {
        border-radius: 12px !important;
        overflow: hidden;
    }

    [role="listbox"] {
        background: #1e293b !important;
        border: 1px solid #475569 !important;
    }

    [role="option"] {
        color: #f8fafc !important;
        background: #1e293b !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    [role="option"]:hover {
        background: #3730a3 !important;
    }

    [role="option"][aria-selected="true"] {
        background: #4338ca !important;
    }

    /* Sidebar buttons */

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        background: #293957 !important;
        color: #ffffff !important;
        border: 1px solid #52658a !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 700 !important;
        min-height: 42px;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background: #4338ca !important;
        border-color: #818cf8 !important;
    }

    /* Brand */

    .brand-box {
        padding: 19px 16px;
        border-radius: 16px;
        margin-bottom: 22px;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 10px 30px rgba(0,0,0,0.22);
    }

    .brand-title {
        font-family: 'Manrope', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: white;
        letter-spacing: -0.5px;
    }

    .brand-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.76rem;
        color: #e0e7ff;
        margin-top: 5px;
        line-height: 1.5;
    }

    .sidebar-section {
        color: #a5b4fc;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 0.72rem;
        letter-spacing: 1.5px;
        margin: 12px 0 8px;
    }

    .sidebar-user {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.10);
        padding: 13px;
        border-radius: 12px;
        margin: 12px 0 18px;
    }

    .sidebar-user-name {
        font-family: 'Manrope', sans-serif;
        font-size: 0.96rem;
        font-weight: 800;
        color: white;
        overflow-wrap: anywhere;
    }

    .sidebar-user-role {
        color: #c7d2fe;
        font-size: 0.76rem;
        margin-top: 4px;
    }

    /* Page banner */

    .page-banner {
        background: linear-gradient(120deg, #111827, #263b67, #3730a3);
        padding: 29px 31px;
        border-radius: 18px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(30,41,59,0.12);
        border: 1px solid rgba(255,255,255,0.12);
    }

    .page-banner h1 {
        color: white !important;
        font-size: 1.95rem;
        margin: 0;
        line-height: 1.3;
    }

    .page-banner p {
        color: #dbeafe;
        margin: 8px 0 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .section-label {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.18rem;
        color: #172033;
        margin: 20px 0 12px;
        letter-spacing: -0.3px;
    }

    /* KPI cards are actual Streamlit buttons.
       Clicking anywhere on the card triggers its action. */

    [class*="st-key-kpi_"] [data-testid="stButton"] button {
        width: 100%;
        min-height: 145px;
        height: 145px;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        text-align: left;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        padding: 17px 18px;
        border-radius: 16px;
        border: 1px solid #e0e7ff;
        border-top: 4px solid #6366f1;
        background: linear-gradient(145deg, #ffffff, #f8faff);
        color: #172033 !important;
        box-shadow: 0 5px 16px rgba(30,41,59,0.055);
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.91rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    [class*="st-key-kpi_"] [data-testid="stButton"] button p {
        white-space: pre-wrap !important;
        text-align: left !important;
        line-height: 1.65 !important;
        color: #172033 !important;
    }

    [class*="st-key-kpi_"] [data-testid="stButton"] button:hover {
        background: linear-gradient(145deg, #eef2ff, #e0e7ff);
        border-color: #818cf8;
        border-top-color: #4338ca;
        transform: translateY(-3px);
        box-shadow: 0 12px 24px rgba(79,70,229,0.14);
    }

    [class*="st-key-kpi_"] [data-testid="stButton"] button:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
    }

    .info-card {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 14px;
        margin-bottom: 12px;
    }

    /* General buttons */

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        border-radius: 10px;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 700;
        transition: all 0.18s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #818cf8;
    }

    /* Form controls */

    [data-baseweb="select"] > div {
        border-radius: 10px;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        border-radius: 10px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stTabs"] button {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700;
    }

    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background: rgba(255,255,255,0.65);
    }

    .footer-text {
        text-align: center;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.78rem;
        color: #94a3b8;
        padding-top: 25px;
    }

    /* Login screen */

    .login-brand {
        background: linear-gradient(145deg, #111827, #3730a3);
        color: white;
        padding: 40px 30px;
        border-radius: 18px;
        min-height: 400px;
    }

    .login-brand h1 {
        color: white !important;
        font-size: 2.2rem;
    }

    .login-brand p {
        color: #dbeafe;
        line-height: 1.8;
    }

    .login-card {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 25px;
        border-radius: 18px;
    }

    .login-heading {
        font-family: 'Manrope', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #172033;
    }

    .login-description {
        color: #64748b;
        margin-bottom: 20px;
    }

    @media (max-width: 800px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .page-banner {
            padding: 21px;
        }

        .page-banner h1 {
            font-size: 1.55rem;
        }

        [class*="st-key-kpi_"] [data-testid="stButton"] button {
            min-height: 125px;
            height: 125px;
            padding: 12px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SHARED FUNCTIONS
# ============================================================

def banner(title, subtitle=""):
    st.markdown(
        f"""
        <div class="page-banner">
            <h1>{html.escape(str(title))}</h1>
            <p>{html.escape(str(subtitle))}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_title(title):
    st.markdown(
        f'<div class="section-label">{html.escape(str(title))}</div>',
        unsafe_allow_html=True
    )


def show(fig):
    if fig is not None:
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)


def navigate_to(page):
    st.session_state["page_navigation"] = page
    st.rerun()


def get_number(df, column, default=0):
    if column not in df.columns or df.empty:
        return default

    values = pd.to_numeric(df[column], errors="coerce").dropna()

    if values.empty:
        return default

    return values


def show_kpi(label, value, key, hint="Click to view details"):
    """
    A single clickable KPI card.

    Unlike a static HTML card followed by a separate button,
    the entire visible card is the Streamlit button.
    """

    with st.container(key=f"kpi_{key}"):
        clicked = st.button(
            f"{label}\n\n{value}\n\n↗ {hint}",
            key=f"kpi_button_{key}",
            use_container_width=True
        )

    if clicked:
        if key == "employees":
            navigate_to("Employees")

        elif key in (
            "average_salary",
            "median_salary",
            "minimum_salary"
        ):
            st.session_state["analysis_view"] = "Salary"
            navigate_to("Analysis")

        elif key == "average_performance":
            st.session_state["analysis_view"] = "Performance"
            navigate_to("Analysis")

        elif key in (
            "maximum_salary",
            "maximum_performance"
        ):
            st.session_state["kpi_dialog"] = key
            st.rerun()


# ============================================================
# KPI EXPLANATION DIALOGS
# ============================================================

def get_kpi_details(df, key):
    if key == "maximum_salary":
        column = "Basic_Salary"
        title = "Maximum Salary"
        description = (
            "The maximum salary is the highest basic salary among "
            "employees matching your current dashboard filters."
        )
        fmt = lambda value: f"₹{value:,.2f}"

    elif key == "maximum_performance":
        column = "Performance_Score"
        title = "Maximum Performance"
        description = (
            "The maximum performance is the highest recorded "
            "performance score among the employees matching "
            "your current dashboard filters."
        )
        fmt = lambda value: f"{value:.2f}"

    else:
        return None

    if column not in df.columns or df.empty:
        return {
            "title": title,
            "description": description,
            "value": "Not available",
            "employees": pd.DataFrame()
        }

    values = pd.to_numeric(df[column], errors="coerce")
    valid = values.dropna()

    if valid.empty:
        return {
            "title": title,
            "description": description,
            "value": "Not available",
            "employees": pd.DataFrame()
        }

    maximum = valid.max()
    matching = df.loc[values == maximum].copy()

    return {
        "title": title,
        "description": description,
        "value": fmt(maximum),
        "employees": matching
    }


def show_kpi_dialog(df):
    key = st.session_state.get("kpi_dialog")

    if not key:
        return

    details = get_kpi_details(df, key)

    if details is None:
        st.session_state.pop("kpi_dialog", None)
        return

    if hasattr(st, "dialog"):

        @st.dialog(details["title"], width="large")
        def explanation_dialog():
            st.write(details["description"])

            st.metric(
                label=details["title"],
                value=details["value"]
            )

            matching = details["employees"]

            if not matching.empty:
                section_title("Matching Employee Records")

                preferred_columns = [
                    "Employee_ID",
                    "Name",
                    "Department",
                    "Designation",
                    "Basic_Salary",
                    "Performance_Score"
                ]

                available_columns = [
                    col for col in preferred_columns
                    if col in matching.columns
                ]

                st.dataframe(
                    matching[available_columns],
                    hide_index=True,
                    use_container_width=True
                )

            st.caption(
                "This value is calculated using the current "
                "dashboard filters."
            )

            left, right = st.columns(2)

            with left:
                if st.button(
                    "Open Analysis",
                    key="dialog_analysis",
                    use_container_width=True
                ):
                    st.session_state.pop("kpi_dialog", None)

                    st.session_state["analysis_view"] = (
                        "Salary"
                        if key == "maximum_salary"
                        else "Performance"
                    )

                    navigate_to("Analysis")

            with right:
                if st.button(
                    "Close",
                    key="dialog_close",
                    use_container_width=True
                ):
                    st.session_state.pop("kpi_dialog", None)
                    st.rerun()

        explanation_dialog()

    else:
        # Compatibility fallback for older Streamlit versions.
        with st.expander(details["title"], expanded=True):
            st.write(details["description"])
            st.metric(details["title"], details["value"])

            if st.button("Close explanation", key="close_old_dialog"):
                st.session_state.pop("kpi_dialog", None)
                st.rerun()


# ============================================================
# AUTHENTICATION PAGE
# ============================================================

def auth_page():

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at top left,
                    rgba(99,102,241,0.13),
                    transparent 35%
                ),
                linear-gradient(135deg,#f8fafc,#eaf0fb);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 1.15], gap="large")

    with left:
        st.markdown(
            """
            <div class="login-brand">
                <div style="font-size:3rem">📊</div>
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

        with login_tab:
            st.subheader("Sign in to your account")

            login_id = st.text_input(
                "Username or email",
                key="login_username"
            )

            show_password = st.checkbox(
                "Show password",
                key="show_login_password"
            )

            password = st.text_input(
                "Password",
                type="default" if show_password else "password",
                key="login_password"
            )

            if st.button(
                "Sign in",
                key="login_button",
                use_container_width=True
            ):
                if not login_id.strip() or not password:
                    st.warning(
                        "Enter your username/email and password."
                    )

                else:
                    user = auth.login(login_id, password)

                    if user:
                        st.session_state.user = user
                        st.session_state.setdefault(
                            "page_navigation",
                            "Dashboard"
                        )
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
                "and lowercase letters, numbers, and symbols is recommended."
            )

            if st.button(
                "Create account",
                key="register_button",
                use_container_width=True
            ):

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
            <div class="footer-text">
                StaffMetrics · Employee Salary & Performance Analysis
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# DASHBOARD
# ============================================================

def page_dashboard(df):

    user = st.session_state.user

    full_name = (
        user.get("full_name")
        or user.get("username", "User")
    )

    banner(
        "Executive Dashboard",
        f"Welcome back, {full_name}. Here is your workforce overview."
    )

    if df.empty:
        st.warning("No employee records are available.")
        return

    required_columns = [
        "Department",
        "Designation",
        "Basic_Salary",
        "Experience_Years",
        "Performance_Score"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error(
            "The dataset is missing required columns: "
            + ", ".join(missing_columns)
        )
        return

    section_title("Dashboard Filters")

    departments = sorted(
        df["Department"].dropna().astype(str).unique().tolist()
    )

    designations = sorted(
        df["Designation"].dropna().astype(str).unique().tolist()
    )

    with st.expander("⚙️ Configure dashboard filters", expanded=True):

        c1, c2, c3 = st.columns(3)

        with c1:
            selected_departments = st.multiselect(
                "Department",
                departments,
                default=departments,
                key="dashboard_departments"
            )

        with c2:
            selected_designations = st.multiselect(
                "Designation",
                designations,
                default=designations,
                key="dashboard_designations"
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

        salary_values = get_number(df, "Basic_Salary")

        salary_min = float(salary_values.min())
        salary_max = float(salary_values.max())

        if salary_min == salary_max:
            selected_salary = (salary_min, salary_max)
            st.caption(f"Salary: ₹{salary_min:,.0f}")

        else:
            selected_salary = st.slider(
                "Basic salary range",
                min_value=salary_min,
                max_value=salary_max,
                value=(salary_min, salary_max),
                key="dashboard_salary"
            )

        c4, c5 = st.columns(2)

        exp_values = get_number(df, "Experience_Years")

        exp_min = int(exp_values.min())
        exp_max = int(exp_values.max())

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
                    key="dashboard_experience"
                )

        performance_values = get_number(df, "Performance_Score")

        perf_min = float(performance_values.min())
        perf_max = float(performance_values.max())

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
                    key="dashboard_performance"
                )

    filtered_df = df[
        df["Department"].astype(str).isin(selected_departments)
        & df["Designation"].astype(str).isin(selected_designations)
        & df["Basic_Salary"].between(*selected_salary)
        & df["Experience_Years"].between(*selected_experience)
        & df["Performance_Score"].between(*selected_performance)
    ].copy()

    if filtered_df.empty:
        st.warning("No employees match your selected filters.")
        return

    st.caption(
        f"Showing {len(filtered_df):,} of {len(df):,} employee records."
    )

    k = an.kpis(filtered_df)

    # Show any previously requested KPI explanation.
    show_kpi_dialog(filtered_df)

    section_title("Workforce Overview")

    # Row 1
    c1, c2, c3 = st.columns(3)

    with c1:
        show_kpi(
            "👥 Employees",
            f"{k['total_employees']:,}",
            "employees",
            "Click to open employee records"
        )

    with c2:
        show_kpi(
            "💰 Average Salary",
            f"₹{k['average_salary']:,.2f}",
            "average_salary",
            "Click to open salary analysis"
        )

    with c3:
        show_kpi(
            "📊 Median Salary",
            f"₹{k['median_salary']:,.2f}",
            "median_salary",
            "Click to open salary analysis"
        )

    # Row 2
    c1, c2, c3 = st.columns(3)

    with c1:
        show_kpi(
            "📉 Minimum Salary",
            f"₹{k['minimum_salary']:,.2f}",
            "minimum_salary",
            "Click to open salary analysis"
        )

    with c2:
        show_kpi(
            "🏆 Maximum Salary",
            f"₹{k['maximum_salary']:,.2f}",
            "maximum_salary",
            "Click for employee details"
        )

    with c3:
        show_kpi(
            "⭐ Average Performance",
            f"{k['average_performance']:.2f}",
            "average_performance",
            "Click to open performance analysis"
        )

    # Row 3
    c1, c2, c3 = st.columns(3)

    with c1:
        show_kpi(
            "🚀 Maximum Performance",
            f"{k['maximum_performance']:.2f}",
            "maximum_performance",
            "Click for employee details"
        )

    # Display any dialog triggered by a card click.
    show_kpi_dialog(filtered_df)

    section_title("Automated Insights")

    for line in an.insights(filtered_df):
        st.info(line)

    section_title("Visual Analytics")

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


# ============================================================
# EMPLOYEE MANAGEMENT
# ============================================================

def manage_employees(df):

    uid = st.session_state.user["id"]

    departments = sorted(
        df["Department"].dropna().astype(str).unique().tolist()
    )

    if not departments:
        departments = ["General"]

    with st.expander("➕ Add an employee"):

        with st.form("add_emp"):

            c1, c2, c3 = st.columns(3)

            employee_id = c1.text_input("Employee ID")
            name = c2.text_input("Name")

            age = c3.number_input(
                "Age",
                min_value=18,
                max_value=70,
                value=30
            )

            gender = c1.selectbox(
                "Gender",
                ["Female", "Male", "Other"]
            )

            department = c2.selectbox(
                "Department",
                departments
            )

            designation = c3.text_input("Designation")

            experience = c1.number_input(
                "Experience (years)",
                min_value=0,
                max_value=45,
                value=3
            )

            joining_year = c2.number_input(
                "Joining year",
                min_value=1990,
                max_value=2030,
                value=2024
            )

            salary = c3.number_input(
                "Basic salary",
                min_value=1.0,
                max_value=1e7,
                value=50000.0
            )

            bonus = c1.number_input(
                "Bonus",
                min_value=0.0,
                max_value=1e6,
                value=0.0
            )

            performance = c2.number_input(
                "Performance score",
                min_value=0.0,
                max_value=5.0,
                value=3.0,
                step=0.5
            )

            submitted = st.form_submit_button(
                "Add employee",
                use_container_width=True
            )

            if submitted:

                if not employee_id.strip() or not name.strip():
                    st.error("Employee ID and Name are required.")

                elif not designation.strip():
                    st.error("Designation is required.")

                else:
                    employee = {
                        "Employee_ID": employee_id.strip(),
                        "Name": name.strip(),
                        "Age": age,
                        "Gender": gender,
                        "Department": department,
                        "Designation": designation.strip(),
                        "Experience_Years": experience,
                        "Joining_Year": joining_year,
                        "Basic_Salary": salary,
                        "Bonus": bonus,
                        "Performance_Score": performance
                    }

                    try:
                        db.add_employee(employee)

                        db.log_activity(
                            uid,
                            f"added employee {employee_id}"
                        )

                        st.success("Employee added successfully.")
                        st.rerun()

                    except Exception as ex:
                        st.error(
                            f"The employee could not be added: {ex}"
                        )

    with st.expander("🗑️ Delete an employee"):

        if df.empty:
            st.info("No employees available.")

        else:
            employee_ids = df["Employee_ID"].astype(str).tolist()

            who = st.selectbox(
                "Select employee",
                employee_ids,
                key="delete_employee_select"
            )

            confirm = st.checkbox(
                "I confirm that I want to delete this employee.",
                key="confirm_employee_delete"
            )

            if st.button(
                "Delete employee",
                disabled=not confirm
            ):

                try:
                    db.delete_employee(who)

                    db.log_activity(
                        uid,
                        f"deleted employee {who}"
                    )

                    st.success("Employee deleted.")
                    st.rerun()

                except Exception as ex:
                    st.error(f"Could not delete employee: {ex}")


def page_employees(df, is_db):

    banner(
        "Employee Management",
        "Search, filter, review, and manage employee records."
    )

    if df.empty:
        st.warning("No employee records are available.")
        return

    section_title("Search and Filter")

    with st.expander("🔎 Employee filters", expanded=True):

        c1, c2, c3 = st.columns(3)

        departments = sorted(
            df["Department"].dropna().astype(str).unique().tolist()
        )

        designations = sorted(
            df["Designation"].dropna().astype(str).unique().tolist()
        )

        with c1:
            dept = st.multiselect(
                "Department",
                departments,
                key="employee_department_filter"
            )

        with c2:
            role = st.multiselect(
                "Designation",
                designations,
                key="employee_designation_filter"
            )

        with c3:
            search = st.text_input(
                "Search by employee ID or name",
                key="employee_search"
            )

        exp_values = get_number(df, "Experience_Years")

        lo = int(exp_values.min())
        hi = int(exp_values.max())

        if lo == hi:
            exp = (lo, hi)
            st.caption(f"Experience: {lo} years")

        else:
            exp = st.slider(
                "Experience range",
                min_value=lo,
                max_value=hi,
                value=(lo, hi),
                key="employee_experience_filter"
            )

    filtered = df[
        df["Experience_Years"].between(*exp)
    ].copy()

    if dept:
        filtered = filtered[
            filtered["Department"].astype(str).isin(dept)
        ]

    if role:
        filtered = filtered[
            filtered["Designation"].astype(str).isin(role)
        ]

    if search.strip():
        query = search.strip()

        mask = (
            filtered["Employee_ID"]
            .astype(str)
            .str.contains(query, case=False, na=False)
            |
            filtered["Name"]
            .astype(str)
            .str.contains(query, case=False, na=False)
        )

        filtered = filtered[mask]

    st.caption(f"{len(filtered):,} employees found.")

    st.dataframe(
        filtered,
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download filtered records",
        filtered.to_csv(index=False),
        "employees_filtered.csv",
        "text/csv"
    )

    if (
        is_db
        and st.session_state.user.get("role") == "admin"
    ):
        section_title("Employee Administration")
        manage_employees(df)


# ============================================================
# SALARY AND PERFORMANCE ANALYSIS
# ============================================================

def page_analysis(df):

    banner(
        "Salary & Performance Analysis",
        "Explore salary statistics, performance indicators, and correlations."
    )

    if df.empty:
        st.warning("No data is available for analysis.")
        return

    analysis_options = [
        "Salary",
        "Performance",
        "Correlation"
    ]

    requested_view = st.session_state.get(
        "analysis_view",
        "Salary"
    )

    if requested_view not in analysis_options:
        requested_view = "Salary"

    view = st.radio(
        "Choose analysis module",
        analysis_options,
        index=analysis_options.index(requested_view),
        horizontal=True,
        key="analysis_view"
    )

    if view == "Salary":

        section_title("Salary Summary")

        st.dataframe(
            an.salary_summary(df).round(2).to_frame("Value"),
            use_container_width=True
        )

        show(an.fig_salary_dist(df))

        section_title("Salary by Experience")

        st.dataframe(
            an.by_experience(df),
            hide_index=True,
            use_container_width=True
        )

        show(an.fig_experience(df))

    elif view == "Performance":

        section_title("Performance Summary")

        st.dataframe(
            an.performance_summary(df).round(2).to_frame("Value"),
            use_container_width=True
        )

        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))

    elif view == "Correlation":

        section_title("Correlation Matrix")

        st.dataframe(
            an.correlation(df).round(2),
            use_container_width=True
        )

        show(an.fig_corr(df))


# ============================================================
# DEPARTMENTS
# ============================================================

def page_departments(df):

    banner(
        "Department Analytics",
        "Compare workforce size, salary, and performance across departments."
    )

    if df.empty:
        st.warning("No department data is available.")
        return

    departments = sorted(
        df["Department"].dropna().astype(str).unique().tolist()
    )

    selected_department = st.selectbox(
        "Focus department",
        ["All departments"] + departments,
        key="department_focus"
    )

    if selected_department == "All departments":
        filtered = df

    else:
        filtered = df[
            df["Department"].astype(str) == selected_department
        ]

    section_title("Department Summary")

    st.dataframe(
        an.dept_table(filtered),
        hide_index=True,
        use_container_width=True
    )

    a, b = st.columns(2)

    with a:
        show(an.fig_dept_count(filtered))

    with b:
        show(an.fig_dept_salary(filtered))

    section_title("Department Performance")

    show(an.fig_dept_perf(filtered))


# ============================================================
# UPLOAD AND EXPORT
# ============================================================

def page_data(df):

    banner(
        "Data Management",
        "Upload employee datasets, review your records, and export reports."
    )

    section_title("Upload Dataset")

    st.info(
        "Upload a CSV file containing the required employee columns. "
        "The uploaded dataset is used for analysis during this session."
    )

    uploaded_file = st.file_uploader(
        "Choose an employee CSV file",
        type=["csv"],
        key="employee_csv_upload"
    )

    if uploaded_file is not None:

        if st.button(
            "Validate and analyse uploaded file",
            use_container_width=True
        ):

            try:
                uploaded_df, log = an.prepare(
                    an.load_data(uploaded_file)
                )

                st.session_state.upload = uploaded_df

                st.success(
                    "File validated and analysed successfully."
                )

                st.dataframe(
                    uploaded_df.head(10),
                    hide_index=True,
                    use_container_width=True
                )

                st.info(
                    "Choose 'Uploaded file' under Data source in the "
                    "sidebar to analyse this dataset throughout the app."
                )

            except Exception as ex:
                st.error(f"Could not process the file: {ex}")

    section_title("Export and Reports")

    st.write("Download your current dataset and analytics.")

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1:
        st.download_button(
            "⬇️ Cleaned employee data",
            df.to_csv(index=False),
            "Employee_Salary_Performance_Cleaned.csv",
            "text/csv",
            use_container_width=True
        )

    with c2:
        st.download_button(
            "⬇️ KPI summary",
            pd.Series(an.kpis(df))
            .rename("value")
            .to_csv(),
            "kpi_summary.csv",
            "text/csv",
            use_container_width=True
        )

    with c3:
        st.download_button(
            "⬇️ Correlation matrix",
            an.correlation(df).round(3).to_csv(),
            "correlation_matrix.csv",
            "text/csv",
            use_container_width=True
        )

    with c4:
        st.download_button(
            "⬇️ Printable HTML report",
            an.report_html(
                df,
                st.session_state.user["username"]
            ),
            "report.html",
            "text/html",
            use_container_width=True
        )


# ============================================================
# ADMINISTRATION
# ============================================================

def page_admin():

    banner(
        "Administration",
        "Manage registered accounts and review recent application activity."
    )

    if st.session_state.user.get("role") != "admin":
        st.error("You do not have permission to access this page.")
        return

    users_tab, activity_tab = st.tabs(
        ["Registered Users", "Recent Activity"]
    )

    with users_tab:

        section_title("Registered Accounts")

        users = pd.DataFrame(db.list_users())

        if users.empty:
            st.info("No registered users found.")

        else:
            sensitive_columns = [
                column
                for column in users.columns
                if any(
                    word in column.lower()
                    for word in [
                        "password",
                        "password_hash",
                        "secret"
                    ]
                )
            ]

            if sensitive_columns:
                users = users.drop(
                    columns=sensitive_columns,
                    errors="ignore"
                )

            st.dataframe(
                users,
                hide_index=True,
                use_container_width=True
            )

    with activity_tab:

        section_title("Recent Application Activity")

        activity = pd.DataFrame(db.recent_activity())

        if activity.empty:
            st.info("No recent activity recorded.")

        else:
            st.dataframe(
                activity,
                hide_index=True,
                use_container_width=True
            )


# ============================================================
# MAIN NAVIGATION
# ============================================================

def main():

    user = st.session_state.user

    pages = [
        "Dashboard",
        "Employees",
        "Analysis",
        "Departments",
        "Upload and export"
    ]

    if user.get("role") == "admin":
        pages.append("Administration")

    if st.session_state.get("page_navigation") not in pages:
        st.session_state["page_navigation"] = "Dashboard"

    with st.sidebar:

        st.markdown(
            """
            <div class="brand-box">
                <div class="brand-title">📊 StaffMetrics</div>
                <div class="brand-subtitle">
                    Employee Intelligence Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        display_name = (
            user.get("full_name")
            or user.get("username", "User")
        )

        st.markdown(
            f"""
            <div class="sidebar-user">
                <div class="sidebar-user-name">
                    👤 {html.escape(str(display_name))}
                </div>
                <div class="sidebar-user-role">
                    {html.escape(str(user.get('role', 'user')).title())}
                    account
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sidebar-section">APPLICATION MENU</div>',
            unsafe_allow_html=True
        )

        st.selectbox(
            "Navigate to module",
            pages,
            key="page_navigation",
            label_visibility="collapsed"
        )

        st.divider()

        st.markdown(
            '<div class="sidebar-section">DATA SOURCE</div>',
            unsafe_allow_html=True
        )

        uploaded_data = st.session_state.get("upload")

        sources = ["Employee database"]

        if uploaded_data is not None:
            sources.append("Uploaded file")

        src = st.selectbox(
            "Choose dataset",
            sources,
            key="data_source_select"
        )

        st.caption(
            "Use the employee database for persistent records "
            "or the uploaded file for session-based analysis."
        )

        st.divider()

        if st.button(
            "🚪 Sign out",
            use_container_width=True
        ):

            db.log_activity(
                user["id"],
                "signed out"
            )

            del st.session_state["user"]

            for key in [
                "page_navigation",
                "kpi_dialog",
                "analysis_view",
                "dashboard_departments",
                "dashboard_designations",
                "dashboard_salary",
                "dashboard_experience",
                "dashboard_performance",
                "employee_department_filter",
                "employee_designation_filter"
            ]:
                st.session_state.pop(key, None)

            st.rerun()

        st.markdown(
            """
            <div style="
                margin-top:25px;
                font-family:'DM Sans',sans-serif;
                font-size:0.72rem;
                color:#c7d2fe;
                text-align:center;
                line-height:1.8;
            ">
                StaffMetrics v2.0<br>
                Employee Analytics
            </div>
            """,
            unsafe_allow_html=True
        )

    is_db = src == "Employee database"

    if is_db:
        df = db.employee_frame()

    else:
        df = st.session_state.upload.copy()

    if df is None:
        df = pd.DataFrame()

    # Normalize numeric columns for filtering and analytics.
    for column in [
        "Basic_Salary",
        "Experience_Years",
        "Performance_Score"
    ]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

    page = st.session_state["page_navigation"]

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
# APPLICATION ENTRY POINT
# ============================================================

if "user" not in st.session_state:
    auth_page()

else:
    main()
