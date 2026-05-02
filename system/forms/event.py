from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout
from django import forms

from core.models import Event

class EventEditForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            'max_merchants',
            'max_party_rooms',
            'submissions_end',
            'module_panels_enabled',
            'module_merchants_enabled',
            'module_performers_enabled',
            'module_partyfloor_enabled',
            'module_competitors_enabled',
            'voucher_performers',
            'voucher_volunteer'
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
                'Event',
                'max_merchants',
                'max_party_rooms',
                'submissions_end',
                'module_panels_enabled',
                'module_merchants_enabled',
                'module_performers_enabled',
                'module_partyfloor_enabled',
                'module_competitors_enabled',
                'voucher_performers',
                'voucher_volunteer'
            )
        )