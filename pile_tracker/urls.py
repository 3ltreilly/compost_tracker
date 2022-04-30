from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("piles/", views.PileListView.as_view(), name="piles"),
    path("pile/<int:pk>", views.PileDetailView, name="pile-detail"),
    path("locations/", views.LocationListView.as_view(), name="locations"),
]

urlpatterns += [
    path("log/", views.logcreate, name="log-create"),
    path("new_pile/", views.pilecreate, name="pile-create"),

]
