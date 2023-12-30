from django.urls import path

from . import views
from . import views_new

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
    path('merchants/<int:merchant_id>/reg', views.merchant_reg_reminder, name='merchant-reg-remind'),
    path('merchants/<int:merchant_id>/waitlist', views.merchant_waitlisted, name='merchant-waitlist'),
    path('merchants/<int:merchant_id>/delete', views.merchant_delete, name='merchant-delete'),
    path('merchants/<int:merchant_id>/assign', views.merchant_assign, name='merchant-assign'),

    # Panels
    path('panels', views_new.PanelsListPageView.as_view(), name='panels'),
    path('panels/<int:panel_id>', views_new.PanelDetailsPageView.as_view(), name='panel-detail'),
    path('panels/<int:panel_id>/accept', views_new.PanelActionAcceptRedirect.as_view(), name='panel-accept'),
    path('panels/<int:panel_id>/waitlist', views_new.PanelActionWaitlistRedirect.as_view(), name='panel-waitlist'),
    path('panels/<int:panel_id>/deny', views_new.PanelActionDenyRedirect.as_view(), name='panel-deny'),
    path('panels/<int:panel_id>/delete', views_new.PanelActionDeleteRedirect.as_view(), name='panel-delete'),

    # Volunteers
    path('volunteers', views.volunteers, name='volunteers'),
    path('volunteers/download_csv', views.volunteer_download_csv, name='volunteer-download'),
    path('volunteers/<int:volunteer_id>', views.volunteer_detail, name='volunteer-detail'),

    # Performers
    path('performers', views.performers, name='performers'),
    path('performers/<int:performer_id>', views.performer_detail, name='performer-detail'),

    # Party Hosts
    path('hosts', views_new.PartyHostListPageViewView.as_view(), name='hosts'),
    path('hosts/<int:host_id>', views_new.PartyHostDetailPageView.as_view(), name='host-detail'),
    path('hosts/<int:host_id>/accept', views_new.PartyHostActionAcceptRedirect.as_view(), name='host-accept'),
    path('hosts/<int:host_id>/assign', views_new.PartyHostActionAssignPageView.as_view(), name='host-assign'),
    path('hosts/<int:host_id>/waitlist', views_new.PartyHostActionWaitlistRedirect.as_view(), name='host-waitlist'),
    path('hosts/<int:host_id>/decline', views_new.PartyHostActionDeclineRedirect.as_view(), name='host-decline'),
    path('hosts/<int:host_id>/delete', views_new.PartyHostActionDeleteRedirect.as_view(), name='host-delete'),

    # Competitors
    path('competitors', views.competitors, name='competitors'),
    path('competitors/<int:competitor_id>', views.competitor_detail, name='competitor-detail')
]
