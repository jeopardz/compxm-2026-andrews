from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_public_legal_and_support_surface_is_wired():
    legal = (ROOT / "sim" / "legal.py").read_text(encoding="utf-8")
    app = (ROOT / "sim" / "app.py").read_text(encoding="utf-8")
    auth = (ROOT / "sim" / "auth.py").read_text(encoding="utf-8")
    for route in ("privacy", "terms", "support"):
        assert f'"{route}"' in legal
    assert "render_public_page_if_requested()" in app
    assert "render_legal_links()" in app
    assert "render_legal_links()" in auth
    assert "SUPPORT_EMAIL" in legal


def test_monitoring_never_enables_default_pii():
    source = (ROOT / "sim" / "monitoring.py").read_text(encoding="utf-8")
    assert "send_default_pii=False" in source
    assert "SENTRY_DSN" in source
