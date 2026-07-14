"""Public legal and support pages for the CompMastery web application."""
from __future__ import annotations

from html import escape

import streamlit as st


LAST_UPDATED = "14 July 2026"


def _secret(key: str, default: str = "") -> str:
    try:
        value = st.secrets.get(key, default)
    except Exception:
        value = default
    return str(value or "").strip()


def support_email() -> str:
    """Return the configured public support address without inventing one."""
    configured = _secret("SUPPORT_EMAIL")
    if configured:
        return configured
    admins = _secret("ADMIN_EMAILS")
    return admins.split(",", 1)[0].strip() if admins else ""


def render_legal_links() -> None:
    """Render links that remain available before and after authentication."""
    st.markdown(
        '<div style="text-align:center;font-size:12px;color:#718096;margin-top:12px">'
        '<a href="?legal=privacy" target="_self">Privacy</a> &nbsp;·&nbsp; '
        '<a href="?legal=terms" target="_self">Terms</a> &nbsp;·&nbsp; '
        '<a href="?legal=support" target="_self">Support</a>'
        '</div>',
        unsafe_allow_html=True,
    )


def _contact_block() -> None:
    email = support_email()
    if email and not email.lower().endswith((".example", ".invalid", ".local")):
        safe = escape(email, quote=True)
        st.markdown(f'Contact: <a href="mailto:{safe}">{safe}</a>', unsafe_allow_html=True)
    else:
        st.warning("Temporary support placeholder only. Set a working SUPPORT_EMAIL before public launch.")


def _privacy() -> None:
    st.title("CompMastery Privacy Notice")
    st.caption(f"Last updated: {LAST_UPDATED}")
    st.markdown(
        """
CompMastery collects the minimum information needed to operate the service: your email
address and account identifier, saved game decisions and results, entitlement and
transaction references, and basic technical logs used for security and reliability.

We use this information to authenticate users, save games, provide purchased access,
prevent abuse, troubleshoot failures, and improve service reliability. Payment-card
details are handled by Lemon Squeezy and are not stored by CompMastery.

Service data may be processed by infrastructure providers used to run CompMastery,
including Supabase, Streamlit Community Cloud, Lemon Squeezy, and an error-monitoring
provider when one is configured. We do not sell personal information.

We retain account and gameplay data while the account is active and as reasonably
needed for security, accounting, dispute resolution, and legal obligations. You may
request access, correction, or deletion of your account data by contacting support.

We use reasonable technical safeguards, but no online service can guarantee absolute
security. CompMastery is not directed to children under 13. This notice may be updated as
the service or legal requirements change.
"""
    )
    _contact_block()


def _terms() -> None:
    st.title("CompMastery Terms of Service")
    st.caption(f"Last updated: {LAST_UPDATED}")
    st.markdown(
        """
By creating an account or using CompMastery, you agree to these terms. You must provide
accurate account information, keep your credentials secure, and use the service only
for lawful personal or educational purposes.

CompMastery provides a business-strategy practice simulation. Results, scores, projections,
and reports are educational and are not financial, investment, legal, or professional
advice. Outcomes in the simulation do not guarantee real-world results.

Paid access is for the duration and price shown at checkout. Payments are processed
by Lemon Squeezy. Refund requests must be made through support and are evaluated under
the checkout terms and applicable law. Deleting a game does not restore a consumed
demo or extend paid access.

You may not interfere with the service, bypass access controls, scrape or overload the
application, misuse another person's account, or copy and resell the service. CompMastery
may suspend access when reasonably necessary to protect users, the service, or comply
with law.

The service is provided on an as-available basis. To the maximum extent permitted by
law, CompMastery is not liable for indirect or consequential loss. Nothing in these terms
limits rights that cannot legally be excluded. We may update these terms and will post
the revised date on this page.
"""
    )
    _contact_block()


def _support() -> None:
    st.title("CompMastery Support")
    st.markdown(
        """
For account access, billing, payment unlocks, data requests, or technical problems,
contact us with the email address used for your CompMastery account. Do not send passwords,
full card numbers, access tokens, or other secrets.

For billing questions, include the Lemon Squeezy order reference from your receipt.
"""
    )
    _contact_block()


def render_public_page_if_requested() -> None:
    """Render a query-addressable public page before the authentication gate."""
    page = st.query_params.get("legal")
    if isinstance(page, list):
        page = page[0] if page else None
    page = str(page or "").lower()
    renderers = {"privacy": _privacy, "terms": _terms, "support": _support}
    if page not in renderers:
        return
    renderers[page]()
    st.markdown("[Back to CompMastery](?)")
    render_legal_links()
    st.stop()
