from datetime import datetime
from datetime import time
from datetime import timedelta

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from pile_tracker.forms import LogModelForm
from pile_tracker.forms import PileModelForm
from pile_tracker.models import Location
from pile_tracker.models import Log
from pile_tracker.models import Pile


# useful functions
def start_of_day(date):
    """Midnight at the start of `date`, in the site's time zone."""
    return timezone.make_aware(datetime.combine(date, time.min))


def last_moved(pk):
    pile = get_object_or_404(Pile, pk=pk)
    log_pile = Log.objects.filter(pile__exact=pk)
    try:
        return log_pile.filter(location__exact=pile.location).earliest("date").date
    except Log.DoesNotExist:
        return start_of_day(pile.born_date)


def next_move(pk):
    """Date the pile is due to move on, or None if its location has no time limit."""
    pile = get_object_or_404(Pile, pk=pk)
    if pile.location.days_at_state is None:
        return None
    return last_moved(pk) + timedelta(days=pile.location.days_at_state)


# Create your views here.
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_piles = Pile.objects.all().count()
    num_locations = Location.objects.all().count()
    num_logs = Log.objects.all().count()
    whos_in_primary = Log.pile_in_primary()

    # (move date, pile id) for every pile that still has a move ahead of it
    upcoming_moves = []
    for pile in Pile.objects.exclude(location__location="Cure/Storage"):
        move_date = next_move(pile.id)
        if move_date is not None:
            upcoming_moves.append((move_date, pile.id))

    if upcoming_moves:
        next_date, next_pile = min(upcoming_moves)
    else:
        next_date, next_pile = None, None

    context = {
        "num_piles": num_piles,
        "num_locations": num_locations,
        "num_logs": num_logs,
        "whos_in_primary": whos_in_primary,
        "next_pile": next_pile,
        "next_date": next_date,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, "index.html", context=context)


class PileListView(generic.ListView):
    model = Pile


# lets do thie without the generic option
def PileDetailView(request, pk):
    pile = get_object_or_404(Pile, pk=pk)
    log_pile = Log.objects.filter(pile__exact=pk)
    try:
        last_turned = log_pile.filter(turn__exact=True).latest("date").date
    except Log.DoesNotExist:
        last_turned = start_of_day(pile.born_date)

    # loop to make chart data; Chart.js wants timestamps in milliseconds
    data = []
    for log in log_pile:
        if log.temp is not None:
            data.append({"x": log.date.timestamp() * 1000, "y": log.temp})

    context = {
        "data": data,
        "id": pile,
        "location": pile.location,
        "born_date": pile.born_date,
        "feedstock": pile.feedstock,
        "last_turned": last_turned,
        "log_pile": log_pile,
        "next_move": next_move(pk),
        "last_moved": last_moved(pk),
    }

    return render(request, "pile_detail.html", context=context)


class LocationListView(generic.ListView):
    model = Location


def logcreate(request):
    if request.method == "POST":
        form = LogModelForm(request.POST)

        if form.is_valid():
            pile = form.cleaned_data["pile"]
            # a blank location means the pile stays where it is
            location = form.cleaned_data["location"] or pile.location

            Log.objects.create(
                date=form.cleaned_data["date"],
                temp=form.cleaned_data["temp"],
                mosture_content=form.cleaned_data["mosture_content"],
                air_temp=form.cleaned_data["air_temp"],
                turn=form.cleaned_data["turn"],
                location=location,
                notes=form.cleaned_data["notes"],
                pile=pile,
            )

            # move the pile to its new location
            if location != pile.location:
                pile.location = location
                pile.save(update_fields=["location"])

            return HttpResponseRedirect(reverse("index"))

    # If this is a GET, create the form with sensible defaults.
    else:
        primary_pile = Log.pile_in_primary()
        form = LogModelForm(
            initial={
                "date": timezone.now,
                "pile": primary_pile,
                "air_temp": Log.get_cur_temp(),
                "location": primary_pile.location.location if primary_pile else "",
            }
        )

    # Invalid POSTs fall through to here so the errors are shown.
    return render(request, "pile_tracker/log_form.html", context={"form": form})


def pilecreate(request):
    if request.method == "POST":
        form = PileModelForm(request.POST)

        if form.is_valid():
            Pile.objects.create(
                id=form.cleaned_data["id"],
                born_date=form.cleaned_data["born_date"],
                location=form.cleaned_data["location"],
            )

            return HttpResponseRedirect(reverse("index"))

    # If this is a GET, create a blank form.
    else:
        form = PileModelForm(initial={"born_date": timezone.localdate})

    # Invalid POSTs fall through to here so the errors are shown.
    return render(request, "pile_tracker/pile_form.html", context={"form": form})
