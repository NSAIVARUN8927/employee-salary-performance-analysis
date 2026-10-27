
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

REQUIRED = [
    "Employee_ID",
    "Department",
    "Experience_Years",
    "Salary",
    "Performance_Rating"
]

NAVY, TEAL = "#14213d", "#0f766e"


# ============================================================
# DATA LOADING
# ============================================================

def load_data(source):
    df = pd.read_csv(source)

    missing = [c for c in REQUIRED if c not in df.columns]

    if missing:
        raise ValueError(
            f"The file is missing required columns: {', '.join(missing)}"
        )

    return df


# ============================================================
# DATA CLEANING
# ============================================================

def clean_data(raw):
    df, log = raw.copy(), []
    n = len(df)

    df = df.drop_duplicates().copy()
    log.append(f"Removed {n - len(df)} duplicate records")

    text = [
        c for c in df.columns
        if not pd.api.types.is_numeric_dtype(df[c])
    ]

    for c in text:
        df[c] = df[c].astype("string").str.strip()

    num = df.select_dtypes(include=np.number).columns

    log.append(
        f"Filled {int(df[num].isna().sum().sum())} missing numeric values with the median"
    )

    for c in num:
        median = df[c].median()

        if pd.notna(median):
            df[c] = df[c].fillna(median)

    log.append(
        f"Filled {int(df[text].isna().sum().sum())} missing text values with 'Unknown'"
    )

    for c in text:
        df[c] = df[c].fillna("Unknown")

    return df, log


# ============================================================
# DATA STANDARDISATION
# ============================================================

MAP = {
    "Employee_Name": "Name",
    "Job_Role": "Designation",
    "Salary": "Basic_Salary",
    "Performance_Rating": "Performance_Score"
}

STD = [
    "Employee_ID",
    "Name",
    "Age",
    "Gender",
    "Designation",
    "Experience_Years",
    "Joining_Year",
    "Department",
    "Basic_Salary",
    "Bonus",
    "Total_Salary",
    "Effective_Date",
    "Performance_Score"
]


def standardise(df):
    d = df.rename(columns=MAP).copy()

    d["Employee_ID"] = d["Employee_ID"].astype(str)

    for col, default in {
        "Age": np.nan,
        "Gender": "Unknown",
        "Designation": "Unknown",
        "Bonus": 0.0
    }.items():
        if col not in d.columns:
            d[col] = default

    if "Name" not in d.columns:
        d["Name"] = d["Employee_ID"]

    jd = (
        pd.to_datetime(d["Joining_Date"], errors="coerce")
        if "Joining_Date" in d.columns
        else pd.Series(pd.NaT, index=d.index)
    )

    d["Joining_Year"] = jd.dt.year.astype("Int64")
    d["Effective_Date"] = jd.dt.strftime("%Y-%m-%d")

    # Preserve existing total salary calculations.
    d["Total_Salary"] = d["Basic_Salary"] + d["Bonus"]

    # Keep the normalized columns required by the existing SQLite application,
    # plus every original dataset field needed for notebook-style analysis.
    extra_cols = [c for c in d.columns if c not in STD]
    return d[STD + extra_cols].reset_index(drop=True)


def prepare(raw):
    clean, log = clean_data(raw)
    return standardise(clean), log


# ============================================================
# STATISTICAL SUMMARIES
# ============================================================


def _summary(s, label):
    s = pd.to_numeric(s, errors="coerce").dropna()

    return pd.Series({
        "Average": s.mean(),
        "Median": s.median(),
        "Minimum": s.min(),
        "Maximum": s.max(),
        "Std. Deviation": s.std()
    }, name=label)


def salary_summary(df):
    return _summary(df["Basic_Salary"], "Salary")


def performance_summary(df):
    return _summary(df["Performance_Score"], "Performance")




# ============================================================
# DEPARTMENT ANALYSIS
# ============================================================

def dept_salary(df):
    return (
        df.groupby("Department")["Basic_Salary"]
        .mean()
        .sort_values(ascending=False)
    )


def dept_performance(df):
    return (
        df.groupby("Department")["Performance_Score"]
        .mean()
        .sort_values(ascending=False)
    )


def dept_table(df):
    """
    Department summary without the Bonus column.

    Returns:
    - Department
    - Employees
    - Avg_Salary
    - Avg_Performance
    """

    g = df.groupby("Department").agg(
        Employees=("Employee_ID", "count"),
        Avg_Salary=("Basic_Salary", "mean"),
        Avg_Performance=("Performance_Score", "mean")
    )

    return (
        g.round(2)
        .sort_values("Avg_Salary", ascending=False)
        .reset_index()
    )


