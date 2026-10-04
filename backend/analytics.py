"""Data analysis for the Employee Salary & Performance project."""
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

REQUIRED = ["Employee_ID", "Department", "Experience_Years", "Salary", "Performance_Rating"]
NAVY, TEAL = "#14213d", "#0f766e"


def load_data(source):
    df = pd.read_csv(source)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"The file is missing required columns: {', '.join(missing)}")
    return df
def clean_data(raw):
    df, log = raw.copy(), []
    n = len(df)
    df = df.drop_duplicates().copy()
    log.append(f"Removed {n - len(df)} duplicate records")
    text = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    for c in text:
        df[c] = df[c].astype("string").str.strip()
    num = df.select_dtypes(include=np.number).columns
    log.append(f"Filled {int(df[num].isna().sum().sum())} missing numeric values with the median")
    for c in num:
        df[c] = df[c].fillna(df[c].median())
    log.append(f"Filled {int(df[text].isna().sum().sum())} missing text values with 'Unknown'")
    for c in text:
        df[c] = df[c].fillna("Unknown")
    return df, log
MAP = {"Employee_Name": "Name", "Job_Role": "Designation", "Salary": "Basic_Salary", "Performance_Rating": "Performance_Score"}
STD = ["Employee_ID", "Name", "Age", "Gender", "Designation", "Experience_Years", "Joining_Year", "Department",
       "Basic_Salary", "Bonus", "Total_Salary", "Effective_Date", "Performance_Score"]


def standardise(df):
    d = df.rename(columns=MAP).copy()
    d["Employee_ID"] = d["Employee_ID"].astype(str)
    for col, default in {"Age": np.nan, "Gender": "Unknown", "Designation": "Unknown", "Bonus": 0.0}.items():
        if col not in d:
            d[col] = default
    if "Name" not in d:
        d["Name"] = d["Employee_ID"]
    jd = pd.to_datetime(d["Joining_Date"], errors="coerce") if "Joining_Date" in d else pd.Series(pd.NaT, index=d.index)
    d["Joining_Year"] = jd.dt.year.astype("Int64")
    d["Effective_Date"] = jd.dt.strftime("%Y-%m-%d")
    d["Total_Salary"] = d["Basic_Salary"] + d["Bonus"]
    return d[STD].reset_index(drop=True)


def prepare(raw):
    clean, log = clean_data(raw)
    return standardise(clean), log
def _summary(s, label):
    s = pd.to_numeric(s, errors="coerce").dropna()
    return pd.Series({f"Average {label}": s.mean(), f"Median {label}": s.median(), f"Minimum {label}": s.min(),
                      f"Maximum {label}": s.max(), f"{label} Std. Deviation": s.std()})


def salary_summary(df):
    return _summary(df["Basic_Salary"], "Salary")


def performance_summary(df):
    return _summary(df["Performance_Score"], "Performance")


def dept_salary(df):
    return df.groupby("Department")["Basic_Salary"].mean().sort_values(ascending=False)


def dept_performance(df):
    return df.groupby("Department")["Performance_Score"].mean().sort_values(ascending=False)


def dept_table(df):
    g = df.groupby("Department").agg(Employees=("Employee_ID", "count"), Avg_Salary=("Basic_Salary", "mean"),
                                     Avg_Performance=("Performance_Score", "mean"), Total_Bonus=("Bonus", "sum"))
    return g.round(2).sort_values("Avg_Salary", ascending=False).reset_index()


def by_experience(df):
    bands = pd.cut(df["Experience_Years"], [-1, 2, 5, 10, 100], labels=["0-2 years", "3-5 years", "6-10 years", "10+ years"])
    g = df.groupby(bands, observed=True).agg(Employees=("Employee_ID", "count"), Avg_Salary=("Basic_Salary", "mean"),
                                             Avg_Performance=("Performance_Score", "mean"))
    return g.round(2).reset_index().rename(columns={"Experience_Years": "Experience"})
def correlation(df):
    return df.select_dtypes(include=np.number).corr()


def kpis(df):
    s, p = df["Basic_Salary"], df["Performance_Score"]
    return {"total_employees": int(len(df)), "average_salary": round(float(s.mean()), 2), "median_salary": round(float(s.median()), 2),
            "minimum_salary": round(float(s.min()), 2), "maximum_salary": round(float(s.max()), 2),
            "average_performance": round(float(p.mean()), 2), "maximum_performance": round(float(p.max()), 2)}


