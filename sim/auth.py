"""Authentication layer for the SaaS build (Supabase Auth).

DUAL-MODE — this is the load-bearing rule:
  * AUTH_ENABLED is False by default (and whenever there is no secrets file), so
    the existing single-user local study app runs EXACTLY as before and never
    imports `supabase`. Every supabase import here is lazy (inside a function) so
    the package need not even be installed for local mode.
  * When AUTH_ENABLED is True (production), users sign in and each one's games are
    isolated by Supabase Row Level Security.

Nothing here runs unless authentication is enabled.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

import streamlit as st

# Cookie that persists the Supabase refresh token across full page reloads, so a
# signed-in user stays signed in. Refresh tokens rotate on each use; the cookie is
# rewritten every time we mint a new session.
#
# Rewritten on a normal render after sign-in so the cookie component can flush.
_PERSIST_LOGIN = True
_COOKIE_KEY = "compmastery_sb_refresh"
_COOKIE_DAYS = 30
_OAUTH_PKCE_COOKIE_KEY = "compmastery_sb_pkce"
_OAUTH_PKCE_MINUTES = 10
_OAUTH_URL_STATE_KEY = "_google_oauth_url"
_OAUTH_ERROR_STATE_KEY = "_oauth_error"
_OAUTH_QUERY_KEYS = ("code", "error", "error_code", "error_description")


# ------------------------------------------------------------------
# configuration
# ------------------------------------------------------------------

def _secret(key: str, default=None):
    """Read a Streamlit secret without crashing when no secrets file exists."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def auth_enabled() -> bool:
    """True only when running as the multi-user SaaS. Defaults False everywhere
    else so the local study app is completely unaffected."""
    val = _secret("AUTH_ENABLED", False)
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on")
    return bool(val)


def get_supabase():
    """Return a Supabase client isolated to this Streamlit browser session."""
    from supabase import ClientOptions, create_client  # lazy: not needed locally

    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_ANON_KEY missing from secrets")
    client = st.session_state.get("_supabase_client")
    if client is None:
        # Supabase OAuth uses PKCE by default. Its code verifier normally lives in
        # process-local storage, but an OAuth redirect can create a new Streamlit
        # session. Keep only that short-lived verifier in a browser cookie so the
        # callback can exchange the authorization code reliably.
        options = ClientOptions(flow_type="pkce", storage=_SupabaseAuthStorage())
        client = create_client(url, key, options=options)
        st.session_state["_supabase_client"] = client
    return client


# ------------------------------------------------------------------
# cookie persistence (refresh token survives page reloads)
# ------------------------------------------------------------------

def init_cookies() -> None:
    """Create the run's CookieManager (a widget, so it must be built fresh each run
    — NOT cached). Call ONCE per run, before require_login(). No-op off SaaS mode
    or when persistent login is disabled (then _cm() is None and all cookie helpers
    are no-ops, so login is session-only)."""
    if not auth_enabled() or not _PERSIST_LOGIN:
        return
    try:
        import extra_streamlit_components as stx
        st.session_state["_cookie_mgr"] = stx.CookieManager(key="compmastery_cookies")
    except Exception:
        st.session_state["_cookie_mgr"] = None


def _cm():
    return st.session_state.get("_cookie_mgr")


def _context_cookie_get(key: str) -> Optional[str]:
    """Read a cookie from the initial HTTP request when the component is loading."""
    try:
        return st.context.cookies.get(key)
    except Exception:
        return None


def _is_https() -> bool:
    try:
        return str(st.context.url).lower().startswith("https://")
    except Exception:
        return True


def _cookie_get() -> Optional[str]:
    cm = _cm()
    if cm is None:
        return None
    try:
        return cm.get(_COOKIE_KEY)
    except Exception:
        return None


def _cookie_set(refresh_token: str) -> None:
    cm = _cm()
    if cm is None:
        return
    try:
        cm.set(_COOKIE_KEY, refresh_token, key="cookie_set",
               expires_at=datetime.now(timezone.utc) + timedelta(days=_COOKIE_DAYS))
    except Exception:
        pass


def _cookie_delete() -> None:
    cm = _cm()
    if cm is None:
        return
    try:
        cm.delete(_COOKIE_KEY, key="cookie_del")
    except Exception:
        pass


def _oauth_verifier_get() -> Optional[str]:
    cm = _cm()
    if cm is not None:
        try:
            value = cm.get(_OAUTH_PKCE_COOKIE_KEY)
            if value:
                return value
        except Exception:
            pass
    return _context_cookie_get(_OAUTH_PKCE_COOKIE_KEY)


def _oauth_verifier_set(value: str) -> None:
    cm = _cm()
    if cm is None:
        return
    try:
        cm.set(
            _OAUTH_PKCE_COOKIE_KEY,
            value,
            key="oauth_pkce_set",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=_OAUTH_PKCE_MINUTES),
            secure=_is_https(),
            same_site="lax",
        )
    except Exception:
        pass


