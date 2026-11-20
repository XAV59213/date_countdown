"""Fixtures communes."""
import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Active custom_components/ pour tous les tests."""
    yield
