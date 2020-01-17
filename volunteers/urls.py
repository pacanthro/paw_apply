from django.urls import path

from . import views

app_name='volunteers'
urlpatterns = [
    path('', views.index, name='index'),
    path('apply', views.apply, name='apply'),
    path('apply/new', views.new, name='new')
]
