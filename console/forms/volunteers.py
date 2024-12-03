from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse

from core.models import get_current_event
from volunteers.models import VolunteerTask

def _clean_task_time(data, key, default):
    cleaned = data.get(key)
    if cleaned and cleaned > timezone.now():
        raise(ValidationError(F'{key} cannot be in the future.'))
    
    return cleaned or default

class VolunteerTaskStartForm(forms.ModelForm):
    task_start = forms.fields.DateTimeField(required=False, widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))
    class Meta:
        model = VolunteerTask
        fields = (
            'event',
            'volunteer',
            'recorded_by',
            'task_name',
            'task_notes',
            'task_multiplier',
            'task_start'
        )

    def __init__(self, *args, **kwargs):
        volunteer = kwargs.pop('volunteer')
        user = kwargs.pop('user')

        super().__init__(*args, **kwargs)
        event = get_current_event()

        # Fields
        self.fields['event'].initial = event
        self.fields['volunteer'].initial = volunteer
        self.fields['recorded_by'].initial = user

        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class="form-horizontal"
        self.helper.label_class = 'col-sm-3 text-capitalize'
        self.helper.field_class = 'col-sm'
        self.helper.layout = Layout(
            Field('event', type='hidden'),
            Field('volunteer', type='hidden'),
            Field('recorded_by', type='hidden'),
            'task_name',
            'task_notes',
            'task_multiplier',
            'task_start'
        )
    
    def clean_task_start(self):
        return _clean_task_time(self.cleaned_data, 'task_start', timezone.now())

class VolunteerTaskEndForm(forms.ModelForm):
    task_end = forms.fields.DateTimeField(required=False, widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))
    class Meta:
        model = VolunteerTask
        fields = (
            'task_end',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields

        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class="form-horizontal"
        self.helper.label_class = 'col-sm-3 text-capitalize'
        self.helper.field_class = 'col-sm'
        self.helper.layout = Layout(
            Field('task_end')
        )
    
    def clean_task_end(self):
        return _clean_task_time(self.cleaned_data, 'task_end', None)

class VolunteerAddTaskForm(forms.ModelForm):
    task_start = forms.fields.DateTimeField(required=False, widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))
    task_end = forms.fields.DateTimeField(required=False, widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))
    
    class Meta:
        model = VolunteerTask
        fields = (
            'event',
            'volunteer',
            'recorded_by',
            'task_name',
            'task_notes',
            'task_multiplier',
            'task_start',
            'task_end'
        )
    
    def __init__(self, *args, **kwargs):
        volunteer = kwargs.pop('volunteer')
        user = kwargs.pop('user')

        super().__init__(*args, **kwargs)
        event = get_current_event()

         # Fields
        self.fields['event'].initial = event
        self.fields['volunteer'].initial = volunteer
        self.fields['recorded_by'].initial = user

        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            Field('event', type='hidden'),
            Field('volunteer', type='hidden'),
            Field('recorded_by', type='hidden'),
            'task_name',
            'task_notes',
            'task_multiplier',
            'task_start',
            'task_end'
        )

    def clean_task_start(self):
        return _clean_task_time(self.cleaned_data, 'task_start', None)
    
    def clean_task_end(self):
        return _clean_task_time(self.cleaned_data, 'task_end', None)

class VolunteerEditTaskForm(forms.ModelForm):
    task_start = forms.fields.DateTimeField(required=False, widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))
    task_end = forms.fields.DateTimeField(required=False, widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))
    
    class Meta:
        model = VolunteerTask
        fields = (
            'task_name',
            'task_notes',
            'task_multiplier',
            'task_start',
            'task_end'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
         # Fields

        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            'task_name',
            'task_notes',
            'task_multiplier',
            'task_start',
            'task_end'
        )

    def clean_task_start(self):
        return _clean_task_time(self.cleaned_data, 'task_start', None)
    
    def clean_task_end(self):
        return _clean_task_time(self.cleaned_data, 'task_end', None)

