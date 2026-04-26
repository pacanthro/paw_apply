from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView
from merchants.models import Table
from modules.page_view import PageView
from system.forms import TableEditForm
from system.forms.tables import TableCreateForm

class MerchantTablesListView(PageView):
    template_name = "system-tables-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['tables'] = Table.objects.filter(deleted=False).all()

        return context

class MerchantTablesEditView(PageView):
    template_name = "system-tables-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = get_object_or_404(Table, pk=kwargs['table_id'])
        form = TableEditForm(instance=table)

        context['table'] = table
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = TableEditForm(request.POST, instance=context['table'])
        
        context['form'] = form

        if form.is_valid():
            form.save()

        return self.render_to_response(context)
    
class MerchantTablesCreateView(PageView):
    template_name = "system-tables-create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = TableCreateForm()

        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = TableCreateForm(request.POST)
        
        context['form'] = form

        if form.is_valid():
            table = form.save()

            # Redirect
            return HttpResponseRedirect(reverse('system:tables-edit', args=[table.key]))

        return self.render_to_response(context)

class MerchantTableDeleteRedirectView(RedirectView):
    permanent = False
    pattern_name = 'system:tables-list'

    def get_redirect_url(self, *args, **kwargs):
        table = get_object_or_404(Table, pk=kwargs['table_id'])
        table.deleted = True
        table.save()

        return reverse('system:tables-list')
