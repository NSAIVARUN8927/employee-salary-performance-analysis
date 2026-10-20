import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import analytics as an, auth, database as db, sql_queries as Q


# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Employee Salary & Performance Analysis",
    page_icon="📊",
    layout="wide"
)

db.init_db()

CSV = "data/employee_salary_performance.csv"

if not db.is_seeded():
    db.seed_database(an.prepare(an.load_data(CSV))[0])


# ============================================================
# GLOBAL CSS AND ANIMATIONS
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: #14213d;
}

[data-testid="stSidebar"] * {
    color: #e6ebf5;
}

.block-container {
    padding-top: 1.6rem;
    max-width: 1250px;
}

h1, h2, h3 {
    color: #14213d;
    font-weight: 600;
}

.banner {
    background: #14213d;
    color: #fff;
    padding: 22px 28px;
    border-radius: 6px;
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


/* ------------------------------------------------------------
   GENERAL BUTTON ANIMATION
------------------------------------------------------------ */

[data-testid="stButton"] > button {
    transition:
        transform 180ms ease,
        box-shadow 180ms ease,
        border-color 180ms ease,
        background 180ms ease;
}

[data-testid="stButton"] > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 9px 24px rgba(20, 33, 61, 0.13);
    border-color: #0f766e;
}

[data-testid="stButton"] > button:active {
    transform: translateY(-1px) scale(0.99);
}


/* ------------------------------------------------------------
   DASHBOARD KPI CARDS
   Native Streamlit buttons prevent URL redirects.
------------------------------------------------------------ */

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button {
    width: 100%;
    min-height: 94px;
    height: 94px;

    display: flex;
    align-items: flex-start;
    justify-content: center;

    text-align: left;
    white-space: normal;

    background: linear-gradient(
        145deg,
        #ffffff,
        #f6f9fc
    ) !important;

    border: 1px solid #dde5ef !important;
    border-top: 3px solid #0f766e !important;
    border-radius: 12px !important;

    padding: 12px 16px !important;

    color: #14213d !important;

    box-shadow: 0 3px 12px rgba(20, 33, 61, 0.04);
}

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button p {
    margin: 0;
    line-height: 1.35;
}

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button p:first-child {
    color: #5b6b82 !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
}

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button p:last-child {
    color: #14213d !important;
    font-size: 1.55rem !important;
    font-weight: 650 !important;
}

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button:hover {
    background: linear-gradient(
        145deg,
        #ffffff,
        #f6f9fc
    ) !important;

    border-top-color: #0f766e !important;
}


/* ------------------------------------------------------------
   KPI DIALOG ANIMATION
------------------------------------------------------------ */

