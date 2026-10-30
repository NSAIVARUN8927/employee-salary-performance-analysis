"""Firebase Authentication REST helpers for the PeoplePulse Streamlit app.

Uses Firebase Identity Toolkit REST endpoints; no Admin SDK or service-account
private key is required for client-side email/password authentication.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts:{}?{}"


class FirebaseAuthError(Exception):
    """Readable Firebase Authentication error."""

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(message)


def _post(action, api_key, payload):
    if not api_key:
        raise FirebaseAuthError("CONFIG_MISSING", "Firebase API key is missing from Streamlit Secrets.")

    url = BASE_URL.format(action, urlencode({"key": api_key}))
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            data = json.loads(exc.read().decode("utf-8"))
            raw = data.get("error", {}).get("message", "FIREBASE_REQUEST_FAILED")
        except Exception:
            raw = "FIREBASE_REQUEST_FAILED"
        code = raw.split(" : ")[0].split(" ")[0]
        messages = {
            "EMAIL_EXISTS": "This email is already registered with Firebase.",
            "EMAIL_NOT_FOUND": "No Firebase account was found for this email.",
            "INVALID_PASSWORD": "The Firebase password is incorrect.",
            "INVALID_LOGIN_CREDENTIALS": "The email or password is incorrect.",
            "USER_DISABLED": "This Firebase account has been disabled.",
            "WEAK_PASSWORD": "Firebase requires a stronger password (at least 6 characters).",
            "INVALID_EMAIL": "Enter a valid email address.",
            "OPERATION_NOT_ALLOWED": "Email/password sign-in is not enabled in Firebase Authentication.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please try again later.",
            "EXPIRED_OOB_CODE": "This password-reset link has expired. Request a new one.",
            "INVALID_OOB_CODE": "This password-reset link is invalid or has already been used.",
            "CONFIG_MISSING": "Firebase configuration is missing.",
        }
        raise FirebaseAuthError(code, messages.get(code, "Firebase could not complete the request. Check Authentication settings and try again.")) from None
    except (URLError, TimeoutError):
        raise FirebaseAuthError("NETWORK_ERROR", "Could not connect to Firebase. Check your internet connection and try again.") from None
    except (ValueError, json.JSONDecodeError):
        raise FirebaseAuthError("INVALID_RESPONSE", "Firebase returned an unexpected response.") from None


def sign_up(email, password, api_key):
    return _post("signUp", api_key, {
        "email": email.strip().lower(),
        "password": password,
        "returnSecureToken": True,
    })


def sign_in(email, password, api_key):
    return _post("signInWithPassword", api_key, {
        "email": email.strip().lower(),
        "password": password,
        "returnSecureToken": True,
    })


def send_password_reset(email, api_key, continue_url):
    return _post("sendOobCode", api_key, {
        "requestType": "PASSWORD_RESET",
        "email": email.strip().lower(),
        "continueUrl": continue_url,
    })
