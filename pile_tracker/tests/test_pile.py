"""Add Pile, pile list and pile page: PILE001-PILE008."""

import datetime

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertRedirects

from pile_tracker.models import Location
from pile_tracker.models import Pile
from pile_tracker.tests.helpers import local_time
from pile_tracker.tests.helpers import make_log
from pile_tracker.tests.helpers import make_pile


def pile_page(client, pile_id):
    return client.get(reverse("pile-detail", args=[pile_id]))


# --- PILE001: add a pile ------------------------------------------------------


@pytest.mark.requirement("PILE001")
def test_add_pile(client, collection):
    response = client.post(
        reverse("pile-create"),
        {"id": "24", "born_date": "2025-11-09", "location": "Collection"},
    )

    assertRedirects(response, reverse("index"))
    pile = Pile.objects.get(id="24")
    assert pile.born_date == datetime.date(2025, 11, 9)
    assert pile.location == collection
    assert pile.feedstock == "horse manure"


@pytest.mark.requirement("PILE001")
def test_add_pile_start_date_defaults_to_today(client):
    response = client.get(reverse("pile-create"))

    assert response.context["form"]["born_date"].value() == timezone.localdate()


# --- PILE002: pile entry checks -----------------------------------------------


@pytest.mark.requirement("PILE002")
def test_blank_id_and_bad_date_are_refused(client):
    response = client.post(reverse("pile-create"), {"id": "", "born_date": "x"})

    assert response.status_code == 200
    assert "id" in response.context["form"].errors
    assert "born_date" in response.context["form"].errors
    assert Pile.objects.count() == 0


@pytest.mark.requirement("PILE002")
def test_no_stage_chosen_is_refused_and_typing_kept(client):
    response = client.post(
        reverse("pile-create"),
        {"id": "7", "born_date": "2026-11-09", "location": ""},
    )

    assert response.status_code == 200
    assert "location" in response.context["form"].errors
    assert 'value="7"' in response.content.decode()


@pytest.mark.requirement("PILE002")
def test_stage_not_set_up_is_refused(client, primary):
    # The dropdown offers Collection, but no Collection location exists yet.
    response = client.post(
        reverse("pile-create"),
        {"id": "7", "born_date": "2026-11-09", "location": "Collection"},
    )

    assert response.status_code == 200
    assert "location" in response.context["form"].errors
    assert Pile.objects.count() == 0


@pytest.mark.requirement("PILE002")
def test_duplicate_id_is_refused_and_existing_pile_unchanged(
    client, collection, primary
):
    make_pile("19", primary, born_date=datetime.date(2025, 1, 19))

    response = client.post(
        reverse("pile-create"),
        {"id": "19", "born_date": "2026-11-09", "location": "Collection"},
    )

    assert "A pile with this ID already exists." in response.content.decode()
    pile = Pile.objects.get(id="19")
    assert pile.born_date == datetime.date(2025, 1, 19)
    assert pile.location == primary


# --- PILE003: pile list -------------------------------------------------------


@pytest.mark.requirement("PILE003")
def test_pile_list_shows_each_pile_with_stage_and_link(client, collection, primary):
    make_pile("1", primary)
    make_pile("2", collection)

    response = client.get(reverse("piles"))

    content = response.content.decode()
    assert f'<a href="{reverse("pile-detail", args=["1"])}">1</a> (Primary)' in content
    assert f'<a href="{reverse("pile-detail", args=["2"])}">2</a> (Collection)' in content


@pytest.mark.requirement("PILE003")
def test_pile_list_when_empty(client):
    response = client.get(reverse("piles"))

    assert "There are no piles yet." in response.content.decode()


# --- PILE004: pile details ----------------------------------------------------


@pytest.mark.requirement("PILE004")
def test_pile_page_shows_details(client, primary):
    make_pile("1", primary, born_date=datetime.date(2026, 1, 1))

    response = pile_page(client, "1")

    content = response.content.decode()
    assert "Title: 1" in content
    assert "Primary" in content
    assert "Jan. 1, 2026" in content
    assert "horse manure" in content


