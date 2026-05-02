from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout
from django import forms

from panels.models import PanelSlot

class PanelSlotEditForm(forms.ModelForm):
    class Meta:
        model = PanelSlot
        fields = (
            'name',
            'order'
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
                'Panel Slot',
                'name',
                'order',
            )
        )

class PanelSlotCreateForm(forms.ModelForm):
    class Meta:
        model = PanelSlot
        fields = (
            'key',
            'name',
            'order'
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
                'Panel Slot',
                'key',
                'name',
                'order',
            )
        )
