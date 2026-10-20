import io
import re

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from backend import analytics as an, auth, database as db


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StaffMetrics - Employee Salary & Performance Analysis",
    page_icon="📊",
    layout="wide",
)

db.init_db()


# ============================================================
# THEME CONFIGURATION
# ============================================================

THEME_OPTIONS = ["☀️ Light", "🌙 Dark"]

if st.session_state.get("theme_choice") not in THEME_OPTIONS:
    st.session_state["theme_choice"] = "☀️ Light"

IS_DARK = st.session_state["theme_choice"] == "🌙 Dark"

if IS_DARK:
    COLORS = {
        "background": "#0E1117", "card": "#1C2430", "input": "#222B38",
        "text": "#F0F6FC", "heading": "#F0F6FC", "muted": "#B0BAC8",
        "border": "#394554", "primary": "#2DD4BF", "primary_hover": "#5EEAD4",
        "primary_text": "#071B19", "sidebar": "#090D14", "sidebar_text": "#F0F6FC",
        "table_alt": "#1C2430", "shadow": "rgba(0, 0, 0, 0.25)",
    }
else:
    COLORS = {
        "background": "#F7F9FC", "card": "#FFFFFF", "input": "#FFFFFF",
        "text": "#253047", "heading": "#14213D", "muted": "#64748B",
        "border": "#DCE4EE", "primary": "#0F766E", "primary_hover": "#115E59",
        "primary_text": "#FFFFFF", "sidebar": "#14213D", "sidebar_text": "#F0F6FC",
        "table_alt": "#F4F7FB", "shadow": "rgba(20, 33, 61, 0.08)",
    }