def _oauth_verifier_delete() -> None:
    cm = _cm()
    if cm is None:
        return
    try:
        cm.delete(_OAUTH_PKCE_COOKIE_KEY, key="oauth_pkce_del")
    except Exception:
        pass


class _SupabaseAuthStorage:
    """Session storage with durable, short-lived handling for the PKCE verifier."""

    def _state(self) -> dict:
        return st.session_state.setdefault("_supabase_auth_storage", {})

    @staticmethod
    def _is_code_verifier(key: str) -> bool:
        return key.endswith("-code-verifier")

    def get_item(self, key: str) -> Optional[str]:
        if self._is_code_verifier(key):
            return _oauth_verifier_get() or self._state().get(key)
        return self._state().get(key)

    def set_item(self, key: str, value: str) -> None:
        self._state()[key] = value
        if self._is_code_verifier(key):
            _oauth_verifier_set(value)

    def remove_item(self, key: str) -> None:
        self._state().pop(key, None)
        if self._is_code_verifier(key):
            _oauth_verifier_delete()


# ------------------------------------------------------------------
# session helpers
# ------------------------------------------------------------------

def current_user_id() -> Optional[str]:
    return st.session_state.get("user_id")


def current_user_email() -> Optional[str]:
    return st.session_state.get("user_email")


def is_logged_in() -> bool:
    return bool(current_user_id())


def _store_session(session) -> None:
    """Persist tokens + identity into st.session_state, the cookie, and re-arm
    the client."""
    st.session_state["sb_access_token"] = session.access_token
    st.session_state["sb_refresh_token"] = session.refresh_token
    st.session_state["user_id"] = session.user.id
    st.session_state["user_email"] = session.user.email
    st.session_state.pop(_OAUTH_URL_STATE_KEY, None)
    _oauth_verifier_delete()
    if session.refresh_token:
        _cookie_set(session.refresh_token)


def restore_session() -> bool:
    """Re-attach a session to the client. Tries in-memory session_state first, then
    the persistent cookie (survives a full page reload). Returns True if active."""
    if not auth_enabled():
        return False
    # 1) Same Streamlit session — tokens already in session_state.
    access = st.session_state.get("sb_access_token")
    refresh = st.session_state.get("sb_refresh_token")
    if access and refresh:
        try:
            get_supabase().auth.set_session(access, refresh)
            return True
        except Exception:
            clear_session()
    # 2) After a reload — recover from the cookie's refresh token.
    cookie_refresh = _cookie_get()
    if cookie_refresh:
        try:
            res = get_supabase().auth.refresh_session(cookie_refresh)
            if res and res.session:
                _store_session(res.session)
                return True
        except Exception:
            _cookie_delete()
    return False


def clear_session() -> None:
    for k in ("sb_access_token", "sb_refresh_token", "user_id", "user_email",
              "_full_access_cache", "_cookie_written", "_supabase_client",
              "_supabase_auth_storage", _OAUTH_URL_STATE_KEY,
              _OAUTH_ERROR_STATE_KEY):
        st.session_state.pop(k, None)
    _cookie_delete()
    _oauth_verifier_delete()


# ------------------------------------------------------------------
# auth actions
# ------------------------------------------------------------------

def sign_in(email: str, password: str) -> tuple[bool, str]:
    try:
        res = get_supabase().auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            _store_session(res.session)
            return True, ""
        return False, "Invalid credentials"
    except Exception:  # never expose provider/internal details in the UI
        return False, "Sign in failed. Check your email and password, then try again."


def sign_up(email: str, password: str) -> tuple[bool, str]:
    try:
        res = get_supabase().auth.sign_up({"email": email, "password": password})
        # If email confirmation is off, a session is returned and we log in directly.
        if res.session:
            _store_session(res.session)
            return True, ""
        return True, "Check your email to confirm your account, then sign in."
    except Exception:
        return False, "Account creation failed. Check the details or try again shortly."


def send_password_reset(email: str) -> tuple[bool, str]:
    try:
        get_supabase().auth.reset_password_for_email(email)
        return True, "Password reset email sent."
    except Exception:
        return False, "Could not send the reset email. Try again shortly."


def sign_out() -> None:
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    clear_session()


def _oauth_redirect_url() -> str:
    """Return this deployment's stable callback URL without query parameters."""
    configured = str(_secret("APP_URL", "") or "").strip()
    current = configured or str(st.context.url)
    parsed = urlsplit(current)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", "", ""))


def _google_oauth_url() -> Optional[str]:
    """Create one Google authorization URL per Streamlit browser session."""
    cached = st.session_state.get(_OAUTH_URL_STATE_KEY)
    if cached:
        return cached
    try:
        response = get_supabase().auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {"redirect_to": _oauth_redirect_url()},
            }
        )
        url = getattr(response, "url", None)
        if url:
            st.session_state[_OAUTH_URL_STATE_KEY] = url
            return url
    except Exception:
        pass
    return None


