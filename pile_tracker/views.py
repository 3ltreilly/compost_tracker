from django.shortcuts import render
from django.views import generic
from pile_tracker.models import Pile, Log, Location
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import datetime, timedelta
import pytz
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
import sqlite3
import os

from pile_tracker.forms import LogModelForm
from django.http import HttpResponseRedirect
from django.urls import reverse

# useful functions
def last_moved(pk):
    id = get_object_or_404(Pile, pk=pk)
    log_pile = Log.objects.filter(pile__exact=pk)
    try:
        last_moved_date = log_pile.filter(location__exact=id.location).earliest('date').date
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
        if pile.location.location != 'Cure/Storage':
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
    try:
        last_turned = log_pile.filter(turn__exact=True).latest('date').date
    # except ObjectDoesNotExist:
    except:
        last_turned = datetime.combine(id.born_date, datetime.min.time())
    
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

# class LogCreate(CreateView):
#     model = Log
#     fields = ['date', 'temp']
#     fields = '__all__'
#     initial = {
#         'pile': Log.pile_in_primary()[0].id,
#         'air_temp': Log.get_cur_temp()
#         }

#     success_url = reverse_lazy('index')

def logcreate(request):
    # get Pile info to do stuff with it
    try:
        primary_pile = Log.pile_in_primary()[0].id
        id = get_object_or_404(Pile, pk=primary_pile)
        location = id.location
    except:
        primary_pile = ''
        location = ''
    # Pile.objects.get(id=Log.pile_in_primary()[0].id)     ?????
    
    # the_log = get_object_or_404(Log)
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = LogModelForm(request.POST)

        # # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            date = form.cleaned_data['date']
            temp = form.cleaned_data['temp']
            mosture_content = form.cleaned_data['mosture_content']
            turn = form.cleaned_data['turn']


            notes =   form.cleaned_data['notes']

            pile = form.cleaned_data['pile'].first()   #get_object_or_404(Pile, pk=form.cleaned_data['pile'])
            # pile = form.cleaned_data['pile']

            if form.cleaned_data['location'] == '':
                location = Location.objects.filter(pile__exact=pile).first()
            else:
                location = Location.objects.filter(location__exact=form.cleaned_data['location']).first()
            
            # save the new log
            log = Log(date = date, temp = temp, mosture_content =mosture_content,turn=turn,location=location,notes=notes,pile=pile)
            log.save()
            # save over the pile again to capture the updated location
            if location:
                pile_update = Pile(id=pile.id, born_date=pile.born_date, feedstock=pile.feedstock, location=location)
                pile_update.save()

            # redirect to a new URL:
        return HttpResponseRedirect(reverse('index') )

    # If this is a GET (or any other method) create the default form.
    else:
        # proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = LogModelForm(initial = {
            'date':datetime.now,
            # 'pile': Log.pile_in_primary()[0].id,
            # 'pile': Pile.objects.get(id=Log.pile_in_primary()[0].id),
            'pile': primary_pile,
            'air_temp': Log.get_cur_temp(),
            'location': location,
            # 'location': Location.objects.filter(location__exact=id.location),
            })

    context = {
        'form': form,
        # 'the_log': the_log,
    }

    return render(request, 'pile_tracker/log_form.html', context=context)