# ============================================================
# GLOBAL THEME CSS
# ============================================================

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    :root {{
        color-scheme: {"dark" if IS_DARK else "light"};
        --app-bg: {COLORS["background"]};
        --card-bg: {COLORS["card"]};
        --input-bg: {COLORS["input"]};
        --text-color: {COLORS["text"]};
        --heading-color: {COLORS["heading"]};
        --muted-color: {COLORS["muted"]};
        --border-color: {COLORS["border"]};
        --primary-color: {COLORS["primary"]};
        --primary-hover: {COLORS["primary_hover"]};
        --primary-text: {COLORS["primary_text"]};
        --sidebar-bg: {COLORS["sidebar"]};
        --sidebar-text: {COLORS["sidebar_text"]};
        --table-alt: {COLORS["table_alt"]};
        --shadow-color: {COLORS["shadow"]};
    }}

    html, body, [class*="css"] {{ font-family: 'IBM Plex Sans', sans-serif; }}

    .stApp, [data-testid="stAppViewContainer"] {{
        background: var(--app-bg) !important;
        color: var(--text-color) !important;
    }}

    .block-container {{ padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1300px; }}

    h1, h2, h3, h4, h5, h6 {{ color: var(--heading-color) !important; font-weight: 600; }}
    [data-testid="stCaptionContainer"] {{ color: var(--muted-color) !important; }}

    [data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color);
    }}
    [data-testid="stSidebar"] * {{ color: var(--sidebar-text); }}

    .banner {{
        background: {("#172334" if IS_DARK else "#14213D")};
        padding: 24px 28px; border-radius: 14px; margin-bottom: 22px;
        border: 1px solid {("#344154" if IS_DARK else "#14213D")};
    }}
    .banner h1 {{ color: #FFFFFF !important; margin: 0; font-size: 1.8rem; }}
    .banner p {{ color: #D6E0EF !important; margin: 6px 0 0; }}

    [data-testid="stButton"] > button, [data-testid="stDownloadButton"] > button {{
        background: var(--card-bg); color: var(--text-color);
        border: 1px solid var(--border-color); border-radius: 9px;
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }}
    [data-testid="stButton"] > button:hover, [data-testid="stDownloadButton"] > button:hover {{
        color: var(--primary-color); border-color: var(--primary-color);
        box-shadow: 0 7px 20px var(--shadow-color); transform: translateY(-2px);
    }}
    [data-testid="stButton"] > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button {{
        background: var(--primary-color) !important; color: var(--primary-text) !important;
        border-color: var(--primary-color) !important; font-weight: 600;
    }}
    [data-testid="stButton"] > button[kind="primary"]:hover {{
        background: var(--primary-hover) !important;
    }}

    input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea {{
        background: var(--input-bg) !important; color: var(--text-color) !important;
        border-color: var(--border-color) !important;
    }}
    [data-baseweb="select"] > div {{
        background: var(--input-bg) !important; color: var(--text-color) !important;
        border-color: var(--border-color) !important;
    }}
    [data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"], [role="option"] {{
        background: var(--card-bg) !important; color: var(--text-color) !important;
    }}
    [role="option"]:hover {{ background: var(--table-alt) !important; }}

    [data-testid="stMetric"] {{
        background: var(--card-bg); padding: 17px; border: 1px solid var(--border-color);
        border-radius: 14px; box-shadow: 0 4px 15px var(--shadow-color);
    }}
    [data-testid="stMetricLabel"] p {{ color: var(--muted-color) !important; }}
    [data-testid="stMetricValue"] div {{ color: var(--heading-color) !important; }}

    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border-color); border-radius: 10px; overflow: hidden;
    }}
    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: var(--primary-color) !important; border-bottom-color: var(--primary-color) !important;
    }}
    [data-testid="stExpander"] {{
        background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px;
    }}
    [data-testid="stAlert"] {{ border-radius: 10px; }}
    a {{ color: var(--primary-color) !important; }}
    hr {{ border-color: var(--border-color) !important; }}

    [class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button {{
        width: 100%; min-height: 120px; white-space: pre-line; text-align: left;
        background: var(--card-bg) !important; color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-left: 5px solid var(--primary-color) !important;
        border-radius: 16px !important; padding: 17px !important;
        box-shadow: 0 7px 18px var(--shadow-color); font-size: 15px;
    }}
    [class*="st-key-dashboard_kpi_"] [data-testid="stButton"] > button:hover {{
        border-color: var(--primary-color) !important; color: var(--primary-color) !important;
        transform: translateY(-4px);
    }}

    .login-heading {{ color: var(--heading-color) !important; font-size: 1.9rem; font-weight: 800; margin-bottom: 5px; }}
    .login-description {{ color: var(--muted-color) !important; margin-bottom: 20px; line-height: 1.6; }}

    @media (prefers-reduced-motion: reduce) {{
        [data-testid="stButton"] > button {{ transition: none !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SHARED UI HELPERS
# ============================================================

def banner(title, subtitle=""):
    st.markdown(
        f'<div class="banner"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def show(fig):
    st.pyplot(fig)
    plt.close(fig)


def read_text(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


@st.cache_data(show_spinner=False)
def analyse(csv_text):
    """Clean and standardise a dataset. Cached per unique CSV text."""
    return an.prepare(an.load_data(io.StringIO(csv_text)))[0]


# ============================================================
# KPI CARDS AND METRIC DIALOG
# ============================================================

KPI_DETAILS = {
    "Average salary": ("💰", "The average basic salary across employees matching the current dashboard filters.", "Analysis"),
    "Median salary": ("⚖️", "The median is the middle salary after salaries are ordered. It shows a typical salary.", "Analysis"),
    "Minimum salary": ("📉", "The lowest basic salary among employees matching the current dashboard filters.", "Analysis"),
    "Maximum salary": ("📈", "The highest basic salary among employees matching the current dashboard filters.", "Analysis"),
    "Average performance": ("⭐", "The average performance score for employees matching the current dashboard filters.", "Analysis"),
    "Maximum performance": ("🏆", "The highest performance score among employees matching the current dashboard filters.", "Analysis"),
}

KPI_ICONS = {"Employees": "👥", **{k: v[0] for k, v in KPI_DETAILS.items()}}


def request_page_navigation(page):
    st.session_state["_pending_page_navigation"] = page
    st.session_state.pop("_metric_dialog", None)
    st.rerun()


def interactive_kpi_cards(items, section_key):
    columns = st.columns(len(items))
    for index, (label, value) in enumerate(items):
        with columns[index]:
            clicked = st.button(
                f"{KPI_ICONS.get(label, '📊')}  {label}\n\n{value}",
                key=f"{section_key}_{index}",
                use_container_width=True,
                help="Open the Employees page" if label == "Employees" else f"Learn about {label.lower()}",
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
    icon, description, module = details
    st.markdown(f"### {icon} {label}")
    st.write(description)
    st.divider()
    st.caption(f"Recommended module: {module}")
    if st.button(f"Open {module} page →", key="metric_dialog_open", type="primary", use_container_width=True):
        request_page_navigation(module)
    if st.button("Close", key="metric_dialog_close", use_container_width=True):
        st.session_state.pop("_metric_dialog", None)
        st.rerun()


# ============================================================
# THEME SELECTOR
# ============================================================

def theme_selector(location="sidebar"):
    st.radio(
        "Appearance",
        options=THEME_OPTIONS,
        key="theme_choice",
        horizontal=(location == "main"),
    )


# ============================================================
# LOGIN AND REGISTRATION
# ============================================================

def auth_page():
    left, right = st.columns([1, 1.08], gap="medium", vertical_alignment="center")

    with left:
        components.html(
            """
            <!doctype html>
            <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { box-sizing: border-box; }
                body { margin: 0; font-family: Arial, sans-serif; }
                .brand {
                    min-height: 510px; padding: 38px 30px; border-radius: 22px; color: white;
                    background: linear-gradient(145deg, #101d38, #1e3a66 58%, #0f766e 130%);
                    box-shadow: 0 22px 55px rgba(20,33,61,.18);
                }
                .logo {
                    width: 76px; height: 76px; display: grid; place-items: center;
                    border-radius: 23px; margin-bottom: 24px; font-size: 38px;
                    background: rgba(255,255,255,.13); border: 1px solid rgba(255,255,255,.28);
                }
                h1 { color: white; font-size: 38px; letter-spacing: -1px; margin: 0 0 12px; }
                .tagline { color: #dbeafe; font-size: 15px; line-height: 1.8; margin-bottom: 25px; }
                .feature { margin: 15px 0; color: #f0fdfa; }
                @media(max-width:700px) { .brand { min-height: auto; padding: 28px 24px; } h1 { font-size: 30px; } }
            </style></head>
            <body>
                <div class="brand">
                    <div class="logo">📊</div>
                    <h1>StaffMetrics</h1>
                    <p class="tagline">
                        Turn employee data into meaningful insights. Understand salaries,
                        track performance, and make confident workforce decisions.
                    </p>
                    <div class="feature">✓ Smart employee analytics</div>
                    <div class="feature">↗ Clear salary insights</div>
                    <div class="feature">★ Performance reporting</div>
                    <div class="feature">⌘ Workforce management</div>
                </div>
            </body></html>
            """,
            height=530,
            scrolling=False,
        )

    with right:
        st.markdown(
            """
            <div class="login-heading">Welcome to StaffMetrics</div>
            <div class="login-description">
                Sign in with your company account to access your employee analytics workspace.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Website appearance")
        theme_selector(location="main")

        login_tab, register_tab = st.tabs(["🔐 Sign in", "✨ Create account"])

        # ---- Sign in ----
        with login_tab:
            st.subheader("Sign in to your account")
            login_user = st.text_input("Username", key="login_username")
            show_login_password = st.checkbox("Show password", key="show_login_password")
            login_password = st.text_input(
                "Password",
                type="default" if show_login_password else "password",
                key="login_password",
            )

            if st.button("Sign in →", key="login_button", use_container_width=True, type="primary"):
                if not login_user.strip() or not login_password:
                    st.warning("Enter your username and password.")
                else:
                    user = auth.login(login_user, login_password)
                    if user:
                        st.session_state["user"] = user
                        db.log_activity(user["id"], "signed in")
                        st.rerun()
                    else:
                        st.error("The username or password is incorrect.")

        # ---- Create account ----
        with register_tab:
            st.subheader("Create your account")
            full_name = st.text_input("Full name", key="register_full_name")
            email = st.text_input("Email address", key="register_email")
            org = st.text_input(
                "Company or industry name",
                key="register_org",
                help="Users from the same company share one admin and see only their company's users.",
            )
            username = st.text_input("Choose a username", key="register_username")

            show_register_password = st.checkbox("Show passwords", key="show_register_password")
            pw_type = "default" if show_register_password else "password"
            password = st.text_input("Create password", type=pw_type, key="register_password")
            confirm_password = st.text_input("Confirm password", type=pw_type, key="register_confirm_password")

            if password:
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

            st.caption("Use at least 8 characters. A mix of letters, numbers and symbols is recommended.")

            if st.button("Create account →", key="register_button", use_container_width=True, type="primary"):
                if not all([full_name.strip(), email.strip(), org.strip(), username.strip(), password, confirm_password]):
                    st.warning("Please complete all the fields.")
                elif password != confirm_password:
                    st.error("The passwords do not match.")
                else:
                    ok, message = auth.register(username, email, full_name, org, password)
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)

        st.caption("StaffMetrics · Employee Salary & Performance Analysis")


# ============================================================
# DATASET SELECTOR (sidebar)
# ============================================================

def sidebar_dataset(uid):
    datasets = db.list_datasets(uid)
    if not datasets:
        st.session_state["active_dataset_id"] = None
        st.caption("No dataset yet. Upload one under Datasets.")
        return None

    ids = [d["id"] for d in datasets]
    names = {d["id"]: d["name"] for d in datasets}
    current = st.session_state.get("active_dataset_id")
    index = ids.index(current) if current in ids else 0

    choice = st.selectbox("Active dataset", ids, index=index, format_func=lambda i: names[i])
    st.session_state["active_dataset_id"] = choice
    return choice


# ============================================================
# DATASETS PAGE (upload and manage CSV files)
# ============================================================

def page_datasets(uid):
    banner("Datasets", "Upload your employee and salary CSV, and manage saved datasets")

    uploaded = st.file_uploader("CSV file", type=["csv"], key="dataset_upload")
    default_name = uploaded.name.rsplit(".", 1)[0] if uploaded else ""
    name = st.text_input("Dataset name", value=default_name, key=f"dataset_name_{default_name}")

    if uploaded is not None and st.button("Save and analyse"):
        raw = read_text(uploaded.getvalue())
        try:
            an.prepare(an.load_data(io.StringIO(raw)))  # validate before saving
        except Exception as ex:
            st.error(f"This file could not be analysed: {ex}")
        else:
            new_id = db.save_dataset(uid, name.strip() or uploaded.name, raw)
            db.log_activity(uid, f"uploaded dataset {new_id}")
            st.session_state["active_dataset_id"] = new_id
            st.success("Dataset saved and selected as the active dataset.")
            st.rerun()

    st.subheader("Saved Datasets")
    rows = db.list_datasets(uid)
    if not rows:
        st.info("No datasets saved yet.")
        return

    st.dataframe(
        pd.DataFrame(rows)[["name", "created_at"]].rename(columns={"name": "Name", "created_at": "Uploaded"}),
        hide_index=True,
        use_container_width=True,
    )

    names = {r["id"]: r["name"] for r in rows}
    target = st.selectbox("Delete a dataset", list(names), format_func=lambda i: names[i], key="delete_dataset_id")
    confirm = st.checkbox("I understand this cannot be undone", key="delete_dataset_confirm")
    if st.button("Delete dataset", disabled=not confirm):
        db.delete_dataset(target, uid)
        db.log_activity(uid, f"deleted dataset {target}")
        if st.session_state.get("active_dataset_id") == target:
            st.session_state["active_dataset_id"] = None
        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def experience_range(df, ds_id):
    """Two number inputs, bounded by the data's own min and max. Returns (from, to) or None."""
    exp = df["Experience_Years"]
    if not exp.notna().any():
        return None
    lo, hi = int(exp.min()), int(exp.max())
    a, b = st.columns(2)
    start = a.number_input("Experience from (years)", min_value=lo, max_value=hi, value=lo, step=1,
                           key=f"exp_from_{ds_id}")
    end = b.number_input("Experience to (years)", min_value=lo, max_value=hi, value=hi, step=1,
                         key=f"exp_to_{ds_id}")
    if start > end:
        st.warning("'From' is greater than 'To'. Showing no results until the range is corrected.")
        return (start, start - 1)  # empty range
    return (start, end)


def page_dashboard(df, ds_id):
    user = st.session_state["user"]
    banner("Executive Dashboard", f"Welcome, {user.get('full_name') or user['username']}")

    required = ["Department", "Designation", "Basic_Salary", "Experience_Years", "Performance_Score"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error("The dataset is missing required columns: " + ", ".join(missing))
        return

    st.subheader("Dashboard Filters")

    departments = ["All"] + sorted(df["Department"].dropna().astype(str).unique().tolist())
    designations = ["All"] + sorted(df["Designation"].dropna().astype(str).unique().tolist())

    c1, c2, c3 = st.columns(3)
    dept = c1.selectbox("Department", departments, key=f"dash_dept_{ds_id}")
    desig = c2.selectbox("Designation", designations, key=f"dash_desig_{ds_id}")
    chart_choice = c3.selectbox(
        "Chart to display",
        ["All charts", "Department-wise salary", "Salary distribution",
         "Department-wise performance", "Salary vs. performance"],
        key=f"dash_chart_{ds_id}",
    )

    exp_range = experience_range(df, ds_id)

    sal_min, sal_max = float(df["Basic_Salary"].min()), float(df["Basic_Salary"].max())
    if sal_min == sal_max:
        sal_range = (sal_min, sal_max)
        st.caption(f"Basic salary: {sal_min:,.0f}")
    else:
        sal_range = st.slider("Basic salary range", sal_min, sal_max, (sal_min, sal_max),
                              key=f"dash_salary_{ds_id}")

    perf_min, perf_max = float(df["Performance_Score"].min()), float(df["Performance_Score"].max())
    if perf_min == perf_max:
        perf_range = (perf_min, perf_max)
        st.caption(f"Performance score: {perf_min}")
    else:
        perf_range = st.slider("Performance score", perf_min, perf_max, (perf_min, perf_max),
                               key=f"dash_perf_{ds_id}")

    # Apply filters
    mask = df["Basic_Salary"].between(*sal_range) & df["Performance_Score"].between(*perf_range)
    if dept != "All":
        mask &= df["Department"].astype(str) == dept
    if desig != "All":
        mask &= df["Designation"].astype(str) == desig
    if exp_range is not None:
        mask &= df["Experience_Years"].between(*exp_range)

    filtered = df[mask]

    if filtered.empty:
        st.warning("No employees match your selected filters.")
        return

    st.caption(f"Showing {len(filtered):,} of {len(df):,} employee records.")

    k = an.kpis(filtered)

    interactive_kpi_cards(
        [
            ("Employees", f"{k['total_employees']:,}"),
            ("Average salary", f"{k['average_salary']:,.0f}"),
            ("Median salary", f"{k['median_salary']:,.0f}"),
            ("Minimum salary", f"{k['minimum_salary']:,.0f}"),
        ],
        section_key=f"dashboard_kpi_top_{ds_id}",
    )
    st.write("")
    interactive_kpi_cards(
        [
            ("Maximum salary", f"{k['maximum_salary']:,.0f}"),
            ("Average performance", f"{k['average_performance']:.2f}"),
            ("Maximum performance", f"{k['maximum_performance']:.2f}"),
        ],
        section_key=f"dashboard_kpi_bottom_{ds_id}",
    )

    if st.session_state.get("_metric_dialog"):
        metric_information_dialog()

    st.subheader("Automated Insights")
    try:
        for line in an.insights(filtered):
            st.info(line)
    except Exception as ex:
        st.warning(f"Could not generate insights: {ex}")

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
            show(an.fig_dept_salary(filtered))
            show(an.fig_salary_dist(filtered))
        with b:
            show(an.fig_dept_perf(filtered))
            show(an.fig_salary_vs_perf(filtered))
    else:
        show(chart_functions[chart_choice](filtered))


# ============================================================
# EMPLOYEES
# ============================================================

def page_employees(df):
    banner("Employees", "Search and filter the active dataset")

    if df.empty:
        st.warning("No employee records are available.")
        return

    c1, c2, c3 = st.columns(3)
    departments = sorted(df["Department"].dropna().astype(str).unique().tolist())
    designations = sorted(df["Designation"].dropna().astype(str).unique().tolist())

    dept = c1.selectbox("Department", ["All"] + departments, key="emp_dept")
    desig = c2.selectbox("Designation", ["All"] + designations, key="emp_desig")

    exp = df["Experience_Years"]
    if exp.notna().any():
        lo, hi = int(exp.min()), int(exp.max())
        if lo == hi:
            c3.caption(f"Experience: {lo} years")
            exp_range = (lo, hi)
        else:
            exp_range = c3.slider("Experience (years)", lo, hi, (lo, hi), key="emp_experience")
    else:
        exp_range = None

    query = st.text_input("Search by ID or name")

    filtered = df
    if dept != "All":
        filtered = filtered[filtered["Department"].astype(str) == dept]
    if desig != "All":
        filtered = filtered[filtered["Designation"].astype(str) == desig]
    if exp_range is not None:
        filtered = filtered[filtered["Experience_Years"].between(*exp_range)]
    if query:
        filtered = filtered[
            filtered["Employee_ID"].astype(str).str.contains(query, case=False, na=False)
            | filtered["Name"].astype(str).str.contains(query, case=False, na=False)
        ]

    st.caption(f"{len(filtered)} employees")
    st.dataframe(filtered, hide_index=True, use_container_width=True)
    st.download_button("Download filtered records (CSV)", filtered.to_csv(index=False),
                       "employees_filtered.csv", mime="text/csv")


# ============================================================
# ANALYSIS
# ============================================================

def page_analysis(df):
    banner("Salary and Performance Analysis", "Statistics, experience trends and correlations")

    if df.empty:
        st.warning("No employee records are available.")
        return

    tab_salary, tab_perf, tab_corr = st.tabs(["Salary", "Performance", "Correlation"])

    with tab_salary:
        st.subheader("Salary Summary")
        st.dataframe(an.salary_summary(df).round(2).to_frame("Value"), use_container_width=True)
        show(an.fig_salary_dist(df))
        st.subheader("Salary by Experience")
        st.dataframe(an.by_experience(df), hide_index=True, use_container_width=True)
        show(an.fig_experience(df))

    with tab_perf:
        st.subheader("Performance Summary")
        st.dataframe(an.performance_summary(df).round(2).to_frame("Value"), use_container_width=True)
        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))

    with tab_corr:
        st.subheader("Correlation Matrix")
        st.dataframe(an.correlation(df).round(2), use_container_width=True)
        show(an.fig_corr(df))


# ============================================================
# DEPARTMENTS
# ============================================================

def page_departments(df):
    banner("Departments", "Employee count, salary and performance by department")

    if df.empty:
        st.warning("No employee records are available.")
        return

    st.dataframe(an.dept_table(df), hide_index=True, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        show(an.fig_dept_count(df))
    with col2:
        show(an.fig_dept_salary(df))


# ============================================================
# EXPORT
# ============================================================

def page_export(df, username):
    banner("Export", "Download results for the active dataset")

    if df.empty:
        st.warning("There is no data available to export.")
        return

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.download_button("Cleaned data (CSV)", df.to_csv(index=False), "cleaned_data.csv",
                           mime="text/csv", use_container_width=True)
    with col2:
        st.download_button("KPI summary (CSV)", pd.Series(an.kpis(df)).rename("value").to_csv(),
                           "kpi_summary.csv", mime="text/csv", use_container_width=True)
    with col3:
        st.download_button("Correlation matrix (CSV)", an.correlation(df).round(3).to_csv(),
                           "correlation_matrix.csv", mime="text/csv", use_container_width=True)
    with col4:
        st.download_button("Printable report (HTML)", an.report_html(df, username),
                           "report.html", mime="text/html", use_container_width=True)


# ============================================================
# ADMINISTRATION (limited to the admin's own company)
# ============================================================

def page_admin(org):
    banner("Administration", f"Users and recent activity for {org.title()}")

    st.subheader("Registered Users")
    users = db.list_users(org)
    if users:
        st.dataframe(pd.DataFrame(users), hide_index=True, use_container_width=True)
    else:
        st.info("No registered users were found.")

    st.subheader("Recent Activity")
    activity = db.recent_activity(org)
    if activity:
        st.dataframe(pd.DataFrame(activity), hide_index=True, use_container_width=True)
    else:
        st.info("No recent activity was found.")


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    user = st.session_state["user"]
    uid, org = user["id"], user["org"]

    pages = ["Dashboard", "Employees", "Analysis", "Departments", "Export", "Datasets"]
    if user.get("role") == "admin":
        pages.append("Administration")

    pending = st.session_state.pop("_pending_page_navigation", None)
    if pending in pages:
        st.session_state["page_navigation"] = pending

    with st.sidebar:
        st.markdown("## 📊 StaffMetrics")
        st.caption("Employee Salary & Performance")
        st.divider()
        st.markdown(f"### {user.get('full_name') or user['username']}")
        st.caption(f"{org.title()} · {user.get('role', 'user').title()}")
        st.divider()

        theme_selector(location="sidebar")
        st.divider()

        page = st.selectbox("Navigate to page", pages, key="page_navigation")
        st.divider()

        dataset_id = sidebar_dataset(uid)
        st.divider()

        if st.button("Sign out", use_container_width=True):
            db.log_activity(uid, "signed out")
            for key in ("user", "active_dataset_id", "_metric_dialog"):
                st.session_state.pop(key, None)
            st.rerun()

    # Pages that don't need a dataset
    if page == "Datasets":
        page_datasets(uid)
        return
    if page == "Administration":
        if user.get("role") == "admin":
            page_admin(org)
        else:
            st.error("You do not have permission to access this page.")
        return

    if dataset_id is None:
        banner("No dataset selected", "")
        st.info("Upload a CSV under Datasets to see your analysis.")
        return

    text = db.load_dataset(dataset_id, uid)
    if text is None:
        st.error("This dataset could not be loaded. Choose another one or upload it again.")
        return

    try:
        df = analyse(text)
    except Exception as ex:
        st.error(f"This dataset could not be analysed: {ex}")
        return

    if page == "Dashboard":
        page_dashboard(df, dataset_id)
    elif page == "Employees":
        page_employees(df)
    elif page == "Analysis":
        page_analysis(df)
    elif page == "Departments":
        page_departments(df)
    elif page == "Export":
        page_export(df, user["username"])


# ============================================================
# ENTRY POINT
# ============================================================

if "user" in st.session_state:
    main()
else:
    auth_page()
