from core.models import Department
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from modules.mixins import SuperuserRequiredMixin
from modules.page_view import PageView
from system.forms import DepartmentEditForm

class DepartmentListPageView(SuperuserRequiredMixin, PageView):
    template_name = "system-department-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['departments'] = Department.objects.filter(deleted=False).all()

        return context

class DepartmentCreatePageView(SuperuserRequiredMixin, PageView):
    template_name = "system-department-create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = DepartmentEditForm()

        context['form'] = form

        return context
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = DepartmentEditForm(request.POST)
        
        context['form'] = form

        if form.is_valid():
            department = form.save()

            return HttpResponseRedirect(reverse('system:department-edit', args=[department.id]))
        
        return self.render_to_response(context)

class DepartmentEditPageView(SuperuserRequiredMixin, PageView):
    template_name = "system-department-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department = get_object_or_404(Department, pk=kwargs['department_id'])

        form = DepartmentEditForm(instance=department)

        context['department'] = department
        context['form'] = form

        return context
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = DepartmentEditForm(request.POST, instance=context['department'])
        
        context['form'] = form

        if form.is_valid():
            form.save()
        
        return self.render_to_response(context)

class DepartmentDeleteRedirectView(SuperuserRequiredMixin, RedirectView):
    permanent = False
    pattern_name = 'system:departments-list'

    def get_redirect_url(self, *args, **kwargs):
        department = get_object_or_404(Department, pk=kwargs['department_id'])
        department.deleted = True
        department.save()

        return reverse('system:departments-list')