# ============================================================
# EXPERIENCE ANALYSIS
# ============================================================

def by_experience(df):
    bands = pd.cut(
        df["Experience_Years"],
        [-1, 2, 5, 10, 100],
        labels=[
            "0-2 years",
            "3-5 years",
            "6-10 years",
            "10+ years"
        ]
    )

    g = df.groupby(bands, observed=True).agg(
        Employees=("Employee_ID", "count"),
        Avg_Salary=("Basic_Salary", "mean"),
        Avg_Performance=("Performance_Score", "mean")
    )

    return (
        g.round(2)
        .reset_index()
        .rename(columns={"Experience_Years": "Experience"})
    )


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

def correlation(df):
    return df.select_dtypes(include=np.number).corr()


# ============================================================
# KEY PERFORMANCE INDICATORS
# ============================================================

def kpis(df):
    s = df["Basic_Salary"]
    p = df["Performance_Score"]

    return {
        "total_employees": int(len(df)),
        "average_salary": round(float(s.mean()), 2),
        "median_salary": round(float(s.median()), 2),
        "minimum_salary": round(float(s.min()), 2),
        "maximum_salary": round(float(s.max()), 2),
        "average_performance": round(float(p.mean()), 2),
        "maximum_performance": round(float(p.max()), 2)
    }


# ============================================================
# AUTOMATED INSIGHTS
# ============================================================

def insights(df):
    k = kpis(df)
    ds = dept_salary(df)
    dp = dept_performance(df)

    c1 = df["Basic_Salary"].corr(df["Experience_Years"])
    c2 = df["Basic_Salary"].corr(df["Performance_Score"])

    def word(c):
        if pd.isna(c):
            return "not meaningfully"

        return (
            "strongly" if abs(c) > 0.6
            else "moderately" if abs(c) > 0.3
            else "weakly"
        )

    results = [
        (
            f"The average salary is {k['average_salary']:,.0f}, "
            f"ranging from {k['minimum_salary']:,.0f} "
            f"to {k['maximum_salary']:,.0f}."
        )
    ]

    if not ds.empty:
        results.append(
            f"{ds.index[0]} has the highest average salary "
            f"({ds.iloc[0]:,.0f}); {ds.index[-1]} has the lowest "
            f"({ds.iloc[-1]:,.0f})."
        )

    if not dp.empty:
        results.append(
            f"{dp.index[0]} has the best average performance score "
            f"({dp.iloc[0]:.2f}); {dp.index[-1]} has the lowest "
            f"({dp.iloc[-1]:.2f})."
        )

    results.extend([
        f"Experience and salary are {word(c1)} related (correlation {c1:.2f}).",
        f"Performance and salary are {word(c2)} related (correlation {c2:.2f}).",
        (
            f"{(df['Performance_Score'] >= 4).mean() * 100:.1f}% "
            "of employees have a performance score of 4 or higher."
        )
    ])

    return results


# ============================================================
# CHART HELPER
# ============================================================

def _fig(title, xl, yl, draw, size=(7, 3.8)):
    fig, ax = plt.subplots(figsize=size)

    draw(ax)

    ax.set(
        title=title,
        xlabel=xl,
        ylabel=yl
    )

    fig.tight_layout()

    return fig


# ============================================================
# SALARY AND PERFORMANCE CHARTS
# ============================================================

def fig_salary_dist(df):
    return _fig(
        "Salary distribution",
        "Salary",
        "Employees",
        lambda ax: sns.histplot(
            df["Basic_Salary"],
            kde=False,
            color=TEAL,
            ax=ax
        )
    )


def fig_perf_dist(df):
    return _fig(
        "Performance score distribution",
        "Score",
        "Employees",
        lambda ax: sns.countplot(
            x=df["Performance_Score"].round().astype(int),
            color=NAVY,
            ax=ax
        )
    )


# ============================================================
# DEPARTMENT CHARTS
# ============================================================

def fig_dept_salary(df):
    s = dept_salary(df)

    return _fig(
        "Average salary by department",
        "Department",
        "Average salary",
        lambda ax: sns.barplot(
            x=s.index,
            y=s.values,
            color=NAVY,
            ax=ax
        )
    )


def fig_dept_perf(df):
    s = dept_performance(df)

    return _fig(
        "Average performance by department",
        "Department",
        "Average score",
        lambda ax: sns.barplot(
            x=s.index,
            y=s.values,
            color=TEAL,
            ax=ax
        )
    )


