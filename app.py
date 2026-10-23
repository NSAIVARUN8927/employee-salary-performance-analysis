import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

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
</style>
""", unsafe_allow_html=True)


def banner(title, subtitle=""):
    st.markdown(f'<div class="banner"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def kpis(items):
    """Display employee and performance statistics in individual cards."""

    card_colors = [
        "kpi-blue",
        "kpi-green",
        "kpi-purple",
        "kpi-orange",
        "kpi-pink",
        "kpi-cyan",
        "kpi-teal"
    ]

    columns = st.columns(len(items), gap="medium")

    for index, (col, item) in enumerate(zip(columns, items)):
        label, value = item
        color_class = card_colors[index % len(card_colors)]

        with col:
            st.markdown(
                f"""
                <div class="kpi-card {color_class}">
                    <span class="kpi-label">{label}</span>
                    <span class="kpi-value">{value}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
def auth_page():
    # Login page styling
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
    banner(
        "Executive Dashboard",
        f"Welcome, {st.session_state.user['full_name'] or st.session_state.user['username']}"
    )

    st.subheader("Dashboard Filters")

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
    banner("Employees", "Search, filter and manage employee records")

    # ==================== FILTER OPTIONS ====================

    c1, c2, c3 = st.columns(3)

    dept = c1.multiselect(
        "Department",
        sorted(df["Department"].dropna().unique())
    )

    role = c2.multiselect(
        "Designation",
        sorted(df["Designation"].dropna().astype(str).unique())
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

    # ==================== APPLY FILTERS ====================

    if selected_min_exp > selected_max_exp:
        st.error(
            "Minimum experience cannot be greater than maximum experience."
        )
        return

    f = df.copy()

    f["Experience_Years"] = pd.to_numeric(
        f["Experience_Years"],
        errors="coerce"
    )

    f = f[
        f["Experience_Years"].between(
            selected_min_exp,
            selected_max_exp,
            inclusive="both"
        )
    ]

    if dept:
        f = f[f["Department"].isin(dept)]

    if role:
        f = f[f["Designation"].astype(str).isin(role)]

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
    banner(
        "Salary and performance analysis",
        "Statistics, experience trends and correlations"
    )

    t1, t2, t3 = st.tabs(["Salary", "Performance", "Correlation"])

    # ==================== SALARY ANALYSIS ====================
    with t1:
        st.subheader("Salary Summary")

        salary_summary = an.salary_summary(df).round(2)

        salary_df = salary_summary.rename_axis(None).reset_index()
        salary_df.columns = ["Salary", "Value"]

        salary_labels = {
            "Average Salary": "Average",
            "Median Salary": "Median",
            "Minimum Salary": "Minimum",
            "Maximum Salary": "Maximum",
            "Salary Std. Deviation": "Std. Deviation",
        }

        salary_df["Salary"] = salary_df["Salary"].replace(salary_labels)

        st.dataframe(
            salary_df,
            hide_index=True,
            use_container_width=True
        )

        show(an.fig_salary_dist(df))

        st.subheader("Salary by Experience")
        st.dataframe(
            an.by_experience(df),
            hide_index=True,
            use_container_width=True
        )
        show(an.fig_experience(df))

    # ==================== PERFORMANCE ANALYSIS ====================
    with t2:
        st.subheader("Performance Summary")

        performance_summary = an.performance_summary(df).round(2)

        performance_df = performance_summary.rename_axis(None).reset_index()
        performance_df.columns = ["Performance", "Value"]

        performance_labels = {
            "Average Performance": "Average",
            "Median Performance": "Median",
            "Minimum Performance": "Minimum",
            "Maximum Performance": "Maximum",
            "Performance Std. Deviation": "Std. Deviation",
        }

        performance_df["Performance"] = (
            performance_df["Performance"].replace(performance_labels)
        )

        st.dataframe(
            performance_df,
            hide_index=True,
            use_container_width=True
        )

        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))

    # ==================== CORRELATION ANALYSIS ====================
    with t3:
        st.subheader("Correlation Matrix")

        correlation_df = an.correlation(df).round(2)
        correlation_df.index.name = "Metric"
        correlation_df = correlation_df.reset_index()

        st.dataframe(
            correlation_df,
            hide_index=True,
            use_container_width=True
        )

        show(an.fig_corr(df))

def page_departments(df):
    banner("Departments", "Employee count, salary and performance by department")
    st.dataframe(an.dept_table(df), hide_index=True)
    a, b = st.columns(2)
    with a:
        show(an.fig_dept_count(df))
    with b:
        show(an.fig_dept_salary(df))



def page_data(df):
    banner("Upload and export", "Analyse your own CSV and download results")
    up = st.file_uploader("Upload a CSV with the same columns as the sample dataset", type="csv")
    if up and st.button("Analyse this file"):
        try:
            st.session_state.upload, log = an.prepare(an.load_data(up))
            st.toast("File analysed. Choose 'Uploaded file' as the data source in the sidebar.")
            st.rerun()
        except Exception as ex:
            st.error(str(ex))
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
            data=df.to_csv(index=False),
            file_name="Employee_Salary_Performance_Cleaned.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    elif export_option == "KPI summary (CSV)":
        st.download_button(
            "⬇️ Download",
            data=pd.Series(an.kpis(df)).rename("value").to_csv(),
            file_name="kpi_summary.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    elif export_option == "Correlation matrix (CSV)":
        st.download_button(
            "⬇️ Download",
            data=an.correlation(df).round(3).to_csv(),
            file_name="correlation_matrix.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    elif export_option == "Printable report (HTML)":
        st.download_button(
            "⬇️ Download",
            data=an.report_html(df, st.session_state.user["username"]),
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

    banner(
        f"Welcome, {full_name}",
        "Your personal account information and registration details"
    )

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

    # Dynamically obtain the logged-in user's display name
    display_name = (
        user.get("full_name")
        or user.get("username")
        or "User"
    )

    # Main application pages
    pages = [
        "Dashboard",
        "Employees",
        "Analysis",
        "Departments",
        "Upload and export"
    ]

    # The profile navigation label changes for each logged-in user
    pages.append(display_name)

    with st.sidebar:
        st.markdown(f"### 👤 {display_name}")
        st.caption(f"{user.get('role', 'user').title()} account")

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
            db.log_activity(user["id"], "signed out")
            del st.session_state["user"]
            st.rerun()

    is_db = src == "Employee database"
    df = db.employee_frame() if is_db else up

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