@pytest.mark.requirement("PILE004")
def test_pile_page_works_for_id_with_letters(client, primary):
    make_pile("A1", primary)

    response = pile_page(client, "A1")

    assert response.status_code == 200


# --- PILE005: last turned -----------------------------------------------------


@pytest.mark.requirement("PILE005")
def test_last_turned_is_most_recent_turn(client, primary):
    pile = make_pile("19", primary, born_date=datetime.date(2025, 1, 1))
    make_log(pile, local_time(2025, 1, 19, 13), turn=True)
    make_log(pile, local_time(2025, 3, 15, 19), turn=True)
    make_log(pile, local_time(2025, 4, 1, 9), turn=False)

    response = pile_page(client, "19")

    assert response.context["last_turned"] == local_time(2025, 3, 15, 19)


@pytest.mark.requirement("PILE005")
def test_never_turned_shows_midnight_on_start_date(client, primary):
    make_pile("1", primary, born_date=datetime.date(2026, 1, 1))

    response = pile_page(client, "1")

    assert response.context["last_turned"] == local_time(2026, 1, 1)


# --- PILE006: check history ---------------------------------------------------


@pytest.mark.requirement("PILE006")
def test_history_lists_logs_oldest_first_and_marks_turns(client, primary):
    pile = make_pile("19", primary, born_date=datetime.date(2025, 1, 1))
    make_log(pile, local_time(2025, 3, 15, 19), temp=130, turn=True)
    make_log(pile, local_time(2025, 1, 19, 13), temp=150, turn=False)

    response = pile_page(client, "19")

    content = response.content.decode()
    assert content.index("<strong>temp:</strong> 150") < content.index(
        "<strong>temp:</strong> 130"
    )
    assert content.count("<strong>turn:</strong> True") == 1


# --- PILE007: temperature chart -----------------------------------------------


@pytest.mark.requirement("PILE007")
def test_chart_has_a_point_per_temperature_including_zero(client, primary):
    pile = make_pile("1", primary)
    make_log(pile, local_time(2026, 1, 2), temp=140)
    make_log(pile, local_time(2026, 1, 3), temp=None)
    make_log(pile, local_time(2026, 1, 4), temp=0)

    response = pile_page(client, "1")

    assert [point["y"] for point in response.context["data"]] == [140, 0]


# --- PILE008: last move and next move -----------------------------------------


@pytest.mark.requirement("PILE008")
def test_next_move_counts_from_earliest_log_in_current_stage(
    client, collection, primary
):
    primary.days_at_state = 42
    primary.save()
    pile = make_pile("19", primary, born_date=datetime.date(2025, 1, 19))
    make_log(pile, local_time(2025, 1, 19, 13), location=collection)
    make_log(pile, local_time(2025, 3, 15, 19), location=primary)
    make_log(pile, local_time(2025, 4, 1, 9), location=primary)

    response = pile_page(client, "19")

    assert response.context["last_moved"] == local_time(2025, 3, 15, 19)
    assert response.context["next_move"].date() == datetime.date(2025, 4, 26)


@pytest.mark.requirement("PILE008")
def test_without_logs_next_move_counts_from_start_date(client, primary):
    make_pile("1", primary, born_date=datetime.date(2026, 1, 1))

    response = pile_page(client, "1")

    assert response.context["last_moved"] == local_time(2026, 1, 1)
    assert response.context["next_move"] == local_time(2026, 1, 4)


@pytest.mark.requirement("PILE008")
def test_stage_without_duration_leaves_next_move_blank(client):
    no_duration = Location.objects.create(location="Collection", days_at_state=None)
    make_pile("1", no_duration)

    response = pile_page(client, "1")

    assert "<p>Next Move: </p>" in response.content.decode()
