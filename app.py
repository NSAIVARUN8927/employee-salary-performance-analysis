import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import analytics as an, auth, database as db, sql_queries as Q

st.set_page_config(page_title="Employee Salary & Performance Analysis", page_icon="📊", layout="wide")
db.init_db()
CSV = "data/employee_salary_performance.csv"
if not db.is_seeded():
    db.seed_database(an.prepare(an.load_data(CSV))[0])
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] {font-family: 'IBM Plex Sans', sans-serif;}
[data-testid="stSidebar"] {background: #14213d;}
[data-testid="stSidebar"] * {color: #e6ebf5;}
.block-container {padding-top: 1.6rem; max-width: 1250px;}
h1, h2, h3 {color: #14213d; font-weight: 600;}
.banner {background: #14213d; color: #fff; padding: 22px 28px; border-radius: 6px; margin-bottom: 20px;}
.banner h1 {color: #fff; margin: 0; font-size: 1.7rem;} .banner p {margin: 4px 0 0; color: #b9c4dc;}
.kpi {background: #fff; border: 1px solid #dde3ee; border-top: 3px solid #0f766e; border-radius: 6px; padding: 14px 16px;}
.kpi span {color: #5b6b82; font-size: 0.85rem;} .kpi b {display: block; font-size: 1.55rem; color: #14213d; font-weight: 600;}
</style>""", unsafe_allow_html=True)


def banner(title, subtitle=""):
    st.markdown(f'<div class="banner"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def kpis(items):
    for col, (label, value) in zip(st.columns(len(items)), items):
        col.markdown(f'<div class="kpi"><span>{label}</span><b>{value}</b></div>', unsafe_allow_html=True)
def auth_page():
    banner("StaffMetrics", "Employee salary and performance analytics for HR teams")
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        t_in, t_up = st.tabs(["Sign in", "Create account"])
        with t_in, st.form("login_form"):
            u, p = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("Sign in"):
                user = auth.login(u, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                st.error("The username or password is incorrect.")
        with t_up, st.form("register_form"):
            name, email = st.text_input("Full name"), st.text_input("Email")
            uname = st.text_input("Choose a username")
            p1, p2 = st.text_input("Password (8+ characters)", type="password"), st.text_input("Confirm password", type="password")
            if st.form_submit_button("Create account"):
                if p1 != p2:
                    st.error("The passwords do not match.")
                else:
                    ok, msg = auth.register(uname, email, name, p1)
                    (st.success if ok else st.error)(msg)
def show(fig):
    st.pyplot(fig)
    plt.close(fig)


def page_dashboard(df):
    banner("Executive dashboard", f"Welcome, {st.session_state.user['full_name'] or st.session_state.user['username']}")
    depts = sorted(df["Department"].unique())
    f = df[df["Department"].isin(st.multiselect("Departments", depts, default=depts))]
    if f.empty:
        st.warning("Select at least one department to see results.")
        return
    k = an.kpis(f)
    kpis([("Employees", k["total_employees"]), ("Average salary", f"{k['average_salary']:,.0f}"),
          ("Median salary", f"{k['median_salary']:,.0f}"), ("Minimum salary", f"{k['minimum_salary']:,.0f}")])
    st.write("")
    kpis([("Maximum salary", f"{k['maximum_salary']:,.0f}"), ("Average performance", f"{k['average_performance']:.2f}"),
          ("Maximum performance", f"{k['maximum_performance']:.2f}")])
    st.subheader("Automated insights")
    for line in an.insights(f):
        st.info(line)
    a, b = st.columns(2)
    with a:
        show(an.fig_dept_salary(f))
        show(an.fig_salary_dist(f))
    with b:
        show(an.fig_dept_perf(f))
        show(an.fig_salary_vs_perf(f))


def manage_employees(df):
    uid = st.session_state.user["id"]
    with st.expander("Add an employee"), st.form("add_emp"):
        c = st.columns(3)
        e = {"Employee_ID": c[0].text_input("Employee ID"), "Name": c[1].text_input("Name"), "Age": c[2].number_input("Age", 18, 70, 30),
             "Gender": c[0].selectbox("Gender", ["Female", "Male"]), "Department": c[1].selectbox("Department", sorted(df["Department"].unique())),
             "Designation": c[2].text_input("Designation"), "Experience_Years": c[0].number_input("Experience (years)", 0, 45, 3),
             "Joining_Year": c[1].number_input("Joining year", 1990, 2030, 2024), "Basic_Salary": c[2].number_input("Basic salary", 1.0, 1e7, 50000.0),
             "Bonus": c[0].number_input("Bonus", 0.0, 1e6, 0.0), "Performance_Score": c[1].number_input("Performance score (0-5)", 0.0, 5.0, 3.0, 0.5)}
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
    c1, c2, c3 = st.columns(3)
    dept = c1.multiselect("Department", sorted(df["Department"].unique()))
    role = c2.multiselect("Designation", sorted(df["Designation"].astype(str).unique()))
    lo, hi = int(df["Experience_Years"].min()), int(df["Experience_Years"].max())
    exp = c3.slider("Experience (years)", lo, max(hi, lo + 1), (lo, max(hi, lo + 1)))
    q = st.text_input("Search by ID or name")
    f = df[df["Experience_Years"].between(*exp)]
    if dept:
        f = f[f["Department"].isin(dept)]
    if role:
        f = f[f["Designation"].astype(str).isin(role)]
    if q:
        f = f[f["Employee_ID"].astype(str).str.contains(q, case=False) | f["Name"].astype(str).str.contains(q, case=False)]
    st.caption(f"{len(f)} employees")
    st.dataframe(f, hide_index=True)
    st.download_button("Download filtered records (CSV)", f.to_csv(index=False), "employees_filtered.csv")
    if is_db and st.session_state.user["role"] == "admin":
        manage_employees(df)
def page_analysis(df):
    banner("Salary and performance analysis", "Statistics, experience trends and correlations")
    t1, t2, t3 = st.tabs(["Salary", "Performance", "Correlation"])
    with t1:
        st.dataframe(an.salary_summary(df).round(2).to_frame("Value"))
        show(an.fig_salary_dist(df))
        st.subheader("By experience")
        st.dataframe(an.by_experience(df), hide_index=True)
        show(an.fig_experience(df))
    with t2:
        st.dataframe(an.performance_summary(df).round(2).to_frame("Value"))
        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))
    with t3:
        st.dataframe(an.correlation(df).round(2))
        show(an.fig_corr(df))


def page_departments(df):
    banner("Departments", "Employee count, salary and performance by department")
    st.dataframe(an.dept_table(df), hide_index=True)
    a, b = st.columns(2)
    with a:
        show(an.fig_dept_count(df))
    with b:
        show(an.fig_dept_salary(df))


def page_sql():
    banner("SQL explorer", "Run the prepared queries or write your own SELECT")
    titles = [f"Q{i}. {t}" for i, (t, _) in enumerate(Q.QUERIES, 1)]
    pick = st.selectbox("Prepared query", titles)
    sql = st.text_area("SQL (read-only)", Q.QUERIES[titles.index(pick)][1], height=130)
    if st.button("Run query"):
        if not sql.strip().lower().startswith("select"):
            st.error("Only SELECT statements can be run here.")
        else:
            try:
                st.dataframe(db.run_query(sql), hide_index=True)
            except Exception as ex:
                st.error(f"The query failed: {ex}")


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
    c = st.columns(4)
    c[0].download_button("Cleaned data (CSV)", df.to_csv(index=False), "Employee_Salary_Performance_Cleaned.csv")
    c[1].download_button("KPI summary (CSV)", pd.Series(an.kpis(df)).rename("value").to_csv(), "kpi_summary.csv")
    c[2].download_button("Correlation matrix (CSV)", an.correlation(df).round(3).to_csv(), "correlation_matrix.csv")
    c[3].download_button("Printable report (HTML)", an.report_html(df, st.session_state.user["username"]), "report.html", mime="text/html")


def page_admin():
    banner("Administration", "Registered users and recent activity")
    st.dataframe(pd.DataFrame(db.list_users()), hide_index=True)
    st.dataframe(pd.DataFrame(db.recent_activity()), hide_index=True)
def main():
    user = st.session_state.user
    pages = ["Dashboard", "Employees", "Analysis", "Departments", "SQL explorer", "Upload and export"]
    if user["role"] == "admin":
        pages.append("Administration")
    with st.sidebar:
        st.markdown(f"### {user['full_name'] or user['username']}")
        st.caption(f"{user['role'].title()} account")
        page = st.radio("Go to", pages)
        up = st.session_state.get("upload")
        src = st.selectbox("Data source", ["Employee database"] + (["Uploaded file"] if up is not None else []))
        if st.button("Sign out"):
            db.log_activity(user["id"], "signed out")
            del st.session_state["user"]
            st.rerun()
    is_db = src == "Employee database"
    df = db.employee_frame() if is_db else up
    if page == "Dashboard": page_dashboard(df)
    elif page == "Employees": page_employees(df, is_db)
    elif page == "Analysis": page_analysis(df)
    elif page == "Departments": page_departments(df)
    elif page == "SQL explorer": page_sql()
    elif page == "Upload and export": page_data(df)
    else: page_admin()


if "user" not in st.session_state:
    auth_page()
else:
    main()
