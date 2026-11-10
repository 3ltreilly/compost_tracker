"""Locations page and stage durations: STAGE001-STAGE002."""

import datetime

import pytest
from django.urls import reverse

from pile_tracker.tests.helpers import local_time
from pile_tracker.tests.helpers import make_log
from pile_tracker.tests.helpers import make_pile

# --- STAGE001: stage list -----------------------------------------------------


@pytest.mark.requirement("STAGE001")
def test_stage_list_shows_each_duration(client, primary):
    primary.days_at_state = 42
    primary.save()

    response = client.get(reverse("locations"))

    assert "Primary (42 days)" in response.content.decode()


@pytest.mark.requirement("STAGE001")
def test_stage_list_when_empty(client):
    response = client.get(reverse("locations"))

    assert "There are no locations yet." in response.content.decode()


# --- STAGE002: stage durations ------------------------------------------------


@pytest.mark.requirement("STAGE002")
def test_changing_a_duration_changes_next_move(client, primary):
    primary.days_at_state = 42
    primary.save()
    pile = make_pile("19", primary, born_date=datetime.date(2025, 1, 19))
    make_log(pile, local_time(2025, 3, 15, 19), location=primary)

    before = client.get(reverse("pile-detail", args=["19"])).context["next_move"]
    primary.days_at_state = 35
    primary.save()
    after = client.get(reverse("pile-detail", args=["19"])).context["next_move"]

    assert before.date() == datetime.date(2025, 4, 26)
    assert after.date() == datetime.date(2025, 4, 19)
