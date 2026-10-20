import os
import re
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from backend import analytics as an, auth, database as db


# ============================================================
# APPLICATION CONFIGURATION
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
# SESSION AND LOGIN CONFIGURATION
# ============================================================

# The app uses Streamlit session state for login.
# This avoids the extra_streamlit_components dependency.

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


def save_login_cookie(user):
    """
    Create a signed token for possible future cookie integration.
    This function does not write a browser cookie.
    """
    safe_user = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user.get("full_name") or user["username"],
        "role": user["role"],
    }

    return auth_serializer.dumps(safe_user)


def restore_login_cookie():
    """
    Browser-cookie restoration is not enabled in this version.
    Users sign in again after their Streamlit session ends.
    """
    return None


def clear_login_cookie():
    """Clear the current Streamlit login session."""
    st.session_state.pop("user", None)


# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .block-container {
        padding-top: 1.6rem;
        max-width: 1250px;
    }

    [data-testid="stSidebar"] {
        background: #14213d;
    }

    [data-testid="stSidebar"] * {
        color: #e6ebf5;
    }

    h1, h2, h3 {
        color: #14213d;
        font-weight: 600;
    }

    .banner {
        background: #14213d;
        color: #fff;
        padding: 22px 28px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    .banner h1 {
        color: #fff;
        margin: 0;
        font-size: 1.7rem;
    }

    .banner p {
        margin: 4px 0 0;
        color: #b9c4dc;
    }

    [data-testid="stButton"] > button {
        transition:
            transform 180ms ease,
            box-shadow 180ms ease,
            border-color 180ms ease;
    }

    [data-testid="stButton"] > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 9px 24px rgba(20, 33, 61, 0.13);
        border-color: #0f766e;
    }

    [class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button {
        position: relative;
        width: 100%;
        min-height: 124px;
        height: 124px;
        white-space: pre-line;
        text-align: left;
        background: linear-gradient(
            135deg,
            #ffffff 0%,
            #f2f8fb 100%
        ) !important;
        border: 1px solid #dce7ef !important;
        border-left: 5px solid #0f766e !important;
        border-radius: 18px !important;
        padding: 17px 18px !important;
        color: #14213d !important;
        box-shadow: 0 7px 18px rgba(20, 33, 61, 0.07);
    }

    [class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button:hover {
        background: linear-gradient(
            135deg,
            #ffffff 0%,
            #e9f7f5 100%
        ) !important;
        transform: translateY(-5px);
        box-shadow: 0 15px 28px rgba(15, 118, 110, 0.14);
    }

    [data-testid="stDialog"] [role="dialog"] {
        border-radius: 16px;
    }

    @media (prefers-reduced-motion: reduce) {
        [data-testid="stButton"] > button {
            transition: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SHARED UI FUNCTIONS
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
# KPI INFORMATION
# ============================================================

KPI_DETAILS = {
    "Average salary": {
        "icon": "💰",
        "description": (
            "The average basic salary across employees matching "
            "the current dashboard filters."
        ),
        "module": "Analysis",
    },
    "Median salary": {
        "icon": "⚖️",
        "description": (
            "The median is the middle salary after salaries are "
            "ordered. It can describe a typical salary more "
            "robustly than the average when unusual values exist."
        ),
        "module": "Analysis",
    },
    "Minimum salary": {
        "icon": "📉",
        "description": (
            "The lowest basic salary among employees matching "
            "the current dashboard filters."
        ),
        "module": "Analysis",
    },
    "Maximum salary": {
        "icon": "📈",
        "description": (
            "The highest basic salary among employees matching "
            "the current dashboard filters."
        ),
        "module": "Analysis",
    },
    "Average performance": {
        "icon": "⭐",
        "description": (
            "The average performance score for employees "
            "matching the current dashboard filters."
        ),
        "module": "Analysis",
    },
    "Maximum performance": {
        "icon": "🏆",
        "description": (
            "The highest performance score among employees "
            "matching the current dashboard filters."
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


# ============================================================
# LOGIN AND REGISTRATION
# ============================================================

def auth_page():
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
            padding-top: 2rem;
        }

        .login-heading {
            color: #14213d;
            font-size: 1.9rem;
            font-weight: 800;
            margin-bottom: 5px;
        }

        .login-description {
            color: #64748b;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [1, 1.08],
        gap="medium",
        vertical_alignment="center",
    )

    with left:
        components.html(
            """
            <!doctype html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    * { box-sizing: border-box; }
                    body {
                        margin: 0;
                        font-family: Arial, sans-serif;
                    }
                    .brand {
                        min-height: 510px;
                        padding: 38px 30px;
                        border-radius: 22px;
                        color: white;
                        background: linear-gradient(
                            145deg,
                            #101d38,
                            #1e3a66 58%,
                            #0f766e 130%
                        );
                        box-shadow: 0 22px 55px rgba(20,33,61,.18);
                    }
                    .logo {
                        width: 76px;
                        height: 76px;
                        display: grid;
                        place-items: center;
                        border-radius: 23px;
                        margin-bottom: 24px;
                        font-size: 38px;
                        background: rgba(255,255,255,.13);
                        border: 1px solid rgba(255,255,255,.28);
                    }
                    h1 {
                        font-size: 38px;
                        letter-spacing: -1px;
                        margin: 0 0 12px;
                    }
                    .tagline {
                        color: #dbeafe;
                        font-size: 15px;
                        line-height: 1.8;
                        margin-bottom: 25px;
                    }
                    .feature {
                        margin: 15px 0;
                        color: #f0fdfa;
                    }
                    @media(max-width:700px) {
                        .brand { min-height: auto; padding: 28px 24px; }
                        h1 { font-size: 30px; }
                    }
                </style>
            </head>
            <body>
                <div class="brand">
                    <div class="logo">📊</div>
                    <h1>StaffMetrics</h1>
                    <p class="tagline">
                        Turn employee data into meaningful insights.
                        Understand salaries, track performance, and
                        make confident workforce decisions.
                    </p>
                    <div class="feature">✓ Smart employee analytics</div>
                    <div class="feature">↗ Clear salary insights</div>
                    <div class="feature">★ Performance reporting</div>
                    <div class="feature">⌘ Workforce management</div>
                </div>
            </body>
            </html>
            """,
            height=530,
            scrolling=False,
        )

    with right:
        st.markdown(
            """
            <div class="login-heading">Welcome back</div>
            <div class="login-description">
                Sign in to continue to your employee analytics workspace.
            </div>
            """,
            unsafe_allow_html=True,
        )

        login_tab, register_tab = st.tabs(
            ["🔐 Sign in", "✨ Create account"]
        )

        # ----------------------------------------------------
        # SIGN IN
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

            if st.button(
                "Sign in →",
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

                        db.log_activity(
                            user["id"],
                            "signed in",
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

        # ----------------------------------------------------
        # REGISTRATION
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
                "Create account →",
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

    if df.empty:
        st.warning("No employee records are available.")
        return

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

    # --------------------------------------------------------
    # SALARY FILTER
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # EXPERIENCE FILTER
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # PERFORMANCE FILTER
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # AUTOMATED INSIGHTS
    # --------------------------------------------------------
    st.subheader("Automated Insights")

    for line in an.insights(filtered_df):
        st.info(line)

    # --------------------------------------------------------
    # VISUAL ANALYTICS
    # --------------------------------------------------------
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

    departments = sorted(
        df["Department"].dropna().unique().tolist()
    )

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
                    "Department", departments
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

                    st.success("Employee added successfully.")
                    st.rerun()

                except Exception as ex:
                    st.error(
                        f"The employee could not be added: {ex}"
                    )

    with st.expander("Delete an employee"):
        employee_ids = df["Employee_ID"].tolist()

        if employee_ids:
            selected_id = st.selectbox(
                "Employee",
                employee_ids,
                key="delete_employee_id",
            )

            if st.button("Delete employee"):
                try:
                    db.delete_employee(selected_id)

                    db.log_activity(
                        uid,
                        f"deleted employee {selected_id}",
                    )

                    st.success("Employee deleted.")
                    st.rerun()

                except Exception as ex:
                    st.error(
                        f"The employee could not be deleted: {ex}"
                    )


def page_employees(df, is_db):
    banner(
        "Employees",
        "Search, filter and manage employee records",
    )

    if df.empty:
        st.warning("No employee records are available.")
        return

    c1, c2, c3 = st.columns(3)

    departments = sorted(
        df["Department"].dropna().unique().tolist()
    )

    designations = sorted(
        df["Designation"].dropna().astype(str).unique().tolist()
    )

    dept = c1.multiselect("Department", departments)
    role = c2.multiselect("Designation", designations)

    lo = int(df["Experience_Years"].min())
    hi = int(df["Experience_Years"].max())

    if lo == hi:
        exp = (lo, hi)
        c3.caption(f"Experience: {lo} years")
    else:
        exp = c3.slider(
            "Experience (years)",
            lo,
            hi,
            (lo, hi),
            key="employee_experience_filter",
        )

    query = st.text_input("Search by ID or name")

    filtered = df[
        df["Experience_Years"].between(*exp)
    ]

    if dept:
        filtered = filtered[
            filtered["Department"].isin(dept)
        ]

    if role:
        filtered = filtered[
            filtered["Designation"].astype(str).isin(role)
        ]

    if query:
        filtered = filtered[
            filtered["Employee_ID"].astype(str).str.contains(
                query, case=False, na=False
            )
            | filtered["Name"].astype(str).str.contains(
                query, case=False, na=False
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
        mime="text/csv",
    )

    if is_db and st.session_state.user.get("role") == "admin":
        manage_employees(df)


# ============================================================
# SALARY AND PERFORMANCE ANALYSIS
# ============================================================

def page_analysis(df):
    banner(
        "Salary and performance analysis",
        "Statistics, experience trends and correlations",
    )

    if df.empty:
        st.warning("No employee records are available.")
        return

    tab_salary, tab_performance, tab_correlation = st.tabs(
        ["Salary", "Performance", "Correlation"]
    )

    with tab_salary:
        st.subheader("Salary Summary")

        st.dataframe(
            an.salary_summary(df).round(2).to_frame("Value"),
            use_container_width=True,
        )

        show(an.fig_salary_dist(df))

        st.subheader("Salary by Experience")

        st.dataframe(
            an.by_experience(df),
            hide_index=True,
            use_container_width=True,
        )

        show(an.fig_experience(df))

    with tab_performance:
        st.subheader("Performance Summary")

        st.dataframe(
            an.performance_summary(df)
            .round(2)
            .to_frame("Value"),
            use_container_width=True,
        )

        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))

    with tab_correlation:
        st.subheader("Correlation Matrix")

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

    if df.empty:
        st.warning("No employee records are available.")
        return

    st.dataframe(
        an.dept_table(df),
        hide_index=True,
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        show(an.fig_dept_count(df))

    with col2:
        show(an.fig_dept_salary(df))


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
        type=["csv"],
        key="employee_csv_upload",
    )

    if uploaded_file and st.button("Analyse this file"):
        try:
            uploaded_df, log = an.prepare(
                an.load_data(uploaded_file)
            )

            st.session_state["upload"] = uploaded_df

            st.success("File analysed successfully.")

            if log:
                st.write(log)

            st.rerun()

        except Exception as ex:
            st.error(f"Could not process the file: {ex}")

    st.subheader("Export")

    if df is None or df.empty:
        st.warning("There is no data available to export.")
        return

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.download_button(
            "Cleaned data (CSV)",
            df.to_csv(index=False),
            "Employee_Salary_Performance_Cleaned.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "KPI summary (CSV)",
            pd.Series(
                an.kpis(df)
            ).rename("value").to_csv(),
            "kpi_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col3:
        st.download_button(
            "Correlation matrix (CSV)",
            an.correlation(df).round(3).to_csv(),
            "correlation_matrix.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col4:
        st.download_button(
            "Printable report (HTML)",
            an.report_html(
                df,
                st.session_state.user["username"],
            ),
            "report.html",
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

    if users:
        st.dataframe(
            pd.DataFrame(users),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No registered users were found.")

    st.subheader("Recent Activity")

    activity = db.recent_activity()

    if activity:
        st.dataframe(
            pd.DataFrame(activity),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No recent activity was found.")


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    user = st.session_state["user"]

    pages = [
        "Dashboard",
        "Employees",
        "Analysis",
        "Departments",
        "Upload and export",
    ]

    if user.get("role") == "admin":
        pages.append("Administration")

    # Apply pending navigation before creating the widget.
    pending_page = st.session_state.pop(
        "_pending_page_navigation",
        None,
    )

    if pending_page in pages:
        st.session_state["page_navigation"] = pending_page

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------
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
            "Sign out",
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
    # ROUTE TO THE SELECTED PAGE
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

if "user" in st.session_state:
    main()
else:
    auth_page()
