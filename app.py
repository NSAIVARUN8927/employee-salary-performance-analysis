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
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700;800&display=swap');

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

/* Main page banner */

.banner {
    background: linear-gradient(120deg, #14213d, #233e70);
    color: #fff;
    padding: 24px 28px;
    border-radius: 14px;
    margin-bottom: 22px;
    box-shadow: 0 8px 22px rgba(20, 33, 61, 0.12);
}

.banner h1 {
    color: #fff;
    margin: 0;
    font-size: 1.7rem;
}

.banner p {
    margin: 5px 0 0;
    color: #cbd5e1;
}


/* ============================================================
   GENERAL BUTTON ANIMATION
============================================================ */

[data-testid="stButton"] > button {
    transition:
        transform 180ms ease,
        box-shadow 180ms ease,
        border-color 180ms ease,
        background 180ms ease;
}

[data-testid="stButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(20, 33, 61, 0.12);
}

[data-testid="stButton"] > button:active {
    transform: scale(0.99);
}


/* ============================================================
   DASHBOARD KPI CARDS
============================================================ */

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button {
    position: relative;
    width: 100%;
    min-height: 124px;
    height: 124px;
    overflow: hidden;

    display: flex;
    align-items: center;
    justify-content: flex-start;

    text-align: left;
    white-space: pre-line;

    background: linear-gradient(
        135deg,
        #ffffff 0%,
        #f2f8fb 100%
    ) !important;

    border: 1px solid #dce7ef !important;
    border-radius: 18px !important;
    border-left: 5px solid #0f766e !important;

    padding: 17px 18px !important;

    color: #14213d !important;

    box-shadow: 0 7px 18px rgba(20, 33, 61, 0.07);

    animation: kpiCardEntrance 420ms ease-out both;
}


/* Decorative arrow */

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button::after {
    content: "↗";

    position: absolute;
    right: 15px;
    top: 12px;

    width: 28px;
    height: 28px;

    display: grid;
    place-items: center;

    border-radius: 9px;

    color: #0f766e;
    background: rgba(15, 118, 110, 0.09);

    font-size: 16px;

    transition:
        transform 180ms ease,
        background 180ms ease;
}


/* KPI hover effect */

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button:hover {
    background: linear-gradient(
        135deg,
        #ffffff 0%,
        #e9f7f5 100%
    ) !important;

    border-color: #b8dcd7 !important;
    border-left-color: #0f766e !important;

    transform: translateY(-5px) scale(1.01);

    box-shadow: 0 15px 28px rgba(15, 118, 110, 0.14);
}

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button:hover::after {
    transform: translate(2px, -2px);
    background: rgba(15, 118, 110, 0.16);
}


/* KPI text */

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button p {
    margin: 0;
    line-height: 1.4;
}

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button p:first-child {
    color: #64748b !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
}

[class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button p:last-child {
    color: #14213d !important;
    font-size: 1.7rem !important;
    font-weight: 750 !important;
}


/* KPI entrance animation */

@keyframes kpiCardEntrance {
    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* Dialog animation */

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


/* Accessibility */

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
            "The average performance score for employees matching "
            "the current dashboard filters."
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


# ============================================================
# NAVIGATION
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
    Native Streamlit buttons prevent URL-based redirects.

    Employees card:
        Opens Employees module.

    Other cards:
        Open a metric information dialog.
    """

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

    /* Animated background */

    .stApp {
        background:
            radial-gradient(
                circle at 8% 8%,
                rgba(20, 184, 166, 0.13),
                transparent 30%
            ),
            radial-gradient(
                circle at 92% 90%,
                rgba(59, 130, 246, 0.13),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #f7faff,
                #edf3fb
            );
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1120px;
        padding-top: 2.4rem;
        padding-bottom: 2rem;
    }


    /* Entrance animations */

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

    @keyframes circleFloat {
        0%, 100% {
            transform: translate(0, 0);
        }

        50% {
            transform: translate(-10px, 12px);
        }
    }


    /* Left branding panel */

    .login-brand {
        position: relative;
        overflow: hidden;

        background: linear-gradient(
            145deg,
            #101d38 0%,
            #1e3a66 58%,
            #0f766e 130%
        );

        color: #fff;

        padding: 42px 34px;

        border-radius: 24px 0 0 24px;

        min-height: 500px;

        display: flex;
        flex-direction: column;
        justify-content: center;

        box-shadow: 0 22px 55px rgba(20, 33, 61, 0.18);

        animation: panelIn 550ms ease-out both;
    }


    /* Decorative background circles */

    .login-brand:before,
    .login-brand:after {
        content: "";
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
    }

    .login-brand:before {
        width: 240px;
        height: 240px;

        right: -100px;
        top: -95px;

        border: 1px solid rgba(255, 255, 255, 0.18);

        box-shadow:
            0 0 0 24px rgba(255, 255, 255, 0.035),
            0 0 0 48px rgba(255, 255, 255, 0.025);

        animation: circleFloat 7s ease-in-out infinite;
    }

    .login-brand:after {
        width: 180px;
        height: 180px;

        left: -95px;
        bottom: -95px;

        background: rgba(45, 212, 191, 0.08);
    }


    /* Logo container */

    .brand-mark {
        position: relative;
        z-index: 1;

        width: 76px;
        height: 76px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 23px;

        font-size: 39px;

        margin-bottom: 24px;

        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.22),
            rgba(255, 255, 255, 0.08)
        );

        border: 1px solid rgba(255, 255, 255, 0.28);

        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);

        animation: logoFloat 4s ease-in-out infinite;
    }


    /* Branding text */

    .login-brand h1 {
        position: relative;
        z-index: 1;

        color: #fff !important;

        font-size: 2.65rem;
        font-weight: 800;
        letter-spacing: -1.2px;

        margin: 0 0 12px 0;
    }

    .login-brand .tagline {
        position: relative;
        z-index: 1;

        color: #dbeafe;

        font-size: 1.03rem;
        line-height: 1.8;

        margin: 0 0 22px 0;

        max-width: 390px;
    }


    /* Feature list */

    .brand-feature {
        position: relative;
        z-index: 1;

        display: flex;
        align-items: center;
        gap: 11px;

        color: #f0fdfa;

        margin: 13px 0;

        font-size: 0.96rem;

        transition: transform 180ms ease;
    }

    .brand-feature:hover {
        transform: translateX(5px);
    }

    .feature-dot {
        width: 28px;
        height: 28px;

        flex: 0 0 28px;

        display: inline-flex;
        align-items: center;
        justify-content: center;

        border-radius: 9px;

        background: rgba(45, 212, 191, 0.16);

        border: 1px solid rgba(153, 246, 228, 0.25);

        color: #99f6e4;
    }


    /* Right login card */

    .login-card {
        background: rgba(255, 255, 255, 0.96);

        padding: 30px 30px 22px;

        border: 1px solid #e0e8f2;

        border-radius: 0 24px 24px 0;

        min-height: 500px;

        box-shadow: 0 22px 55px rgba(20, 33, 61, 0.10);

        animation: panelIn 720ms ease-out both;
    }

    .login-heading {
        color: #14213d;

        font-size: 1.9rem;
        font-weight: 800;
        letter-spacing: -0.6px;

        margin-bottom: 5px;
    }

    .login-description {
        color: #64748b;

        margin-bottom: 20px;

        line-height: 1.6;
    }


    /* Input styling */

    [data-testid="stTextInput"] input {
        border-radius: 11px;
        border: 1px solid #d6e0eb;
        min-height: 43px;
        transition: border-color 180ms ease, box-shadow 180ms ease;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #0f766e;
        box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.10);
    }


    /* Tabs */

    [data-testid="stTabs"] button {
        font-weight: 700;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        color: #0f766e !important;
    }


    /* Login buttons */

    .stButton > button {
        border-radius: 11px;
        min-height: 46px;
        font-weight: 700;

        transition:
            transform 180ms ease,
            box-shadow 180ms ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.17);
    }


    /* Footer */

    .security-note {
        font-size: 0.78rem;
        color: #94a3b8;
        text-align: center;
        margin-top: 18px;
    }


    /* Mobile responsive design */

    @media (max-width: 700px) {

        .block-container {
            padding-top: 1rem;
        }

        .login-brand {
            border-radius: 20px 20px 0 0;
            min-height: auto;
            padding: 28px 24px;
        }

        .login-brand h1 {
            font-size: 2.15rem;
        }

        .login-card {
            border-radius: 0 0 20px 20px;
            min-height: auto;
            padding: 22px 20px;
        }
    }


    /* Accessibility */

    @media (prefers-reduced-motion: reduce) {
        .login-brand,
        .login-card,
        .brand-mark,
        .login-brand:before {
            animation: none !important;
        }
    }

    </style>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # TWO-COLUMN LOGIN LAYOUT
    # --------------------------------------------------------

    left, right = st.columns(
        [1, 1.08],
        gap="small",
        vertical_alignment="center"
    )


    # --------------------------------------------------------
    # LEFT BRANDING PANEL
    # --------------------------------------------------------

    with left:

        st.markdown("""
        <div class="login-brand">

            <div class="brand-mark">📊</div>

            <h1>StaffMetrics</h1>

            <p class="tagline">
                Turn employee data into meaningful insights.
                Understand salaries, track performance, and
                make confident workforce decisions.
            </p>

            <div class="brand-feature">
                <span class="feature-dot">✓</span>
                <span>Smart employee analytics</span>
            </div>

            <div class="brand-feature">
                <span class="feature-dot">↗</span>
                <span>Clear salary insights</span>
            </div>

            <div class="brand-feature">
                <span class="feature-dot">★</span>
                <span>Performance reporting</span>
            </div>

            <div class="brand-feature">
                <span class="feature-dot">⌘</span>
                <span>Workforce management</span>
            </div>

        </div>
        """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # RIGHT LOGIN PANEL
    # --------------------------------------------------------

    with right:

        st.markdown("""
        <div class="login-card">

            <div class="login-heading">
                Welcome back
            </div>

            <div class="login-description">
                Sign in to continue to your employee analytics workspace.
            </div>

        </div>
        """, unsafe_allow_html=True)


        login_tab, register_tab = st.tabs([
            "🔐 Sign in",
            "✨ Create account"
        ])


        # ====================================================
        # SIGN-IN TAB
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
                type="default" if show_login_password else "password",
                key="login_password"
            )

            st.checkbox(
                "Remember me on this session",
                key="remember_me"
            )


            if st.button(
                "Sign in  →",
                key="login_button",
                use_container_width=True,
                type="primary"
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


            with st.expander("Forgot your password?"):

                st.write(
                    "Password recovery requires a configured "
                    "email or authentication provider."
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


            # Password strength indicator

            if password:

                import re

                score = sum([
                    len(password) >= 8,
                    bool(re.search(r"[A-Z]", password)),
                    bool(re.search(r"[a-z]", password)),
                    bool(re.search(r"[0-9]", password)),
                    bool(re.search(r"[^A-Za-z0-9]", password)),
                ])

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
                type="primary"
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


    # Department, designation and chart filters

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


    # Salary filter

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
            key="dashboard_salary"
        )


    # Experience filter

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
                key="dashboard_experience"
            )


    # Performance filter

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
                key="dashboard_performance"
            )


    # Apply filters

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


    # Charts

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


# ============================================================
# EMPLOYEE MANAGEMENT
# ============================================================

def manage_employees(df):

    uid = st.session_state.user["id"]


    # Add employee

    with st.expander("Add an employee"):

        with st.form("add_emp"):

            c = st.columns(3)

            e = {
                "Employee_ID": c[0].text_input("Employee ID"),
                "Name": c[1].text_input("Name"),
                "Age": c[2].number_input("Age", 18, 70, 30),

                "Gender": c[0].selectbox(
                    "Gender",
                    ["Female", "Male"]
                ),

                "Department": c[1].selectbox(
                    "Department",
                    sorted(df["Department"].unique())
                ),

                "Designation": c[2].text_input("Designation"),

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
                        "after the page refreshes."
                    )

                except Exception as ex:

                    st.error(
                        f"The employee could not be added: {ex}"
                    )


    # Delete employee

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

    lo = int(df["Experience_Years"].min())
    hi = int(df["Experience_Years"].max())

    exp = c3.slider(
        "Experience (years)",
        lo,
        max(hi, lo + 1),
        (lo, max(hi, lo + 1))
    )

    q = st.text_input("Search by ID or name")

    f = df[df["Experience_Years"].between(*exp)]

    if dept:
        f = f[f["Department"].isin(dept)]

    if role:
        f = f[f["Designation"].astype(str).isin(role)]

    if q:
        f = f[
            f["Employee_ID"].astype(str).str.contains(q, case=False)
            | f["Name"].astype(str).str.contains(q, case=False)
        ]

    st.caption(f"{len(f)} employees")

    st.dataframe(f, hide_index=True)

    st.download_button(
        "Download filtered records (CSV)",
        f.to_csv(index=False),
        "employees_filtered.csv"
    )

    if is_db and st.session_state.user["role"] == "admin":
        manage_employees(df)


# ============================================================
# ANALYSIS PAGE
# ============================================================

def page_analysis(df):

    banner(
        "Salary and performance analysis",
        "Statistics, experience trends and correlations"
    )

    t1, t2, t3 = st.tabs([
        "Salary",
        "Performance",
        "Correlation"
    ])

    with t1:

        st.dataframe(
            an.salary_summary(df).round(2).to_frame("Value")
        )

        show(an.fig_salary_dist(df))

        st.subheader("By experience")

        st.dataframe(
            an.by_experience(df),
            hide_index=True
        )

        show(an.fig_experience(df))


    with t2:

        st.dataframe(
            an.performance_summary(df).round(2).to_frame("Value")
        )

        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))


    with t3:

        st.dataframe(
            an.correlation(df).round(2)
        )

        show(an.fig_corr(df))


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
        show(an.fig_dept_count(df))

    with b:
        show(an.fig_dept_salary(df))


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


    # Apply navigation before creating the sidebar selectbox

    pending_page = st.session_state.pop(
        "_pending_page_navigation",
        None
    )

    if pending_page in pages:
        st.session_state["page_navigation"] = pending_page


    # Sidebar

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


    # Select data source

    is_db = src == "Employee database"

    df = db.employee_frame() if is_db else up


    # Route to selected page

    if page == "Dashboard":

        page_dashboard(df)

    elif page == "Employees":

        page_employees(df, is_db)

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
