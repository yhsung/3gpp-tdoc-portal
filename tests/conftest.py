"""Pytest configuration and shared fixtures for the 3GPP TDoc Portal test suite."""
import sys
from unittest.mock import MagicMock


def _make_cache_data():
    """Return a pass-through replacement for st.cache_data.

    The real st.cache_data decorator requires an active Streamlit server for
    some operations.  In tests we want the decorated function to behave like an
    ordinary function while still exposing the .clear() method that the
    production code calls.
    """

    def cache_data(func=None, *, ttl=None, show_spinner=True, **kwargs):
        def decorator(f):
            f.clear = MagicMock()
            return f

        if func is not None:
            # Called as @st.cache_data without parentheses
            func.clear = MagicMock()
            return func
        # Called as @st.cache_data(...) with keyword arguments
        return decorator

    return cache_data


# Inject mock before any portal module is imported so that the
# @st.cache_data decorator at module-load time of portal.fetcher is
# replaced with the pass-through version above.
_st_mock = MagicMock()
_st_mock.cache_data = _make_cache_data()
sys.modules.setdefault("streamlit", _st_mock)

# Mock heavy/optional dependencies so that download_tdocs (and portal modules
# that import it) can be loaded in the test environment without requiring the
# full production dependency set.
for _mod in (
    "docling",
    "docling.document_converter",
    "tqdm",
):
    sys.modules.setdefault(_mod, MagicMock())
