from django.urls import path

from . import views

app_name='system'
urlpatterns = [
    # Event
    path('event', views.event.EventIndexPageView.as_view(), name="event-index"),

    # Departments
    path('departments', views.departments.DepartmentListPageView.as_view(), name="departments-list"),
    path('departments/<int:department_id>', views.departments.DepartmentEditPageView.as_view(), name="department-edit"),
    path('departments/create', views.departments.DepartmentCreatePageView.as_view(), name="department-create"),
    path('department/delete/<int:department_id>', views.departments.DepartmentDeleteRedirectView.as_view(), name="department-delete"),

    # Event Rooms
    path('rooms', views.event_rooms.EventRoomsListPageView.as_view(), name="rooms-list"),

    # Scheduling Configs
    path('schedconfig', views.sched_configs.SchedulingConfigListView.as_view(), name="schedconfig-list"),

    # Merchant Tables
    path('tables', views.tables.MerchantTablesListView.as_view(), name="tables-list"),

    # Days Available
    path('days', views.days_available.DaysAvailableListView.as_view(), name="days-list"),

    # Panel Durations
    path('durations', views.panel_durations.PanelDurationListView.as_view(), name="duration-list"),

    # Panel Slots
    path('slots', views.panel_slots.PanelSlotsListView.as_view(), name="slot-list"),

    # Times Available
    path('times', views.times_available.TimesAvailableListView.as_view(), name="times-list"),
]