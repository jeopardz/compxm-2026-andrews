"""Minimal production logging and optional Sentry error reporting."""
from __future__ import annotations

import logging
import os

import streamlit as st


LOGGER = logging.getLogger("compmastery")


def _setting(key: str, default: str = "") -> str:
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value.strip()
    try:
        return str(st.secrets.get(key, default) or "").strip()
    except Exception:
        return default


def init_monitoring() -> bool:
    """Initialize safe stdout logging and Sentry when SENTRY_DSN is configured."""
    level_name = _setting("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    dsn = _setting("SENTRY_DSN")
    if not dsn:
        LOGGER.info("Sentry disabled; SENTRY_DSN is not configured")
        return False
    try:
        import sentry_sdk

        sample_rate = float(_setting("SENTRY_TRACES_SAMPLE_RATE", "0.05"))
        sentry_sdk.init(
            dsn=dsn,
            environment=_setting("SENTRY_ENVIRONMENT", "production"),
            traces_sample_rate=max(0.0, min(sample_rate, 1.0)),
            send_default_pii=False,
        )
        LOGGER.info("Sentry monitoring enabled")
        return True
    except Exception:
        LOGGER.exception("Sentry initialization failed")
        return False
