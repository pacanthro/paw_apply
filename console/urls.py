from django.urls import path

from . import views
from . import views_new

app_name='console'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # Merchants
    path('merchants', views_new.MerchantsListPageView.as_view(), name='merchants'),
    path('merchants/download_csv', views_new.MerchantCSVDownloadView.as_view(), name='merchant-download'),
    path('merchants/<int:merchant_id>', views_new.MerchantDetailsPageView.as_view(), name='merchant-detail'),
    path('merchants/<int:merchant_id>/payment', views_new.MerchantActionRequestPaymentRedirect.as_view(),  name='merchant-payment'),
    path('merchants/<int:merchant_id>/confirm', views_new.MerchantActionPaymentConfirmedRedirect.as_view(), name='merchant-confirm'),
    path('merchants/<int:merchant_id>/register', views_new.MerchantActionRegistrationReminderRedirect.as_view(), name='merchant-reg-remind'),
    path('merchants/<int:merchant_id>/waitlist', views_new.MerchantActionWaitlistRedirect.as_view(), name='merchant-waitlist'),
    path('merchants/<int:merchant_id>/delete', views_new.MerchantActionDeleteRedirect.as_view(), name='merchant-delete'),
    path('merchants/<int:merchant_id>/assign', views_new.MerchantActionAssignPageView.as_view(), name='merchant-assign'),

    # Panels
    path('panels', views_new.PanelsListPageView.as_view(), name='panels'),
    path('panels/<int:panel_id>', views_new.PanelDetailsPageView.as_view(), name='panel-detail'),
    path('panels/<int:panel_id>/accept', views_new.PanelActionAcceptRedirect.as_view(), name='panel-accept'),
    path('panels/<int:panel_id>/waitlist', views_new.PanelActionWaitlistRedirect.as_view(), name='panel-waitlist'),
    path('panels/<int:panel_id>/deny', views_new.PanelActionDenyRedirect.as_view(), name='panel-deny'),
    path('panels/<int:panel_id>/delete', views_new.PanelActionDeleteRedirect.as_view(), name='panel-delete'),

    # Volunteers
    path('volunteers', views_new.VolunteerListPageView.as_view(), name='volunteers'),
    path('volunteers/download_csv', views_new.VolunteerCSVDownloadView.as_view(), name='volunteer-download'),
    path('volunteers/<int:volunteer_id>', views_new.VolunteerDetailsPageView.as_view(), name='volunteer-detail'),
    path('volunteers/<int:volunteer_id>/accept', views_new.VolunteerActionAcceptRedirect.as_view(), name='volunteer-accept'),
    path('volunteers/<int:volunteer_id>/decline', views_new.VolunteerActionDeclinetRedirect.as_view(), name='volunteer-decline'),
    path('volunteers/<int:volunteer_id>/delete', views_new.VolunteerActionDeleteRedirect.as_view(), name='volunteer-delete'),

    # Performers
    path('performers', views_new.PerformersListPageView.as_view(), name='performers'),
    path('performers/<int:performer_id>', views_new.PerformerDetailPageView.as_view(), name='performer-detail'),
    path('performers/<int:performer_id>/accept', views_new.PerformerActionAcceptRedirect.as_view(), name='performer-accept'),
    path('performers/<int:performer_id>/waitlist', views_new.PerformerActionWaitlistRedirect.as_view(), name='performer-waitlist'),
    path('performers/<int:performer_id>/decline', views_new.PerformerActionDeclineRedirect.as_view(), name='performer-decline'),
    path('performers/<int:performer_id>/delete', views_new.PerformerActionDeleteRedirect.as_view(), name='performer-delete'),

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
