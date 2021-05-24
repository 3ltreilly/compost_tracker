from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('piles/', views.PileListView.as_view(), name='piles'),
    path('pile/<int:pk>', views.PileDetailView, name='pile-detail'),
    path('locations/', views.LocationListView.as_view(), name='locations'),
]

urlpatterns += [
    path('log/', views.LogCreate.as_view(), name='log-create'),
]