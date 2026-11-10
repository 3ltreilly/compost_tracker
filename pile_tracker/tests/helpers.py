import datetime

from django.utils import timezone

from pile_tracker.models import Log
from pile_tracker.models import Pile


def make_pile(pile_id, location, born_date=datetime.date(2026, 1, 1)):
    return Pile.objects.create(id=pile_id, born_date=born_date, location=location)


def local_time(year, month, day, hour=0, minute=0):
    """A timezone-aware datetime in the site's time zone (America/New_York)."""
    return timezone.make_aware(datetime.datetime(year, month, day, hour, minute))


def make_log(pile, date, **fields):
    return Log.objects.create(pile=pile, date=date, **fields)
