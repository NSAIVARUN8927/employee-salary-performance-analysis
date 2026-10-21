import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import analytics as an, auth, database as db

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

    import re
    import streamlit as st

    # =========================================================
    # STAFFMETRICS — PROFESSIONAL AUTHENTICATION INTERFACE
    # =========================================================

    st.markdown("""
    <style>

    /* ---------------- GLOBAL LOGIN BACKGROUND ---------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 12% 15%,
                rgba(37, 99, 235, 0.20),
                transparent 32%
            ),
            radial-gradient(
                circle at 88% 85%,
                rgba(6, 182, 212, 0.13),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #070b18 0%,
                #0b1224 50%,
                #101c35 100%
            );

        background-attachment: fixed;
        color: #e5edf9;
    }

    /* ---------------- HIDE SIDEBAR ---------------- */

    [data-testid="stSidebar"] {
        display: none;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ---------------- PAGE CONTAINER ---------------- */

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ---------------- ANIMATED BACKGROUND ---------------- */

    @keyframes backgroundGlow {
        0% {
            transform: translate(0, 0) scale(1);
        }

        50% {
            transform: translate(20px, -25px) scale(1.08);
        }

        100% {
            transform: translate(0, 0) scale(1);
        }
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(18px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes floatAnimation {
        0%, 100% {
            transform: translateY(0);
        }

        50% {
            transform: translateY(-12px);
        }
    }

    @keyframes pulseGlow {
        0%, 100% {
            box-shadow: 0 0 18px rgba(59, 130, 246, 0.12);
        }

        50% {
            box-shadow: 0 0 35px rgba(59, 130, 246, 0.28);
        }
    }

    .login-shell {
        animation: fadeIn 0.8s ease-out both;
    }

    .ambient-orb {
        position: fixed;
        width: 230px;
        height: 230px;
        border-radius: 50%;
        background: rgba(37, 99, 235, 0.12);
        filter: blur(65px);
        pointer-events: none;
        z-index: 0;
        animation: backgroundGlow 8s ease-in-out infinite;
    }

    .ambient-orb.one {
        top: 8%;
        left: 3%;
    }

    .ambient-orb.two {
        bottom: 5%;
        right: 3%;
        background: rgba(6, 182, 212, 0.12);
        animation-delay: -4s;
    }

    /* ---------------- BRAND PANEL ---------------- */

    .brand-panel {
        min-height: 580px;
        height: 100%;
        padding: 42px 35px;

        background:
            linear-gradient(
                145deg,
                rgba(30, 58, 105, 0.90),
                rgba(12, 24, 48, 0.96)
            );

        border: 1px solid rgba(148, 180, 255, 0.18);
        border-radius: 24px 0 0 24px;

        display: flex;
        flex-direction: column;
        justify-content: space-between;

        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.24);
        overflow: hidden;
        position: relative;
    }

    .brand-panel::before {
        content: "";
        position: absolute;
        top: -110px;
        right: -110px;

        width: 300px;
        height: 300px;

        border-radius: 50%;

        background: rgba(59, 130, 246, 0.14);
        filter: blur(10px);

        animation: floatAnimation 7s ease-in-out infinite;
    }

    .brand-panel::after {
        content: "";
        position: absolute;

        width: 220px;
        height: 220px;

        bottom: -120px;
        left: -70px;

        border: 1px solid rgba(103, 232, 249, 0.18);
        border-radius: 50%;
        box-shadow:
            0 0 0 25px rgba(103, 232, 249, 0.025),
            0 0 0 50px rgba(103, 232, 249, 0.02);
    }

    .brand-content {
        position: relative;
        z-index: 1;
    }

    .brand-logo {
        width: 56px;
        height: 56px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 16px;

        background: linear-gradient(
            145deg,
            #60a5fa,
            #2563eb
        );

        color: white;
        font-size: 28px;

        box-shadow: 0 8px 30px rgba(37, 99, 235, 0.35);
        animation: pulseGlow 4s ease-in-out infinite;
    }

    .brand-name {
        color: #ffffff;
        font-size: 29px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-top: 18px;
    }

    .brand-name span {
        color: #60a5fa;
    }

    .brand-tagline {
        color: #a9bad7;
        font-size: 12px;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    .brand-headline {
        color: #ffffff;
        font-size: 35px;
        line-height: 1.25;
        letter-spacing: -1.2px;
        font-weight: 750;
        margin-top: 55px;
    }

    .brand-headline span {
        color: #60a5fa;
    }

    .brand-description {
        color: #b5c4dc;
        font-size: 14px;
        line-height: 1.9;
        margin-top: 18px;
    }

    /* ---------------- VISUAL ANALYTICS CARD ---------------- */

    .visual-card {
        margin-top: 30px;
        padding: 18px;

        background: rgba(255, 255, 255, 0.045);
        border: 1px solid rgba(148, 180, 255, 0.14);
        border-radius: 17px;

        backdrop-filter: blur(14px);
    }

    .visual-card-label {
        color: #9eb1d0;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .visual-card-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 650;
        margin-top: 7px;
    }

    .visual-bars {
        display: flex;
        align-items: flex-end;
        gap: 9px;
        height: 75px;
        margin-top: 15px;
    }

    .visual-bar {
        flex: 1;
        border-radius: 5px 5px 2px 2px;
        background: linear-gradient(
            to top,
            #2563eb,
            #67e8f9
        );
        transform-origin: bottom;
        animation: barRise 1s ease-out both;
    }

    @keyframes barRise {
        from {
            transform: scaleY(0.05);
            opacity: 0.3;
        }

        to {
            transform: scaleY(1);
            opacity: 1;
        }
    }

    .bar1 { height: 35%; animation-delay: 0.1s; }
    .bar2 { height: 60%; animation-delay: 0.2s; }
    .bar3 { height: 44%; animation-delay: 0.3s; }
    .bar4 { height: 78%; animation-delay: 0.4s; }
    .bar5 { height: 55%; animation-delay: 0.5s; }
    .bar6 { height: 95%; animation-delay: 0.6s; }
    .bar7 { height: 72%; animation-delay: 0.7s; }

    .brand-footer {
        color: #7f93b4;
        font-size: 11px;
        margin-top: 28px;
        position: relative;
        z-index: 2;
    }

    /* ---------------- AUTHENTICATION PANEL ---------------- */

    .auth-panel {
        min-height: 580px;
        padding: 35px 32px;

        background: rgba(15, 23, 42, 0.91);

        border: 1px solid rgba(148, 163, 184, 0.17);
        border-left: none;

        border-radius: 0 24px 24px 0;

        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.22);
        backdrop-filter: blur(20px);
    }

    .auth-eyebrow {
        color: #60a5fa;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .auth-title {
        color: #f8fafc;
        font-size: 29px;
        font-weight: 750;
        letter-spacing: -0.8px;
        margin-top: 12px;
    }

    .auth-subtitle {
        color: #94a3b8;
        font-size: 13px;
        line-height: 1.7;
        margin-top: 8px;
        margin-bottom: 24px;
    }

    /* ---------------- FORM LABELS ---------------- */

    [data-testid="stWidgetLabel"] p {
        color: #d4deed !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    /* ---------------- INPUT FIELDS ---------------- */

    [data-testid="stTextInput"] input,
    [data-testid="stTextInput"] input:focus {
        background: #111c30 !important;
        color: #f1f5f9 !important;

        border: 1px solid #293851 !important;
        border-radius: 10px !important;

        min-height: 44px;
        transition: border-color 0.2s ease,
                    box-shadow 0.2s ease;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #60a5fa !important;

        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #64748b !important;
    }

    /* ---------------- CHECKBOXES ---------------- */

    [data-testid="stCheckbox"] label {
        color: #b8c6db !important;
        font-size: 12px !important;
    }

    /* ---------------- BUTTONS ---------------- */

    .stButton > button,
    [data-testid="stFormSubmitButton"] > button {
        width: 100%;
        min-height: 46px;

        background: linear-gradient(
            100deg,
            #2563eb,
            #0ea5e9
        ) !important;

        color: white !important;
        border: 1px solid rgba(147, 197, 253, 0.25) !important;
        border-radius: 10px !important;

        font-weight: 700 !important;
        font-size: 13px !important;

        transition: transform 0.2s ease,
                    box-shadow 0.2s ease,
                    filter 0.2s ease;
    }

    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);

        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);

        filter: brightness(1.12);
    }

    .stButton > button:focus-visible,
    [data-testid="stFormSubmitButton"] > button:focus-visible {
        outline: 2px solid #67e8f9 !important;
        outline-offset: 3px;
    }

    /* ---------------- TABS ---------------- */

    [data-testid="stTabs"] [role="tablist"] {
        gap: 10px;
        border-bottom: 1px solid #26334a;
    }

    [data-testid="stTabs"] button[role="tab"] {
        color: #94a3b8 !important;
        font-weight: 650;
        font-size: 13px;
    }

    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #60a5fa !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: #60a5fa !important;
    }

    /* ---------------- DIVIDERS AND CAPTIONS ---------------- */

    hr {
        border-color: #26334a !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #94a3b8;
    }

    /* ---------------- ALERTS ---------------- */

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* ---------------- RESPONSIVE DESIGN ---------------- */

    @media (max-width: 800px) {
        .block-container {
            padding: 1rem;
        }

        .brand-panel {
            min-height: auto;
            padding: 25px;
            border-radius: 20px 20px 0 0;
        }

        .brand-headline {
            font-size: 27px;
            margin-top: 25px;
        }

        .visual-card {
            margin-top: 20px;
        }

        .brand-footer {
            margin-top: 20px;
        }

        .auth-panel {
            min-height: auto;
            padding: 25px 20px;
            border-left: 1px solid rgba(148, 163, 184, 0.17);
            border-radius: 0 0 20px 20px;
        }
    }

    /* Respect reduced-motion accessibility settings. */

    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    </style>

    <div class="ambient-orb one"></div>
    <div class="ambient-orb two"></div>
    """, unsafe_allow_html=True)

    # =========================================================
    # TWO-PANEL LOGIN LAYOUT
    # =========================================================

    left, right = st.columns(
        [1.02, 1],
        gap="small"
    )

    # =========================================================
    # LEFT: BRANDING AND VISUALS
    # =========================================================

    with left:

        st.markdown("""
        <div class="brand-panel">

            <div class="brand-content">

                <div class="brand-logo">✦</div>

                <div class="brand-name">
                    Staff<span>Metrics</span>
                </div>

                <div class="brand-tagline">
                    Workforce intelligence
                </div>

                <div class="brand-headline">
                    Understand your workforce.<br>
                    <span>Unlock better decisions.</span>
                </div>

                <div class="brand-description">
                    One intelligent workspace for employee analytics,
                    compensation insights, and performance management.
                    Transform workforce data into decisions that matter.
                </div>

                <div class="visual-card">

                    <div class="visual-card-label">
                        Your analytics workspace
                    </div>

                    <div class="visual-card-title">
                        Workforce insights
                    </div>

                    <div class="visual-bars">
                        <div class="visual-bar bar1"></div>
                        <div class="visual-bar bar2"></div>
                        <div class="visual-bar bar3"></div>
                        <div class="visual-bar bar4"></div>
                        <div class="visual-bar bar5"></div>
                        <div class="visual-bar bar6"></div>
                        <div class="visual-bar bar7"></div>
                    </div>

                </div>

            </div>

            <div class="brand-footer">
                STAFFMETRICS &nbsp;·&nbsp;
                EMPLOYEE ANALYTICS PLATFORM
            </div>

        </div>
        """, unsafe_allow_html=True)

    # =========================================================
    # RIGHT: LOGIN, REGISTRATION AND RECOVERY
    # =========================================================

    with right:

        st.markdown("""
        <div class="auth-panel">

            <div class="auth-eyebrow">
                Secure workspace
            </div>

            <div class="auth-title">
                Welcome back
            </div>

            <div class="auth-subtitle">
                Sign in to access your employee analytics dashboard.
                Your workspace is waiting for you.
            </div>

        </div>
        """, unsafe_allow_html=True)

        login_tab, register_tab, recovery_tab = st.tabs([
            "Sign in",
            "Create account",
            "Forgot password?"
        ])

        # =====================================================
        # SIGN IN
        # =====================================================

        with login_tab:

            st.markdown("#### Sign in to StaffMetrics")

            with st.form(
                "staffmetrics_login_form",
                clear_on_submit=False
            ):

                login_id = st.text_input(
                    "Username or email",
                    placeholder="Enter your username or email",
                    key="login_username"
                )

                login_password = st.text_input(
                    "Password",
                    placeholder="Enter your password",
                    type="password",
                    key="login_password"
                )

                remember_me = st.checkbox(
                    "Remember me for this session",
                    key="remember_me"
                )

                submitted = st.form_submit_button(
                    "Sign in  →",
                    use_container_width=True
                )

            # Enter submits the form automatically.

            if submitted:

                if not login_id.strip() or not login_password:

                    st.warning(
                        "Please enter your username/email and password."
                    )

                else:

                    try:

                        user = auth.login(
                            login_id.strip(),
                            login_password
                        )

                        if user:

                            st.session_state.user = user

                            # This checkbox is only a session preference.
                            # It does not create persistent authentication.

                            st.session_state.remember_me = remember_me

                            db.log_activity(
                                user["id"],
                                "signed in"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Unable to sign in with those credentials. "
                                "Check your details and try again."
                            )

                    except Exception:

                        # Avoid displaying internal database or
                        # authentication errors to the user.

                        st.error(
                            "Sign-in is temporarily unavailable. "
                            "Please try again later."
                        )

            st.markdown("---")

            st.markdown("""
            <div style="
                text-align:center;
                color:#94a3b8;
                font-size:11px;
                line-height:1.8;
            ">
                🔒 Protected account access<br>
                Use your registered credentials to continue.
            </div>
            """, unsafe_allow_html=True)

        # =====================================================
        # REGISTRATION
        # =====================================================

        with register_tab:

            st.markdown("#### Create your account")

            with st.form(
                "staffmetrics_register_form",
                clear_on_submit=False
            ):

                full_name = st.text_input(
                    "Full name",
                    placeholder="Enter your full name",
                    key="register_full_name"
                )

                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                    key="register_email"
                )

                username = st.text_input(
                    "Username",
                    placeholder="Choose a username",
                    key="register_username"
                )

                password = st.text_input(
                    "Create password",
                    type="password",
                    placeholder="At least 12 characters recommended",
                    key="register_password"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="register_confirm_password"
                )

                submitted_register = st.form_submit_button(
                    "Create secure account  →",
                    use_container_width=True
                )

            # Password feedback outside the form updates when
            # Streamlit reruns after a widget interaction.

            if password:

                score = sum([
                    len(password) >= 12,
                    bool(re.search(r"[A-Z]", password)),
                    bool(re.search(r"[a-z]", password)),
                    bool(re.search(r"[0-9]", password)),
                    bool(re.search(r"[^A-Za-z0-9]", password))
                ])

                if len(password) < 8:

                    st.warning(
                        "Password strength: Too short."
                    )

                elif score <= 2:

                    st.warning(
                        "Password strength: Weak. "
                        "Consider using a longer passphrase."
                    )

                elif score <= 4:

                    st.info(
                        "Password strength: Moderate. "
                        "Add more variety or length."
                    )

                else:

                    st.success(
                        "Password strength: Strong."
                    )

            if submitted_register:

                if not all([
                    full_name.strip(),
                    email.strip(),
                    username.strip(),
                    password,
                    confirm_password
                ]):

                    st.warning(
                        "Please complete every field."
                    )

                elif not re.fullmatch(
                    r"[^@\s]+@[^@\s]+\.[^@\s]+",
                    email.strip()
                ):

                    st.error(
                        "Enter a valid email address."
                    )

                elif len(username.strip()) < 3:

                    st.error(
                        "Your username must contain at least "
                        "3 characters."
                    )

                elif len(password) < 12:

                    st.error(
                        "Use a password with at least "
                        "12 characters."
                    )

                elif password != confirm_password:

                    st.error(
                        "The passwords do not match."
                    )

                else:

                    try:

                        success, message = auth.register(
                            username.strip(),
                            email.strip(),
                            full_name.strip(),
                            password
                        )

                        if success:

                            st.success(
                                "Account created successfully."
                            )

                            st.info(
                                "You can now switch to Sign in "
                                "to access your account."
                            )

                        else:

                            st.error(message)

                    except Exception:

                        st.error(
                            "Account registration is temporarily "
                            "unavailable. Please try again later."
                        )

        # =====================================================
        # FORGOT PASSWORD
        # =====================================================

        with recovery_tab:

            st.markdown("#### Recover your account")

            st.write(
                "Forgot your password? Use your registered email "
                "to begin the account recovery process."
            )

            st.info(
                "Password recovery requires a backend service "
                "that generates secure, single-use reset tokens "
                "and sends them to the registered email address."
            )

            with st.form(
                "staffmetrics_password_recovery_form"
            ):

                recovery_email = st.text_input(
                    "Registered email address",
                    placeholder="Enter your registered email",
                    key="recovery_email"
                )

                recovery_submit = st.form_submit_button(
                    "Request password reset  →",
                    use_container_width=True
                )

            if recovery_submit:

                if not recovery_email.strip():

                    st.warning(
                        "Enter your registered email address."
                    )

                elif not re.fullmatch(
                    r"[^@\s]+@[^@\s]+\.[^@\s]+",
                    recovery_email.strip()
                ):

                    st.warning(
                        "Enter a valid email address."
                    )

                else:

                    st.warning(
                        "The password-reset service is not connected "
                        "yet. No reset email has been sent. "
                        "Connect a secure recovery backend to enable it."
                    )

        # =====================================================
        # FOOTER
        # =====================================================

        st.markdown("""
        <div style="
            text-align:center;
            color:#64748b;
            font-size:10px;
            margin-top:24px;
            line-height:1.8;
        ">
            StaffMetrics · Employee Salary & Performance Analysis<br>
            Secure access to your workforce analytics workspace
        </div>
        """, unsafe_allow_html=True)
