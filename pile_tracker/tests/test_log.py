"""Add Log page: LOG001-LOG004."""

import json
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertRedirects

from pile_tracker.models import Log
from pile_tracker.models import Pile
from pile_tracker.tests.helpers import local_time
from pile_tracker.tests.helpers import make_pile


def weather_says(temp_f):
    """Patch the weather API to report `temp_f` degrees F."""
    response = mock.MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(
        {"main": {"temp": temp_f}}
    ).encode()
    return mock.patch("pile_tracker.models.request.urlopen", return_value=response)


def add_log(client, **fields):
    return client.post(reverse("log-create"), fields)


# --- LOG001: record a check ---------------------------------------------------


@pytest.mark.requirement("LOG001")
def test_saves_a_check_with_all_its_values(client, primary):
    pile = make_pile("19", primary)

    response = add_log(
        client,
        pile="19",
        date="2025-11-09 08:00",
        temp="135",
        mosture_content="60",
        air_temp="41",
        turn="on",
        notes="steaming",
    )

    assertRedirects(response, reverse("index"))
    log = Log.objects.get()
    assert log.pile == pile
    assert log.date == local_time(2025, 11, 9, 8)
    assert log.temp == 135
    assert log.mosture_content == 60
    assert log.air_temp == 41
    assert log.turn is True
    assert log.notes == "steaming"


# --- LOG002: sensible defaults ------------------------------------------------


@pytest.mark.requirement("LOG002")
def test_defaults_to_pile_in_primary_and_its_stage(client, collection, primary):
    make_pile("1", collection)
    in_primary = make_pile("2", primary)

    response = client.get(reverse("log-create"))

    initial = response.context["form"].initial
    assert initial["pile"] == in_primary
    assert initial["location"] == "Primary"


@pytest.mark.requirement("LOG002")
def test_no_pile_in_primary_leaves_pile_and_stage_blank(client, collection):
    make_pile("1", collection)

    response = client.get(reverse("log-create"))

    initial = response.context["form"].initial
    assert initial["pile"] is None
    assert initial["location"] == ""


@pytest.mark.requirement("LOG002")
def test_air_temperature_drops_the_fraction(client, primary):
    with weather_says(48.7):
        response = client.get(reverse("log-create"))

    assert response.context["form"].initial["air_temp"] == 48


@pytest.mark.requirement("LOG002")
def test_weather_lookup_uses_api_key_from_environment(client):
    with weather_says(50) as urlopen:
        client.get(reverse("log-create"))

    url = urlopen.call_args.args[0]
    assert "appid=test-key" in url


@pytest.mark.requirement("LOG002")
def test_air_temperature_blank_when_no_api_key_is_set(client, monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY")

    with weather_says(50) as urlopen:
        response = client.get(reverse("log-create"))

    assert response.context["form"].initial["air_temp"] is None
    urlopen.assert_not_called()


@pytest.mark.requirement("LOG002")
def test_page_opens_with_blank_air_temperature_when_weather_is_down(client):
    response = client.get(reverse("log-create"))

    assert response.status_code == 200
    assert response.context["form"].initial["air_temp"] is None


# --- LOG003: moving a pile ----------------------------------------------------


@pytest.mark.requirement("LOG003")
def test_choosing_a_stage_moves_the_pile(client, collection, primary):
    make_pile("20", collection)

    add_log(client, pile="20", date="2025-11-09 08:00", location="Primary")

    assert Pile.objects.get(id="20").location == primary
    assert Log.objects.get().location == primary


@pytest.mark.requirement("LOG003")
def test_blank_stage_keeps_the_pile_where_it_is(client, collection, primary):
    make_pile("20", collection)

    add_log(client, pile="20", date="2025-11-09 08:00", location="")

    assert Pile.objects.get(id="20").location == collection
    assert Log.objects.get().location == collection


# --- LOG004: log entry checks -------------------------------------------------


def assert_refused(response, field):
    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert Log.objects.count() == 0


@pytest.mark.requirement("LOG004")
def test_bad_date_is_refused_and_typing_kept(client, primary):
    make_pile("1", primary)

    response = add_log(client, pile="1", date="yesterday", notes="kept this")

    assert_refused(response, "date")
    assert 'value="kept this"' in response.content.decode()


@pytest.mark.requirement("LOG004")
def test_no_pile_is_refused(client):
    response = add_log(client, date="2025-11-09 08:00")

    assert_refused(response, "pile")


@pytest.mark.requirement("LOG004")
def test_temperature_must_be_a_whole_number(client, primary):
    make_pile("1", primary)

    response = add_log(client, pile="1", date="2025-11-09 08:00", temp="hot")

    assert_refused(response, "temp")


@pytest.mark.requirement("LOG004")
def test_notes_over_200_characters_are_refused(client, primary):
    make_pile("1", primary)

    response = add_log(client, pile="1", date="2025-11-09 08:00", notes="x" * 201)

    assert_refused(response, "notes")


@pytest.mark.requirement("LOG004")
def test_stage_not_set_up_is_refused_and_pile_not_moved(client, primary):
    make_pile("1", primary)

    response = add_log(client, pile="1", date="2025-11-09 08:00", location="Secondary")

    assert_refused(response, "location")
    assert Pile.objects.get(id="1").location == primary


# --- Not tied to a requirement ------------------------------------------------


def test_new_log_date_defaults_to_aware_datetime(primary):
    """Guards the timezone fix: a log's default date carries a timezone."""
    log = Log.objects.create(pile=make_pile("1", primary))

    assert timezone.is_aware(log.date)
