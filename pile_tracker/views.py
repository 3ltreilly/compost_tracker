from django.shortcuts import render
from django.views import generic
from pile_tracker.models import Pile, Log, Location
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import datetime, timedelta
import pytz
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404

# useful functions
def last_moved(pk):
    id = get_object_or_404(Pile, pk=pk)
    log_pile = Log.objects.filter(pile__exact=pk)
    try:
        last_moved_date = log_pile.filter(move_to__exact=id.location).latest('date').date
    except:
        last_moved_date = datetime.combine(id.born_date, datetime.min.time(), pytz.UTC)
    return last_moved_date

def next_move(pk):
    id = get_object_or_404(Pile, pk=pk)
    prev_move = last_moved(pk)
    return prev_move + timedelta(days=id.location.days_at_state)

# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_piles = Pile.objects.all().count()
    num_locations = Location.objects.all().count()
    num_logs = Log.objects.all().count()
    whos_in_primary = Pile.objects.filter(location__exact=2).first()

    wip = {}
    for pile in Pile.objects.all():
        wip.update({
            # pile.id: next_move(pile.id)
            next_move(pile.id): pile.id
        })
    next_pile = wip[sorted(wip)[0]]
    next_date = sorted(wip)[0]
    
    # wip_list = 
    # for pile in Pile.objects.all():
    #     wip.update({
    #         pile.id: next_move(pile.id)
    #     })


    context = {
        'num_piles': num_piles,
        'num_locations': num_locations,
        'num_logs': num_logs,
        'whos_in_primary': whos_in_primary,
        'next_pile': next_pile,
        'next_date': next_date,
    }

    # Render the HTML template index.html with the data in the context variable 
    return render(request, 'index.html', context=context)

class PileListView(generic.ListView):
    model = Pile

# lets do thie without the generic option
def PileDetailView(request, pk):

    id = get_object_or_404(Pile, pk=pk)
    log_pile = Log.objects.filter(pile__exact=pk)
    last_turned = log_pile.filter(turn__exact=True).latest('date').date
    
    n_m = next_move(pk)
    l_m = last_moved(pk)

    context = {
        'id': id,
        'location': id.location,
        'born_date': id.born_date,
        'feedstock': id.feedstock,
        'last_turned': last_turned,
        'log_pile': log_pile,
        'next_move': n_m,
        'last_moved': l_m,
    }
    
    return render(request, 'pile_detail.html', context=context)

class LocationListView(generic.ListView):
    model = Location

class LogCreate(CreateView):
    model = Log
    fields = ['date', 'temp']
    fields = '__all__'
    initial = {
        'pile': Log.pile_in_primary()[0].id,
        'air_temp': Log.get_cur_temp()
        }

    success_url = reverse_lazy('index')
