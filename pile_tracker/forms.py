from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


from django.forms import ModelForm

# from catalog.models import Pile
stages = (
        ('','---------'),
        ('Collection', 'Collection'),
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
        ('Cure/Storate', 'Cure/Storate'),
    )

class LogModelForm(forms.Form):
   date = forms.DateTimeField()
   temp = forms.IntegerField()
   mosture_content = forms.IntegerField(required=False)
   turn = forms.BooleanField(required=False)


   # move_to = forms.ChoiceField(required=False, help_text='new location for the pile', widget=forms.Select, choices=stages,initial='')
   move_to = forms.CharField(
      required=False,
      max_length=12,
      widget=forms.Select(choices=stages),
      help_text='current location for pile',
    )


   notes = forms.CharField(required=False, max_length=200, help_text='general notes')

   pile = forms.IntegerField()
   air_temp = forms.IntegerField(required=False)

   def clean_due_back(self):
      data = self.cleaned_data['due_back']

    #    # Check if a date is not in the past.
    #    if data < datetime.date.today():
    #        raise ValidationError(_('Invalid date - renewal in past'))

    #    # Check if a date is in the allowed range (+4 weeks from today).
    #    if data > datetime.date.today() + datetime.timedelta(weeks=4):
    #        raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

       # Remember to always return the cleaned data.
      return data

   # def save(self):
   #    data = self.cleaned_data
   #    log = Log(date = 'date')

   #  class Meta:
   #      model = Log
   #      fields = ['date', 'temp']