def fig_dept_count(df):
    return _fig(
        "Employees by department",
        "Employees",
        "",
        lambda ax: sns.countplot(
            data=df,
            y="Department",
            color=TEAL,
            ax=ax
        )
    )


# ============================================================
# RELATIONSHIP CHARTS
# ============================================================

def fig_salary_vs_perf(df):
    return _fig(
        "Salary vs performance",
        "Salary",
        "Performance score",
        lambda ax: sns.scatterplot(
            data=df,
            x="Basic_Salary",
            y="Performance_Score",
            hue="Department",
            ax=ax
        )
    )


def fig_experience(df):
    return _fig(
        "Experience vs salary",
        "Experience (years)",
        "Salary",
        lambda ax: sns.scatterplot(
            data=df,
            x="Experience_Years",
            y="Basic_Salary",
            hue="Department",
            ax=ax
        )
    )


# ============================================================
# CORRELATION HEATMAP
# ============================================================

def fig_corr(df):
    return _fig(
        "Correlation heatmap",
        "",
        "",
        lambda ax: sns.heatmap(
            correlation(df),
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            ax=ax,
            annot_kws={"size": 7}
        ),
        size=(8, 6)
    )


# ============================================================
# HTML REPORT
# ============================================================

def report_html(df, user):
    rows = "".join(
        f"<tr><td>{name.replace('_', ' ').title()}</td>"
        f"<td>{value:,}</td></tr>"
        for name, value in kpis(df).items()
    )

    items = "".join(
        f"<li>{item}</li>"
        for item in insights(df)
    )

    department_html = dept_table(df).to_html(index=False)

    return (
        "<html><head><meta charset='utf-8'>"
        "<title>Employee report</title>"
        "<style>"
        "body{font-family:Arial;margin:40px;color:#14213d}"
        "table{border-collapse:collapse}"
        "td,th{border:1px solid #ccd;padding:6px 12px;text-align:left}"
        "th{background:#e8eefc}"
        "@media print{button{display:none}}"
        "</style></head><body>"
        "<h1>Employee Salary &amp; Performance Report</h1>"
        f"<p>Prepared for {user}</p>"
        f"<h2>Key indicators</h2><table>{rows}</table>"
        f"<h2>Automated insights</h2><ul>{items}</ul>"
        f"<h2>Departments</h2>{department_html}<br>"
        "<button onclick='window.print()'>Print report</button>"
        "</body></html>"
    )



# ============================================================
# NOTEBOOK-ALIGNED WORKFORCE AND PRODUCTIVITY ANALYSIS
# ============================================================

def _has(df, columns):
    return all(c in df.columns for c in columns)


def _numeric(df, column):
    return pd.to_numeric(df[column], errors="coerce") if column in df.columns else pd.Series(dtype=float)


def categorical_counts(df, column):
    if column not in df.columns:
        return pd.DataFrame(columns=[column, "Employees"])
    return (
        df[column].fillna("Unknown").astype(str).value_counts()
        .rename_axis(column).reset_index(name="Employees")
    )


def workforce_summary(df):
    fields = [
        ("Gender", "Gender"),
        ("Education", "Education"),
        ("Employment type", "Employment_Type"),
        ("Job role", "Designation"),
    ]
    rows = []
    for label, col in fields:
        if col in df.columns:
            rows.append({
                "Category": label,
                "Distinct values": int(df[col].nunique(dropna=True)),
                "Employees": int(df[col].notna().sum())
            })
    return pd.DataFrame(rows)


def missing_summary(df):
    return pd.DataFrame({
        "Column": df.columns,
        "Missing values": [int(df[c].isna().sum()) for c in df.columns],
        "Missing (%)": [
            round(float(df[c].isna().mean() * 100), 2) for c in df.columns
        ]
    }).sort_values(["Missing values", "Column"], ascending=[False, True])


def _categorical_chart(df, column, title, kind="bar"):
    if column not in df.columns:
        return None
    counts = df[column].fillna("Unknown").astype(str).value_counts()
    if counts.empty:
        return None
    fig, ax = plt.subplots(figsize=(7, 3.8))
    if kind == "pie":
        counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)
        ax.set_ylabel("")
    else:
        counts.plot(kind="bar", color=TEAL, ax=ax)
        ax.set_xlabel(column.replace("_", " "))
        ax.set_ylabel("Employees")
        ax.tick_params(axis="x", rotation=35)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def fig_salary_box(df):
    return _fig(
        "Salary box plot", "Salary", "",
        lambda ax: sns.boxplot(x=_numeric(df, "Basic_Salary"), color=TEAL, ax=ax)
    )


