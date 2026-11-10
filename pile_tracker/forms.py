from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from pile_tracker.models import Location
from pile_tracker.models import Pile

# from catalog.models import Pile
stages = (
    ("", "---------"),
    ("Collection", "Collection"),
    ("Primary", "Primary"),
    ("Secondary", "Secondary"),
    ("Cure/Storage", "Cure/Storage"),
)


def location_from_name(name):
    """Look up the Location chosen in a stage dropdown; blank means no change."""
    if name == "":
        return None
    location = Location.objects.filter(location=name).first()
    if location is None:
        raise ValidationError(
            _("No %(name)s location has been set up yet. Add it in the admin."),
            params={"name": name},
        )
    return location


class LogModelForm(forms.Form):
    date = forms.DateTimeField()
    temp = forms.IntegerField(required=False)
    mosture_content = forms.IntegerField(required=False)
    turn = forms.BooleanField(required=False)

    # location = forms.ChoiceField(required=False, help_text='new location for the pile', widget=forms.Select, choices=stages,initial='')
    location = forms.CharField(
        required=False,
        max_length=12,
        widget=forms.Select(choices=stages),
        help_text="current location of pile",
    )

    notes = forms.CharField(required=False, max_length=200, help_text="general notes")

    pile = forms.ModelChoiceField(queryset=Pile.objects.all())
    air_temp = forms.IntegerField(required=False)

    def clean_location(self):
        return location_from_name(self.cleaned_data["location"])

    def clean_due_back(self):
        data = self.cleaned_data["due_back"]

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


class PileModelForm(forms.Form):
    born_date = forms.DateField()

    location = forms.CharField(
        max_length=12,
        widget=forms.Select(choices=stages),
        help_text="current location of pile",
    )

    id = forms.CharField(max_length=20)

    def clean_location(self):
        return location_from_name(self.cleaned_data["location"])

    def clean_id(self):
        pile_id = self.cleaned_data["id"]
        if Pile.objects.filter(id=pile_id).exists():
            raise ValidationError(_("A pile with this ID already exists."))
        return pile_id

    def clean_due_back(self):
        data = self.cleaned_data["due_back"]
        # Remember to always return the cleaned data.
        return data
