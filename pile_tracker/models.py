# https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.IntegerField

import json
import os
from urllib import request

from django.db import models
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
from django.utils import timezone


# Create your models here.
class Pile(models.Model):
    """Model representing a shit pile"""

    id = models.CharField(
        max_length=20, primary_key=True, help_text="Unique ID for a pile"
    )

    # pile start date
    born_date = models.DateField()

    # feedstock and mix
    feedstock = models.CharField(
        max_length=200,
        default="horse manure",
        help_text="what is in this pile?  just horse S or added chips?",
    )

    # cuttent locations, list.  add a sub dicription for multiple piles in the same location
    location = models.ForeignKey("Location", on_delete=models.RESTRICT)

    # https://docs.djangoproject.com/en/dev/topics/db/queries/#field-lookups
    # https://docs.djangoproject.com/en/dev/ref/models/querysets/#field-lookups
    # def last_turned(self):
    #     return Log.objects.latest('turn')
    # def next_loc_move(self):
    #     # move_date =
    #     log_pile = Log.objects.filter(pile__exact=self.id)
    #     return move_date

    def __str__(self):
        """String for representing the Model object."""
        return self.id

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse("pile-detail", args=[str(self.id)])


# logs for temp, dateline, ambient temp, mc, Daily weather?, picture?,
class Log(models.Model):

    date = models.DateTimeField(default=timezone.now)
    temp = models.IntegerField(null=True, blank=True)

    mosture_content = models.IntegerField(null=True, blank=True)
    turn = models.BooleanField(default=False)
    location = models.ForeignKey(
        "Location",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        help_text="new location for the pile",
    )
    notes = models.CharField(
        max_length=200, help_text="general notes", null=True, blank=True
    )
    pile = models.ForeignKey("Pile", on_delete=models.CASCADE, null=True)
    # make a method to grab current ambient temp?

    @staticmethod
    def pile_in_primary():
        """Return the pile in the Primary stage, or None if there isn't one."""
        return Pile.objects.filter(location__location="Primary").first()

    @staticmethod
    def get_cur_temp():
        """Return the current air temperature in °F, or None if it can't be fetched."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            return None
        try:
            # let's update to this api when it's ready
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?zip=06238,US&units=imperial&appid={api_key}"
            with request.urlopen(weather_url, timeout=5) as response:
                the_weather = json.loads(response.read())
            return int(the_weather["main"]["temp"])
        except (OSError, KeyError, ValueError):
            # OSError covers network errors and timeouts; KeyError an
            # unexpected response; ValueError bad JSON.
            return None

    air_temp = models.IntegerField(null=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return "Pile_" + str(self.pile) + "_" + str(self.date)

    class Meta:
        ordering = ["date"]


# locations for each pile
class Location(models.Model):
    stages = (
        ("Collection", "Collection"),
        ("Primary", "Primary"),
        ("Secondary", "Secondary"),
        ("Cure/Storage", "Cure/Storage"),
    )

    location = models.CharField(
        max_length=12,
        choices=stages,
        blank=True,
        help_text="current location for pile",
    )

    days_at_state = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.location


# meta for handy stuff?
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models
# https://docs.djangoproject.com/en/3.1/ref/models/options/
# class Meta:
#     ordering = ['-my_field_name']
