import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

REQUIRED = [
    "Employee_ID",
    "Department",
    "Experience_Years",
    "Salary",
    "Performance_Rating"
]

NAVY, TEAL = "#14213d", "#0f766e"


# ============================================================
# INDIAN CURRENCY FORMATTER
# ============================================================

def _indian_currency(value, _position=None):
    """Format numbers using Indian numbering, e.g. ₹1,00,000."""
    try:
        number = float(value)
        if not np.isfinite(number):
            return ""

        negative = number < 0
        number = abs(int(round(number)))
        digits = str(number)

        if len(digits) > 3:
            last_three = digits[-3:]
            remaining = digits[:-3]
            groups = []

            while remaining:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]

            digits = ",".join(groups + [last_three])

        return f"{'-' if negative else ''}₹{digits}"

    except (TypeError, ValueError, OverflowError):
        return ""


def _format_salary_axis(ax, axis="x"):
    """Format salary axis labels and prevent clipping."""
    if axis == "x":
        ax.xaxis.set_major_formatter(FuncFormatter(_indian_currency))
        ax.tick_params(axis="x", labelsize=9)
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(_indian_currency))
        ax.tick_params(axis="y", labelsize=9)

    ax.figure.tight_layout(pad=1.5)

    if axis == "x":
        ax.figure.subplots_adjust(bottom=0.25)
    else:
        ax.figure.subplots_adjust(left=0.25)


# ============================================================
# DATA LOADING
# ============================================================

def load_data(source):
    df = pd.read_csv(source)

    missing = [column for column in REQUIRED if column not in df.columns]

    if missing:
        raise ValueError(
            f"The file is missing required columns: {', '.join(missing)}"
        )

    return df


# ============================================================
# DATA CLEANING
# ============================================================

