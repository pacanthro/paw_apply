from django.urls import path

from . import views

app_name='console'
urlpatterns = [
    path('', views.index, name='index'),
    path('merchants', views.merchants, name='merchants'),
    path('merchants/<int:merchant_id>', views.merchant_detail, name='merchant-detail'),
    path('merchants/<int:merchant_id>/payment', views.merchant_payment,  name='merchant-payment')
]
