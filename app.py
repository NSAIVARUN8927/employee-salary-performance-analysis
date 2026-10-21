import os
import time

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import analytics as an, auth, database as db

st.set_page_config(page_title="Employee Salary & Performance Analysis", page_icon="📊", layout="wide")
db.init_db()
CSV = "data/employee_salary_performance.csv"
if not db.is_seeded():
    db.seed_database(an.prepare(an.load_data(CSV))[0])

# Session expiry: a signed-in user is forced back to the login page after
# this many seconds of being open, regardless of activity. Streamlit has no
# native session timeout, so this is enforced on every rerun below.
SESSION_TIMEOUT_SECONDS = 60 * 60  # 1 hour

# Base URL used to build password-reset links. Set APP_BASE_URL in your
# deployment environment (e.g. https://your-app.streamlit.app); falls back
# to localhost for local development.
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8501")

LIGHT_THEME = """
.stApp {background: #f5f7fb;}
.block-container {padding-top: 1.6rem; max-width: 1250px;}
h1, h2, h3 {color: #14213d; font-weight: 600;}
[data-testid="stSidebar"] {background: #14213d;}
[data-testid="stSidebar"] * {color: #e6ebf5;}
.banner {background: #14213d; color: #fff; padding: 22px 28px; border-radius: 6px; margin-bottom: 20px;}
.banner h1 {color: #fff; margin: 0; font-size: 1.7rem;} .banner p {margin: 4px 0 0; color: #b9c4dc;}
.kpi {background: #fff; border: 1px solid #dde3ee; border-top: 3px solid #0f766e; border-radius: 6px; padding: 14px 16px;}
.kpi span {color: #5b6b82; font-size: 0.85rem;} .kpi b {display: block; font-size: 1.55rem; color: #14213d; font-weight: 600;}
[data-testid="stDataFrame"] {background: #fff;}
"""

DARK_THEME = """
.stApp {background: #0b1224; color: #e5edf9;}
.block-container {padding-top: 1.6rem; max-width: 1250px;}
h1, h2, h3 {color: #e5edf9; font-weight: 600;}
p, label, span, div {color: #cbd5e1;}
[data-testid="stSidebar"] {background: #070b18;}
[data-testid="stSidebar"] * {color: #e6ebf5;}
.banner {background: linear-gradient(100deg, #1e3a69, #0c1830); color: #fff; padding: 22px 28px; border-radius: 6px; margin-bottom: 20px;}
.banner h1 {color: #fff; margin: 0; font-size: 1.7rem;} .banner p {margin: 4px 0 0; color: #b9c4dc;}
.kpi {background: #111c30; border: 1px solid #293851; border-top: 3px solid #2dd4bf; border-radius: 6px; padding: 14px 16px;}
.kpi span {color: #94a3b8; font-size: 0.85rem;} .kpi b {display: block; font-size: 1.55rem; color: #f1f5f9; font-weight: 600;}
[data-testid="stDataFrame"] {background: #111c30;}
[data-testid="stMetricValue"] {color: #f1f5f9;}
"""


def apply_theme():
    theme = st.session_state.get("theme", "Light")
    base = """<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] {font-family: 'IBM Plex Sans', sans-serif;}
</style>"""
    st.markdown(base, unsafe_allow_html=True)
    st.markdown(f"<style>{DARK_THEME if theme == 'Dark' else LIGHT_THEME}</style>", unsafe_allow_html=True)


apply_theme()


