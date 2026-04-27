from modules.page_view import PageView
from modules.mixins import SuperuserRequiredMixin

class EventIndexPageView(SuperuserRequiredMixin, PageView):
    template_name = "system-event-index.html"