@keyframes metricDialogEntrance {
    from {
        opacity: 0;
        transform: translateY(12px) scale(0.985);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

[data-testid="stDialog"] [role="dialog"] {
    animation: metricDialogEntrance 220ms ease-out;
    border-radius: 16px;
}


/* Respect reduced-motion preferences */

@media (prefers-reduced-motion: reduce) {
    [data-testid="stButton"] > button,
    [data-testid="stDialog"] [role="dialog"] {
        transition: none !important;
        animation: none !important;
    }
}
</style>
""", unsafe_allow_html=True)


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


# ============================================================
# KPI DETAILS
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
            "to explore salary distribution and differences."
        ),
        "module": "Analysis",
    },

    "Maximum salary": {
        "icon": "📈",
        "description": (
            "The highest basic salary among employees matching "
            "the current dashboard filters. Use the analysis module "
            "to explore salary distribution and differences."
        ),
        "module": "Analysis",
    },

    "Average performance": {
        "icon": "⭐",
        "description": (
            "The average performance score for employees matching "
            "the current dashboard filters. It helps summarize "
            "the performance level of the selected workforce."
        ),
        "module": "Analysis",
    },

    "Maximum performance": {
        "icon": "🏆",
        "description": (
            "The highest performance score among employees "
            "matching the current dashboard filters. Use the "
            "analysis module for additional performance summaries "
            "and charts."
        ),
        "module": "Analysis",
    },
}


# ============================================================
# NAVIGATION HELPERS
# ============================================================

def request_page_navigation(module):
    """
    Save the destination before rerunning the app.
    Navigation is handled before the sidebar selectbox is created.
    """

    st.session_state["_pending_page_navigation"] = module

    st.session_state.pop("_metric_dialog", None)

    st.rerun()


# ============================================================
# CLICKABLE KPI CARDS
# ============================================================

def interactive_kpi_cards(items, section_key):
    """
    Display clickable KPI cards using native Streamlit buttons.

    Employees:
        Opens the Employees module.

    Other KPI cards:
        Opens a metric-information dialog.

    No HTML links or URL-based redirects are used.
    """

    columns = st.columns(len(items))

    for index, (label, value) in enumerate(items):

        with columns[index]:

            clicked = st.button(
                f"{label}\n\n{value}",
                key=f"{section_key}_{index}",
                use_container_width=True,
                help=(
                    "Open the Employees module"
                    if label == "Employees"
                    else f"Learn what {label.lower()} means"
                )
            )

        if clicked:

            if label == "Employees":

                request_page_navigation("Employees")

            else:

                st.session_state["_metric_dialog"] = label

                st.rerun()


# ============================================================
# KPI INFORMATION DIALOG
# ============================================================

@st.dialog("Metric overview", width="small")
def metric_information_dialog():

    label = st.session_state.get("_metric_dialog")

    details = KPI_DETAILS.get(label)

    if not details:
        st.write("Metric information is not available.")
        return

    st.markdown(
        f"### {details['icon']} {label}"
    )

    st.write(details["description"])

    st.divider()

    st.caption(
        f"Recommended module: {details['module']}"
    )

    if st.button(
        f"Open {details['module']} module  →",
        key="metric_dialog_open_module",
        type="primary",
        use_container_width=True
    ):

        request_page_navigation(details["module"])

    if st.button(
        "Close",
        key="metric_dialog_close",
        use_container_width=True
    ):

        st.session_state.pop("_metric_dialog", None)

        st.rerun()


# ============================================================
# LOGIN AND REGISTRATION PAGE
# ============================================================

def auth_page():

    st.markdown("""
    <style>

    /* Login page background */

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(59, 130, 246, 0.15),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #f8fafc,
                #eaf0fb
            );
    }


    /* Hide sidebar before authentication */

    [data-testid="stSidebar"] {
        display: none;
    }


    /* Login page layout */

    .block-container {
        max-width: 1100px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }


    /* Login entrance animation */

    @keyframes loginPanelEntrance {
        from {
            opacity: 0;
            transform: translateY(14px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }


    /* Left branding panel */

    .login-brand {
        background: linear-gradient(
            145deg,
            #14213d,
            #233e70
        );

        color: white;

        padding: 45px 32px;

        border-radius: 22px 0 0 22px;

        min-height: 450px;

        display: flex;
        flex-direction: column;
        justify-content: center;

        box-shadow: 0 15px 40px rgba(20, 33, 61, 0.15);

        animation: loginPanelEntrance 550ms ease-out both;
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


    /* Right login card */

    .login-card {
        background: rgba(255, 255, 255, 0.92);

        padding: 25px 28px;

        border: 1px solid #e2e8f0;

        border-radius: 0 22px 22px 0;

        min-height: 450px;

        box-shadow: 0 15px 40px rgba(20, 33, 61, 0.10);

        animation: loginPanelEntrance 650ms ease-out both;
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


    /* Login buttons */

    .stButton > button {
        width: 100%;

        border-radius: 10px;

        min-height: 45px;

        font-weight: 600;

        border: none;

        background: linear-gradient(
            90deg,
            #2563eb,
            #0f766e
        );

        color: white;

        transition: all 0.2s ease;
    }


    .stButton > button:hover {
        transform: translateY(-2px);

        box-shadow: 0 7px 18px rgba(37, 99, 235, 0.2);

        color: white;
    }


    /* Text input styling */

    [data-testid="stTextInput"] input {
        border-radius: 9px;
        border: 1px solid #cbd5e1;
    }


    /* Tabs */

    [data-testid="stTabs"] button {
        font-weight: 600;
    }


    /* Footer */

    .security-note {
        font-size: 0.8rem;
        color: #64748b;
        text-align: center;
        margin-top: 20px;
    }


    /* Mobile responsive layout */

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


    # --------------------------------------------------------
    # ORIGINAL TWO-COLUMN LOGIN DESIGN
    # --------------------------------------------------------

    left, right = st.columns(
        [1, 1.15],
        gap="small"
    )


    # --------------------------------------------------------
    # LEFT BRANDING PANEL
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # RIGHT LOGIN PANEL
    # --------------------------------------------------------

    with right:

        st.markdown("""
        <div class="login-card">

            <div class="login-heading">
                Welcome back!
            </div>

            <div class="login-description">
                Sign in to access your analytics dashboard.
            </div>

        </div>
        """, unsafe_allow_html=True)


        login_tab, register_tab = st.tabs(
            [
                "🔐 Sign in",
                "✨ Create account"
            ]
        )


        # ====================================================
        # LOGIN TAB
        # ====================================================

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


            remember_me = st.checkbox(
                "Remember me on this session",
                key="remember_me"
            )


            if st.button(
                "Sign in",
                key="login_button"
            ):

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
                            "The username/email or password is incorrect."
                        )


            # ------------------------------------------------
            # FORGOT PASSWORD
            # ------------------------------------------------

            with st.expander("Forgot your password?"):

                st.write(
                    "Password recovery requires a configured email "
                    "or authentication provider."
                )

                st.info(
                    "The password-reset service must be configured "
                    "before a recovery email can be sent."
                )


        # ====================================================
        # REGISTRATION TAB
        # ====================================================

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


            # ------------------------------------------------
            # PASSWORD STRENGTH CHECK
            # ------------------------------------------------

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

                    st.warning(
                        "Password strength: Weak"
                    )

                elif score <= 4:

                    st.info(
                        "Password strength: Moderate"
                    )

                else:

                    st.success(
                        "Password strength: Strong"
                    )


            st.caption(
                "Use at least 8 characters. A combination of "
                "uppercase letters, lowercase letters, numbers, "
                "and symbols is recommended."
            )


            # ------------------------------------------------
            # CREATE ACCOUNT
            # ------------------------------------------------

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


        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        st.markdown(
            '<div class="security-note">'
            'StaffMetrics · Employee Salary & Performance Analysis'
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# DASHBOARD
# ============================================================

def page_dashboard(df):

    banner(
        "Executive Dashboard",
        (
            f"Welcome, "
            f"{st.session_state.user['full_name'] or st.session_state.user['username']}"
        )
    )


    st.subheader("Dashboard Filters")


    # --------------------------------------------------------
    # DEPARTMENT, DESIGNATION AND CHART FILTERS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SALARY FILTER
    # --------------------------------------------------------

    salary_min = float(
        df["Basic_Salary"].min()
    )

    salary_max = float(
        df["Basic_Salary"].max()
    )


    if salary_min == salary_max:

        selected_salary = (
            salary_min,
            salary_max
        )

        st.caption(
            f"Salary filter: {salary_min:,.0f}"
        )

    else:

        selected_salary = st.slider(
            "Basic salary range",
            min_value=salary_min,
            max_value=salary_max,
            value=(
                salary_min,
                salary_max
            ),
            key="dashboard_salary"
        )


    # --------------------------------------------------------
    # EXPERIENCE FILTER
    # --------------------------------------------------------

    c4, c5 = st.columns(2)


    exp_min = int(
        df["Experience_Years"].min()
    )

    exp_max = int(
        df["Experience_Years"].max()
    )


    with c4:

        if exp_min == exp_max:

            selected_experience = (
                exp_min,
                exp_max
            )

            st.caption(
                f"Experience: {exp_min} years"
            )

        else:

            selected_experience = st.slider(
                "Experience (years)",
                min_value=exp_min,
                max_value=exp_max,
                value=(
                    exp_min,
                    exp_max
                ),
                key="dashboard_experience"
            )


    # --------------------------------------------------------
    # PERFORMANCE FILTER
    # --------------------------------------------------------

    perf_min = float(
        df["Performance_Score"].min()
    )

    perf_max = float(
        df["Performance_Score"].max()
    )


    with c5:

        if perf_min == perf_max:

            selected_performance = (
                perf_min,
                perf_max
            )

            st.caption(
                f"Performance score: {perf_min}"
            )

        else:

            selected_performance = st.slider(
                "Performance score",
                min_value=perf_min,
                max_value=perf_max,
                value=(
                    perf_min,
                    perf_max
                ),
                key="dashboard_performance"
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

        st.warning(
            "No employees match your selected filters."
        )

        return


    st.caption(
        f"Showing {len(filtered_df):,} of {len(df):,} employee records."
    )


    # --------------------------------------------------------
    # CLICKABLE KPI CARDS
    # --------------------------------------------------------

    k = an.kpis(filtered_df)


    # First row of cards

    interactive_kpi_cards(
        [
            (
                "Employees",
                f"{k['total_employees']:,}"
            ),
            (
                "Average salary",
                f"{k['average_salary']:,.0f}"
            ),
            (
                "Median salary",
                f"{k['median_salary']:,.0f}"
            ),
            (
                "Minimum salary",
                f"{k['minimum_salary']:,.0f}"
            ),
        ],
        section_key="dashboard_kpi_top"
    )


    st.write("")


    # Second row of cards

    interactive_kpi_cards(
        [
            (
                "Maximum salary",
                f"{k['maximum_salary']:,.0f}"
            ),
            (
                "Average performance",
                f"{k['average_performance']:.2f}"
            ),
            (
                "Maximum performance",
                f"{k['maximum_performance']:.2f}"
            ),
        ],
        section_key="dashboard_kpi_bottom"
    )


    # Show KPI information dialog when selected

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


# ============================================================
# ADD AND DELETE EMPLOYEES
# ============================================================

def manage_employees(df):

    uid = st.session_state.user["id"]


    # --------------------------------------------------------
    # ADD EMPLOYEE
    # --------------------------------------------------------

    with st.expander("Add an employee"):

        with st.form("add_emp"):

            c = st.columns(3)


            e = {
                "Employee_ID": c[0].text_input(
                    "Employee ID"
                ),

                "Name": c[1].text_input(
                    "Name"
                ),

                "Age": c[2].number_input(
                    "Age",
                    18,
                    70,
                    30
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
                    0,
                    45,
                    3
                ),

                "Joining_Year": c[1].number_input(
                    "Joining year",
                    1990,
                    2030,
                    2024
                ),

                "Basic_Salary": c[2].number_input(
                    "Basic salary",
                    1.0,
                    1e7,
                    50000.0
                ),

                "Bonus": c[0].number_input(
                    "Bonus",
                    0.0,
                    1e6,
                    0.0
                ),

                "Performance_Score": c[1].number_input(
                    "Performance score (0-5)",
                    0.0,
                    5.0,
                    3.0,
                    0.5
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
                        "Employee added. It appears in the table "
                        "the next time the page refreshes."
                    )

                except Exception as ex:

                    st.error(
                        f"The employee could not be added: {ex}"
                    )


    # --------------------------------------------------------
    # DELETE EMPLOYEE
    # --------------------------------------------------------

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


# ============================================================
# EMPLOYEES PAGE
# ============================================================

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


    lo = int(
        df["Experience_Years"].min()
    )

    hi = int(
        df["Experience_Years"].max()
    )


    exp = c3.slider(
        "Experience (years)",
        lo,
        max(hi, lo + 1),
        (
            lo,
            max(hi, lo + 1)
        )
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
                q,
                case=False
            )
            |
            f["Name"].astype(str).str.contains(
                q,
                case=False
            )
        ]


    st.caption(
        f"{len(f)} employees"
    )


    st.dataframe(
        f,
        hide_index=True
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


# ============================================================
# ANALYSIS PAGE
# ============================================================

def page_analysis(df):

    banner(
        "Salary and performance analysis",
        "Statistics, experience trends and correlations"
    )


    t1, t2, t3 = st.tabs(
        [
            "Salary",
            "Performance",
            "Correlation"
        ]
    )


    # --------------------------------------------------------
    # SALARY ANALYSIS
    # --------------------------------------------------------

    with t1:

        st.dataframe(
            an.salary_summary(df).round(2).to_frame("Value")
        )

        show(
            an.fig_salary_dist(df)
        )

        st.subheader("By experience")

        st.dataframe(
            an.by_experience(df),
            hide_index=True
        )

        show(
            an.fig_experience(df)
        )


    # --------------------------------------------------------
    # PERFORMANCE ANALYSIS
    # --------------------------------------------------------

    with t2:

        st.dataframe(
            an.performance_summary(df).round(2).to_frame("Value")
        )

        show(
            an.fig_perf_dist(df)
        )

        show(
            an.fig_dept_perf(df)
        )


    # --------------------------------------------------------
    # CORRELATION ANALYSIS
    # --------------------------------------------------------

    with t3:

        st.dataframe(
            an.correlation(df).round(2)
        )

        show(
            an.fig_corr(df)
        )


# ============================================================
# DEPARTMENTS PAGE
# ============================================================

def page_departments(df):

    banner(
        "Departments",
        "Employee count, salary and performance by department"
    )


    st.dataframe(
        an.dept_table(df),
        hide_index=True
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


# ============================================================
# SQL EXPLORER PAGE
# ============================================================

def page_sql():

    banner(
        "SQL explorer",
        "Run the prepared queries or write your own SELECT"
    )


    titles = [
        f"Q{i}. {t}"
        for i, (t, _) in enumerate(Q.QUERIES, 1)
    ]


    pick = st.selectbox(
        "Prepared query",
        titles
    )


    sql = st.text_area(
        "SQL (read-only)",
        Q.QUERIES[titles.index(pick)][1],
        height=130
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
                    hide_index=True
                )

            except Exception as ex:

                st.error(
                    f"The query failed: {ex}"
                )


# ============================================================
# UPLOAD AND EXPORT PAGE
# ============================================================

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


# ============================================================
# ADMINISTRATION PAGE
# ============================================================

def page_admin():

    banner(
        "Administration",
        "Registered users and recent activity"
    )


    st.dataframe(
        pd.DataFrame(db.list_users()),
        hide_index=True
    )


    st.dataframe(
        pd.DataFrame(db.recent_activity()),
        hide_index=True
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
        "SQL explorer",
        "Upload and export"
    ]


    if user["role"] == "admin":

        pages.append("Administration")


    # --------------------------------------------------------
    # APPLY PENDING NAVIGATION BEFORE CREATING THE SELECTBOX
    # --------------------------------------------------------

    pending_page = st.session_state.pop(
        "_pending_page_navigation",
        None
    )


    if pending_page in pages:

        st.session_state["page_navigation"] = pending_page


    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

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


        src = st.selectbox(
            "Data source",
            ["Employee database"]
            + (["Uploaded file"] if up is not None else [])
        )


        if st.button("Sign out"):

            db.log_activity(
                user["id"],
                "signed out"
            )

            del st.session_state["user"]

            st.rerun()


    # --------------------------------------------------------
    # SELECT DATA SOURCE
    # --------------------------------------------------------

    is_db = src == "Employee database"


    if is_db:

        df = db.employee_frame()

    else:

        df = up


    # --------------------------------------------------------
    # ROUTE TO THE SELECTED MODULE
    # --------------------------------------------------------

    if page == "Dashboard":

        page_dashboard(df)


    elif page == "Employees":

        page_employees(
            df,
            is_db
        )


    elif page == "Analysis":

        page_analysis(df)


    elif page == "Departments":

        page_departments(df)


    elif page == "SQL explorer":

        page_sql()


    elif page == "Upload and export":

        page_data(df)


    else:

        page_admin()


# ============================================================
# APP ENTRY POINT
# ============================================================

if "user" not in st.session_state:

    auth_page()

else:

    main()
