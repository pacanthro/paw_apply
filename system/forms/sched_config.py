from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout
from django import forms

from core.models import DaysAvailable, SchedulingConfig, get_current_event

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