def insights(df):
    k, ds, dp = kpis(df), dept_salary(df), dept_performance(df)
    c1, c2 = df["Basic_Salary"].corr(df["Experience_Years"]), df["Basic_Salary"].corr(df["Performance_Score"])
    word = lambda c: "strongly" if abs(c) > 0.6 else "moderately" if abs(c) > 0.3 else "weakly"
    return [f"The average salary is {k['average_salary']:,.0f}, ranging from {k['minimum_salary']:,.0f} to {k['maximum_salary']:,.0f}.",
            f"{ds.index[0]} has the highest average salary ({ds.iloc[0]:,.0f}); {ds.index[-1]} has the lowest ({ds.iloc[-1]:,.0f}).",
            f"{dp.index[0]} has the best average performance score ({dp.iloc[0]:.2f}); {dp.index[-1]} has the lowest ({dp.iloc[-1]:.2f}).",
            f"Experience and salary are {word(c1)} related (correlation {c1:.2f}).",
            f"Performance and salary are {word(c2)} related (correlation {c2:.2f}).",
            f"{(df['Performance_Score'] >= 4).mean() * 100:.1f}% of employees have a performance score of 4 or higher."]
def _fig(title, xl, yl, draw, size=(7, 3.8)):
    fig, ax = plt.subplots(figsize=size)
    draw(ax)
    ax.set(title=title, xlabel=xl, ylabel=yl)
    fig.tight_layout()
    return fig


def fig_salary_dist(df):
    return _fig("Salary distribution", "Salary", "Employees", lambda ax: sns.histplot(df["Basic_Salary"], kde=True, color=TEAL, ax=ax))


def fig_perf_dist(df):
    return _fig("Performance score distribution", "Score", "Employees", lambda ax: sns.countplot(x=df["Performance_Score"].round().astype(int), color=NAVY, ax=ax))


def fig_dept_salary(df):
    s = dept_salary(df)
    return _fig("Average salary by department", "Department", "Average salary", lambda ax: sns.barplot(x=s.index, y=s.values, color=NAVY, ax=ax))


def fig_dept_perf(df):
    s = dept_performance(df)
    return _fig("Average performance by department", "Department", "Average score", lambda ax: sns.barplot(x=s.index, y=s.values, color=TEAL, ax=ax))


def fig_dept_count(df):
    return _fig("Employees by department", "Employees", "", lambda ax: sns.countplot(data=df, y="Department", color=TEAL, ax=ax))


def fig_salary_vs_perf(df):
    return _fig("Salary vs performance", "Salary", "Performance score", lambda ax: sns.scatterplot(data=df, x="Basic_Salary", y="Performance_Score", hue="Department", ax=ax))


def fig_experience(df):
    return _fig("Experience vs salary", "Experience (years)", "Salary", lambda ax: sns.scatterplot(data=df, x="Experience_Years", y="Basic_Salary", hue="Department", ax=ax))


def fig_corr(df):
    return _fig("Correlation heatmap", "", "", lambda ax: sns.heatmap(correlation(df), annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax, annot_kws={"size": 7}), size=(8, 6))
def report_html(df, user):
    rows = "".join(f"<tr><td>{n.replace('_', ' ').title()}</td><td>{v:,}</td></tr>" for n, v in kpis(df).items())
    items = "".join(f"<li>{i}</li>" for i in insights(df))
    return ("<html><head><meta charset='utf-8'><title>Employee report</title><style>body{font-family:Arial;margin:40px;color:#14213d}"
            "table{border-collapse:collapse}td,th{border:1px solid #ccd;padding:6px 12px;text-align:left}th{background:#e8eefc}"
            "@media print{button{display:none}}</style></head><body>"
            f"<h1>Employee Salary &amp; Performance Report</h1><p>Prepared for {user}</p>"
            f"<h2>Key indicators</h2><table>{rows}</table><h2>Automated insights</h2><ul>{items}</ul>"
            f"<h2>Departments</h2>{dept_table(df).to_html(index=False)}<br><button onclick='window.print()'>Print report</button></body></html>")
