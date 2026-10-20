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


# ==================== GLOBAL STYLING ====================

st.markdown("""
<style>
@import url(
    'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap'
);

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
    background: linear-gradient(135deg, #14213d, #233e70);
    color: white;
    padding: 22px 28px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(20, 33, 61, 0.12);
}

.banner h1 {
    color: white;
    margin: 0;
    font-size: 1.7rem;
}

.banner p {
    margin: 4px 0 0;
    color: #b9c4dc;
}

.kpi {
    background: linear-gradient(145deg, #ffffff, #f6f9fc);
    border: 1px solid #dde5ef;
    border-top: 3px solid #0f766e;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 3px 12px rgba(20, 33, 61, 0.04);
}

.kpi span {
    color: #5b6b82;
    font-size: 0.85rem;
}

.kpi b {
    display: block;
    font-size: 1.55rem;
    color: #14213d;
    font-weight: 650;
}

/* Button animations */

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

/* Modal animation */

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

/* Login form */

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
    border-radius: 10px;
    min-height: 45px;
    font-weight: 600;
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

@media (prefers-reduced-motion: reduce) {
    [data-testid="stButton"] > button,
    [data-testid="stDialog"] [role="dialog"] {
        transition: none !important;
        animation: none !important;
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
}
</style>
""", unsafe_allow_html=True)


# ==================== THEME-AWARE STYLING ====================

THEME = st.session_state.get("theme_choice", "Light")

if THEME == "Dark":
    st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {
        background: #0b1220 !important;
        color: #f1f5f9 !important;
    }

    [data-testid="stHeader"] {
        background: #0b1220 !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, li, .stMarkdown,
    [data-testid="stCaptionContainer"] {
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background: #111827 !important;
        height: 100vh !important;
        overflow: hidden !important;
        scrollbar-width: none !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        height: 100vh !important;
        overflow-y: hidden !important;
    }

    [data-testid="stSidebar"]::-webkit-scrollbar,
    [data-testid="stSidebar"] *::-webkit-scrollbar {
        display: none !important;
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: #f8fafc !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        background: #263244 !important;
        border: 1px solid #64748b !important;
    }

    [data-baseweb="select"] > div {
        background: #263244 !important;
        border-color: #64748b !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="select"] span {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #1e293b !important;
        color: #f8fafc !important;
    }

    [role="option"] {
        color: #f8fafc !important;
    }

    [role="option"]:hover {
        background: #334155 !important;
    }

    [data-testid="stButton"] button,
    [data-testid="stDownloadButton"] button {
        background: #334155 !important;
        color: #f8fafc !important;
        border: 1px solid #64748b !important;
    }

    [data-testid="stButton"] button p,
    [data-testid="stButton"] button span {
        color: #f8fafc !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        background: #172033 !important;
        color: #f8fafc !important;
    }

    [data-testid="stExpander"],
    [data-testid="stDialog"] [role="dialog"] {
        background: #172033 !important;
        color: #f8fafc !important;
        border-color: #475569 !important;
    }

    .kpi {
        background: linear-gradient(145deg, #1e293b, #263244) !important;
        border-color: #475569 !important;
    }

    .kpi span {
        color: #cbd5e1 !important;
    }

    .kpi b {
        color: #f8fafc !important;
    }

    .login-card {
        background: #172033 !important;
        border-color: #475569 !important;
    }

    .login-heading {
        color: #f8fafc !important;
    }

    .login-description {
        color: #cbd5e1 !important;
    }

    .banner {
        background: linear-gradient(135deg, #111827, #1e3a5f) !important;
    }
    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        height: 100vh !important;
        overflow: hidden !important;
        scrollbar-width: none !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        height: 100vh !important;
        overflow-y: hidden !important;
    }

    [data-testid="stSidebar"]::-webkit-scrollbar,
    [data-testid="stSidebar"] *::-webkit-scrollbar {
        display: none !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: #14213d !important;
        -webkit-text-fill-color: #14213d !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
    }

    [data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #cbd5e1 !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="select"] span {
        color: #14213d !important;
        -webkit-text-fill-color: #14213d !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #ffffff !important;
        color: #14213d !important;
    }

    [role="option"] {
        color: #14213d !important;
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
            "salaries are ordered. It is less affected by unusually "
            "high or low salaries than the average."
        ),
        "module": "Analysis",
    },
    "Average performance": {
        "icon": "⭐",
        "description": (
            "The average employee performance score for the current "
            "selection. It helps summarize overall performance."
        ),
        "module": "Analysis",
    },
    "Average experience": {
        "icon": "📈",
        "description": (
            "The average number of years of experience among the "
            "employees currently shown."
        ),
        "module": "Employees",
    },
    "Total employees": {
        "icon": "👥",
        "description": (
            "The number of employee records remaining after applying "
            "the dashboard filters."
        ),
        "module": "Employees",
    },
}


