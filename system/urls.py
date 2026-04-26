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
    path('rooms/<int:event_room_id>', views.event_rooms.EventRoomsEditPageView.as_view(), name='rooms-edit'),
    path('rooms/create', views.event_rooms.EventRoomsCreatePageView.as_view(), name="rooms-create"),
    path('rooms/delete/<int:event_room_id>', views.event_rooms.EventRoomsDeleteRedirectView.as_view(), name="rooms-delete"),

    # Scheduling Configs
    path('schedconfig', views.sched_configs.SchedulingConfigListView.as_view(), name="schedconfig-list"),
    path('schedconfig/<int:config_id>', views.sched_configs.SchedulingConfigEditView.as_view(), name="schedconfig-edit"),
    path('schedconfig/create', views.sched_configs.SchedulingConfigCreateView.as_view(), name="schedconfig-create"),
    path('schedconfig/delete/<int:config_id>', views.sched_configs.SchedulingConfighDeleteRedirectView.as_view(), name="schedconfig-delete"),

    # Merchant Tables
    path('tables', views.tables.MerchantTablesListView.as_view(), name="tables-list"),
    path('tables/edit/<str:table_id>', views.tables.MerchantTablesEditView.as_view(), name="tables-edit"),
    path('tables/create', views.tables.MerchantTablesCreateView.as_view(), name="tables-create"),
    path('tables/delete/<str:table_id>', views.tables.MerchantTableDeleteRedirectView.as_view(), name="tables-delete"),

    # Days Available
    path('days', views.days_available.DaysAvailableListView.as_view(), name="days-list"),
    path('days/edit/<str:day_id>', views.days_available.DaysAvailableEditView.as_view(), name="days-edit"),
    path('days/create', views.days_available.DaysAvailableCreateView.as_view(), name="days-create"),
    path('days/delete/<str:day_id>', views.days_available.DayAvailableDeleteRedirectView.as_view(), name="days-delete"),

    # Panel Durations
    path('durations', views.panel_durations.PanelDurationListView.as_view(), name="duration-list"),

    # Panel Slots
    path('slots', views.panel_slots.PanelSlotsListView.as_view(), name="slot-list"),

    # Times Available
    path('times', views.times_available.TimesAvailableListView.as_view(), name="times-list"),
]