def show(fig):
    st.pyplot(fig)
    plt.close(fig)



def page_dashboard(df):
    banner(
        "Executive Dashboard",
        f"Welcome, {st.session_state.user['full_name'] or st.session_state.user['username']}"
    )

    st.subheader("Dashboard Filters")

    # Department and designation filters
    c1, c2, c3 = st.columns(3)

    departments = sorted(df["Department"].dropna().unique().tolist())
    designations = sorted(df["Designation"].dropna().astype(str).unique().tolist())

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

    # Experience and performance filters
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
        st.warning("No employees match your selected filters.")
        return

    st.caption(
        f"Showing {len(filtered_df):,} of {len(df):,} employee records."
    )

    # KPI cards
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

    # Automated insights
    st.subheader("Automated Insights")

    for line in an.insights(filtered_df):
        st.info(line)

    # Chart selection
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
    pages = ["Dashboard", "Employees", "Analysis", "Departments", "Upload and export"]
    if user["role"] == "admin":
        pages.append("Administration")
    with st.sidebar:
        st.markdown(f"### {user['full_name'] or user['username']}")
        st.caption(f"{user['role'].title()} account")
        page = st.selectbox(
            "Navigate to page",
            pages,
            key="page_navigation"
        )
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
    elif page == "Upload and export": page_data(df)
    else: page_admin()


if "user" not in st.session_state:
    auth_page()
else:
    main()
