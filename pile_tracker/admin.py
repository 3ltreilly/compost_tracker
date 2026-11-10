from django.contrib import admin

# Register your models here.
from .models import Location
from .models import Log
from .models import Pile

admin.site.register(Pile)
admin.site.register(Log)
admin.site.register(Location)

# from .models import Pile, Log

# admin.site.register(Pile)
# admin.site.register(Log)
