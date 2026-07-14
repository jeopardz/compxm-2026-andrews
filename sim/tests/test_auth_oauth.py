from types import SimpleNamespace

import pytest

from sim import auth


class RerunRequested(BaseException):
    pass


class FakeCookieManager:
    def __init__(self):
        self.values = {}
        self.set_calls = []
        self.deleted = []

    def get(self, key):
        return self.values.get(key)

    def set(self, cookie, value, **kwargs):
        self.values[cookie] = value
        self.set_calls.append((cookie, value, kwargs))

    def delete(self, cookie, **kwargs):
        self.values.pop(cookie, None)
        self.deleted.append((cookie, kwargs))


class FakeStreamlit:
    def __init__(self, *, url="https://example.test/app", cookies=None, secrets=None):
        self.session_state = {}
        self.query_params = {}
        self.secrets = secrets or {}
        self.context = SimpleNamespace(url=url, cookies=cookies or {})

    @staticmethod
    def rerun():
        raise RerunRequested


def test_pkce_storage_persists_only_verifier_in_short_lived_cookie(monkeypatch):
    fake_st = FakeStreamlit()
    manager = FakeCookieManager()
    fake_st.session_state["_cookie_mgr"] = manager
    monkeypatch.setattr(auth, "st", fake_st)

    storage = auth._SupabaseAuthStorage()
    storage.set_item("supabase.auth.token", "session-json")
    storage.set_item("supabase.auth.token-code-verifier", "pkce-secret")

    assert storage.get_item("supabase.auth.token") == "session-json"
    assert storage.get_item("supabase.auth.token-code-verifier") == "pkce-secret"
    assert auth._COOKIE_KEY not in manager.values
    assert manager.values[auth._OAUTH_PKCE_COOKIE_KEY] == "pkce-secret"
    assert manager.set_calls[-1][2]["secure"] is True
    assert manager.set_calls[-1][2]["same_site"] == "lax"

    storage.remove_item("supabase.auth.token-code-verifier")
    assert storage.get_item("supabase.auth.token-code-verifier") is None
    assert manager.deleted[-1][0] == auth._OAUTH_PKCE_COOKIE_KEY


def test_pkce_storage_reads_verifier_from_initial_request_cookie(monkeypatch):
    fake_st = FakeStreamlit(cookies={auth._OAUTH_PKCE_COOKIE_KEY: "from-request"})
    monkeypatch.setattr(auth, "st", fake_st)

    storage = auth._SupabaseAuthStorage()

    assert storage.get_item("project-auth-token-code-verifier") == "from-request"


def test_oauth_redirect_url_uses_configured_public_url_without_query(monkeypatch):
    fake_st = FakeStreamlit(
        url="https://internal.test/ignored?old=1",
        secrets={"APP_URL": "https://public.example.com/path?unsafe=1#fragment"},
    )
    monkeypatch.setattr(auth, "st", fake_st)

    assert auth._oauth_redirect_url() == "https://public.example.com/path"


def test_google_oauth_url_uses_pkce_client_and_is_cached(monkeypatch):
    fake_st = FakeStreamlit(url="https://app.example.com/")
    monkeypatch.setattr(auth, "st", fake_st)
    calls = []

    class FakeAuth:
        @staticmethod
        def sign_in_with_oauth(payload):
            calls.append(payload)
            return SimpleNamespace(url="https://accounts.google.test/oauth")

    monkeypatch.setattr(
        auth,
        "get_supabase",
        lambda: SimpleNamespace(auth=FakeAuth()),
    )

    first = auth._google_oauth_url()
    second = auth._google_oauth_url()

    assert first == second == "https://accounts.google.test/oauth"
    assert calls == [
        {
            "provider": "google",
            "options": {"redirect_to": "https://app.example.com/"},
        }
    ]


def test_installed_supabase_client_writes_pkce_verifier_through_storage(monkeypatch):
    fake_st = FakeStreamlit(
        url="https://app.example.com/",
        secrets={
            "SUPABASE_URL": "https://project-ref.supabase.co",
            "SUPABASE_ANON_KEY": "anon-key",
        },
    )
    manager = FakeCookieManager()
    fake_st.session_state["_cookie_mgr"] = manager
    monkeypatch.setattr(auth, "st", fake_st)

    response = auth.get_supabase().auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {"redirect_to": "https://app.example.com/"},
        }
    )

    assert response.url.startswith("https://project-ref.supabase.co/auth/v1/authorize?")
    assert manager.values[auth._OAUTH_PKCE_COOKIE_KEY]


def test_oauth_callback_exchanges_code_and_stores_session(monkeypatch):
    fake_st = FakeStreamlit(cookies={auth._OAUTH_PKCE_COOKIE_KEY: "verifier"})
    manager = FakeCookieManager()
    manager.values[auth._OAUTH_PKCE_COOKIE_KEY] = "verifier"
    fake_st.session_state.update(
        {
            "_cookie_mgr": manager,
            auth._OAUTH_URL_STATE_KEY: "old-oauth-url",
        }
    )
    fake_st.query_params.update({"code": "one-time-code", "unrelated": "keep"})
    monkeypatch.setattr(auth, "st", fake_st)

    session = object()
    exchanged = []
    stored = []

    class FakeAuth:
        @staticmethod
        def exchange_code_for_session(payload):
            exchanged.append(payload)
            return SimpleNamespace(session=session)

    monkeypatch.setattr(
        auth,
        "get_supabase",
        lambda: SimpleNamespace(auth=FakeAuth()),
    )
    monkeypatch.setattr(auth, "_store_session", stored.append)

    with pytest.raises(RerunRequested):
        auth._handle_oauth_callback()

    assert exchanged == [{"auth_code": "one-time-code"}]
    assert stored == [session]
    assert fake_st.query_params == {"unrelated": "keep"}
    assert auth._OAUTH_URL_STATE_KEY not in fake_st.session_state
    assert manager.deleted[-1][0] == auth._OAUTH_PKCE_COOKIE_KEY


def test_oauth_callback_rejects_code_without_pkce_verifier(monkeypatch):
    fake_st = FakeStreamlit()
    fake_st.query_params["code"] = "one-time-code"
    monkeypatch.setattr(auth, "st", fake_st)

    with pytest.raises(RerunRequested):
        auth._handle_oauth_callback()

    assert "code" not in fake_st.query_params
    assert "expired" in fake_st.session_state[auth._OAUTH_ERROR_STATE_KEY]