def clean_data(raw):
    df = raw.copy()
    log = []
    original_count = len(df)

    df = df.drop_duplicates().copy()
    log.append(
        f"Removed {original_count - len(df)} duplicate records"
    )

    text_columns = [
        column for column in df.columns
        if not pd.api.types.is_numeric_dtype(df[column])
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    numeric_columns = df.select_dtypes(include=np.number).columns

    missing_numeric = int(
        df[numeric_columns].isna().sum().sum()
    )

    log.append(
        f"Filled {missing_numeric} missing numeric values with the median"
    )

    for column in numeric_columns:
        median = df[column].median()

        if pd.notna(median):
            df[column] = df[column].fillna(median)

    missing_text = int(
        df[text_columns].isna().sum().sum()
    )

    log.append(
        f"Filled {missing_text} missing text values with 'Unknown'"
    )

    for column in text_columns:
        df[column] = df[column].fillna("Unknown")

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

    defaults = {
        "Age": np.nan,
        "Gender": "Unknown",
        "Designation": "Unknown",
        "Bonus": 0.0
    }

    for column, default in defaults.items():
        if column not in d.columns:
            d[column] = default

    if "Name" not in d.columns:
        d["Name"] = d["Employee_ID"]

    if "Joining_Date" in d.columns:
        joining_date = pd.to_datetime(
            d["Joining_Date"],
            errors="coerce"
        )
    else:
        joining_date = pd.Series(
            pd.NaT,
            index=d.index
        )

    d["Joining_Year"] = joining_date.dt.year.astype("Int64")
    d["Effective_Date"] = joining_date.dt.strftime("%Y-%m-%d")

    d["Basic_Salary"] = pd.to_numeric(
        d["Basic_Salary"],
        errors="coerce"
    )

    d["Bonus"] = pd.to_numeric(
        d["Bonus"],
        errors="coerce"
    ).fillna(0)

    d["Total_Salary"] = d["Basic_Salary"] + d["Bonus"]

    if "Performance_Score" in d.columns:
        d["Performance_Score"] = pd.to_numeric(
            d["Performance_Score"],
            errors="coerce"
        )

    for column in STD:
        if column not in d.columns:
            d[column] = np.nan

    extra_columns = [
        column for column in d.columns
        if column not in STD
    ]

    return d[STD + extra_columns].reset_index(drop=True)


def prepare(raw):
    cleaned, log = clean_data(raw)
    return standardise(cleaned), log


# ============================================================
# STATISTICAL SUMMARIES
# ============================================================

def _summary(series, label):
    series = pd.to_numeric(
        series,
        errors="coerce"
    ).dropna()

    return pd.Series({
        "Average": series.mean(),
        "Median": series.median(),
        "Minimum": series.min(),
        "Maximum": series.max(),
        "Std. Deviation": series.std()
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
    """Return department statistics without the Bonus column."""
    grouped = df.groupby("Department").agg(
        Employees=("Employee_ID", "count"),
        Avg_Salary=("Basic_Salary", "mean"),
        Avg_Performance=("Performance_Score", "mean")
    )

    return (
        grouped.round(2)
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

    grouped = df.groupby(
        bands,
        observed=True
    ).agg(
        Employees=("Employee_ID", "count"),
        Avg_Salary=("Basic_Salary", "mean"),
        Avg_Performance=("Performance_Score", "mean")
    )

    return (
        grouped.round(2)
        .reset_index()
        .rename(columns={"Experience_Years": "Experience"})
    )


def experience_category_counts(df):
    if "Experience_Years" not in df.columns:
        return pd.DataFrame(
            columns=["Experience group", "Employees"]
        )

    years = pd.to_numeric(
        df["Experience_Years"],
        errors="coerce"
    )

    bands = pd.cut(
        years,
        bins=[-np.inf, 2, 5, np.inf],
        labels=[
            "Fresher (0-2)",
            "Mid-level (3-5)",
            "Experienced (6+)"
        ]
    )

    return (
        bands.value_counts(sort=False)
        .rename_axis("Experience group")
        .reset_index(name="Employees")
    )


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

def correlation(df):
    return df.select_dtypes(include=np.number).corr()


def numeric_correlation(df):
    excluded = {"Bonus", "Total_Salary"}

    numeric = df.select_dtypes(include=np.number)

    numeric = numeric[
        [column for column in numeric.columns if column not in excluded]
    ]

    return numeric.corr()


# ============================================================
# KEY PERFORMANCE INDICATORS
# ============================================================

def kpis(df):
    salary = pd.to_numeric(
        df["Basic_Salary"],
        errors="coerce"
    )

    performance = pd.to_numeric(
        df["Performance_Score"],
        errors="coerce"
    )

    return {
        "total_employees": int(len(df)),
        "average_salary": round(float(salary.mean()), 2),
        "median_salary": round(float(salary.median()), 2),
        "minimum_salary": round(float(salary.min()), 2),
        "maximum_salary": round(float(salary.max()), 2),
        "average_performance": round(float(performance.mean()), 2),
        "maximum_performance": round(float(performance.max()), 2)
    }


# ============================================================
# AUTOMATED INSIGHTS
# ============================================================

def insights(df):
    indicators = kpis(df)
    department_salaries = dept_salary(df)
    department_performance = dept_performance(df)

    salary = pd.to_numeric(df["Basic_Salary"], errors="coerce")
    experience = pd.to_numeric(df["Experience_Years"], errors="coerce")
    performance = pd.to_numeric(df["Performance_Score"], errors="coerce")

    correlation_experience = salary.corr(experience)
    correlation_performance = salary.corr(performance)

    def strength(value):
        if pd.isna(value):
            return "not meaningfully"

        if abs(value) > 0.6:
            return "strongly"

        if abs(value) > 0.3:
            return "moderately"

        return "weakly"

    results = [
        (
            f"The average salary is "
            f"{_indian_currency(indicators['average_salary'])}, "
            f"ranging from "
            f"{_indian_currency(indicators['minimum_salary'])} "
            f"to "
            f"{_indian_currency(indicators['maximum_salary'])}."
        )
    ]

    if not department_salaries.empty:
        results.append(
            f"{department_salaries.index[0]} has the highest average "
            f"salary ({_indian_currency(department_salaries.iloc[0])}); "
            f"{department_salaries.index[-1]} has the lowest "
            f"({_indian_currency(department_salaries.iloc[-1])})."
        )

    if not department_performance.empty:
        results.append(
            f"{department_performance.index[0]} has the best average "
            f"performance score ({department_performance.iloc[0]:.2f}); "
            f"{department_performance.index[-1]} has the lowest "
            f"({department_performance.iloc[-1]:.2f})."
        )

    results.append(
        f"Experience and salary are "
        f"{strength(correlation_experience)} related "
        f"(correlation {correlation_experience:.2f})."
    )

    results.append(
        f"Performance and salary are "
        f"{strength(correlation_performance)} related "
        f"(correlation {correlation_performance:.2f})."
    )

    results.append(
        f"{(performance >= 4).mean() * 100:.1f}% of employees "
        f"have a performance score of 4 or higher."
    )

    return results


# ============================================================
# GENERAL CHART HELPER
# ============================================================

def _fig(title, xl, yl, draw, size=(7, 3.8)):
    """
    Consistent chart formatting for analysis graphs.

    Keeps the X-axis at the bottom and Y-axis on the left,
    with gridlines behind the data.
    """

    fig, ax = plt.subplots(figsize=size)

    # Draw the graph.
    draw(ax)

    # Apply titles and axis labels.
    ax.set_title(
        title,
        loc="left",
        pad=16,
        fontsize=12,
        fontweight="bold"
    )

    ax.set_xlabel(
        xl,
        labelpad=9
    )

    ax.set_ylabel(
        yl,
        labelpad=9
    )

    # Keep the scale and tick labels in their normal positions.
    ax.xaxis.set_ticks_position("bottom")
    ax.xaxis.set_label_position("bottom")

    ax.yaxis.set_ticks_position("left")
    ax.yaxis.set_label_position("left")

    ax.tick_params(
        axis="x",
        bottom=True,
        labelbottom=True,
        top=False,
        labeltop=False,
        direction="out",
        pad=5
    )

    ax.tick_params(
        axis="y",
        left=True,
        labelleft=True,
        right=False,
        labelright=False,
        direction="out",
        pad=5
    )

    # Ensure gridlines stay behind the plotted data.
    ax.set_axisbelow(True)

    ax.grid(
        True,
        axis="both",
        linestyle="--",
        linewidth=0.6,
        alpha=0.22
    )

    # Avoid unnecessary borders.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Preserve space for labels and prevent clipping.
    fig.tight_layout(pad=1.5)

    return fig

# ============================================================
# SALARY AND PERFORMANCE CHARTS
# ============================================================

def fig_salary_dist(df):
    fig, ax = plt.subplots(figsize=(7, 3.8))

    salary = pd.to_numeric(
        df["Basic_Salary"],
        errors="coerce"
    ).dropna()

    sns.histplot(
        salary,
        kde=False,
        color=TEAL,
        ax=ax
    )

    ax.set_title("Salary distribution")
    ax.set_xlabel("Salary")
    ax.set_ylabel("Employees")

    _format_salary_axis(ax, "x")

    return fig


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


def fig_salary_box(df):
    if df is None or df.empty or "Basic_Salary" not in df.columns:
        return None

    salary = pd.to_numeric(
        df["Basic_Salary"],
        errors="coerce"
    ).dropna()

    if salary.empty:
        return None

    fig, ax = plt.subplots(figsize=(7, 3.8))

    sns.boxplot(
        x=salary,
        color=TEAL,
        ax=ax
    )

    ax.set_title("Salary Distribution — Box Plot")
    ax.set_xlabel("Basic Salary")
    ax.set_ylabel("")

    _format_salary_axis(ax, "x")

    return fig


def fig_performance_box(df):
    performance = pd.to_numeric(
        df["Performance_Score"],
        errors="coerce"
    ).dropna()

    if performance.empty:
        return None

    return _fig(
        "Performance score box plot",
        "Performance score",
        "",
        lambda ax: sns.boxplot(
            x=performance,
            color=NAVY,
            ax=ax
        )
    )


# ============================================================
# DEPARTMENT CHARTS
# ============================================================

def fig_dept_salary(df):
    salary_by_department = dept_salary(df)

    fig, ax = plt.subplots(figsize=(7, 3.8))

    sns.barplot(
        x=salary_by_department.index,
        y=salary_by_department.values,
        color=NAVY,
        ax=ax
    )

    ax.set_title("Average salary by department")
    ax.set_xlabel("Department")
    ax.set_ylabel("Average salary")
    ax.tick_params(axis="x", rotation=25)

    _format_salary_axis(ax, "y")

    return fig


def fig_dept_perf(df):
    scores = dept_performance(df)

    return _fig(
        "Average performance by department",
        "Department",
        "Average score",
        lambda ax: sns.barplot(
            x=scores.index,
            y=scores.values,
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
    fig, ax = plt.subplots(figsize=(7, 3.8))

    sns.scatterplot(
        data=df,
        x="Basic_Salary",
        y="Performance_Score",
        hue="Department" if "Department" in df.columns else None,
        ax=ax
    )

    ax.set_title("Salary vs performance")
    ax.set_xlabel("Salary")
    ax.set_ylabel("Performance score")

    _format_salary_axis(ax, "x")

    return fig


def fig_experience(df):
    fig, ax = plt.subplots(figsize=(7, 3.8))

    sns.scatterplot(
        data=df,
        x="Experience_Years",
        y="Basic_Salary",
        hue="Department" if "Department" in df.columns else None,
        ax=ax
    )

    ax.set_title("Experience vs salary")
    ax.set_xlabel("Experience (years)")
    ax.set_ylabel("Salary")

    _format_salary_axis(ax, "y")

    return fig


# ============================================================
# CORRELATION HEATMAPS
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


def fig_full_corr(df):
    corr = numeric_correlation(df)

    if corr.empty:
        return None

    fig, ax = plt.subplots(figsize=(11, 7))

    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        ax=ax,
        annot_kws={"size": 7}
    )

    ax.set_title("Employee dataset correlation heatmap")
    fig.tight_layout()

    return fig


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
    return all(column in df.columns for column in columns)


def _numeric(df, column):
    if column not in df.columns:
        return pd.Series(dtype=float)

    return pd.to_numeric(df[column], errors="coerce")


def categorical_counts(df, column):
    if column not in df.columns:
        return pd.DataFrame(columns=[column, "Employees"])

    return (
        df[column]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .rename_axis(column)
        .reset_index(name="Employees")
    )


def workforce_summary(df):
    fields = [
        ("Gender", "Gender"),
        ("Education", "Education"),
        ("Employment type", "Employment_Type"),
        ("Job role", "Designation")
    ]

    rows = []

    for label, column in fields:
        if column in df.columns:
            rows.append({
                "Category": label,
                "Distinct values": int(df[column].nunique(dropna=True)),
                "Employees": int(df[column].notna().sum())
            })

    return pd.DataFrame(rows)


def missing_summary(df):
    return pd.DataFrame({
        "Column": df.columns,
        "Missing values": [
            int(df[column].isna().sum())
            for column in df.columns
        ],
        "Missing (%)": [
            round(float(df[column].isna().mean() * 100), 2)
            for column in df.columns
        ]
    }).sort_values(
        ["Missing values", "Column"],
        ascending=[False, True]
    )


def _categorical_chart(df, column, title, kind="bar"):
    """
    Create readable categorical charts.

    Improvements:
    - Job roles use horizontal bars.
    - Long category names remain readable.
    - Categories are sorted by employee count.
    - Axis labels do not overlap.
    - Chart spacing adapts to the number of categories.
    """

    if column not in df.columns:
        return None

    counts = (
        df[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .value_counts()
    )

    if counts.empty:
        return None

    # Pie charts remain unchanged in purpose.
    if kind == "pie":
        fig, ax = plt.subplots(figsize=(7, 4.5))

        counts.plot(
            kind="pie",
            autopct="%1.1f%%",
            startangle=90,
            ax=ax
        )

        ax.set_ylabel("")
        ax.set_title(title, pad=16)
        ax.axis("equal")

        fig.tight_layout()
        return fig

    # Job roles and other long category labels are easier to read
    # when placed along the vertical axis.
    use_horizontal_bars = (
        column in ["Designation", "Department", "Education"]
        or len(counts) >= 7
    )

    if use_horizontal_bars:
        # Display the largest categories at the top.
        counts = counts.sort_values(ascending=True)

        chart_height = max(4.2, min(8.5, 2.0 + len(counts) * 0.42))

        fig, ax = plt.subplots(
            figsize=(8, chart_height)
        )

        bars = ax.barh(
            counts.index.astype(str),
            counts.values,
            color=TEAL,
            height=0.68,
            edgecolor="white",
            linewidth=0.7
        )

        ax.set_xlabel("Number of Employees", labelpad=10)
        ax.set_ylabel("")
        ax.set_title(title, pad=18, loc="left")

        # Keep category names on the left and counts on the bottom.
        ax.tick_params(
            axis="y",
            labelsize=9,
            pad=8,
            left=False,
            labelleft=True
        )

        ax.tick_params(
            axis="x",
            labelsize=9,
            bottom=True,
            labelbottom=True,
            top=False,
            labeltop=False
        )

        # Place subtle gridlines behind the bars.
        ax.set_axisbelow(True)
        ax.grid(
            axis="x",
            linestyle="--",
            alpha=0.25
        )
        ax.grid(axis="y", visible=False)

        # Add employee counts at the end of each bar.
        ax.bar_label(
            bars,
            labels=[f"{int(value)}" for value in counts.values],
            padding=5,
            fontsize=9
        )

        # Leave space for the labels at the end of each bar.
        maximum = max(counts.values) if len(counts) else 0
        ax.set_xlim(0, maximum * 1.18 if maximum > 0 else 1)

        # Clean chart appearance.
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

    else:
        # Use a vertical bar chart for smaller categories.
        fig, ax = plt.subplots(figsize=(7, 4.2))

        bars = ax.bar(
            counts.index.astype(str),
            counts.values,
            color=TEAL,
            width=0.68
        )

        ax.set_xlabel(column.replace("_", " "), labelpad=10)
        ax.set_ylabel("Number of Employees", labelpad=10)
        ax.set_title(title, pad=16, loc="left")

        ax.tick_params(
            axis="x",
            rotation=25,
            labelsize=9,
            bottom=True,
            labelbottom=True,
            top=False,
            labeltop=False
        )

        ax.tick_params(
            axis="y",
            left=True,
            labelleft=True,
            right=False,
            labelright=False
        )

        ax.set_axisbelow(True)
        ax.grid(axis="y", linestyle="--", alpha=0.25)
        ax.grid(axis="x", visible=False)

        ax.bar_label(
            bars,
            padding=3,
            fontsize=9
        )

        maximum = max(counts.values) if len(counts) else 0
        ax.set_ylim(0, maximum * 1.18 if maximum > 0 else 1)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

    return fig

# ============================================================
# ATTENDANCE AND PRODUCTIVITY CHARTS
# ============================================================

def fig_attendance_vs_performance(df):
    if not _has(df, ["Attendance_Percentage", "Performance_Score"]):
        return None

    return _fig(
        "Attendance vs performance",
        "Attendance (%)",
        "Performance score",
        lambda ax: sns.scatterplot(
            data=df,
            x="Attendance_Percentage",
            y="Performance_Score",
            hue="Department" if "Department" in df.columns else None,
            ax=ax
        )
    )


def fig_training_vs_performance(df):
    if not _has(df, ["Training_Hours", "Performance_Score"]):
        return None

    return _fig(
        "Training hours vs performance",
        "Training hours",
        "Performance score",
        lambda ax: sns.scatterplot(
            data=df,
            x="Training_Hours",
            y="Performance_Score",
            hue="Department" if "Department" in df.columns else None,
            ax=ax
        )
    )


def fig_overtime_vs_satisfaction(df):
    if not _has(df, ["Overtime_Hours", "Job_Satisfaction"]):
        return None

    return _fig(
        "Overtime vs job satisfaction",
        "Overtime hours",
        "Job satisfaction",
        lambda ax: sns.scatterplot(
            data=df,
            x="Overtime_Hours",
            y="Job_Satisfaction",
            hue="Department" if "Department" in df.columns else None,
            ax=ax
        )
    )


def fig_numeric_relationship(
    df,
    x,
    y,
    title,
    xlabel=None,
    ylabel=None
):
    if not _has(df, [x, y]):
        return None

    return _fig(
        title,
        xlabel or x.replace("_", " "),
        ylabel or y.replace("_", " "),
        lambda ax: sns.scatterplot(
            data=df,
            x=x,
            y=y,
            ax=ax
        )
    )


# ============================================================
# DEPARTMENT SUMMARY
# ============================================================

def department_full_summary(df):
    required = ["Department", "Employee_ID"]

    if not _has(df, required):
        return pd.DataFrame()

    aggregations = {
        "Employees": ("Employee_ID", "count")
    }

    metrics = [
        ("Basic_Salary", "Average salary"),
        ("Performance_Score", "Average performance"),
        ("Experience_Years", "Average experience"),
        ("Attendance_Percentage", "Average attendance"),
        ("Training_Hours", "Average training hours"),
        ("Projects_Completed", "Average projects completed")
    ]

    for column, label in metrics:
        if column in df.columns:
            aggregations[label] = (column, "mean")

    return (
        df.groupby("Department")
        .agg(**aggregations)
        .round(2)
        .reset_index()
    )


# ============================================================
# PRODUCTIVITY SUMMARY
# ============================================================

def productivity_summary(df):
    metrics = [
        ("Attendance_Percentage", "Average attendance (%)"),
        ("Training_Hours", "Average training hours"),
        ("Overtime_Hours", "Average overtime hours"),
        ("Leave_Days", "Average leave days"),
        ("Projects_Completed", "Average projects completed"),
        ("Job_Satisfaction", "Average job satisfaction"),
        ("Manager_Rating", "Average manager rating")
    ]

    rows = []

    for column, label in metrics:
        if column in df.columns:
            values = _numeric(df, column).dropna()

            rows.append({
                "Metric": label,
                "Average": (
                    round(float(values.mean()), 2)
                    if not values.empty else None
                ),
                "Median": (
                    round(float(values.median()), 2)
                    if not values.empty else None
                ),
                "Minimum": (
                    round(float(values.min()), 2)
                    if not values.empty else None
                ),
                "Maximum": (
                    round(float(values.max()), 2)
                    if not values.empty else None
                )
            })

    return pd.DataFrame(rows)


# ============================================================
# PROMOTION ELIGIBILITY
# ============================================================

def promotion_eligible_count(df):
    if "Promotion_Eligible" not in df.columns:
        return None

    return int(
        df["Promotion_Eligible"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["yes", "true", "1"])
        .sum()
    )
