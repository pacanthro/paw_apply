from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout
from django import forms

from merchants.models import Table

class TableEditForm(forms.ModelForm):
    class Meta:
        model = Table
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
                'Merchant Table',
                'name',
                'order',
            )
        )

class TableCreateForm(forms.ModelForm):
    class Meta:
        model = Table
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
                'Merchant Table',
                'key',
                'name',
                'order',
            )
        )
