from django.urls import path

from . import views

app_name='partyfloor'
urlpatterns = [
    path('', views.index, name='index'),
    path('apply', views.apply, name='apply'),
    path('new', views.new, name='new'),
    path('confirm', views.confirm, name='confirm')
]
