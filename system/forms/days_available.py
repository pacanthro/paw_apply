from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout
from django import forms

from core.models import DaysAvailable

class DaysAvailableEditForm(forms.ModelForm):
    class Meta:
        model = DaysAvailable
        fields = (
            'name',
            'order',
            'available_scheduling',
            'available_party',
            'party_only'
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
                'Day Available',
                'name',
                'order',
                'available_scheduling',
                'available_party',
                'party_only'
            )
        )

class DaysAvailableCreateForm(forms.ModelForm):
    class Meta:
        model = DaysAvailable
        fields = (
            'key',
            'name',
            'order',
            'available_scheduling',
            'available_party',
            'party_only'
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
                'Day Available',
                'key',
                'name',
                'order',
                'available_scheduling',
                'available_party',
                'party_only'
            )
        )