def banner(title, subtitle=""):
    st.markdown(f'<div class="banner"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def kpis(items):
    for col, (label, value) in zip(st.columns(len(items)), items):
        col.markdown(f'<div class="kpi"><span>{label}</span><b>{value}</b></div>', unsafe_allow_html=True)


def session_expired():
    started = st.session_state.get("login_time")
    return started is not None and (time.time() - started) > SESSION_TIMEOUT_SECONDS


def reset_password_view(token):
    """Standalone page shown when the app is opened with ?reset_token=... in
    the URL (the link sent by request_password_reset)."""
    banner("Reset your password", "Choose a new password for your StaffMetrics account")
    user = auth.validate_reset_token(token)
    if not user:
        st.error("This reset link is invalid or has expired. Request a new one from the sign-in page.")
        if st.button("Back to sign in"):
            st.query_params.clear()
            st.rerun()
        return
    st.info(f"Resetting the password for **{user['username']}** ({user['email']}).")
    with st.form("reset_password_form"):
        p1 = st.text_input("New password", type="password")
        p2 = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Update password")
    if submitted:
        if p1 != p2:
            st.error("The passwords do not match.")
        else:
            ok, message = auth.reset_password(token, p1)
            if ok:
                st.success(message)
                if st.button("Continue to sign in"):
                    st.query_params.clear()
                    st.rerun()
            else:
                st.error(message)
def auth_page():
    import re
    import streamlit as st
    import time

    # =========================================================
    # EAGLES - CINEMATIC AUTHENTICATION PAGE
    # =========================================================

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

        /* GLOBAL BACKGROUND */

        .stApp {
            background:
                radial-gradient(
                    circle at 15% 20%,
                    rgba(0, 180, 255, 0.15),
                    transparent 35%
                ),
                radial-gradient(
                    circle at 85% 75%,
                    rgba(0, 255, 220, 0.10),
                    transparent 35%
                ),
                linear-gradient(
                    135deg,
                    #020711 0%,
                    #07172b 48%,
                    #03101e 100%
                );

            background-attachment: fixed;
            font-family: 'Inter', sans-serif;
            color: #eaf6ff;
        }

        /* HIDE STREAMLIT CHROME */

        [data-testid="stSidebar"] {
            display: none;
        }

        #MainMenu,
        footer {
            visibility: hidden;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        /* ANIMATIONS */

        @keyframes fadeUp {
            from {
                opacity: 0;
                transform: translateY(25px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes eagleGlow {
            0%, 100% {
                filter: drop-shadow(0 0 8px rgba(0, 190, 255, .25));
                transform: translateY(0);
            }

            50% {
                filter: drop-shadow(0 0 25px rgba(0, 220, 255, .65));
                transform: translateY(-5px);
            }
        }

        @keyframes ambientMove {
            0%, 100% {
                transform: translate(0, 0);
            }

            50% {
                transform: translate(25px, -20px);
            }
        }

        @keyframes barAnimation {
            from {
                transform: scaleY(.1);
                opacity: .25;
            }

            to {
                transform: scaleY(1);
                opacity: 1;
            }
        }

        @keyframes borderGlow {
            0%, 100% {
                box-shadow: 0 0 15px rgba(0, 174, 255, .04);
            }

            50% {
                box-shadow: 0 0 35px rgba(0, 174, 255, .13);
            }
        }

        /* BACKGROUND LIGHTS */

        .eagles-orb {
            position: fixed;
            width: 250px;
            height: 250px;
            border-radius: 50%;
            background: rgba(0, 153, 255, .10);
            filter: blur(70px);
            pointer-events: none;
            z-index: 0;
            animation: ambientMove 9s ease-in-out infinite;
        }

        .eagles-orb-one {
            top: 8%;
            left: -80px;
        }

        .eagles-orb-two {
            bottom: 5%;
            right: -70px;
            background: rgba(0, 255, 210, .09);
            animation-delay: -4s;
        }

        /* MAIN TWO-PANEL LAYOUT */

        .eagles-brand-panel {
            position: relative;
            overflow: hidden;
            min-height: 650px;
            height: 100%;

            padding: 35px 32px;

            border: 1px solid rgba(76, 200, 255, .24);
            border-radius: 24px 0 0 24px;

            background:
                radial-gradient(
                    circle at 80% 25%,
                    rgba(0, 174, 255, .22),
                    transparent 35%
                ),
                linear-gradient(
                    150deg,
                    rgba(7, 36, 65, .98),
                    rgba(2, 11, 25, .98)
                );

            box-shadow: 0 25px 80px rgba(0, 0, 0, .4);

            animation: fadeUp .8s ease-out both;
        }

        .eagles-brand-panel::before {
            content: "";
            position: absolute;
            width: 320px;
            height: 320px;
            top: 100px;
            right: -180px;

            border: 1px solid rgba(0, 200, 255, .22);
            border-radius: 50%;

            box-shadow:
                0 0 0 30px rgba(0, 200, 255, .025),
                0 0 0 60px rgba(0, 200, 255, .02);
        }

        .eagles-brand-panel::after {
            content: "";
            position: absolute;
            width: 220px;
            height: 220px;
            bottom: -130px;
            left: -70px;

            border: 1px solid rgba(0, 255, 220, .2);
            border-radius: 50%;
        }

        .eagles-content {
            position: relative;
            z-index: 2;
        }

        /* EAGLE LOGO */

        .eagles-logo {
            width: 76px;
            height: 76px;

            display: flex;
            justify-content: center;
            align-items: center;

            font-size: 43px;

            border: 1px solid rgba(0, 220, 255, .45);
            border-radius: 22px;

            background: linear-gradient(
                145deg,
                rgba(0, 190, 255, .22),
                rgba(0, 255, 220, .06)
            );

            animation: eagleGlow 4s ease-in-out infinite;
        }

        .eagles-brand-name {
            font-family: 'Orbitron', sans-serif;
            font-size: 31px;
            font-weight: 800;
            letter-spacing: 5px;
            color: #ffffff;
            margin-top: 20px;
        }

        .eagles-brand-name span {
            color: #24dfff;
        }

        .eagles-tagline {
            font-size: 10px;
            letter-spacing: 4px;
            color: #75cde9;
            margin-top: 8px;
        }

        .eagles-headline {
            font-size: 34px;
            line-height: 1.3;
            font-weight: 800;
            letter-spacing: -1px;
            color: #f4fbff;
            margin-top: 45px;
        }

        .eagles-headline span {
            color: #2bdcff;
            text-shadow: 0 0 20px rgba(43, 220, 255, .2);
        }

        .eagles-description {
            color: #a7c2d9;
            font-size: 13px;
            line-height: 1.9;
            margin-top: 20px;
        }

        /* ANALYTICS VISUAL */

        .eagles-analytics {
            margin-top: 35px;
            padding: 20px;

            border: 1px solid rgba(74, 198, 255, .22);
            border-radius: 18px;

            background: rgba(4, 22, 41, .72);
            backdrop-filter: blur(15px);

            animation: borderGlow 5s ease-in-out infinite;
        }

        .analytics-label {
            color: #82b6d4;
            font-size: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .analytics-heading {
            color: #f0fbff;
            font-size: 17px;
            font-weight: 700;
            margin-top: 8px;
        }

        .eagles-chart {
            height: 90px;
            display: flex;
            align-items: flex-end;
            gap: 12px;
            margin-top: 20px;
        }

        .eagles-bar {
            flex: 1;
            min-width: 5px;

            border-radius: 5px 5px 1px 1px;

            background: linear-gradient(
                to top,
                #0077ff,
                #00e5ff
            );

            transform-origin: bottom;
            animation: barAnimation 1.1s ease-out both;
        }

        .eb1 { height: 35%; animation-delay: .1s; }
        .eb2 { height: 60%; animation-delay: .2s; }
        .eb3 { height: 45%; animation-delay: .3s; }
        .eb4 { height: 80%; animation-delay: .4s; }
        .eb5 { height: 58%; animation-delay: .5s; }
        .eb6 { height: 95%; animation-delay: .6s; }
        .eb7 { height: 72%; animation-delay: .7s; }
        .eb8 { height: 87%; animation-delay: .8s; }

        .eagles-brand-footer {
            position: relative;
            z-index: 2;

            margin-top: 35px;

            color: #668ba9;
            font-size: 9px;
            letter-spacing: 2px;
        }

        /* AUTH PANEL */

        .eagles-auth-panel {
            min-height: 650px;
            padding: 35px 30px;

            background: rgba(5, 16, 32, .94);

            border: 1px solid rgba(76, 200, 255, .24);
            border-left: none;
            border-radius: 0 24px 24px 0;

            box-shadow: 0 25px 80px rgba(0, 0, 0, .35);
            backdrop-filter: blur(22px);

            animation: fadeUp .9s ease-out both;
        }

        .secure-label {
            color: #2bdcff;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        .auth-heading {
            color: #f3f9ff;
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -1px;
            margin-top: 15px;
        }

        .auth-description {
            color: #8da9c4;
            font-size: 12px;
            line-height: 1.8;
            margin-top: 10px;
            margin-bottom: 25px;
        }

        /* INPUTS */

        [data-testid="stWidgetLabel"] p {
            color: #c7dced !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }

        [data-testid="stTextInput"] input {
            background: #09182b !important;
            color: #f1faff !important;

            border: 1px solid #23435d !important;
            border-radius: 10px !important;

            min-height: 44px;
            transition: border-color .2s, box-shadow .2s;
        }

        [data-testid="stTextInput"] input:focus {
            border-color: #18cfff !important;
            box-shadow: 0 0 0 3px rgba(24, 207, 255, .12) !important;
        }

        [data-testid="stTextInput"] input::placeholder {
            color: #617e98 !important;
        }

        [data-testid="stCheckbox"] label {
            color: #a7c1d7 !important;
            font-size: 12px !important;
        }

        /* BUTTONS */

        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            width: 100%;
            min-height: 46px;

            color: #ffffff !important;

            background: linear-gradient(
                100deg,
                #0077ff,
                #00bcd4
            ) !important;

            border: 1px solid rgba(70, 220, 255, .3) !important;
            border-radius: 10px !important;

            font-weight: 700 !important;
            transition: all .2s ease;
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 180, 255, .2);
            filter: brightness(1.1);
        }

        /* TABS */

        [data-testid="stTabs"] [role="tablist"] {
            gap: 7px;
            border-bottom: 1px solid #19344b;
        }

        [data-testid="stTabs"] button[role="tab"] {
            color: #91abc1 !important;
            font-size: 12px;
            font-weight: 700;
        }

        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #27dfff !important;
        }

        /* MESSAGES */

        [data-testid="stAlert"] {
            border-radius: 10px;
        }

        hr {
            border-color: #1d354a !important;
        }

        /* RESPONSIVE */

        @media (max-width: 800px) {
            .block-container {
                padding: 1rem;
            }

            .eagles-brand-panel {
                min-height: auto;
                padding: 25px;
                border-radius: 20px 20px 0 0;
            }

            .eagles-headline {
                font-size: 27px;
                margin-top: 25px;
            }

            .eagles-auth-panel {
                min-height: auto;
                padding: 25px 20px;
                border-left: 1px solid rgba(76, 200, 255, .24);
                border-radius: 0 0 20px 20px;
            }

            .eagles-brand-name {
                font-size: 27px;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: .01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: .01ms !important;
            }
        }
        </style>

        <div class="eagles-orb eagles-orb-one"></div>
        <div class="eagles-orb eagles-orb-two"></div>
        """,
        unsafe_allow_html=True
    )

    # =========================================================
    # THEME CONTROL
    # =========================================================

    theme_col = st.columns([6, 1])[1]

    with theme_col:
        theme = st.selectbox(
            "Theme",
            ["Dark", "Light"],
            index=0,
            key="eagles_login_theme",
            label_visibility="collapsed"
        )

    # This authentication page is intentionally designed in dark mode.
    # The theme selector is retained for compatibility with your app.
    # Your existing dashboard theme setting remains separate.

    # =========================================================
    # TWO-PANEL LAYOUT
    # =========================================================

    left, right = st.columns([1.03, 1], gap="small")

    # =========================================================
    # LEFT PANEL - EAGLES BRANDING
    # =========================================================

    with left:
        st.markdown(
            """
            <div class="eagles-brand-panel">

                <div class="eagles-content">

                    <div class="eagles-logo">🦅</div>

                    <div class="eagles-brand-name">
                        EAG<span>LES</span>
                    </div>

                    <div class="eagles-tagline">
                        INTELLIGENCE · PRECISION · PERFORMANCE
                    </div>

                    <div class="eagles-headline">
                        See beyond the numbers.<br>
                        <span>Lead with intelligence.</span>
                    </div>

                    <div class="eagles-description">
                        Discover a smarter way to understand your workforce.
                        Explore employee compensation, performance trends,
                        and department insights through one intelligent
                        analytics workspace.
                    </div>

                    <div class="eagles-analytics">

                        <div class="analytics-label">
                            EAGLES ANALYTICS PLATFORM
                        </div>

                        <div class="analytics-heading">
                            Workforce intelligence
                        </div>

                        <div class="eagles-chart">
                            <div class="eagles-bar eb1"></div>
                            <div class="eagles-bar eb2"></div>
                            <div class="eagles-bar eb3"></div>
                            <div class="eagles-bar eb4"></div>
                            <div class="eagles-bar eb5"></div>
                            <div class="eagles-bar eb6"></div>
                            <div class="eagles-bar eb7"></div>
                            <div class="eagles-bar eb8"></div>
                        </div>

                    </div>

                </div>

                <div class="eagles-brand-footer">
                    EAGLES · EMPLOYEE SALARY & PERFORMANCE ANALYSIS
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # =========================================================
    # RIGHT PANEL - AUTHENTICATION
    # =========================================================

    with right:
        st.markdown(
            """
            <div class="eagles-auth-panel">

                <div class="secure-label">
                    ● SECURE WORKSPACE
                </div>

                <div class="auth-heading">
                    Welcome back
                </div>

                <div class="auth-description">
                    Sign in to your EAGLES workspace and continue
                    exploring your employee analytics dashboard.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        login_tab, register_tab, recovery_tab = st.tabs(
            ["Sign in", "Create account", "Forgot password?"]
        )

        # =====================================================
        # SIGN IN
        # =====================================================

        with login_tab:
            st.markdown("#### Sign in to EAGLES")

            with st.form("eagles_login_form"):
                login_id = st.text_input(
                    "Username or email",
                    placeholder="Enter your username or email",
                    key="eagles_login_id"
                )

                login_password = st.text_input(
                    "Password",
                    placeholder="Enter your password",
                    type="password",
                    key="eagles_login_password"
                )

                remember_me = st.checkbox(
                    "Remember me for this session",
                    key="eagles_remember_me"
                )

                login_submit = st.form_submit_button(
                    "SIGN IN  →",
                    use_container_width=True
                )

            # Pressing Enter in a form field submits the form.

            if login_submit:
                if not login_id.strip() or not login_password:
                    st.warning("Enter your username/email and password.")
                else:
                    try:
                        user = auth.login(
                            login_id.strip(),
                            login_password
                        )

                        if user:
                            st.session_state.user = user
                            st.session_state.login_time = time.time()
                            st.session_state.remember_me = remember_me

                            db.log_activity(
                                user["id"],
                                "signed in"
                            )

                            st.rerun()
                        else:
                            st.error(
                                "Invalid username/email or password."
                            )

                    except PermissionError as exc:
                        st.error(str(exc))

                    except Exception:
                        st.error(
                            "Sign-in is temporarily unavailable. "
                            "Please try again later."
                        )

            st.markdown("---")

            st.markdown(
                """
                <div style="
                    text-align:center;
                    color:#7f9bb5;
                    font-size:11px;
                    line-height:1.9;
                ">
                    🔒 Secure account access<br>
                    Your workforce analytics workspace awaits.
                </div>
                """,
                unsafe_allow_html=True
            )

        # =====================================================
        # REGISTRATION
        # =====================================================

        with register_tab:
            st.markdown("#### Create your EAGLES account")

            with st.form("eagles_register_form"):
                full_name = st.text_input(
                    "Full name",
                    placeholder="Your full name"
                )

                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com"
                )

                username = st.text_input(
                    "Username",
                    placeholder="Choose a username"
                )

                password = st.text_input(
                    "Create password",
                    type="password",
                    placeholder="Use at least 12 characters"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password"
                )

                register_submit = st.form_submit_button(
                    "CREATE ACCOUNT  →",
                    use_container_width=True
                )

            if password:
                score = sum([
                    len(password) >= 12,
                    bool(re.search(r"[A-Z]", password)),
                    bool(re.search(r"[a-z]", password)),
                    bool(re.search(r"\d", password)),
                    bool(re.search(r"[^A-Za-z0-9]", password))
                ])

                if len(password) < 12:
                    st.info(
                        "Password tip: use at least 12 characters."
                    )
                elif score <= 3:
                    st.warning(
                        "Consider using a longer, less predictable password."
                    )
                else:
                    st.success("Password length and variety look good.")

            if register_submit:
                if not all([
                    full_name.strip(),
                    email.strip(),
                    username.strip(),
                    password,
                    confirm_password
                ]):
                    st.warning("Complete all fields.")
                elif not re.fullmatch(
                    r"[^@\s]+@[^@\s]+\.[^@\s]+",
                    email.strip()
                ):
                    st.error("Enter a valid email address.")
                elif len(username.strip()) < 3:
                    st.error("Username must contain at least 3 characters.")
                elif len(password) < 12:
                    st.error("Use a password with at least 12 characters.")
                elif password != confirm_password:
                    st.error("The passwords do not match.")
                else:
                    try:
                        success, message = auth.register(
                            username.strip(),
                            email.strip(),
                            full_name.strip(),
                            password
                        )

                        if success:
                            st.success("Your account has been created.")
                            st.info(
                                "Open the Sign in tab to access EAGLES."
                            )
                        else:
                            st.error(message)

                    except Exception:
                        st.error(
                            "Registration is temporarily unavailable. "
                            "Please try again later."
                        )

        # =====================================================
        # PASSWORD RECOVERY
        # =====================================================

        with recovery_tab:
            st.markdown("#### Recover your account")

            st.write(
                "Enter your registered email address to request "
                "a password reset."
            )

            try:
                email_configured = auth.email_configured()
            except Exception:
                email_configured = False

            if not email_configured:
                st.info(
                    "Email delivery is not configured. Password-reset "
                    "emails require the SMTP settings supported by "
                    "your backend."
                )

            with st.form("eagles_recovery_form"):
                recovery_email = st.text_input(
                    "Registered email",
                    placeholder="Enter your registered email"
                )

                recovery_submit = st.form_submit_button(
                    "REQUEST RESET LINK  →",
                    use_container_width=True
                )

            if recovery_submit:
                if not recovery_email.strip():
                    st.warning("Enter your registered email.")
                elif not re.fullmatch(
                    r"[^@\s]+@[^@\s]+\.[^@\s]+",
                    recovery_email.strip()
                ):
                    st.warning("Enter a valid email address.")
                else:
                    try:
                        sent, user_message, admin_message = (
                            auth.request_password_reset(
                                recovery_email.strip(),
                                APP_BASE_URL
                            )
                        )

                        if sent:
                            st.success(user_message)
                        else:
                            st.warning(user_message)

                            if admin_message:
                                st.caption(admin_message)

                    except Exception:
                        st.error(
                            "We couldn't process the request. "
                            "Please try again later."
                        )

        st.markdown(
            """
            <div style="
                text-align:center;
                color:#66849f;
                font-size:10px;
                line-height:1.8;
                margin-top:24px;
            ">
                EAGLES · Employee Salary & Performance Analysis<br>
                Intelligence for better workforce decisions
            </div>
            """,
            unsafe_allow_html=True
        )
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
            if not e["Employee_ID"].strip() or not e["Name"].strip():
                st.error("Employee ID and name are required.")
            else:
                try:
                    db.add_employee(e)
                    db.log_activity(uid, f"added employee {e['Employee_ID']}")
                    st.success("Employee added. It appears in the table the next time the page refreshes.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"The employee could not be added: {ex}")

    with st.expander("Edit an employee"):
        edit_id = st.selectbox("Employee to edit", df["Employee_ID"], key="edit_emp_select")
        current = df[df["Employee_ID"] == edit_id].iloc[0]
        with st.form("edit_emp"):
            c = st.columns(3)
            e = {
                "Name": c[0].text_input("Name", value=str(current["Name"])),
                "Age": c[1].number_input("Age", 18, 70, int(current["Age"]) if pd.notna(current["Age"]) else 30),
                "Gender": c[2].selectbox("Gender", ["Female", "Male"], index=["Female", "Male"].index(current["Gender"]) if current["Gender"] in ["Female", "Male"] else 0),
                "Department": c[0].selectbox("Department", sorted(df["Department"].unique()), index=sorted(df["Department"].unique()).index(current["Department"])),
                "Designation": c[1].text_input("Designation", value=str(current["Designation"])),
                "Experience_Years": c[2].number_input("Experience (years)", 0, 45, int(current["Experience_Years"])),
                "Joining_Year": c[0].number_input("Joining year", 1990, 2030, int(current["Joining_Year"]) if pd.notna(current["Joining_Year"]) else 2024),
                "Basic_Salary": c[1].number_input("Basic salary", 1.0, 1e7, float(current["Basic_Salary"])),
                "Bonus": c[2].number_input("Bonus", 0.0, 1e6, float(current["Bonus"])),
                "Performance_Score": c[0].number_input("Performance score (0-5)", 0.0, 5.0, float(current["Performance_Score"]), 0.5),
            }
            if st.form_submit_button("Save changes"):
                try:
                    db.update_employee(edit_id, e)
                    db.log_activity(uid, f"edited employee {edit_id}")
                    st.success("Employee updated.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"The employee could not be updated: {ex}")

    with st.expander("Delete an employee"):
        who = st.selectbox("Employee", df["Employee_ID"], key="delete_emp_select")
        confirm = st.checkbox(f"I confirm I want to permanently delete employee {who}.")
        if st.button("Delete employee", disabled=not confirm):
            db.delete_employee(who)
            db.log_activity(uid, f"deleted employee {who}")
            st.success(f"Employee {who} deleted.")
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

    page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1, key="emp_page_size")
    total_pages = max(1, -(-len(f) // page_size))
    page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="emp_page_num")
    start = (page_num - 1) * page_size
    st.caption(f"Page {page_num} of {total_pages}")
    st.dataframe(f.iloc[start:start + page_size], hide_index=True)

    st.download_button("Download filtered records (CSV)", f.to_csv(index=False), "employees_filtered.csv")
    if is_db and st.session_state.user["role"] == "admin":
        manage_employees(df)
def page_analysis(df):
    banner("Salary and performance analysis", "Statistics, experience trends and correlations")
    t1, t2, t3, t4 = st.tabs(["Salary", "Performance", "Correlation", "Percentiles & outliers"])
    with t1:
        st.dataframe(an.salary_summary(df).round(2).to_frame("Value"))
        show(an.fig_salary_dist(df))
        show(an.fig_salary_box_by_dept(df))
        st.subheader("By experience")
        st.dataframe(an.by_experience(df), hide_index=True)
        show(an.fig_experience(df))
        st.subheader("By designation")
        st.dataframe(an.by_designation(df), hide_index=True)
    with t2:
        st.dataframe(an.performance_summary(df).round(2).to_frame("Value"))
        show(an.fig_perf_dist(df))
        show(an.fig_dept_perf(df))
        st.subheader("Top performers")
        st.dataframe(an.top_performers(df), hide_index=True)
    with t3:
        st.dataframe(an.correlation(df).round(2))
        show(an.fig_corr(df))
        st.caption("A correlation shows association, not causation — it does not prove that one factor causes the other.")
    with t4:
        st.subheader("Salary percentiles")
        st.dataframe(an.salary_percentiles(df).to_frame("Salary"))
        st.subheader("Salary bands")
        st.dataframe(an.salary_bands(df), hide_index=True)
        st.subheader("Salary outliers (1.5\u00d7 IQR rule)")
        outliers = an.salary_outliers(df)
        if outliers.empty:
            st.info("No salary outliers were found in the current selection.")
        else:
            st.dataframe(outliers, hide_index=True)


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
    if session_expired():
        db.log_activity(st.session_state.user["id"], "session expired")
        del st.session_state["user"]
        st.session_state.pop("login_time", None)
        st.warning("Your session expired after a period of inactivity. Please sign in again.")
        st.rerun()
        return

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
        theme = st.selectbox(
            "Theme", ["Light", "Dark"],
            index=["Light", "Dark"].index(st.session_state.get("theme", "Light")),
            key="theme_select_main"
        )
        if theme != st.session_state.get("theme", "Light"):
            st.session_state.theme = theme
            st.rerun()
        if st.button("Sign out"):
            db.log_activity(user["id"], "signed out")
            del st.session_state["user"]
            st.session_state.pop("login_time", None)
            st.rerun()
    is_db = src == "Employee database"
    df = db.employee_frame() if is_db else up
    if page == "Dashboard": page_dashboard(df)
    elif page == "Employees": page_employees(df, is_db)
    elif page == "Analysis": page_analysis(df)
    elif page == "Departments": page_departments(df)
    elif page == "Upload and export": page_data(df)
    else: page_admin()


_reset_token = st.query_params.get("reset_token")
if _reset_token and "user" not in st.session_state:
    reset_password_view(_reset_token)
elif "user" not in st.session_state:
    auth_page()
else:
    main()