@st.dialog("KPI details")
def show_kpi_details(label):
    detail = KPI_DETAILS.get(label)

    if not detail:
        st.info("No additional details are available.")
        return

    st.markdown(f"### {detail['icon']} {label}")
    st.write(detail["description"])
    st.caption(f"Related module: {detail['module']}")


# ==================== LOGIN AND REGISTRATION ====================

def auth_page():
    st.markdown("""
    <div style="height:25px"></div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown("""
        <div class="login-brand">
            <div class="brand-icon">📊</div>
            <h1>StaffMetrics</h1>
            <p>
                Employee Salary & Performance Analysis.
                Explore workforce data, compare salary trends,
                understand employee performance and make
                data-driven decisions.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="login-card">
            <div class="login-heading">Welcome</div>
            <div class="login-description">
                Sign in to continue or create a new account.
            </div>
        </div>
        """, unsafe_allow_html=True)

        login_tab, register_tab = st.tabs(
            ["Sign in", "Register"]
        )

        with login_tab:
            with st.form("login_form"):
                login_id = st.text_input(
                    "Username or email"
                )

                password = st.text_input(
                    "Password",
                    type="password"
                )

                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True
                )

            if submitted:
                user = auth.login(login_id, password)

                if user:
                    st.session_state.user = user

                    db.log_activity(
                        user["id"],
                        "signed in"
                    )

                    st.rerun()
                else:
                    st.error(
                        "Invalid username/email or password."
                    )

        with register_tab:
            with st.form("register_form"):
                username = st.text_input("Username")
                email = st.text_input("Email")
                full_name = st.text_input("Full name")

                password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password"
                )

                submitted = st.form_submit_button(
                    "Create account",
                    use_container_width=True
                )

            if submitted:
                if not all([
                    username.strip(),
                    email.strip(),
                    password,
                    confirm_password
                ]):
                    st.error("Please complete all required fields.")

                elif password != confirm_password:
                    st.error("Passwords do not match.")

                else:
                    try:
                        result = auth.register(
                            username.strip(),
                            email.strip(),
                            full_name.strip(),
                            password
                        )

                        if result:
                            st.success(
                                "Account created successfully. "
                                "You can now sign in."
                            )
                        else:
                            st.error(
                                "Registration failed. "
                                "The username or email may already exist."
                            )

                    except Exception as ex:
                        st.error(f"Registration failed: {ex}")

        st.markdown(
            '<div class="security-note">'
            'Your employee analytics workspace'
            '</div>',
            unsafe_allow_html=True
        )


# ==================== DASHBOARD ====================

def page_dashboard(df):

    banner(
        "Dashboard",
        "An overview of employee salary and performance"
    )

    if df.empty:
        st.warning("No employee records are available.")
        return

    # Filters
    c1, c2, c3 = st.columns(3)

    departments = c1.multiselect(
        "Department",
        sorted(df["Department"].dropna().unique()),
        key="dashboard_departments"
    )

    designations = c2.multiselect(
        "Designation",
        sorted(df["Designation"].dropna().astype(str).unique()),
        key="dashboard_designations"
    )

    exp_min = int(df["Experience_Years"].min())
    exp_max = int(df["Experience_Years"].max())

    experience = c3.slider(
        "Experience (years)",
        min_value=exp_min,
        max_value=max(exp_max, exp_min + 1),
        value=(exp_min, max(exp_max, exp_min + 1)),
        key="dashboard_experience"
    )

    filtered = df.copy()

    if departments:
        filtered = filtered[
            filtered["Department"].isin(departments)
        ]

    if designations:
        filtered = filtered[
            filtered["Designation"].astype(str).isin(designations)
        ]

    filtered = filtered[
        filtered["Experience_Years"].between(*experience)
    ]

    if filtered.empty:
        st.warning("No employees match the selected filters.")
        return

    # Calculate metrics from the filtered data.
    total_employees = len(filtered)
    average_salary = filtered["Basic_Salary"].mean()
    median_salary = filtered["Basic_Salary"].median()
    average_performance = filtered["Performance_Score"].mean()
    average_experience = filtered["Experience_Years"].mean()

    metric_values = [
        ("Total employees", f"{total_employees:,}"),
        ("Average salary", f"₹{average_salary:,.2f}"),
        ("Median salary", f"₹{median_salary:,.2f}"),
        ("Average performance", f"{average_performance:.2f}/5"),
        ("Average experience", f"{average_experience:.1f} years"),
    ]

    # Clickable KPI cards
    cols = st.columns(len(metric_values))

    for col, (label, value) in zip(cols, metric_values):
        with col:
            if st.button(
                f"{KPI_DETAILS[label]['icon']} {label}\n{value}",
                key=f"kpi_{label}",
                use_container_width=True
            ):
                show_kpi_details(label)

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Department-wise salary")
        show(an.fig_dept_salary(filtered))

    with right:
        st.subheader("Salary distribution")
        show(an.fig_salary_dist(filtered))

    left, right = st.columns(2)

    with left:
        st.subheader("Department-wise performance")
        show(an.fig_dept_perf(filtered))

    with right:
        st.subheader("Salary vs performance")
        show(an.fig_salary_vs_perf(filtered))

    st.subheader("Employee records")

    st.dataframe(
        filtered,
        hide_index=True,
        use_container_width=True
    )


# ==================== EMPLOYEE MANAGEMENT ====================

def manage_employees(df):

    uid = st.session_state.user["id"]

    st.subheader("Manage employee records")

    with st.expander("Add a new employee"):

        with st.form("add_employee_form"):

            c = st.columns(3)

            e = {
                "Employee_ID": c[0].text_input(
                    "Employee ID"
                ).strip(),

                "Name": c[1].text_input(
                    "Employee name"
                ).strip(),

                "Age": c[2].number_input(
                    "Age",
                    min_value=18,
                    max_value=100,
                    value=25
                ),

                "Gender": c[0].selectbox(
                    "Gender",
                    ["Male", "Female", "Other"]
                ),

                "Department": c[1].selectbox(
                    "Department",
                    sorted(df["Department"].dropna().unique())
                ),

                "Designation": c[2].text_input(
                    "Designation",
                    value="Employee"
                ),

                "Experience_Years": c[0].number_input(
                    "Experience (years)",
                    min_value=0,
                    max_value=45,
                    value=3
                ),

                "Joining_Year": c[1].number_input(
                    "Joining year",
                    min_value=1990,
                    max_value=2030,
                    value=2024
                ),

                "Basic_Salary": c[2].number_input(
                    "Basic salary",
                    min_value=1.0,
                    max_value=1e7,
                    value=50000.0
                ),

                "Bonus": c[0].number_input(
                    "Bonus",
                    min_value=0.0,
                    max_value=1e6,
                    value=0.0
                ),

                "Performance_Score": c[1].number_input(
                    "Performance score (0-5)",
                    min_value=0.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.5
                )
            }

            if st.form_submit_button("Add employee"):

                if not e["Employee_ID"] or not e["Name"]:
                    st.error("Employee ID and name are required.")

                else:
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

    q = st.text_input("Search by ID or name")

    f = df[
        df["Experience_Years"].between(*exp)
    ]

    if dept:
        f = f[f["Department"].isin(dept)]

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
