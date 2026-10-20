import io
import re

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import analytics as an, auth, database as db


# ============================================================
# SETUP
# ============================================================

st.set_page_config(page_title="StaffMetrics", page_icon="📊", layout="wide")
db.init_db()

PAGES = ["Dashboard", "Employees", "Analysis", "Departments", "Datasets", "Export"]

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; max-width: 1200px; }
    .hero {
        padding: 1.1rem 1.4rem; border-radius: 12px; margin-bottom: 1.2rem;
        background: linear-gradient(135deg, #0f766e 0%, #14213d 100%); color: #ffffff;
    }
    .hero h2 { margin: 0; color: #ffffff; font-weight: 600; }
    .hero p { margin: 0.3rem 0 0; opacity: 0.85; }
    .insight {
        border-left: 4px solid #0f766e; padding: 0.5rem 0.9rem; margin: 0.4rem 0;
        border-radius: 6px; background: rgba(15, 118, 110, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def hero(title, subtitle=""):
    st.markdown(f'<div class="hero"><h2>{title}</h2><p>{subtitle}</p></div>', unsafe_allow_html=True)


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


def slider_range(label, series, key, decimals=0):
    lo, hi = float(series.min()), float(series.max())
    if lo == hi:
        st.caption(f"{label}: {lo:,.{decimals}f}")
        return lo, hi
    return st.slider(label, lo, hi, (lo, hi), key=key)


def experience_inputs(df, key):
    """'From' and 'To' inputs, limited to the min and max in the uploaded data."""
    exp = df["Experience_Years"]
    if not exp.notna().any():
        return None
    lo, hi = int(exp.min()), int(exp.max())
    a, b = st.columns(2)
    start = a.number_input("Experience from (years)", lo, hi, lo, key=f"{key}_from")
    end = b.number_input("Experience to (years)", lo, hi, hi, key=f"{key}_to")
    return start, end


def dept_and_designation_options(df):
    depts = ["All"] + sorted(df["Department"].dropna().astype(str).unique().tolist())
    desigs = ["All"] + sorted(df["Designation"].dropna().astype(str).unique().tolist())
    return depts, desigs


# ============================================================
# SIGN IN AND CREATE ACCOUNT
# ============================================================

def auth_page():
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown("## 📊 StaffMetrics")
        st.caption("Employee salary and performance analysis for your company.")
        sign_in, create = st.tabs(["Sign in", "Create account"])

        with sign_in:
            with st.form("sign_in_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign in", type="primary", width="stretch")

            if submitted:
                user = auth.login(username, password) if username.strip() and password else None
                if user:
                    st.session_state["user"] = user
                    db.log_activity(user["id"], "signed in")
                    st.rerun()
                st.error("Incorrect username or password.")

        with create:
            with st.form("register_form"):
                full_name = st.text_input("Full name")
                email = st.text_input("Email")
                org = st.text_input(
                    "Company or industry",
                    help="Users from the same company share one admin and see only their own company's users.",
                )
                username = st.text_input("Username", help="3-20 letters, numbers or underscores")
                pw1 = st.text_input("Password", type="password", help="At least 8 characters")
                pw2 = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create account", type="primary", width="stretch")

            if submitted:
                if not all([full_name.strip(), email.strip(), org.strip(), username.strip(), pw1, pw2]):
                    st.error("Please fill in every field.")
                elif pw1 != pw2:
                    st.error("The passwords do not match.")
                else:
                    ok, message = auth.register(username, email, full_name, org, pw1)
                    (st.success if ok else st.error)(message)


# ============================================================
# SIDEBAR DATASET SELECTOR
# ============================================================

def dataset_selector(uid):
    rows = db.list_datasets(uid)
    if not rows:
        st.caption("No dataset yet. Upload one on the Datasets page.")
        return None

    names = {r["id"]: r["name"] for r in rows}
    ids = list(names)
    if st.session_state.get("active_dataset_id") not in ids:
        st.session_state["active_dataset_id"] = ids[0]

    return st.selectbox("Active dataset", ids, format_func=names.get, key="active_dataset_id")


# ============================================================
# DATASETS PAGE
# ============================================================

def datasets_page(uid):
    hero("Datasets", "Upload an employee and salary CSV for your company")

    uploaded = st.file_uploader("CSV file", type=["csv"])
    default_name = uploaded.name.rsplit(".", 1)[0] if uploaded else ""
    name = st.text_input("Dataset name", value=default_name)

    if uploaded is not None and st.button("Save and analyse", type="primary"):
        raw = read_text(uploaded.getvalue())
        try:
            an.prepare(an.load_data(io.StringIO(raw)))  # validate before saving
        except Exception as ex:
            st.error(f"This file could not be analysed: {ex}")
        else:
            new_id = db.save_dataset(uid, name.strip() or uploaded.name, raw)
            db.log_activity(uid, f"uploaded dataset {new_id}")
            st.session_state["active_dataset_id"] = new_id
            st.rerun()

    st.subheader("Saved datasets")
    rows = db.list_datasets(uid)
    if not rows:
        st.info("No datasets saved yet.")
        return

    st.dataframe(
        pd.DataFrame(rows)[["name", "created_at"]].rename(columns={"name": "Name", "created_at": "Uploaded"}),
        hide_index=True,
        width="stretch",
    )

    names = {r["id"]: r["name"] for r in rows}
    target = st.selectbox("Delete a dataset", list(names), format_func=names.get, key="delete_target")
    confirm = st.checkbox("I understand this cannot be undone", key="delete_confirm")
    if st.button("Delete dataset", disabled=not confirm):
        db.delete_dataset(target, uid)
        db.log_activity(uid, f"deleted dataset {target}")
        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(df, ds_id):
    user = st.session_state["user"]
    hero("Executive Dashboard", f"Welcome, {user.get('full_name') or user['username']}")

    required = ["Department", "Designation", "Basic_Salary", "Performance_Score"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error("The dataset is missing required columns: " + ", ".join(missing))
        return

    depts, desigs = dept_and_designation_options(df)

    f1, f2, f3 = st.columns(3)
    dept = f1.selectbox("Department", depts, key=f"dept_{ds_id}")
    desig = f2.selectbox("Designation", desigs, key=f"desig_{ds_id}")
    chart_choice = f3.selectbox(
        "Chart to display",
        ["All charts", "Department-wise salary", "Salary distribution",
         "Department-wise performance", "Salary vs. performance"],
        key=f"chart_{ds_id}",
    )

    exp_range = experience_inputs(df, f"dash_{ds_id}")
    sal_range = slider_range("Basic salary range", df["Basic_Salary"], f"sal_{ds_id}")
    perf_range = slider_range("Performance score", df["Performance_Score"], f"perf_{ds_id}", decimals=2)

    mask = df["Basic_Salary"].between(*sal_range) & df["Performance_Score"].between(*perf_range)
    if dept != "All":
        mask &= df["Department"].astype(str) == dept
    if desig != "All":
        mask &= df["Designation"].astype(str) == desig
    if exp_range is not None:
        mask &= df["Experience_Years"].between(*exp_range)

    f = df[mask]
    if f.empty:
        st.warning("No employees match these filters. Check the experience range and other selections.")
        return

    st.caption(f"Showing {len(f):,} of {len(df):,} employee records.")

    k = an.kpis(f)
    row1 = st.columns(4)
    row1[0].metric("Employees", f"{k['total_employees']:,}")
    row1[1].metric("Average salary", f"{k['average_salary']:,.0f}")
    row1[2].metric("Median salary", f"{k['median_salary']:,.0f}")
    row1[3].metric("Minimum salary", f"{k['minimum_salary']:,.0f}")

    row2 = st.columns(3)
    row2[0].metric("Maximum salary", f"{k['maximum_salary']:,.0f}")
    row2[1].metric("Average performance", f"{k['average_performance']:.2f}")
    row2[2].metric("Maximum performance", f"{k['maximum_performance']:.2f}")

    st.subheader("Automated insights")
    try:
        for line in an.insights(f):
            st.markdown(f'<div class="insight">{line}</div>', unsafe_allow_html=True)
    except Exception as ex:
        st.warning(f"Could not generate insights: {ex}")

    st.subheader("Charts")
    charts = {
        "Department-wise salary": an.fig_dept_salary,
        "Salary distribution": an.fig_salary_dist,
        "Department-wise performance": an.fig_dept_perf,
        "Salary vs. performance": an.fig_salary_vs_perf,
    }
    if chart_choice == "All charts":
        a, b = st.columns(2)
        with a:
            show(an.fig_dept_salary(f))
            show(an.fig_salary_dist(f))
        with b:
            show(an.fig_dept_perf(f))
            show(an.fig_salary_vs_perf(f))
    else:
        show(charts[chart_choice](f))


# ============================================================
# EMPLOYEES
# ============================================================

def employees_page(df):
    hero("Employees", "Search and filter the active dataset")

    depts, desigs = dept_and_designation_options(df)
    c1, c2, c3 = st.columns(3)
    dept = c1.selectbox("Department", depts, key="emp_dept")
    desig = c2.selectbox("Designation", desigs, key="emp_desig")
    query = c3.text_input("Search by ID or name")

    exp_range = experience_inputs(df, "emp")

    f = df
    if dept != "All":
        f = f[f["Department"].astype(str) == dept]
    if desig != "All":
        f = f[f["Designation"].astype(str) == desig]
    if exp_range is not None:
        f = f[f["Experience_Years"].between(*exp_range)]
    if query:
        f = f[
            f["Employee_ID"].astype(str).str.contains(query, case=False, na=False)
            | f["Name"].astype(str).str.contains(query, case=False, na=False)
        ]

    st.caption(f"{len(f)} employees")
    st.dataframe(f, hide_index=True, width="stretch")
    st.download_button("Download filtered records (CSV)", f.to_csv(index=False),
                       "employees_filtered.csv", mime="text/csv")


# ============================================================
# ANALYSIS
# ============================================================

def analysis_page(df):
    hero("Salary and Performance Analysis", "Statistics, experience trends and correlations")

    tab_salary, tab_perf, tab_corr = st.tabs(["Salary", "Performance", "Correlation"])

    with tab_salary:
        st.dataframe(an.salary_summary(df).round(2).to_frame("Value"), width="stretch")
        show(an.fig_salary_dist(df))
        st.subheader("By experience")
        st.dataframe(an.by_experience(df), hide_index=True, width="stretch")
        show(an.fig_experience(df))

    with tab_perf:
        st.dataframe(an.performance_summary(df).round(2).to_frame("Value"), width="stretch")
        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))

    with tab_corr:
        st.dataframe(an.correlation(df).round(2), width="stretch")
        show(an.fig_corr(df))


# ============================================================
# DEPARTMENTS
# ============================================================

def departments_page(df):
    hero("Departments", "Employee count, salary and performance by department")
    st.dataframe(an.dept_table(df), hide_index=True, width="stretch")
    a, b = st.columns(2)
    with a:
        show(an.fig_dept_count(df))
    with b:
        show(an.fig_dept_salary(df))


# ============================================================
# EXPORT
# ============================================================

def export_page(df, username):
    hero("Export", "Download results for the active dataset")
    c1, c2, c3, c4 = st.columns(4)
    c1.download_button("Cleaned data (CSV)", df.to_csv(index=False),
                       "cleaned_data.csv", mime="text/csv", width="stretch")
    c2.download_button("KPI summary (CSV)", pd.Series(an.kpis(df)).rename("value").to_csv(),
                       "kpi_summary.csv", mime="text/csv", width="stretch")
    c3.download_button("Correlation matrix (CSV)", an.correlation(df).round(3).to_csv(),
                       "correlation_matrix.csv", mime="text/csv", width="stretch")
    c4.download_button("Printable report (HTML)", an.report_html(df, username),
                       "report.html", mime="text/html", width="stretch")


# ============================================================
# ADMINISTRATION (own company only, no emails or user IDs)
# ============================================================

def admin_page(org):
    hero("Administration", f"Users and recent activity for {org.title()}")

    st.subheader("Registered users")
    users = db.list_users(org)
    if users:
        st.dataframe(pd.DataFrame(users), hide_index=True, width="stretch")
    else:
        st.info("No users found.")

    st.subheader("Recent activity")
    activity = db.recent_activity(org)
    if activity:
        st.dataframe(pd.DataFrame(activity), hide_index=True, width="stretch")
    else:
        st.info("No activity recorded yet.")


# ============================================================
# MAIN
# ============================================================

def main():
    user = st.session_state["user"]
    uid, org = user["id"], user["org"]
    pages = PAGES + (["Administration"] if user["role"] == "admin" else [])

    with st.sidebar:
        st.markdown(f"### {user.get('full_name') or user['username']}")
        st.caption(f"{org.title()} · {user['role'].title()}")
        st.divider()
        page = st.radio("Navigate", pages, key="nav")
        st.divider()
        ds_id = dataset_selector(uid)
        st.divider()
        if st.button("Sign out", width="stretch"):
            db.log_activity(uid, "signed out")
            st.session_state.clear()
            st.rerun()

    if page == "Datasets":
        datasets_page(uid)
        return

    if page == "Administration":
        admin_page(org)
        return

    if ds_id is None:
        hero("No dataset selected")
        st.info("Upload a CSV on the Datasets page to see your analysis.")
        return

    text = db.load_dataset(ds_id, uid)
    if text is None:
        st.error("This dataset could not be loaded. Select another one or upload it again.")
        return

    try:
        df = analyse(text)
    except Exception as ex:
        st.error(f"This dataset could not be analysed: {ex}")
        return

    if page == "Dashboard":
        dashboard(df, ds_id)
    elif page == "Employees":
        employees_page(df)
    elif page == "Analysis":
        analysis_page(df)
    elif page == "Departments":
        departments_page(df)
    elif page == "Export":
        export_page(df, user["username"])


# ============================================================
# ENTRY POINT
# ============================================================

if "user" in st.session_state:
    main()
else:
    auth_page()
