import datetime
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from pile_tracker.models import Location
from pile_tracker.models import Log
from pile_tracker.models import Pile

pytestmark = pytest.mark.django_db


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


def make_pile(pile_id, location, born_date=datetime.date(2026, 1, 1)):
    return Pile.objects.create(id=pile_id, born_date=born_date, location=location)


# --- Log form -----------------------------------------------------------------


def test_invalid_log_form_is_shown_again_with_errors(client, primary):
    make_pile("1", primary)

    response = client.post(reverse("log-create"), {"date": "not a date", "pile": "1"})

    assert response.status_code == 200
    assert response.context["form"].errors
    assert Log.objects.count() == 0


def test_log_saves_air_temp(client, primary):
    make_pile("1", primary)

    client.post(
        reverse("log-create"),
        {"date": "2026-11-09 08:00", "pile": "1", "air_temp": "41"},
    )

    assert Log.objects.get().air_temp == 41


def test_log_form_defaults_to_pile_in_primary(client, collection, primary):
    make_pile("1", collection)
    in_primary = make_pile("2", primary)

    response = client.get(reverse("log-create"))

    assert response.context["form"].initial["pile"] == in_primary


def test_log_form_loads_when_weather_api_is_down(client):
    response = client.get(reverse("log-create"))

    assert response.status_code == 200


def test_log_with_new_location_moves_the_pile(client, collection, primary):
    make_pile("1", collection)

    client.post(
        reverse("log-create"),
        {"date": "2026-11-09 08:00", "pile": "1", "location": "Primary"},
    )

    assert Pile.objects.get(id="1").location == primary


def test_get_cur_temp_returns_none_when_api_unreachable():
    assert Log.get_cur_temp() is None


# --- Pile form ----------------------------------------------------------------


def test_invalid_pile_form_is_shown_again_with_errors(client):
    response = client.post(reverse("pile-create"), {"id": "", "born_date": "x"})

    assert response.status_code == 200
    assert response.context["form"].errors
    assert Pile.objects.count() == 0


def test_new_pile_requires_a_location(client):
    response = client.post(
        reverse("pile-create"),
        {"id": "7", "born_date": "2026-11-09", "location": ""},
    )

    assert response.status_code == 200
    assert "location" in response.context["form"].errors


def test_new_pile_location_must_be_set_up(client, primary):
    # The dropdown offers Collection, but no Collection location exists yet.
    response = client.post(
        reverse("pile-create"),
        {"id": "7", "born_date": "2026-11-09", "location": "Collection"},
    )

    assert response.status_code == 200
    assert "location" in response.context["form"].errors


def test_log_location_must_be_set_up(client, primary):
    make_pile("1", primary)

    response = client.post(
        reverse("log-create"),
        {"date": "2026-11-09 08:00", "pile": "1", "location": "Secondary"},
    )

    assert "location" in response.context["form"].errors
    assert Log.objects.count() == 0


def test_new_pile_cannot_overwrite_existing_pile(client, collection, primary):
    make_pile("1", primary, born_date=datetime.date(2025, 5, 5))

    response = client.post(
        reverse("pile-create"),
        {"id": "1", "born_date": "2026-11-09", "location": "Collection"},
    )

    assert "id" in response.context["form"].errors
    pile = Pile.objects.get(id="1")
    assert pile.born_date == datetime.date(2025, 5, 5)
    assert pile.location == primary


# --- Home page ----------------------------------------------------------------


def test_home_page_with_no_piles(client):
    response = client.get(reverse("index"))

    assert response.status_code == 200
    assert response.context["next_pile"] is None


def test_home_page_when_every_pile_is_curing(client, cure):
    make_pile("1", cure)

    response = client.get(reverse("index"))

    assert response.status_code == 200
    assert response.context["next_pile"] is None


def test_home_page_when_location_has_no_days_at_state(client, collection):
    collection.days_at_state = None
    collection.save()
    make_pile("1", collection)

    response = client.get(reverse("index"))

    assert response.status_code == 200


def test_home_page_picks_soonest_move_even_with_ties(client, collection, primary):
    # All born the same day; Primary (3 days) is due before Collection (30 days).
    make_pile("1", collection)
    make_pile("2", primary)
    make_pile("3", primary)

    response = client.get(reverse("index"))

    assert response.context["next_pile"] in {"2", "3"}
    assert response.context["next_date"].date() == datetime.date(2026, 1, 4)


def test_home_page_finds_pile_in_primary_by_name(client, primary):
    # Primary is location id 1 here, not 2.
    make_pile("1", primary)

    response = client.get(reverse("index"))

    assert response.context["whos_in_primary"].id == "1"


# --- Pile detail --------------------------------------------------------------


def test_pile_detail_dates_are_timezone_aware(client, primary):
    make_pile("1", primary)

    response = client.get(reverse("pile-detail", args=["1"]))

    assert timezone.is_aware(response.context["last_turned"])
    assert timezone.is_aware(response.context["last_moved"])


def test_pile_detail_works_for_non_numeric_pile_id(client, primary):
    make_pile("A1", primary)

    response = client.get(reverse("pile-detail", args=["A1"]))

    assert response.status_code == 200


def test_pile_detail_chart_includes_zero_degree_reading(client, primary):
    pile = make_pile("1", primary)
    Log.objects.create(pile=pile, temp=0, date=timezone.now())

    response = client.get(reverse("pile-detail", args=["1"]))

    assert len(response.context["data"]) == 1


def test_new_log_date_defaults_to_aware_datetime(primary):
    log = Log.objects.create(pile=make_pile("1", primary))

    assert timezone.is_aware(log.date)
