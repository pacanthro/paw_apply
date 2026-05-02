from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout
from django import forms
from django.core.exceptions import ValidationError

from core.models import DaysAvailable, SchedulingConfig, get_current_event

import logging

logger = logging.getLogger("django.server")

class SchedulingConfigEditForm(forms.ModelForm):
    panels_start = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"})
    )
    panels_end = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"})
    )
    performers_start = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"})
    )
    performers_end = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"})
    )
    class Meta:
        model = SchedulingConfig
        fields = (
            'panels_start',
            'panels_end',
            'performers_start',
            'performers_end'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        
        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            Fieldset(
                'Scheduling Configuration',
                'panels_start',
                'panels_end',
                'performers_start',
                'performers_end'
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        clean_panels_start = cleaned_data.get("panels_start")
        clean_panels_end = cleaned_data.get("panels_end")
        clean_performers_start = cleaned_data.get("performers_start")
        clean_performers_end = cleaned_data.get("performers_end")

        if clean_panels_start and clean_panels_end:
            if clean_panels_end <= clean_panels_start:
                self.add_error('panels_end', ValidationError("'Panels End' must be after 'Panels Start'."))
        
        if clean_performers_start and clean_performers_end:
            if clean_performers_end <= clean_performers_start:
                self.add_error('performers_end', ValidationError("'Performers End' must be after 'Performers Start'"))


class SchedulingConfigCreateForm(forms.ModelForm):
    panels_start = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"})
    )
    panels_end = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"})
    )
    performers_start = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"})
    )
    performers_end = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"})
    )
    class Meta:
        model = SchedulingConfig
        fields = (
            'day_available',
            'panels_start',
            'panels_end',
            'performers_start',
            'performers_end'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        event = get_current_event()

        # Fields
        self.fields['day_available'].queryset = DaysAvailable.objects.filter(available_scheduling=True)
        
        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            Fieldset(
                'Scheduling Configuration',
                'day_available',
                'panels_start',
                'panels_end',
                'performers_start',
                'performers_end'
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        clean_panels_start = cleaned_data.get("panels_start")
        clean_panels_end = cleaned_data.get("panels_end")
        clean_performers_start = cleaned_data.get("performers_start")
        clean_performers_end = cleaned_data.get("performers_end")

        if clean_panels_start and clean_panels_end:
            if clean_panels_end <= clean_panels_start:
                self.add_error('panels_end', ValidationError("'Panels End' must be after 'Panels Start'."))
        
        if clean_performers_start and clean_performers_end:
            if clean_performers_end <= clean_performers_start:
                self.add_error('performers_end', ValidationError("'Performers End' must be after 'Performers Start'"))
