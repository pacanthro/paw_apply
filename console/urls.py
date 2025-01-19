from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name='console'
urlpatterns = [
    path('', views.ConsoleIndexPageView.as_view(), name='index'),
    path('login', views.ConsoleLoginPageView.as_view(), name='login'),
    path('logout', views.ConsoleLogoutRedirect.as_view(), name='logout'),
    path('forgot-password', views.ResetPasswordView.as_view(), name='forgot-password'),
    path('forgot-password-confirm/<uidb64>/<token>', views.ResetPasswordConfirmView.as_view(), name='forgot-password-confirm'),
    path('forgcot-password-complete', views.ResetPasswordCompleteView.as_view(), name='forgot-password-complete'),


    # Merchants
    path('merchants', views.MerchantsListPageView.as_view(), name='merchants'),
    path('merchants/download_csv', views.MerchantCSVDownloadView.as_view(), name='merchant-download'),
    path('merchants/<int:merchant_id>', views.MerchantDetailsPageView.as_view(), name='merchant-detail'),
    path('merchants/<int:merchant_id>/accept', views.MerchantActionAcceptedRedirect.as_view(), name='merchant-accept'),
    path('merchants/<int:merchant_id>/payment', views.MerchantActionRequestPaymentRedirect.as_view(),  name='merchant-payment'),
    path('merchants/<int:merchant_id>/confirm', views.MerchantActionPaymentConfirmedRedirect.as_view(), name='merchant-confirm'),
    path('merchants/<int:merchant_id>/register', views.MerchantActionRegistrationReminderRedirect.as_view(), name='merchant-reg-remind'),
    path('merchants/<int:merchant_id>/waitlist', views.MerchantActionWaitlistRedirect.as_view(), name='merchant-waitlist'),
    path('merchants/<int:merchant_id>/delete', views.MerchantActionDeleteRedirect.as_view(), name='merchant-delete'),
    path('merchants/<int:merchant_id>/assign', views.MerchantActionAssignPageView.as_view(), name='merchant-assign'),

    # Panels
    path('panels', views.PanelsListPageView.as_view(), name='panels'),
    path('panels/<int:panel_id>', views.PanelDetailsPageView.as_view(), name='panel-detail'),
    path('panels/<int:panel_id>/accept', views.PanelActionAcceptRedirect.as_view(), name='panel-accept'),
    path('panels/<int:panel_id>/waitlist', views.PanelActionWaitlistRedirect.as_view(), name='panel-waitlist'),
    path('panels/<int:panel_id>/deny', views.PanelActionDenyRedirect.as_view(), name='panel-deny'),
    path('panels/<int:panel_id>/delete', views.PanelActionDeleteRedirect.as_view(), name='panel-delete'),
    path('panels/schedule', views.PanelSchedulePageView.as_view(), name='panels-schedule'),
    path('panels/schedule/<int:panel_id>/assign', views.PanelActionAssignPageView.as_view(), name='panel-assign'),
    path('panels/schedule/<int:panel_id>/unassign', views.PanelActionUnscheduleRedirect.as_view(), name='panel-unassign'),
    path('panels/schedule/<int:panel_id>/cancel', views.PanelActionCancelRedirect.as_view(), name='panel-cancel'),

    # Volunteers
    path('volunteers', views.VolunteerListPageView.as_view(), name='volunteers'),
    path('volunteers/download_csv', views.VolunteerCSVDownloadView.as_view(), name='volunteer-download'),
    path('volunteers/<int:volunteer_id>', views.VolunteerDetailsPageView.as_view(), name='volunteer-detail'),
    path('volunteers/<int:volunteer_id>/accept', views.VolunteerActionAcceptRedirect.as_view(), name='volunteer-accept'),
    path('volunteers/<int:volunteer_id>/decline', views.VolunteerActionDeclinedRedirect.as_view(), name='volunteer-decline'),
    path('volunteers/<int:volunteer_id>/delete', views.VolunteerActionDeleteRedirect.as_view(), name='volunteer-delete'),
    path('volunteers/<int:volunteer_id>/task', views.VolunteerAddTaskPageView.as_view(), name='volunteer-add-task'),
    path('volunteers/<int:volunteer_id>/task/<int:task_id>/edit', views.VolunteerEditTaskPageView.as_view(), name="volunteer-edit-task"),
    path('volunteers/<int:volunteer_id>/task/<int:task_id>/delete', views.VolunteerActionDeleteTaskRedirect.as_view(), name="volunteer-delete-task"),
    path('volunteers/dashboard', views.VolunteerDashboardPageView.as_view(), name="volunteer-dashboard"),
    path('volunteers/dashboard/task/<int:volunteer_id>/start', views.VolunteerStartTaskRedirect.as_view(), name='volunteer-task-start'),
    path('volunteers/dashboard/task/<int:task_id>/end', views.VolunteerEndTaskRedirect.as_view(), name='volunteer-task-end'),
    path('volunteers/email', views.VolunteerComposeMassEmailPageView.as_view(), name='volunteer-email'),

    # Performers
    path('performers', views.PerformersListPageView.as_view(), name='performers'),
    path('performers/<int:performer_id>', views.PerformerDetailPageView.as_view(), name='performer-detail'),
    path('performers/<int:performer_id>/accept', views.PerformerActionAcceptRedirect.as_view(), name='performer-accept'),
    path('performers/<int:performer_id>/waitlist', views.PerformerActionWaitlistRedirect.as_view(), name='performer-waitlist'),
    path('performers/<int:performer_id>/decline', views.PerformerActionDeclineRedirect.as_view(), name='performer-decline'),
    path('performers/<int:performer_id>/delete', views.PerformerActionDeleteRedirect.as_view(), name='performer-delete'),
    path('performers/schedule', views.PerformersSchedulePageView.as_view(), name='performer-schedule'),
    path('performers/schedule/<int:performer_id>/assign', views.PerformerActionAssignPageView.as_view(), name='performer-assign'),
    path('performers/schedule/<int:performer_id>/unassign', views.PerformerActionUnscheduleRedirect.as_view(), name='performer-unassign'),

    # Party Hosts
    path('hosts', views.PartyHostListPageViewView.as_view(), name='hosts'),
    path('hosts/<int:host_id>', views.PartyHostDetailPageView.as_view(), name='host-detail'),
    path('hosts/<int:host_id>/accept', views.PartyHostActionAcceptRedirect.as_view(), name='host-accept'),
    path('hosts/<int:host_id>/assign', views.PartyHostActionAssignPageView.as_view(), name='host-assign'),
    path('hosts/<int:host_id>/waitlist', views.PartyHostActionWaitlistRedirect.as_view(), name='host-waitlist'),
    path('hosts/<int:host_id>/decline', views.PartyHostActionDeclineRedirect.as_view(), name='host-decline'),
    path('hosts/<int:host_id>/delete', views.PartyHostActionDeleteRedirect.as_view(), name='host-delete'),

    # Competitors
    path('competitors', views.CompetitorsListPageView.as_view(), name='competitors'),
    path('competitors/<int:competitor_id>', views.CompetitorDetailPageView.as_view(), name='competitor-detail'),
    path('competitors/<int:competitor_id>/accept', views.CompetitorActionAcceptRedirect.as_view(), name='competitor-accept'),
    path('competitors/<int:competitor_id>/decline', views.CompetitorActionDeclineRedirect.as_view(), name='competitor-decline'),
    path('competitors/<int:competitor_id>/delete', views.CompetitorActionDeleteRedirect.as_view(), name='competitor-delete')
]
