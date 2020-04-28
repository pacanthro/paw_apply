from django.urls import path

from . import views

app_name='console'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # Merchants
    path('merchants', views.merchants, name='merchants'),
    path('merchants/<int:merchant_id>', views.merchant_detail, name='merchant-detail'),
    path('merchants/<int:merchant_id>/payment', views.merchant_payment,  name='merchant-payment'),
    path('merchants/<int:merchant_id>/confirm', views.merchant_confirmed, name='merchant-confirm'),
    path('merchants/download_csv', views.merchant_download_csv, name='merchant-download'),
    # Panels
    path('panels', views.panels, name='panels'),
    path('panels/<int:panel_id>', views.panel_detail, name='panel-detail'),

    # Volunteers
    path('volunteers', views.volunteers, name='volunteers'),
    path('volunteers/<int:volunteer_id>', views.volunteer_detail, name='volunteer-detail')
]
