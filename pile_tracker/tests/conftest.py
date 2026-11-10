from unittest import mock

import pytest

from pile_tracker.models import Location


@pytest.fixture(autouse=True)
def enable_db(db):
    """Every test in this package uses the test database."""


@pytest.fixture(autouse=True)
def weather_api_down():
    """Never reach the real weather API from tests; act as if it's unreachable."""
    with mock.patch("pile_tracker.models.request.urlopen", side_effect=OSError):
        yield


@pytest.fixture
def collection():
    return Location.objects.create(location="Collection", days_at_state=30)


@pytest.fixture
def primary():
    return Location.objects.create(location="Primary", days_at_state=3)


@pytest.fixture
def cure():
    return Location.objects.create(location="Cure/Storage", days_at_state=90)