def _clear_oauth_query_params() -> None:
    for key in _OAUTH_QUERY_KEYS:
        try:
            del st.query_params[key]
        except (KeyError, AttributeError):
            pass


def _handle_oauth_callback() -> None:
    """Exchange Google's one-time callback code for a Supabase user session."""
    try:
        code = st.query_params.get("code")
        provider_error = st.query_params.get("error")
    except Exception:
        return

    if provider_error:
        _clear_oauth_query_params()
        _oauth_verifier_delete()
        st.session_state.pop(_OAUTH_URL_STATE_KEY, None)
        st.session_state[_OAUTH_ERROR_STATE_KEY] = (
            "Google sign-in was cancelled or could not be completed. Please try again."
        )
        st.rerun()

    if not code:
        return

    if not _oauth_verifier_get():
        _clear_oauth_query_params()
        st.session_state.pop(_OAUTH_URL_STATE_KEY, None)
        st.session_state[_OAUTH_ERROR_STATE_KEY] = (
            "The Google sign-in session expired. Please start again."
        )
        st.rerun()

    try:
        response = get_supabase().auth.exchange_code_for_session({"auth_code": code})
        if not response or not response.session:
            raise RuntimeError("OAuth callback returned no session")
        _store_session(response.session)
        _oauth_verifier_delete()
        st.session_state.pop(_OAUTH_URL_STATE_KEY, None)
        _clear_oauth_query_params()
        st.rerun()
    except Exception:
        _oauth_verifier_delete()
        st.session_state.pop(_OAUTH_URL_STATE_KEY, None)
        _clear_oauth_query_params()
        st.session_state[_OAUTH_ERROR_STATE_KEY] = (
            "Google sign-in failed. Please try again."
        )
        st.rerun()


# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------

def render_login_page() -> None:
    """Render the sign-in / sign-up / reset UI. Call require_login() instead of
    this directly unless you need custom placement."""
    st.title("CompMastery")
    st.subheader("Competitive business simulation in four focused rounds")
    st.markdown(
        "- Make product, marketing, operations, people and finance decisions\n"
        "- Play validated scenarios across three difficulty levels\n"
        "- Review market reports and a balanced scorecard after every round"
    )
    st.caption("Sign in to save your games and track your progress.")

    oauth_error = st.session_state.pop(_OAUTH_ERROR_STATE_KEY, None)
    if oauth_error:
        st.error(oauth_error)

    google_url = _google_oauth_url()
    if google_url:
        st.link_button("Continue with Google", google_url, width="stretch")
        st.caption("Or continue with email")
    else:
        st.warning("Google sign-in is temporarily unavailable. You can still use email.")

    tab_in, tab_up, tab_reset = st.tabs(["Sign in", "Create account", "Forgot password"])

    with tab_in:
        with st.form("sign_in_form"):
            email = st.text_input("Email", key="si_email")
            password = st.text_input("Password", type="password", key="si_pw")
            if st.form_submit_button("Sign in", width="stretch"):
                ok, msg = sign_in(email.strip(), password)
                if ok:
                    st.rerun()
                else:
                    st.error(msg or "Sign in failed")

    with tab_up:
        with st.form("sign_up_form"):
            email = st.text_input("Email", key="su_email")
            password = st.text_input("Password (min 6 chars)", type="password", key="su_pw")
            if st.form_submit_button("Create account", width="stretch"):
                ok, msg = sign_up(email.strip(), password)
                if ok and not msg:
                    st.rerun()
                elif ok:
                    st.success(msg)
                else:
                    st.error(msg or "Sign up failed")

    with tab_reset:
        with st.form("reset_form"):
            email = st.text_input("Email", key="rs_email")
            if st.form_submit_button("Send reset link", width="stretch"):
                ok, msg = send_password_reset(email.strip())
                (st.success if ok else st.error)(msg)

    from sim.legal import render_legal_links
    render_legal_links()


def require_login() -> None:
    """Gate the app: in SaaS mode, show the login page and stop unless signed in.
    In local mode this is a no-op, so the study app is unchanged."""
    if not auth_enabled():
        return
    _handle_oauth_callback()
    if not is_logged_in():
        restore_session()
    if not is_logged_in():
        render_login_page()
        st.stop()
    # Logged in: re-assert the persistence cookie on this (non-interrupted) run so
    # it actually flushes to the browser. Writing it only during sign-in doesn't
    # persist, because the immediate st.rerun() cuts the run before the cookie
    # component sends its value. Refreshing here on a normal render fixes that.
    refresh = st.session_state.get("sb_refresh_token")
    if refresh and not st.session_state.get("_cookie_written"):
        _cookie_set(refresh)
        st.session_state["_cookie_written"] = True


def render_logout(sidebar: bool = True) -> None:
    target = st.sidebar if sidebar else st
    if is_logged_in():
        target.caption(f"Signed in as {current_user_email()}")
        if target.button("Sign out", width="stretch"):
            sign_out()
            st.rerun()
