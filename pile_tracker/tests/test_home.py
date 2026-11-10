"""Home page: HOME001-HOME003."""

import datetime
import re

import pytest
from django.urls import reverse
from django.utils import timezone

from pile_tracker.models import Location
from pile_tracker.tests.helpers import make_log
from pile_tracker.tests.helpers import make_pile


def primary_line(response):
    """The text of the 'Pile number in primary stage' line."""
    match = re.search(
        r"Pile number in primary stage:</strong>(.*?)</li>", response.content.decode()
    )
    return match.group(1).strip()


# --- HOME001: record counts ---------------------------------------------------


@pytest.mark.requirement("HOME001")
def test_shows_record_counts(client, collection, primary, cure):
    pile = make_pile("1", primary)
    make_pile("2", collection)
    make_log(pile, timezone.now())

    response = client.get(reverse("index"))

    content = response.content.decode()
    assert "<strong>Piles:</strong> 2" in content
    assert "<strong>Locations:</strong> 3" in content
    assert "<strong>Logs:</strong> 1" in content


# --- HOME002: pile in Primary -------------------------------------------------


@pytest.mark.requirement("HOME002")
def test_finds_pile_in_primary_by_name(client, primary):
    # Primary is location id 1 here, not 2.
    make_pile("1", primary)

    response = client.get(reverse("index"))

    assert primary_line(response) == "1"


@pytest.mark.requirement("HOME002")
def test_several_piles_in_primary_shows_first_id_as_text(client, primary):
    make_pile("9", primary)
    make_pile("10", primary)

    response = client.get(reverse("index"))

    assert primary_line(response) == "10"


@pytest.mark.requirement("HOME002")
def test_no_pile_in_primary_leaves_line_blank(client, collection):
    make_pile("1", collection)

    response = client.get(reverse("index"))

    assert primary_line(response) == ""


# --- HOME003: next move due ---------------------------------------------------


@pytest.mark.requirement("HOME003")
def test_picks_soonest_move_even_with_ties(client, collection, primary):
    # All born the same day; Primary (3 days) is due before Collection (30 days).
    make_pile("1", collection)
    make_pile("2", primary)
    make_pile("3", primary)

    response = client.get(reverse("index"))

    assert response.context["next_pile"] in {"2", "3"}
    assert response.context["next_date"].date() == datetime.date(2026, 1, 4)


@pytest.mark.requirement("HOME003")
def test_no_piles_means_no_moves_scheduled(client):
    response = client.get(reverse("index"))

    assert response.status_code == 200
    assert "no moves scheduled" in response.content.decode()


@pytest.mark.requirement("HOME003")
def test_curing_piles_are_not_scheduled(client, cure):
    make_pile("1", cure)

    response = client.get(reverse("index"))

    assert response.status_code == 200
    assert "no moves scheduled" in response.content.decode()


@pytest.mark.requirement("HOME003")
def test_stage_without_duration_is_not_scheduled(client):
    no_duration = Location.objects.create(location="Collection", days_at_state=None)
    make_pile("1", no_duration)

    response = client.get(reverse("index"))

    assert response.status_code == 200
    assert "no moves scheduled" in response.content.decode()


@pytest.mark.requirement("HOME003")
def test_overdue_move_is_shown_without_marking_it_overdue(client, primary):
    born = timezone.localdate() - datetime.timedelta(days=33)  # due 30 days ago
    make_pile("1", primary, born_date=born)

    response = client.get(reverse("index"))

    assert response.context["next_pile"] == "1"
    assert response.context["next_date"].date() == born + datetime.timedelta(days=3)
    assert "overdue" not in response.content.decode().lower()