def fig_performance_box(df):
    return _fig(
        "Performance score box plot", "Performance score", "",
        lambda ax: sns.boxplot(x=_numeric(df, "Performance_Score"), color=NAVY, ax=ax)
    )


def fig_attendance_vs_performance(df):
    if not _has(df, ["Attendance_Percentage", "Performance_Score"]):
        return None
    return _fig(
        "Attendance vs performance", "Attendance (%)", "Performance score",
        lambda ax: sns.scatterplot(
            data=df, x="Attendance_Percentage", y="Performance_Score",
            hue="Department" if "Department" in df.columns else None, ax=ax
        )
    )


def fig_training_vs_performance(df):
    if not _has(df, ["Training_Hours", "Performance_Score"]):
        return None
    return _fig(
        "Training hours vs performance", "Training hours", "Performance score",
        lambda ax: sns.scatterplot(
            data=df, x="Training_Hours", y="Performance_Score",
            hue="Department" if "Department" in df.columns else None, ax=ax
        )
    )


def fig_overtime_vs_satisfaction(df):
    if not _has(df, ["Overtime_Hours", "Job_Satisfaction"]):
        return None
    return _fig(
        "Overtime vs job satisfaction", "Overtime hours", "Job satisfaction",
        lambda ax: sns.scatterplot(
            data=df, x="Overtime_Hours", y="Job_Satisfaction",
            hue="Department" if "Department" in df.columns else None, ax=ax
        )
    )


def fig_numeric_relationship(df, x, y, title, xlabel=None, ylabel=None):
    if not _has(df, [x, y]):
        return None
    return _fig(
        title, xlabel or x.replace("_", " "), ylabel or y.replace("_", " "),
        lambda ax: sns.scatterplot(data=df, x=x, y=y, ax=ax)
    )


def numeric_correlation(df):
    excluded = {"Bonus", "Total_Salary"}
    numeric = df.select_dtypes(include=np.number)
    numeric = numeric[[c for c in numeric.columns if c not in excluded]]
    return numeric.corr()


def fig_full_corr(df):
    corr = numeric_correlation(df)
    if corr.empty:
        return None
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, ax=ax, annot_kws={"size": 7})
    ax.set_title("Employee dataset correlation heatmap")
    fig.tight_layout()
    return fig


def department_full_summary(df):
    required = ["Department", "Employee_ID"]
    if not _has(df, required):
        return pd.DataFrame()
    aggregations = {"Employees": ("Employee_ID", "count")}
    for col, label in [
        ("Basic_Salary", "Average salary"),
        ("Performance_Score", "Average performance"),
        ("Experience_Years", "Average experience"),
        ("Attendance_Percentage", "Average attendance"),
        ("Training_Hours", "Average training hours"),
        ("Projects_Completed", "Average projects completed"),
    ]:
        if col in df.columns:
            aggregations[label] = (col, "mean")
    return df.groupby("Department").agg(**aggregations).round(2).reset_index()


def productivity_summary(df):
    metrics = [
        ("Attendance_Percentage", "Average attendance (%)"),
        ("Training_Hours", "Average training hours"),
        ("Overtime_Hours", "Average overtime hours"),
        ("Leave_Days", "Average leave days"),
        ("Projects_Completed", "Average projects completed"),
        ("Job_Satisfaction", "Average job satisfaction"),
        ("Manager_Rating", "Average manager rating"),
    ]
    rows = []
    for col, label in metrics:
        if col in df.columns:
            values = _numeric(df, col).dropna()
            rows.append({
                "Metric": label,
                "Average": round(float(values.mean()), 2) if not values.empty else None,
                "Median": round(float(values.median()), 2) if not values.empty else None,
                "Minimum": round(float(values.min()), 2) if not values.empty else None,
                "Maximum": round(float(values.max()), 2) if not values.empty else None,
            })
    return pd.DataFrame(rows)


def promotion_eligible_count(df):
    if "Promotion_Eligible" not in df.columns:
        return None
    return int(
        df["Promotion_Eligible"].astype(str).str.strip().str.lower()
        .isin(["yes", "true", "1"]).sum()
    )


def experience_category_counts(df):
    if "Experience_Years" not in df.columns:
        return pd.DataFrame(columns=["Experience group", "Employees"])
    years = _numeric(df, "Experience_Years")
    bands = pd.cut(
        years, bins=[-np.inf, 2, 5, np.inf],
        labels=["Fresher (0-2)", "Mid-level (3-5)", "Experienced (6+)"]
    )
    return bands.value_counts(sort=False).rename_axis("Experience group").reset_index(name="Employees")
